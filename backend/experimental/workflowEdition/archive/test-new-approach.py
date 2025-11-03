#!/usr/bin/env python3
"""
Test script to demonstrate the new MCP orchestration approach
vs the old approach of listing all functions in system prompt
"""

import asyncio
import json
import httpx

class SystemPromptComparison:
    def __init__(self):
        self.ollama_server_url = "http://localhost:8000"
        
    async def test_analysis(self, question: str):
        """Test the new approach with a sample financial question"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.ollama_server_url}/analyze",
                    json={
                        "question": question,
                        "model": "gpt-oss:20b"
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result
                else:
                    return {"error": f"HTTP {response.status_code}: {response.text}"}
                    
        except Exception as e:
            return {"error": str(e)}
    
    def print_comparison(self):
        """Print comparison between old and new approaches"""
        print("=" * 60)
        print("SYSTEM PROMPT APPROACH COMPARISON")
        print("=" * 60)
        
        print("\n🔴 OLD APPROACH:")
        print("- System prompt loads base prompt from file")
        print("- Discovers ALL MCP tools from servers (HTTP calls to /tools)")
        print("- Lists every function with descriptions and parameters")
        print("- Creates very long enhanced system prompt")
        print("- High token usage for system prompt")
        print("- Static list of functions in prompt")
        
        print("\n🟢 NEW APPROACH:")
        print("- System prompt contains MCP orchestration guidance") 
        print("- Describes server capabilities and function categories")
        print("- No specific function listing in prompt")
        print("- LLM learns to use realistic MCP function names")
        print("- Much shorter system prompt, lower token usage")
        print("- Dynamic orchestration based on question analysis")
        
        print("\n📊 BENEFITS OF NEW APPROACH:")
        print("- Reduced token usage (shorter system prompts)")
        print("- More flexible - doesn't need to list all functions upfront")
        print("- Better scalability as more MCP tools are added")
        print("- LLM learns patterns instead of memorizing function lists")
        print("- Still validates against actual MCP servers when needed")

    async def run_test(self):
        """Run test with sample questions"""
        self.print_comparison()
        
        print("\n" + "=" * 60)
        print("TESTING NEW APPROACH")
        print("=" * 60)
        
        test_questions = [
            "What are the top 5 most active stocks today?",
            "Calculate the 20-day moving average for AAPL",
            "Show me the RSI indicator for Tesla stock", 
            "What's the portfolio risk for equal weights in AAPL, GOOGL, MSFT?",
            "Get me the latest cryptocurrency prices",  # Should trigger validation error - no crypto functions
            "Show me the weather forecast for trading",  # Should trigger validation error - no weather functions
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n📝 TEST {i}: {question}")
            print("-" * 50)
            
            result = await self.test_analysis(question)
            
            if result.get("success"):
                data = result.get("data", {})
                
                # Print key metrics
                print(f"✅ Success: {result['success']}")
                
                # Extract tool call info from body
                for item in data.get("body", []):
                    key = item.get("key")
                    value = item.get("value")
                    
                    if key == "mcp_validation":
                        validation_passed = value.get("validation_passed", False)
                        valid_count = len(value.get("valid_functions", []))
                        invalid_functions = value.get("invalid_functions", [])
                        print(f"✅ MCP Validation: {'PASSED' if validation_passed else 'FAILED'}")
                        print(f"   Valid functions: {valid_count}")
                        if invalid_functions:
                            print(f"   ❌ Invalid functions: {', '.join(invalid_functions)}")
                    elif key == "tool_calls_planned":
                        print(f"🔧 Tool calls planned: {value}")
                    elif key == "dsl_response":
                        steps = value.get("steps", [])
                        print(f"📋 DSL steps generated: {len(steps)}")
                        for j, step in enumerate(steps, 1):
                            fn = step.get("fn", "unknown")
                            args = step.get("args", {})
                            print(f"   {j}. {fn}({', '.join(f'{k}={v}' for k, v in args.items())})")
                    elif key == "tool_calls":
                        planned_calls = value.get("planned_tool_calls", [])
                        for j, call in enumerate(planned_calls, 1):
                            tool_name = call.get("tool_name", "unknown")
                            valid_mcp = call.get("valid_mcp", False)
                            status_icon = "✅" if valid_mcp else "❌"
                            print(f"   {status_icon} {tool_name} ({'valid' if valid_mcp else 'invalid'})")
                            
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
                
            print()

async def main():
    """Main test function"""
    tester = SystemPromptComparison()
    await tester.run_test()

if __name__ == "__main__":
    print("🧪 Testing New MCP Orchestration Approach")
    print("Make sure the following are running:")
    print("1. ollama serve")
    print("2. ollama pull llama3.2")
    print("3. python ollama-server.py (this server)")
    print("4. MCP servers (financial + analytics)")
    print()
    
    asyncio.run(main())