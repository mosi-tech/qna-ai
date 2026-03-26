#!/usr/bin/env python3
"""
MCP Client based on official Python SDK example

Sessions are cached per server — the subprocess is spawned once and reused
for all tool calls within the lifetime of the client instance.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client

logger = logging.getLogger(__name__)

class MCPClient:
    def __init__(self):
        self.server_configs: Dict[str, Dict[str, Any]] = {}
        self.available_tools: Dict[str, Dict[str, Any]] = {}
        # Persistent sessions — one subprocess per server, reused across calls
        self._sessions: Dict[str, ClientSession] = {}
        self._exit_stacks: Dict[str, AsyncExitStack] = {}
        # Track which event loop each session belongs to
        self._session_loops: Dict[str, Any] = {}
        # Per-server locks to prevent concurrent session creation
        self._session_locks: Dict[str, Any] = {}

    async def _get_or_create_session(self, server_name: str, server_config: Dict[str, Any]) -> ClientSession:
        """Return cached session or connect/spawn and keep it alive.

        If server_config has a 'url' key, connects via SSE (HTTP persistent server).
        Otherwise spawns a stdio subprocess.

        Sessions are evicted when called from a different event loop (e.g. worker threads).
        """
        current_loop = asyncio.get_running_loop()

        # Ensure per-server lock exists
        if server_name not in self._session_locks:
            self._session_locks[server_name] = asyncio.Lock()

        async with self._session_locks[server_name]:
            # Evict session if it was created in a different event loop
            if server_name in self._sessions:
                if self._session_loops.get(server_name) is not current_loop:
                    logger.info(f"🔄 Event loop changed for {server_name} — evicting stale session")
                    await self._close_session(server_name)
                else:
                    return self._sessions[server_name]

            exit_stack = AsyncExitStack()
            await exit_stack.__aenter__()

            url = server_config.get("url")
            if url:
                # SSE transport — connect to a running HTTP server
                streams = await exit_stack.enter_async_context(sse_client(url))
                logger.info(f"✅ SSE session connected to {server_name} at {url}")
            else:
                # Stdio transport — spawn subprocess
                server_params = StdioServerParameters(
                    command=server_config["command"],
                    args=server_config.get("args", []),
                    env=server_config.get("env", {})
                )
                streams = await exit_stack.enter_async_context(stdio_client(server_params))
                logger.info(f"✅ Stdio session started for {server_name}")

            read_stream, write_stream = streams
            session = await exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
            await session.initialize()

            self._sessions[server_name] = session
            self._exit_stacks[server_name] = exit_stack
            self._session_loops[server_name] = current_loop
            return session

    async def discover_tools_from_server(self, server_name: str, server_config: Dict[str, Any]) -> Dict[str, Any]:
        """Discover tools from a single MCP server, reusing a persistent session."""
        tools = {}
        try:
            session = await self._get_or_create_session(server_name, server_config)
            tools_result = await session.list_tools()

            for tool in tools_result.tools:
                original_name = tool.name
                prefixed_name = f"{server_name}__{original_name}"
                tools[prefixed_name] = {
                    "name": prefixed_name,
                    "original_name": original_name,
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
        """Discover available tools from all configured MCP servers."""
        all_tools = {}
        for server_name, server_config in self.server_configs.items():
            logger.info(f"Discovering tools from {server_name}")
            server_tools = await self.discover_tools_from_server(server_name, server_config)
            all_tools.update(server_tools)

        self.available_tools = all_tools
        logger.info(f"Total tools discovered: {len(all_tools)}")
        return all_tools

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a specific MCP tool, reusing the persistent session for that server."""
        tool_info = self.available_tools.get(tool_name)
        if not tool_info:
            raise ValueError(f"Tool {tool_name} not found in available tools")

        server_name = tool_info["server"]
        original_name = tool_info.get("original_name", tool_name)

        server_config = self.server_configs.get(server_name)
        if not server_config:
            raise ValueError(f"No config found for server {server_name}")

        try:
            session = await self._get_or_create_session(server_name, server_config)
            result = await session.call_tool(original_name, arguments)
            return result
        except Exception as e:
            logger.error(f"Failed to call tool {tool_name} (original: {original_name}): {e}")
            # Session may be broken — evict it so the next call spawns a fresh one
            await self._close_session(server_name)
            raise

    async def _close_session(self, server_name: str):
        """Close and evict a single server session."""
        exit_stack = self._exit_stacks.pop(server_name, None)
        self._sessions.pop(server_name, None)
        self._session_loops.pop(server_name, None)
        if exit_stack:
            try:
                await exit_stack.__aexit__(None, None, None)
            except Exception:
                pass

    def validate_function_exists(self, function_name: str) -> bool:
        return function_name in self.available_tools

    def get_function_schema(self, function_name: str) -> Optional[Dict[str, Any]]:
        tool_info = self.available_tools.get(function_name)
        if tool_info:
            return tool_info.get("inputSchema")
        return None

    def get_tools_summary(self) -> Dict[str, List[str]]:
        summary = {}
        for tool_name, tool_info in self.available_tools.items():
            server = tool_info["server"]
            if server not in summary:
                summary[server] = []
            summary[server].append(tool_name)
        return summary

    def find_function_server(self, function_name: str) -> Dict[str, Any]:
        results = []
        for tool_name, tool_info in self.available_tools.items():
            original_name = tool_info.get("original_name", tool_name)
            if original_name == function_name:
                results.append({
                    "server": tool_info["server"],
                    "prefixed_name": tool_name,
                    "original_name": original_name,
                    "description": tool_info.get("description", "")
                })

        if not results:
            return {
                "success": False,
                "function_name": function_name,
                "error": f"Function '{function_name}' not found in any server",
                "suggestion": "Check available functions or verify the function name"
            }

        return {
            "success": True,
            "function_name": function_name,
            "found_in_servers": results,
            "recommendation": f"Use {results[0]['server']}__get_function_docstring to get docstring for this function"
        }

    async def close_all_sessions(self):
        """Shut down all persistent server subprocesses."""
        for server_name in list(self._exit_stacks.keys()):
            await self._close_session(server_name)
        self.available_tools.clear()
        self.server_configs.clear()
        logger.info("All MCP sessions closed")


# Singleton instance
mcp_client = MCPClient()

async def initialize_mcp_client(config: Dict[str, Any]) -> MCPClient:
    """Initialize MCP client with server configurations."""
    client = mcp_client
    client.server_configs = config.get("mcpServers", {})
    logger.info(f"Configured {len(client.server_configs)} MCP servers")
    await client.discover_all_tools()
    return client
