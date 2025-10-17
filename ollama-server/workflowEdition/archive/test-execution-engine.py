#!/usr/bin/env python3
"""
Test script for the Financial Analysis Execution Engine
"""

import requests
import json
import time

def test_execution_engine():
    """Test the execution engine"""
    base_url = "http://localhost:8003"
    
    # Test health check
    print("Testing execution engine health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            health_data = response.json()
            print(f"Available tools: {health_data.get('available_tools', 0)}")
            print(f"MCP servers: {health_data.get('mcp_servers', [])}")
        else:
            print("❌ Health check failed")
            return
    except requests.RequestException as e:
        print(f"❌ Execution engine not running: {e}")
        return
    
    # Test tools endpoint
    print("\nTesting tools discovery...")
    try:
        response = requests.get(f"{base_url}/tools")
        if response.status_code == 200:
            tools_data = response.json()
            print("✅ Tools discovery working")
            print(f"Total tools available: {tools_data.get('total_tools', 0)}")
            print("Tool mappings:")
            for tool, server in list(tools_data.get('tools', {}).items())[:5]:  # Show first 5
                print(f"  - {tool} → {server}")
            if tools_data.get('total_tools', 0) > 5:
                print(f"  ... and {tools_data.get('total_tools', 0) - 5} more")
        else:
            print("❌ Tools discovery failed")
    except requests.RequestException as e:
        print(f"❌ Tools discovery error: {e}")
    
    # Test execution with sample plans
    print("\nTesting execution with sample plans...")
    test_plans = [
        {
            "question": "Get most active stocks",
            "plan": {
                "steps": [
                    {
                        "fn": "alpaca_market_screener_most_actives",
                        "args": {"top": 5}
                    }
                ]
            },
            "description": "Sample plan to get most active stocks"
        },
        {
            "question": "Get AAPL current data",
            "plan": {
                "steps": [
                    {
                        "fn": "alpaca_market_stocks_snapshots",
                        "args": {"symbols": "AAPL"}
                    }
                ]
            },
            "description": "Sample plan to get AAPL snapshot data"
        }
    ]
    
    for test_plan in test_plans:
        print(f"\nTesting execution: {test_plan['question']}")
        try:
            response = requests.post(
                f"{base_url}/execute",
                json=test_plan,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Execution successful")
                if result.get("success"):
                    data = result.get("data", {})
                    metadata = data.get("metadata", {})
                    execution_summary = metadata.get("execution_summary", {})
                    print(f"Execution summary: {execution_summary}")
                    print(f"Data sources: {metadata.get('data_sources', [])}")
                    
                    # Show first few results
                    body = data.get("body", [])
                    print("Sample results:")
                    for item in body[:3]:  # Show first 3 items
                        print(f"  - {item.get('key')}: {str(item.get('value'))[:100]}...")
                else:
                    print(f"Execution failed: {result.get('error')}")
            else:
                print(f"❌ Execution failed: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.RequestException as e:
            print(f"❌ Execution error: {e}")
        
        time.sleep(1)  # Brief pause between requests

def test_end_to_end_workflow():
    """Test the complete workflow: planning + execution"""
    print("\n" + "="*60)
    print("TESTING END-TO-END WORKFLOW")
    print("="*60)
    
    # Step 1: Get a plan from ollama-server
    print("Step 1: Getting tool call plan from ollama-server...")
    try:
        planning_response = requests.post(
            "http://localhost:8000/analyze",
            json={"question": "What are the top 3 most active stocks today?", "model": "qwen3:0.6b"},
            timeout=30
        )
        
        if planning_response.status_code != 200:
            print("❌ Failed to get plan from ollama-server")
            return
            
        planning_result = planning_response.json()
        if not planning_result.get("success"):
            print("❌ Planning failed")
            return
            
        # Extract the tool calls from the planning result
        planning_data = planning_result.get("data", {})
        body = planning_data.get("body", [])
        
        # Find the DSL response
        dsl_response = None
        for item in body:
            if item.get("key") == "dsl_response":
                dsl_response = item.get("value")
                break
        
        if not dsl_response or not dsl_response.get("steps"):
            print("❌ No valid tool calls found in planning response")
            return
            
        print(f"✅ Got plan with {len(dsl_response['steps'])} steps")
        
        # Step 2: Execute the plan
        print("Step 2: Executing the plan...")
        execution_request = {
            "question": "What are the top 3 most active stocks today?",
            "plan": dsl_response,
            "description": "End-to-end test: planning + execution"
        }
        
        execution_response = requests.post(
            "http://localhost:8003/execute",
            json=execution_request,
            timeout=60
        )
        
        if execution_response.status_code == 200:
            execution_result = execution_response.json()
            if execution_result.get("success"):
                print("✅ End-to-end workflow successful!")
                data = execution_result.get("data", {})
                metadata = data.get("metadata", {})
                print(f"Execution mode: {metadata.get('execution_mode')}")
                print(f"Success rate: {metadata.get('execution_summary', {}).get('success_rate', 'unknown')}")
            else:
                print(f"❌ Execution failed: {execution_result.get('error')}")
        else:
            print(f"❌ Execution request failed: {execution_response.status_code}")
            
    except Exception as e:
        print(f"❌ End-to-end test error: {e}")

if __name__ == "__main__":
    print("Testing Financial Analysis Execution Engine")
    print("=" * 60)
    test_execution_engine()
    
    # Test end-to-end workflow if both servers are running
    test_end_to_end_workflow()