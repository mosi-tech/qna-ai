#!/bin/bash

echo "🔍 Testing Ollama with curl commands..."
echo ""

# Test 1: Check if Ollama is running and list models
echo "1. Checking available models:"
curl -s http://localhost:11434/api/tags | jq '.'
echo ""

# Test 2: Simple generation test
echo "2. Testing simple generation:"
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-oss:latest",
    "prompt": "Say hello in exactly 3 words.",
    "stream": false,
    "options": {
      "temperature": 0.1
    }
  }' | jq '.response'
echo ""

# Test 3: JSON validation test with a sample question
echo "3. Testing validation with sample question:"
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-oss:latest",
    "prompt": "You are a financial API validator. Validate this question: \"Which watchlist tickers had the highest 3-month Sharpe ratio?\" \n\nRespond with a JSON object in this exact format:\n{\n  \"status\": \"VALID\",\n  \"original_question\": \"Which watchlist tickers had the highest 3-month Sharpe ratio?\",\n  \"validation_notes\": \"Your validation explanation here\",\n  \"required_apis\": [\"api1\", \"api2\"],\n  \"data_requirements\": [\"requirement1\", \"requirement2\"]\n}\n\nOnly respond with valid JSON, no other text.",
    "stream": false,
    "options": {
      "temperature": 0.1,
      "top_p": 0.9
    }
  }' | jq '.response'
echo ""

echo "✅ Curl tests complete!"