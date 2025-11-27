#!/usr/bin/env python3
"""
MCP Server for Analysis and Execution Details

Provides tools for fetching analysis metadata and summarized execution results.
Used by FollowUpChatAgent to answer questions about previous analyses without bloating context.
"""

import asyncio
import json
import logging
import sys
import os
from typing import Any, Dict, List

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# MCP Server Framework
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("analysis-details-server")

# Create server instance
app = Server("analysis-details-server")


@app.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List all available analysis/execution tools"""
    return [
        types.Tool(
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
        types.Tool(
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
        types.Tool(
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
        ),
        types.Tool(
            name="list_session_executions",
            description="List recent executions for a session with basic info (ID, status, timestamp, question)",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "The session ID to get executions for"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of executions to return (default: 5)",
                        "default": 5
                    }
                },
                "required": ["session_id"]
            }
        ),
        types.Tool(
            name="list_session_analyses",
            description="List recent analyses for a session with basic info (ID, timestamp, question)",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "The session ID to get analyses for"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of analyses to return (default: 5)",
                        "default": 5
                    }
                },
                "required": ["session_id"]
            }
        ),
        types.Tool(
            name="get_last_execution",
            description="Get the most recent execution for a session with full details",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "The session ID to get the last execution for"
                    }
                },
                "required": ["session_id"]
            }
        ),
        types.Tool(
            name="get_last_analysis",
            description="Get the most recent analysis for a session with full details",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "The session ID to get the last analysis for"
                    }
                },
                "required": ["session_id"]
            }
        )
    ]


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> List[types.TextContent]:
    """Handle tool calls"""
    logger.info(f"📋 Tool called: {name} with args: {arguments}")
    
    try:
        if name == "get_execution":
            result = await handle_get_execution(arguments)
        elif name == "get_analysis":
            result = await handle_get_analysis(arguments)
        elif name == "get_execution_summary":
            result = await handle_get_execution_summary(arguments)
        elif name == "list_session_executions":
            result = await handle_list_session_executions(arguments)
        elif name == "list_session_analyses":
            result = await handle_list_session_analyses(arguments)
        elif name == "get_last_execution":
            result = await handle_get_last_execution(arguments)
        elif name == "get_last_analysis":
            result = await handle_get_last_analysis(arguments)
        else:
            result = json.dumps({"error": f"Unknown tool: {name}"})
        
        # Wrap result in proper MCP response format
        return [types.TextContent(type="text", text=result)]
    except Exception as e:
        logger.error(f"❌ Error handling tool call: {e}")
        error_result = json.dumps({"error": str(e)})
        return [types.TextContent(type="text", text=error_result)]


async def handle_get_execution(arguments: dict) -> str:
    """Get execution details from database"""
    try:
        execution_id = arguments.get("execution_id")
        
        if not execution_id:
            return json.dumps({"error": "execution_id is required"})
        
        # Get execution from database via MongoDB client
        from shared.db.mongodb_client import MongoDBClient
        
        db_client = MongoDBClient()
        await db_client.connect()
        
        try:
            # Fetch execution from database
            execution = await db_client.get_execution(execution_id)
            
            if not execution:
                return json.dumps({"error": f"Execution {execution_id} not found"})
            
            # Convert ExecutionModel to dict and return
            if hasattr(execution, 'dict'):
                result = execution.dict(by_alias=True)
            else:
                result = execution
            
            return json.dumps(result, default=str)
        finally:
            await db_client.disconnect()
        
    except Exception as e:
        logger.error(f"❌ Error in get_execution: {e}", exc_info=True)
        return json.dumps({"error": str(e)})


async def handle_get_analysis(arguments: dict) -> str:
    """Get analysis metadata from database"""
    try:
        analysis_id = arguments.get("analysis_id")
        
        if not analysis_id:
            return json.dumps({"error": "analysis_id is required"})
        
        # Get analysis from database via MongoDB client
        from shared.db.mongodb_client import MongoDBClient
        
        db_client = MongoDBClient()
        await db_client.connect()
        
        try:
            # Fetch analysis from database
            analysis = await db_client.get_analysis(analysis_id)
            
            if not analysis:
                return json.dumps({"error": f"Analysis {analysis_id} not found"})
            
            # Convert AnalysisModel to dict and return
            if hasattr(analysis, 'dict'):
                result = analysis.dict(by_alias=True)
            else:
                result = analysis
            
            return json.dumps(result, default=str)
        finally:
            await db_client.disconnect()
        
    except Exception as e:
        logger.error(f"❌ Error in get_analysis: {e}", exc_info=True)
        return json.dumps({"error": str(e)})


async def handle_get_execution_summary(arguments: dict) -> str:
    """Get summarized execution results from database"""
    try:
        execution_id = arguments.get("execution_id")
        max_length = arguments.get("max_length", 500)
        
        if not execution_id:
            return json.dumps({"error": "execution_id is required"})
        
        # Get execution from database via MongoDB client
        from shared.db.mongodb_client import MongoDBClient
        
        db_client = MongoDBClient()
        await db_client.connect()
        
        try:
            # Fetch execution from database
            execution = await db_client.get_execution(execution_id)
            
            if not execution:
                return json.dumps({"error": f"Execution {execution_id} not found"})
            
            # Build summary from execution data
            summary = {
                "execution_id": execution_id,
                "status": execution.status.value if hasattr(execution.status, 'value') else str(execution.status),
                "question": getattr(execution, 'question', ''),
            }
            
            # Add result if available and execution was successful
            if hasattr(execution, 'result') and execution.result:
                summary["result"] = execution.result
            
            # Add execution time if available
            if hasattr(execution, 'execution_time_ms'):
                summary["execution_time_ms"] = execution.execution_time_ms
            
            # Add error if execution failed
            if hasattr(execution, 'error') and execution.error:
                summary["error"] = execution.error
            
            result = json.dumps(summary, default=str)
            if len(result) > max_length:
                # Truncate result if too long
                summary["result"] = str(summary.get("result", ""))[:max_length-100]
                result = json.dumps(summary, default=str)
            
            return result
        finally:
            await db_client.disconnect()
        
    except Exception as e:
        logger.error(f"❌ Error in get_execution_summary: {e}", exc_info=True)
        return json.dumps({"error": str(e)})


async def handle_list_session_executions(arguments: dict) -> str:
    """List recent executions for a session"""
    try:
        session_id = arguments.get("session_id")
        limit = arguments.get("limit", 5)
        
        if not session_id:
            return json.dumps({"error": "session_id is required"})
        
        # Get execution history from database via MongoDB client
        from shared.db.mongodb_client import MongoDBClient
        
        db_client = MongoDBClient()
        await db_client.connect()
        
        try:
            # Fetch executions for this session
            executions = await db_client.list_executions(session_id, limit=limit)
            
            # Build summary list
            summary_list = []
            for execution in executions:
                summary_list.append({
                    "execution_id": execution.execution_id,
                    "status": execution.status.value if hasattr(execution.status, 'value') else str(execution.status),
                    "timestamp": execution.created_at.isoformat() if hasattr(execution.created_at, 'isoformat') else str(execution.created_at),
                    "question": getattr(execution, 'question', ''),
                })
            
            return json.dumps({
                "session_id": session_id,
                "count": len(summary_list),
                "executions": summary_list
            }, default=str)
        finally:
            await db_client.disconnect()
        
    except Exception as e:
        logger.error(f"❌ Error in list_session_executions: {e}", exc_info=True)
        return json.dumps({"error": str(e)})


async def handle_list_session_analyses(arguments: dict) -> str:
    """List recent analyses for a session"""
    try:
        session_id = arguments.get("session_id")
        limit = arguments.get("limit", 5)
        
        if not session_id:
            return json.dumps({"error": "session_id is required"})
        
        # Get analysis history from database via MongoDB client
        from shared.db.mongodb_client import MongoDBClient
        
        db_client = MongoDBClient()
        await db_client.connect()
        
        try:
            # Fetch analyses for this session
            analyses = await db_client.find_analyses({
                "sessionId": session_id
            })
            
            # Sort by created_at descending and limit
            if analyses:
                analyses.sort(
                    key=lambda a: a.created_at if hasattr(a.created_at, 'timestamp') else a.created_at,
                    reverse=True
                )
                analyses = analyses[:limit]
            
            # Build summary list
            summary_list = []
            for analysis in analyses:
                summary_list.append({
                    "analysis_id": analysis.analysis_id,
                    "timestamp": analysis.created_at.isoformat() if hasattr(analysis.created_at, 'isoformat') else str(analysis.created_at),
                    "question": getattr(analysis, 'question', ''),
                })
            
            return json.dumps({
                "session_id": session_id,
                "count": len(summary_list),
                "analyses": summary_list
            }, default=str)
        finally:
            await db_client.disconnect()
        
    except Exception as e:
        logger.error(f"❌ Error in list_session_analyses: {e}", exc_info=True)
        return json.dumps({"error": str(e)})


async def handle_get_last_execution(arguments: dict) -> str:
    """Get the most recent execution for a session"""
    try:
        session_id = arguments.get("session_id")
        
        if not session_id:
            return json.dumps({"error": "session_id is required"})
        
        # Get execution from database via MongoDB client
        from shared.db.mongodb_client import MongoDBClient
        
        db_client = MongoDBClient()
        await db_client.connect()
        
        try:
            # Fetch executions for this session (get 1 most recent)
            executions = await db_client.list_executions(session_id, limit=1)
            
            if not executions:
                return json.dumps({"error": f"No executions found for session {session_id}"})
            
            # Convert to dict and return
            execution = executions[0]
            if hasattr(execution, 'dict'):
                result = execution.dict(by_alias=True)
            else:
                result = execution
            
            return json.dumps(result, default=str)
        finally:
            await db_client.disconnect()
        
    except Exception as e:
        logger.error(f"❌ Error in get_last_execution: {e}", exc_info=True)
        return json.dumps({"error": str(e)})


async def handle_get_last_analysis(arguments: dict) -> str:
    """Get the most recent analysis for a session"""
    try:
        session_id = arguments.get("session_id")
        
        if not session_id:
            return json.dumps({"error": "session_id is required"})
        
        # Get analysis from database via MongoDB client
        from shared.db.mongodb_client import MongoDBClient
        
        db_client = MongoDBClient()
        await db_client.connect()
        
        try:
            # Fetch analyses for this session
            analyses = await db_client.find_analyses({
                "sessionId": session_id
            })
            
            if not analyses:
                return json.dumps({"error": f"No analyses found for session {session_id}"})
            
            # Sort by created_at descending and get the first one
            analyses.sort(
                key=lambda a: a.created_at if hasattr(a.created_at, 'timestamp') else a.created_at,
                reverse=True
            )
            
            # Convert to dict and return
            analysis = analyses[0]
            if hasattr(analysis, 'dict'):
                result = analysis.dict(by_alias=True)
            else:
                result = analysis
            
            return json.dumps(result, default=str)
        finally:
            await db_client.disconnect()
        
    except Exception as e:
        logger.error(f"❌ Error in get_last_analysis: {e}", exc_info=True)
        return json.dumps({"error": str(e)})


async def main():
    """Run the MCP server"""
    logger.info("🚀 Starting analysis-details MCP server...")
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="analysis-details",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
