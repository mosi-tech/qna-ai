#!/bin/bash

# Start ChromaDB Server with Persistent Data
# This script starts ChromaDB with data persisted to backend/data/analysis_library_db

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DATA_PATH="$PROJECT_ROOT/backend/data/analysis_library_db"

echo "🚀 Starting ChromaDB Server"
echo "=================================================="
echo "Data Path: $DATA_PATH"
echo "Port: 8050"
echo ""

# Create data directory if it doesn't exist
echo "📁 Creating data directory..."
mkdir -p "$DATA_PATH"
echo "✅ Data directory ready: $DATA_PATH"

# Check if chroma command is available
echo ""
echo "🔍 Checking if ChromaDB is installed..."
if ! command -v chroma &> /dev/null; then
    echo "❌ ChromaDB CLI is not installed"
    echo ""
    echo "📦 Install with: pip install chromadb"
    exit 1
fi

echo "✅ ChromaDB is installed"

# Get version
CHROMA_VERSION=$(chroma --version 2>/dev/null || echo "unknown")
echo "   Version: $CHROMA_VERSION"

# Check if server is already running on port 8050
echo ""
echo "🔍 Checking if port 8050 is already in use..."
if lsof -Pi :8050 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port 8050 is already in use"
    PID=$(lsof -Pi :8050 -sTCP:LISTEN -t 2>/dev/null)
    echo "   Process ID: $PID"
    
    # Check if it's actually ChromaDB
    if ps -p $PID -o comm= 2>/dev/null | grep -q chroma; then
        echo "✅ ChromaDB is already running"
        echo ""
        echo "✅ Access at: http://localhost:8050"
        exit 0
    fi
fi

# Start ChromaDB server with persistent data path
echo ""
echo "🚀 Starting ChromaDB server..."

# Run in background and capture PID
nohup chroma run --path "$DATA_PATH" --port 8050 > "$DATA_PATH/chroma.log" 2>&1 &
CHROMA_PID=$!

# Save PID to file for later reference
echo $CHROMA_PID > "$DATA_PATH/chroma.pid"

echo "   Process ID: $CHROMA_PID"
echo "   Logs: $DATA_PATH/chroma.log"

# Wait for server to be ready
echo "⏳ Waiting for ChromaDB to be ready..."
sleep 3

# Test the connection
echo ""
echo "🧪 Testing connection..."
for i in {1..10}; do
    if curl -s http://localhost:8050/api/v1/heartbeat > /dev/null 2>&1; then
        echo "✅ ChromaDB is responding on http://localhost:8050"
        break
    fi
    
    if [ $i -lt 10 ]; then
        echo "   Attempt $i/10... waiting..."
        sleep 1
    else
        echo "⚠️  Could not verify connection after 10 attempts"
    fi
done

echo ""
echo "=================================================="
echo "✅ ChromaDB Server is running (PID: $CHROMA_PID)"
echo ""
echo "📊 Data Location: $DATA_PATH"
echo "🌐 Access at: http://localhost:8050"
echo ""
echo "📋 Useful commands:"
echo "   Stop server:  kill $CHROMA_PID"
echo "   Check data:   ls -la $DATA_PATH"
echo "   Remove data:  rm -rf $DATA_PATH"
echo ""
echo "💡 To restart, use: bash $(basename $0)"
echo ""
