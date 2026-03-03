#!/usr/bin/env python3
"""
Test script for Ollama provider
"""

import asyncio
import logging
from llm.providers.ollama import OllamaProvider

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_ollama_provider():
    """Test Ollama provider basic functionality"""
    
    try:
        # Create Ollama provider
        provider = OllamaProvider(
            default_model="qwen3:0.6b",  # Use available model
            base_url="http://localhost:11434"
        )
        
        logger.info("✅ Ollama provider created successfully")
        
        # Test basic API call
        messages = [
            {"role": "user", "content": "Hello, respond with a JSON object containing a greeting message."}
        ]
        
        logger.info("🔄 Testing basic API call...")
        response = await provider.call_api(
            model="qwen3:0.6b",  # Use available model
            messages=messages,
            max_tokens=100
        )
        
        if response.get("success"):
            logger.info("✅ API call successful")
            
            # Parse response
            content, tool_calls = provider.parse_response(response["data"])
            logger.info(f"📝 Response content: {content[:100]}...")
            logger.info(f"🔧 Tool calls: {len(tool_calls)}")
            
        else:
            logger.error(f"❌ API call failed: {response.get('error')}")
            
    except ImportError as e:
        logger.error(f"❌ Ollama library not installed: {e}")
        logger.info("💡 Install with: pip install ollama")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        logger.info("💡 Make sure Ollama is running at http://localhost:11434")

if __name__ == "__main__":
    asyncio.run(test_ollama_provider())