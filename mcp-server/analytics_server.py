#!/usr/bin/env python3
"""
MCP Analytics Server

Python-based MCP server that provides technical analysis and portfolio analytics:
- Technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands, etc.)
- Risk metrics (VaR, Sharpe ratio, volatility, etc.)
- Portfolio optimization and allocation
- Performance analysis

This server works in conjunction with the financial server to provide
comprehensive market analysis capabilities.
"""

import asyncio
import json
import logging
import inspect
import re
from typing import Dict, List, Any, Optional, get_type_hints

# MCP Server Framework
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Import analytics functions and schema utilities
import analytics
from schema_utils import initialize_schema_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-analytics-server")

# Create server instance
app = Server("mcp-analytics-server")

# Cache for generated schemas - populated once at startup
_schema_cache = {}

# Output schemas for analytics functions
ANALYTICS_OUTPUT_SCHEMAS = {
    "calculate_sma": {
        "type": "array",
        "items": {"type": "number"},
        "description": "Simple moving average values"
    },
    "calculate_rsi": {
        "type": "array", 
        "items": {"type": "number"},
        "description": "RSI indicator values"
    },
    "calculate_correlation_matrix": {
        "type": "object",
        "description": "Correlation matrix between assets"
    },
    "calculate_portfolio_metrics": {
        "type": "object",
        "properties": {
            "returns": {"type": "number"},
            "volatility": {"type": "number"},
            "sharpe_ratio": {"type": "number"}
        },
        "description": "Portfolio performance metrics"
    }
}


def _get_output_schema_for_function(func_name: str) -> Dict[str, Any]:
    """Get output schema for specific analytics function"""
    if func_name in ANALYTICS_OUTPUT_SCHEMAS:
        return ANALYTICS_OUTPUT_SCHEMAS[func_name]
    elif "calculate" in func_name:
        return {"type": "number", "description": f"Calculated result from {func_name}"}
    elif "matrix" in func_name or "correlation" in func_name:
        return {"type": "object", "description": f"Matrix or correlation result from {func_name}"}
    else:
        return {"type": "object", "description": f"Analytics result from {func_name}"}


def _get_function_parameters(func_name: str) -> Dict[str, Any]:
    """Get parameter definitions for specific analytics function"""
    return {
        "required": [],
        "optional": [],
        "types": {}
    }


def initialize_schema_cache():
    """Initialize the schema cache at startup to avoid repeated generation."""
    global _schema_cache
    
    # Automatically discover all analytics functions
    all_functions = {}
    
    # Get all callable functions from the analytics module
    for name, obj in inspect.getmembers(analytics):
        if (inspect.isfunction(obj) and 
            not name.startswith('_') and  # Skip private functions
            hasattr(obj, '__module__') and  # Has module info
            obj.__module__ and obj.__module__.startswith('analytics.')):  # From analytics package
            all_functions[name] = obj
    
    logger.info(f"Auto-discovered {len(all_functions)} analytics functions")
    
    logger.info("Generating schemas for all analytics functions...")
    
    for func_name, func in all_functions.items():
        try:
            schema = extract_schema_from_docstring(func)
            if schema:
                _schema_cache[func_name] = schema
                logger.debug(f"Cached schema for {func_name}")
            else:
                # Fallback schema for functions without proper docstrings
                _schema_cache[func_name] = {
                    "description": f"Analytics function: {func_name}",
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
    
    logger.info(f"Schema cache initialized with {len(_schema_cache)} functions")


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

# Register all analytics functions as MCP tools
@app.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List all available analytics tools"""
    # Use cached schemas for performance
    tools = []
    
    # Add all analytics function tools
    for func_name, schema in _schema_cache.items():
        tools.append(types.Tool(
            name=func_name,
            description=schema['description'],
            inputSchema=schema['inputSchema']
        ))
    
    # Add schema discovery tools for distributed validation
    tools.extend([
        types.Tool(
            name="get_analytics_function_schemas",
            description="Get all analytics function schemas for workflow validation",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="get_analytics_function_schema",
            description="Get schema for specific analytics function",
            inputSchema={
                "type": "object",
                "properties": {
                    "function_name": {
                        "type": "string",
                        "description": "Name of the analytics function to get schema for"
                    }
                },
                "required": ["function_name"],
                "additionalProperties": False
            }
        )
    ])
    
    logger.debug(f"Returned {len(tools)} analytics tools from cache (including schema tools)")
    return tools


@app.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool execution"""
    try:
        logger.info(f"Executing analytics tool: {name} with arguments keys: {list(arguments.keys())}")
        
        # Handle schema discovery tools
        if name == "get_analytics_function_schemas":
            # Return all analytics function schemas with output schemas
            schemas_with_output = {}
            for func_name, schema in _schema_cache.items():
                schemas_with_output[func_name] = {
                    "source": "analytics",
                    "description": schema["description"],
                    "input_schema": schema["inputSchema"],
                    "output_schema": _get_output_schema_for_function(func_name),
                    "parameters": _get_function_parameters(func_name)
                }
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "functions": schemas_with_output,
                    "count": len(schemas_with_output),
                    "source": "analytics",
                    "server": "mcp-analytics-server"
                }, indent=2)
            )]
        
        elif name == "get_analytics_function_schema":
            function_name = arguments["function_name"]
            if function_name not in _schema_cache:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": f"Function '{function_name}' not found",
                        "available_functions": list(_schema_cache.keys())[:10],
                        "suggestions": [fn for fn in _schema_cache.keys() if function_name.lower() in fn.lower()][:5]
                    })
                )]
            
            schema = _schema_cache[function_name]
            detailed_schema = {
                "function_name": function_name,
                "source": "analytics",
                "description": schema["description"],
                "input_schema": schema["inputSchema"],
                "output_schema": _get_output_schema_for_function(function_name),
                "parameters": _get_function_parameters(function_name)
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(detailed_schema, indent=2)
            )]
        
        # Handle regular analytics functions
        elif hasattr(analytics, name):
            # Execute the analytics function
            function = getattr(analytics, name)
            result = function(**arguments)
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        else:
            # Get all available functions for error message
            available_functions = [n for n, obj in inspect.getmembers(analytics) 
                                 if inspect.isfunction(obj) and not n.startswith('_')]
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Unknown analytics tool: {name}",
                    "available_tools": available_functions + ["get_analytics_function_schemas", "get_analytics_function_schema"]
                })
            )]
        
    except Exception as e:
        logger.error(f"Analytics tool execution failed: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"Analytics tool execution failed: {str(e)}"
            })
        )]


async def main():
    """Run the MCP Analytics Server"""
    logger.info("Starting MCP Analytics Server...")
    
    # Initialize schema cache once at startup
    initialize_schema_cache()
    
    logger.info(f"Total functions exposed: {len(_schema_cache)}")
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-analytics-server",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())