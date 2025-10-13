#!/usr/bin/env python3
"""
Test script for Ollama Cloud provider
"""

import asyncio
import logging
import os
from llm.providers.ollama import OllamaProvider

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_ollama_cloud():
    """Test Ollama Cloud provider functionality"""
    
    # Get API key from environment
    api_key = os.getenv("OLLAMA_API_KEY")
    if not api_key:
        logger.error("❌ OLLAMA_API_KEY environment variable not set")
        logger.info("💡 Set with: export OLLAMA_API_KEY=your_api_key")
        return
    
    try:
        # Create Ollama Cloud provider
        provider = OllamaProvider(
            api_key=api_key,
            default_model="gpt-oss:120b",  # Use cloud model
            base_url="https://ollama.com/api"
        )
        
        logger.info("✅ Ollama Cloud provider created successfully")
        logger.info(f"🔗 Using endpoint: {provider.cloud_endpoint}")
        logger.info(f"🤖 Using model: gpt-oss:120b")
        
        # Test basic API call
        messages = [
            {"role": "user", "content": "Why is the sky blue? Please provide a brief scientific explanation."}
        ]
        
        logger.info("🔄 Testing Ollama Cloud API call...")
        response = await provider.call_api(
            model="gpt-oss:120b",
            messages=messages,
            max_tokens=200
        )
        
        if response.get("success"):
            logger.info("✅ Ollama Cloud API call successful")
            
            # Parse response
            content, tool_calls = provider.parse_response(response["data"])
            logger.info(f"📝 Response content: {content[:200]}...")
            logger.info(f"🔧 Tool calls: {len(tool_calls)}")
            
        else:
            logger.error(f"❌ Ollama Cloud API call failed: {response.get('error')}")
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")

async def test_ollama_local():
    """Test local Ollama provider functionality"""
    
    try:
        # Create local Ollama provider
        provider = OllamaProvider(
            api_key="",  # No API key for local
            default_model="qwen3:0.6b",
            base_url="http://localhost:11434"
        )
        
        logger.info("✅ Local Ollama provider created successfully")
        logger.info(f"🔗 Using local endpoint: http://localhost:11434")
        logger.info(f"🤖 Using model: qwen3:0.6b")
        
        # Test basic API call
        messages = [
            {"role": "user", "content": "Hello, respond with a brief greeting."}
        ]
        
        logger.info("🔄 Testing local Ollama API call...")
        response = await provider.call_api(
            model="qwen3:0.6b",
            messages=messages,
            max_tokens=50
        )
        
        if response.get("success"):
            logger.info("✅ Local Ollama API call successful")
            
            # Parse response
            content, tool_calls = provider.parse_response(response["data"])
            logger.info(f"📝 Response content: {content}")
            logger.info(f"🔧 Tool calls: {len(tool_calls)}")
            
        else:
            logger.error(f"❌ Local Ollama API call failed: {response.get('error')}")
            
    except Exception as e:
        logger.error(f"❌ Local test failed: {e}")
        logger.info("💡 Make sure Ollama is running locally at http://localhost:11434")

async def main():
    """Run both tests"""
    logger.info("🧪 Testing Ollama Provider - Cloud and Local")
    logger.info("=" * 50)
    
    logger.info("🌐 Testing Ollama Cloud...")
    await test_ollama_cloud()
    
    logger.info("\n" + "=" * 50)
    
    logger.info("🏠 Testing Local Ollama...")
    await test_ollama_local()

if __name__ == "__main__":
    asyncio.run(main())