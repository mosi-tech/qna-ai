#!/bin/bash

# QnA-AI Development Environment Stop Script
# This script stops all running services

echo "🛑 Stopping QnA-AI Development Environment"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Function to check if a port is in use and kill it
kill_port() {
    local port=$1
    local service=$2

    if lsof -i :"$port" >/dev/null 2>&1; then
        PID=$(lsof -ti :$port)
        kill -9 $PID 2>/dev/null || true
        sleep 1

        if ! lsof -i :"$port" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Stopped $service (port $port)${NC}"
        else
            echo -e "${RED}❌ Failed to stop $service (port $port)${NC}"
        fi
    else
        echo "   $service not running (port $port)"
    fi
}

# Stop all services by port
kill_port 3000 "Frontend"
kill_port 8010 "API Server"
kill_port 8013 "Execution Server"
kill_port 3003 "Financial MCP"
kill_port 3004 "Analytics MCP"
kill_port 3005 "Validation MCP"

echo ""
echo "=========================================="
echo -e "${GREEN}✅ All services stopped${NC}"
echo "=========================================="
