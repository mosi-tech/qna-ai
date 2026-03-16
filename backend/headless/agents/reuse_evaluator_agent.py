#!/usr/bin/env python3
"""
Reuse Evaluator Agent

Evaluates if existing analyses can be reused for new financial questions.

Input:
    {
        "question": "Show QQQ ETF price",
        "existing_analyses": [...]
    }

Output:
    {
        "should_reuse": true,
        "analysis_id": "xxx",
        "script_name": "qqq_performance_analysis.py",
        "similarity": 0.89,
        "reason": "Same analysis methodology - only parameters differ",
        "execution": {...}
    }
"""

import json
from typing import Dict, Any, List, Optional

from agent_base import AgentBase, AgentResult


class ReuseEvaluatorAgent(AgentBase):
    """Agent that evaluates whether existing analyses can be reused"""

    def __init__(
        self,
        prompt_file: str = "../../shared/config/system-prompt-reuse-evaluator.txt",
        llm_model: str = None,  # Use task-based config by default
        llm_provider: str = None  # Use task-based config by default
    ):
        super().__init__(
            name="reuse_evaluator",
            task="REUSE_EVALUATOR",
            prompt_file=prompt_file,
            llm_model=llm_model,
            llm_provider=llm_provider
        )

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "User's question"},
                "existing_analyses": {"type": "array", "description": "List of existing analyses"}
            },
            "required": ["question"]
        }

    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "should_reuse": {"type": "boolean"},
                "analysis_id": {"type": "string"},
                "script_name": {"type": "string"},
                "similarity": {"type": "number"},
                "reason": {"type": "string"},
                "execution": {"type": "object"}
            },
            "required": ["should_reuse", "reason"]
        }

    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """Evaluate reuse potential"""
        question = input_data.get("question", "")
        existing_analyses = input_data.get("existing_analyses", [])

        # Build evaluation prompt
        evaluation_prompt = self._build_evaluation_prompt(question, existing_analyses)

        try:
            # Make LLM request
            response = self._make_llm_request(
                messages=[{"role": "user", "content": evaluation_prompt}]
            )

            content = response.get("content", "").strip()
            result_data = self._safe_parse_json(content)

            # Validate result structure
            if "should_reuse" not in result_data:
                raise Exception("Missing 'should_reuse' field in response")

            # If should_reuse is True, validate script_name
            if result_data.get("should_reuse"):
                if not result_data.get("script_name"):
                    raise Exception("should_reuse=true but missing script_name")

                # Validate script_name exists in provided analyses
                script_name = result_data["script_name"]
                valid_script_names = []

                for analysis in existing_analyses:
                    execution_data = analysis.get("execution", {})
                    if isinstance(execution_data, dict) and execution_data.get("script_name"):
                        valid_script_names.append(execution_data["script_name"])

                if script_name not in valid_script_names:
                    self.logger.warning(f"⚠️  Invalid script_name '{script_name}' not found in provided analyses")
                    # Fall back to not reusing
                    result_data = {
                        "should_reuse": False,
                        "reason": f"Invalid script name returned by LLM: {script_name}"
                    }

                # Try to find matching analysis_id
                if result_data.get("should_reuse"):
                    for analysis in existing_analyses:
                        execution_data = analysis.get("execution", {})
                        if isinstance(execution_data, dict):
                            if execution_data.get("script_name") == script_name:
                                result_data["analysis_id"] = analysis.get("id")
                                result_data["similarity"] = result_data.get("similarity", 0.85)
                                break

            self.logger.info(f"✅ Reuse decision: {'YES' if result_data.get('should_reuse') else 'NO'}")

            return AgentResult(success=True, data=result_data)

        except Exception as e:
            self.logger.error(f"❌ Failed to evaluate reuse: {e}")
            return AgentResult(success=False, error=str(e))

    def _build_evaluation_prompt(self, question: str, existing_analyses: List[Dict]) -> str:
        """Build evaluation prompt with question and existing analyses"""
        # Format existing analyses section
        if existing_analyses:
            analyses_section = "RELEVANT EXISTING ANALYSES:\n\n"
            for i, analysis in enumerate(existing_analyses, 1):
                analysis_id = analysis.get('id') or analysis.get('question', 'Unknown Analysis')
                analyses_section += f"{i}. {analysis_id}\n"

                # Include full analysis JSON
                analyses_section += "```json\n"
                analyses_section += json.dumps(analysis, indent=2)
                analyses_section += "\n```\n\n"
        else:
            analyses_section = "RELEVANT EXISTING ANALYSES: None provided\n\n"

        # Build evaluation prompt
        evaluation_prompt = f"""USER QUERY: {question}

{analyses_section}TASK: Evaluate if any of the existing analyses can be reused for this user query.

Consider:
1. Is the core financial methodology the same?
2. Are only parameters different (symbols, timeframes, thresholds)?
3. Is the expected output format similar?
4. Does the analysis approach match what's needed?

When should_reuse=true:
- The script_name MUST be the exact script_name from one of the provided analyses
- Never make up or invent script names
- Convert user requirements into the technical parameter format expected by the script
- Provide execution parameters that would work with the reused script

Return your decision in the exact JSON format specified in the system prompt.
"""

        return evaluation_prompt


# Factory function for easy creation
def create_reuse_evaluator_agent(**kwargs) -> ReuseEvaluatorAgent:
    """Create Reuse Evaluator agent with optional overrides"""
    return ReuseEvaluatorAgent(**kwargs)


# For direct execution
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        question = sys.argv[1]
        agent = ReuseEvaluatorAgent()

        # Create mock existing analyses for testing
        mock_analyses = [
            {
                "id": "analysis_001",
                "question": "Show QQQ ETF price and YTD return",
                "execution": {
                    "script_name": "qqq_price_analysis.py",
                    "parameters": {
                        "symbol": "QQQ",
                        "period_days": 252
                    }
                }
            }
        ]

        result = agent.execute({
            "question": question,
            "existing_analyses": mock_analyses
        })
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print("Usage: python reuse_evaluator_agent.py \"Your question here\"")