#!/usr/bin/env python3
"""
Validated Execution Engine - Enhanced with Schema Validation and Transform Steps

Supports recursive validation, output schemas, and proper data transformation steps.
"""

import json
import logging
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import jsonschema

# Add mcp-server to path for direct imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'mcp-server'))

# Import everything directly
try:
    import financial.functions_mock as DataLib
    print("✅ Imported financial functions as DataLib")
except ImportError as e:
    print(f"❌ Failed to import DataLib: {e}")
    DataLib = None

try:
    import analytics as AnalyticsLib
    print("✅ Imported analytics functions as AnalyticsLib") 
except ImportError as e:
    print(f"❌ Failed to import AnalyticsLib: {e}")
    AnalyticsLib = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("validated-engine")

app = FastAPI(title="Validated Execution Engine")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Schema definitions
OUTPUT_SCHEMAS = {
    "alpaca_trading_positions": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string"},
                "qty": {"type": "number"},
                "market_value": {"type": "number"},
                "unrealized_pl": {"type": "number"}
            }
        }
    },
    "alpaca_market_stocks_bars": {
        "type": "object",
        "properties": {
            "bars": {
                "type": "object",
                "patternProperties": {
                    "^[A-Z]+$": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "t": {"type": "string"},
                                "o": {"type": "number"},
                                "h": {"type": "number"},
                                "l": {"type": "number"},
                                "c": {"type": "number"},
                                "v": {"type": "number"}
                            }
                        }
                    }
                }
            }
        }
    },
    "symbol_list": {
        "type": "array",
        "items": {"type": "string"}
    },
    "csv_symbols": {
        "type": "string"
    }
}

class ValidationConfig(BaseModel):
    recursive: bool = True
    fail_fast: bool = True
    schema_strict: bool = True

class WorkflowStep(BaseModel):
    id: Optional[str] = None
    type: str  # mcp_call, python_function
    fn: Optional[str] = None  # For mcp_call
    args: Optional[Dict[str, Any]] = None  # For mcp_call
    function_file: Optional[str] = None  # For python_function
    function_name: Optional[str] = None  # For python_function
    input_variables: Optional[List[str]] = None  # For python_function
    output_variable: Optional[str] = None
    output_schema: Optional[str] = None
    validates_input_against: Optional[str] = None

class AnalysisWorkflow(BaseModel):
    steps: List[WorkflowStep]

class ExecutionPlan(BaseModel):
    validation: Optional[ValidationConfig] = None
    workflow: Optional[AnalysisWorkflow] = None

class ExecutionRequest(BaseModel):
    question: str
    plan: ExecutionPlan
    description: Optional[str] = None

class ExecutionResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    validation_results: Optional[Dict[str, Any]] = None
    timestamp: str

def validate_schema(data: Any, schema_name: str) -> Dict[str, Any]:
    """Validate data against predefined schema"""
    if schema_name not in OUTPUT_SCHEMAS:
        return {"valid": False, "error": f"Schema '{schema_name}' not found"}
    
    try:
        jsonschema.validate(data, OUTPUT_SCHEMAS[schema_name])
        return {"valid": True}
    except jsonschema.ValidationError as e:
        return {"valid": False, "error": str(e)}

def recursive_validation(steps: List[WorkflowStep]) -> Dict[str, Any]:
    """Perform recursive validation on workflow steps"""
    validation_results = {
        "passed": True,
        "errors": [],
        "warnings": [],
        "step_validations": []
    }
    
    for i, step in enumerate(steps):
        step_result = {"step_id": step.id or f"step_{i}", "valid": True, "issues": []}
        
        # Validate output schema exists
        if step.output_schema and step.output_schema not in OUTPUT_SCHEMAS:
            step_result["valid"] = False
            step_result["issues"].append(f"Unknown output schema: {step.output_schema}")
        
        # Validate input compatibility with previous step
        if step.validates_input_against and i > 0:
            prev_step = steps[i-1]
            if prev_step.output_schema != step.validates_input_against:
                step_result["valid"] = False
                step_result["issues"].append(f"Input validation mismatch: expects {step.validates_input_against}, previous step outputs {prev_step.output_schema}")
        
        # Check python_function step requirements
        if step.type == "python_function":
            if not step.function_file or not step.function_name:
                step_result["issues"].append("Python function step missing function_file or function_name")
        
        # Check mcp_call step requirements  
        if step.type == "mcp_call":
            if not step.fn:
                step_result["issues"].append("MCP call step missing fn parameter")
        
        validation_results["step_validations"].append(step_result)
        
        if not step_result["valid"]:
            validation_results["passed"] = False
            validation_results["errors"].extend(step_result["issues"])
    
    return validation_results

