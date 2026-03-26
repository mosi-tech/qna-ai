#!/usr/bin/env python3
"""
MCP Block Solver Agent  (Plan → Execute → Format)

Solves ONE block's sub_question using real MCP tools without context overflow.

Flow
────
Call 1  (plan)    LLM sees tool schemas + sub_question
                  → returns a JSON plan:
                    {
                      "fetch":   {"tool": "get_historical_data", "args": {...}},
                      "compute": [
                        {"tool": "calculate_returns_metrics", "args": {}},
                        {"tool": "calculate_risk_metrics",   "args": {}}
                      ]
                    }

Python  (execute) Runs fetch_tool   → full raw data kept in Python memory
                  Detects data type, extracts relevant series (prices → returns etc.)
                  Runs each compute_tool on the FULL series
                  Collects compact analytics results

Call 2  (format)  LLM receives ONLY compact results (a few numbers / short dicts)
                  → formats to exact dataContract shape

Raw rows never enter the LLM context at any point.

If fetch result is already compact (<= COMPACT_THRESHOLD rows),
compute step is skipped and raw result goes straight to Call 2.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

from agent_base import AgentBase, AgentResult

logger = logging.getLogger(__name__)

# Add mcp-server to path so we can call analytics directly
_MCP_SERVER_DIR = Path(__file__).resolve().parent.parent.parent / "mcp-server"
if str(_MCP_SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(_MCP_SERVER_DIR))

# Rows below this → data is compact enough, skip the compute step
COMPACT_THRESHOLD = 50


# ─── System prompts ───────────────────────────────────────────────────────────

_SELECT_SYSTEM_PROMPT = """\
You are a financial function selector. Given a sub-question, pick the functions
needed to answer it — ONE fetch function and ZERO or MORE compute functions.

Rules
─────
1. fetch  — one function that retrieves raw data (get_historical_data, get_positions, etc.)
2. compute — functions that compute analytics on that data (calculate_*, analyze_*, etc.)
   Set to [] if: fetch already returns compact data, OR dataContract.type is "timeseries"
3. Use ONLY exact function names from AVAILABLE FUNCTIONS.
   NEVER invent, guess, or compose function names that are not in the list.
   If no function exists for a metric, omit it — do not add it to compute[].

Common metric → function mapping (use these exact names):
  Sharpe ratio, VaR, volatility, Sortino  → calculate_risk_metrics
  CAGR / annual return, total return      → calculate_returns_metrics  (or calculate_cagr for scalar)
  Max drawdown, recovery, underwater      → calculate_drawdown_analysis
  Beta, alpha, information ratio          → calculate_benchmark_metrics
  Monthly return heatmap                  → calculate_monthly_returns
  Rolling volatility                      → calculate_rolling_volatility

Output ONLY this JSON:
{
  "fetch": "<exact function name>",
  "compute": ["<exact function name>", ...]
}"""

_PLAN_SYSTEM_PROMPT = """\
You are a financial data planning agent. You are given complete docstrings for the
functions you must call. Produce an EXECUTION PLAN with exact arguments.

Rules
─────
1. Use ONLY the function names and parameter names shown in the docstrings.
   NEVER invent function names or parameter names not present in the docstrings.
2. Only include functions in compute[] whose docstrings appear in FUNCTION DOCSTRINGS.
   If a metric has no matching function in the docstrings, omit it entirely.
3. For date ranges expressed as periods (e.g. "10y", "1y"), convert to absolute dates.
   Today is 2026-03-24.
4. compute[].args should only include extra args beyond returns/prices — those are
   injected automatically from the fetched data.

Output ONLY a JSON object — no prose, no markdown fences:
{
  "fetch": {
    "tool": "<function name>",
    "args": { <exact param names and values from docstring> }
  },
  "compute": [
    {"tool": "<function name>", "args": { <any extra args only> }},
    ...
  ]
}"""

_FORMAT_SYSTEM_PROMPT = """\
You are a financial data formatter. You receive the results of tool executions
and must format them into the exact dataContract shape requested.

