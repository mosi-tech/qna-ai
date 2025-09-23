#!/usr/bin/env python3
"""
Test script for Ollama MCP Integration
"""

import requests
import json
import time

def test_server():
    """Test the Ollama MCP server"""
    base_url = "http://localhost:8000"
    
    # Test health check
    print("Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print("❌ Health check failed")
            return
    except requests.RequestException as e:
        print(f"❌ Server not running: {e}")
        return
    
    # Test models endpoint
    print("\nTesting models endpoint...")
    try:
        response = requests.get(f"{base_url}/models")
        if response.status_code == 200:
            print("✅ Models endpoint working")
            print(f"Response: {response.json()}")
        else:
            print("❌ Models endpoint failed")
    except requests.RequestException as e:
        print(f"❌ Models endpoint error: {e}")
    
    # Test analysis endpoint
    print("\nTesting analysis endpoint...")
    test_questions = [
        "What are the top 5 most active stocks today?",
        "Calculate the 20-day moving average for AAPL",
        "Show me portfolio risk metrics for a sample portfolio"
    ]
    
    for question in test_questions:
        print(f"\nTesting question: {question}")
        try:
            response = requests.post(
                f"{base_url}/analyze",
                json={"question": question, "model": "gpt-oss:20b"},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Analysis successful")
                if result.get("success"):
                    print(f"Data: {json.dumps(result.get('data', {}), indent=2)}")
                else:
                    print(f"Error: {result.get('error')}")
            else:
                print(f"❌ Analysis failed: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.RequestException as e:
            print(f"❌ Analysis error: {e}")
        
        time.sleep(1)  # Brief pause between requests

if __name__ == "__main__":
    print("Testing Ollama MCP Integration Server")
    print("=" * 50)
    test_server()