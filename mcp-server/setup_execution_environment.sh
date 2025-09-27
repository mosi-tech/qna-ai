#!/bin/bash
# Setup execution environment for financial analysis scripts

echo "🚀 Setting up financial analysis execution environment..."

# Install minimal required packages for script execution
pip install pandas>=1.5.0
pip install numpy>=1.21.0
pip install pytz>=2022.1
pip install python-dateutil>=2.8.0

echo "✅ Execution environment setup complete!"
echo ""
echo "🔧 To start the servers:"
echo "  1. MCP Validation: python mcp-server/mcp_script_validation_server.py"
echo "  2. HTTP Execution: python mcp-server/http_script_execution_server.py"