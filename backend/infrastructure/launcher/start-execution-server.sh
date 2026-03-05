#!/bin/bash
if [ "$TRACK_CALLS" = "true" ]; then
  eval "$(curl -sS localhost:8001/setup 2>/dev/null)" || true
fi

echo "🚀 Starting HTTP Script Execution Server..."
echo "Port: 8013"
echo "Purpose: Execute validated Python scripts via HTTP"
echo ""

# Check if required Python packages are installed
echo "📦 Checking requirements..."
if ! python3 -c "import fastapi, uvicorn, pandas, numpy" 2>/dev/null; then
    echo "❌ Missing required packages. Installing..."
    pip3 install -r requirements.txt
fi

echo "✅ Starting HTTP Script Execution Server..."
python3 http_script_execution_server.py