def apply_transform(operation: str, data: Any, **kwargs) -> Any:
    """Apply transformation operations"""
    try:
        if operation == "array_pluck":
            field = kwargs.get("field")
            if isinstance(data, list):
                return [item.get(field) for item in data if isinstance(item, dict) and field in item]
            return []
        
        elif operation == "array_join":
            delimiter = kwargs.get("delimiter", ",")
            if isinstance(data, list):
                return delimiter.join(str(item) for item in data)
            return str(data)
        
        elif operation == "date_subtract":
            period = kwargs.get("period", 6)
            unit = kwargs.get("unit", "months")
            if unit == "months":
                result_date = datetime.now() - timedelta(days=period * 30)
            elif unit == "days":
                result_date = datetime.now() - timedelta(days=period)
            else:
                result_date = datetime.now()
            return result_date.strftime('%Y-%m-%d')
        
        elif operation == "format_symbols":
            if isinstance(data, list):
                return ",".join(str(item) for item in data)
            return str(data)
        
        elif operation == "calculate_returns":
            # Basic return calculation for OHLC data
            if isinstance(data, dict) and "bars" in data:
                results = []
                for symbol, bars in data["bars"].items():
                    if bars and len(bars) > 1:
                        start_price = float(bars[0]["c"])
                        end_price = float(bars[-1]["c"])
                        returns = ((end_price - start_price) / start_price) * 100
                        results.append({
                            "symbol": symbol,
                            "returns": returns,
                            "start_price": start_price,
                            "end_price": end_price
                        })
                return results
            return []
        
        else:
            logger.warning(f"Unknown transform operation: {operation}")
            return data
            
    except Exception as e:
        logger.error(f"Transform operation {operation} failed: {e}")
        return data

def resolve_template_variables(args: Dict[str, Any], context_data: Dict[str, Any]) -> Dict[str, Any]:
    """Resolve template variables like {{variable_name}} in arguments"""
    import re
    resolved_args = {}
    
    for key, value in args.items():
        if isinstance(value, str):
            # Find template variables in the format {{variable_name}}
            template_pattern = r'\{\{(\w+)\}\}'
            matches = re.findall(template_pattern, value)
            
            resolved_value = value
            for match in matches:
                template_var = f"{{{{{match}}}}}"
                
                # Look for the variable in context_data
                if match in context_data:
                    replacement_data = context_data[match]
                    
                    # Handle different data types
                    if isinstance(replacement_data, dict):
                        # For most_actives data, extract symbols
                        if "most_actives" in replacement_data:
                            symbols = [stock["symbol"] for stock in replacement_data["most_actives"]]
                            replacement = ",".join(symbols)
                        else:
                            replacement = str(replacement_data)
                    elif isinstance(replacement_data, list):
                        # Join list items with commas
                        replacement = ",".join(str(item) for item in replacement_data)
                    else:
                        replacement = str(replacement_data)
                    
                    resolved_value = resolved_value.replace(template_var, replacement)
                    logger.info(f"🔄 Resolved {template_var} → {replacement[:50]}{'...' if len(replacement) > 50 else ''}")
                else:
                    logger.warning(f"⚠️  Template variable {template_var} not found in context")
            
            resolved_args[key] = resolved_value
        else:
            resolved_args[key] = value
    
    return resolved_args

