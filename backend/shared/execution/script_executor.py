#!/usr/bin/env python3
"""
Shared Script Execution Logic

Used by both MCP validation server and HTTP execution server.
Handles script execution with proper MCP function injection.
"""

import json
import logging
import os
import sys
import subprocess
import tempfile
import uuid
    
from datetime import datetime
from typing import Dict, Any, Optional

from .mcp_injection import create_mcp_injection_wrapper
from ..security.script_sandbox import ScriptSandbox

logger = logging.getLogger("shared-script-executor")


def create_enhanced_script(script_content: str, mock_mode: bool = True) -> str:
    """
    Create enhanced script with MCP injection wrapper for verification purposes
    
    Args:
        script_content: Raw script content to enhance
        mock_mode: Whether to use mock mode (True) or production mode (False)
        
    Returns:
        Enhanced script with MCP injection wrapper
    """
    try:
        # Create MCP injection wrapper
        mcp_wrapper = create_mcp_injection_wrapper(production_mode=not mock_mode)
        
        # Create enhanced script
        enhanced_script = mcp_wrapper + script_content
        
        logger.debug(f"✅ Enhanced script created (wrapper: {len(mcp_wrapper)} chars, total: {len(enhanced_script)} chars)")
        return enhanced_script
        
    except Exception as e:
        logger.error(f"❌ Error creating enhanced script: {e}")
        # Return original script if enhancement fails
        return script_content

