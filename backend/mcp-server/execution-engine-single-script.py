#!/usr/bin/env python3
"""
Single Script Execution Engine with Built-in Validation

Validates and executes single Python scripts for financial analysis.
Supports mock validation and self-correction capabilities.
"""

import json
import logging
import sys
import os
import subprocess
import tempfile
import shutil
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add mcp-server to path for MCP function access
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'mcp-server'))

# Import MCP functions for real execution
try:
    import financial.functions_mock as FinancialLib
    print("✅ Imported financial functions")
except ImportError as e:
    print(f"❌ Failed to import financial functions: {e}")
    FinancialLib = None

try:
    import analytics as AnalyticsLib
    print("✅ Imported analytics functions")
except ImportError as e:
    print(f"❌ Failed to import analytics functions: {e}")
    AnalyticsLib = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("single-script-engine")

app = FastAPI(title="Single Script Financial Analysis Engine")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class ScriptRequest(BaseModel):
    script_content: str
    mock: bool = True
    script_name: Optional[str] = None

class ValidationResult(BaseModel):
    success: bool
    output: Optional[Dict[Any, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None

# Global MCP function registry
MCP_FUNCTIONS = {}

def build_mcp_function_registry():
    """Build registry of available MCP functions"""
    global MCP_FUNCTIONS
    
    if FinancialLib:
        # Financial functions
        financial_functions = [
            "alpaca_trading_positions",
            "alpaca_market_stocks_bars", 
            "alpaca_market_screener_most_actives",
            "alpaca_market_screener_top_gainers",
            "alpaca_market_screener_top_losers",
            "eodhd_screener",
            "eodhd_real_time"
        ]
        
        for func_name in financial_functions:
            if hasattr(FinancialLib, func_name):
                MCP_FUNCTIONS[func_name] = getattr(FinancialLib, func_name)
    
    if AnalyticsLib:
        # Analytics functions  
        analytics_functions = [
            "calculate_returns_metrics",
            "calculate_risk_metrics", 
            "calculate_sma",
            "calculate_rsi",
            "calculate_portfolio_metrics"
        ]
        
        for func_name in analytics_functions:
            if hasattr(AnalyticsLib, func_name):
                MCP_FUNCTIONS[func_name] = getattr(AnalyticsLib, func_name)

    logger.info(f"📚 Registered {len(MCP_FUNCTIONS)} MCP functions")

def create_script_execution_environment(script_content: str, mock: bool = True) -> str:
    """Create enhanced script with MCP function injection"""
    
    # MCP function wrapper for injection
    mcp_wrapper = '''
import json
import logging
from typing import Dict, Any

# MCP Function Registry (injected by execution engine)
_MCP_FUNCTIONS = ''' + json.dumps(list(MCP_FUNCTIONS.keys())) + '''

def call_mcp_function(function_name: str, args: Dict[str, Any]):
    """Call MCP function through execution engine"""
    if _MOCK_MODE:
        # Mock mode - return None, script should handle with mock data
        return None
    else:
        # Production mode - call real MCP function
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'mcp-server'))
        
        # Import and call the function
        if function_name.startswith('alpaca_') or function_name.startswith('eodhd_'):
            import financial.functions_mock as FinancialLib
            if hasattr(FinancialLib, function_name):
                func = getattr(FinancialLib, function_name)
                return func(**args)
        elif function_name.startswith('calculate_'):
            import analytics as AnalyticsLib
            if hasattr(AnalyticsLib, function_name):
                func = getattr(AnalyticsLib, function_name)
                return func(**args)
        
        raise ValueError(f"Unknown MCP function: {function_name}")

# Global mock mode flag (injected by execution engine)
_MOCK_MODE = ''' + str(mock).lower() + '''

'''
    
    # Inject the wrapper at the beginning of the script
    enhanced_script = mcp_wrapper + "\n" + script_content
    
    return enhanced_script

@app.post("/validate-script")
async def validate_script(request: ScriptRequest) -> ValidationResult:
    """Validate script by running it in mock mode"""
    
    logger.info(f"🧪 Validating script (mock={request.mock})")
    
    try:
        # Create enhanced script with MCP injection
        enhanced_script = create_script_execution_environment(
            request.script_content, 
            mock=request.mock
        )
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(enhanced_script)
            script_path = f.name
        
        try:
            # Execute script
            start_time = datetime.now()
            
            cmd = [sys.executable, script_path]
            if request.mock:
                cmd.append("--mock")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            if result.returncode == 0:
                # Parse output
                try:
                    output = json.loads(result.stdout)
                    logger.info("✅ Script validation successful")
                    return ValidationResult(
                        success=True,
                        output=output,
                        execution_time=execution_time
                    )
                except json.JSONDecodeError:
                    # Non-JSON output
                    return ValidationResult(
                        success=True,
                        output={"raw_output": result.stdout},
                        execution_time=execution_time
                    )
            else:
                # Execution failed
                error_msg = result.stderr or result.stdout
                logger.error(f"❌ Script validation failed: {error_msg}")
                return ValidationResult(
                    success=False,
                    error=error_msg,
                    execution_time=execution_time
                )
                
        finally:
            # Cleanup temporary file
            try:
                os.unlink(script_path)
            except:
                pass
                
    except subprocess.TimeoutExpired:
        logger.error("❌ Script validation timed out")
        return ValidationResult(
            success=False,
            error="Script execution timed out after 30 seconds"
        )
    except Exception as e:
        logger.error(f"❌ Script validation error: {e}")
        return ValidationResult(
            success=False,
            error=str(e)
        )

@app.post("/execute-script")
async def execute_script(request: ScriptRequest) -> ValidationResult:
    """Execute script in production mode with real MCP data"""
    
    logger.info("🚀 Executing script in production mode")
    
    # Force production mode
    request.mock = False
    
    return await validate_script(request)

@app.get("/functions")
async def get_functions() -> Dict[str, List[str]]:
    """Get available MCP functions"""
    
    financial_funcs = [name for name in MCP_FUNCTIONS.keys() 
                      if name.startswith(('alpaca_', 'eodhd_'))]
    analytics_funcs = [name for name in MCP_FUNCTIONS.keys() 
                      if name.startswith('calculate_')]
    
    return {
        "financial": financial_funcs,
        "analytics": analytics_funcs,
        "total_count": len(MCP_FUNCTIONS)
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "mcp_functions_loaded": len(MCP_FUNCTIONS),
        "timestamp": datetime.now().isoformat()
    }

class ScriptSaveRequest(BaseModel):
    script_content: str
    script_name: str
    question: str
    validation_passed: bool = False

@app.post("/save-script")
async def save_script(request: ScriptSaveRequest):
    """Save validated script to scripts directory"""
    
    # Create scripts directory if it doesn't exist
    scripts_dir = os.path.join(os.path.dirname(__file__), "scripts")
    os.makedirs(scripts_dir, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"financial_analysis_{request.script_name}_{timestamp}.py"
    filepath = os.path.join(scripts_dir, filename)
    
    # Add metadata header
    script_header = f'''#!/usr/bin/env python3
"""
Financial Analysis Script: {request.question}
Generated: {datetime.now().isoformat()}
Validation Status: {"PASSED" if request.validation_passed else "PENDING"}
"""

'''
    
    # Save script
    with open(filepath, 'w') as f:
        f.write(script_header + request.script_content)
    
    # Make executable
    os.chmod(filepath, 0o755)
    
    logger.info(f"💾 Saved script: {filename}")
    
    return {
        "saved": True,
        "filepath": filepath,
        "filename": filename,
        "execute_commands": {
            "validation": f"python {filepath} --mock",
            "production": f"python {filepath}"
        }
    }

@app.on_event("startup")
async def startup_event():
    """Initialize MCP function registry on startup"""
    build_mcp_function_registry()
    logger.info("🚀 Single Script Execution Engine started")

if __name__ == "__main__":
    logger.info("🚀 Starting Single Script Financial Analysis Engine on port 8006...")
    uvicorn.run(app, host="0.0.0.0", port=8006)