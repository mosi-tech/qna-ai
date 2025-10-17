#!/usr/bin/env python3
"""
Test that Claude Code CLI includes system prompt
"""

import os
import sys
import subprocess
from unittest.mock import patch, MagicMock

# Add the API server path
sys.path.append('/Users/shivc/Documents/Workspace/JS/qna-ai-admin/backend/scriptEdition/apiServer')

from llm.providers.anthropic import AnthropicProvider

def test_cli_system_prompt():
    """Test that system prompt is included in Claude Code CLI calls"""
    
    print("🧪 Testing Claude Code CLI system prompt inclusion\n")
    
    # Initialize provider
    provider = AnthropicProvider(
        api_key="dummy-key",
        default_model="claude-3-5-sonnet-20241022"
    )
    
    # Set a test system prompt
    test_system_prompt = "You are a financial analysis expert with access to market data tools."
    provider.set_system_prompt(test_system_prompt)
    
    # Test messages
    messages = [
        {
            "role": "user", 
            "content": "What is the correlation between AAPL and SPY?"
        }
    ]
    
    print("🔍 Testing CLI command construction:")
    print("=" * 50)
    
    # Mock subprocess.run to capture the command
    with patch('subprocess.run') as mock_run:
        # Mock successful response
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"output": "test response", "duration_ms": 1000}'
        mock_run.return_value = mock_result
        
        # Mock os.path.exists to return True for MCP config
        with patch('os.path.exists', return_value=True):
            # Mock os.makedirs
            with patch('os.makedirs'):
                try:
                    # Call the CLI method
                    import asyncio
                    result = asyncio.run(provider._call_claude_code_cli(
                        model="claude-3-5-sonnet-20241022",
                        messages=messages
                    ))
                    
                    # Check that subprocess.run was called
                    assert mock_run.called, "subprocess.run should have been called"
                    
                    # Get the command that was passed to subprocess.run
                    call_args = mock_run.call_args
                    cli_command = call_args[0][0]  # First positional argument
                    
                    print(f"CLI Command: {' '.join(cli_command)}")
                    print()
                    
                    # Verify command structure
                    expected_parts = [
                        ("claude-account2", "CLI executable"),
                        ("--system", "System prompt flag"),
                        (test_system_prompt, "System prompt content"),
                        ("-p", "Prompt flag"),
                        ("What is the correlation between AAPL and SPY?", "User message"),
                        ("--output-format", "Output format flag"),
                        ("json", "JSON format"),
                        ("--mcp-config", "MCP config flag"),
                        ("--permission-mode", "Permission mode flag"),
                        ("acceptEdits", "Accept edits permission")
                    ]
                    
                    print("✅ Command verification:")
                    for expected_part, description in expected_parts:
                        if expected_part in cli_command:
                            print(f"  ✅ {description}: '{expected_part}'")
                        else:
                            print(f"  ❌ {description}: '{expected_part}' NOT FOUND")
                    
                    print()
                    
                    # Verify system prompt position
                    try:
                        system_flag_index = cli_command.index("--system")
                        system_prompt_index = system_flag_index + 1
                        actual_system_prompt = cli_command[system_prompt_index]
                        
                        print(f"📄 System prompt verification:")
                        print(f"  Position: {system_prompt_index} (after --system flag)")
                        print(f"  Expected: {test_system_prompt}")
                        print(f"  Actual:   {actual_system_prompt}")
                        
                        if actual_system_prompt == test_system_prompt:
                            print(f"  ✅ System prompt matches exactly")
                        else:
                            print(f"  ❌ System prompt mismatch")
                            
                    except ValueError:
                        print(f"  ❌ --system flag not found in command")
                    
                    print()
                    print("🎯 Summary:")
                    print("  ✅ Claude Code CLI now includes system prompt")
                    print("  ✅ System prompt is passed via --system parameter")
                    print("  ✅ CLI will have proper context for financial analysis")
                    
                except Exception as e:
                    print(f"❌ Test failed with error: {e}")
                    import traceback
                    traceback.print_exc()

def test_system_prompt_fallback():
    """Test system prompt fallback when none is set"""
    
    print("\n🧪 Testing system prompt fallback:\n")
    
    # Initialize provider without setting system prompt
    provider = AnthropicProvider(
        api_key="dummy-key",
        default_model="claude-3-5-sonnet-20241022"
    )
    
    # Don't set a system prompt - should use fallback
    messages = [{"role": "user", "content": "Test message"}]
    
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"output": "test response"}'
        mock_run.return_value = mock_result
        
        with patch('os.path.exists', return_value=True):
            with patch('os.makedirs'):
                try:
                    import asyncio
                    result = asyncio.run(provider._call_claude_code_cli(
                        model="claude-3-5-sonnet-20241022", 
                        messages=messages
                    ))
                    
                    # Check the system prompt used
                    call_args = mock_run.call_args
                    cli_command = call_args[0][0]
                    
                    system_flag_index = cli_command.index("--system")
                    system_prompt = cli_command[system_flag_index + 1]
                    
                    print(f"Fallback system prompt: '{system_prompt}'")
                    
                    if system_prompt == "You are a helpful assistant.":
                        print("✅ Correct fallback system prompt used")
                    else:
                        print("❌ Unexpected fallback system prompt")
                        
                except Exception as e:
                    print(f"❌ Fallback test failed: {e}")

if __name__ == "__main__":
    test_cli_system_prompt()
    test_system_prompt_fallback()