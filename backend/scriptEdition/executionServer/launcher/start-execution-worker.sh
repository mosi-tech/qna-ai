#!/bin/bash
# Start Execution Worker with .env configuration

# Change to launcher directory to ensure .env is found
cd "$(dirname "$0")"

echo "🚀 Starting Execution Worker..."
echo "📄 Loading configuration from .env file"

# Run the Python worker (it will auto-load .env from this directory)
python3 ../queue_worker.py --type execution "$@"