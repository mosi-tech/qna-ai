#!/bin/bash

# Start MCP HTTP Wrapper Servers
# This script starts HTTP wrapper servers that expose MCP server functionality via HTTP

echo "Starting MCP HTTP wrapper servers..."
echo "Financial server will be available at: http://localhost:8001"
echo "Analytics server will be available at: http://localhost:8002"
echo ""
echo "These servers wrap your existing MCP servers and expose them via HTTP"
echo "for the ollama-server to discover tools without FastMCP dependency."
echo ""
echo "Press Ctrl+C to stop both servers."
echo ""

cd "$(dirname "$0")"
python mcp-http-wrapper.py