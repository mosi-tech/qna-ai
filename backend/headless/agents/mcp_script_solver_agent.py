#!/usr/bin/env python3
"""
MCP Script Solver Agent  (Select → Docstring → Script → Execute → Validate)

Solves ONE block's sub_question by having the LLM write a Python script
that calls financial/analytics functions directly.

Flow
────
Call 1  (select)   LLM sees catalog (name + rich description)
                   → returns {"fetch": "get_historical_data", "compute": [...]}

Python             Fetches full docstrings for selected functions

Call 2  (script)   LLM sees docstrings + sub_question + dataContract
                   → writes a complete, self-contained Python script

Python             Executes the script as a subprocess
                   Captures stdout JSON

Validate           Checks all dataContract.fields are present and non-null
                   On failure → retry Call 2 once with the error injected

Unlike the Plan→Execute→Format agent, the LLM has full expressive power —
it can do multi-step fetches, custom math, conditionals, anything Python allows.
"""

import json
import os
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent_base import AgentBase, AgentResult

import logging
logger = logging.getLogger(__name__)

_MCP_SERVER_DIR = Path(__file__).resolve().parent.parent.parent / "mcp-server"
if str(_MCP_SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(_MCP_SERVER_DIR))

MAX_RETRIES = 2


# ─── System prompts ───────────────────────────────────────────────────────────

_SELECT_SYSTEM_PROMPT = """\
You are a financial function selector. Given a sub-question, pick the functions
needed to answer it — ONE fetch function and ZERO or MORE compute functions.

Rules
─────
1. fetch  — one function that retrieves raw data (get_historical_data, get_positions, etc.)
2. compute — functions that compute analytics on that data (calculate_*, analyze_*, etc.)
   Set to [] if fetch already returns compact/summary data.
3. Use ONLY exact function names from AVAILABLE FUNCTIONS.
   NEVER invent, guess, or compose function names not in the list.
   If no function exists for a metric, omit it — do not add it.

Common metric → function mapping (use these exact names):
  Sharpe ratio, VaR, volatility, Sortino  → calculate_risk_metrics
  CAGR / annual return, total return      → calculate_returns_metrics
  Max drawdown, recovery, underwater      → calculate_drawdown_analysis
  Beta, alpha, information ratio          → calculate_benchmark_metrics
  Monthly return heatmap                  → calculate_monthly_returns
  Rolling volatility                      → calculate_rolling_volatility

For each EXPECTED FIELD, identify which function produces that metric, then
output the minimal set of functions needed.

Output ONLY this JSON:
{
  "fetch": "<exact function name>",
  "compute": ["<exact function name>", ...]
}"""


_JUDGE_SYSTEM_PROMPT = """\
You are a financial output completeness judge. Given a sub-question and a script result,
determine if the output is complete and answers what was asked.

Check for:
- Are all expected fields present and non-null in the output?
- Does the output structure match the dataContract type (e.g. kpi has cards, timeseries has data+series)?
- Does the output address the sub-question (right subject, right scope)?
- Are there placeholder values like "N/A", null, or empty lists where real values are expected?

Do NOT check numeric ranges or whether values are financially reasonable —
that is not your job. Only check completeness and relevance.

Output ONLY this JSON:
{
  "valid": true or false,
  "issues": ["issue 1", "issue 2", ...]
}
If valid, issues can be []. If not valid, describe what is missing or incomplete."""


