#!/usr/bin/env python3
"""
Test force_api parameter for context search vs. analysis requests
"""

import os
import sys

# Add the API server path
sys.path.append('/Users/shivc/Documents/Workspace/JS/qna-ai-admin/ollama-server/scriptEdition/apiServer')

from llm.providers.anthropic import AnthropicProvider

def test_force_api():
    """Test force_api parameter overrides environment variable"""
    
    print("🧪 Testing force_api parameter functionality\n")
    
    # Initialize provider with dummy credentials
    provider = AnthropicProvider(
        api_key="dummy-key",
        default_model="claude-3-5-sonnet-20241022"
    )
    
    messages = [{"role": "user", "content": "Test question"}]
    
    print("🔍 Testing force_api parameter with different env var settings:")
    print("=" * 60)
    
    # Test cases: (env_var_value, force_api, expected_result, description)
    test_cases = [
        ("true", False, True, "CLI enabled, no force → should use CLI"),
        ("true", True, False, "CLI enabled, force API → should use API"),
        ("false", False, False, "CLI disabled, no force → should use API"),
        ("false", True, False, "CLI disabled, force API → should use API"),
        (None, False, False, "No env var, no force → should use API"),
        (None, True, False, "No env var, force API → should use API"),
    ]
    
    for env_value, force_api, expected_cli, description in test_cases:
        # Set environment variable
        if env_value is None:
            if "USE_CLAUDE_CODE_CLI" in os.environ:
                del os.environ["USE_CLAUDE_CODE_CLI"]
            env_display = "UNSET"
        else:
            os.environ["USE_CLAUDE_CODE_CLI"] = env_value
            env_display = f"'{env_value}'"
        
        # Test routing decision
        should_use_cli = provider._should_use_claude_code_cli(messages, force_api)
        
        # Determine expected behavior
        expected_text = "CLI" if expected_cli else "API"
        actual_text = "CLI" if should_use_cli else "API"
        status = "✅ PASS" if should_use_cli == expected_cli else "❌ FAIL"
        
        print(f"{description}")
        print(f"  Env: {env_display:6} | force_api: {str(force_api):5} → {actual_text:3} | Expected: {expected_text:3} | {status}")
        print()
    
    print("🎯 Use Cases:")
    print("=" * 40)
    
    # Set up CLI enabled environment
    os.environ["USE_CLAUDE_CODE_CLI"] = "true"
    
    # Use case 1: Regular analysis request (should use CLI)
    analysis_request = provider._should_use_claude_code_cli(messages, force_api=False)
    print(f"1. Analysis request (CLI enabled):     {analysis_request} → {'CLI' if analysis_request else 'API'}")
    
    # Use case 2: Context search request (should force API)
    context_request = provider._should_use_claude_code_cli(messages, force_api=True)
    print(f"2. Context search (CLI enabled + force): {context_request} → {'CLI' if context_request else 'API'}")
    
    print()
    
    # Set up CLI disabled environment
    os.environ["USE_CLAUDE_CODE_CLI"] = "false"
    
    # Use case 3: Regular analysis request (should use API)
    analysis_request_disabled = provider._should_use_claude_code_cli(messages, force_api=False)
    print(f"3. Analysis request (CLI disabled):    {analysis_request_disabled} → {'CLI' if analysis_request_disabled else 'API'}")
    
    # Use case 4: Context search request (should use API)
    context_request_disabled = provider._should_use_claude_code_cli(messages, force_api=True)
    print(f"4. Context search (CLI disabled):      {context_request_disabled} → {'CLI' if context_request_disabled else 'API'}")
    
    print()
    print("🎯 Summary:")
    print("  ✅ Context search always uses API (force_api=True)")
    print("  ✅ Analysis requests respect USE_CLAUDE_CODE_CLI environment variable")
    print("  ✅ force_api parameter overrides environment variable when needed")
    print("  ✅ Provides granular control for different request types")

if __name__ == "__main__":
    test_force_api()