#!/usr/bin/env python3
"""
Test script to verify Claude Code CLI response parsing flow
Shows how the response flows from CLI -> anthropic.py -> analysis_simplified.py -> routes.py
"""

import json
from typing import Dict, Any

def simulate_claude_cli_raw_response():
    """Simulate the raw Claude Code CLI response (array format)"""
    return [
        {
            "type": "message",
            "content": "Some intermediate response"
        },
        {
            "type": "tool_call", 
            "content": "Tool execution details"
        },
        {
            "type": "final_result",
            "result": '```json\n{\n  "script_generation": {\n    "status": "success",\n    "script_name": "conditional_buy_strategy_analysis_20251010_224636_gojd.py",\n    "validation_attempts": 2,\n    "analysis_description": "Analyzes a conditional buy strategy: investing monthly in QQQ, but switching to VOO when rolling 7-day returns drop below -3%. Compares strategy performance against buy-and-hold QQQ benchmark.",\n    "execution": {\n      "script_name": "conditional_buy_strategy_analysis_20251010_224636_gojd.py",\n      "parameters": {\n        "source_symbol": "QQQ",\n        "target_symbol": "VOO",\n        "analysis_period_days": 730,\n        "rolling_window_days": 7,\n        "return_threshold": -0.03,\n        "monthly_investment": 1000\n      }\n    }\n  }\n}\n```',
            "usage": {
                "input_tokens": 1500,
                "output_tokens": 500
            }
        }
    ]

def simulate_anthropic_provider_parsing(response_data):
    """Simulate the parsing in _call_claude_code_cli"""
    print("🔧 Step 1: Raw Claude CLI response")
    print(f"Response type: {type(response_data)}")
    print(f"Response length: {len(response_data)}")
    print()
    
    # Handle response_data as array - last element contains the result
    if isinstance(response_data, list) and len(response_data) > 0:
        # Get the last element which contains the result
        last_element = response_data[-1]
        print("🔧 Step 2: Extract last element")
        print(f"Last element: {json.dumps(last_element, indent=2)}")
        print()
        
        # Extract the result field which is stringified JSON - return as-is
        if isinstance(last_element, dict) and "result" in last_element:
            output_text = last_element["result"]  # Return stringified JSON as-is
            print("🔧 Step 3: Extract result field (stringified JSON)")
            print(f"output_text type: {type(output_text)}")
            print(f"output_text content: {repr(output_text)}")
            print()
        else:
            output_text = json.dumps(last_element, indent=2)
    else:
        output_text = response_data.get("output", json.dumps(response_data, indent=2))
    
    # Convert CLI response to provider format
    provider_response = {
        "success": True,
        "data": {
            "content": [{"type": "text", "text": output_text}],
            "claude_code_result": response_data,
            "usage": response_data[-1].get("usage", {}) if isinstance(response_data, list) and len(response_data) > 0 else {}
        },
        "provider": "anthropic-cli"
    }
    
    print("🔧 Step 4: Provider response format")
    print(f"Provider response keys: {provider_response.keys()}")
    print(f"Content: {provider_response['data']['content'][0]['text'][:100]}...")
    print()
    
    return provider_response

def simulate_llm_service_processing(provider_response):
    """Simulate how LLMService.make_request processes the provider response"""
    print("🔧 Step 5: LLM Service processing")
    
    # Extract content from provider response (similar to parse_response)
    content_blocks = provider_response["data"].get("content", [])
    text_content = ""
    
    for block in content_blocks:
        if isinstance(block, dict) and block.get("type") == "text":
            text_content += block.get("text", "")
        elif isinstance(block, str):
            text_content += block
    
    llm_result = {
        "success": True,
        "content": text_content,
        "provider": provider_response["provider"],
        "usage": provider_response["data"].get("usage", {})
    }
    
    print(f"LLM result keys: {llm_result.keys()}")
    print(f"Content type: {type(llm_result['content'])}")
    print(f"Content preview: {llm_result['content'][:100]}...")
    print()
    
    return llm_result

