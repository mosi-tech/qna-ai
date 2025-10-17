#!/usr/bin/env python3
"""
Test the defensive programming validation
"""

import sys
import os
sys.path.append('/Users/shivc/Documents/Workspace/JS/qna-ai-admin/mcp-server')

from shared_script_executor import check_defensive_programming

# Test scripts with forbidden patterns
test_scripts = {
    "assert_violation": '''
def test_function():
    assert symbol in bars, f"No data returned for {symbol}"
    return bars[symbol]
''',
    
    "get_with_default": '''
def test_function():
    data = bars.get(symbol, {})
    return data
''',
    
    "defensive_result_check": '''
def test_function():
    if result and result.get('success'):
        return result['data']
    else:
        return None
''',
    
    "correct_pattern": '''
def test_function():
    data = bars[symbol]  # Direct access - will KeyError if missing
    return data['close']  # Direct access - will KeyError if missing
'''
}

def test_defensive_validation():
    print("Testing defensive programming validation...\n")
    
    for test_name, script_content in test_scripts.items():
        print(f"Testing: {test_name}")
        result = check_defensive_programming(script_content)
        
        if result["valid"]:
            print("✅ PASSED - No defensive programming detected")
        else:
            print(f"❌ FAILED - {result['error']}")
            print(f"   Line {result['line_number']}: {result['line']}")
            print(f"   Not allowed: {result['not_allowed']}")
            print(f"   Use instead: {result['use_instead']}")
        
        print("-" * 50)

if __name__ == "__main__":
    test_defensive_validation()