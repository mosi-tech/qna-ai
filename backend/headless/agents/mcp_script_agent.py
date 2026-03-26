#!/usr/bin/env python3
"""
MCP Script Agent

Solves ONE block's sub_question by having the LLM write a Python script that:
  1. Imports directly from analytics / financial modules (no MCP protocol overhead)
  2. Fetches raw data AND processes / aggregates it inside the script
  3. print(json.dumps(compact_result)) — only the processed result leaves the script

This avoids the context-overflow problem of mcp_block_solver_agent, where raw API
responses (e.g. 3 650 rows of OHLCV) were injected back into the LLM context.

Flow:
    LLM call 1  →  writes Python script (no tool calls)
    subprocess  →  executes script, captures stdout JSON
    (optional)  →  LLM call 2 formats result to exact dataContract shape

Input:
    {
        "blockId": "FKLineChart",
        "sub_question": "What is the CAGR and Sharpe ratio for QQQ over 10 years?",
        "canonical_params": {"ticker": "QQQ", "period": "10y"},
        "dataContract": {
            "type": "kpi",
            "description": "...",
            "fields": ["cagr", "sharpe", "max_drawdown"]
        }
    }

Output:
    {
        "blockId": "FKLineChart",
        "data": { ... },
        "script": "...",          // generated script (for debugging)
        "success": true
    }
"""

import asyncio
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent_base import AgentBase, AgentResult

# Path to mcp-server directory so generated scripts can import from it
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
_MCP_SERVER_DIR = _BACKEND_DIR / "mcp-server"


# ─── System prompt for script generation ──────────────────────────────────────

_SCRIPT_SYSTEM_PROMPT = """\
You are a financial data engineer. Write a self-contained Python script that \
answers ONE specific sub-question by fetching and processing financial data.

The script runs with these paths already on sys.path:
  - backend/mcp-server   (import analytics, financial.functions_real, etc.)
  - backend              (import shared.*)

Available imports
─────────────────
Analytics (pure-Python, no I/O overhead):
  from analytics import (
      calculate_annualized_return, calculate_annualized_volatility,
      calculate_sharpe_ratio, calculate_drawdown_analysis,
      calculate_beta, calculate_correlation, calculate_var,
      calculate_rsi, calculate_macd, calculate_bollinger_bands,
      calculate_monthly_returns, calculate_cumulative_returns,
      # ... and many more calculate_* / analyze_* / detect_* functions
  )

Financial data (real API calls — may return large raw data):
  from financial.functions_real import REAL_FINANCIAL_FUNCTIONS
  fn = REAL_FINANCIAL_FUNCTIONS["get_historical_data"]
  raw = fn(symbol="QQQ", start="2015-01-01", end="2025-01-01", timeframe="1Day")
  # raw = {"success": True, "data": [{"timestamp": ..., "open": ..., "close": ...}, ...]}

  Other useful keys in REAL_FINANCIAL_FUNCTIONS:
    "get_latest_quotes", "get_fundamentals", "get_positions",
    "get_account", "get_portfolio_history", "get_dividends",
    "get_market_news", "get_most_active_stocks", "get_top_gainers"

Rules
─────
1. ALWAYS process / aggregate raw data inside the script. Never output raw rows.
   e.g. fetch 3 650 rows of OHLCV → compute CAGR, Sharpe, drawdown → output 3 numbers.
2. The LAST line must be:  print(json.dumps(result))
3. Shape result to match the dataContract type exactly:
   kpi        → {"cards": [{"label": str, "value": str, "delta": float|null}]}
   timeseries → {"data": [{"date": "YYYY-MM-DD", <field>: value, ...}],
                  "series": [{"key": str, "label": str}]}
   categorical → {"data": [{"label": str, "value": float}]}
   table-rows  → {"columns": [{"key": str, "label": str}], "rows": [...]}
   ranked      → {"data": [{"label": str, "value": float, "delta": float|null}]}
   matrix      → {"rows": [str], "cols": [str],
                  "cells": [[value, ...], ...]}   (rows × cols grid)
4. Use try/except around API calls; on failure return an empty-but-valid structure.
5. Do NOT import requests, httpx, or call URLs directly.
6. Do NOT include markdown fences or any explanation — output the raw Python only.\
"""


