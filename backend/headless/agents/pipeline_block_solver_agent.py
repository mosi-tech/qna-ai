#!/usr/bin/env python3
"""
Pipeline Block Solver Agent

Solves ONE block's sub_question using the same flow as AnalysisPipeline:
CodePromptBuilderService pre-selects functions + AnalysisService generates the script.

Flow
────
1. CodePromptBuilderService.create_code_prompt_messages()
   - Selects relevant MCP functions (LLM call)
   - Fetches full docstrings via get_function_docstring
   - Returns simulated conversation with pre-loaded docs

2. AnalysisService.analyze_question(question, messages)
   - messages = [user: question] + simulated_convo  (same as AnalysisPipeline line 590)
   - Runs conversation loop with write_and_validate
   - Returns analysis_result

3. Format result to dataContract shape (single LLM call)
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

from agent_base import AgentBase, AgentResult

logger = logging.getLogger(__name__)

_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

# Load .env from apiServer (same as step5_analysis.py)
try:
    from dotenv import load_dotenv
    load_dotenv(_BACKEND_DIR / "apiServer" / ".env")
except ImportError:
    pass


_FORMAT_SYSTEM_PROMPT = """\
You are a financial data formatter. You receive the raw result of a script execution
and must format it into the exact dataContract shape requested.

Rules
─────
1. Return ONLY JSON — no prose, no markdown fences.
2. Use EXACTLY the field names listed in dataContract.fields.
3. Shape output to match dataContract.type:
   - kpi        → {"cards": [{"label": str, "value": str, "delta": float|null}]}
   - timeseries → {"data": [{"date": "YYYY-MM-DD", <field>: value}], "series": [{"key": str, "label": str}]}
   - categorical → {"data": [{"label": str, "value": float}]}
   - table-rows  → {"columns": [{"key": str, "label": str}], "rows": [...]}
   - ranked      → {"data": [{"label": str, "value": float, "delta": float|null}]}
