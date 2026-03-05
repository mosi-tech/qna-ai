#!/bin/bash
# Stop ChromaDB Server

echo "🛑 Stopping ChromaDB Server..."
echo ""

# Get the project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
DATA_PATH="$PROJECT_ROOT/backend/data/analysis_library_db"

# Try to get PID from .pid file first
if [ -f "$DATA_PATH/chroma.pid" ]; then
    PID=$(cat "$DATA_PATH/chroma.pid" 2>/dev/null)
    
    if [ ! -z "$PID" ] && ps -p $PID > /dev/null 2>&1; then
        echo "Found ChromaDB process from .pid file: PID $PID"
        kill $PID
        rm -f "$DATA_PATH/chroma.pid"
        
        # Wait for process to terminate
        sleep 1
        
        if ! ps -p $PID > /dev/null 2>&1; then
            echo "✅ ChromaDB server stopped"
        else
            echo "⚠️  Process still running, forcing kill..."
            kill -9 $PID
            sleep 1
            echo "✅ ChromaDB server stopped (forced)"
        fi
        exit 0
    fi
fi

# Fallback: Find ChromaDB process on port 8050
if lsof -Pi :8050 -sTCP:LISTEN -t >/dev/null 2>&1; then
    PID=$(lsof -Pi :8050 -sTCP:LISTEN -t 2>/dev/null)
    
    # Verify it's ChromaDB
    if ps -p $PID -o comm= 2>/dev/null | grep -q chroma; then
        echo "Found ChromaDB process on port 8050: PID $PID"
        kill $PID
        
        # Wait for process to terminate
        sleep 1
        
        if ! ps -p $PID > /dev/null 2>&1; then
            echo "✅ ChromaDB server stopped"
        else
            echo "⚠️  Process still running, forcing kill..."
            kill -9 $PID
            sleep 1
            echo "✅ ChromaDB server stopped (forced)"
        fi
    else
        PROC=$(ps -p $PID -o comm= 2>/dev/null)
        echo "❌ Port 8050 is in use by: $PROC (not ChromaDB)"
        exit 1
    fi
else
    echo "ℹ️  No ChromaDB server running on port 8050"
fi

echo ""
echo "✅ Done"


