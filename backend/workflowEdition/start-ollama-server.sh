#!/bin/bash

# Start Ollama MCP Financial Analysis Server

echo "Setting up Ollama MCP Integration..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements-ollama.txt

# Check if MCP servers can be imported
echo "Checking MCP server dependencies..."
cd ../mcp
python -c "import financial; import analytics; print('MCP servers are ready')" || {
    echo "Installing MCP dependencies..."
    pip install -r requirements.txt
}
cd ../ollama-server

# Start the server
echo "Starting Ollama MCP Financial Analysis Server..."
echo "Server will be available at: http://localhost:8000"
echo "API Documentation at: http://localhost:8000/docs"
echo ""
echo "Test the server with:"
echo "curl -X POST http://localhost:8000/analyze \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"question\": \"What are the top 5 most active stocks today?\"}'"
echo ""

python ollama-server.py