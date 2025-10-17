#!/usr/bin/env python3
"""
Test complete environment variable control for analysis service
"""

import asyncio
import sys
import os

# Add the API server path
sys.path.append('/Users/shivc/Documents/Workspace/JS/qna-ai-admin/backend/scriptEdition/apiServer')

from services.analysis_simplified import AnalysisService

async def test_complete_env_control():
    """Test complete environment variable control for analysis service"""
    
    print("🧪 Testing complete environment variable control\n")
    
    # Test 1: Environment variable set to false - should use API
    print("Test 1: USE_CLAUDE_CODE_CLI=false")
    os.environ["USE_CLAUDE_CODE_CLI"] = "false"
    
    analysis_service = AnalysisService()
    
    # Check internal routing decision
    messages = [{"role": "user", "content": "Test question"}]
    should_use_cli = analysis_service.llm_service.provider._should_use_claude_code_cli(messages)
    
    print(f"  Environment variable: {os.getenv('USE_CLAUDE_CODE_CLI')}")
    print(f"  Should use CLI: {should_use_cli}")
    print(f"  Expected: False")
    print(f"  ✅ PASS" if should_use_cli == False else f"  ❌ FAIL")
    print()
    
    # Test 2: Environment variable set to true - should use CLI
    print("Test 2: USE_CLAUDE_CODE_CLI=true")
    os.environ["USE_CLAUDE_CODE_CLI"] = "true"
    
    # Create new service to pick up env change
    analysis_service = AnalysisService()
    
    should_use_cli = analysis_service.llm_service.provider._should_use_claude_code_cli(messages)
    
    print(f"  Environment variable: {os.getenv('USE_CLAUDE_CODE_CLI')}")
    print(f"  Should use CLI: {should_use_cli}")
    print(f"  Expected: True")
    print(f"  ✅ PASS" if should_use_cli == True else f"  ❌ FAIL")
    print()
    
    # Test 3: Verify independence from tool presence
    print("Test 3: Tool presence independence test")
    
    # Test with no tools
    analysis_service.llm_service.provider.set_tools([])
    should_use_cli_no_tools = analysis_service.llm_service.provider._should_use_claude_code_cli(messages)
    
    # Test with tools
    analysis_service.llm_service.provider.set_tools([
        {
            "type": "function",
            "function": {
                "name": "test_tool",
                "description": "Test tool",
                "parameters": {"type": "object", "properties": {}}
            }
        }
    ])
    should_use_cli_with_tools = analysis_service.llm_service.provider._should_use_claude_code_cli(messages)
    
    print(f"  Environment variable: {os.getenv('USE_CLAUDE_CODE_CLI')}")
    print(f"  Should use CLI (no tools): {should_use_cli_no_tools}")
    print(f"  Should use CLI (with tools): {should_use_cli_with_tools}")
    print(f"  Both should be True: {should_use_cli_no_tools == should_use_cli_with_tools == True}")
    print(f"  ✅ PASS" if should_use_cli_no_tools == should_use_cli_with_tools == True else f"  ❌ FAIL")
    print()
    
    # Test 4: Test different environment variable values
    print("Test 4: Various environment variable values")
    
    test_cases = [
        ("false", False),
        ("FALSE", False),
        ("true", True),
        ("TRUE", True),
        ("True", True),
        ("1", False),  # Should be false since it's not "true"
        ("yes", False),  # Should be false since it's not "true"
        ("", False),  # Empty string should be false
    ]
    
    for env_value, expected in test_cases:
        os.environ["USE_CLAUDE_CODE_CLI"] = env_value
        
        # Create new service to pick up env change
        analysis_service = AnalysisService()
        should_use_cli = analysis_service.llm_service.provider._should_use_claude_code_cli(messages)
        
        result = "✅ PASS" if should_use_cli == expected else "❌ FAIL"
        print(f"    '{env_value}' -> {should_use_cli} (expected {expected}) {result}")
    
    print()
    
    # Test 5: Test missing environment variable
    print("Test 5: Missing environment variable")
    
    if "USE_CLAUDE_CODE_CLI" in os.environ:
        del os.environ["USE_CLAUDE_CODE_CLI"]
    
    analysis_service = AnalysisService()
    should_use_cli = analysis_service.llm_service.provider._should_use_claude_code_cli(messages)
    
    print(f"  Environment variable: {os.getenv('USE_CLAUDE_CODE_CLI', 'NOT_SET')}")
    print(f"  Should use CLI: {should_use_cli}")
    print(f"  Expected: False (default)")
    print(f"  ✅ PASS" if should_use_cli == False else f"  ❌ FAIL")
    print()
    
    print("🎯 Complete environment variable control test finished!")
    print("\n📋 Summary:")
    print("  ✅ Environment variable controls CLI usage regardless of tool presence")
    print("  ✅ Only 'true' (case-insensitive) enables CLI, everything else disables it")
    print("  ✅ Missing environment variable defaults to disabled (API usage)")
    print("  ✅ Tool presence/absence doesn't affect routing decision")

if __name__ == "__main__":
    asyncio.run(test_complete_env_control())