#!/bin/bash

# Navigate to the parent directory (scriptEdition)
cd "$(dirname "$0")/.."

# Load environment variables from infrastructure/.env file if it exists
if [ -f "infrastructure/.env" ]; then
    echo "📁 Loading environment variables from infrastructure/.env file..."
    set -a
    source infrastructure/.env
    set +a
else
    echo "⚠️  No infrastructure/.env file found. Please create one from infrastructure/.env.example"
    echo "💡 Run: cp infrastructure/.env.example infrastructure/.env"
    echo "📝 Then edit infrastructure/.env with your actual API keys"
fi

# Set default environment variables (can be overridden by .env)
export NODE_ENV=${NODE_ENV:-development}
export PORT=${PORT:-8010}
export LLM_PROVIDER=${LLM_PROVIDER:-anthropic}
export ANTHROPIC_MODEL=${ANTHROPIC_MODEL:-claude-3-5-haiku-20241022}
export OLLAMA_BASE_URL=${OLLAMA_BASE_URL:-http://localhost:11434}
export OLLAMA_MODEL=${OLLAMA_MODEL:-qwen3:0.6b}

# Check if required API key is set based on provider
if [ "$LLM_PROVIDER" = "anthropic" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ Error: ANTHROPIC_API_KEY is not set!"
    echo "📝 Please set it in your .env file"
    exit 1
elif [ "$LLM_PROVIDER" = "openai" ] && [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY is not set!"
    echo "📝 Please set it in your .env file"
    exit 1
fi

echo "🔧 Provider: $ANTHROPIC_API_KEY"

echo "🚀 Starting Financial Analysis Server..."
echo "🔧 Provider: $LLM_PROVIDER"
if [ "$LLM_PROVIDER" = "anthropic" ]; then
    echo "🔧 Model: $ANTHROPIC_MODEL"
elif [ "$LLM_PROVIDER" = "openai" ]; then
    echo "🔧 Model: ${OPENAI_MODEL:-gpt-4-turbo-preview}"
else
    echo "🔧 Model: $OLLAMA_MODEL"
fi
echo "🔧 Port: $PORT"

# Run the server using modular architecture
cd apiServer && python server.py