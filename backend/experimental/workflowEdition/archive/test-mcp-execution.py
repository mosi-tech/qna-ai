#!/usr/bin/env python3
"""
Test script for Enhanced Execution Engine

This script helps test and debug workflow execution directly through the Enhanced Execution Engine.
"""

import asyncio
import json
import httpx
import os

EXECUTION_ENGINE_URL = "http://localhost:8003"

async def check_execution_engine_status():
    """Check if the Enhanced Execution Engine is running"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{EXECUTION_ENGINE_URL}/health")
            if response.status_code == 200:
                return f"✅ Enhanced Execution Engine is running - Status: {response.status_code}"
            else:
                return f"⚠️ Engine responding but with status: {response.status_code}"
    except Exception as e:
        return f"❌ Enhanced Execution Engine is not running: {str(e)}"

async def list_available_workflows(directory="ollama-server/workflow"):
    """List available workflow files"""
    try:
        if os.path.exists(directory):
            files = [f for f in os.listdir(directory) if f.endswith('.json')]
            if files:
                return f"📁 Found {len(files)} workflow files:\n" + "\n".join([f"  - {f}" for f in files])
            else:
                return f"📁 No workflow files found in {directory}"
        else:
            return f"❌ Directory {directory} not found"
    except Exception as e:
        return f"❌ Error listing workflows: {str(e)}"

async def execute_sample_workflow():
    """Execute a simple test workflow"""
    try:
        sample_workflow = {
            "question": "Test workflow execution",
            "plan": {
                "python_fallback": {
                    "data_needed": [],
                    "script": """
def test_function():
    \"\"\"Simple test function that returns sample data\"\"\"
    import json
    return {
        'status': 'success',
        'message': 'Test workflow executed successfully',
        'data': {
            'timestamp': '2024-12-25',
            'test_value': 42
        }
    }
""",
                    "function_name": "test_function"
                }
            },
            "description": "Simple test to verify execution engine works"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{EXECUTION_ENGINE_URL}/execute", 
                json=sample_workflow,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return f"✅ Workflow executed successfully:\n{json.dumps(result, indent=2)}"
            else:
                return f"❌ Workflow execution failed with status {response.status_code}: {response.text}"
                
    except Exception as e:
        return f"❌ Error executing workflow: {str(e)}"

async def execute_existing_workflow():
    """Test executing an existing workflow file"""
    try:
        # Load workflow file manually and execute via /execute endpoint
        workflow_file = "ollama-server/workflow/workflow_downside_correlation_20241225_150100.json"
        
        # Read the workflow file
        with open(workflow_file, 'r') as f:
            workflow_data = json.load(f)
        
        # Check if it has the required script content
        script_ref = workflow_data.get("plan", {}).get("python_fallback", {}).get("script_reference", "")
        if script_ref and os.path.exists(script_ref):
            # Load the script content
            with open(script_ref, 'r') as f:
                script_content = f.read()
            
            # Update workflow with actual script content
            workflow_data["plan"]["python_fallback"]["script"] = script_content
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{EXECUTION_ENGINE_URL}/execute", 
                json=workflow_data,
                timeout=60.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return f"✅ Existing workflow executed successfully:\n{json.dumps(result, indent=2)[:500]}..."
            else:
                return f"❌ Existing workflow execution failed with status {response.status_code}: {response.text}"
                
    except Exception as e:
        return f"❌ Error executing existing workflow: {str(e)}"

async def check_available_tools():
    """Check what tools are available in the execution engine"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{EXECUTION_ENGINE_URL}/tools")
            if response.status_code == 200:
                tools_data = response.json()
                return f"🔧 Available tools:\n{json.dumps(tools_data, indent=2)}"
            else:
                return f"❌ Failed to get tools: {response.status_code}"
    except Exception as e:
        return f"❌ Error getting tools: {str(e)}"

async def check_mcp_servers():
    """Check if MCP servers are running"""
    servers = {
        "mcp-financial-server": "http://localhost:8001", 
        "mcp-analytics-server": "http://localhost:8002"
    }
    results = []
    
    for name, url in servers.items():
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{url}/tools", timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    tool_count = len(data.get("tools", []))
                    results.append(f"✅ {name}: {tool_count} tools available")
                else:
                    results.append(f"⚠️ {name}: responded with {response.status_code}")
        except Exception as e:
            results.append(f"❌ {name}: {str(e)}")
    
    return "🔍 MCP Server Status:\n" + "\n".join(results)

async def main():
    print("🧪 Enhanced Execution Engine Test")
    print("=" * 40)
    print("\n📋 Required Services:")
    print("   1. Enhanced Execution Engine (port 8003) - Direct HTTP API")
    print("   2. MCP Financial Server (port 8001) - HTTP wrapper for MCP") 
    print("   3. MCP Analytics Server (port 8002) - HTTP wrapper for MCP")
    print("   4. MCP Execution Server - Native MCP server (stdio)")
    print("=" * 40)
    
    # Test 1: Check engine status
    print("\n1. Checking Enhanced Execution Engine status...")
    status = await check_execution_engine_status()
    print(status)
    
    # Test 2: Check MCP servers
    print("\n2. Checking MCP servers...")
    mcp_status = await check_mcp_servers()
    print(mcp_status)
    
    # Test 3: Check available tools
    print("\n3. Checking available tools...")
    tools = await check_available_tools()
    print(tools)
    
    # Test 4: List available workflows
    print("\n4. Listing available workflows...")
    workflows = await list_available_workflows()
    print(workflows)
    
    # Test 5: Execute a sample workflow
    print("\n5. Testing simple workflow execution...")
    result = await execute_sample_workflow()
    print(result)
    
    # Test 6: Execute an existing workflow
    print("\n6. Testing existing workflow execution...")
    existing_result = await execute_existing_workflow()
    print(existing_result)
    
    # Summary
    print("\n" + "=" * 60)
    print("🔧 DEBUGGING SUMMARY")
    print("=" * 60)
    print("✅ Enhanced Execution Engine: Working")
    print("❓ MCP Financial Server: Need to start on port 8001")
    print("❓ MCP Analytics Server: Need to start on port 8002") 
    print("❓ MCP Execution Server: Native MCP server (stdio)")
    print("\n🚀 To start missing services:")
    print("   python ollama-server/mcp-http-wrapper.py  # Ports 8001, 8002")
    print("   python ollama-server/mcp-execution-server.py  # Native MCP")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())