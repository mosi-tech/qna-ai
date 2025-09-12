#!/usr/bin/env python3
"""
Integration wrapper for calling analytics functions from workflows.
This provides a simple command-line interface for the modular analytics system.
"""

import sys
import json
import argparse
from analytics.main import AnalyticsEngine


def main():
    """Main entry point for workflow integration."""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python integration_wrapper.py <function_name> [json_args]"}))
        sys.exit(1)
    
    function_name = sys.argv[1]
    
    # Special commands
    if function_name == "--list":
        engine = AnalyticsEngine()
        functions = engine.list_functions()
        print(json.dumps(functions, indent=2))
        return
    
    # Parse JSON arguments if provided
    args = {}
    if len(sys.argv) > 2:
        try:
            args = json.loads(sys.argv[2])
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Invalid JSON arguments: {str(e)}"}))
            sys.exit(1)
    
    # Execute function
    engine = AnalyticsEngine()
    result = engine.execute_function(function_name, **args)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()