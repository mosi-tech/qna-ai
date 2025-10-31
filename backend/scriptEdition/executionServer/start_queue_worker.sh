#!/bin/bash
"""
Start Queue Worker Script

Starts the MongoDB queue worker with environment configuration.
"""

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    echo "📝 Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
else
    echo "ℹ️  No .env file found, using system environment variables"
fi

# Set default environment variables if not already set
export MONGO_URL=${MONGO_URL:-"mongodb://localhost:27017"}
export MONGO_DB_NAME=${MONGO_DB_NAME:-"qna_ai_admin"}

# Default worker configuration
WORKER_ID=${WORKER_ID:-"worker_$(hostname)_$$"}
POLL_INTERVAL=${POLL_INTERVAL:-5}
MAX_CONCURRENT=${MAX_CONCURRENT:-3}
LOG_LEVEL=${LOG_LEVEL:-"INFO"}

echo "🚀 Starting Queue Worker with configuration:"
echo "   Worker ID: $WORKER_ID"
echo "   MongoDB URL: $MONGO_URL"
echo "   Database: $MONGO_DB_NAME"
echo "   Poll Interval: $POLL_INTERVAL seconds"
echo "   Max Concurrent: $MAX_CONCURRENT"
echo "   Log Level: $LOG_LEVEL"
echo ""

# Start the worker
python3 queue_worker.py \
    --worker-id "$WORKER_ID" \
    --poll-interval "$POLL_INTERVAL" \
    --max-concurrent "$MAX_CONCURRENT" \
    --log-level "$LOG_LEVEL"