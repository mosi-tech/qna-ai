#!/usr/bin/env python3
"""
Test script for MCP HTTP Wrapper

This script tests if the MCP HTTP wrapper is properly bridging MCP servers to HTTP endpoints.
"""

import asyncio
import json
import httpx

async def test_mcp_http_wrapper():
    print("🧪 MCP HTTP Wrapper Test")
    print("=" * 40)
    
    # Test endpoints
    financial_server = "http://localhost:8001"
    analytics_server = "http://localhost:8002"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test 1: Health checks
        print("\n1. Testing health endpoints...")
        
        try:
            response = await client.get(f"{financial_server}/health")
            if response.status_code == 200:
                print(f"✅ Financial server health: {response.json()}")
            else:
                print(f"❌ Financial server health failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Financial server unreachable: {e}")
        
        try:
            response = await client.get(f"{analytics_server}/health")
            if response.status_code == 200:
                print(f"✅ Analytics server health: {response.json()}")
            else:
                print(f"❌ Analytics server health failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Analytics server unreachable: {e}")
        
        # Test 2: Tools discovery
        print("\n2. Testing tools endpoints...")
        
        try:
            response = await client.get(f"{financial_server}/tools")
            if response.status_code == 200:
                tools_data = response.json()
                tools_list = tools_data.get('tools', [])
                print(f"✅ Financial server tools: {len(tools_list)} tools found")
                if tools_list:
                    sample_tools = [t.get('name', 'unnamed') for t in tools_list[:3]]
                    print(f"   Sample tools: {sample_tools}")
                else:
                    print("   ⚠️  No tools returned - MCP server connection issue")
            else:
                print(f"❌ Financial server tools failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Financial server tools error: {e}")
        
        try:
            response = await client.get(f"{analytics_server}/tools")
            if response.status_code == 200:
                tools_data = response.json()
                tools_list = tools_data.get('tools', [])
                print(f"✅ Analytics server tools: {len(tools_list)} tools found")
                if tools_list:
                    sample_tools = [t.get('name', 'unnamed') for t in tools_list[:3]]
                    print(f"   Sample tools: {sample_tools}")
                else:
                    print("   ⚠️  No tools returned - MCP server connection issue")
            else:
                print(f"❌ Analytics server tools failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Analytics server tools error: {e}")
        
        # Test 3: Sample tool execution (if tools are available)
        print("\n3. Testing tool execution...")
        
        # Try a simple financial tool
        try:
            response = await client.post(
                f"{financial_server}/execute/alpaca_trading_account", 
                json={}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Sample financial tool execution successful")
                print(f"   Account status: {result.get('status', 'unknown')}")
            else:
                print(f"❌ Financial tool execution failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Financial tool execution error: {e}")
        
        # Try a simple analytics tool
        try:
            response = await client.post(
                f"{analytics_server}/execute/calculate_returns_metrics",
                json={"returns": {"0": 0.01, "1": 0.02, "2": -0.01}}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Sample analytics tool execution successful")
                print(f"   Result keys: {list(result.keys()) if isinstance(result, dict) else 'non-dict result'}")
            else:
                print(f"❌ Analytics tool execution failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Analytics tool execution error: {e}")
    
    print("\n" + "=" * 60)
    print("🔧 DIAGNOSIS")
    print("=" * 60)
    print("If tools are empty:")
    print("  - MCP servers may not be properly connected via stdio")
    print("  - MCP HTTP wrapper may have configuration issues")
    print("  - Check MCP server paths in mcp-http-wrapper.py")
    print("\nIf tool execution fails:")
    print("  - Check tool names match exactly")
    print("  - Verify parameter formats")
    print("  - Check MCP server implementations")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_mcp_http_wrapper())