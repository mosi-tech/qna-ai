#!/usr/bin/env python3
"""
Test environment variable control for Claude Code CLI
"""

import asyncio
import sys
import os

# Add the API server path
sys.path.append('/Users/shivc/Documents/Workspace/JS/qna-ai-admin/ollama-server/scriptEdition/apiServer')

from llm.providers.anthropic import AnthropicProvider

async def test_env_var_control():
    """Test environment variable control for Claude Code CLI routing"""
    
    # Initialize provider
    provider = AnthropicProvider(
        api_key="test-key",
        default_model="claude-3-5-sonnet-20241022"
    )
    
    # Test message
    messages = [
        {
            "role": "user",
            "content": "What's the current price of AAPL?"
        }
    ]
    
    print("🧪 Testing environment variable control for Claude Code CLI\n")
    
    # Test 1: No environment variable set (default false)
    print("Test 1: No USE_CLAUDE_CODE_CLI environment variable")
    if "USE_CLAUDE_CODE_CLI" in os.environ:
        del os.environ["USE_CLAUDE_CODE_CLI"]
    
    should_use_cli = provider._should_use_claude_code_cli(messages)
    print(f"  Should use CLI: {should_use_cli}")
    print(f"  Expected: False")
    print(f"  ✅ PASS" if should_use_cli == False else f"  ❌ FAIL")
    print()
    
    # Test 2: Environment variable set to false
    print("Test 2: USE_CLAUDE_CODE_CLI=false")
    os.environ["USE_CLAUDE_CODE_CLI"] = "false"
    
    should_use_cli = provider._should_use_claude_code_cli(messages)
    print(f"  Should use CLI: {should_use_cli}")
    print(f"  Expected: False")
    print(f"  ✅ PASS" if should_use_cli == False else f"  ❌ FAIL")
    print()
    
    # Test 3: Environment variable set to true
    print("Test 3: USE_CLAUDE_CODE_CLI=true")
    os.environ["USE_CLAUDE_CODE_CLI"] = "true"
    
    should_use_cli = provider._should_use_claude_code_cli(messages)
    print(f"  Should use CLI: {should_use_cli}")
    print(f"  Expected: True")
    print(f"  ✅ PASS" if should_use_cli == True else f"  ❌ FAIL")
    print()
    
    # Test 4: Environment variable set to True (uppercase)
    print("Test 4: USE_CLAUDE_CODE_CLI=True")
    os.environ["USE_CLAUDE_CODE_CLI"] = "True"
    
    should_use_cli = provider._should_use_claude_code_cli(messages)
    print(f"  Should use CLI: {should_use_cli}")
    print(f"  Expected: True")
    print(f"  ✅ PASS" if should_use_cli == True else f"  ❌ FAIL")
    print()
    
    # Test 5: Environment variable set to invalid value
    print("Test 5: USE_CLAUDE_CODE_CLI=invalid")
    os.environ["USE_CLAUDE_CODE_CLI"] = "invalid"
    
    should_use_cli = provider._should_use_claude_code_cli(messages)
    print(f"  Should use CLI: {should_use_cli}")
    print(f"  Expected: False")
    print(f"  ✅ PASS" if should_use_cli == False else f"  ❌ FAIL")
    print()
    
    # Test 6: With tools present - should still respect env var
    print("Test 6: With tools present but USE_CLAUDE_CODE_CLI=false")
    os.environ["USE_CLAUDE_CODE_CLI"] = "false"
    
    # Set some tools
    provider.set_tools([
        {
            "type": "function",
            "function": {
                "name": "test_tool",
                "description": "Test tool",
                "parameters": {"type": "object", "properties": {}}
            }
        }
    ])
    
    should_use_cli = provider._should_use_claude_code_cli(messages)
    print(f"  Should use CLI: {should_use_cli}")
    print(f"  Has tools: {bool(provider._raw_tools)}")
    print(f"  Expected: False (env var overrides tool presence)")
    print(f"  ✅ PASS" if should_use_cli == False else f"  ❌ FAIL")
    print()
    
    # Test 7: With tools present and env var true
    print("Test 7: With tools present and USE_CLAUDE_CODE_CLI=true")
    os.environ["USE_CLAUDE_CODE_CLI"] = "true"
    
    should_use_cli = provider._should_use_claude_code_cli(messages)
    print(f"  Should use CLI: {should_use_cli}")
    print(f"  Has tools: {bool(provider._raw_tools)}")
    print(f"  Expected: True")
    print(f"  ✅ PASS" if should_use_cli == True else f"  ❌ FAIL")
    print()
    
    print("🎯 Environment variable control test complete!")

if __name__ == "__main__":
    asyncio.run(test_env_var_control())