class MCPScriptAgent(AgentBase):
    """Agent that solves a single block's sub_question via LLM-generated Python script"""

    def __init__(
        self,
        llm_model: Optional[str] = None,
        llm_provider: Optional[str] = None,
        script_timeout: int = 60,
    ):
        super().__init__(
            name="mcp_script",
            task="MCP_DIRECT",
            prompt_file=None,
            llm_model=llm_model,
            llm_provider=llm_provider,
        )
        self.system_prompt = _SCRIPT_SYSTEM_PROMPT
        self.script_timeout = script_timeout

    # ── AgentBase schema stubs ─────────────────────────────────────────────────

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
                "script":           {"type": "string"},
                "functions_called": {"type": "array"},
                "success":          {"type": "boolean"},
            },
            "required": ["blockId", "data", "success"],
        }

    # ── Main process ──────────────────────────────────────────────────────────

    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        block_id        = input_data.get("blockId", "unknown")
        sub_question    = input_data.get("sub_question", "")
        canonical_params = input_data.get("canonical_params", {})
        data_contract   = input_data.get("dataContract", {})

        contract_type   = data_contract.get("type", "kpi")
        fields          = data_contract.get("fields", [])
        description     = data_contract.get("description", "")

        # ── Step 1: ask LLM to write the script ───────────────────────────────
        user_message = (
            f"BLOCK ID: {block_id}\n"
            f"SUB-QUESTION: {sub_question}\n"
            f"CANONICAL PARAMS: {json.dumps(canonical_params)}\n"
            f"DATA CONTRACT TYPE: {contract_type}\n"
            f"DESCRIPTION: {description}\n"
            f"EXPECTED FIELDS: {fields}\n\n"
            f"Write a Python script that answers the sub-question and prints a JSON "
            f"result shaped to the '{contract_type}' dataContract with fields {fields}."
        )

        self.logger.info(f"📝 [{block_id}] Asking LLM to write data-fetch script")
        t0 = time.time()

        response = self._make_llm_request(
            messages=[{"role": "user", "content": user_message}],
            tools=None,  # No tools — pure text generation
        )

        if not response.get("success"):
            return AgentResult(
                success=False,
                error=f"LLM script generation failed: {response.get('error', 'unknown')}",
            )

        script_code = response.get("content", "").strip()

        # Strip accidental markdown fences
        if script_code.startswith("```"):
            lines = script_code.split("\n")
            script_code = "\n".join(
                l for l in lines if not l.startswith("```")
            ).strip()

        gen_elapsed = time.time() - t0
        self.logger.info(
            f"📝 [{block_id}] Script generated in {gen_elapsed:.1f}s "
            f"({len(script_code)} chars)"
        )

        if not script_code:
            return AgentResult(success=False, error="LLM returned empty script")

        # ── Step 2: execute the script ────────────────────────────────────────
        exec_result = self._execute_script(block_id, script_code)

        if not exec_result["success"]:
            # Optionally retry once with the error injected back into the prompt
            self.logger.warning(
                f"⚠️  [{block_id}] Script failed: {exec_result['error'][:200]} — retrying"
            )
            exec_result = self._retry_with_error(
                block_id, user_message, script_code, exec_result["error"]
            )

        if not exec_result["success"]:
            return AgentResult(
                success=False,
                error=f"Script execution failed: {exec_result['error']}",
            )

        data = exec_result["data"]

        # Ensure blockId is present
        if isinstance(data, dict) and "blockId" not in data:
            data["blockId"] = block_id

        total_elapsed = time.time() - t0
        self.logger.info(
            f"✅ [{block_id}] Solved via script in {total_elapsed:.1f}s total"
        )

        return AgentResult(
            success=True,
            data={
                "blockId":          block_id,
                "data":             data,
                "script":           script_code,
                "functions_called": _infer_functions_called(script_code),
            },
        )

    # ── Script execution ──────────────────────────────────────────────────────

    def _execute_script(self, block_id: str, script_code: str) -> Dict[str, Any]:
        """Write script to a temp file and execute it as a subprocess."""
        env = self._build_script_env()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, prefix=f"mcp_script_{block_id}_"
        ) as f:
            f.write(script_code)
            tmp_path = f.name

        try:
            t0 = time.time()
            result = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True,
                text=True,
                timeout=self.script_timeout,
                cwd=str(_MCP_SERVER_DIR),
                env=env,
            )
            elapsed = time.time() - t0

            self.logger.info(
                f"  [{block_id}] Script exited {result.returncode} in {elapsed:.1f}s "
                f"— stdout {len(result.stdout)} chars"
            )

            if result.returncode != 0:
                stderr_tail = result.stderr.strip().split("\n")[-5:]
                return {
                    "success": False,
                    "error": "\n".join(stderr_tail),
                    "stderr": result.stderr,
                }

            stdout = result.stdout.strip()
            if not stdout:
                return {"success": False, "error": "Script produced no output"}

            # Find last line that looks like JSON (script may print debug lines)
            data = None
            for line in reversed(stdout.split("\n")):
                line = line.strip()
                if line.startswith("{") or line.startswith("["):
                    try:
                        data = json.loads(line)
                        break
                    except json.JSONDecodeError:
                        continue

            if data is None:
                return {
                    "success": False,
                    "error": f"Script stdout was not valid JSON: {stdout[:300]}",
                }

            return {"success": True, "data": data}

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Script timed out after {self.script_timeout}s",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    def _retry_with_error(
        self,
        block_id: str,
        original_user_msg: str,
        failed_script: str,
        error: str,
    ) -> Dict[str, Any]:
        """Ask the LLM to fix the script given the execution error."""
        fix_message = (
            f"{original_user_msg}\n\n"
            f"Your previous script failed with this error:\n{error}\n\n"
            f"Previous script:\n```python\n{failed_script}\n```\n\n"
            f"Write a corrected Python script. Return ONLY raw Python, no markdown."
        )

        self.logger.info(f"🔁 [{block_id}] Retrying with error context")
        response = self._make_llm_request(
            messages=[{"role": "user", "content": fix_message}],
            tools=None,
        )

        if not response.get("success"):
            return {"success": False, "error": "Retry LLM call failed"}

        fixed_code = response.get("content", "").strip()
        if fixed_code.startswith("```"):
            lines = fixed_code.split("\n")
            fixed_code = "\n".join(
                l for l in lines if not l.startswith("```")
            ).strip()

        if not fixed_code:
            return {"success": False, "error": "Retry produced empty script"}

        return self._execute_script(block_id, fixed_code)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _build_script_env(self) -> Dict[str, str]:
        """Build subprocess environment with correct PYTHONPATH."""
        env = os.environ.copy()
        existing_path = env.get("PYTHONPATH", "")
        extra_paths = [str(_MCP_SERVER_DIR), str(_BACKEND_DIR)]
        env["PYTHONPATH"] = os.pathsep.join(extra_paths + ([existing_path] if existing_path else []))
        return env


