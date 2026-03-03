#!/bin/bash

echo "🔄 Restarting Ollama Script Servers..."

# Restart both servers
pm2 restart ollama-script-server
pm2 restart script-execution-server

echo "✅ Servers restarted!"
echo ""

# Show status
pm2 status

echo ""
echo "🧪 Quick Test:"
echo "  curl http://localhost:8010/health"
echo "  curl http://localhost:8013/health"