def execute_function(fn_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute function directly on the imported modules"""
    try:
        logger.info(f"🔧 Executing {fn_name} with args: {args}")
        
        # Try DataLib first (financial functions)
        if DataLib and hasattr(DataLib, 'MOCK_FINANCIAL_FUNCTIONS') and fn_name in DataLib.MOCK_FINANCIAL_FUNCTIONS:
            result = DataLib.MOCK_FINANCIAL_FUNCTIONS[fn_name](**args)
        # Try AnalyticsLib (analytics functions) 
        elif AnalyticsLib and hasattr(AnalyticsLib, fn_name):
            func = getattr(AnalyticsLib, fn_name)
            result = func(**args)
        else:
            # Function not found
            available = []
            if DataLib and hasattr(DataLib, 'MOCK_FINANCIAL_FUNCTIONS'):
                available.extend(list(DataLib.MOCK_FINANCIAL_FUNCTIONS.keys())[:5])
            if AnalyticsLib:
                available.extend([name for name in dir(AnalyticsLib) if not name.startswith('_')][:5])
            
            return {
                "success": False,
                "error": f"Function '{fn_name}' not found",
                "available_sample": available
            }
        
        # Format result to match expected structure
        return {
            "success": True,
            "tool": fn_name,
            "args": args,
            "result": {
                "content": [{
                    "type": "text", 
                    "text": json.dumps(result, indent=2, default=str)
                }]
            },
            "server": "validated"
        }
        
    except Exception as e:
        logger.error(f"❌ Function {fn_name} failed: {e}")
        import traceback
        return {
            "success": False,
            "error": f"Function execution error: {str(e)}",
            "traceback": traceback.format_exc(),
            "tool": fn_name,
            "args": args
        }

def execute_python_function(step: WorkflowStep, context_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute Python function step"""
    try:
        # Load function from file
        function_file = step.function_file
        if not os.path.exists(function_file):
            engine_dir = os.path.dirname(__file__)
            function_file = os.path.join(engine_dir, step.function_file)
        
        # Read and execute function file
        with open(function_file, 'r') as f:
            function_code = f.read()
        
        # Create namespace and execute function code
        namespace = {
            'json': json, 'datetime': datetime, '__builtins__': __builtins__
        }
        exec(function_code, namespace)
        
        # Get the function
        if step.function_name not in namespace:
            return {
                "success": False,
                "error": f"Function '{step.function_name}' not found in {function_file}",
                "tool": f"python_function_{step.function_name}"
            }
        
        func = namespace[step.function_name]
        
        # Prepare input arguments
        input_args = []
        if step.input_variables:
            for var_name in step.input_variables:
                if var_name in context_data:
                    input_args.append(context_data[var_name])
                else:
                    logger.warning(f"⚠️  Input variable {var_name} not found in context")
                    input_args.append(None)
        
        # Execute function
        if input_args:
            result = func(*input_args)
        else:
            result = func()
        
        return {
            "success": True,
            "tool": f"python_function_{step.function_name}",
            "args": {"input_variables": step.input_variables},
            "result": {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result, indent=2, default=str)
                }]
            },
            "function_result": result,
            "server": "validated"
        }
        
    except Exception as e:
        logger.error(f"❌ Python function {step.function_name} failed: {e}")
        import traceback
        return {
            "success": False,
            "error": f"Python function execution error: {str(e)}",
            "traceback": traceback.format_exc(),
            "tool": f"python_function_{step.function_name}",
            "args": {"input_variables": step.input_variables}
        }

