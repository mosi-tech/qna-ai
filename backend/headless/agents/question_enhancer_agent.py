#!/usr/bin/env python3
"""
Question Enhancer Agent

Expands short user questions into more detailed questions with specific
requirements. Runs BEFORE ui_planner to ensure planner receives well-formed questions.

Input:
    {
        "question": "Show QQQ price",
        "original_question": "Show QQQ price"
    }

Output:
    {
        "enhanced_question": "Show QQQ ETF current price, daily change, 52-week high/low with 1-year historical data...",
        "data_requirements": [...],
        "metadata": {...}
    }
"""

import os
from typing import Dict, Any, List

from agent_base import AgentBase, AgentResult


class QuestionEnhancerAgent(AgentBase):
    """Agent that enhances questions with specific data requirements"""

    def __init__(
        self,
        prompt_file: str = "../../shared/config/agents/test/question_enhancer.txt",
        llm_model: str = None,  # Use task-based config by default
        llm_provider: str = None  # Use task-based config by default
    ):
        super().__init__(
            name="question_enhancer",
            task="QUESTION_ENHANCER",
            prompt_file=prompt_file,
            llm_model=llm_model,
            llm_provider=llm_provider
        )

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "User's question"},
                "blocks": {"type": "array", "description": "Blocks from ui_planner (optional)"},
                "original_question": {"type": "string", "description": "Original question"}
            },
            "required": ["question"]
        }

    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "enhanced_question": {"type": "string"},
                "data_requirements": {"type": "array"},
                "metadata": {"type": "object"}
            },
            "required": ["enhanced_question"]
        }

    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """Process and enhance the question"""
        question = input_data.get("question", "")
        blocks = input_data.get("blocks", [])
        original_question = input_data.get("original_question", question)

        # Build block specifications for prompt
        block_specs = self._build_block_specs(blocks)

        user_message = f"""
Original Question: {original_question}

Dashboard Plan ({len(blocks)} blocks):
{block_specs}

Please enhance this question by adding specific data requirements that will help the analysis generate the right data for each block.

Return ONLY a JSON object with:
- enhanced_question: The original question plus specific data requirements
- data_requirements: Array of data requirements extracted from the blocks
- metadata: Object with block_count, timestamp, etc.

Enhancement guidelines:
- Be specific about what data is needed (e.g., "current price", "1-year history", "daily closing prices")
- Include time periods (e.g., "past year", "YTD", "30 days")
- Mention specific metrics (e.g., "volume", "market cap", "P/E ratio")
- Request percentages and numeric values where appropriate

No markdown, no code blocks, just JSON.
"""

        try:
            # Make LLM request
            response = self._make_llm_request(
                messages=[{"role": "user", "content": user_message}]
            )

            content = response.get("content", "").strip()
            result_data = self._safe_parse_json(content)

            # Validate result structure
            if "enhanced_question" not in result_data:
                raise Exception("Missing 'enhanced_question' field in response")

            # Add metadata
            result_data.setdefault("metadata", {})["block_count"] = len(blocks)
            result_data["metadata"]["original_question"] = original_question
            result_data["metadata"]["enhanced_block_ids"] = [b.get("blockId") for b in blocks]

            self.logger.info(f"✅ Enhanced question ({len(result_data['enhanced_question'])} chars)")

            return AgentResult(success=True, data=result_data)

        except Exception as e:
            self.logger.error(f"❌ Failed to enhance question: {e}")
            return AgentResult(success=False, error=str(e))

    def _build_block_specs(self, blocks: List[Dict]) -> str:
        """Build formatted block specifications for prompt"""
        lines = []
        for i, block in enumerate(blocks, 1):
            block_id = block.get("blockId", "?")
            title = block.get("title", "?")
            category = block.get("category", "?")
            contract = block.get("dataContract", {})

            lines.append(f"{i}. {block_id}: {title}")
            lines.append(f"   Category: {category}")
            lines.append(f"   Data Type: {contract.get('type', '?')}")
            lines.append(f"   Description: {contract.get('description', '?')}")
            if contract.get("points"):
                lines.append(f"   Points: {contract.get('points')}")

        return "\n".join(lines)


# Factory function for easy creation
def create_question_enhancer_agent(**kwargs) -> QuestionEnhancerAgent:
    """Create Question Enhancer agent with optional overrides"""
    return QuestionEnhancerAgent(**kwargs)


# For direct execution
if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) > 1:
        question = sys.argv[1]
        agent = QuestionEnhancerAgent()

        # Create mock blocks for testing
        mock_blocks = [
            {
                "blockId": "kpi-card-01",
                "title": "QQQ Price",
                "category": "kpi-cards",
                "dataContract": {"type": "kpi", "description": "Current price and change"}
            }
        ]

        result = agent.execute({"question": question, "blocks": mock_blocks})
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print("Usage: python question_enhancer_agent.py \"Your question here\"")