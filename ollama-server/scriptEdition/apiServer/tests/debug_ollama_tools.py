#!/usr/bin/env python3
"""
Debug script to check Ollama MCP tools integration
"""

import asyncio
import logging
import os
from services.analysis import AnalysisService
from llm.utils import LLMConfig
from llm.service import create_llm_service

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def debug_ollama_mcp_tools():
    """Debug Ollama MCP tools integration"""
    
    print("🔍 Debugging Ollama MCP Tools Integration")
    print("=" * 60)
    
    # Test 1: Check environment setup
    print("1️⃣ Environment Check:")
    api_key = os.getenv("OLLAMA_API_KEY")
    print(f"   OLLAMA_API_KEY: {'✅ Set' if api_key else '❌ Not set'}")
    
    # Test 2: Create Ollama service directly
    print("\n2️⃣ Creating Ollama LLM Service:")
    
    config = LLMConfig(
        provider_type="ollama",
        default_model="gpt-oss:120b" if api_key else "qwen3:0.6b",
        api_key=api_key or "",
        base_url="https://ollama.com/api" if api_key else "http://localhost:11434"
    )
    
    llm_service = create_llm_service(config=config)
    print(f"   Service created: ✅")
    print(f"   Provider type: {llm_service.provider_type}")
    print(f"   Is cloud: {getattr(llm_service.provider, 'is_cloud', 'N/A')}")
    
    # Test 3: Create Analysis Service
    print("\n3️⃣ Creating Analysis Service with Ollama:")
    
    analysis_service = AnalysisService(llm_service=llm_service)
    print(f"   Analysis service created: ✅")
    
    # Test 4: Check MCP initialization
    print("\n4️⃣ Checking MCP Integration:")
    
    try:
        init_result = await analysis_service.ensure_mcp_initialized()
        print(f"   MCP initialization: {'✅ Success' if init_result else '❌ Failed'}")
        
        if init_result:
            mcp_tools = analysis_service.get_mcp_tools()
            print(f"   MCP tools count: {len(mcp_tools)}")
            
            if mcp_tools:
                print("   First 3 MCP tools:")
                for i, tool in enumerate(mcp_tools[:3]):
                    print(f"     {i+1}. {tool.get('function', {}).get('name', 'unknown')}")
            else:
                print("   ❌ No MCP tools found")
                
    except Exception as e:
        print(f"   MCP initialization failed: ❌ {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
    
    # Test 5: Check provider tools
    print("\n5️⃣ Checking Provider Tools:")
    
    try:
        # Check raw tools
        raw_tools = getattr(llm_service.provider, '_raw_tools', None)
        print(f"   Raw tools count: {len(raw_tools) if raw_tools else 0}")
        
        # Check processed tools
        processed_tools = llm_service.provider.get_processed_tools()
        print(f"   Processed tools count: {len(processed_tools)}")
        
        if processed_tools:
            print("   First 3 processed tools:")
            for i, tool in enumerate(processed_tools[:3]):
                print(f"     {i+1}. {tool.get('function', {}).get('name', 'unknown')}")
        else:
            print("   ❌ No processed tools found")
            
    except Exception as e:
        print(f"   Provider tools check failed: ❌ {e}")
    
    # Test 6: Simple analysis with tools
    print("\n6️⃣ Testing Simple Analysis:")
    
    try:
        question = "What are the top 5 most active stocks today?"
        print(f"   Question: {question}")
        
        result = await analysis_service.analyze_question(question)
        
        if result.get("success"):
            print("   Analysis: ✅ Success")
            print(f"   Response preview: {result.get('content', '')[:200]}...")
            
            # Check if tools were used
            tool_calls = result.get('tool_calls', [])
            print(f"   Tool calls made: {len(tool_calls)}")
            
            if tool_calls:
                for i, call in enumerate(tool_calls):
                    function_name = call.get('function', {}).get('name', 'unknown')
                    print(f"     {i+1}. {function_name}")
            
        else:
            print(f"   Analysis failed: ❌ {result.get('error')}")
            
    except Exception as e:
        print(f"   Analysis test failed: ❌ {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(debug_ollama_mcp_tools())