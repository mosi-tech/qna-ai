#!/usr/bin/env python3
"""
Code Script Generator Agent

Takes enriched prompts from Code Prompt Builder and generates Python scripts
using validation-server__write_and_validate().

Input:
    {
        "enriched_prompt": "...",
        "selected_functions": [...],
        "question": "Show QQQ ETF price"
    }

Output:
    {
        "script": "#!/usr/bin/env python3\n...",
        "script_name": "qqq_performance_analysis_20260316.py",
        "metadata": {...}
    }
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

from agent_base import AgentBase, AgentResult


class CodeScriptGeneratorAgent(AgentBase):
    """Agent that generates Python scripts using enriched prompts"""

    def __init__(
        self,
        prompt_file: str = "../../shared/config/agents/test/code_generator_old.txt",  # Use test prompt for standalone script generation
        llm_model: str = None,  # Use task-based config by default (gpt-oss:120b via env)
        llm_provider: str = None  # Use task-based config by default
    ):
        super().__init__(
            name="code_script_generator",
            task="CODE_SCRIPT_GENERATOR",
            prompt_file=prompt_file,
            llm_model=llm_model,
            llm_provider=llm_provider
        )

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "enriched_prompt": {"type": "string", "description": "Enriched prompt from code_prompt_builder"},
                "selected_functions": {"type": "array", "description": "Selected MCP functions"},
                "question": {"type": "string", "description": "Original user question"},
                "context": {"type": "object", "description": "Additional context"}
            },
            "required": ["enriched_prompt", "question"]
        }

    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "script": {"type": "string"},
                "script_name": {"type": "string"},
                "validation_result": {"type": "object"},
                "metadata": {"type": "object"}
            },
            "required": ["script", "script_name"]
        }

    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """Generate Python script from enriched prompt"""
        enriched_prompt = input_data.get("enriched_prompt", "")
        question = input_data.get("question", "")
        selected_functions = input_data.get("selected_functions", [])
        context = input_data.get("context", {})

        # Handle case where enriched_prompt is a dict (from existing code_prompt_builder)
        if isinstance(enriched_prompt, dict):
            # Extract key information for the script generation
            analysis_type = enriched_prompt.get("analysis_type", "")
            suggested_workflow = enriched_prompt.get("suggested_workflow", "")
            function_schemas = enriched_prompt.get("function_schemas", {})
            code_instructions = enriched_prompt.get("code_generation_instructions", "")

            # Build the enriched prompt for the LLM
            enriched_prompt_str = f"""
ANALYSIS TYPE: {analysis_type}

SUGGESTED WORKFLOW:
{suggested_workflow}

CODE GENERATION INSTRUCTIONS:
{code_instructions}

AVAILABLE FUNCTIONS:
{json.dumps(function_schemas, indent=2)}
"""
        else:
            enriched_prompt_str = enriched_prompt

        # Add validation feedback if provided (for retry attempts)
        validation_feedback_section = ""
        validation_messages = context.get("validation_feedback", [])
        if validation_messages:
            validation_feedback_section = "\n\nVALIDATION FEEDBACK FROM PREVIOUS ATTEMPTS:"
            for i, vm in enumerate(validation_messages):
                validation_feedback_section += f"\nAttempt {vm['attempt']}: {'VALID' if vm['valid'] else 'INVALID'}"
                if vm.get("errors"):
                    validation_feedback_section += f"\n  Errors: {vm['errors']}"
                if vm.get("warnings"):
                    validation_feedback_section += f"\n  Warnings: {vm['warnings']}"
            validation_feedback_section += "\n\nPLEASE FIX THESE ISSUES IN THE NEW SCRIPT."

        # Build the complete user message
        user_message = f"""ORIGINAL QUESTION: {question}

{enriched_prompt_str}
{validation_feedback_section}

SELECTED FUNCTIONS: {', '.join(selected_functions)}

TASK: Generate a Python script that answers the original question using call_mcp_function().

The script should:
1. Use call_mcp_function() to call the selected MCP functions
2. Include proper imports (json, pandas, datetime, typing)
3. Define an analyze_question() function with typed parameters
4. Include a main() function for HTTP execution
5. Return results as JSON using print(json.dumps(results, indent=2))
6. Handle errors gracefully with try/except

Return ONLY valid Python code (no markdown, no backticks). The code should be complete and runnable.
"""

        try:
            # Make LLM request with code generation model
            response = self._make_llm_request(
                messages=[{"role": "user", "content": user_message}]
            )

            content = response.get("content", "").strip()

            # Clean up the response (remove markdown code blocks if present)
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("python"):
                    content = content[6:].strip()
            if content.endswith("```"):
                content = content[:-3].strip()

            # Validate script looks like Python code
            if not content.startswith("#!/usr/bin/env python3") and not content.startswith("import"):
                raise Exception("Response doesn't appear to be a Python script")

            # Generate script name from question
            question_slug = question.lower().replace(" ", "_").replace("/", "_").replace("?", "").replace(",", "")[:50]
            script_name = f"{question_slug}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"

            # Build result
            result_data = {
                "script": content,
                "script_name": script_name,
                "metadata": {
                    "question": question,
                    "enriched_prompt_length": len(enriched_prompt),
                    "selected_function_count": len(selected_functions),
                    "script_length": len(content),
                    "timestamp": datetime.now().isoformat()
                }
            }

            self.logger.info(f"✅ Generated script: {script_name} ({len(content)} chars)")

            return AgentResult(success=True, data=result_data)

        except Exception as e:
            self.logger.error(f"❌ Failed to generate script: {e}")
            return AgentResult(success=False, error=str(e))


# Factory function for easy creation
def create_code_script_generator_agent(**kwargs) -> CodeScriptGeneratorAgent:
    """Create Code Script Generator agent with optional overrides"""
    return CodeScriptGeneratorAgent(**kwargs)


# For direct execution
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        question = sys.argv[1]
        agent = CodeScriptGeneratorAgent()

        # Mock enriched prompt for testing
        mock_enriched_prompt = """
ANALYSIS REQUIREMENTS:
- Fetch historical price data for QQQ ETF
- Calculate current price and daily change
- Return as JSON

SELECTED FUNCTIONS:
- financial_data__get_historical_data: Fetch historical OHLCV data
- analytics_engine__calculate_daily_return: Calculate returns

DATA STRUCTURE:
{
  "current_price": float,
  "daily_change": float,
  "timestamp": string
}
"""

        result = agent.execute({
            "question": question,
            "enriched_prompt": mock_enriched_prompt,
            "selected_functions": ["financial_data__get_historical_data"]
        })
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print("Usage: python code_script_generator_agent.py \"Your question here\"")