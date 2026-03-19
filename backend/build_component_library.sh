#!/bin/bash
# Component Library Builder Shell Script
# Usage: ./build_component_library.sh [start_at]

# Setup environment
eval "$(curl -sS localhost:8001/setup)"

# Configuration
PYTHON_SCRIPT="python3 headless/agents/component_library_builder.py"
OUTPUT_FILE="headless/output/component_library.json"
LOG_FILE="component_builder.log"

# Check for start_at argument
if [ -n "$1" ]; then
    START_AT="--start-at $1"
    echo "Resuming from question $1"
else
    START_AT=""
    echo "Starting from beginning"
fi

# Run the component library builder
echo "Starting component library builder..."
echo "Output: $OUTPUT_FILE"
echo "Logs: $LOG_FILE"
echo ""

nohup $PYTHON_SCRIPT --resume $START_AT > $LOG_FILE 2>&1 &
PID=$!

echo "Started with PID: $PID"
echo "Monitor: tail -f $LOG_FILE"
echo "Progress: cat $OUTPUT_FILE | python3 -c \"import json; print(len(json.load(sys.stdin)))\""
echo ""
echo "To stop: kill $PID"