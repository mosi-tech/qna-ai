#!/usr/bin/env python3
"""
HTTP Script Execution Server

Executes validated Python scripts via curl commands.
Displays results server-side, never returns data to LLM.
"""

import json
import logging
import os
import secrets
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import shared execution logic
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from shared.execution import execute_script
from shared.storage import get_storage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("http-script-execution")

# ---------------------------------------------------------------------------
# Auth: shared-secret token
# Set EXECUTION_SERVER_TOKEN in the environment (infrastructure/.env).
# If not set a random token is generated at startup — note it in the logs.
# ---------------------------------------------------------------------------
_EXECUTION_TOKEN: str = os.getenv("EXECUTION_SERVER_TOKEN", "")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _EXECUTION_TOKEN
    if not _EXECUTION_TOKEN:
        _EXECUTION_TOKEN = secrets.token_hex(32)
        logger.warning("⚠️  EXECUTION_SERVER_TOKEN not set — generated ephemeral token:")
        logger.warning(f"    EXECUTION_SERVER_TOKEN={_EXECUTION_TOKEN}")
        logger.warning("    Add this to infrastructure/.env to keep it stable across restarts.")
    else:
        logger.info("✅ EXECUTION_SERVER_TOKEN loaded from environment")
    logger.info("🚀 Starting HTTP Script Execution Server on port 8013...")
    yield
    logger.info("🛑 HTTP Script Execution Server shutting down...")


def verify_token(x_execution_token: str = Header(..., alias="X-Execution-Token")):
    """FastAPI dependency — validates the shared execution secret."""
    if x_execution_token != _EXECUTION_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing X-Execution-Token")


app = FastAPI(title="HTTP Script Execution Server", lifespan=lifespan)
# Restrict CORS: this server is internal-only (bound to 127.0.0.1)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8010", "http://127.0.0.1:8010"],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

class ScriptExecutionRequest(BaseModel):
    script_name: str
    production: bool = True
    parameters: Optional[Dict[str, Any]] = None

class ScriptContentRequest(BaseModel):
    script_content: str
    script_name: str

class ExecutionResult(BaseModel):
    success: bool
    script_name: str
    execution_time: Optional[float] = None
    output_preview: Optional[str] = None  # Brief preview, not full results
    error: Optional[str] = None


@app.post("/execute-script", dependencies=[Depends(verify_token)])
async def execute_script_endpoint(request: ScriptExecutionRequest) -> ExecutionResult:
    """Execute validated script in production mode"""
    
    logger.info(f"🚀 Executing script: {request.script_name}")
    
    try:
        # Read script from storage
        storage = get_storage()
        script_content = await storage.read_script(request.script_name)
    except FileNotFoundError:
        logger.error(f"❌ Script not found: {request.script_name}")
        raise HTTPException(status_code=404, detail=f"Script not found: {request.script_name}")
    except Exception as e:
        logger.error(f"❌ Failed to read script from storage: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to read script: {str(e)}")
    
    try:
        
        # Execute script in production mode using shared logic
        execution_result = execute_script(
            script_content=script_content,
            mock_mode=False,  # Production mode
            timeout=300,  # 5 minute timeout
            parameters=request.parameters
        )
        
        if execution_result["success"]:
            # Display results server-side
            output_data = execution_result["output"]
            display_results_server_side(output_data, request.script_name)
            
            # Return minimal success info (no actual data)
            return ExecutionResult(
                success=True,
                script_name=request.script_name,
                execution_time=execution_result["execution_time"],
                output_preview="Results displayed server-side. Check server logs for analysis output."
            )
        else:
            # Execution failed
            logger.error(f"❌ Script execution failed: {execution_result['error']}")
            
            return ExecutionResult(
                success=False,
                script_name=request.script_name,
                execution_time=execution_result.get("execution_time"),
                error=execution_result["error"]
            )
                
    except Exception as e:
        logger.error(f"❌ Execution error: {e}")
        return ExecutionResult(
            success=False,
            script_name=request.script_name,
            error=str(e)
        )

