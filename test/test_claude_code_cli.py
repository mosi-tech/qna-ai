#!/usr/bin/env python3
"""
Test Claude Code CLI integration
"""

import asyncio
import sys
import os

# Add the API server path
sys.path.append('/Users/shivc/Documents/Workspace/JS/qna-ai-admin/ollama-server/scriptEdition/apiServer')

from llm.providers.anthropic import AnthropicProvider

async def test_claude_code_cli():
    """Test the Claude Code CLI integration"""
    
    # Initialize provider
    provider = AnthropicProvider(
        api_key="test-key",  # Won't be used for CLI
        default_model="claude-3-5-sonnet-20241022"
    )
    
    # Set up system prompt and tools to trigger CLI path
    system_prompt = "You are a financial analysis assistant."
    tools = [
        {
            "name": "test_tool",
            "description": "Test tool",
            "input_schema": {"type": "object", "properties": {}}
        }
    ]
    
    provider.set_system_prompt(system_prompt)
    provider.set_tools(tools)
    
    # Test message
    messages = [
        {
            "role": "user",
            "content": "What's the current price of AAPL?"
        }
    ]
    
    # Check routing logic
    should_use_cli = provider._should_use_claude_code_cli(messages)
    print(f"Should use CLI: {should_use_cli}")
    print(f"Has tools: {bool(provider._raw_tools)}")
    print(f"Tools count: {len(provider._raw_tools) if provider._raw_tools else 0}")
    
    if should_use_cli:
        print("✅ Would route to Claude Code CLI")
        print("🔄 Testing CLI call...")
        
        try:
            result = await provider._call_claude_code_cli(
                model="claude-3-5-sonnet-20241022",
                messages=messages
            )
            
            if result["success"]:
                print("✅ CLI call successful")
                print(f"Response: {result}")
            else:
                print(f"❌ CLI call failed: {result['error']}")
                
        except Exception as e:
            print(f"❌ CLI test error: {e}")
    else:
        print("❌ Would NOT route to Claude Code CLI")

if __name__ == "__main__":
    asyncio.run(test_claude_code_cli())