_SCRIPT_SYSTEM_PROMPT = """\
You are a financial data script writer. Write a self-contained Python script
that answers the sub-question and outputs JSON matching the dataContract.

Rules
─────
1. Import ONLY from these modules (already on sys.path):
     from financial.functions_mock import <function>
     from analytics import <function>
   Use ONLY the exact function names and parameter names shown in DOCSTRINGS.
   NEVER invent function names or import paths.

2. The script must print a single JSON object to stdout as its last action:
     import json; print(json.dumps(result))

3. result must contain ALL fields listed in EXPECTED FIELDS.
   Use the exact field names from EXPECTED FIELDS as keys.

4. Format values appropriately for the dataContract type:
   - kpi        → result = {"cards": [{"label": str, "value": str, "delta": float|null}]}
   - timeseries → result = {"data": [...], "series": [...]}
   - categorical → result = {"data": [{"label": str, "value": float}]}
   - table-rows  → result = {"columns": [...], "rows": [...]}
   - ranked      → result = {"data": [{"label": str, "value": float, "delta": float|null}]}

5. For date periods (e.g. "10y", "1y"), convert to absolute dates. Today = 2026-03-24.

6. financial data returns: {"success": bool, "data": {"SYMBOL": [bars...]}, "error": ...}
   Each bar has: timestamp, symbol, open, high, low, close, volume

7. Do not use try/except to silently swallow errors — let them propagate so
   failures are visible.

Output ONLY the Python script — no prose, no markdown fences."""


# ─── Agent ────────────────────────────────────────────────────────────────────

