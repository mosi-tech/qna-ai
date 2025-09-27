#!/usr/bin/env python3
"""
HTTP Script Execution Server

Executes validated Python scripts via curl commands.
Displays results server-side, never returns data to LLM.
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import shared execution logic
from shared_script_executor import execute_script

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("http-script-execution")

app = FastAPI(title="HTTP Script Execution Server")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class ScriptExecutionRequest(BaseModel):
    script_name: str
    production: bool = True

class ScriptContentRequest(BaseModel):
    script_content: str
    script_name: str

class ExecutionResult(BaseModel):
    success: bool
    script_name: str
    execution_time: Optional[float] = None
    output_preview: Optional[str] = None  # Brief preview, not full results
    error: Optional[str] = None


@app.post("/execute-script")
async def execute_script_endpoint(request: ScriptExecutionRequest) -> ExecutionResult:
    """Execute validated script in production mode"""
    
    logger.info(f"🚀 Executing script: {request.script_name}")
    
    # Get scripts directory
    scripts_dir = os.path.join(os.path.dirname(__file__), "scripts")
    script_path = os.path.join(scripts_dir, request.script_name)
    
    if not os.path.exists(script_path):
        logger.error(f"❌ Script not found: {request.script_name}")
        raise HTTPException(status_code=404, detail=f"Script not found: {request.script_name}")
    
    try:
        # Read the validated script
        with open(script_path, 'r') as f:
            script_content = f.read()
        
        # Execute script in production mode using shared logic
        execution_result = execute_script(
            script_content=script_content,
            mock_mode=False,  # Production mode
            timeout=300  # 5 minute timeout
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
    """Display analysis results on server console"""
    
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
    
    # Extract nested results if they exist
    analysis_results = response.get("results", response)
    
    # Display key results
    if "outperformers" in analysis_results:
        etfs = analysis_results["outperformers"]
        print(f"\n🏆 Found {len(etfs)} ETFs outperforming benchmarks:")
        
        for i, etf in enumerate(etfs[:10], 1):  # Top 10
            symbol = etf.get("symbol", "N/A")
            return_pct = etf.get("total_return_pct", "N/A")
            vs_spy = etf.get("excess_return_vs_spy", "N/A")
            vs_qqq = etf.get("excess_return_vs_qqq", "N/A")
            
            print(f"  {i:2d}. {symbol:6s} | Return: {return_pct:>6}% | vs SPY: +{vs_spy:>5}% | vs QQQ: +{vs_qqq:>5}%")
    
    # Display benchmarks
    if "benchmarks" in analysis_results:
        benchmarks = analysis_results["benchmarks"]
        print(f"\n📊 Benchmark Performance:")
        
        for symbol, data in benchmarks.items():
            return_pct = data.get("return_pct", "N/A")
            volatility = data.get("volatility_pct", "N/A")
            print(f"  {symbol}: {return_pct}% return | {volatility}% volatility")
    
    # Display summary
    if "analysis_summary" in analysis_results:
        summary = analysis_results["analysis_summary"]
        total_analyzed = summary.get("total_etfs_analyzed", 0)
        outperformers = summary.get("etfs_outperforming_both", 0)
        success_rate = summary.get("outperformance_rate", "N/A")
        
        print(f"\n📈 Summary:")
        print(f"  Total ETFs Analyzed: {total_analyzed}")
        print(f"  Outperformers Found: {outperformers}")
        print(f"  Success Rate: {success_rate}%")
    
    # Display metadata
    if "metadata" in response:
        metadata = response["metadata"]
        timestamp = metadata.get("timestamp", "N/A")
        analysis_method = metadata.get("analysis_method", "N/A")
        
        print(f"\n🔬 Analysis Details:")
        print(f"  Timestamp: {timestamp}")
        print(f"  Method: {analysis_method}")
    
    print("="*100 + "\n")

@app.post("/save-script")
async def save_script(request: ScriptContentRequest):
    """Save validated script for execution"""
    
    # Create scripts directory if it doesn't exist
    scripts_dir = os.path.join(os.path.dirname(__file__), "scripts")
    os.makedirs(scripts_dir, exist_ok=True)
    
    # Save script
    script_path = os.path.join(scripts_dir, request.script_name)
    
    # Add metadata header
    script_header = f'''#!/usr/bin/env python3
"""
Validated Financial Analysis Script
Name: {request.script_name}
Saved: {datetime.now().isoformat()}
Status: Ready for production execution
"""

'''
    
    with open(script_path, 'w') as f:
        f.write(script_header + request.script_content)
    
    # Make executable
    os.chmod(script_path, 0o755)
    
    logger.info(f"💾 Saved script: {request.script_name}")
    
    return {
        "saved": True,
        "script_name": request.script_name,
        "script_path": script_path,
        "execute_command": f"curl -X POST http://localhost:8007/execute-script -H 'Content-Type: application/json' -d '{{\"script_name\": \"{request.script_name}\"}}'"
    }

@app.get("/scripts")
async def list_scripts():
    """List available scripts for execution"""
    
    scripts_dir = os.path.join(os.path.dirname(__file__), "scripts")
    
    if not os.path.exists(scripts_dir):
        return {"scripts": []}
    
    scripts = []
    for filename in os.listdir(scripts_dir):
        if filename.endswith('.py'):
            filepath = os.path.join(scripts_dir, filename)
            stat = os.stat(filepath)
            
            scripts.append({
                "name": filename,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "execute_command": f"curl -X POST http://localhost:8007/execute-script -H 'Content-Type: application/json' -d '{{\"script_name\": \"{filename}\"}}'"
            })
    
    return {"scripts": scripts}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "server_mode": "production_execution"
    }

@app.on_event("startup")
async def startup_event():
    """Initialize server on startup"""
    logger.info("🚀 HTTP Script Execution Server started on port 8007")

if __name__ == "__main__":
    logger.info("🚀 Starting HTTP Script Execution Server on port 8007...")
    uvicorn.run(app, host="0.0.0.0", port=8007)