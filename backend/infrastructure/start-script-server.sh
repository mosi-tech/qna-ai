#!/bin/bash

echo "🚀 Starting Financial Analysis Server with PM2..."
echo "Port: 8010 (API Server) + 8013 (Execution Server)"
echo "Purpose: Generate and execute Python scripts for financial analysis"
echo ""

# Navigate to infrastructure directory
cd "$(dirname "$0")"

# Check if PM2 is installed
if ! command -v pm2 &> /dev/null; then
    echo "❌ PM2 is not installed. Installing..."
    npm install -g pm2
fi

# Check if required Python packages are installed
echo "📦 Checking requirements..."
if ! python3 -c "import fastapi, uvicorn, httpx" 2>/dev/null; then
    echo "❌ Missing required packages. Installing..."
    pip3 install -r requirements-ollama.txt
fi

# Create logs directory
mkdir -p ../apiServer/logs
mkdir -p ../executionServer/logs

# Stop existing PM2 processes if running
echo "🔄 Stopping existing servers..."
pm2 stop ollama-script-server 2>/dev/null || true
pm2 stop script-execution-server 2>/dev/null || true

# Start servers with PM2
echo "✅ Starting servers with PM2..."
pm2 start ecosystem.config.js

# Show status
echo ""
echo "📊 Server Status:"
pm2 status

echo ""
echo "📋 Useful PM2 Commands:"
echo "  pm2 logs ollama-script-server    # View script server logs"
echo "  pm2 logs script-execution-server # View execution server logs"
echo "  pm2 restart ollama-script-server # Restart script server"
echo "  pm2 monit                        # Monitor both servers"
echo "  pm2 stop all                     # Stop all servers"
echo ""
echo "🧪 Test the servers:"
echo "  curl http://localhost:8010/health"
echo "  curl http://localhost:8013/health"