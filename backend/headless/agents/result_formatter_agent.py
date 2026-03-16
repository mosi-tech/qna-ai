#!/usr/bin/env python3
"""
Result Formatter Agent

Formats script execution results for dashboard visualization.

Input:
    {
        "question": "Show QQQ ETF price",
        "script_results": {...},
        "blocks": [...]
    }

Output:
    {
        "dashboard_data": {
            "kpi_metrics": {...},
            "charts": {...},
            "tables": {...}
        },
        "blocks_status": [...],
        "metadata": {...}
    }
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from agent_base import AgentBase, AgentResult


class ResultFormatterAgent(AgentBase):
    """Agent that formats results for dashboard rendering"""

    def __init__(
        self,
        prompt_file: str = "../../shared/config/system-prompt-result-formatter.txt",
        llm_model: str = "glm-4.7:cloud",
        llm_provider: str = "ollama"
    ):
        super().__init__(
            name="result_formatter",
            prompt_file=prompt_file,
            llm_model=llm_model,
            llm_provider=llm_provider
        )

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "User's question"},
                "script_results": {"type": "object", "description": "Results from script execution"},
                "blocks": {"type": "array", "description": "Dashboard blocks from ui_planner"}
            },
            "required": ["question", "script_results"]
        }

    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "dashboard_data": {"type": "object"},
                "blocks_status": {"type": "array"},
                "metadata": {"type": "object"}
            },
            "required": ["dashboard_data", "blocks_status"]
        }

    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """Format results for dashboard"""
        question = input_data.get("question", "")
        script_results = input_data.get("script_results", {})
        blocks = input_data.get("blocks", [])

        # Build formatting prompt
        blocks_spec = self._build_blocks_spec(blocks)
        formatter_prompt = self._build_formatter_prompt(question, script_results, blocks_spec)

        try:
            # Make LLM request
            response = self._make_llm_request(
                messages=[{"role": "user", "content": formatter_prompt}]
            )

            content = response.get("content", "").strip()
            result_data = self._safe_parse_json(content)

            # Validate result structure
            if "dashboard_data" not in result_data:
                raise Exception("Missing 'dashboard_data' field in response")

            # Add metadata
            total_blocks = len(blocks) if blocks else 1
            successful_blocks = len([b for b in result_data.get("blocks_status", []) if b.get("status") == "success"])

            result_data.setdefault("metadata", {}).update({
                "question": question,
                "timestamp": datetime.now().isoformat(),
                "blocks_total": total_blocks,
                "blocks_successful": successful_blocks,
                "blocks_failed": total_blocks - successful_blocks
            })

            self.logger.info(f"✅ Formatting complete: {successful_blocks}/{total_blocks} blocks successful")

            return AgentResult(success=True, data=result_data)

        except Exception as e:
            self.logger.error(f"❌ Failed to format results: {e}")

            # Return fallback format on error
            return AgentResult(
                success=True,
                data={
                    "dashboard_data": {
                        "kpi_metrics": script_results,
                        "charts": {},
                        "tables": {}
                    },
                    "blocks_status": [
                        {
                            "block_id": "fallback",
                            "status": "warning",
                            "warning": "Formatting error, using raw results",
                            "data": script_results
                        }
                    ],
                    "metadata": {
                        "question": question,
                        "timestamp": datetime.now().isoformat(),
                        "error": str(e)
                    }
                }
            )

    def _build_blocks_spec(self, blocks: List[Dict]) -> str:
        """Build blocks specification for prompt"""
        if not blocks:
            return "No blocks specified - use script results directly"

        lines = ["DASHBOARD BLOCKS:"]
        for i, block in enumerate(blocks, 1):
            block_id = block.get("blockId", "?")
            title = block.get("title", "?")
            category = block.get("category", "?")
            contract = block.get("dataContract", {})

            lines.append(f"\n{i}. {block_id}: {title}")
            lines.append(f"   Type: {category}")
            lines.append(f"   Description: {contract.get('description', '?')}")
            if contract.get("points"):
                lines.append(f"   Expected data structure: {contract.get('points')}")

        return "\n".join(lines)

    def _build_formatter_prompt(self, question: str, script_results: Dict, blocks_spec: str) -> str:
        """Build formatting prompt"""
        # Truncate script_results if too long
        results_preview = json.dumps(script_results, indent=2)
        if len(results_preview) > 8000:
            results_preview = results_preview[:8000] + "\n\n... [results truncated] ..."

        formatter_prompt = f"""USER QUESTION: {question}

{blocks_spec}

SCRIPT RESULTS:
```json
{results_preview}
```

TASK: Format the script results into dashboard data structures suitable for rendering.

Please:
1. Map script results to the data contracts specified by the dashboard blocks
2. Transform data to match expected formats for each block type
3. Include metadata and status information for each block
4. Handle missing or incomplete data gracefully

Return your formatted output in the exact JSON format specified in the system prompt.
"""

        return formatter_prompt


# Factory function for easy creation
def create_result_formatter_agent(**kwargs) -> ResultFormatterAgent:
    """Create Result Formatter agent with optional overrides"""
    return ResultFormatterAgent(**kwargs)


# For direct execution
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        question = sys.argv[1]
        agent = ResultFormatterAgent()

        # Mock script results and blocks for testing
        mock_results = {
            "question": question,
            "symbol": "QQQ",
            "current_price": 450.25,
            "daily_change": 12.50,
            "daily_change_percent": 2.86,
            "ytd_return": 15.25,
            "success": True
        }

        mock_blocks = [
            {
                "blockId": "kpi-card-01",
                "title": "QQQ Price",
                "category": "kpi-cards",
                "dataContract": {
                    "type": "kpi",
                    "description": "Current price and change",
                    "points": {"value": "number", "change": "number", "change_percent": "number"}
                }
            }
        ]

        result = agent.execute({
            "question": question,
            "script_results": mock_results,
            "blocks": mock_blocks
        })
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print("Usage: python result_formatter_agent.py \"Your question here\"")