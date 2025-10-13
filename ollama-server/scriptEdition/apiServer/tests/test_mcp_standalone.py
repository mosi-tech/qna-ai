#!/usr/bin/env python3
"""
Test MCP client standalone to verify tools are available
"""

import asyncio
import logging
from integrations.mcp.mcp_integration import MCPIntegration

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_mcp_standalone():
    """Test MCP integration standalone"""
    
    print("🔧 Testing MCP Integration Standalone")
    print("=" * 50)
    
    # Create MCP integration
    mcp_integration = MCPIntegration()
    
    # Test initialization
    print("1️⃣ Initializing MCP...")
    init_success = await mcp_integration.ensure_mcp_initialized()
    
    if init_success:
        print("   ✅ MCP initialized successfully")
        
        # Get tools
        tools = mcp_integration.get_mcp_tools()
        print(f"   📊 Available tools: {len(tools)}")
        
        if tools:
            print("   🔧 Sample tools:")
            for i, tool in enumerate(tools[:5]):  # Show first 5 tools
                name = tool.get('function', {}).get('name', 'unknown')
                desc = tool.get('function', {}).get('description', 'No description')
                print(f"     {i+1}. {name}")
                print(f"        {desc[:100]}...")
        else:
            print("   ❌ No tools found")
            
    else:
        print("   ❌ MCP initialization failed")
        
    # Test specific tool lookup
    print("\n2️⃣ Testing specific tool patterns...")
    
    if init_success and tools:
        financial_tools = [t for t in tools if 'alpaca' in t.get('function', {}).get('name', '').lower()]
        analytics_tools = [t for t in tools if 'calculate' in t.get('function', {}).get('name', '').lower()]
        
        print(f"   📈 Financial tools: {len(financial_tools)}")
        print(f"   📊 Analytics tools: {len(analytics_tools)}")
        
        if financial_tools:
            print("   Sample financial tools:")
            for tool in financial_tools[:3]:
                print(f"     - {tool.get('function', {}).get('name')}")
                
        if analytics_tools:
            print("   Sample analytics tools:")
            for tool in analytics_tools[:3]:
                print(f"     - {tool.get('function', {}).get('name')}")

if __name__ == "__main__":
    asyncio.run(test_mcp_standalone())