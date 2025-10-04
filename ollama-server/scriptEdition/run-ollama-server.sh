#!/bin/bash

# Navigate to the script directory
cd "$(dirname "$0")"

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    echo "📁 Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
else
    echo "⚠️  No .env file found. Please create one from .env.example"
    echo "💡 Run: cp .env.example .env"
    echo "📝 Then edit .env with your actual API keys"
fi

# Set default environment variables (can be overridden by .env)
export NODE_ENV=${NODE_ENV:-development}
export PORT=${PORT:-8010}
export LLM_PROVIDER=${LLM_PROVIDER:-anthropic}
export ANTHROPIC_MODEL=${ANTHROPIC_MODEL:-claude-3-5-haiku-20241022}
export OLLAMA_BASE_URL=${OLLAMA_BASE_URL:-http://localhost:11434}
export OLLAMA_MODEL=${OLLAMA_MODEL:-qwen3:0.6b}

# Check if required API key is set when using Anthropic
if [ "$LLM_PROVIDER" = "anthropic" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ Error: ANTHROPIC_API_KEY is not set!"
    echo "📝 Please set it in your .env file"
    exit 1
fi

echo "🚀 Starting Financial Analysis Server..."
echo "🔧 Provider: $LLM_PROVIDER"
echo "🔧 Model: ${ANTHROPIC_MODEL:-$OLLAMA_MODEL}"
echo "🔧 Port: $PORT"

# Run the server
python3 ollama-script-server.py