#!/usr/bin/env python3
"""
Test simplified MCP tools system
"""

import asyncio
import logging
import os
from llm.service import create_analysis_llm, create_code_prompt_builder_llm, LLMService
from llm.utils import LLMConfig
from llm.mcp_tools import load_mcp_tools

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_mcp_configs():
    """Test different MCP configurations"""
    
    print("🧪 Testing Simplified MCP Tools System")
    print("=" * 60)
    
    # Test 1: Direct config loading
    print("1️⃣ Testing direct config loading:")
    
    configs_to_test = [
        "analysis-tools.json",
        "code-gen-tools.json", 
        "no-tools.json",
        "default-tools.json"
    ]
    
    for config_file in configs_to_test:
        try:
            tools = await load_mcp_tools(config_file)
            print(f"   {config_file}: ✅ {len(tools)} tools")
            if tools:
                for tool in tools[:2]:  # Show first 2 tools
                    name = tool.get('function', {}).get('name', 'unknown')
                    print(f"     - {name}")
        except Exception as e:
            print(f"   {config_file}: ❌ {e}")
    
    # Test 2: Service-specific tool loading
    print("\n2️⃣ Testing service-specific tool loading:")
    
    # Analysis service (should load analysis-tools.json)
    print("   Analysis Service:")
    analysis_service = create_analysis_llm()
    await analysis_service.ensure_tools_loaded()
    print(f"     Tools loaded: {len(analysis_service.default_tools)}")
    
    # Code gen service (should load code-gen-tools.json)  
    print("   Code Gen Service:")
    code_gen_service = create_code_prompt_builder_llm()
    await code_gen_service.ensure_tools_loaded()
    print(f"     Tools loaded: {len(code_gen_service.default_tools)}")
    
    # Test 3: Manual configuration modes
    print("\n3️⃣ Testing manual configuration modes:")
    
    # No tools mode
    print("   No Tools Mode:")
    config = LLMConfig(
        provider_type="ollama",
        default_model="qwen3:0.6b",
        mcp_tools_mode="none"
    )
    no_tools_service = LLMService(config)
    await no_tools_service.ensure_tools_loaded()
    print(f"     Tools loaded: {len(no_tools_service.default_tools)}")
    
    # Explicit config mode
    print("   Explicit Config Mode:")
    config = LLMConfig(
        provider_type="ollama",
        default_model="qwen3:0.6b", 
        mcp_tools_mode="config",
        mcp_tools_config="analysis-tools.json"
    )
    explicit_service = LLMService(config)
    await explicit_service.ensure_tools_loaded()
    print(f"     Tools loaded: {len(explicit_service.default_tools)}")
    
    # Test 4: Runtime tool management
    print("\n4️⃣ Testing runtime tool management:")
    
    service = create_analysis_llm()
    await service.ensure_tools_loaded()
    original_count = len(service.default_tools)
    print(f"   Original tools: {original_count}")
    
    # Override with empty tools
    service.override_tools([])
    current_tools = service.provider.get_processed_tools()
    print(f"   After override (empty): {len(current_tools)}")
    
    # Reset to default
    service.reset_to_default_tools()
    current_tools = service.provider.get_processed_tools()
    print(f"   After reset: {len(current_tools)}")
    
    # Load different config
    await service.load_tools_from_config("code-gen-tools.json")
    current_tools = service.provider.get_processed_tools()
    print(f"   After loading code-gen config: {len(current_tools)}")

async def test_ollama_with_tools():
    """Test Ollama provider with MCP tools"""
    
    print("\n🔧 Testing Ollama with MCP Tools")
    print("=" * 60)
    
    # Set up Ollama service
    api_key = os.getenv("OLLAMA_API_KEY")
    
    config = LLMConfig(
        provider_type="ollama",
        default_model="gpt-oss:120b" if api_key else "qwen3:0.6b",
        api_key=api_key or "",
        base_url="https://ollama.com/api" if api_key else "http://localhost:11434",
        service_name="analysis"
    )
    
    service = LLMService(config)
    await service.ensure_tools_loaded()
    
    print(f"   Provider: {service.provider_type}")
    print(f"   Is cloud: {getattr(service.provider, 'is_cloud', 'N/A')}")
    print(f"   Tools loaded: {len(service.default_tools)}")
    
    if service.default_tools:
        print("   Sample tools:")
        for tool in service.default_tools[:3]:
            name = tool.get('function', {}).get('name', 'unknown')
            print(f"     - {name}")

if __name__ == "__main__":
    async def main():
        await test_mcp_configs()
        await test_ollama_with_tools()
    
    asyncio.run(main())