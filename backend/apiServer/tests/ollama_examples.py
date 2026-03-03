#!/usr/bin/env python3
"""
Examples of using Ollama provider with both local and cloud configurations
"""

import asyncio
from llm.service import create_llm_service
from llm.utils import LLMConfig

async def example_local_ollama():
    """Example using local Ollama instance"""
    
    # Create config for local Ollama
    config = LLMConfig(
        provider_type="ollama",
        api_key="",  # No API key needed for local
        base_url="http://localhost:11434",
        default_model="qwen3:0.6b",
        max_tokens=2000,
        temperature=0.7
    )
    
    # Create LLM service
    llm_service = create_llm_service(config=config)
    
    print("🏠 Local Ollama Example")
    print(f"Provider: {llm_service.provider_type}")
    print(f"Model: {llm_service.default_model}")
    print(f"Config: {llm_service.get_config_info()}")
    
    # Make a simple request
    result = await llm_service.simple_completion(
        prompt="Explain quantum computing in one sentence.",
        max_tokens=100
    )
    
    if result["success"]:
        print(f"✅ Response: {result['content']}")
    else:
        print(f"❌ Error: {result['error']}")

async def example_cloud_ollama():
    """Example using Ollama Cloud"""
    
    # Create config for Ollama Cloud
    config = LLMConfig(
        provider_type="ollama",
        api_key="YOUR_OLLAMA_API_KEY",  # Replace with actual API key
        base_url="https://ollama.com/api",
        default_model="gpt-oss:120b",
        max_tokens=2000,
        temperature=0.7
    )
    
    # Create LLM service
    llm_service = create_llm_service(config=config)
    
    print("\n🌐 Ollama Cloud Example")
    print(f"Provider: {llm_service.provider_type}")
    print(f"Model: {llm_service.default_model}")
    print(f"Config: {llm_service.get_config_info()}")
    
    # Note: This will only work with a valid API key
    print("Note: Replace YOUR_OLLAMA_API_KEY with actual API key to test")

async def example_factory_auto_detection():
    """Example showing automatic detection of local vs cloud"""
    
    from llm.providers import create_provider
    
    # Local Ollama (no API key)
    local_provider = create_provider(
        "ollama", 
        api_key="",
        default_model="qwen3:0.6b"
    )
    print(f"\n🔍 Auto-detection - Local: {local_provider.is_cloud}")
    
    # Cloud Ollama (with API key)
    cloud_provider = create_provider(
        "ollama",
        api_key="fake_key_for_demo",
        default_model="gpt-oss:120b"
    )
    print(f"🔍 Auto-detection - Cloud: {cloud_provider.is_cloud}")

if __name__ == "__main__":
    async def main():
        await example_local_ollama()
        await example_cloud_ollama()
        await example_factory_auto_detection()
    
    asyncio.run(main())