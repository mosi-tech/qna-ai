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
import shutil
from datetime import datetime
from typing import Dict, Any, Optional

# Add paths for direct MCP imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Direct imports from MCP modules
try:
    import financial.functions_mock as financial_functions
    print("✅ Imported financial functions directly")
except ImportError as e:
    print(f"❌ Failed to import financial functions: {e}")
    financial_functions = None

try:
    import analytics as analytics_functions  
    print("✅ Imported analytics functions directly")
except ImportError as e:
    print(f"❌ Failed to import analytics functions: {e}")
    analytics_functions = None

logger = logging.getLogger("shared-script-executor")

def create_mcp_injection_wrapper(production_mode: bool = False):
    """Create MCP function injection wrapper for script execution"""
    
    if production_mode:
        # Production mode: Real MCP function calls
        return '''
import sys
import os
import json
import logging

def convert_for_json(obj):
    """
    Convert nested objects with pandas/numpy types to JSON-serializable format
    Handles nested dictionaries, lists, and complex data structures
    """
    import numpy as np
    import pandas as pd
    
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Series):
        return obj.tolist()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict('records')
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, dict):
        return {key: convert_for_json(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_for_json(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        return convert_for_json(obj.__dict__)
    else:
        return str(obj)  # Fallback to string representation


# Add MCP server directory to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = "/Users/shivc/Documents/Workspace/JS/qna-ai-admin"
mcp_server_dir = os.path.join(project_root, 'backend/mcp-server')

# Add both possible locations to path
for path in [script_dir, mcp_server_dir]:
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)

import financial.functions_real as financial_lib
import analytics as analytics_lib

def call_mcp_function(function_name: str, args: dict):
    """Call real MCP functions in production mode"""
    try:
        # Strip server prefix if present (e.g., "financial_server__eodhd_eod_data" -> "eodhd_eod_data")
        actual_function_name = function_name.split('__')[-1] if '__' in function_name else function_name
        
        # Direct imports for production
        if hasattr(financial_lib, actual_function_name):
                func = getattr(financial_lib, actual_function_name)
                result = func(**args)
                logging.info(f"✅ MCP call successful: {actual_function_name} (from {function_name})")
                return result
        elif hasattr(analytics_lib, actual_function_name):
                func = getattr(analytics_lib, actual_function_name)
                result = func(**args)
                logging.info(f"✅ MCP call successful: {actual_function_name} (from {function_name})")
                return result
        
        raise Exception(f"Unknown MCP function: {actual_function_name} (from {function_name})") 
        
    except Exception as e:
        logging.error(f"❌ MCP call failed {function_name}: {e}")
        raise
        

# Production logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
'''
    else:
        # Validation mode: Use actual modules but with mock data
        return '''
import sys
import os
import json
import logging

def convert_for_json(obj):
    """
    Convert nested objects with pandas/numpy types to JSON-serializable format
    Handles nested dictionaries, lists, and complex data structures
    """
    import numpy as np
    import pandas as pd
    
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Series):
        return obj.tolist()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict('records')
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, dict):
        return {key: convert_for_json(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_for_json(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        return convert_for_json(obj.__dict__)
    else:
        return str(obj)  # Fallback to string representation

# Add MCP server directory to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = "/Users/shivc/Documents/Workspace/JS/qna-ai-admin"
mcp_server_dir = os.path.join(project_root, 'backend/mcp-server')

# Add both possible locations to path
for path in [script_dir, mcp_server_dir]:
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)

import financial.functions_mock as financial_lib
import analytics as analytics_lib

def call_mcp_function(function_name: str, args: dict):
    """Call actual MCP functions in validation mode"""
    try:
        # Strip server prefix if present (e.g., "financial_server__eodhd_eod_data" -> "eodhd_eod_data")
        actual_function_name = function_name.split('__')[-1] if '__' in function_name else function_name
        
        # Check financial functions first
        if hasattr(financial_lib, actual_function_name):
            func = getattr(financial_lib, actual_function_name)
            result = func(**args)
            logging.info(f"✅ MCP call successful: {actual_function_name} (from {function_name})")
            return result
        elif hasattr(analytics_lib, actual_function_name):
            func = getattr(analytics_lib, actual_function_name)
            result = func(**args)
            logging.info(f"✅ MCP call successful: {actual_function_name} (from {function_name})")
            return result
        
        raise Exception(f"Unknown MCP function: {actual_function_name} (from {function_name})")
        
    except Exception as e:
        import traceback
        logging.error(f"❌ MCP call failed {function_name}: {e}")
        logging.error(f"Full traceback: {traceback.format_exc()}")
        raise

# Validation logging  
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
'''


def create_enhance_script(script_content: str, mock_mode: bool = True, parameters: Optional[Dict[str, Any]] = None) -> str:
    # Create MCP injection wrapper
        mcp_wrapper = create_mcp_injection_wrapper(production_mode=not mock_mode)
        
        # Add parameter injection if parameters provided
        parameter_injection = ""
        if parameters:
            parameter_injection = f"\n# Parameter injection\nPARAMETERS = {json.dumps(parameters, indent=2)}\n\n"
        
        enhanced_script = mcp_wrapper + parameter_injection + script_content
        return enhanced_script


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
        # Get project root directory - hardcoded for MCP testing
        project_root = "/Users/shivc/Documents/Workspace/JS/qna-ai-admin/backend/mcp-server/"
        
        # Create enhance script
        enhanced_script = create_enhance_script(script_content, mock_mode, parameters)
        
        # logger.info(enhanced_script)
        
        # Create temporary file in project directory with predictable name for debugging
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        script_path = os.path.join(project_root, "temp", f"temp_validation_script_{timestamp}.py")
        with open(script_path, 'w') as f:
            f.write(enhanced_script)
        
        # Execute script - mode is already embedded in the enhanced script via MCP wrapper
        cmd = [sys.executable, script_path]
        
        start_time = datetime.now()
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=project_root
        )

        execution_time = (datetime.now() - start_time).total_seconds()
        
        if result.returncode == 0:

            # Subprocess executed without crashing
            try:
                # Try to parse as JSON
                output_data = json.loads(result.stdout)
                
                # Check if the script itself reports analysis success/failure
                script_success = output_data.get("analysis_completed", False)
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
                        "mock_mode": mock_mode
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
                        # "suggestion": get_package_suggestion(forbidden)
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
        
        # Check for .get() with defaults - FAIL FAST
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
        
        # Check for defensive if result checks - FAIL FAST
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

def get_package_suggestion(forbidden_package: str) -> str:
    """Get suggested alternative for forbidden packages"""
    suggestions = {
        'yfinance': 'Use MCP financial server: call_mcp_function("financial_server__alpaca_market_stocks_bars", args)',
        'quandl': 'Use MCP financial server: call_mcp_function("financial_server__eodhd_real_time", args)',
        'alpha_vantage': 'Use MCP financial server: call_mcp_function("financial_server__alpaca_market_stocks_bars", args)',
        'matplotlib': 'Remove visualization - analysis scripts should return data only',
        'plotly': 'Remove visualization - analysis scripts should return data only',
        'seaborn': 'Remove visualization - analysis scripts should return data only',
        'requests': 'Use MCP functions instead of external HTTP requests'
    }
    return suggestions.get(forbidden_package, 'Use approved packages from execution_requirements.txt')