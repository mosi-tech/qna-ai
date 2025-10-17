#!/usr/bin/env python3
"""
Test the simplified analysis service with Claude Code CLI
"""

import asyncio
import sys
import os

# Add the API server path
sys.path.append('/Users/shivc/Documents/Workspace/JS/qna-ai-admin/ollama-server/scriptEdition/apiServer')

from services.analysis import AnalysisService

async def test_simplified_analysis():
    """Test the simplified analysis service"""
    
    print("🔧 Initializing simplified analysis service...")
    
    # Initialize the simplified service
    analysis_service = AnalysisService()
    
    # Test with a financial question
    question = "What is the correlation between AAPL and MSFT over the last 30 days?"
    
    print(f"🤔 Analyzing question: {question}")
    
    try:
        result = await analysis_service.analyze_question(
            question=question,
            model="claude-3-5-sonnet-20241022"
        )
        
        if result["success"]:
            print("✅ Analysis successful!")
            
            data = result["data"]
            print(f"Provider: {data.get('provider')}")
            print(f"Response Type: {data.get('response_type')}")
            
            analysis_result = data.get("analysis_result", {})
            content = analysis_result.get("content", "")
            
            print(f"\n📊 Analysis Result:")
            print(f"Script Generated: {analysis_result.get('script_generated', False)}")
            print(f"Script Path: {analysis_result.get('script_path', 'N/A')}")
            print(f"Execution Successful: {analysis_result.get('execution_successful', False)}")
            
            print(f"\n💬 Response Content:")
            print(content[:500] + "..." if len(content) > 500 else content)
            
        else:
            print(f"❌ Analysis failed: {result.get('data', {}).get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    asyncio.run(test_simplified_analysis())