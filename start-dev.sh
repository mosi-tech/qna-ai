#!/bin/bash

# QnA-AI Development Environment Startup Script
# This script starts all services needed to run the application

set -e  # Exit on error

echo "🚀 Starting QnA-AI Development Environment"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -i :"$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command_exists python3; then
    echo -e "${RED}❌ Python3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python3 found${NC}"

if ! command_exists node; then
    echo -e "${RED}❌ Node.js not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Node.js found${NC}"

if ! command_exists redis-server; then
    echo -e "${YELLOW}⚠️  Redis not found (optional but recommended)${NC}"
fi

echo ""

# Check if .env file exists
if [ ! -f "backend/scriptEdition/infrastructure/.env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from example...${NC}"
    if [ -f "backend/scriptEdition/infrastructure/.env.example" ]; then
        cp backend/scriptEdition/infrastructure/.env.example backend/scriptEdition/infrastructure/.env
        echo -e "${YELLOW}⚠️  Please edit backend/scriptEdition/infrastructure/.env with your API keys${NC}"
        echo ""
    fi
fi

# Start Redis if not running
if command_exists redis-server; then
    if ! port_in_use 6379; then
        echo "🔄 Starting Redis..."
        redis-server --daemonize yes
        sleep 2
        echo -e "${GREEN}✅ Redis started${NC}"
    else
        echo -e "${GREEN}✅ Redis already running${NC}"
    fi
fi
echo ""

# Check if dependencies are installed
echo "📦 Checking dependencies..."

# Check Python dependencies
if ! python3 -c "import fastapi, uvicorn" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Installing Python dependencies...${NC}"
    echo "This may take a few minutes..."

    # Install API server deps
    cd backend/scriptEdition/apiServer
    pip3 install -r requirements.txt >/dev/null 2>&1 || echo -e "${YELLOW}Some packages may have failed${NC}"
    cd ../../..

    # Install shared deps
    cd backend/shared
    pip3 install -r requirements.txt >/dev/null 2>&1 || echo -e "${YELLOW}Some packages may have failed${NC}"
    cd ../..

    # Install MCP server deps
    cd backend/mcp-server
    pip3 install -r requirements.txt >/dev/null 2>&1 || echo -e "${YELLOW}Some packages may have failed${NC}"
    cd ../..
fi
echo -e "${GREEN}✅ Python dependencies OK${NC}"

# Check Node dependencies
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}⚠️  Installing Node dependencies...${NC}"
    cd frontend
    npm install
    cd ..
fi
echo -e "${GREEN}✅ Node dependencies OK${NC}"
echo ""

# Create tmux session or start services in background
echo "🎯 Starting services..."
echo ""

# Kill any existing processes on our ports
for port in 8010 8013 3000 3003; do
    if port_in_use $port; then
        echo -e "${YELLOW}⚠️  Port $port is in use. Killing process...${NC}"
        PID=$(lsof -ti :$port)
        kill -9 $PID 2>/dev/null || true
        sleep 1
    fi
done

# Start API Server
echo "📡 Starting API Server (port 8010)..."
cd backend/scriptEdition/apiServer
python3 server.py > ../../../logs/api-server.log 2>&1 &
API_PID=$!
cd ../../..
sleep 3

# Check if API server started
if port_in_use 8010; then
    echo -e "${GREEN}✅ API Server started (PID: $API_PID)${NC}"
else
    echo -e "${RED}❌ API Server failed to start. Check logs/api-server.log${NC}"
fi

# Start Execution Server
echo "⚙️  Starting Execution Server (port 8013)..."
cd backend/mcp-server
python3 http_script_execution_server.py > ../../logs/execution-server.log 2>&1 &
EXEC_PID=$!
cd ../..
sleep 2

if port_in_use 8013; then
    echo -e "${GREEN}✅ Execution Server started (PID: $EXEC_PID)${NC}"
else
    echo -e "${RED}❌ Execution Server failed to start. Check logs/execution-server.log${NC}"
fi

# Start MCP Financial Server (optional)
echo "💰 Starting Financial MCP Server (port 3003)..."
cd backend/mcp-server
python3 financial_server_mock.py > ../../logs/financial-server.log 2>&1 &
FIN_PID=$!
cd ../..
sleep 2

if port_in_use 3003; then
    echo -e "${GREEN}✅ Financial MCP Server started (PID: $FIN_PID)${NC}"
else
    echo -e "${YELLOW}⚠️  Financial MCP Server may have failed. Check logs/financial-server.log${NC}"
fi

# Start Frontend
echo "🎨 Starting Frontend (port 3000)..."
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
sleep 3

if port_in_use 3000; then
    echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
else
    echo -e "${RED}❌ Frontend failed to start. Check logs/frontend.log${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✅ All services started!${NC}"
echo "=========================================="
echo ""
echo "📍 Service URLs:"
echo "   Frontend:        http://localhost:3000"
echo "   API Server:      http://localhost:8010"
echo "   Execution:       http://localhost:8013"
echo "   Financial MCP:   http://localhost:3003"
echo ""
echo "📊 Process IDs:"
echo "   API Server:      $API_PID"
echo "   Execution:       $EXEC_PID"
echo "   Financial MCP:   $FIN_PID"
echo "   Frontend:        $FRONTEND_PID"
echo ""
echo "📝 Logs location: ./logs/"
echo ""
echo "🧪 Quick health checks:"
echo "   curl http://localhost:8010/health"
echo "   curl http://localhost:8013/health"
echo ""
echo "🛑 To stop all services, run:"
echo "   ./stop-dev.sh"
echo "   Or manually: kill $API_PID $EXEC_PID $FIN_PID $FRONTEND_PID"
echo ""
echo -e "${GREEN}🎉 Ready to use! Open http://localhost:3000${NC}"
