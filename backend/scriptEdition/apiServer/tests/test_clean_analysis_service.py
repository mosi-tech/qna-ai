#!/usr/bin/env python3
"""
Test the cleaned up Analysis Service with simplified MCP tools
"""

import asyncio
import logging
import os
from services.analysis import AnalysisService
from llm.service import create_analysis_llm
from llm.utils import LLMConfig

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_clean_analysis_service():
    """Test the cleaned up Analysis Service"""
    
    print("🧪 Testing Cleaned Analysis Service")
    print("=" * 60)
    
    # Test 1: Default Analysis Service
    print("1️⃣ Testing default Analysis Service:")
    
    analysis_service = AnalysisService()
    print(f"   ✅ Created analysis service")
    print(f"   Provider: {analysis_service.llm_service.provider_type}")
    print(f"   Model: {analysis_service.llm_service.default_model}")
    
    # Test 2: Analysis Service with Ollama
    print("\n2️⃣ Testing Analysis Service with Ollama:")
    
    api_key = os.getenv("OLLAMA_API_KEY")
    
    config = LLMConfig(
        provider_type="ollama",
        default_model="gpt-oss:120b" if api_key else "qwen3:0.6b",
        api_key=api_key or "",
        base_url="https://ollama.com/api" if api_key else "http://localhost:11434",
        service_name="analysis"
    )
    
    llm_service = create_analysis_llm()  # This should use analysis-tools.json
    ollama_analysis = AnalysisService(llm_service=llm_service)
    
    print(f"   ✅ Created Ollama analysis service")
    print(f"   Provider: {ollama_analysis.llm_service.provider_type}")
    print(f"   Is cloud: {getattr(ollama_analysis.llm_service.provider, 'is_cloud', 'N/A')}")
    
    # Test 3: Tools loading
    print("\n3️⃣ Testing MCP tools loading:")
    
    await ollama_analysis.llm_service.ensure_tools_loaded()
    tools_count = len(ollama_analysis.llm_service.default_tools)
    print(f"   Tools loaded: {tools_count}")
    
    if tools_count > 0:
        print("   Sample tools:")
        for tool in ollama_analysis.llm_service.default_tools[:3]:
            name = tool.get('function', {}).get('name', 'unknown')
            print(f"     - {name}")
    
    # Test 4: Tool management
    print("\n4️⃣ Testing tool management:")
    
    # Test tool override and reset
    ollama_analysis.llm_service.override_tools([])  # Empty tools
    current_tools = ollama_analysis.llm_service.provider.get_processed_tools()
    print(f"   After override (empty): {len(current_tools)} tools")
    
    # Reset to defaults
    ollama_analysis.llm_service.reset_to_default_tools()
    current_tools = ollama_analysis.llm_service.provider.get_processed_tools()
    print(f"   After reset: {len(current_tools)} tools")
    
    # Test 5: Simple analysis (if tools available)
    print("\n5️⃣ Testing simple analysis:")
    
    if tools_count > 0:
        try:
            question = "What are the available tools?"
            print(f"   Question: {question}")
            
            # This should work now with the simplified system
            result = await ollama_analysis.analyze_question(question)
            
            if result.get("success"):
                print("   ✅ Analysis completed successfully")
                response_preview = result.get('content', '')[:200]
                print(f"   Response preview: {response_preview}...")
                
                tool_calls = result.get('tool_calls', [])
                print(f"   Tool calls made: {len(tool_calls)}")
            else:
                print(f"   ❌ Analysis failed: {result.get('error')}")
                
        except Exception as e:
            print(f"   ❌ Analysis test failed: {e}")
    else:
        print("   🚫 Skipping analysis test (no tools available)")

if __name__ == "__main__":
    asyncio.run(test_clean_analysis_service())