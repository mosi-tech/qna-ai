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
import re
    
from datetime import datetime
from typing import Dict, Any, Optional

from .mcp_injection import create_mcp_injection_wrapper

logger = logging.getLogger("shared-script-executor")


def check_for_hardcoded_parameters(script_content: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Check if script contains hardcoded parameter values instead of using args.
    
    Args:
        script_content: Python script content to check
        parameters: Dictionary of parameters that should be passed via command-line
        
    Returns:
        Dict with 'valid': bool and 'issues': list of detected problems
    """
    if not parameters:
        return {"valid": True, "issues": []}
    
    issues = []
    
    # Extract the __main__ block
    main_match = re.search(r'if __name__ == "__main__":(.*?)(?=\n(?:^|\n)(?![\s])|\Z)', script_content, re.DOTALL)
    if not main_match:
        return {"valid": True, "issues": []}
    
    main_block = main_match.group(1)
    
    for param_name, param_value in parameters.items():
        if param_value is None:
            continue
        
        param_value_str = str(param_value)
        
        # Check for direct hardcoded value assignment (e.g., analysis_periods=[1, 5, 10])
        hardcoded_patterns = [
            # List/array hardcoding: param_name=[...]
            param_name + r'\s*=\s*\[',
            # String hardcoding: param_name=['...'] or param_name="..."
            param_name + r'\s*=\s*["\']',
            # Numeric hardcoding: param_name=123 or param_name=0.5
            param_name + r'\s*=\s*\d',
        ]
        
        for pattern in hardcoded_patterns:
            if re.search(pattern, main_block):
                # More specific check: is this actually overriding the arg?
                # Check if param_name= is used WITHOUT args.param_name
                if f'args.{param_name}' not in main_block or param_name in main_block.split('args.')[0]:
                    issues.append(
                        f"Parameter '{param_name}' appears to be hardcoded instead of using args.{param_name}"
                    )
                    break
    
    return {
        "valid": len(issues) == 0,
        "issues": issues
    }


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
    Execute Python script with MCP function injection
    
    Args:
        script_content: Complete Python script content
        mock_mode: If True, runs in validation mode; if False, production mode
        timeout: Execution timeout in seconds
        parameters: Optional dictionary of parameters to inject into script
        
    Returns:
        Dict with execution results
    """

    logger.info(f"🚀 Executing script (mock={mock_mode}, timeout={timeout}s)")
    
    try:
        # Check for hardcoded parameters before execution
        if parameters:
            param_check = check_for_hardcoded_parameters(script_content, parameters)
            if not param_check["valid"]:
                error_msg = f"Script contains hardcoded parameter values: {'; '.join(param_check['issues'])}"
                logger.error(f"❌ {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "error_type": "HardcodedParametersError",
                    "issues": param_check["issues"],
                    "mock_mode": mock_mode
                }
        
        # Create enhanced script with MCP injection wrapper
        enhanced_script = create_enhanced_script(script_content, mock_mode)
        
        # Write temporary script for subprocess execution
        script_path = _write_temp_script_local(enhanced_script)
        
        # Execute script with parameters as command line arguments
        cmd = [sys.executable, script_path]
        
        # Add parameters as individual arguments
        if parameters:
            for key, value in parameters.items():
                if value is not None:
                    cmd.extend([f'--{key}', str(value)])
        
        start_time = datetime.now()
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.path.dirname(script_path) if os.path.isabs(script_path) else None
        )

        execution_time = (datetime.now() - start_time).total_seconds()
        
        return _process_execution_result(result, execution_time, mock_mode)
                
    except subprocess.TimeoutExpired:
        logger.error(f"❌ Script execution timed out after {timeout}s")
        return {
            "success": False,
            "error": f"Script execution timed out after {timeout} seconds",
            "error_type": "TimeoutError",
            "mock_mode": mock_mode
        }
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