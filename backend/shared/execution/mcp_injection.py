#!/usr/bin/env python3
"""
MCP Function Injection Wrapper

Creates wrapper code that gets injected into executed scripts to provide
MCP function calling capabilities in both production and validation modes.
"""

import os
import logging

logger = logging.getLogger(__name__)

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
        # Strip server prefix if present
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