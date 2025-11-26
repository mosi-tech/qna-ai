#!/usr/bin/env python3
"""
MCP Server for Analysis and Execution Details

Provides tools for fetching analysis metadata and summarized execution results.
Used by FollowUpChatAgent to answer questions about previous analyses without bloating context.
"""

import json
import logging
import sys
from typing import Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("analysis-details-server")

# Try to import MCP server dependencies
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent, NotificationOptions
    from mcp.server import InitializationOptions
except ImportError:
    logger.error("⚠️ MCP dependencies not found. Install with: pip install mcp")
    sys.exit(1)


class AnalysisDetailsServer:
    """MCP Server for analysis and execution details"""
    
    def __init__(self):
        self.server = Server("analysis-details-server")
        self.register_tools()
        self.audit_service = None
    
    def register_tools(self):
        """Register tools available through this MCP server"""
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> str:
            """Handle tool calls"""
            logger.info(f"📋 Tool called: {name} with args: {arguments}")
            
            if name == "get_execution":
                return await self.handle_get_execution(arguments)
            elif name == "get_analysis":
                return await self.handle_get_analysis(arguments)
            elif name == "get_execution_summary":
                return await self.handle_get_execution_summary(arguments)
            else:
                return json.dumps({"error": f"Unknown tool: {name}"})
        
        # Define tool schemas
        self.server.tools = [
            Tool(
                name="get_execution",
                description="Get execution details including script, parameters, and status",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "execution_id": {
                            "type": "string",
                            "description": "The execution ID to fetch"
                        }
                    },
                    "required": ["execution_id"]
                }
            ),
            Tool(
                name="get_analysis",
                description="Get analysis metadata including type, description, and original question",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "analysis_id": {
                            "type": "string",
                            "description": "The analysis ID to fetch"
                        }
                    },
                    "required": ["analysis_id"]
                }
            ),
            Tool(
                name="get_execution_summary",
                description="Get a summarized version of execution results with key metrics only",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "execution_id": {
                            "type": "string",
                            "description": "The execution ID to summarize"
                        },
                        "max_length": {
                            "type": "integer",
                            "description": "Maximum length of summary in characters (default: 500)",
                            "default": 500
                        }
                    },
                    "required": ["execution_id"]
                }
            )
        ]
        
        logger.info(f"✅ Registered {len(self.server.tools)} tools")
    
    async def handle_get_execution(self, arguments: dict) -> str:
        """Get execution details"""
        try:
            execution_id = arguments.get("execution_id")
            
            if not execution_id:
                return json.dumps({"error": "execution_id is required"})
            
            # TODO: Connect to audit_service when available
            # For now, return placeholder
            return json.dumps({
                "execution_id": execution_id,
                "generated_script": "analysis_script.py",
                "execution_params": {
                    "assets": ["AAPL", "MSFT"],
                    "period": "1y",
                    "transaction_cost": 0.001
                },
                "status": "completed",
                "execution_time": 2.345,
                "note": "Connect audit_service in production"
            })
            
        except Exception as e:
            logger.error(f"❌ Error in get_execution: {e}")
            return json.dumps({"error": str(e)})
    
    async def handle_get_analysis(self, arguments: dict) -> str:
        """Get analysis metadata"""
        try:
            analysis_id = arguments.get("analysis_id")
            
            if not analysis_id:
                return json.dumps({"error": "analysis_id is required"})
            
            # TODO: Connect to audit_service when available
            # For now, return placeholder
            return json.dumps({
                "analysis_id": analysis_id,
                "analysis_type": "correlation",
                "description": "Correlation analysis between two assets",
                "question": "What is the correlation between AAPL and MSFT?",
                "created_at": "2024-01-15T10:30:00Z",
                "note": "Connect audit_service in production"
            })
            
        except Exception as e:
            logger.error(f"❌ Error in get_analysis: {e}")
            return json.dumps({"error": str(e)})
    
    async def handle_get_execution_summary(self, arguments: dict) -> str:
        """Get summarized execution results"""
        try:
            execution_id = arguments.get("execution_id")
            max_length = arguments.get("max_length", 500)
            
            if not execution_id:
                return json.dumps({"error": "execution_id is required"})
            
            # TODO: Connect to audit_service and summarize results
            # For now, return placeholder
            summary = {
                "execution_id": execution_id,
                "key_metrics": {
                    "correlation": 0.75,
                    "p_value": 0.001,
                    "sample_size": 252
                },
                "status": "completed",
                "summary": "Strong positive correlation detected",
                "note": "Connect audit_service in production"
            }
            
            result = json.dumps(summary)
            if len(result) > max_length:
                # Truncate to max_length if needed
                summary["summary"] = summary["summary"][:max_length-50]
                result = json.dumps(summary)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in get_execution_summary: {e}")
            return json.dumps({"error": str(e)})
    
if __name__ == "__main__":
    import asyncio
    import mcp.server.stdio
    
    async def main():
        """Run the MCP server"""
        logger.info("🚀 Starting analysis-details MCP server...")
        
        server_instance = AnalysisDetailsServer()
        
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server_instance.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="analysis-details",
                    server_version="1.0.0",
                    capabilities=server_instance.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )
            logger.info("✅ Server running and listening for tool calls")
    
    asyncio.run(main())
