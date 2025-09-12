#!/usr/bin/env python3
"""
Standalone Analytics Main - Can be run directly without import issues
"""

import sys
import os
import json
import argparse

# Add the parent directory to sys.path to enable imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import with absolute imports
from analytics.main import analytics_engine

def main():
    """Main entry point for command-line usage"""
    parser = argparse.ArgumentParser(description='Financial Analytics Engine')
    parser.add_argument('--list-functions', action='store_true', 
                       help='List all available functions')
    parser.add_argument('--function', type=str, 
                       help='Execute specific function')
    parser.add_argument('--data', type=str, 
                       help='JSON data file path')
    
    args = parser.parse_args()
    
    if args.list_functions:
        functions = analytics_engine.list_functions()
        counts = analytics_engine.get_function_count()
        
        print("📊 Comprehensive Technical Analysis System")
        print("=" * 50)
        print(f"Total Functions: {counts['total']}")
        print()
        
        for category, function_list in functions.items():
            print(f"{category.replace('_', ' ').title()} ({len(function_list)}):")
            for func in function_list:
                print(f"  - {func}")
            print()
                
    elif args.function and args.data:
        try:
            with open(args.data, 'r') as f:
                data = json.load(f)
            
            result = analytics_engine.execute_function(args.function, data=data)
            print(json.dumps(result, indent=2, default=str))
            
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()