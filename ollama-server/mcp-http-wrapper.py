#!/usr/bin/env python3
"""
HTTP Wrapper for MCP Servers

This creates HTTP endpoints that wrap MCP servers running via stdio,
allowing the ollama-server to discover tools without FastMCP dependency.
"""

import asyncio
import json
import logging
import subprocess
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("mcp-http-wrapper")

class MCPHttpWrapper:
    def __init__(self, server_path: str, server_name: str):
        self.server_path = server_path
        self.server_name = server_name
        self.tools_cache = None
        
    async def get_tools_from_mcp_server(self) -> Dict[str, Any]:
        """Get tools from MCP server via stdio communication"""
        if self.tools_cache:
            return self.tools_cache
            
        try:
            # Start MCP server process
            process = await asyncio.create_subprocess_exec(
                sys.executable, self.server_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Send MCP initialization message
            init_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "mcp-http-wrapper",
                        "version": "1.0.0"
                    }
                }
            }
            
            # Send initialization message
            init_data = json.dumps(init_message) + "\n"
            process.stdin.write(init_data.encode())
            await process.stdin.drain()
            
            # Read initialization response
            init_response = await process.stdout.readline()
            logger.debug(f"Init response: {init_response.decode().strip()}")
            
            # Send initialization complete notification
            init_complete = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {}
            }
            
            complete_data = json.dumps(init_complete) + "\n"
            process.stdin.write(complete_data.encode())
            await process.stdin.drain()
            
            # Send list_tools request (correct method name)
            tools_message = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            tools_data = json.dumps(tools_message) + "\n"
            process.stdin.write(tools_data.encode())
            await process.stdin.drain()
            
            # Read tools response
            tools_response = await process.stdout.readline()
            logger.debug(f"Tools response: {tools_response.decode().strip()}")
            
            # Close process
            process.stdin.close()
            await process.wait()
            
            # Parse response
            if tools_response:
                response_data = json.loads(tools_response.decode())
                logger.info(f"Parsed tools response for {self.server_name}: {response_data}")
                
                if "result" in response_data:
                    # MCP servers return tools array directly in result
                    if isinstance(response_data["result"], list):
                        self.tools_cache = {"tools": response_data["result"]}
                    else:
                        self.tools_cache = response_data["result"]
                    return self.tools_cache
                elif "error" in response_data:
                    logger.error(f"MCP server error: {response_data['error']}")
                    
        except Exception as e:
            logger.error(f"Failed to get tools from MCP server {self.server_name}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
        # Return empty tools list if failed
        return {"tools": []}

# Create wrapper instances  
import os
mcp_path = os.path.abspath("../mcp")
financial_wrapper = MCPHttpWrapper(os.path.join(mcp_path, "financial_server_mock.py"), "mcp-financial-server")
analytics_wrapper = MCPHttpWrapper(os.path.join(mcp_path, "analytics_server.py"), "mcp-analytics-server")

# Create FastAPI apps for each server
financial_app = FastAPI(title="MCP Financial Server HTTP Wrapper")
analytics_app = FastAPI(title="MCP Analytics Server HTTP Wrapper")

# Add CORS
for app in [financial_app, analytics_app]:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@financial_app.get("/health")
async def financial_health():
    return {"status": "healthy", "server": "mcp-financial-server", "timestamp": datetime.now().isoformat()}

@financial_app.get("/tools")
async def financial_tools():
    try:
        # Clear cache and fetch fresh tools
        financial_wrapper.tools_cache = None
        tools = await financial_wrapper.get_tools_from_mcp_server()
        logger.info(f"Financial tools endpoint returning: {len(tools.get('tools', []))} tools")
        return tools
    except Exception as e:
        logger.error(f"Error in financial tools endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@analytics_app.get("/health")  
async def analytics_health():
    return {"status": "healthy", "server": "mcp-analytics-server", "timestamp": datetime.now().isoformat()}

@analytics_app.get("/tools")
async def analytics_tools():
    try:
        # Clear cache and fetch fresh tools
        analytics_wrapper.tools_cache = None
        tools = await analytics_wrapper.get_tools_from_mcp_server()
        logger.info(f"Analytics tools endpoint returning: {len(tools.get('tools', []))} tools")
        return tools
    except Exception as e:
        logger.error(f"Error in analytics tools endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_financial_server():
    """Run financial server on port 8001"""
    config = uvicorn.Config(financial_app, host="0.0.0.0", port=8001, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def run_analytics_server():
    """Run analytics server on port 8002"""
    config = uvicorn.Config(analytics_app, host="0.0.0.0", port=8002, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    """Run both HTTP wrapper servers concurrently"""
    logger.info("Starting MCP HTTP wrapper servers...")
    logger.info("Financial server: http://localhost:8001")
    logger.info("Analytics server: http://localhost:8002")
    
    await asyncio.gather(
        run_financial_server(),
        run_analytics_server()
    )

if __name__ == "__main__":
    asyncio.run(main())