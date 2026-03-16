#!/usr/bin/env python3
"""
Script Executor Agent

Executes generated Python scripts and captures results.

Input:
    {
        "script_path": "/path/to/script.py",
        "parameters": {"symbol": "QQQ"},
        "script_content": "#!/usr/bin/env python3\n..."  // Optional
    }

Output:
    {
        "success": true,
        "results": {...},
        "execution_time": 2.3,
        "error": null
    }
"""

import json
import subprocess
import tempfile
import os
from typing import Dict, Any, Optional
from datetime import datetime

from agent_base import AgentBase, AgentResult


class ScriptExecutorAgent(AgentBase):
    """Agent that executes Python scripts"""

    def __init__(
        self,
        prompt_file: str = "../../shared/config/agents/test/script_executor.txt",
        llm_model: str = None,  # Use task-based config by default
        llm_provider: str = None  # Use task-based config by default
    ):
        super().__init__(
            name="script_executor",
            task="SCRIPT_EXECUTOR",
            prompt_file=prompt_file,
            llm_model=llm_model,
            llm_provider=llm_provider
        )

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "script_path": {"type": "string", "description": "Path to Python script"},
                "script_content": {"type": "string", "description": "Script content (optional)"},
                "parameters": {"type": "object", "description": "Execution parameters"}
            },
            "required": []
        }

    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "results": {"type": "object"},
                "execution_time": {"type": "number"},
                "stdout": {"type": "string"},
                "stderr": {"type": "string"},
                "error": {"type": "string"},
                "metadata": {"type": "object"}
            },
            "required": ["success"]
        }

    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """Execute the Python script"""
        script_path = input_data.get("script_path")
        script_content = input_data.get("script_content")
        parameters = input_data.get("parameters", {})

        # If script_content is provided, write to temp file
        if script_content and not script_path:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(script_content)
                script_path = f.name
                self._temp_file = script_path  # Track for cleanup
        elif not script_path:
            return AgentResult(
                success=False,
                error="Either script_path or script_content must be provided"
            )

        # Check if script exists
        if not os.path.exists(script_path):
            return AgentResult(
                success=False,
                error=f"Script not found: {script_path}"
            )

        try:
            start_time = datetime.now()

            # Build command with parameters
            cmd = ["python", script_path]
            for key, value in parameters.items():
                cmd.extend([f"--{key}", str(value)])

            self.logger.info(f"🚀 Executing: {' '.join(cmd)}")

            # Execute script
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout
            )

            execution_time = (datetime.now() - start_time).total_seconds()

            # Parse output
            results = None
            stdout = result.stdout
            stderr = result.stderr

            if result.returncode == 0 and stdout:
                try:
                    results = json.loads(stdout)
                except json.JSONDecodeError:
                    # Output wasn't JSON, keep as is
                    self.logger.warning("Script output was not valid JSON")
                    results = {"output": stdout}

            # Build result data
            result_data = {
                "success": result.returncode == 0,
                "results": results,
                "execution_time": execution_time,
                "stdout": stdout,
                "stderr": stderr,
                "error": stderr if result.returncode != 0 else None,
                "metadata": {
                    "script_path": script_path,
                    "parameters": parameters,
                    "return_code": result.returncode,
                    "timestamp": datetime.now().isoformat()
                }
            }

            self.logger.info(f"✅ Execution complete: {'SUCCESS' if result.returncode == 0 else 'FAILED'} ({execution_time:.2f}s)")

            return AgentResult(success=True, data=result_data)

        except subprocess.TimeoutExpired:
            return AgentResult(
                success=False,
                error=f"Script execution timed out after 60 seconds"
            )
        except Exception as e:
            self.logger.error(f"❌ Failed to execute script: {e}")
            return AgentResult(
                success=False,
                error=str(e)
            )
        finally:
            # Clean up temp file if we created one
            if hasattr(self, '_temp_file') and self._temp_file:
                try:
                    os.unlink(self._temp_file)
                    delattr(self, '_temp_file')
                except:
                    pass


# Factory function for easy creation
def create_script_executor_agent(**kwargs) -> ScriptExecutorAgent:
    """Create Script Executor agent with optional overrides"""
    return ScriptExecutorAgent(**kwargs)


# For direct execution
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        script_path = sys.argv[1]
        agent = ScriptExecutorAgent()

        result = agent.execute({
            "script_path": script_path,
            "parameters": {}
        })
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print("Usage: python script_executor_agent.py /path/to/script.py")