def simulate_analysis_simplified_processing(llm_result, question, model):
    """Simulate analysis_simplified.py analyze_question method"""
    print("🔧 Step 6: Analysis Simplified processing")
    
    if llm_result.get("success"):
        # Format the successful response based on new standardized format
        response_data = {
            "question": question,
            "provider": llm_result["provider"],
            "model": model,
            "response_type": llm_result.get("response_type"),
            "raw_content": llm_result.get("raw_content", ""),
            "timestamp": "2024-10-11T10:30:00Z"  # Mock timestamp
        }
        
        # Add completion information
        if llm_result.get("task_completed"):
            response_data["task_completed"] = llm_result["task_completed"]
        
        # Always use consistent key structure regardless of response type
        response_data["analysis_result"] = llm_result.get("data", {})
        
        analysis_result = {
            "success": True,
            "data": response_data
        }
    else:
        analysis_result = {
            "success": False,
            "error": llm_result.get("error", "Unknown error"),
            "provider": llm_result.get("provider", "unknown"),
            "timestamp": "2024-10-11T10:30:00Z"
        }
    
    print(f"Analysis result keys: {analysis_result.keys()}")
    if analysis_result["success"]:
        print(f"Data keys: {analysis_result['data'].keys()}")
        print(f"Raw content preview: {analysis_result['data']['raw_content'][:100]}...")
    print()
    
    return analysis_result

def simulate_routes_py_processing(analysis_result):
    """Simulate what happens in routes.py at line 89"""
    print("🔧 Step 7: Routes.py processing (line 89)")
    
    # This is what the 'result' variable looks like in routes.py
    print("=" * 60)
    print("FINAL RESULT in routes.py (line 89):")
    print("=" * 60)
    print(json.dumps(analysis_result, indent=2))
    print()
    
    # Show how to access the actual JSON content
    if analysis_result["success"]:
        raw_content = analysis_result["data"]["raw_content"]
        print("🔍 How to extract the actual JSON from raw_content:")
        print(f"Raw content type: {type(raw_content)}")
        
        # This is how you'd parse the JSON from the markdown code block
        if raw_content.startswith("```json\n") and raw_content.endswith("\n```"):
            json_content = raw_content[8:-4]  # Remove ```json\n and \n```
            try:
                parsed_json = json.loads(json_content)
                print("✅ Successfully parsed JSON:")
                print(json.dumps(parsed_json, indent=2))
                
                # Show how to access specific fields
                if "script_generation" in parsed_json:
                    script_info = parsed_json["script_generation"]
                    print(f"\n📝 Script name: {script_info.get('script_name')}")
                    print(f"📝 Status: {script_info.get('status')}")
                    print(f"📝 Description: {script_info.get('analysis_description')}")
                    
                    if "execution" in script_info:
                        execution = script_info["execution"]
                        print(f"📝 Parameters: {json.dumps(execution.get('parameters', {}), indent=2)}")
                
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON: {e}")
        else:
            print("⚠️ Content is not in expected markdown JSON format")

def main():
    """Run the complete test flow"""
    print("🧪 Testing Claude Code CLI Response Parsing Flow")
    print("=" * 60)
    
    # Simulate the complete flow
    question = "What is the best conditional buy strategy for QQQ vs VOO?"
    model = "claude-3-5-haiku-20241022"
    
    # Step 1: Raw CLI response
    raw_response = simulate_claude_cli_raw_response()
    
    # Step 2: Anthropic provider parsing
    provider_response = simulate_anthropic_provider_parsing(raw_response)
    
    # Step 3: LLM service processing
    llm_result = simulate_llm_service_processing(provider_response)
    
    # Step 4: Analysis simplified processing
    analysis_result = simulate_analysis_simplified_processing(llm_result, question, model)
    
    # Step 5: Routes.py final result
    simulate_routes_py_processing(analysis_result)

if __name__ == "__main__":
    main()