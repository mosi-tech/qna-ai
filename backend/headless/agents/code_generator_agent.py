#!/usr/bin/env python3
"""
Code Generator Agent

Generates Python scripts using MCP functions to answer financial questions.

Input:
    {
        "question": "Show QQQ ETF price",
        "selected_functions": [...],
        "function_schemas": {...}
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


class CodeGeneratorAgent(AgentBase):
    """Agent that generates Python scripts using MCP functions"""

    def __init__(
        self,
        prompt_file: str = "../../shared/config/system-prompt-code-generation-fixed.txt",
        llm_model: str = "gpt-oss:120b",  # Use better model for code generation
        llm_provider: str = "ollama"
    ):
        super().__init__(
            name="code_generator",
            prompt_file=prompt_file,
            llm_model=llm_model,
            llm_provider=llm_provider
        )

        self._load_function_catalog()

    def _load_function_catalog(self):
        """Load available MCP function catalog"""
        # This would normally fetch from MCP, but for now we'll load a local cache
        self.function_catalog = {
            "financial_data__get_historical_data": "Fetches historical price data for symbols",
            "financial_data__get_real_time_data": "Gets current market data and quotes",
            "financial_data__get_fundamentals": "Fetches fundamental data for a company",
            "analytics_engine__calculate_annualized_return": "Calculates annualized return from price series",
            "analytics_engine__calculate_annualized_volatility": "Calculates annualized volatility (risk)",
            "analytics_engine__calculate_correlation": "Calculates correlation between assets",
            "analytics_engine__calculate_beta": "Calculates beta (systematic risk)",
            "analytics_engine__calculate_sharpe_ratio": "Calculates Sharpe ratio (risk-adjusted return)",
            "analytics_engine__calculate_drawdown": "Calculates maximum drawdown",
            "analytics_engine__calculate_cagr": "Calculates compound annual growth rate",
        }

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "Enhanced user question"},
                "blocks": {"type": "array", "description": "Dashboard blocks (optional)"},
                "data_requirements": {"type": "array", "description": "Data requirements (optional)"}
            },
            "required": ["question"]
        }

    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "script": {"type": "string"},
                "script_name": {"type": "string"},
                "metadata": {"type": "object"}
            },
            "required": ["script", "script_name"]
        }

    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """Generate Python script"""
        question = input_data.get("question", "")
        blocks = input_data.get("blocks", [])

        # Generate script name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        question_hash = hash(question.encode()) & 0xffffffff  # Convert to positive int
        script_name = f"analysis_{timestamp}_{question_hash:08x}.py"

        # Build function list for prompt
        function_list = self._build_function_list()

        # Build data requirements from blocks
        data_specs = self._build_data_specs(blocks)

        user_message = f"""
Task: Generate a Python script to answer the following question.

Question: {question}

Available MCP Functions:
{function_list}

Data Requirements:
{data_specs}

Requirements:
1. Use the MCP functions available (use call_mcp_function() to call them)
2. The script should be self-contained and executable
3. Include proper imports at the top
4. Define an analyze_question() function that takes parameters
5. Add a main() function that handles command line arguments
6. Return results as JSON using print(json.dumps(results, indent=2))
7. Handle errors gracefully with try/except
8. Add docstring explaining the script's purpose
9. Use type hints for better code quality

Script Structure:
```python
#!/usr/bin/env python3
\"\"\"[Description of what the script does]\"\"\"

import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional

def analyze_question(param1: str, ...) -> Dict[str, Any]:
    \"\"\"Main analysis function\"\"\"
    # Your analysis code here
    return results

def main(**kwargs):
    \"\"\"Main entry point for HTTP execution\"\"\"
    return analyze_question(
        param1=kwargs.get('param1'),
        ...
    )

if __name__ == \"__main__\":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--param1', ...)
    args = parser.parse_args()
    result = analyze_question(args.param1, ...)
    print(json.dumps(result, indent=2))
```

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

            # Build result
            result_data = {
                "script": content,
                "script_name": script_name,
                "metadata": {
                    "question": question,
                    "timestamp": datetime.now().isoformat(),
                    "script_length": len(content),
                    "block_count": len(blocks)
                }
            }

            self.logger.info(f"✅ Generated script: {script_name} ({len(content)} chars)")

            return AgentResult(success=True, data=result_data)

        except Exception as e:
            self.logger.error(f"❌ Failed to generate script: {e}")
            return AgentResult(success=False, error=str(e))

    def _build_function_list(self) -> str:
        """Build formatted function list for prompt"""
        lines = []
        lines.append("Available MCP Functions:")
        for func_name, description in self.function_catalog.items():
            lines.append(f"\n- {func_name}: {description}")
        return "\n".join(lines)

    def _build_data_specs(self, blocks: List[Dict]) -> str:
        """Build data specifications from blocks"""
        if not blocks:
            return "No specific blocks specified - generate comprehensive analysis"

        lines = ["Required Output Data Structure:"]
        for block in blocks:
            contract = block.get("dataContract", {})
            lines.append(f"\n- {block.get('blockId')}: {block.get('title')}")
            lines.append(f"  Type: {contract.get('type')}")
            lines.append(f"  Description: {contract.get('description')}")
            if contract.get("points"):
                lines.append(f"  Expected points: {contract.get('points')}")
            if contract.get("categories"):
                lines.append(f"  Categories: {', '.join(contract.get('categories', []))}")

        return "\n".join(lines)


# Factory function for easy creation
def create_code_generator_agent(**kwargs) -> CodeGeneratorAgent:
    """Create Code Generator agent with optional overrides"""
    return CodeGeneratorAgent(**kwargs)


# For direct execution
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        question = sys.argv[1]
        agent = CodeGeneratorAgent()

        result = agent.execute({"question": question})
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print("Usage: python code_generator_agent.py \"Your question here\"")