async def execute_python_script(script: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute Python script with context data and validation"""
    try:
        import pandas as pd
        import numpy as np
        import io
        import sys
        
        # Capture stdout
        captured_output = io.StringIO()
        original_stdout = sys.stdout
        sys.stdout = captured_output
        
        logger.info("🐍 Executing Python script with validation...")
        logger.info(f"📊 Context data keys: {list(context_data.keys())}")
        
        namespace = {
            'json': json, 'datetime': datetime, 'pd': pd, 'np': np,
            'context_data': context_data, '__builtins__': __builtins__,
            'validate_schema': validate_schema, 'apply_transform': apply_transform
        }
        
        exec(script, namespace)
        
        # Restore stdout
        sys.stdout = original_stdout
        print_output = captured_output.getvalue()
        
        if 'result' in namespace:
            output_data = namespace['result']
            logger.info(f"✅ Script returned result: {type(output_data)}")
        else:
            output_data = {k: v for k, v in namespace.items() 
                         if not k.startswith('_') and k not in ['json', 'datetime', 'pd', 'np', 'context_data', 'validate_schema', 'apply_transform']}
            logger.info(f"✅ Script completed, extracted variables: {list(output_data.keys())}")
        
        # Log print output if any
        if print_output.strip():
            logger.info(f"📄 Script output:\n{print_output}")
        
        return {
            "success": True, 
            "result": output_data,
            "stdout": print_output,
            "logs": f"Context keys: {list(context_data.keys())}",
            "validation_enabled": True
        }
            
    except Exception as e:
        # Restore stdout in case of error
        sys.stdout = original_stdout
        import traceback
        error_msg = f"Script execution error: {str(e)}"
        logger.error(f"❌ {error_msg}")
        logger.error(f"📄 Traceback:\n{traceback.format_exc()}")
        return {"success": False, "error": error_msg, "traceback": traceback.format_exc()}

@app.post("/execute", response_model=ExecutionResponse)
async def execute_plan(request: ExecutionRequest):
    """Execute plan with validation using direct function calls"""
    try:
        logger.info(f"📝 Received request: {request.question}")
        
        validation_results = None
        
        # Handle workflow with validation (primary execution path)
        if request.plan.workflow:
            workflow = request.plan.workflow
            
            # Validate workflow steps if validation enabled
            if request.plan.validation and request.plan.validation.recursive:
                validation_results = recursive_validation(workflow.steps)
                logger.info(f"🔍 Workflow validation results: {validation_results}")
                
                if not validation_results["passed"] and request.plan.validation.fail_fast:
                    return ExecutionResponse(
                        success=False, 
                        error="Workflow validation failed",
                        validation_results=validation_results,
                        timestamp=datetime.now().isoformat()
                    )
            
            context_data = {}
            data_results = []
            
            # Execute validated workflow steps
            logger.info(f"🚀 Starting validated workflow: {len(workflow.steps)} steps")
            for i, step in enumerate(workflow.steps):
                logger.info(f"📊 Step {i+1}/{len(workflow.steps)}: {step.id or f'step_{i}'} ({step.type})")
                
                if step.type == "python_function":
                    result = execute_python_function(step, context_data)
                elif step.type == "mcp_call":
                    resolved_args = resolve_template_variables(step.args or {}, context_data)
                    result = execute_function(step.fn, resolved_args)
                else:
                    result = {
                        "success": False,
                        "error": f"Unknown step type: {step.type}"
                    }
                
                data_results.append(result)
                
                if result["success"]:
                    logger.info(f"✅ Step {i+1} completed successfully")
                    context_data[f"tool_result_{i}"] = result
                    
                    # Store result with output variable name
                    if step.output_variable:
                        try:
                            if step.type == "python_function" and "function_result" in result:
                                context_data[step.output_variable] = result["function_result"]
                            else:
                                mcp_result = result.get("result", {})
                                if "content" in mcp_result and len(mcp_result["content"]) > 0:
                                    content_text = mcp_result["content"][0].get("text", "")
                                    actual_data = json.loads(content_text)
                                    context_data[step.output_variable] = actual_data
                                    
                                    # Validate against schema if specified
                                    if step.output_schema:
                                        schema_validation = validate_schema(actual_data, step.output_schema)
                                        if not schema_validation["valid"]:
                                            logger.warning(f"⚠️  Schema validation failed for {step.output_variable}: {schema_validation['error']}")
                            
                            logger.info(f"✅ Stored {step.output_variable}: {type(context_data[step.output_variable])}")
                        except Exception as e:
                            logger.error(f"❌ Data extraction failed for {step.output_variable}: {e}")
                else:
                    logger.error(f"❌ Step {i+1} failed: {result.get('error', 'Unknown error')}")
            
            # Format response for workflow execution
            body = [
                {"key": "question", "value": request.question, "description": "Question analyzed"},
                {"key": "analysis_method", "value": "Validated Engine Workflow", "description": "Validated workflow execution"}
            ]
            
            if validation_results:
                body.append({"key": "validation_status", "value": validation_results["passed"], "description": "Recursive validation results"})
            
            for i, result in enumerate(data_results):
                if result["success"]:
                    body.append({"key": f"step_{i+1}", "value": f"{result['tool']} via validated", "description": f"Step {i+1} execution"})
            
            # Save result to answers folder as JSON
            try:
                engine_dir = os.path.dirname(__file__)
                answers_dir = os.path.join(engine_dir, "answers")
                os.makedirs(answers_dir, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                clean_question = "".join(c for c in request.question if c.isalnum() or c in (' ', '-', '_')).rstrip()[:50]
                filename = f"workflow_answer_{clean_question.replace(' ', '_')}_{timestamp}.json"
                filepath = os.path.join(answers_dir, filename)
                
                answer_data = {
                    "description": request.description,
                    "body": body,
                    "validation_results": validation_results,
                    "metadata": {"timestamp": datetime.now().isoformat(), "engine": "validated"}
                }
                
                with open(filepath, 'w') as f:
                    json.dump(answer_data, f, indent=2, default=str)
                    
                logger.info(f"💾 Workflow answer saved to: {filepath}")
                
            except Exception as e:
                logger.error(f"❌ Failed to save answer: {e}")
            
            return ExecutionResponse(
                success=True,
                data={"description": request.description, "body": body, "metadata": {"timestamp": datetime.now().isoformat()}},
                validation_results=validation_results,
                timestamp=datetime.now().isoformat()
            )
        
        else:
            return ExecutionResponse(
                success=False, 
                error="No workflow provided in execution plan",
                timestamp=datetime.now().isoformat()
            )
            if request.plan.validation and request.plan.validation.recursive:
                validation_results = recursive_validation(request.plan.steps)
                logger.info(f"🔍 Validation results: {validation_results}")
                
                if not validation_results["passed"] and request.plan.validation.fail_fast:
                    return ExecutionResponse(
                        success=False, 
                        error="Validation failed",
                        validation_results=validation_results,
                        timestamp=datetime.now().isoformat()
                    )
            
            context_data = {}
            data_results = []
            
            # Execute data gathering with validation
            logger.info(f"🚀 Starting validated workflow: {len(workflow.data_needed)} steps")
            for i, tool_call in enumerate(workflow.data_needed):
                resolved_args = resolve_template_variables(tool_call.args, context_data)
                logger.info(f"📊 Step {i+1}/{len(workflow.data_needed)}: {tool_call.fn} ({tool_call.type})")
                
                if tool_call.type == "transform":
                    result = execute_transform(tool_call, context_data)
                else:
                    result = execute_function(tool_call.fn, resolved_args)
                
                data_results.append(result)
                
                if result["success"]:
                    logger.info(f"✅ Step {i+1} completed successfully")
                    context_data[f"tool_result_{i}"] = result
                    
                    # Extract data with output variable name
                    if tool_call.output_variable:
                        try:
                            logger.info(f"🔍 Extracting data for variable: {tool_call.output_variable}")
                            
                            if tool_call.type == "transform" and "transform_result" in result:
                                context_data[tool_call.output_variable] = result["transform_result"]
                            else:
                                mcp_result = result.get("result", {})
                                if "content" in mcp_result and len(mcp_result["content"]) > 0:
                                    content_text = mcp_result["content"][0].get("text", "")
                                    actual_data = json.loads(content_text)
                                    context_data[tool_call.output_variable] = actual_data
                            
                            # Validate against schema if specified
                            if tool_call.output_schema:
                                schema_validation = validate_schema(context_data[tool_call.output_variable], tool_call.output_schema)
                                if not schema_validation["valid"]:
                                    logger.warning(f"⚠️  Schema validation failed for {tool_call.output_variable}: {schema_validation['error']}")
                            
                            logger.info(f"✅ Extracted {tool_call.output_variable}: {type(context_data[tool_call.output_variable])}")
                        except Exception as e:
                            logger.error(f"❌ Data extraction failed for {tool_call.output_variable}: {e}")
                            context_data[tool_call.output_variable] = None
                else:
                    logger.error(f"❌ Step {i+1} failed: {result.get('error', 'Unknown error')}")
            
            # Execute Python script
            script_content = workflow.script
            if not script_content and workflow.script_reference:
                script_path = workflow.script_reference
                if not os.path.exists(script_path):
                    engine_dir = os.path.dirname(__file__)
                    script_path = os.path.join(engine_dir, workflow.script_reference)
                
                with open(script_path, 'r') as f:
                    script_content = f.read()
            
            if workflow.function_name:
                script_content += f"\n\nresult = {workflow.function_name}()"
            
            script_result = await execute_python_script(script_content, context_data)
            
            # Format response
            body = [
                {"key": "question", "value": request.question, "description": "Question analyzed"},
                {"key": "analysis_method", "value": "Validated Engine Workflow", "description": "Validated workflow with Python analysis"}
            ]
            
            if validation_results:
                body.append({"key": "validation_status", "value": validation_results["passed"], "description": "Recursive validation results"})
            
            for i, result in enumerate(data_results):
                if result["success"]:
                    body.append({"key": f"data_source_{i+1}", "value": f"{result['tool']} via validated", "description": f"Data from {result['tool']}"})
            
            if script_result["success"]:
                body.append({"key": "analysis_results", "value": script_result["result"], "description": "Python script results with validation"})
            else:
                body.append({"key": "analysis_error", "value": script_result["error"], "description": "Python script error"})
            
            # Save result to answers folder as JSON
            try:
                engine_dir = os.path.dirname(__file__)
                answers_dir = os.path.join(engine_dir, "answers")
                os.makedirs(answers_dir, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                clean_question = "".join(c for c in request.question if c.isalnum() or c in (' ', '-', '_')).rstrip()[:50]
                filename = f"workflow_answer_{clean_question.replace(' ', '_')}_{timestamp}.json"
                filepath = os.path.join(answers_dir, filename)
                
                answer_data = {
                    "description": request.description,
                    "body": body,
                    "validation_results": validation_results,
                    "metadata": {"timestamp": datetime.now().isoformat(), "engine": "validated"}
                }
                
                with open(filepath, 'w') as f:
                    json.dump(answer_data, f, indent=2, default=str)
                    
                logger.info(f"💾 Workflow answer saved to: {filepath}")
                
            except Exception as e:
                logger.error(f"❌ Failed to save answer: {e}")
            
            return ExecutionResponse(
                success=True,
                data={"description": request.description, "body": body, "metadata": {"timestamp": datetime.now().isoformat()}},
                validation_results=validation_results,
                timestamp=datetime.now().isoformat()
            )
        
        else:
            return ExecutionResponse(
                success=False, 
                error="No valid execution plan provided",
                timestamp=datetime.now().isoformat()
            )
        
    except Exception as e:
        logger.error(f"❌ Execution failed: {e}")
        import traceback
        return ExecutionResponse(
            success=False, 
            error=str(e), 
            timestamp=datetime.now().isoformat()
        )

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(), 
        "engine": "validated",
        "features": ["recursive_validation", "transform_steps", "schema_enforcement"]
    }

@app.get("/schemas")
async def get_schemas():
    """Get available output schemas"""
    return {
        "schemas": OUTPUT_SCHEMAS,
        "transform_operations": [
            "array_pluck", "array_join", "date_subtract", 
            "format_symbols", "calculate_returns"
        ]
    }

if __name__ == "__main__":
    print("🚀 Starting Validated Execution Engine...")
    uvicorn.run(app, host="0.0.0.0", port=8004)