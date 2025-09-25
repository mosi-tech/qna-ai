#!/usr/bin/env python3
"""
Debug what parameters the MCP server actually receives
"""

import json

# Create a test MCP call to see exactly what gets passed
test_cases = [
    {
        "name": "working_case", 
        "params": {"symbols": "AAPL"}
    },
    {
        "name": "failing_case",
        "params": {"symbols": "AAPL", "timeframe": "1Day", "start": "2023-01-01", "end": "2024-12-20"}
    }
]

print("Testing parameter serialization that MCP server would receive...")

for test in test_cases:
    print(f"\n{test['name']}:")
    print(f"Parameters: {test['params']}")
    
    # This is what gets passed to function(**arguments) in the MCP server
    try:
        # Simulate what MCP server does: function(**arguments)
        print(f"Unpacked: **{test['params']}")
        
        # Check JSON serialization (MCP uses JSON)
        json_params = json.dumps(test['params'])
        json_back = json.loads(json_params)
        print(f"JSON round-trip: {json_back}")
        
        # Check if there are any type issues
        for key, value in test['params'].items():
            print(f"  {key}: {type(value).__name__} = {repr(value)}")
            
    except Exception as e:
        print(f"❌ Error in parameter handling: {e}")

print("\nNext: Let's check the exact MCP server logs...")