4. Format numeric values as human-readable strings for kpi cards (e.g. "14.2%" not 0.142).
5. Keep raw numbers for chart/table data."""


class PipelineBlockSolverAgent(AgentBase):

    def __init__(self, llm_model: str = None, llm_provider: str = None):
        super().__init__(
            name="pipeline_block_solver",
            task="PIPELINE",
            prompt_file=None,
            llm_model=llm_model,
            llm_provider=llm_provider,
        )
        self.system_prompt = _FORMAT_SYSTEM_PROMPT
        self._analysis_svc = None
        self._prompt_builder = None

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
        """Sync entry point — wraps the async implementation."""
        return asyncio.run(self._process_async(input_data))

    async def execute_async(self, input_data: Dict[str, Any]) -> AgentResult:
        """Async entry point — for use with asyncio.gather in orchestrator."""
        return await self._process_async(input_data)

    async def _process_async(self, input_data: Dict[str, Any]) -> AgentResult:
        block_id         = input_data.get("blockId", "unknown")
        sub_question     = input_data.get("sub_question", "")
        canonical_params = input_data.get("canonical_params", {})
        data_contract    = input_data.get("dataContract", {})

        # Include dataContract in the query so the script outputs the right shape
        enriched_query = (
            f"{sub_question}\n\n"
            f"Output must match this data contract:\n"
            f"type: {data_contract.get('type')}\n"
            f"fields: {data_contract.get('fields', [])}\n"
            f"canonical params: {json.dumps(canonical_params)}"
        )

        self.logger.info(f"🔧 [{block_id}] Running pipeline for: {sub_question[:80]}")

        # ── Step 1: Build enriched prompt via CodePromptBuilderService ─────────
        self.logger.info(f"📖 [{block_id}] Building enriched prompt (select + docstrings)…")
        try:
            prompt_result = await self._build_prompt(enriched_query)
        except Exception as e:
            return AgentResult(success=False, error=f"Prompt builder failed: {e}")

        if prompt_result.get("status") != "success":
            return AgentResult(
                success=False,
                error=f"Prompt builder error: {prompt_result.get('error', 'unknown')}"
            )

        functions_selected = prompt_result.get("selected_functions", [])
        # Prepend user message before simulated convo — mirrors AnalysisPipeline line 590
        simulated_convo = prompt_result.get("user_messages", [])
        messages = [{"role": "user", "content": enriched_query}] + simulated_convo
        self.logger.info(
            f"📖 [{block_id}] Selected {len(functions_selected)} functions: {functions_selected}"
        )

        # ── Step 2: Run AnalysisService (script generation + execution) ────────
        self.logger.info(f"✍️  [{block_id}] Running analysis service…")
        try:
            analysis_result = await self._run_analysis(enriched_query, messages)
        except Exception as e:
            return AgentResult(success=False, error=f"Analysis failed: {e}")

        if not analysis_result.get("success"):
            return AgentResult(
                success=False,
                error=f"Analysis error: {analysis_result.get('error', 'unknown')}"
            )

        raw_result = (
            analysis_result.get("data", {}).get("analysis_result") or
            analysis_result.get("data", {}).get("raw_content") or
            analysis_result.get("data", {})
        )
        self.logger.info(f"✅ [{block_id}] Analysis complete, formatting result…")

        # ── Step 3: Format to dataContract shape ──────────────────────────────
        format_msg = (
            f"BLOCK ID: {block_id}\n"
            f"SUB-QUESTION: {sub_question}\n"
            f"DATA CONTRACT TYPE: {data_contract.get('type')}\n"
            f"EXPECTED FIELDS: {data_contract.get('fields', [])}\n\n"
            f"ANALYSIS RESULT:\n{json.dumps(raw_result, indent=2, default=str)[:1500]}\n\n"
            f"Format into the dataContract shape. Return ONLY JSON."
        )

        format_resp = await self._make_llm_request_async(
            messages=[{"role": "user", "content": format_msg}],
        )
        if not format_resp.get("success"):
            return AgentResult(success=False, error=f"Format call failed: {format_resp.get('error')}")

        try:
            result_data = self._safe_parse_json(format_resp.get("content", ""))
        except Exception as e:
            return AgentResult(success=False, error=f"Invalid format JSON: {e}")

        result_data["blockId"]          = block_id
        result_data["functions_called"] = functions_selected

        self.logger.info(f"✅ [{block_id}] Done — functions: {functions_selected}")
        return AgentResult(success=True, data=result_data)

    # ── Async helpers ─────────────────────────────────────────────────────────

    async def _build_prompt(self, query: str) -> Dict[str, Any]:
        from shared.analyze import CodePromptBuilderService
        if self._prompt_builder is None:
            self._prompt_builder = CodePromptBuilderService()
        return await self._prompt_builder.create_code_prompt_messages(query)

    async def _run_analysis(self, question: str, messages: List[Dict]) -> Dict[str, Any]:
        from shared.analyze import AnalysisService
        if self._analysis_svc is None:
            self._analysis_svc = AnalysisService()
        return await self._analysis_svc.analyze_question(question, messages=messages)

    def _make_llm_request(self, messages, tools=None, system_prompt_override=None):
        original = self.system_prompt
        if system_prompt_override:
            self.system_prompt = system_prompt_override
        try:
            return super()._make_llm_request(messages=messages, tools=tools)
        finally:
            self.system_prompt = original

    async def _make_llm_request_async(self, messages, tools=None):
        """Async variant — avoids nested asyncio.run() when called from within a running loop."""
        return await self.llm_service.make_request(
            messages=messages,
            system_prompt=self.system_prompt,
            tools=tools,
        )


# ─── Factory ──────────────────────────────────────────────────────────────────

def create_pipeline_block_solver_agent(**kwargs) -> PipelineBlockSolverAgent:
    return PipelineBlockSolverAgent(**kwargs)


# ─── CLI test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "What is the CAGR and Sharpe ratio for QQQ over 10 years?"
    agent = PipelineBlockSolverAgent()
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
