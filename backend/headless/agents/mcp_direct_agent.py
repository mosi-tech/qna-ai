#!/usr/bin/env python3
"""
MCP Direct Agent

Answers user questions by directly calling MCP functions without generating scripts.
Useful for simple data fetches and aggregations that don't need complex logic.

Input:
    {
        "question": "Show QQQ ETF price",
        "blocks": [...],  # from ui_planner
        "selected_functions": ["financial_data__get_real_time_data", ...]
    }

Output:
    {
        "blocks_data": [
            {"blockId": "kpi-card-01", "data": {...}},
            ...
        ],
        "metadata": {...}
    }
"""

import asyncio
import json
from typing import Dict, Any, List

from agent_base import AgentBase, AgentResult


class MCPDirectAgent(AgentBase):
    """Agent that answers questions via direct MCP tool calling"""

    def __init__(
        self,
        prompt_file: str = "../../shared/config/agents/test/mcp_direct.txt",
        llm_model: str = None,  # Use task-based config by default
        llm_provider: str = None  # Use task-based config by default
    ):
        super().__init__(
            name="mcp_direct",
            task="MCP_DIRECT",
            prompt_file=prompt_file,
            llm_model=llm_model,
            llm_provider=llm_provider
        )

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "User's original question"},
                "blocks": {"type": "array", "description": "Blocks from ui_planner"},
                "selected_functions": {"type": "array", "description": "Selected MCP function names"}
            },
            "required": ["question", "blocks", "selected_functions"]
        }

    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "blocks_data": {"type": "array"},
                "raw_results": {"type": "object"},
                "metadata": {"type": "object"}
            },
            "required": ["blocks_data"]
        }

    async def _load_selected_tools(self, selected_functions: List[str]) -> List[Dict[str, Any]]:
        """Load MCP tools and filter to only selected functions"""
        from shared.llm.mcp_tools import _mcp_loader

        # Load tools from financial-data and analytics-engine servers
        # These are the same servers used by code_prompt_builder
        all_tools = await _mcp_loader.load_tools_for_service("code-prompt-builder")

        self.logger.info(f"Loaded {len(all_tools)} total tools from code-prompt-builder config")

        self.logger.info(f"Looking for matches for: {selected_functions}")

        # Extract just the function names from selected (after the double underscore)
        # E.g., "financial_data__get_real_time_data" → "get_real_time_data"
        selected_function_names = []
        for fn in selected_functions:
            if "__" in fn:
                selected_function_names.append(fn.split("__")[-1])
            else:
                selected_function_names.append(fn)

        self.logger.info(f"Extracted function names: {selected_function_names}")

        # Filter to only selected functions
        selected_tools = []
        for tool in all_tools:
            tool_name = tool.get("function", {}).get("name", "")

            # Extract the function name part (after the last `__`)
            if "__" in tool_name:
                function_name = tool_name.split("__")[-1]
            else:
                function_name = tool_name

            # Check if this function matches any selected
            if function_name in selected_function_names:
                selected_tools.append(tool)
                self.logger.info(f"  ✓ Matched: {tool_name}")

        self.logger.info(f"Filtered to {len(selected_tools)} tools for selected functions")

        return selected_tools

    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """Answer questions using direct MCP tool calling"""
        question = input_data.get("question", "")
        blocks = input_data.get("blocks", [])
        selected_functions = input_data.get("selected_functions", [])

        # Load and filter MCP tools
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        selected_tools = loop.run_until_complete(self._load_selected_tools(selected_functions))

        if not selected_tools:
            self.logger.warning(f"⚠️ No tools found for selected functions: {selected_functions}")

        # Override LLM service tools with selected subset
        # Pass tools directly to make_request to avoid ensure_tools_loaded reset
        tools_to_use = selected_tools if selected_tools else None

        if not tools_to_use:
            self.logger.warning(f"⚠️ No tools available for MCP calling")

        # Extract sub-questions from blocks
        sub_questions = [
            {
                "block_id": block.get("blockId"),
                "sub_question": block.get("sub_question"),
                "canonical_params": block.get("canonical_params", {}),
                "data_type": block.get("dataContract", {}).get("type")
            }
            for block in blocks
        ]

        # Build the user message
        function_list = "\n".join([f"- {fn}" for fn in selected_functions])
        sub_q_list = "\n".join([
            f"{i+1}. Block: {sq['block_id']}\n   Question: {sq['sub_question']}\n   Params: {sq['canonical_params']}"
            for i, sq in enumerate(sub_questions)
        ])

        user_message = f"""ORIGINAL QUESTION: {question}

SELECTED MCP FUNCTIONS:
{function_list}

BLOCKS TO ANSWER:
{sub_q_list}

TASK: Answer each block's sub-question by calling the appropriate MCP tools.

For each block:
1. Identify which MCP tool(s) to call
2. Extract parameters from canonical_params
3. Call the tool(s)
4. Format the result to match the block's data type (kpi, timeseries, categorical, table)

Return ONLY JSON with this structure:
{{
  "blocks_data": [
    {{
      "blockId": "block-id-01",
      "data": {{ ... }}  // formatted result matching dataContract.type
    }}
  ],
  "raw_results": {{ ... }},  // raw tool results
  "metadata": {{
    "functions_called": ["function1", "function2"],
    "total_calls": 2
  }}
}}

IMPORTANT: You have MCP tools available. USE THEM to answer the questions. Do not make up data.
"""

        try:
            # Make LLM request with tool calling
            # Pass tools directly to avoid ensure_tools_loaded reset
            if tools_to_use:
                self.logger.info(f"🔧 Passing {len(tools_to_use)} tools directly to LLM")

            response = self._make_llm_request(
                messages=[{"role": "user", "content": user_message}],
                tools=tools_to_use
            )

            # Check if the response was successful
            if not response.get("success"):
                error_msg = response.get("error", "Unknown error")
                raise Exception(f"LLM request failed: {error_msg}")

            # Check for tool calls
            self.logger.info(f"🔧 Response keys: {list(response.keys())}")
            self.logger.info(f"🔧 Response success: {response.get('success')}")
            self.logger.info(f"🔧 Response content length: {len(response.get('content', ''))}")
            self.logger.info(f"🔧 Response tool_calls count: {len(response.get('tool_calls', []))}")

            if response.get("tool_calls"):
                self.logger.info(f"🔧 LLM made {len(response['tool_calls'])} tool calls")

                # Execute tool calls manually
                tool_results = []
                for tc in response.get("tool_calls", []):
                    function_name = tc.get("function", {}).get("name")
                    arguments = tc.get("function", {}).get("arguments", {})

                    self.logger.info(f"  Executing: {function_name} with args: {list(arguments.keys())}")

                    # Call the MCP function via the shared MCP client
                    try:
                        result = self._execute_mcp_function(function_name, arguments)
                        tool_results.append({
                            "function": function_name,
                            "result": result,
                            "success": True
                        })
                    except Exception as e:
                        self.logger.warning(f"  ⚠️ Failed to execute {function_name}: {e}")
                        tool_results.append({
                            "function": function_name,
                            "error": str(e),
                            "success": False
                        })

                # Now ask LLM to format the results
                if tool_results:
                    self.logger.info(f"🔧 Got {len(tool_results)} tool results, asking LLM to format")

                    formatted_results = self._format_tool_results(tool_results)

                    followup_message = f"""TOOL EXECUTION RESULTS:

{formatted_results}

TASK: Based on these tool results, format the answer for each block.

IMPORTANT: Do NOT call any more tools. Just return JSON with the formatted results.

Return ONLY JSON with this structure:
{{
  "blocks_data": [
    {{
      "blockId": "block-id-01",
      "data": {{ ... }}
    }}
  ],
  "metadata": {{
    "total_calls": {len(tool_results)}
  }}
}}
"""

                    # Build proper message history with assistant's tool_calls message
                    # We need to include the tool results as part of the conversation history
                    followup_messages = [
                        {"role": "user", "content": user_message},
                        {"role": "assistant", "tool_calls": response.get("tool_calls", [])},
                        {"role": "tool", "content": json.dumps(tool_results, indent=2)},
                        {"role": "user", "content": followup_message}
                    ]

                    # Pass empty tools list to prevent further tool calls
                    followup_response = self._make_llm_request(messages=followup_messages, tools=[])

                    self.logger.info(f"🔧 Followup response keys: {list(followup_response.keys())}")
                    self.logger.info(f"🔧 Followup response success: {followup_response.get('success')}")

                    # Check if the response was successful
                    if not followup_response.get("success"):
                        error_msg = followup_response.get("error", "Unknown error")
                        raise Exception(f"LLM followup request failed: {error_msg}")

                    content = followup_response.get("content", "").strip()
                    self.logger.info(f"🔧 Followup content length: {len(content)}, content preview: {content[:200]}")

                    if not content:
                        # Check if there are tool_calls in the response (LLLM might be calling more tools)
                        followup_tool_calls = followup_response.get("tool_calls", [])
                        if followup_tool_calls:
                            self.logger.warning(f"⚠️  LLM made {len(followup_tool_calls)} more tool calls instead of returning JSON")
                            self.logger.warning(f"⚠️  Tool calls: {json.dumps(followup_tool_calls, indent=2)}")
                            raise Exception(f"LLM made additional tool calls ({len(followup_tool_calls)}) instead of returning formatted results. This may indicate that the tool results didn't contain the expected information.")
                        else:
                            raise Exception("LLM returned empty content without tool calls")

                    result_data = self._safe_parse_json(content)
                else:
                    raise Exception("No tool results after executing tool calls")

            else:
                # No tool calls, parse JSON content directly
                self.logger.info("No tool calls, parsing content as JSON")
                content = response.get("content", "").strip()

                if not content:
                    raise Exception("LLM returned empty content without tool calls")

                self.logger.info(f"🔧 Direct response content length: {len(content)}, preview: {content[:200]}")
                result_data = self._safe_parse_json(content)

            # Validate result structure
            if "blocks_data" not in result_data:
                raise Exception("Missing 'blocks_data' field in response")

            # Ensure blocks_data matches expected block IDs
            result_block_ids = {b["blockId"] for b in result_data["blocks_data"]}
            expected_block_ids = {b["blockId"] for b in blocks}

            if result_block_ids != expected_block_ids:
                self.logger.warning(f"Block ID mismatch. Expected: {expected_block_ids}, Got: {result_block_ids}")

            self.logger.info(f"✅ Answered {len(result_data['blocks_data'])} blocks via MCP tool calling")

            return AgentResult(success=True, data=result_data)

        except Exception as e:
            self.logger.error(f"❌ Failed to answer via MCP: {e}")
            return AgentResult(success=False, error=str(e))

    def _execute_mcp_function(self, function_name: str, arguments: Dict) -> Any:
        """Execute an MCP function via the MCP client"""
        from shared.integrations.mcp.mcp_client import mcp_client
        import asyncio

        try:
            # Get event loop or create new one
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            # Call the tool async
            result = loop.run_until_complete(mcp_client.call_tool(function_name, arguments))

            # Extract actual result from response
            if hasattr(result, 'content') and result.content:
                text_content = result.content[0].text
                try:
                    import json
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
def create_mcp_direct_agent(**kwargs) -> MCPDirectAgent:
    """Create MCP Direct agent with optional overrides"""
    return MCPDirectAgent(**kwargs)


# For direct execution
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        question = sys.argv[1]
        agent = MCPDirectAgent()

        # Mock input for testing
        mock_input = {
            "question": question,
            "blocks": [
                {
                    "blockId": "kpi-card-01",
                    "sub_question": "What is the current price of QQQ?",
                    "canonical_params": {"ticker": "QQQ"},
                    "dataContract": {"type": "kpi"}
                }
            ],
            "selected_functions": ["get_real_time_data"]
        }

        result = agent.execute(mock_input)
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print("Usage: python mcp_direct_agent.py \"Your question here\"")