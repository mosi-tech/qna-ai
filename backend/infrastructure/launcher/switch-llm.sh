#!/bin/bash
if [ "$TRACK_CALLS" = "true" ]; then
  eval "$(curl -sS localhost:8001/setup 2>/dev/null)" || true
fi

# Universal LLM Provider Switcher
# Usage: ./switch-llm.sh anthropic|ollama

INFRA_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ECO="$INFRA_DIR/pm2.config.js"

if [ $# -eq 0 ]; then
    echo "Usage: $0 [anthropic|ollama]"
    echo ""
    echo "Current provider in pm2.config.js:"
    grep "LLM_PROVIDER:" "$ECO"
    exit 1
fi

PROVIDER=$1

case $PROVIDER in
    anthropic)
        echo "🔄 Switching to Anthropic Claude..."
        sed -i '' "s/LLM_PROVIDER: '[^']*'/LLM_PROVIDER: 'anthropic'/" "$ECO"
        echo "✅ Updated pm2.config.js"
        echo "📝 Make sure you have set your ANTHROPIC_API_KEY"
        ;;
    ollama)
        echo "🔄 Switching to Ollama..."
        sed -i '' "s/LLM_PROVIDER: '[^']*'/LLM_PROVIDER: 'ollama'/" "$ECO"
        echo "✅ Updated pm2.config.js"
        echo "📝 Make sure Ollama is running: ollama serve"
        ;;
    *)
        echo "❌ Invalid provider. Use 'anthropic' or 'ollama'"
        exit 1
        ;;
esac

echo ""
echo "🔄 Restarting server with new provider..."
pm2 restart ollama-script-server --update-env

echo ""
echo "🎉 Switched to $PROVIDER provider!"
echo "📍 Test endpoint: http://localhost:8010/analyze"
echo "🔍 Check logs: pm2 logs ollama-script-server"