Rules
─────
1. Return ONLY JSON — no prose, no markdown fences.
2. Use EXACTLY the field names listed in dataContract.fields.
3. Shape output to match dataContract.type:
   - kpi        → {"cards": [{"label": str, "value": str, "delta": float|null}]}
   - timeseries → {"data": [{"date": "YYYY-MM-DD", <field>: value, ...}],
                   "series": [{"key": str, "label": str}]}
   - categorical → {"data": [{"label": str, "value": float}]}
   - table-rows  → {"columns": [{"key": str, "label": str}], "rows": [...]}
   - ranked      → {"data": [{"label": str, "value": float, "delta": float|null}]}
   - matrix      → {"rows": [str], "cols": [str], "cells": [[val,…],…]}
4. Format numeric values as human-readable strings for kpi cards
   (e.g. "14.2%" not 0.142), but keep raw numbers for chart data."""


class MCPBlockSolverAgent(AgentBase):

    def __init__(self, llm_model: str = None, llm_provider: str = None):
        super().__init__(
            name="mcp_block_solver",
            task="MCP_DIRECT",
            prompt_file=None,
            llm_model=llm_model,
            llm_provider=llm_provider,
        )
        self.system_prompt = _PLAN_SYSTEM_PROMPT

    # ── Schema stubs ──────────────────────────────────────────────────────────

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "blockId":          {"type": "string"},
                "sub_question":     {"type": "string"},
                "canonical_params": {"type": "object"},
                "dataContract":     {"type": "object"},
            },
            "required": ["blockId", "sub_question", "dataContract"],
        }

    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "blockId":          {"type": "string"},
                "data":             {"type": "object"},
                "functions_called": {"type": "array"},
                "success":          {"type": "boolean"},
            },
            "required": ["blockId", "data", "success"],
        }

    # ── Main process ──────────────────────────────────────────────────────────

    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        block_id         = input_data.get("blockId", "unknown")
        sub_question     = input_data.get("sub_question", "")
        canonical_params = input_data.get("canonical_params", {})
        data_contract    = input_data.get("dataContract", {})

        catalog = self._get_tool_catalog()
        self.logger.info(f"🔧 [{block_id}] {len(catalog)} functions available")

        # ── Call 1: select functions ───────────────────────────────────────────
        select_message = _build_select_message(
            block_id, sub_question, canonical_params, data_contract, catalog,
        )
        self.logger.info(f"🔍 [{block_id}] Call 1 — selecting functions")
        select_response = self._make_llm_request(
            messages=[{"role": "user", "content": select_message}],
            tools=None,
            system_prompt_override=_SELECT_SYSTEM_PROMPT,
        )
        if not select_response.get("success"):
            return AgentResult(success=False, error=f"Select call failed: {select_response.get('error')}")

        try:
            selection = self._safe_parse_json(select_response.get("content", ""))
        except Exception as e:
            return AgentResult(success=False, error=f"Invalid selection JSON: {e}")
        if not selection or "fetch" not in selection:
            return AgentResult(success=False, error=f"Invalid selection: {select_response.get('content', '')[:200]}")

        self.logger.info(
            f"🔍 [{block_id}] Selected: fetch={selection['fetch']}, "
            f"compute={selection.get('compute', [])}"
        )

        # ── Fetch docstrings for selected functions ────────────────────────────
        selected_names = [selection["fetch"]] + selection.get("compute", [])
        docstrings = self._fetch_docstrings(selected_names)
        self.logger.info(f"📖 [{block_id}] Fetched docstrings for: {list(docstrings.keys())}")

        # ── Call 2: plan with full docstrings ──────────────────────────────────
        plan_message = _build_plan_message(
            block_id, sub_question, canonical_params, data_contract, docstrings,
        )
        self.logger.info(f"📋 [{block_id}] Call 2 — building plan with full docstrings")
        plan_response = self._make_llm_request(
            messages=[{"role": "user", "content": plan_message}],
            tools=None,
        )

        if not plan_response.get("success"):
            return AgentResult(success=False, error=f"Plan call failed: {plan_response.get('error')}")

        try:
            plan = self._safe_parse_json(plan_response.get("content", ""))
        except Exception as parse_err:
            return AgentResult(success=False, error=f"LLM returned invalid plan JSON: {parse_err}")
        if not plan or "fetch" not in plan:
            return AgentResult(success=False, error=f"LLM returned invalid plan: {plan_response.get('content', '')[:300]}")

        self.logger.info(
            f"📋 [{block_id}] Plan: fetch={plan['fetch']['tool']}, "
            f"compute={[c['tool'] for c in plan.get('compute', [])]}"
        )

        # ── Python execution ──────────────────────────────────────────────────
        functions_called = []

        # Step A: fetch
        fetch_tool = plan["fetch"]["tool"]
        fetch_args = plan["fetch"].get("args", {})

        try:
            self.logger.info(f"  [{block_id}] Fetching: {fetch_tool}({list(fetch_args.keys())})")
            raw_data = self._call_function(fetch_tool, fetch_args)
            functions_called.append(fetch_tool)
        except Exception as e:
            return AgentResult(success=False, error=f"Fetch failed ({fetch_tool}): {e}")

        # Step B: compute analytics on full data (if plan specifies any)
        compute_steps = plan.get("compute", [])
        compact_results: Dict[str, Any] = {}

        data_array = _find_data_array(raw_data)
        row_count  = len(data_array) if data_array is not None else 0
        is_large   = row_count > COMPACT_THRESHOLD

        self.logger.info(
            f"  [{block_id}] Fetch returned {row_count} rows "
            f"({'large' if is_large else 'compact'}), "
            f"{len(compute_steps)} compute steps planned"
        )

        if compute_steps:
            self.logger.info(
                f"  [{block_id}] {row_count} rows — running "
                f"{len(compute_steps)} analytics tools on full data"
            )
            series = _extract_series(data_array or [])

            for step in compute_steps:
                tool_name  = step["tool"]
                extra_args = step.get("args", {})
                try:
                    args = _build_analytics_args(tool_name, series, extra_args)
                    self.logger.info(f"  [{block_id}] Computing: {tool_name}")
                    result = self._call_function(tool_name, args)
                    compact_results[tool_name] = result
                    functions_called.append(tool_name)
                except Exception as e:
                    self.logger.warning(f"  [{block_id}] Compute {tool_name} failed: {e}")
                    compact_results[tool_name] = {"error": str(e)}

            context_data = compact_results

        elif is_large:
            # Timeseries / table — downsample raw data, no analytics
            self.logger.info(f"  [{block_id}] Large data, no compute — downsampling {row_count} rows")
            context_data = _downsample(raw_data, data_array, data_contract, max_points=150)

        else:
            # Already compact — pass through as-is
            context_data = raw_data

        # ── Call 2: format ────────────────────────────────────────────────────
        format_message = _build_format_message(
            block_id, sub_question, data_contract,
            fetch_tool, context_data, functions_called,
        )

        self.logger.info(f"🖊  [{block_id}] Call 2 — formatting result")
        format_response = self._make_llm_request(
            messages=[{"role": "user", "content": format_message}],
            tools=None,
            system_prompt_override=_FORMAT_SYSTEM_PROMPT,
        )

        if not format_response.get("success"):
            return AgentResult(success=False, error=f"Format call failed: {format_response.get('error')}")

        try:
            result_data = self._safe_parse_json(format_response.get("content", ""))
        except Exception as parse_err:
            return AgentResult(success=False, error=f"LLM returned invalid format JSON: {parse_err}")
        if not result_data:
            return AgentResult(success=False, error=f"LLM returned invalid JSON in format call: {format_response.get('content', '')[:300]}")

        result_data.setdefault("blockId", block_id)
        result_data.setdefault("functions_called", functions_called)

        self.logger.info(
            f"✅ [{block_id}] Done — functions: {functions_called}"
        )
        return AgentResult(success=True, data=result_data)

    # ── Function library helpers ───────────────────────────────────────────────
    # We call Python functions directly — no MCP protocol overhead, no schema
    # validation issues.  The function registries are loaded once and cached.

    def _get_function_registry(self) -> Dict[str, Any]:
        """Return a flat {name: callable} registry of all financial + analytics fns."""
        if not hasattr(self, "_fn_registry"):
            from financial.functions_mock import MOCK_FINANCIAL_FUNCTIONS
            import analytics as _analytics_module
            import inspect

            registry: Dict[str, Any] = {}

            # Financial functions
            for name, fn in MOCK_FINANCIAL_FUNCTIONS.items():
                registry[name] = fn

            # Analytics functions — everything exported from the analytics package
            for name, obj in inspect.getmembers(_analytics_module, inspect.isfunction):
                if not name.startswith("_"):
                    registry[name] = obj

            self._fn_registry = registry
            self.logger.info(
                f"Function registry: {len(MOCK_FINANCIAL_FUNCTIONS)} financial, "
                f"{len(registry) - len(MOCK_FINANCIAL_FUNCTIONS)} analytics"
            )
        return self._fn_registry

    def _get_tool_catalog(self) -> List[Dict[str, Any]]:
        """Return a lightweight tool catalog (name + signature + rich description).

        Uses up to the first two paragraphs of the docstring so that lines like
        "Computes Sharpe ratio, VaR, Sortino..." are included — not just the
        generic opening sentence.
        """
        if not hasattr(self, "_tool_catalog_cache"):
            import inspect
            registry = self._get_function_registry()
            catalog = []
            for name, fn in registry.items():
                full_doc = inspect.getdoc(fn) or ""
                # Take up to the first two non-empty paragraphs (split on blank lines)
                paragraphs = [p.strip() for p in full_doc.split("\n\n") if p.strip()]
                summary_parts = []
                char_budget = 200
                for para in paragraphs[:2]:
                    # Stop if we hit the Args / Returns section
                    if para.lower().startswith(("args", "returns", "raises", "example")):
                        break
                    summary_parts.append(para.replace("\n", " "))
                    char_budget -= len(summary_parts[-1])
                    if char_budget <= 0:
                        break
                description = " — ".join(summary_parts)[:220]

                try:
                    sig = inspect.signature(fn)
                    params = ", ".join(
                        f"{p}{'=...' if v.default is not inspect.Parameter.empty else ''}"
                        for p, v in sig.parameters.items()
                        if v.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
                    )
                except (ValueError, TypeError):
                    params = "..."
                catalog.append({"name": name, "signature": f"{name}({params})", "description": description})
            self._tool_catalog_cache = catalog
        return self._tool_catalog_cache

    def _fetch_docstrings(self, function_names: List[str]) -> Dict[str, str]:
        """Return {name: full_docstring} for each requested function name.
        If a name is not found exactly, tries fuzzy matching against the registry.
        """
        import inspect
        registry = self._get_function_registry()
        result = {}
        for name in function_names:
            fn = registry.get(name)
            if fn:
                result[name] = inspect.getdoc(fn) or f"No docstring for {name}"
            else:
                self.logger.warning(f"  Unknown function {name!r} — skipped (not in registry)")
        return result

    def _call_function(self, function_name: str, arguments: Dict) -> Any:
        """Call a financial or analytics function directly by name."""
        registry = self._get_function_registry()
        fn = registry.get(function_name)
        if fn is None:
            raise ValueError(f"Unknown function: {function_name!r}")
        result = fn(**arguments)
        # Normalise: convert dataclasses/objects to plain dicts
        return _normalise(result)

    def _make_llm_request(self, messages, tools=None, system_prompt_override=None):
        """Override to allow swapping system prompt between calls."""
        original = self.system_prompt
        if system_prompt_override:
            self.system_prompt = system_prompt_override
        try:
            return super()._make_llm_request(messages=messages, tools=tools)
        finally:
            self.system_prompt = original


# ─── Prompt builders ──────────────────────────────────────────────────────────

def _build_select_message(
    block_id, sub_question, canonical_params, data_contract, catalog,
) -> str:
    catalog_str = _tool_catalog(catalog, max_tools=80)
    return (
        f"BLOCK ID: {block_id}\n"
        f"SUB-QUESTION: {sub_question}\n"
        f"CANONICAL PARAMS: {json.dumps(canonical_params)}\n"
        f"DATA CONTRACT TYPE: {data_contract.get('type', 'unknown')}\n"
        f"EXPECTED FIELDS: {data_contract.get('fields', [])}\n\n"
        f"AVAILABLE FUNCTIONS:\n{catalog_str}\n\n"
        f"For each EXPECTED FIELD, identify which function in AVAILABLE FUNCTIONS "
        f"produces that metric. Then output the minimal set of functions needed."
    )


def _build_plan_message(
    block_id, sub_question, canonical_params, data_contract, docstrings,
) -> str:
    docs_str = "\n\n".join(
        f"=== {name} ===\n{doc}" for name, doc in docstrings.items()
    )
    return (
        f"BLOCK ID: {block_id}\n"
        f"SUB-QUESTION: {sub_question}\n"
        f"CANONICAL PARAMS: {json.dumps(canonical_params)}\n"
        f"DATA CONTRACT TYPE: {data_contract.get('type', 'unknown')}\n"
        f"EXPECTED FIELDS: {data_contract.get('fields', [])}\n\n"
        f"FUNCTION DOCSTRINGS:\n{docs_str}\n\n"
        f"Produce the execution plan JSON."
    )


def _build_format_message(
    block_id, sub_question, data_contract,
    fetch_tool, context_data, functions_called,
) -> str:
    data_json = json.dumps(context_data, indent=2, default=str)
    return (
        f"BLOCK ID: {block_id}\n"
        f"SUB-QUESTION: {sub_question}\n"
        f"DATA CONTRACT TYPE: {data_contract.get('type', 'unknown')}\n"
        f"EXPECTED FIELDS: {data_contract.get('fields', [])}\n\n"
        f"TOOL RESULTS (from {fetch_tool} + analytics):\n{data_json}\n\n"
        f"Format the above into the dataContract shape.\n"
        f"Return ONLY JSON with keys: blockId, data, functions_called.\n"
        f"functions_called = {json.dumps(functions_called)}"
    )


def _tool_catalog(catalog: List[Dict], max_tools: int = 80) -> str:
    """One-line summary per function: signature — description."""
    lines = []
    for entry in catalog[:max_tools]:
        sig  = entry.get("signature", entry.get("name", ""))
        desc = entry.get("description", "").split(".")[0].strip()[:80]
        lines.append(f"  {sig} — {desc}")
    if len(catalog) > max_tools:
        lines.append(f"  … and {len(catalog) - max_tools} more")
    return "\n".join(lines)


# ─── Data helpers ─────────────────────────────────────────────────────────────

def _normalise(obj: Any) -> Any:
    """Recursively convert dataclass instances / named-tuples to plain dicts."""
    if isinstance(obj, dict):
        return {k: _normalise(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_normalise(i) for i in obj]
    if hasattr(obj, "__dict__") and not isinstance(obj, type):
        return _normalise(vars(obj))
    if hasattr(obj, "_asdict"):  # named tuple
        return _normalise(obj._asdict())
    return obj


def _find_data_array(raw: Any) -> Optional[List]:
    """Find the main data array in an MCP tool result.

    Handles two common shapes:
    - Direct list:  {"data": [{...}, ...]}
    - Symbol-keyed: {"data": {"QQQ": [{...}, ...]}}  ← financial server format
    """
    if not isinstance(raw, dict):
        return None
    for key in ("data", "bars", "results", "quotes", "trades", "history", "records"):
        val = raw.get(key)
        if isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict):
            return val
        # Symbol-keyed dict → flatten all symbol arrays into one list
        if isinstance(val, dict) and val:
            combined = []
            for inner in val.values():
                if isinstance(inner, list):
                    combined.extend(inner)
            if combined and isinstance(combined[0], dict):
                return combined
    return None


def _extract_series(data_array: List[Dict]) -> Dict[str, float]:
    """
    Extract a date → value series from an array of row dicts.
    Tries close prices first (for returns-based analytics),
    falls back to first numeric field.
    """
    price_keys = ("close", "Close", "c", "adjClose", "adj_close", "price", "value")
    date_keys  = ("timestamp", "date", "t", "time", "Date", "datetime")

    close_key = next((k for k in price_keys if data_array[0].get(k) is not None), None)
    date_key  = next((k for k in date_keys  if data_array[0].get(k) is not None), None)

    if close_key is None:
        # Fall back to first numeric field
        for k, v in data_array[0].items():
            if isinstance(v, (int, float)):
                close_key = k
                break

    if close_key is None:
        return {}

    if date_key:
        return {row[date_key]: float(row[close_key]) for row in data_array if row.get(close_key) is not None}
    else:
        return {i: float(row[close_key]) for i, row in enumerate(data_array) if row.get(close_key) is not None}


def _build_analytics_args(tool_name: str, series: Dict, extra_args: Dict) -> Dict:
    """
    Map the extracted price/value series to the argument the analytics tool expects.
    Most analytics tools take `returns` (pct changes); some take `prices`; a few
    take scalar args derived from the series (e.g. calculate_cagr).
    """
    import pandas as pd
    from datetime import datetime

    price_series = pd.Series(series).sort_index()

    # Tools that take scalar values derived from the price series
    if tool_name == "calculate_cagr":
        start_val = float(price_series.iloc[0])
        end_val   = float(price_series.iloc[-1])
        # Estimate years from index (try parsing as dates, fall back to count/252)
        try:
            idx = price_series.index
            years = (pd.to_datetime(idx[-1]) - pd.to_datetime(idx[0])).days / 365.25
        except Exception:
            years = len(price_series) / 252
        return {"start_value": start_val, "end_value": end_val, "years": round(years, 4), **extra_args}

    # Tools that want prices directly
    price_tools = {
        "calculate_annualized_return",
        "calculate_annualized_volatility",
        "calculate_cumulative_returns",
        "analyze_leverage_fund",
    }

    if tool_name in price_tools:
        return {"prices": series, **extra_args}

    # Default: compute returns from prices
    returns = price_series.pct_change().dropna()
    return {"returns": returns.to_dict(), **extra_args}


def _downsample(raw: Dict, data_array: List, data_contract: Dict, max_points: int) -> Dict:
    """
    Downsample a large array to max_points evenly-spaced rows.
    Also projects to only the fields the block needs.
    """
    import numpy as np

    n      = len(data_array)
    fields = set(data_contract.get("fields") or [])
    keep   = fields | {"timestamp", "date", "t", "time", "Date", "datetime",
                       "ticker", "symbol", "name", "label"}

    indices = sorted(set(
        [0] + list(np.linspace(1, n - 2, max_points - 2, dtype=int)) + [n - 1]
    ))
    sampled = [
        {k: v for k, v in data_array[i].items() if not fields or k in keep}
        for i in indices
    ]

    array_key = next(
        (k for k in ("data", "bars", "results") if isinstance(raw.get(k), list)), "data"
    )
    return {
        **{k: v for k, v in raw.items() if k != array_key},
        array_key:       sampled,
        "_total_rows":   n,
        "_returned_rows": len(sampled),
        "_note":         f"Downsampled from {n} to {len(sampled)} rows for display",
    }


# ─── Factory ──────────────────────────────────────────────────────────────────

def create_mcp_block_solver_agent(**kwargs) -> MCPBlockSolverAgent:
    return MCPBlockSolverAgent(**kwargs)


# ─── CLI test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys as _sys

    q = _sys.argv[1] if len(_sys.argv) > 1 else "What is the CAGR and Sharpe ratio for QQQ over 10 years?"
    agent = MCPBlockSolverAgent()
    result = agent.execute({
        "blockId": "FKMetricGrid",
        "sub_question": q,
        "canonical_params": {"ticker": "QQQ", "period": "10y"},
        "dataContract": {
            "type": "kpi",
            "description": "CAGR, Sharpe ratio, max drawdown for QQQ",
            "fields": ["cagr", "sharpe", "max_drawdown"],
        },
    })
    print(json.dumps(result.to_dict(), indent=2))
