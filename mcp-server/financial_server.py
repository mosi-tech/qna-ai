#!/usr/bin/env python3
"""
MCP Financial Server - Unified Implementation

Delegates to mock or real implementation based on USE_MOCK_FINANCIAL_DATA environment variable.
Set USE_MOCK_FINANCIAL_DATA=false to use real APIs with credentials.
"""

import os
import sys
import asyncio

def main():
    """Main entry point - delegates to appropriate implementation"""
    use_mock = os.getenv('USE_MOCK_FINANCIAL_DATA', 'true').lower() == 'true'
    
    if use_mock:
        # Import and run mock server
        from financial_server_mock import main as mock_main
        print("Starting MCP Financial Server (Mock Implementation)...")
        asyncio.run(mock_main())
    else:
        # Import and run real server  
        from financial_server_real import main as real_main
        print("Starting MCP Financial Server (Real Implementation)...")
        asyncio.run(real_main())


if __name__ == "__main__":
    main()