#!/usr/bin/env python3
"""
Flat Workflow Execution Engine - Clean Implementation

Supports flat workflow structure with mcp_call and python_function step types.
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

# Global schema cache
FUNCTION_SCHEMAS = {}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("flat-engine")

app = FastAPI(title="Flat Workflow Execution Engine")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def build_function_schemas():
    """Build comprehensive function schema cache from available functions"""
    global FUNCTION_SCHEMAS
    
    # Financial functions from DataLib
    if DataLib and hasattr(DataLib, 'MOCK_FINANCIAL_FUNCTIONS'):
        for fn_name in DataLib.MOCK_FINANCIAL_FUNCTIONS.keys():
            FUNCTION_SCHEMAS[fn_name] = {
                "source": "financial",
                "input_schema": get_function_input_schema(fn_name),
                "output_schema": get_function_output_schema(fn_name),
                "description": f"Financial function: {fn_name}",
                "parameters": get_function_parameters(fn_name)
            }
    
    # Analytics functions from AnalyticsLib  
    if AnalyticsLib:
        for attr_name in dir(AnalyticsLib):
            if not attr_name.startswith('_') and callable(getattr(AnalyticsLib, attr_name)):
                FUNCTION_SCHEMAS[attr_name] = {
                    "source": "analytics",
                    "input_schema": get_function_input_schema(attr_name),
                    "output_schema": get_function_output_schema(attr_name),
                    "description": f"Analytics function: {attr_name}",
                    "parameters": get_function_parameters(attr_name)
                }
    
    logger.info(f"📚 Built schema cache for {len(FUNCTION_SCHEMAS)} functions")

def get_function_input_schema(fn_name: str) -> dict:
    """Get input schema for specific function"""
    # This would typically inspect function signatures or docstrings
    # For now, return basic schema based on known patterns
    if "positions" in fn_name:
        return {"type": "object", "properties": {}}
    elif "bars" in fn_name:
        return {
            "type": "object", 
            "properties": {
                "symbols": {"type": "string", "description": "Comma-separated symbols"},
                "timeframe": {"type": "string", "description": "Bar timeframe"},
                "start": {"type": "string", "description": "Start date"},
                "end": {"type": "string", "description": "End date"}
            },
            "required": ["symbols"]
        }
    else:
        return {"type": "object"}

def get_function_output_schema(fn_name: str) -> dict:
    """Get output schema for specific function"""
    if fn_name in OUTPUT_SCHEMAS:
        return OUTPUT_SCHEMAS[fn_name]
    elif "positions" in fn_name:
        return OUTPUT_SCHEMAS["alpaca_trading_positions"]
    elif "bars" in fn_name:
        return OUTPUT_SCHEMAS["alpaca_market_stocks_bars"] 
    else:
        return {"type": "object"}

def get_function_parameters(fn_name: str) -> dict:
    """Get parameter definitions for specific function"""
    # This would typically use function introspection
    return {
        "required": [],
        "optional": [],
        "types": {}
    }

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
            "server": "flat"
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
            "server": "flat"
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

@app.post("/execute", response_model=ExecutionResponse)
async def execute_plan(request: ExecutionRequest):
    """Execute flat workflow plan"""
    try:
        logger.info(f"📝 Received request: {request.question}")
        
        validation_results = None
        
        # Handle workflow execution
        if not request.plan.workflow:
            return ExecutionResponse(
                success=False, 
                error="No workflow provided in execution plan",
                timestamp=datetime.now().isoformat()
            )
        
        workflow = request.plan.workflow
        
        # Assume workflow is pre-validated during creation phase
        logger.info(f"🚀 Executing pre-validated workflow with {len(workflow.steps)} steps")
        
        context_data = {}
        data_results = []
        
        # Execute workflow steps
        logger.info(f"🚀 Starting flat workflow: {len(workflow.steps)} steps")
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
                                
                                # Schema already validated during creation phase
                                logger.debug(f"📊 Data type: {type(actual_data)}")
                        
                        logger.info(f"✅ Stored {step.output_variable}: {type(context_data[step.output_variable])}")
                    except Exception as e:
                        logger.error(f"❌ Data extraction failed for {step.output_variable}: {e}")
            else:
                logger.error(f"❌ Step {i+1} failed: {result.get('error', 'Unknown error')}")
        
        # Format response
        body = [
            {"key": "question", "value": request.question, "description": "Question analyzed"},
            {"key": "analysis_method", "value": "Flat Workflow Engine", "description": "Pre-validated workflow execution"},
            {"key": "validation_note", "value": "Workflow validated during creation phase", "description": "Validation approach"}
        ]
        
        for i, result in enumerate(data_results):
            if result["success"]:
                step = workflow.steps[i]
                body.append({"key": f"step_{i+1}", "value": f"{result['tool']} via flat", "description": f"Step {step.id or f'step_{i}'} execution"})
        
        # Save result to answers folder as JSON
        try:
            engine_dir = os.path.dirname(__file__)
            answers_dir = os.path.join(engine_dir, "answers")
            os.makedirs(answers_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            clean_question = "".join(c for c in request.question if c.isalnum() or c in (' ', '-', '_')).rstrip()[:50]
            filename = f"flat_workflow_{clean_question.replace(' ', '_')}_{timestamp}.json"
            filepath = os.path.join(answers_dir, filename)
            
            answer_data = {
                "description": request.description,
                "body": body,
                "validation_note": "Pre-validated during workflow creation",
                "metadata": {"timestamp": datetime.now().isoformat(), "engine": "flat"}
            }
            
            with open(filepath, 'w') as f:
                json.dump(answer_data, f, indent=2, default=str)
                
            logger.info(f"💾 Flat workflow answer saved to: {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save answer: {e}")
        
        return ExecutionResponse(
            success=True,
            data={"description": request.description, "body": body, "metadata": {"timestamp": datetime.now().isoformat()}},
            validation_results={"note": "Pre-validated during workflow creation"},
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
        "engine": "flat",
        "features": ["flat_workflow", "python_functions", "schema_validation"]
    }

@app.get("/schemas")
async def get_schemas():
    """Get available output schemas"""
    return {
        "schemas": OUTPUT_SCHEMAS,
        "step_types": ["mcp_call", "python_function"]
    }

@app.get("/functions")
async def get_available_functions():
    """Get all available MCP functions with schemas"""
    if not FUNCTION_SCHEMAS:
        build_function_schemas()
    
    return {
        "functions": FUNCTION_SCHEMAS,
        "count": len(FUNCTION_SCHEMAS),
        "sources": list(set(schema["source"] for schema in FUNCTION_SCHEMAS.values()))
    }

@app.get("/functions/{function_name}")
async def get_function_schema(function_name: str):
    """Get schema for specific function"""
    if not FUNCTION_SCHEMAS:
        build_function_schemas()
    
    if function_name not in FUNCTION_SCHEMAS:
        return {
            "error": f"Function '{function_name}' not found",
            "available": list(FUNCTION_SCHEMAS.keys())[:10]
        }
    
    return FUNCTION_SCHEMAS[function_name]

@app.post("/validate-step")
async def validate_workflow_step(step: dict):
    """Validate a single workflow step against available schemas"""
    if not FUNCTION_SCHEMAS:
        build_function_schemas()
    
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "suggestions": []
    }
    
    if step.get("type") == "mcp_call":
        fn_name = step.get("fn")
        if not fn_name:
            validation_result["valid"] = False
            validation_result["errors"].append("Missing 'fn' parameter for mcp_call")
        elif fn_name not in FUNCTION_SCHEMAS:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Function '{fn_name}' not available")
            validation_result["suggestions"].extend(list(FUNCTION_SCHEMAS.keys())[:5])
        else:
            # Validate arguments against input schema
            function_schema = FUNCTION_SCHEMAS[fn_name]
            step_args = step.get("args", {})
            
            # Basic validation - could be enhanced with jsonschema
            input_schema = function_schema["input_schema"]
            if "required" in input_schema:
                for required_param in input_schema.get("required", []):
                    if required_param not in step_args:
                        validation_result["warnings"].append(f"Missing recommended parameter: {required_param}")
    
    elif step.get("type") == "python_function":
        if not step.get("function_file"):
            validation_result["valid"] = False
            validation_result["errors"].append("Missing 'function_file' for python_function")
        if not step.get("function_name"):
            validation_result["valid"] = False
            validation_result["errors"].append("Missing 'function_name' for python_function")
    
    else:
        validation_result["valid"] = False
        validation_result["errors"].append(f"Unknown step type: {step.get('type')}")
    
    return validation_result

@app.post("/validate-workflow")
async def validate_complete_workflow(workflow: dict):
    """Validate entire workflow for step compatibility"""
    if not FUNCTION_SCHEMAS:
        build_function_schemas()
    
    workflow_result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "step_results": [],
        "data_flow_analysis": []
    }
    
    steps = workflow.get("steps", [])
    context_variables = {}  # Track available variables
    
    for i, step in enumerate(steps):
        step_result = await validate_workflow_step(step)
        step_result["step_index"] = i
        step_result["step_id"] = step.get("id", f"step_{i}")
        
        # Track output variables
        if step.get("output_variable"):
            if step.get("type") == "mcp_call" and step.get("fn") in FUNCTION_SCHEMAS:
                output_schema = FUNCTION_SCHEMAS[step["fn"]]["output_schema"]
                context_variables[step["output_variable"]] = {
                    "type": output_schema.get("type", "object"),
                    "schema": output_schema,
                    "source_step": i
                }
        
        # Validate template variables in args
        if step.get("args"):
            for arg_key, arg_value in step["args"].items():
                if isinstance(arg_value, str) and "{{" in arg_value and "}}" in arg_value:
                    import re
                    template_vars = re.findall(r'\{\{(\w+)\}\}', arg_value)
                    for var_name in template_vars:
                        if var_name not in context_variables:
                            step_result["errors"].append(f"Template variable {{{{var_name}}}} not available")
                            step_result["valid"] = False
        
        workflow_result["step_results"].append(step_result)
        
        if not step_result["valid"]:
            workflow_result["valid"] = False
            workflow_result["errors"].extend(step_result["errors"])
    
    return workflow_result

@app.on_event("startup")
async def startup_event():
    """Initialize schema cache on startup"""
    build_function_schemas()
    logger.info("🚀 Schema cache initialized")

if __name__ == "__main__":
    print("🚀 Starting Flat Workflow Execution Engine...")
    uvicorn.run(app, host="0.0.0.0", port=8005)