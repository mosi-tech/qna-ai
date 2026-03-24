#!/usr/bin/env python3
"""
MCP Block Solver Agent

Solves ONE block's sub_question using real MCP tools (financial + analytics servers).
Designed to be run in parallel across multiple blocks via ThreadPoolExecutor.

Input:
    {
        "blockId": "FKLineChart",
        "sub_question": "What is the daily closing price of QQQ over 10 years?",
        "canonical_params": {"ticker": "QQQ", "period": "10y"},
        "dataContract": {
            "type": "timeseries",
            "description": "...",
            "fields": ["date", "price"]
        }
    }

Output:
    {
        "blockId": "FKLineChart",
        "data": { ... },   // shaped to match dataContract.fields
        "functions_called": ["get_historical_data"],
        "success": true
    }
"""

import asyncio
import json
from typing import Dict, Any, List

from agent_base import AgentBase, AgentResult


class MCPBlockSolverAgent(AgentBase):
    """Agent that solves a single block's sub_question via direct MCP tool calling"""

    SYSTEM_PROMPT = """You are a financial data fetcher. Your job is to answer ONE specific sub-question by calling MCP tools and returning structured data.

Rules:
1. Call the appropriate MCP tool(s) to fetch real data
2. Use canonical_params as hints for tool arguments (ticker, period, etc.)
3. Return data with EXACTLY the field names listed in dataContract.fields
4. Shape the output to match the dataContract type:
   - timeseries: {"data": [{"date": "...", <fields>: value, ...}], "series": [{"key": "<field>", "label": "<label>"}]}
   - kpi: {"cards": [{"label": "...", "value": "...", "delta": number}]}
   - categorical: {"data": [{"label": "...", "value": number}]}
   - table-rows: {"columns": [{"key": "...", "label": "..."}], "rows": [...]}
   - ranked-list: {"data": [{"label": "...", "value": number, "delta": number}]}
5. Do NOT make up data — always call MCP tools first
6. Return ONLY JSON, no prose"""

    def __init__(
        self,
        llm_model: str = None,
        llm_provider: str = None
    ):
        super().__init__(
            name="mcp_block_solver",
            task="MCP_DIRECT",
            prompt_file=None,
            llm_model=llm_model,
            llm_provider=llm_provider
        )
        # Set system prompt from class constant (no prompt file)
        self.system_prompt = self.SYSTEM_PROMPT

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "blockId": {"type": "string", "description": "Block identifier"},
                "sub_question": {"type": "string", "description": "The specific sub-question this block answers"},
                "canonical_params": {"type": "object", "description": "Hint parameters (ticker, period, etc.)"},
                "dataContract": {"type": "object", "description": "Contract describing the expected data shape"}
            },
            "required": ["blockId", "sub_question", "dataContract"]
        }

    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "blockId": {"type": "string"},
                "data": {"type": "object"},
                "functions_called": {"type": "array"},
                "success": {"type": "boolean"}
            },
            "required": ["blockId", "data", "functions_called"]
        }

    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """Solve a single block's sub_question using MCP tools"""
        block_id = input_data.get("blockId", "unknown")
        sub_question = input_data.get("sub_question", "")
        canonical_params = input_data.get("canonical_params", {})
        data_contract = input_data.get("dataContract", {})

        # Load ALL MCP tools (same service as mcp_direct_agent)
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        tools = loop.run_until_complete(self._load_all_tools())

        if not tools:
            self.logger.warning(f"No MCP tools loaded for block {block_id}")

        # Build user message
        user_message = f"""BLOCK ID: {block_id}
SUB-QUESTION: {sub_question}
CANONICAL PARAMS: {json.dumps(canonical_params)}
DATA CONTRACT TYPE: {data_contract.get('type', 'unknown')}
EXPECTED FIELDS: {data_contract.get('fields', [])}

Call the appropriate MCP tool(s) to answer the sub-question.
Return JSON with this structure:
{{
  "blockId": "{block_id}",
  "data": {{ ... shaped to dataContract type with the exact field names above ... }},
  "functions_called": ["tool_name"]
}}"""

        try:
            # Step 1: First LLM call with tools — get tool_calls
            self.logger.info(f"🔧 [{block_id}] First LLM call with {len(tools)} tools")
            response = self._make_llm_request(
                messages=[{"role": "user", "content": user_message}],
                tools=tools if tools else None
            )

            if not response.get("success"):
                raise Exception(f"LLM request failed: {response.get('error', 'Unknown error')}")

            self.logger.info(
                f"🔧 [{block_id}] tool_calls={len(response.get('tool_calls', []))}, "
                f"content_len={len(response.get('content', ''))}"
            )

            if response.get("tool_calls"):
                # Step 2: Execute each tool_call
                tool_results = []
                for tc in response.get("tool_calls", []):
                    function_name = tc.get("function", {}).get("name")
                    arguments = tc.get("function", {}).get("arguments", {})

                    self.logger.info(f"  [{block_id}] Executing: {function_name} with args: {list(arguments.keys())}")

                    try:
                        result = self._execute_mcp_function(function_name, arguments)
                        tool_results.append({
                            "function": function_name,
                            "result": result,
                            "success": True
                        })
                    except Exception as e:
                        self.logger.warning(f"  [{block_id}] Failed to execute {function_name}: {e}")
                        tool_results.append({
                            "function": function_name,
                            "error": str(e),
                            "success": False
                        })

                if not tool_results:
                    raise Exception("No tool results after executing tool calls")

                # Step 3: Second LLM call with tool results + empty tools — get formatted JSON
                formatted_results = self._format_tool_results(tool_results)
                functions_called = [tr["function"] for tr in tool_results if tr.get("success")]

                followup_message = f"""TOOL EXECUTION RESULTS:

{formatted_results}

TASK: Based on these tool results, format the answer for block "{block_id}".

IMPORTANT: Do NOT call any more tools. Just return JSON with the formatted result.

Return ONLY JSON with this structure:
{{
  "blockId": "{block_id}",
  "data": {{ ... shaped to {data_contract.get('type', 'unknown')} type with fields {data_contract.get('fields', [])} ... }},
  "functions_called": {json.dumps(functions_called)}
}}"""

                followup_messages = [
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "tool_calls": response.get("tool_calls", [])},
                    {"role": "tool", "content": json.dumps(tool_results, indent=2)},
                    {"role": "user", "content": followup_message}
                ]

                # Pass empty tools list to prevent further tool calls
                followup_response = self._make_llm_request(messages=followup_messages, tools=[])

                if not followup_response.get("success"):
                    raise Exception(f"LLM followup request failed: {followup_response.get('error', 'Unknown error')}")

                content = followup_response.get("content", "").strip()

                self.logger.info(
                    f"🔧 [{block_id}] Followup content_len={len(content)}, "
                    f"preview={content[:150]}"
                )

                if not content:
                    # Check if LLM made additional (unexpected) tool calls
                    extra_tool_calls = followup_response.get("tool_calls", [])
                    if extra_tool_calls:
                        self.logger.warning(
                            f"[{block_id}] LLM made {len(extra_tool_calls)} extra tool calls instead of returning JSON"
                        )
                        raise Exception(
                            f"LLM made additional tool calls ({len(extra_tool_calls)}) "
                            "instead of returning formatted results"
                        )
                    raise Exception("LLM returned empty content without tool calls")

                result_data = self._safe_parse_json(content)

            else:
                # No tool calls — parse JSON content directly
                self.logger.info(f"[{block_id}] No tool calls, parsing content as JSON")
                content = response.get("content", "").strip()

                if not content:
                    raise Exception("LLM returned empty content without tool calls")

                self.logger.info(f"🔧 [{block_id}] Direct content_len={len(content)}, preview={content[:150]}")
                result_data = self._safe_parse_json(content)

            # Normalise output: ensure blockId and functions_called are present
            if "blockId" not in result_data:
                result_data["blockId"] = block_id
            if "functions_called" not in result_data:
                result_data["functions_called"] = []

            self.logger.info(
                f"✅ [{block_id}] Solved via MCP — "
                f"functions: {result_data.get('functions_called', [])}"
            )

            return AgentResult(success=True, data=result_data)

        except Exception as e:
            self.logger.error(f"❌ [{block_id}] Failed to solve block: {e}")
            return AgentResult(success=False, error=str(e))

    async def _load_all_tools(self) -> List[Dict[str, Any]]:
        """Load ALL MCP tools from code-prompt-builder service config"""
        from shared.llm.mcp_tools import _mcp_loader

        all_tools = await _mcp_loader.load_tools_for_service("code-prompt-builder")
        self.logger.info(f"Loaded {len(all_tools)} total tools from code-prompt-builder config")
        return all_tools

    def _execute_mcp_function(self, function_name: str, arguments: Dict) -> Any:
        """Execute an MCP function via the MCP client"""
        from shared.integrations.mcp.mcp_client import mcp_client

        try:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            result = loop.run_until_complete(mcp_client.call_tool(function_name, arguments))

            # Extract actual result from response
            if hasattr(result, 'content') and result.content:
                text_content = result.content[0].text
                try:
                    parsed = json.loads(text_content)
                    return parsed
                except json.JSONDecodeError:
                    return text_content
            return result

        except Exception as e:
            self.logger.warning(f"Failed to execute {function_name}: {e}")
            raise

    def _format_tool_results(self, tool_results: List[Dict]) -> str:
        """Format tool results for display"""
        lines = []
        for tr in tool_results:
            fn = tr.get("function")
            if tr.get("success"):
                lines.append(f"✅ {fn}: {json.dumps(tr.get('result', {}), indent=2)}")
            else:
                lines.append(f"❌ {fn}: {tr.get('error', 'Unknown error')}")
        return "\n".join(lines)


# Factory function for easy creation
def create_mcp_block_solver_agent(**kwargs) -> MCPBlockSolverAgent:
    """Create MCP Block Solver agent with optional overrides"""
    return MCPBlockSolverAgent(**kwargs)


# For direct execution / testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        sub_question = sys.argv[1]
        agent = MCPBlockSolverAgent()

        mock_input = {
            "blockId": "FKLineChart",
            "sub_question": sub_question,
            "canonical_params": {"ticker": "QQQ", "period": "10y"},
            "dataContract": {
                "type": "timeseries",
                "description": "Daily closing price",
                "fields": ["date", "price"]
            }
        }

        result = agent.execute(mock_input)
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print("Usage: python mcp_block_solver_agent.py \"What is the daily closing price of QQQ?\"")