def _infer_functions_called(script: str) -> List[str]:
    """Rough heuristic — extract function names used from the script."""
    import re
    fns = re.findall(
        r'(?:from analytics import|REAL_FINANCIAL_FUNCTIONS\[")[^\]\'"]+', script
    )
    # Also catch calculate_*/analyze_* calls
    calls = re.findall(r'\b(calculate_\w+|analyze_\w+|detect_\w+|get_\w+)\s*\(', script)
    return list(dict.fromkeys(fns + calls))  # dedup, preserve order


# ─── Factory ──────────────────────────────────────────────────────────────────

def create_mcp_script_agent(**kwargs) -> MCPScriptAgent:
    return MCPScriptAgent(**kwargs)


# ─── CLI test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    question = sys.argv[1] if len(sys.argv) > 1 else "What is the CAGR and Sharpe ratio for QQQ over 10 years?"

    agent = MCPScriptAgent()
    result = agent.execute({
        "blockId": "FKMetricGrid",
        "sub_question": question,
        "canonical_params": {"ticker": "QQQ", "period": "10y"},
        "dataContract": {
            "type": "kpi",
            "description": "CAGR, Sharpe ratio, max drawdown for QQQ",
            "fields": ["cagr", "sharpe", "max_drawdown"],
        },
    })
    print(json.dumps(result.to_dict(), indent=2))
