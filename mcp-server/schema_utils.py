"""
MCP Schema Generation Utilities

Shared utilities for extracting MCP tool schemas from function docstrings
and type hints. Used by both analytics and financial servers.
"""

import inspect
import re
import logging
from typing import Dict, List, Any, Optional, get_type_hints

logger = logging.getLogger(__name__)


def extract_schema_from_docstring(func) -> Optional[Dict[str, Any]]:
    """Extract MCP tool schema from function docstring and type hints.
    
    Parses Google-style docstrings to extract parameter descriptions
    and combines with type hints to generate MCP tool schema.
    
    Args:
        func: Function to analyze
        
    Returns:
        Dict containing description and inputSchema for MCP tool
    """
    try:
        # Get function signature and type hints
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)
        docstring = inspect.getdoc(func)
        
        if not docstring:
            return None
            
        # Extract description (first paragraph of docstring)
        lines = docstring.strip().split('\n')
        description = lines[0].strip()
        
        # Find Args section
        in_args = False
        args_lines = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('Args:'):
                in_args = True
                continue
            elif in_args and (line.startswith('Returns:') or line.startswith('Raises:') or line.startswith('Example:') or line.startswith('Note:')):
                break
            elif in_args and line:
                args_lines.append(line)
        
        # Parse parameter descriptions
        param_descriptions = {}
        current_param = None
        
        for line in args_lines:
            # Match parameter definition: "param_name: description"
            param_match = re.match(r'^(\w+):\s*(.+)', line)
            if param_match:
                current_param = param_match.group(1)
                param_descriptions[current_param] = param_match.group(2)
            elif current_param and line.startswith(' '):
                # Continuation of previous parameter description
                param_descriptions[current_param] += ' ' + line.strip()
        
        # Build schema properties
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            if param_name in ['self', 'cls']:
                continue
                
            # Get type information
            param_type = type_hints.get(param_name, param.annotation)
            json_type = python_type_to_json_type(param_type)
            
            # Get description
            param_desc = param_descriptions.get(param_name, f"Parameter {param_name}")
            
            # Build property schema
            prop_schema = {
                "type": json_type,
                "description": param_desc
            }
            
            # Add default value if available
            if param.default != inspect.Parameter.empty:
                prop_schema["default"] = param.default
            else:
                required.append(param_name)
            
            properties[param_name] = prop_schema
        
        # Build complete schema
        schema = {
            "description": description,
            "inputSchema": {
                "type": "object",
                "properties": properties
            }
        }
        
        if required:
            schema["inputSchema"]["required"] = required
            
        return schema
        
    except Exception as e:
        logger.warning(f"Failed to extract schema for {func.__name__}: {e}")
        return None


def python_type_to_json_type(python_type) -> str:
    """Convert Python type hints to JSON schema types.
    
    Handles common Python types including pandas DataFrame and Series
    which are frequently used in analytics functions.
    """
    if python_type == inspect.Parameter.empty:
        return "string"
    
    # Handle string representation of types
    if isinstance(python_type, str):
        python_type = python_type.lower()
        if 'int' in python_type:
            return "integer"
        elif 'float' in python_type or 'number' in python_type:
            return "number"
        elif 'bool' in python_type:
            return "boolean"
        elif 'list' in python_type or 'array' in python_type:
            return "array"
        elif 'dict' in python_type or 'dataframe' in python_type or 'series' in python_type:
            return "object"
        else:
            return "string"
    
    # Handle actual type objects
    type_str = str(python_type).lower()
    
    # Check for pandas types first (most specific)
    if 'dataframe' in type_str or 'series' in type_str:
        return "object"
    # Check for numpy types
    elif 'ndarray' in type_str or 'numpy' in type_str:
        return "array"
    # Check for Union types (common in analytics functions)
    elif 'union' in type_str:
        # For Union types, default to object since they can accept multiple types
        return "object"
    # Standard Python types
    elif 'int' in type_str:
        return "integer"
    elif 'float' in type_str or 'number' in type_str:
        return "number"
    elif 'bool' in type_str:
        return "boolean"
    elif 'list' in type_str or 'array' in type_str:
        return "array"
    elif 'dict' in type_str:
        return "object"
    else:
        return "string"


def initialize_schema_cache(functions_dict: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Initialize schema cache for a dictionary of functions.
    
    Args:
        functions_dict: Dictionary mapping function names to function objects
        
    Returns:
        Dictionary mapping function names to their MCP schemas
    """
    schema_cache = {}
    
    logger.info(f"Generating schemas for {len(functions_dict)} functions...")
    
    for func_name, func in functions_dict.items():
        try:
            schema = extract_schema_from_docstring(func)
            if schema:
                schema_cache[func_name] = schema
                logger.debug(f"Cached schema for {func_name}")
            else:
                # Fallback schema for functions without proper docstrings
                schema_cache[func_name] = {
                    "description": f"Function: {func_name}",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "data": {"type": "array", "description": "Input data"}
                        },
                        "required": ["data"]
                    }
                }
                logger.warning(f"Using fallback schema for {func_name}")
        except Exception as e:
            logger.error(f"Failed to generate schema for {func_name}: {e}")
            continue
    
    logger.info(f"Schema cache initialized with {len(schema_cache)} functions")
    return schema_cache