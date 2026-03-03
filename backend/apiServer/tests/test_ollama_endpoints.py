#!/usr/bin/env python3
"""
Test different Ollama endpoints to verify correct API path
"""

import requests
import json
import os

def test_endpoint(url, api_key, data):
    """Test a specific endpoint"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"🧪 Testing: {url}")
        response = requests.post(url, headers=headers, json=data, timeout=10)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 405:
            print("❌ Method Not Allowed - Wrong endpoint")
        elif response.status_code == 401:
            print("🔑 Unauthorized - Check API key")
        elif response.status_code == 404:
            print("🔍 Not Found - Wrong path")
        elif response.status_code == 200:
            print("✅ Success!")
            print(f"📝 Response: {response.json()}")
        else:
            print(f"⚠️ Unexpected status: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    print("-" * 50)

def main():
    # Get API key from environment
    api_key = os.getenv("OLLAMA_API_KEY", "test_key")
    
    # Test data
    test_data = {
        "model": "gpt-oss:120b",
        "messages": [
            {"role": "user", "content": "Hello"}
        ],
        "stream": False
    }
    
    print("🔍 Testing Ollama Cloud Endpoints")
    print("=" * 50)
    
    # Test different possible endpoints
    endpoints = [
        "https://ollama.com/chat",           # This gives 405
        "https://ollama.com/api/chat",       # Correct endpoint from curl example
        "https://ollama.com/v1/chat",        # Alternative
        "https://ollama.com/api/v1/chat",    # Alternative
    ]
    
    for endpoint in endpoints:
        test_endpoint(endpoint, api_key, test_data)

if __name__ == "__main__":
    main()