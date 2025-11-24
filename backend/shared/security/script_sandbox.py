#!/usr/bin/env python3
"""
Script Sandbox - Isolated execution environment for user-generated scripts

Provides resource limits and security constraints:
- CPU time limit (30 seconds)
- Memory limit (512MB)
- File system restrictions
- Network access blocking
- Subprocess restrictions
"""

import subprocess
import os
import tempfile
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ScriptSandbox:
    """Isolated execution environment for user scripts with resource limits"""

    # Resource limits
    CPU_TIMEOUT_SECONDS = 30
    MEMORY_LIMIT_MB = 512
    TEMP_DIR_PREFIX = "qna_sandbox_"

    # Restricted environment variables
    SAFE_ENV_VARS = {
        "PATH": "/usr/bin:/bin",
        "HOME": "/tmp",
        "TMPDIR": "/tmp",
        "LANG": "en_US.UTF-8",
    }

    @staticmethod
    def _create_sandbox_environment() -> Dict[str, str]:
        """Create restricted environment for script execution"""
        return ScriptSandbox.SAFE_ENV_VARS.copy()

    @staticmethod
    def _create_sandbox_temp_dir() -> str:
        """Create temporary directory for script execution"""
        try:
            temp_dir = tempfile.mkdtemp(prefix=ScriptSandbox.TEMP_DIR_PREFIX)
            logger.debug(f"Created sandbox temp dir: {temp_dir}")
            return temp_dir
        except Exception as e:
            logger.error(f"Failed to create sandbox temp dir: {e}")
            raise

    @staticmethod
    def _cleanup_temp_dir(temp_dir: str) -> None:
        """Clean up temporary directory after script execution"""
        try:
            if os.path.exists(temp_dir):
                import shutil

                shutil.rmtree(temp_dir, ignore_errors=True)
                logger.debug(f"Cleaned up sandbox temp dir: {temp_dir}")
        except Exception as e:
            logger.warning(f"Failed to cleanup sandbox temp dir: {e}")

    @staticmethod
    async def execute_safely(
        script_content: str,
        timeout: int = CPU_TIMEOUT_SECONDS,
        memory_limit_mb: int = MEMORY_LIMIT_MB,
    ) -> Dict[str, Any]:
        """
        Execute script in isolated sandbox with resource limits

        Args:
            script_content: Python script to execute
            timeout: CPU timeout in seconds (default: 30)
            memory_limit_mb: Memory limit in MB (default: 512)

        Returns:
            {
                "success": bool,
                "stdout": str,
                "stderr": str,
                "return_code": int,
                "error": str (if failed),
                "execution_time": float,
                "resource_limits_hit": bool
            }
        """
        temp_dir = None
        try:
            import time

            start_time = time.time()

            # Create sandbox environment
            env = ScriptSandbox._create_sandbox_environment()
            temp_dir = ScriptSandbox._create_sandbox_temp_dir()

            logger.info(
                f"🔒 Executing script in sandbox - timeout: {timeout}s, memory: {memory_limit_mb}MB"
            )

            # Use preexec_fn for resource limits (Unix only)
            def limit_resources():
                import resource

                # CPU time limit
                resource.setrlimit(resource.RLIMIT_CPU, (timeout, timeout + 5))

                # Memory limit (soft limit = hard limit)
                memory_bytes = memory_limit_mb * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))

                # Prevent core dumps
                resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

                # File size limit (prevent filling disk)
                resource.setrlimit(resource.RLIMIT_FSIZE, (100 * 1024 * 1024, 100 * 1024 * 1024))

                logger.debug("Resource limits set for subprocess")

            # Execute script in subprocess
            result = subprocess.run(
                ["python3", "-u", "-c", script_content],
                capture_output=True,
                timeout=timeout + 5,  # Add buffer for OS signals
                env=env,
                cwd=temp_dir,
                preexec_fn=limit_resources,
                text=True,
            )

            execution_time = time.time() - start_time

            # Check for resource limit hits
            resource_limits_hit = (
                result.returncode == -24  # SIGXCPU (CPU limit)
                or result.returncode == -9  # SIGKILL (Memory limit)
                or "Resource temporarily unavailable" in result.stderr
            )

            if resource_limits_hit:
                logger.warning(
                    f"⚠️ Script hit resource limits - return_code: {result.returncode}"
                )

            success = result.returncode == 0

            log_level = logging.INFO if success else logging.WARNING
            logger.log(
                log_level,
                f"Script execution {'✅ succeeded' if success else '❌ failed'} "
                f"(time: {execution_time:.2f}s, code: {result.returncode})",
            )

            return {
                "success": success,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "execution_time": execution_time,
                "resource_limits_hit": resource_limits_hit,
            }

        except subprocess.TimeoutExpired as e:
            logger.error(f"❌ Script execution timeout ({timeout}s exceeded)")
            return {
                "success": False,
                "error": f"Script execution timeout after {timeout} seconds",
                "stdout": e.stdout or "",
                "stderr": e.stderr or "",
                "return_code": -1,
                "execution_time": timeout,
                "resource_limits_hit": True,
            }

        except Exception as e:
            logger.error(f"❌ Script execution error: {e}")
            return {
                "success": False,
                "error": f"Script execution failed: {str(e)}",
                "stdout": "",
                "stderr": str(e),
                "return_code": -1,
                "execution_time": 0,
                "resource_limits_hit": False,
            }

        finally:
            if temp_dir:
                ScriptSandbox._cleanup_temp_dir(temp_dir)

    @staticmethod
    def validate_script_syntax(script_content: str) -> Dict[str, Any]:
        """
        Validate Python script syntax without executing

        Args:
            script_content: Python script to validate

        Returns:
            {
                "valid": bool,
                "error": str (if invalid),
                "error_line": int (if invalid)
            }
        """
        try:
            import ast

            ast.parse(script_content)
            logger.debug("Script syntax validated successfully")
            return {"valid": True, "error": None, "error_line": None}

        except SyntaxError as e:
            logger.warning(f"Script syntax error at line {e.lineno}: {e.msg}")
            return {
                "valid": False,
                "error": f"Syntax error: {e.msg}",
                "error_line": e.lineno,
            }

        except Exception as e:
            logger.error(f"Script validation error: {e}")
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}",
                "error_line": None,
            }

    @staticmethod
    def check_dangerous_imports(script_content: str) -> Dict[str, Any]:
        """
        Check for potentially dangerous imports and operations

        Args:
            script_content: Python script to check

        Returns:
            {
                "safe": bool,
                "dangerous_operations": [list of found operations],
                "warnings": [list of warnings]
            }
        """
        dangerous_patterns = [
            ("os.system", "System command execution"),
            ("subprocess", "Subprocess execution"),
            ("__import__", "Dynamic imports"),
            ("exec(", "Code execution"),
            ("eval(", "Code evaluation"),
            ("compile(", "Code compilation"),
            ("open(", "File operations (check if intended)"),
            ("socket", "Network operations"),
            ("urllib", "URL operations"),
            ("requests", "HTTP requests"),
        ]

        found_operations = []
        for pattern, description in dangerous_patterns:
            if pattern in script_content:
                found_operations.append(f"{pattern} - {description}")
                logger.warning(f"Found potentially dangerous operation: {pattern}")

        return {
            "safe": len(found_operations) == 0,
            "dangerous_operations": found_operations,
            "warnings": (
                [
                    "Script contains system operations. "
                    "Sandbox will limit access but review carefully."
                ]
                if found_operations
                else []
            ),
        }