def display_results_server_side(response: dict, script_name: str):
    """Display analysis results on server console - generic formatter"""
    
    print("\n" + "="*100)
    print(f"🔬 FINANCIAL ANALYSIS RESULTS: {script_name}")
    print("="*100)
    
    # Display question
    if "question" in response:
        print(f"📋 Question: {response['question']}")
        print("-" * 50)
    
    # Display analysis status
    if response.get("analysis_completed", False):
        print("✅ Analysis Status: COMPLETED")
    else:
        print("❌ Analysis Status: FAILED")
        if "error" in response:
            print(f"❌ Error: {response['error']}")
        print("="*100 + "\n")
        return
    
    # Display the full results as formatted JSON
    print("\n📊 ANALYSIS RESULTS:")
    print("-" * 50)
    
    # Pretty print the entire response as JSON
    try:
        formatted_json = json.dumps(response, indent=2, default=str, ensure_ascii=False)
        print(formatted_json)
    except Exception as e:
        print(f"Error formatting results: {e}")
        print(str(response))
    
    print("="*100 + "\n")

@app.post("/save-script", dependencies=[Depends(verify_token)])
async def save_script(request: ScriptContentRequest):
    """Save validated script for execution"""
    
    # Add metadata header
    script_header = f'''#!/usr/bin/env python3
"""
Validated Financial Analysis Script
Name: {request.script_name}
Saved: {datetime.now().isoformat()}
Status: Ready for production execution
"""

'''
    
    full_script_content = script_header + request.script_content
    
    # Save script to storage
    storage = get_storage()
    metadata = {
        "script_name": request.script_name,
        "saved_at": datetime.now().isoformat(),
        "status": "ready_for_execution",
        "validated": True
    }
    
    try:
        success = await storage.write_script(
            request.script_name, 
            full_script_content, 
            metadata=metadata
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save script to storage")
            
        logger.info(f"💾 Saved script to storage: {request.script_name}")
    except Exception as e:
        logger.error(f"❌ Failed to save script: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save script: {str(e)}")
    
    return {
        "saved": True,
        "script_name": request.script_name,
        "execute_command": f"curl -X POST http://localhost:8013/execute-script -H 'Content-Type: application/json' -d '{{\"script_name\": \"{request.script_name}\"}}'"
    }

@app.get("/scripts", dependencies=[Depends(verify_token)])
async def list_scripts():
    """List available scripts for execution"""
    
    try:
        storage = get_storage()
        script_names = await storage.list_scripts()
        
        scripts = []
        for script_name in script_names:
            try:
                metadata = await storage.get_script_metadata(script_name)
                if metadata:
                    scripts.append({
                        "name": script_name,
                        "size": metadata.get("size", 0),
                        "modified": metadata.get("modified", "unknown"),
                        "status": metadata.get("status", "unknown"),
                        "execute_command": f"curl -X POST http://localhost:8013/execute-script -H 'Content-Type: application/json' -d '{{\"script_name\": \"{script_name}\"}}'"
                    })
            except Exception as e:
                logger.warning(f"Failed to get metadata for {script_name}: {e}")
                scripts.append({
                    "name": script_name,
                    "size": 0,
                    "modified": "unknown",
                    "status": "unknown",
                    "execute_command": f"curl -X POST http://localhost:8013/execute-script -H 'Content-Type: application/json' -d '{{\"script_name\": \"{script_name}\"}}'"
                })
        
        return {"scripts": scripts}
        
    except Exception as e:
        logger.error(f"❌ Failed to list scripts: {e}")
        return {"scripts": [], "error": str(e)}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "server_mode": "production_execution"
    }

if __name__ == "__main__":
    logger.info("🚀 Starting HTTP Script Execution Server on port 8013 (127.0.0.1 only)...")
    # Bind to loopback only — this server is not meant to be reachable from
    # outside the local machine.
    uvicorn.run(app, host="127.0.0.1", port=8013)