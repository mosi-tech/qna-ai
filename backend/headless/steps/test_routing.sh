#!/bin/bash
# Run question routing test with LLM classification

# Load environment from localhost:8001/setup
eval "$(curl -sS localhost:8001/setup)"

# Load local test env overrides
if [ -f "$(dirname "$0")/.env.test_routing" ]; then
    export $(grep -v '^#' "$(dirname "$0")/.env.test_routing" | xargs)
fi

# Change to script directory
cd "$(dirname "$0")"

# Run the test
# Pass through any command-line arguments
python test_routing.py "$@"