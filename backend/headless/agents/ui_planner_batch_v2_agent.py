#!/usr/bin/env python3
"""
UI Planner Batch V2 Agent

Decomposes financial questions into atomic sub-questions using batch processing.
Unlike v1 which tries to answer in one shot, v2 breaks questions into manageable pieces.

Input:
    {
        "question": "Show me my equity portfolio with holdings and daily P&L"
    }

Output:
    {
        "original_question": "...",
        "intent": "...",
        "decomposition": [
            {
                "sub_question": "...",
                "block_type": "...",
                "title": "...",
                "description": "...",
                "canonical_params": {...}
            },
            ...
        ],
        "dashboard_title": "..."
    }
"""

import json
import logging
import os
import sys
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

from agent_base import AgentBase, AgentResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ui_planner_batch_v2")


class UIsPlannerBatchV2Agent(AgentBase):
    """Agent that decomposes questions into atomic sub-questions for batch processing"""

    def __init__(
        self,
        prompt_file: str = None,
        llm_model: str = None,
        llm_provider: str = None
    ):
        # Use batch prompt if not specified
        if prompt_file is None:
            prompt_file = os.path.join(
                os.path.dirname(__file__),
                "..",
                "config",
                "system-prompt-ui-planner-batch-v2.txt"
            )

        super().__init__(
            name="ui_planner_batch_v2",
            task="UI_PLANNER_BATCH_V2",
            prompt_file=prompt_file,
            llm_model=llm_model,
            llm_provider=llm_provider
        )
        logger.info("✅ UI Planner Batch V2 initialized")

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "User's financial question"}
            },
            "required": ["question"]
        }

    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "original_question": {"type": "string"},
                "intent": {"type": "string"},
                "decomposition": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "sub_question": {"type": "string"},
                            "block_type": {"type": "string"},
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "canonical_params": {"type": "object"}
                        }
                    }
                },
                "dashboard_title": {"type": "string"}
            }
        }

    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """Decompose question into atomic sub-questions"""
        question = input_data.get("question", "")

        if not question:
            self.logger.warning("No question provided")
            return AgentResult(success=False, error="Question is required")

        try:
            # Build user prompt
            user_prompt = f"Decompose this question into atomic sub-questions:\n\n{question}"

            # Call LLM with system prompt
            self.logger.info(f"📋 Decomposing question: {question[:60]}...")
            response = self._make_llm_request(
                messages=[{"role": "user", "content": user_prompt}],
                system_prompt=self.system_prompt
            )

            # Parse JSON response
            response_text = response.get("content", "").strip()

            # Find JSON in response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                self.logger.error(f"No JSON found in response: {response_text[:200]}")
                return AgentResult(success=False, error="No JSON in LLM response")

            json_str = response_text[json_start:json_end]
            decomposition = json.loads(json_str)

            # Validate structure
            if not decomposition.get("decomposition"):
                decomposition["decomposition"] = []

            self.logger.info(f"✅ Decomposed into {len(decomposition.get('decomposition', []))} sub-questions")
            return AgentResult(success=True, data=decomposition)

        except json.JSONDecodeError as e:
            self.logger.error(f"❌ Failed to parse JSON: {e}")
            return AgentResult(success=False, error=f"JSON parse error: {e}")
        except Exception as e:
            self.logger.error(f"❌ Failed to decompose question: {e}")
            return AgentResult(success=False, error=str(e))


def create_ui_planner_batch_v2(**kwargs) -> UIsPlannerBatchV2Agent:
    """Factory function"""
    return UIsPlannerBatchV2Agent(**kwargs)


if __name__ == "__main__":
    test_question = "Show me my equity portfolio with holdings and daily P&L"

    agent = create_ui_planner_batch_v2()
    result = agent.execute({"question": test_question})
    print(json.dumps(result.to_dict(), indent=2))
