#!/bin/bash

echo "🧪 Testing Tool Calling with gpt-oss:20b"
echo "=========================================="

# Test 1: Simple volatility question (should trigger validation tools)
echo ""
echo "Test 1: Portfolio volatility analysis (should use validation tools)"
echo "Expected: LLM should call validate_python_script during generation"
echo ""

curl -X POST http://localhost:8010/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is my portfolio volatility over the past 30 days?",
    "model": "gpt-oss:20b"
  }' | jq '.data.body[] | select(.key == "tool_calls_made" or .key == "tools_used" or .key == "real_time_validation")'

echo ""
echo "=========================================="
echo "Check the server logs for tool call details!"
echo "Look for:"
echo "✅ Executing MCP tool: [function_name]"
echo "✅ Tool call [function_name] executed successfully"
echo "✅ LLM made [N] tool calls during generation"