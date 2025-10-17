#!/usr/bin/env python3
"""
Test Claude Code CLI with a financial question
"""

import asyncio
import sys
import os

# Add the API server path
sys.path.append('/Users/shivc/Documents/Workspace/JS/qna-ai-admin/backend/scriptEdition/apiServer')

from llm.providers.anthropic import AnthropicProvider

async def test_financial_question():
    """Test Claude Code CLI with a financial analysis question"""
    
    # Initialize provider
    provider = AnthropicProvider(
        api_key="test-key",  # Won't be used for CLI
        default_model="claude-3-5-sonnet-20241022"
    )
    
    # Set up system prompt and tools to trigger CLI path
    system_prompt = """You are a financial analysis assistant with access to market data and analytics tools."""
    
    # Mock some tools to trigger CLI usage
    tools = [
        {
            "name": "alpaca_market_stocks_bars",
            "description": "Get historical stock price data",
            "input_schema": {"type": "object", "properties": {"symbols": {"type": "array"}}}
        }
    ]
    
    provider.set_system_prompt(system_prompt)
    provider.set_tools(tools)
    
    # Financial analysis question
    messages = [
        {
            "role": "user",
            "content": "Can you analyze the correlation between AAPL and SPY over the last 30 days? I want to understand how Apple moves relative to the market."
        }
    ]
    
    print("🔄 Testing financial analysis with Claude Code CLI...")
    
    try:
        result = await provider._call_claude_code_cli(
            model="claude-3-5-sonnet-20241022",
            messages=messages
        )
        
        if result["success"]:
            print("✅ Financial analysis CLI call successful")
            
            # Extract the response
            data = result["data"]
            claude_result = data.get("claude_code_result", {})
            
            print(f"\n📊 Analysis Result:")
            print(f"Duration: {claude_result.get('duration_ms', 0)}ms")
            print(f"Turns: {claude_result.get('num_turns', 0)}")
            print(f"Cost: ${claude_result.get('total_cost_usd', 0)}")
            
            # Get the actual response text
            response_text = claude_result.get("result", "")
            print(f"\n💬 Response:")
            print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
            
        else:
            print(f"❌ Financial analysis CLI call failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Financial analysis test error: {e}")

if __name__ == "__main__":
    asyncio.run(test_financial_question())