class MCPScriptSolverAgent(AgentBase):

    def __init__(self, llm_model: str = None, llm_provider: str = None):
        super().__init__(
            name="mcp_script_solver",
            task="MCP_SCRIPT",
            prompt_file=None,
            llm_model=llm_model,
            llm_provider=llm_provider,
        )
        self.system_prompt = _SELECT_SYSTEM_PROMPT

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
        select_msg = _build_select_message(
            block_id, sub_question, canonical_params, data_contract, catalog,
        )
        self.logger.info(f"🔍 [{block_id}] Call 1 — selecting functions")
        sel_resp = self._make_llm_request(
            messages=[{"role": "user", "content": select_msg}],
            tools=None,
            system_prompt_override=_SELECT_SYSTEM_PROMPT,
        )
        if not sel_resp.get("success"):
            return AgentResult(success=False, error=f"Select failed: {sel_resp.get('error')}")

        try:
            selection = self._safe_parse_json(sel_resp.get("content", ""))
        except Exception as e:
            self.logger.error(f"Select raw response: {sel_resp.get('content','')[:400]!r}")
            return AgentResult(success=False, error=f"Invalid selection JSON: {e}")
        if not selection or "fetch" not in selection:
            return AgentResult(success=False, error=f"Invalid selection: {sel_resp.get('content','')[:200]}")

        self.logger.info(
            f"🔍 [{block_id}] Selected: fetch={selection['fetch']}, "
            f"compute={selection.get('compute', [])}"
        )

        # ── Fetch docstrings ───────────────────────────────────────────────────
        names = [selection["fetch"]] + selection.get("compute", [])
        docstrings = self._fetch_docstrings(names)
        self.logger.info(f"📖 [{block_id}] Docstrings for: {list(docstrings.keys())}")

        # ── Call 2+: write script, execute, validate, retry ───────────────────
        script_msg = _build_script_message(
            block_id, sub_question, canonical_params, data_contract, docstrings,
        )

        last_error: Optional[str] = None
        for attempt in range(MAX_RETRIES + 1):
            messages = [{"role": "user", "content": script_msg}]
            if last_error:
                messages.append({"role": "assistant", "content": last_script})
                messages.append({"role": "user", "content": (
                    f"The script failed with this error:\n{last_error}\n\n"
                    f"Fix the script. Output ONLY the corrected Python — no prose."
                )})

            label = f"Call {2 + attempt}"
            self.logger.info(f"✍️  [{block_id}] {label} — writing script (attempt {attempt + 1})")
            script_resp = self._make_llm_request(
                messages=messages,
                tools=None,
                system_prompt_override=_SCRIPT_SYSTEM_PROMPT,
            )
            if not script_resp.get("success"):
                return AgentResult(success=False, error=f"Script call failed: {script_resp.get('error')}")

            last_script = _strip_fences(script_resp.get("content", ""))
            self.logger.info(f"  [{block_id}] Script written ({len(last_script)} chars), executing…")

            output, exec_error = _execute_script(last_script, str(_MCP_SERVER_DIR))

            if exec_error:
                self.logger.warning(f"  [{block_id}] Script error (attempt {attempt + 1}): {exec_error[:200]}")
                last_error = exec_error
                continue

            # Parse stdout as JSON
            try:
                result_data = json.loads(output)
            except Exception as e:
                last_error = f"Script stdout is not valid JSON: {e}\nOutput was:\n{output[:300]}"
                self.logger.warning(f"  [{block_id}] {last_error}")
                continue

            # ── Judge: does this output actually answer the question? ──────────
            verdict = self._judge(sub_question, data_contract, result_data)
            if not verdict["valid"]:
                issues = "; ".join(verdict["issues"])
                last_error = f"Output does not answer the question. Issues: {issues}\nOutput: {json.dumps(result_data)[:400]}"
                self.logger.warning(f"  [{block_id}] Judge rejected: {issues}")
                continue

            # ✅ Success
            result_data["blockId"] = block_id
            result_data["functions_called"] = names
            self.logger.info(f"✅ [{block_id}] Done in {attempt + 1} attempt(s)")
            return AgentResult(success=True, data=result_data)

        return AgentResult(
            success=False,
            error=f"Script failed after {MAX_RETRIES + 1} attempts. Last error: {last_error}",
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_function_registry(self) -> Dict[str, Any]:
        if not hasattr(self, "_fn_registry"):
            import inspect
            from financial.functions_mock import MOCK_FINANCIAL_FUNCTIONS
            import analytics as _an

            registry: Dict[str, Any] = {**MOCK_FINANCIAL_FUNCTIONS}
            for name, obj in inspect.getmembers(_an, inspect.isfunction):
                if not name.startswith("_"):
                    registry[name] = obj

            self._fn_registry = registry
            self.logger.info(
                f"Function registry: {len(MOCK_FINANCIAL_FUNCTIONS)} financial, "
                f"{len(registry) - len(MOCK_FINANCIAL_FUNCTIONS)} analytics"
            )
        return self._fn_registry

    def _get_tool_catalog(self) -> List[Dict[str, Any]]:
        if not hasattr(self, "_catalog_cache"):
            import inspect
            registry = self._get_function_registry()
            catalog = []
            for name, fn in registry.items():
                full_doc = inspect.getdoc(fn) or ""
                paragraphs = [p.strip() for p in full_doc.split("\n\n") if p.strip()]
                parts, budget = [], 200
                for para in paragraphs[:2]:
                    if para.lower().startswith(("args", "returns", "raises", "example")):
                        break
                    parts.append(para.replace("\n", " "))
                    budget -= len(parts[-1])
                    if budget <= 0:
                        break
                description = " — ".join(parts)[:220]
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
            self._catalog_cache = catalog
        return self._catalog_cache

    def _fetch_docstrings(self, names: List[str]) -> Dict[str, str]:
        import inspect
        registry = self._get_function_registry()
        result = {}
        for name in names:
            fn = registry.get(name)
            if fn:
                result[name] = inspect.getdoc(fn) or f"No docstring for {name}"
            else:
                self.logger.warning(f"  Unknown function {name!r} — skipped")
        return result

    def _judge(self, sub_question: str, data_contract: Dict, result: Any) -> Dict:
        """Ask the LLM whether the script output genuinely answers the question."""
        msg = (
            f"SUB-QUESTION: {sub_question}\n"
            f"DATA CONTRACT TYPE: {data_contract.get('type')}\n"
            f"EXPECTED FIELDS: {data_contract.get('fields', [])}\n\n"
            f"SCRIPT OUTPUT:\n{json.dumps(result, indent=2, default=str)[:800]}\n\n"
            f"Does this output correctly answer the sub-question?"
        )
        resp = self._make_llm_request(
            messages=[{"role": "user", "content": msg}],
            tools=None,
            system_prompt_override=_JUDGE_SYSTEM_PROMPT,
        )
        if not resp.get("success"):
            # If judge call fails, allow through — don't block on judge errors
            self.logger.warning(f"  Judge call failed: {resp.get('error')} — allowing output")
            return {"valid": True, "issues": []}
        try:
            return self._safe_parse_json(resp.get("content", ""))
        except Exception:
            return {"valid": True, "issues": []}  # parse failure → allow through

    def _make_llm_request(self, messages, tools=None, system_prompt_override=None):
        original = self.system_prompt
        if system_prompt_override:
            self.system_prompt = system_prompt_override
        try:
            return super()._make_llm_request(messages=messages, tools=tools)
        finally:
            self.system_prompt = original


# ─── Prompt builders ──────────────────────────────────────────────────────────

def _build_select_message(block_id, sub_question, canonical_params, data_contract, catalog) -> str:
    lines = []
    for e in catalog[:80]:
        sig  = e.get("signature", e["name"])
        desc = e.get("description", "").split(".")[0].strip()[:80]
        lines.append(f"  {sig} — {desc}")
    if len(catalog) > 80:
        lines.append(f"  … and {len(catalog) - 80} more")
    catalog_str = "\n".join(lines)
    return (
        f"BLOCK ID: {block_id}\n"
        f"SUB-QUESTION: {sub_question}\n"
        f"CANONICAL PARAMS: {json.dumps(canonical_params)}\n"
        f"DATA CONTRACT TYPE: {data_contract.get('type', 'unknown')}\n"
        f"EXPECTED FIELDS: {data_contract.get('fields', [])}\n\n"
        f"AVAILABLE FUNCTIONS:\n{catalog_str}\n\n"
        f"For each EXPECTED FIELD, identify which function produces that metric, "
        f"then output the minimal set of functions needed."
    )


def _build_script_message(block_id, sub_question, canonical_params, data_contract, docstrings) -> str:
    docs_str = "\n\n".join(f"=== {name} ===\n{doc}" for name, doc in docstrings.items())
    return (
        f"BLOCK ID: {block_id}\n"
        f"SUB-QUESTION: {sub_question}\n"
        f"CANONICAL PARAMS: {json.dumps(canonical_params)}\n"
        f"DATA CONTRACT TYPE: {data_contract.get('type', 'unknown')}\n"
        f"EXPECTED FIELDS: {data_contract.get('fields', [])}\n\n"
        f"FUNCTION DOCSTRINGS:\n{docs_str}\n\n"
        f"Write the Python script."
    )


# ─── Script execution ─────────────────────────────────────────────────────────

def _execute_script(script: str, mcp_server_dir: str) -> tuple:
    """Write script to temp file, run it, return (stdout, error_or_None)."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(textwrap.dedent(f"""\
import sys
sys.path.insert(0, {mcp_server_dir!r})
"""))
        f.write(script)
        tmp_path = f.name

    try:
        proc = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if proc.returncode != 0:
            err = (proc.stderr or proc.stdout or "unknown error").strip()
            return "", err
        stdout = proc.stdout.strip()
        if not stdout:
            return "", "Script produced no output"
        return stdout, None
    except subprocess.TimeoutExpired:
        return "", "Script timed out after 30s"
    finally:
        os.unlink(tmp_path)


def _strip_fences(text: str) -> str:
    """Remove markdown code fences if the LLM wrapped the script in them."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        # Drop first line (```python) and last line (```)
        inner = lines[1:] if lines[-1].strip() == "```" else lines[1:]
        if inner and inner[-1].strip() == "```":
            inner = inner[:-1]
        text = "\n".join(inner)
    return text



# ─── Factory ──────────────────────────────────────────────────────────────────

def create_mcp_script_solver_agent(**kwargs) -> MCPScriptSolverAgent:
    return MCPScriptSolverAgent(**kwargs)


# ─── CLI test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "What is the CAGR and Sharpe ratio for QQQ over 10 years?"
    agent = MCPScriptSolverAgent()
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
