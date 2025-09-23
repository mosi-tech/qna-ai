# Ollama Native MCP Integration

This setup integrates your MCP financial and analytics servers with Ollama using native HTTP connections (no FastMCP dependency) to provide AI-powered financial analysis.

## Quick Start

1. **Navigate to the ollama-server directory:**
   ```bash
   cd ollama-server
   ```

2. **Start the MCP HTTP wrapper servers (in one terminal):**
   ```bash
   ./start-mcp-wrappers.sh
   ```

3. **Start the ollama server (in another terminal):**
   ```bash
   ./start-ollama-server.sh
   ```

4. **Open the web interface:**
   ```bash
   open ollama-web-interface.html
   ```

5. **Or test via API:**
   ```bash
   python test-ollama-integration.py
   ```

## Components

### 1. MCP HTTP Wrappers (`mcp-http-wrapper.py`)
- HTTP wrapper servers that expose MCP server functionality via HTTP
- Financial server wrapper: http://localhost:8001
- Analytics server wrapper: http://localhost:8002
- No FastMCP dependency required

### 2. System Prompt (`system-prompt.txt`)
- Instructs the model to use MCP tools
- Enforces JSON output format
- Provides financial analysis guidelines

### 3. Ollama Server (`ollama-server.py`)
- FastAPI server that accepts questions via HTTP
- Connects to MCP HTTP wrapper servers to discover tools
- Uses Ollama for tool call planning and analysis
- Returns structured JSON responses

### 4. Web Interface (`ollama-web-interface.html`)
- Simple web UI to interact with the system
- Example questions for testing
- Real-time results display

## API Endpoints

### POST /analyze
Send financial questions and get structured analysis:

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the top 5 most active stocks today?"}'
```

Response format:
```json
{
  "success": true,
  "data": {
    "description": "Analysis explanation",
    "body": [
      {
        "key": "metric_name",
        "value": "calculated_value",
        "description": "What this means"
      }
    ],
    "metadata": {
      "timestamp": "2024-...",
      "data_sources": ["alpaca", "eodhd"],
      "calculation_methods": ["technical_analysis"]
    }
  },
  "timestamp": "2024-..."
}
```

### GET /health
Health check endpoint

### GET /models
List available Ollama models

## Testing

1. **Test MCP servers independently:**
   ```bash
   cd mcp
   python financial_server.py --test
   python analytics_server.py --test
   ```

2. **Test the integration:**
   ```bash
   python test-ollama-integration.py
   ```

## Example Questions

- "What are the top 5 most active stocks today?"
- "Calculate the 20-day moving average for AAPL"
- "Show me risk metrics for a portfolio with 60% stocks and 40% bonds"
- "What are the top gainers in the market today?"
- "Calculate RSI for TSLA over the last 14 days"

## Troubleshooting

1. **Server won't start:**
   - Check if Ollama is installed: `ollama --version`
   - Verify MCP dependencies: `pip install -r mcp/requirements.txt`

2. **MCP HTTP wrappers not working:**
   - Make sure to start the wrappers first: `./start-mcp-wrappers.sh`
   - Check wrapper server logs for errors
   - Verify your API keys in environment variables

3. **Slow responses:**
   - Normal for first request (model loading)
   - Subsequent requests should be faster

4. **JSON parsing errors:**
   - The system will fall back to raw text responses
   - Check system prompt formatting

## Architecture

```
User Question → FastAPI Server → Ollama + Native MCP HTTP APIs → Structured JSON Response
                    ↓
            [Financial Server (HTTP): Alpaca, EODHD APIs]
                    ↓  
            [Analytics Server (HTTP): Technical indicators, Portfolio metrics]
                    ↓
            [Formatted Response: Retail-friendly explanations]
```

The system combines real financial data with AI analysis using native HTTP connections to MCP servers (no FastMCP dependency), providing actionable insights in a structured format perfect for your QnA application.