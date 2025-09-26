#!/usr/bin/env python3
"""
MCP Validation Server - Dedicated server for workflow validation

Provides MCP functions for validating workflow steps, schemas, and complete workflows
during the workflow creation phase.
"""

import json
import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
import re

# Schema-agnostic validation server
# Schemas are provided by the LLM from MCP function discovery

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("validation-server")

# No global schema cache - schemas provided by LLM
# Example schema format for reference
EXAMPLE_SCHEMA_FORMAT = {
    "alpaca_trading_positions": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Stock symbol"},
                "qty": {"type": "number", "description": "Quantity held"},
                "market_value": {"type": "number", "description": "Current market value"},
                "unrealized_pl": {"type": "number", "description": "Unrealized P&L"}
            }
        }
    },
    "alpaca_market_stocks_bars": {
        "type": "object",
        "properties": {
            "bars": {
                "type": "object",
                "description": "OHLC bars by symbol",
                "patternProperties": {
                    "^[A-Z]+$": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "t": {"type": "string", "description": "timestamp"},
                                "o": {"type": "number", "description": "open price"},
                                "h": {"type": "number", "description": "high price"},
                                "l": {"type": "number", "description": "low price"},
                                "c": {"type": "number", "description": "close price"},
                                "v": {"type": "number", "description": "volume"}
                            }
                        }
                    }
                }
            }
        }
    },
    "symbol_list": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Array of stock symbols"
    },
    "csv_symbols": {
        "type": "string",
        "description": "Comma-separated stock symbols"
    }
}

# No function building needed - schemas provided by LLM

# MCP Validation Functions

def mcp_get_available_functions(function_schemas: dict) -> dict:
    """Get all available MCP functions with their schemas"""
    return {
        "functions": function_schemas,
        "count": len(function_schemas),
        "sources": list(set(schema["source"] for schema in function_schemas.values())),
        "categories": ["mcp_call", "python_function"]
    }

def mcp_get_function_schema(function_name: str, function_schemas: dict) -> dict:
    """Get detailed schema for specific MCP function"""
    if function_name not in function_schemas:
        return {
            "error": f"Function '{function_name}' not found",
            "available_functions": list(function_schemas.keys())[:10],
            "suggestions": [fn for fn in function_schemas.keys() if function_name.lower() in fn.lower()][:5]
        }
    
    schema = function_schemas[function_name].copy()
    schema["function_name"] = function_name
    return schema

def mcp_validate_workflow_step(step_definition: dict, function_schemas: dict) -> dict:
    """Validate a single workflow step against available schemas"""
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "suggestions": [],
        "step_type": step_definition.get("type", "unknown")
    }
    
    step_type = step_definition.get("type")
    
    if step_type == "mcp_call":
        fn_name = step_definition.get("fn")
        
        if not fn_name:
            validation_result["valid"] = False
            validation_result["errors"].append("Missing 'fn' parameter for mcp_call step")
            return validation_result
        
        if fn_name not in function_schemas:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Function '{fn_name}' not available")
            # Suggest similar functions
            suggestions = [f for f in function_schemas.keys() if fn_name.lower() in f.lower()]
            if suggestions:
                validation_result["suggestions"] = suggestions[:3]
            return validation_result
        
        # Validate step arguments against function input schema
        function_schema = function_schemas[fn_name]
        step_args = step_definition.get("args", {})
        input_schema = function_schema["input_schema"]
        
        # Check required parameters
        required_params = input_schema.get("required", [])
        for param in required_params:
            if param not in step_args:
                validation_result["warnings"].append(f"Missing recommended parameter: '{param}'")
        
        # Validate parameter types
        properties = input_schema.get("properties", {})
        for arg_name, arg_value in step_args.items():
            if arg_name in properties:
                expected_type = properties[arg_name].get("type")
                if expected_type == "string" and not isinstance(arg_value, str):
                    validation_result["warnings"].append(f"Parameter '{arg_name}' should be string, got {type(arg_value).__name__}")
    
    elif step_type == "python_function":
        function_file = step_definition.get("function_file")
        function_name = step_definition.get("function_name")
        
        if not function_file:
            validation_result["valid"] = False
            validation_result["errors"].append("Missing 'function_file' for python_function step")
        
        if not function_name:
            validation_result["valid"] = False
            validation_result["errors"].append("Missing 'function_name' for python_function step")
        
        # Validate input_variables if provided
        input_variables = step_definition.get("input_variables", [])
        if not input_variables:
            validation_result["warnings"].append("No input_variables specified - function may not receive data")
    
    else:
        validation_result["valid"] = False
        validation_result["errors"].append(f"Unknown step type: '{step_type}'. Valid types: mcp_call, python_function")
    
    return validation_result

def mcp_validate_template_variables(template_string: str, available_variables: dict) -> dict:
    """Validate that template variables can be resolved"""
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "template_variables": [],
        "resolution_plan": {}
    }
    
    # Find template variables
    template_pattern = r'\{\{(\w+)\}\}'
    matches = re.findall(template_pattern, template_string)
    
    for var_name in matches:
        validation_result["template_variables"].append(var_name)
        
        if var_name not in available_variables:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Template variable '{{{{{var_name}}}}}' not available")
        else:
            var_info = available_variables[var_name]
            validation_result["resolution_plan"][var_name] = {
                "source_step": var_info.get("source_step", "unknown"),
                "data_type": var_info.get("type", "unknown"),
                "schema": var_info.get("schema", {})
            }
    
    return validation_result

