#!/usr/bin/env python3
"""
MCP Client based on official Python SDK example
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)

class MCPClient:
    def __init__(self):
        self.server_configs: Dict[str, Dict[str, Any]] = {}
        self.available_tools: Dict[str, Dict[str, Any]] = {}
        
    async def discover_tools_from_server(self, server_name: str, server_config: Dict[str, Any]) -> Dict[str, Any]:
        """Discover tools from a single MCP server using official pattern"""
        tools = {}
        
        try:
            # Create server parameters
            server_params = StdioServerParameters(
                command=server_config["command"],
                args=server_config.get("args", []),
                env=server_config.get("env", {})
            )
            
            # Use the official pattern with AsyncExitStack
            async with AsyncExitStack() as exit_stack:
                # Start the server process and create streams
                streams = await exit_stack.enter_async_context(stdio_client(server_params))
                read_stream, write_stream = streams
                
                # Create and initialize the session
                session = await exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
                
                # Initialize the session
                init_result = await session.initialize()
                logger.info(f"Connected to MCP server {server_name}: {init_result}")
                
                # List tools
                tools_result = await session.list_tools()
                
                for tool in tools_result.tools:
                    tool_name = tool.name
                    tools[tool_name] = {
                        "name": tool_name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema,
                        "server": server_name
                    }
                    
                logger.info(f"Discovered {len(tools_result.tools)} tools from {server_name}")
                
        except Exception as e:
            logger.error(f"Failed to discover tools from {server_name}: {e}")
            logger.exception(e)
        
        return tools
    
    async def discover_all_tools(self) -> Dict[str, Any]:
        """Discover available tools from all configured MCP servers"""
        all_tools = {}
        
        for server_name, server_config in self.server_configs.items():
            logger.info(f"Discovering tools from {server_name}")
            server_tools = await self.discover_tools_from_server(server_name, server_config)
            all_tools.update(server_tools)
        
        self.available_tools = all_tools
        logger.info(f"Total tools discovered: {len(all_tools)}")
        return all_tools
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a specific MCP tool using official pattern"""
        # Find which server has this tool
        tool_info = self.available_tools.get(tool_name)
        if not tool_info:
            raise ValueError(f"Tool {tool_name} not found in available tools")
        
        server_name = tool_info["server"]
        server_config = self.server_configs.get(server_name)
        if not server_config:
            raise ValueError(f"No config found for server {server_name}")
        
        try:
            # Create server parameters
            server_params = StdioServerParameters(
                command=server_config["command"],
                args=server_config.get("args", []),
                env=server_config.get("env", {})
            )
            
            # Use the official pattern
            async with AsyncExitStack() as exit_stack:
                streams = await exit_stack.enter_async_context(stdio_client(server_params))
                read_stream, write_stream = streams
                
                session = await exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
                await session.initialize()
                
                result = await session.call_tool(tool_name, arguments)
                return result
                
        except Exception as e:
            logger.error(f"Failed to call tool {tool_name}: {e}")
            raise
    
    def validate_function_exists(self, function_name: str) -> bool:
        """Validate that a function exists in available MCP tools"""
        return function_name in self.available_tools
    
    def get_function_schema(self, function_name: str) -> Optional[Dict[str, Any]]:
        """Get the input schema for a specific function"""
        tool_info = self.available_tools.get(function_name)
        if tool_info:
            return tool_info.get("inputSchema")
        return None
    
    def get_tools_summary(self) -> Dict[str, List[str]]:
        """Get a summary of available tools by server"""
        summary = {}
        for tool_name, tool_info in self.available_tools.items():
            server = tool_info["server"]
            if server not in summary:
                summary[server] = []
            summary[server].append(tool_name)
        return summary
    
    async def close_all_sessions(self):
        """Clear cached tools and configurations"""
        self.available_tools.clear()
        self.server_configs.clear()
        logger.info("Cleared MCP client cache")

# Singleton instance
mcp_client = MCPClient()

async def initialize_mcp_client(config: Dict[str, Any]) -> MCPClient:
    """Initialize MCP client with server configurations"""
    client = mcp_client
    
    # Store server configurations
    client.server_configs = config.get("mcpServers", {})
    logger.info(f"Configured {len(client.server_configs)} MCP servers")
    
    # Discover all available tools
    await client.discover_all_tools()
    
    return client

# Test function
async def test_mcp_client():
    """Test the MCP client functionality"""
    config = {
        "mcpServers": {
            "financial-server": {
                "command": "python",
                "args": ["/Users/shivc/Documents/Workspace/JS/qna-ai-admin/mcp/financial_server.py"],
                "env": {
                    "USE_MOCK_FINANCIAL_DATA": "false"
                }
            },
            "analytics-server": {
                "command": "python", 
                "args": ["/Users/shivc/Documents/Workspace/JS/qna-ai-admin/mcp/analytics_server.py"]
            }
        }
    }
    
    client = await initialize_mcp_client(config)
    
    print("MCP Client Test Results:")
    print("=" * 50)
    
    # Show discovered tools
    summary = client.get_tools_summary()
    for server, tools in summary.items():
        print(f"\n{server}: {len(tools)} tools")
        for tool in tools[:5]:  # Show first 5 tools
            print(f"  - {tool}")
        if len(tools) > 5:
            print(f"  ... and {len(tools) - 5} more")
    
    # Test validation
    print(f"\nValidation Tests:")
    print(f"alpaca_market_stocks_bars exists: {client.validate_function_exists('alpaca_market_stocks_bars')}")
    print(f"invalid_function exists: {client.validate_function_exists('invalid_function')}")
    
    await client.close_all_sessions()

if __name__ == "__main__":
    asyncio.run(test_mcp_client())