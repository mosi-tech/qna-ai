#!/bin/bash
# Start Analysis Worker with .env configuration

# Change to launcher directory to ensure .env is found
cd "$(dirname "$0")"

echo "🚀 Starting Analysis Worker..."
echo "📄 Loading configuration from .env file"

# Debug: Show which python we're using
echo "🐍 Using Python: $(which python3)"
echo "🐍 Python version: $(python3 --version)"

# Run the Python worker (it will auto-load .env from this directory)
python3 ../queue_worker.py --type analysis "$@"