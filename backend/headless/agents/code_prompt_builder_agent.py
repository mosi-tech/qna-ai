#!/usr/bin/env python3
"""
Code Prompt Builder Agent

Analyzes financial questions and selects relevant MCP functions to build enriched prompts for code generation.

Input:
    {
        "question": "Show QQQ ETF price",
        "context": {...}
    }

Output:
    {
        "enriched_prompt": "...",
        "selected_functions": [...],
        "metadata": {...}
    }
"""

import json
from typing import Dict, Any, List, Optional

from agent_base import AgentBase, AgentResult


class CodePromptBuilderAgent(AgentBase):
    """Agent that selects MCP functions and builds enriched prompts"""

    def __init__(
        self,
        prompt_file: str = "../../shared/config/agents/test/code_prompt_builder.txt",  # Use test prompt for compatibility
        llm_model: str = None,  # Use task-based config by default
        llm_provider: str = None  # Use task-based config by default
    ):
        super().__init__(
            name="code_prompt_builder",
            task="CODE_PROMPT_BUILDER",
            prompt_file=prompt_file,
            llm_model=llm_model,
            llm_provider=llm_provider
        )

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "User's financial question"},
                "context": {"type": "object", "description": "Additional context"},
                "blocks": {"type": "array", "description": "Dashboard blocks from ui_planner"}
            },
            "required": ["question"]
        }

    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "enriched_prompt": {"type": "string"},
                "selected_functions": {"type": "array"},
                "metadata": {"type": "object"}
            },
            "required": ["enriched_prompt", "selected_functions"]
        }

    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """Build enriched prompt for code generation"""
        question = input_data.get("question", "")
        context = input_data.get("context", {})
        blocks = input_data.get("blocks", [])

        # Get available MCP function schemas
        # In a real implementation, this would query the MCP servers
        function_schemas = self._get_available_functions()

        # Build blocks context if available
        blocks_context = ""
        if blocks:
            blocks_context = self._build_blocks_context(blocks)

        # Build user message for LLM
        user_message = f"""USER QUESTION: {question}

{blocks_context}

AVAILABLE MCP FUNCTIONS (Select 3-6 most relevant):
{function_schemas}

TASK: Analyze this financial question and build an enriched prompt for code generation.

Please:
1. Analyze what financial analysis is being requested
2. Select 3-6 relevant MCP functions that best address the requirements
3. Build a comprehensive enriched prompt for the code generator

Return your output in the exact JSON format specified in the system prompt.
"""

        try:
            # Make LLM request
            response = self._make_llm_request(
                messages=[{"role": "user", "content": user_message}]
            )

            content = response.get("content", "").strip()
            result_data = self._safe_parse_json(content)

            # Validate result structure
            if "enriched_prompt" not in result_data:
                raise Exception("Missing 'enriched_prompt' field in response")

            # Add metadata
            result_data.setdefault("metadata", {}).update({
                "question": question,
                "timestamp": self._now_iso(),
                "function_count": len(result_data.get("selected_functions", [])),
                "block_count": len(blocks)
            })

            self.logger.info(f"✅ Built enriched prompt ({len(result_data['enriched_prompt'])} chars) with {len(result_data.get('selected_functions', []))} functions")

            return AgentResult(success=True, data=result_data)

        except Exception as e:
            self.logger.error(f"❌ Failed to build enriched prompt: {e}")
            return AgentResult(success=False, error=str(e))

    def _get_available_functions(self) -> str:
        """Get formatted list of available MCP functions"""
        # This would normally query MCP servers for available functions
        # For now, return a fixed list of commonly used functions
        functions = [
            {
                "name": "financial_data__get_historical_data",
                "description": "Fetch historical price data (OHLCV) for symbols"
            },
            {
                "name": "financial_data__get_real_time_data",
                "description": "Get current market data and quotes"
            },
            {
                "name": "financial_data__get_fundamentals",
                "description": "Fetch fundamental data for a company"
            },
            {
                "name": "analytics_engine__calculate_annualized_return",
                "description": "Calculate annualized return from price series"
            },
            {
                "name": "analytics_engine__calculate_annualized_volatility",
                "description": "Calculate annualized volatility (risk)"
            },
            {
                "name": "analytics_engine__calculate_correlation",
                "description": "Calculate correlation between assets"
            },
            {
                "name": "analytics_engine__calculate_beta",
                "description": "Calculate beta (systematic risk)"
            },
            {
                "name": "analytics_engine__calculate_sharpe_ratio",
                "description": "Calculate Sharpe ratio (risk-adjusted return)"
            },
            {
                "name": "analytics_engine__calculate_drawdown",
                "description": "Calculate maximum drawdown"
            }
        ]

        lines = ["Available Functions:"]
        for func in functions:
            lines.append(f"- {func['name']}: {func['description']}")

        return "\n".join(lines)

    def _build_blocks_context(self, blocks: List[Dict]) -> str:
        """Build blocks context from ui_planner"""
        if not blocks:
            return ""

        lines = ["DASHBOARD BLOCKS (for data requirements):"]
        for i, block in enumerate(blocks, 1):
            block_id = block.get("blockId", "?")
            title = block.get("title", "?")
            category = block.get("category", "?")
            contract = block.get("dataContract", {})

            lines.append(f"\n{i}. {block_id}: {title}")
            lines.append(f"   Type: {category}")
            lines.append(f"   Description: {contract.get('description', '?')}")
            if contract.get("points"):
                lines.append(f"   Expected data: {contract.get('points')}")

        return "\n".join(lines)

    def _now_iso(self) -> str:
        """Get current time in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()


# Factory function for easy creation
def create_code_prompt_builder_agent(**kwargs) -> CodePromptBuilderAgent:
    """Create Code Prompt Builder agent with optional overrides"""
    return CodePromptBuilderAgent(**kwargs)


# For direct execution
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        question = sys.argv[1]
        agent = CodePromptBuilderAgent()

        result = agent.execute({"question": question})
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print("Usage: python code_prompt_builder_agent.py \"Your question here\"")