def execute_script(script_content: str, mock_mode: bool = True, timeout: int = 30, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Execute Python script with MCP function injection in secured sandbox
    
    Args:
        script_content: Complete Python script content
        mock_mode: If True, runs in validation mode; if False, production mode
        timeout: Execution timeout in seconds
        parameters: Optional dictionary of parameters to inject into script
        
    Returns:
        Dict with execution results
    """

    logger.info(f"🚀 Executing script in sandbox (mock={mock_mode}, timeout={timeout}s)")
    
    try:
        # Create enhanced script with MCP injection wrapper
        enhanced_script = create_enhanced_script(script_content, mock_mode)
        
        # Build command with parameters
        cmd_args = []
        if parameters:
            for key, value in parameters.items():
                if value is not None:
                    cmd_args.extend([f'--{key}', str(value)])
        
        # Execute script in sandbox
        import asyncio
        loop = asyncio.new_event_loop()
        sandbox_result = loop.run_until_complete(
            ScriptSandbox.execute_safely(
                enhanced_script,
                timeout=timeout,
                memory_limit_mb=512
            )
        )
        loop.close()
        
        if not sandbox_result.get("success"):
            logger.error(f"❌ Script execution failed in sandbox: {sandbox_result.get('error')}")
            return {
                "success": False,
                "error": sandbox_result.get("error", "Unknown sandbox error"),
                "error_type": "SandboxExecutionError",
                "mock_mode": mock_mode,
                "resource_limits_hit": sandbox_result.get("resource_limits_hit", False),
                "execution_time": sandbox_result.get("execution_time", 0)
            }
        
        # Parse sandbox output
        stdout = sandbox_result.get("stdout", "")
        stderr = sandbox_result.get("stderr", "")
        execution_time = sandbox_result.get("execution_time", 0)
        
        # Create mock subprocess result for processing
        class MockResult:
            def __init__(self, returncode, stdout, stderr):
                self.returncode = returncode
                self.stdout = stdout
                self.stderr = stderr
        
        result = MockResult(0, stdout, stderr)
        return _process_execution_result(result, execution_time, mock_mode)
                
    except Exception as e:
        logger.error(f"❌ Execution error: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "ExecutionError",
            "mock_mode": mock_mode
        }


def _process_execution_result(result, execution_time: float, mock_mode: bool) -> Dict[str, Any]:
    """Process subprocess execution result"""
    if result.returncode == 0:
        # Subprocess executed without crashing
        try:
            # Try to parse as JSON
            output_data = json.loads(result.stdout)
            
            # Check if the script itself reports analysis success/failure
            script_success = output_data.get("analysis_completed", True)
            script_error = output_data.get("error", None)
            
            if script_success:
                logger.info("✅ Script executed successfully")
            else:
                logger.warning(f"❌ Script analysis failed: {script_error}")
            
            # In mock mode, validate schema but check script success
            if mock_mode:
                # Validation mode: return script success and include error if present
                result_data = {
                    "success": script_success,
                    "execution_time": execution_time,
                    "mock_mode": mock_mode,
                    "output": output_data
                }
                if not script_success and script_error:
                    result_data["success"] = False
                    result_data["error"] = script_error
                    result_data["output"] = output_data
                    # Include error_traceback if present
                    if "error_traceback" in output_data:
                        result_data["error_traceback"] = output_data["error_traceback"]
                return result_data
            else:
                # Production mode: return script success and full output
                return {
                    "success": script_success,
                    "output": output_data,
                    "execution_time": execution_time,
                    "mock_mode": mock_mode
                }
        except json.JSONDecodeError:
            # Non-JSON output - treat as failure in validation
            logger.warning("❌ Script produced non-JSON output")
            return {
                "success": False,
                "output": {"raw_output": result.stdout},
                "execution_time": execution_time,
                "mock_mode": mock_mode,
                "error": "Script produced non-JSON output"
            }
    else:
        # Execution failed
        error_output = result.stderr.strip() or result.stdout.strip()
        logger.warning(f"❌ Script execution failed: {error_output}")
        
        return {
            "success": False,
            "error": error_output,
            "error_type": classify_error(error_output),
            "execution_time": execution_time,
            "mock_mode": mock_mode,
            "full_stderr": result.stderr,
            "full_stdout": result.stdout
        }

def classify_error(error_output: str) -> str:
    """Classify error type for better self-correction"""
    error_lower = error_output.lower()
    
    if "syntaxerror" in error_lower:
        return "SyntaxError"
    elif "importerror" in error_lower or "modulenotfounderror" in error_lower:
        return "ImportError"
    elif "attributeerror" in error_lower:
        return "AttributeError"
    elif "typeerror" in error_lower:
        return "TypeError"
    elif "valueerror" in error_lower:
        return "ValueError"
    elif "keyerror" in error_lower:
        return "KeyError"
    elif "indentationerror" in error_lower:
        return "IndentationError"
    elif "nameerror" in error_lower:
        return "NameError"
    else:
        return "RuntimeError"

def check_forbidden_imports(script_content: str) -> Dict[str, Any]:
    """Check for forbidden package imports"""
    forbidden_packages = [
        'yfinance', 'quandl', 'alpha_vantage', 'fredapi', 'bloomberg',
        'matplotlib', 'plotly', 'seaborn', 'dash', 'streamlit',
        'bokeh', 'altair', 'pygal', 'requests', 'urllib'
    ]
    
    forbidden_found = []
    
    for line in script_content.split('\n'):
        line = line.strip()
        if line.startswith('import ') or line.startswith('from '):
            for forbidden in forbidden_packages:
                if forbidden in line:
                    forbidden_found.append({
                        "package": forbidden,
                        "line": line,
                        "suggestion": get_package_suggestion(forbidden)
                    })
    
    if forbidden_found:
        return {
            "valid": False,
            "error": "Forbidden package imports detected",
            "error_type": "ForbiddenImportError",
            "forbidden_imports": forbidden_found,
            "allowed_packages": [
                "pandas", "numpy", "pytz", "python-dateutil", 
                "Built-in: json, logging, datetime, os, sys, math, statistics, random"
            ]
        }
    
    return {"valid": True}

def get_package_suggestion(forbidden_package: str) -> str:
    """Get suggested alternative for forbidden packages"""
    suggestions = {
        'yfinance': 'Use MCP financial server: call_mcp_function("alpaca_market_stocks_bars", args)',
        'quandl': 'Use MCP financial server: call_mcp_function("eodhd_real_time", args)',
        'alpha_vantage': 'Use MCP financial server: call_mcp_function("alpaca_market_stocks_bars", args)',
        'matplotlib': 'Remove visualization - analysis scripts should return data only',
        'plotly': 'Remove visualization - analysis scripts should return data only',
        'seaborn': 'Remove visualization - analysis scripts should return data only',
        'requests': 'Use MCP functions instead of external HTTP requests'
    }
    return suggestions.get(forbidden_package, 'Use approved packages from execution_requirements.txt')

def check_defensive_programming(script_content: str) -> Dict[str, Any]:
    """Check for forbidden defensive programming patterns - fail fast on first violation"""
    
    lines = script_content.split('\n')
    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()
        
        # Check for assert statements - FAIL FAST
        if line_stripped.startswith('assert '):
            return {
                "valid": False,
                "error": "Assert statements are forbidden",
                "error_type": "DefensiveProgrammingError",
                "line_number": i,
                "line": line_stripped,
                "not_allowed": "assert statements",
                "use_instead": "Direct access that fails with clear KeyError/AttributeError"
            }
        
        # Check for .get() with defaults - FAIL FAST (commented out)
        # if '.get(' in line and ',' in line:
        #     return {
        #         "valid": False,
        #         "error": "Defensive .get() with defaults is forbidden",
        #         "error_type": "DefensiveProgrammingError", 
        #         "line_number": i,
        #         "line": line_stripped,
        #         "not_allowed": ".get(key, default) patterns",
        #         "use_instead": "Direct dict access like data['key'] to fail fast"
        #     }
        
        # Check for defensive if result checks - FAIL FAST (commented out)
        # if ('if result and result.get' in line or 
        #     ('if result:' in line and 'get(' in line)):
        #     return {
        #         "valid": False,
        #         "error": "Defensive result checking is forbidden",
        #         "error_type": "DefensiveProgrammingError",
        #         "line_number": i, 
        #         "line": line_stripped,
        #         "not_allowed": "if result and result.get() patterns",
        #         "use_instead": "Direct access like result['data'] to fail fast"
        #     }
    
    return {"valid": True}


def _write_temp_script_local(enhanced_script: str) -> str:
    """
    Write temporary script to local filesystem for subprocess execution
    This is always local regardless of storage provider since subprocess needs local files
    """

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_suffix = uuid.uuid4().hex[:4]
    
    # Create temp file with proper extension
    fd, script_path = tempfile.mkstemp(
        suffix=".py",
        prefix=f"temp_validation_script_{timestamp}_{random_suffix}_"
    )
    
    try:
        # Write script content
        with os.fdopen(fd, 'w') as f:
            f.write(enhanced_script)
        
        # Make executable
        os.chmod(script_path, 0o755)
        
        return script_path
    except Exception:
        # Clean up on error
        try:
            os.unlink(script_path)
        except OSError:
            pass
        raise