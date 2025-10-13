#!/usr/bin/env python3
"""
Test Ollama configuration and API key handling
"""

import os
from llm.utils import LLMConfig
from llm.service import create_llm_service

def test_config_creation():
    """Test different ways to create Ollama config"""
    
    print("🔧 Testing Ollama Configuration")
    print("=" * 50)
    
    # Test 1: Environment variable pickup
    print("1️⃣ Testing environment variable pickup:")
    api_key = os.getenv("OLLAMA_API_KEY")
    print(f"   OLLAMA_API_KEY from env: {'✅ Set' if api_key else '❌ Not set'}")
    
    if api_key:
        print(f"   Key preview: {api_key[:8]}...")
    
    # Test 2: Auto config from environment
    print("\n2️⃣ Testing auto config from environment:")
    
    # Set environment for testing
    os.environ["LLM_PROVIDER"] = "ollama"
    os.environ["LLM_BASE_URL"] = "https://ollama.com/api"
    
    config = LLMConfig.from_env()
    print(f"   Provider: {config.provider_type}")
    print(f"   Model: {config.default_model}")
    print(f"   API Key: {'✅ Set' if config.api_key else '❌ Not set'}")
    print(f"   Base URL: {config.base_url}")
    
    # Test 3: Manual config for cloud
    print("\n3️⃣ Testing manual config for Ollama Cloud:")
    
    cloud_config = LLMConfig(
        provider_type="ollama",
        default_model="gpt-oss:120b",
        api_key=api_key,  # Use actual API key from env
        base_url="https://ollama.com/api"
    )
    
    print(f"   Provider: {cloud_config.provider_type}")
    print(f"   Model: {cloud_config.default_model}")
    print(f"   API Key: {'✅ Set' if cloud_config.api_key else '❌ Not set'}")
    print(f"   Base URL: {cloud_config.base_url}")
    
    # Test 4: Service creation
    print("\n4️⃣ Testing LLM service creation:")
    
    try:
        service = create_llm_service(config=cloud_config)
        info = service.get_config_info()
        print(f"   Service created: ✅")
        print(f"   Provider: {info['provider']}")
        print(f"   Model: {info['model']}")
        print(f"   Has API Key: {'✅' if info['has_api_key'] else '❌'}")
        print(f"   Base URL: {info['base_url']}")
        
        # Check if provider detected cloud correctly
        print(f"   Is Cloud: {'✅' if service.provider.is_cloud else '❌'}")
        
    except Exception as e:
        print(f"   Service creation failed: ❌ {e}")

def test_provider_direct():
    """Test provider creation directly"""
    
    print("\n🔧 Testing Direct Provider Creation")
    print("=" * 50)
    
    from llm.providers.ollama import OllamaProvider
    
    api_key = os.getenv("OLLAMA_API_KEY")
    
    if api_key:
        provider = OllamaProvider(
            api_key=api_key,
            default_model="gpt-oss:120b",
            base_url="https://ollama.com/api"
        )
        
        print(f"Provider created: ✅")
        print(f"Is Cloud: {'✅' if provider.is_cloud else '❌'}")
        print(f"API Key: {'✅ Set' if provider.api_key else '❌ Not set'}")
        print(f"Endpoint: {provider.cloud_endpoint}")
        
    else:
        print("❌ No OLLAMA_API_KEY found in environment")
        print("💡 Set with: export OLLAMA_API_KEY=your_api_key")

if __name__ == "__main__":
    test_config_creation()
    test_provider_direct()