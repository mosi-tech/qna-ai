#!/bin/bash
# Start all MCP servers as persistent HTTP/SSE processes
#
# Usage:
#   ./start_servers.sh          # start all three servers
#   ./start_servers.sh stop     # kill all three servers
#
# Ports:
#   Financial (mock): 8101
#   Analytics:        8102
#   Validation:       8103
#
# Add to your .env:
#   FINANCIAL_MCP_URL=http://localhost:8101/sse
#   ANALYTICS_MCP_URL=http://localhost:8102/sse
#   VALIDATION_MCP_URL=http://localhost:8103/sse

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LOGS_DIR="$SCRIPT_DIR/logs"
PIDS_DIR="$SCRIPT_DIR/pids"

mkdir -p "$LOGS_DIR" "$PIDS_DIR"

start_server() {
    local name=$1
    local script=$2
    local port=$3
    local pid_file="$PIDS_DIR/${name}.pid"

    if [ -f "$pid_file" ] && kill -0 "$(cat "$pid_file")" 2>/dev/null; then
        echo "⚡ $name already running (pid $(cat "$pid_file"))"
        return
    fi

    PYTHONPATH="$BACKEND_DIR" python3 "$SCRIPT_DIR/$script" --port "$port" \
        > "$LOGS_DIR/${name}.log" 2>&1 &
    echo $! > "$pid_file"
    echo "✅ $name started on port $port (pid $!)"
}

stop_server() {
    local name=$1
    local pid_file="$PIDS_DIR/${name}.pid"
    if [ -f "$pid_file" ]; then
        local pid
        pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            echo "🛑 $name stopped (pid $pid)"
        fi
        rm -f "$pid_file"
    else
        echo "⚠️  $name not running"
    fi
}

case "${1:-start}" in
    stop)
        stop_server "financial"
        stop_server "analytics"
        stop_server "validation"
        ;;
    restart)
        stop_server "financial"
        stop_server "analytics"
        stop_server "validation"
        sleep 1
        start_server "financial"  "financial_server_mock.py"        8101
        start_server "analytics"  "analytics_server.py"             8102
        start_server "validation" "mcp_script_validation_server.py" 8103
        ;;
    *)
        start_server "financial"  "financial_server_mock.py"        8101
        start_server "analytics"  "analytics_server.py"             8102
        start_server "validation" "mcp_script_validation_server.py" 8103
        echo ""
        echo "Add to your .env:"
        echo "  FINANCIAL_MCP_URL=http://localhost:8101/sse"
        echo "  ANALYTICS_MCP_URL=http://localhost:8102/sse"
        echo "  VALIDATION_MCP_URL=http://localhost:8103/sse"
        ;;
esac