def mcp_validate_complete_workflow(workflow_definition: dict, function_schemas: dict) -> dict:
    """Validate entire workflow for step compatibility and data flow"""
    workflow_result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "step_results": [],
        "data_flow_analysis": [],
        "available_variables": {}
    }
    
    steps = workflow_definition.get("steps", [])
    context_variables = {}  # Track available variables at each step
    
    for i, step in enumerate(steps):
        step_id = step.get("id", f"step_{i}")
        
        # Validate individual step
        step_result = mcp_validate_workflow_step(step, function_schemas)
        step_result["step_index"] = i
        step_result["step_id"] = step_id
        
        # Track output variables for data flow analysis
        output_var = step.get("output_variable")
        if output_var:
            if step.get("type") == "mcp_call":
                fn_name = step.get("fn")
                if fn_name in function_schemas:
                    output_schema = function_schemas[fn_name]["output_schema"]
                    context_variables[output_var] = {
                        "type": output_schema.get("type", "object"),
                        "schema": output_schema,
                        "source_step": i,
                        "source_function": fn_name
                    }
            elif step.get("type") == "python_function":
                context_variables[output_var] = {
                    "type": "object",  # Python functions can return anything
                    "schema": {"type": "object"},
                    "source_step": i,
                    "source_function": step.get("function_name", "unknown")
                }
        
        # Validate template variables in step arguments
        step_args = step.get("args", {})
        for arg_name, arg_value in step_args.items():
            if isinstance(arg_value, str) and "{{" in arg_value:
                template_validation = mcp_validate_template_variables(arg_value, context_variables)
                if not template_validation["valid"]:
                    step_result["valid"] = False
                    step_result["errors"].extend(template_validation["errors"])
                    workflow_result["valid"] = False
        
        # Add data flow info
        if output_var:
            workflow_result["data_flow_analysis"].append({
                "step": i,
                "step_id": step_id,
                "produces": output_var,
                "data_type": context_variables.get(output_var, {}).get("type", "unknown")
            })
        
        workflow_result["step_results"].append(step_result)
        
        if not step_result["valid"]:
            workflow_result["valid"] = False
            workflow_result["errors"].extend([f"Step {i} ({step_id}): {error}" for error in step_result["errors"]])
    
    workflow_result["available_variables"] = context_variables
    
    return workflow_result

def mcp_suggest_next_step(current_workflow: dict, goal_description: str, function_schemas: dict) -> dict:
    """Suggest next workflow step based on current state and goal"""
    suggestions = {
        "suggested_steps": [],
        "reasoning": [],
        "available_variables": {},
        "next_step_options": []
    }
    
    # Analyze current workflow state
    steps = current_workflow.get("steps", [])
    available_vars = {}
    
    # Track what variables are available
    for i, step in enumerate(steps):
        output_var = step.get("output_variable")
        if output_var and step.get("type") == "mcp_call":
            fn_name = step.get("fn")
            if fn_name in function_schemas:
                available_vars[output_var] = {
                    "type": function_schemas[fn_name]["output_schema"].get("type"),
                    "source": fn_name
                }
    
    # Suggest next steps based on available data and goal
    if "momentum" in goal_description.lower():
        if any("position" in var_source.get("source", "").lower() for var_source in available_vars.values()):
            suggestions["suggested_steps"].append({
                "type": "python_function",
                "function_name": "extract_symbols",
                "rationale": "Extract symbols from positions for momentum analysis"
            })
        
        if "symbol" in str(available_vars):
            suggestions["suggested_steps"].append({
                "type": "mcp_call", 
                "fn": "alpaca_market_stocks_bars",
                "rationale": "Get historical price data for momentum calculation"
            })
    
    suggestions["available_variables"] = available_vars
    return suggestions

# Export MCP functions (note: these now require schema parameters)
MCP_VALIDATION_FUNCTIONS = {
    "get_available_functions": mcp_get_available_functions,
    "get_function_schema": mcp_get_function_schema,
    "validate_workflow_step": mcp_validate_workflow_step,
    "validate_template_variables": mcp_validate_template_variables,
    "validate_complete_workflow": mcp_validate_complete_workflow,
    "suggest_next_step": mcp_suggest_next_step
}

if __name__ == "__main__":
    # Test validation functions with example schemas
    print("🧪 Testing schema-agnostic validation functions...")
    
    # Example schemas for testing
    test_schemas = {
        "alpaca_trading_positions": {
            "source": "financial",
            "input_schema": {"type": "object", "properties": {}},
            "output_schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string"},
                        "qty": {"type": "number"}
                    }
                }
            }
        }
    }
    
    # Test step validation
    test_step = {
        "type": "mcp_call",
        "fn": "alpaca_trading_positions",
        "output_variable": "positions"
    }
    
    result = mcp_validate_workflow_step(test_step, test_schemas)
    print(f"Step validation: {result}")
    
    # Test workflow validation
    test_workflow = {
        "steps": [
            {
                "type": "mcp_call",
                "fn": "alpaca_trading_positions", 
                "output_variable": "positions"
            },
            {
                "type": "python_function",
                "function_file": "extract_symbols.py",
                "function_name": "extract_symbols",
                "input_variables": ["positions"],
                "output_variable": "symbols"
            }
        ]
    }
    
    result = mcp_validate_complete_workflow(test_workflow, test_schemas)
    print(f"Workflow validation: {result}")
    
    print("✅ Schema-agnostic validation server ready!")