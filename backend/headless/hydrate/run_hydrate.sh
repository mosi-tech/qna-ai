#!/bin/bash
# Run the Cache Hydration Pipeline with environment setup
# Usage: ./run.sh [options]
#   --use-planner      Use real UIPlanner (requires LLM)
#   --use-llm          Use LLM for question generation
#   --warm-cache N     Number of questions to pre-generate
#   --max-iterations N Maximum iterations
#   --target 0.95      Target hit rate

# Setup environment
eval "$(curl -sS localhost:8001/setup)"

# Run the pipeline
cd "$(dirname "$0")"
python hydrate_pipeline.py "$@"