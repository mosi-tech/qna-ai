#!/usr/bin/env python3
"""
Direct Execution Engine - Ultra Simple

Just imports modules directly and calls functions on them. No registry, no mapping, no complexity.
"""

import json
import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

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
logger = logging.getLogger("direct-engine")

app = FastAPI(title="Direct Execution Engine")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class ToolCall(BaseModel):
    fn: str
    args: Dict[str, Any]
    output: Optional[str] = None

class PythonFallback(BaseModel):
    data_needed: List[ToolCall]
    script: Optional[str] = None
    script_reference: Optional[str] = None
    function_name: Optional[str] = None

class ExecutionPlan(BaseModel):
    python_fallback: Optional[PythonFallback] = None

class ExecutionRequest(BaseModel):
    question: str
    plan: ExecutionPlan
    description: Optional[str] = None

class ExecutionResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str

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
            "server": "direct"
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

async def execute_python_script(script: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute Python script with context data"""
    try:
        import pandas as pd
        import numpy as np
        import io
        import sys
        
        # Capture stdout
        captured_output = io.StringIO()
        original_stdout = sys.stdout
        sys.stdout = captured_output
        
        logger.info("🐍 Executing Python script...")
        logger.info(f"📊 Context data keys: {list(context_data.keys())}")
        
        namespace = {
            'json': json, 'datetime': datetime, 'pd': pd, 'np': np,
            'context_data': context_data, '__builtins__': __builtins__
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
                         if not k.startswith('_') and k not in ['json', 'datetime', 'pd', 'np', 'context_data']}
            logger.info(f"✅ Script completed, extracted variables: {list(output_data.keys())}")
        
        # Log print output if any
        if print_output.strip():
            logger.info(f"📄 Script output:\n{print_output}")
        
        return {
            "success": True, 
            "result": output_data,
            "stdout": print_output,
            "logs": f"Context keys: {list(context_data.keys())}"
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
    """Execute plan using direct function calls"""
    try:
        logger.info(f"📝 Received request: {request.question}")
        
        if not request.plan.python_fallback:
            return ExecutionResponse(success=False, error="Only python_fallback supported", timestamp=datetime.now().isoformat())
        
        fallback = request.plan.python_fallback
        context_data = {}
        data_results = []
        
        # Execute data gathering
        logger.info(f"🚀 Starting data gathering: {len(fallback.data_needed)} steps")
        for i, tool_call in enumerate(fallback.data_needed):
            # Perform template substitution for this step
            resolved_args = resolve_template_variables(tool_call.args, context_data)
            logger.info(f"📊 Step {i+1}/{len(fallback.data_needed)}: {tool_call.fn} with resolved args {resolved_args}")
            result = execute_function(tool_call.fn, resolved_args)
            data_results.append(result)
            
            if result["success"]:
                logger.info(f"✅ Step {i+1} completed successfully")
                context_data[f"tool_result_{i}"] = result
                
                # Extract data with output variable name
                if tool_call.output:
                    try:
                        logger.info(f"🔍 Extracting data for variable: {tool_call.output}")
                        mcp_result = result.get("result", {})
                        if "content" in mcp_result and len(mcp_result["content"]) > 0:
                            content_text = mcp_result["content"][0].get("text", "")
                            actual_data = json.loads(content_text)
                            context_data[tool_call.output] = actual_data
                            
                            if "positions" in tool_call.fn and isinstance(actual_data, list):
                                context_data["position_symbols"] = [p.get("symbol") for p in actual_data if p.get("symbol")]
                                logger.info(f"📈 Extracted {len(actual_data)} positions, symbols: {context_data['position_symbols']}")
                            
                            logger.info(f"✅ Extracted {tool_call.output}: {type(actual_data)} with {len(actual_data) if hasattr(actual_data, '__len__') else 'N/A'} items")
                        else:
                            context_data[tool_call.output] = None
                            logger.warning(f"⚠️  No content found for {tool_call.output}")
                    except Exception as e:
                        logger.error(f"❌ Data extraction failed for {tool_call.output}: {e}")
                        context_data[tool_call.output] = None
            else:
                logger.error(f"❌ Step {i+1} failed: {result.get('error', 'Unknown error')}")
        
        # Execute Python script
        script_content = fallback.script
        if not script_content and fallback.script_reference:
            # Look for script relative to this engine's directory first, then current working directory
            script_path = fallback.script_reference
            if not os.path.exists(script_path):
                engine_dir = os.path.dirname(__file__)
                script_path = os.path.join(engine_dir, fallback.script_reference)
            
            with open(script_path, 'r') as f:
                script_content = f.read()
        
        if fallback.function_name:
            script_content += f"\n\nresult = {fallback.function_name}()"
        
        script_result = await execute_python_script(script_content, context_data)
        
        # Format response
        body = [
            {"key": "question", "value": request.question, "description": "Question analyzed"},
            {"key": "analysis_method", "value": "Direct Engine", "description": "Direct function calls"}
        ]
        
        for i, result in enumerate(data_results):
            if result["success"]:
                body.append({"key": f"data_source_{i+1}", "value": f"{result['tool']} via direct", "description": f"Data from {result['tool']}"})
        
        if script_result["success"]:
            body.append({"key": "analysis_results", "value": script_result["result"], "description": "Python script results"})
        else:
            body.append({"key": "analysis_error", "value": script_result["error"], "description": "Python script error"})
        
        # Save result to answers folder as JSON
        try:
            # Create answers directory if it doesn't exist
            engine_dir = os.path.dirname(__file__)
            answers_dir = os.path.join(engine_dir, "answers")
            os.makedirs(answers_dir, exist_ok=True)
            
            # Generate filename based on timestamp and question
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Clean question for filename (remove special chars, limit length)
            clean_question = "".join(c for c in request.question if c.isalnum() or c in (' ', '-', '_')).rstrip()[:50]
            filename = f"answer_{clean_question.replace(' ', '_')}_{timestamp}.json"
            filepath = os.path.join(answers_dir, filename)
            
            # Save the complete response as JSON
            answer_data = {
                "description": request.description,
                "body": body,
                "metadata": {"timestamp": datetime.now().isoformat()}
            }
            
            with open(filepath, 'w') as f:
                json.dump(answer_data, f, indent=2, default=str)
                
            logger.info(f"💾 Answer saved to: {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save answer: {e}")
        
        return ExecutionResponse(
            success=True,
            data={"description": request.description, "body": body, "metadata": {"timestamp": datetime.now().isoformat()}},
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Execution failed: {e}")
        return ExecutionResponse(success=False, error=str(e), timestamp=datetime.now().isoformat())

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat(), "engine": "direct"}

if __name__ == "__main__":
    print("🚀 Starting Direct Execution Engine...")
    uvicorn.run(app, host="0.0.0.0", port=8003)