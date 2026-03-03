#!/usr/bin/env python3
"""
Test Script for Shared ResultFormatter

Tests the same shared ResultFormatter functionality used by worker.py
to verify markdown generation works correctly.

Usage:
    python test_result_formatter.py

Make sure to set up your .env file with LLM configuration first.
"""

import asyncio
import logging
import os
import sys

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add shared module to path
shared_path = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, shared_path)

# Import the same shared formatter used by worker.py
from shared.services.result_formatter import create_shared_result_formatter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("result-formatter-test")


def create_sample_execution_result():
    """Create sample execution result data for testing"""
    return {
        "response_type": "Stock Volatility Analysis",
        "results": {
            "top_volatile_stocks": [
                {"symbol": "TSLA", "volatility": 0.045, "price": 234.56},
                {"symbol": "NVDA", "volatility": 0.038, "price": 456.78},
                {"symbol": "AMD", "volatility": 0.035, "price": 123.45}
            ],
            "market_summary": {
                "avg_volatility": 0.028,
                "total_stocks_analyzed": 500,
                "market_trend": "bullish"
            },
            "risk_metrics": {
                "portfolio_var": 0.032,
                "sharpe_ratio": 1.45,
                "max_drawdown": 0.18
            },
            "timestamp": "2024-10-31T15:30:00Z"
        }
    }


def create_sample_execution_result_simple():
    """Create simple execution result for basic testing"""
    return {
        "results": {
            "aapl_price": 180.50,
            "daily_return": 0.025,
            "volume": 45_000_000,
            "rsi": 68.5,
            "moving_avg_20": 175.30
        }
    }


async def test_result_formatter():
    """Test the shared ResultFormatter exactly like worker.py uses it"""
    
    print("🧪 Testing Shared ResultFormatter")
    print("=" * 50)
    
    try:
        # Step 1: Create shared result formatter (same as worker.py)
        print("📦 Creating shared result formatter...")
        result_formatter = create_shared_result_formatter()
        print(f"✅ Created formatter using LLM: {result_formatter.llm_service.config.provider_type}/{result_formatter.llm_service.config.default_model}")
        
        # Step 2: Test with sample data
        print("\n📊 Testing with sample financial data...")
        execution_result = create_sample_execution_result()
        user_question = "What are the most volatile stocks in the market today?"
        
        # Step 3: Generate markdown (same call as worker.py)
        print("🤖 Generating markdown...")
        markdown = await result_formatter.format_execution_result(
            execution_result, 
            user_question
        )
        
        # Step 4: Display results
        if markdown:
            print("✅ Markdown generation successful!")
            print("\n" + "="*60)
            print("GENERATED MARKDOWN:")
            print("="*60)
            print(markdown)
            print("="*60)
            
            # Save to file for inspection
            output_file = "test_result_output.md"
            with open(output_file, 'w') as f:
                f.write(f"# ResultFormatter Test Output\n\n")
                f.write(f"**Question:** {user_question}\n\n")
                f.write(f"**Generated Markdown:**\n\n")
                f.write(markdown)
            
            print(f"\n💾 Saved output to: {output_file}")
            
        else:
            print("❌ Markdown generation failed!")
            return False
            
        # Step 5: Test with simpler data
        print("\n📊 Testing with simple data...")
        simple_result = create_sample_execution_result_simple()
        simple_question = "What is AAPL's current price and performance?"
        
        markdown_simple = await result_formatter.format_execution_result(
            simple_result,
            simple_question
        )
        
        if markdown_simple:
            print("✅ Simple test successful!")
            print("\nSimple Markdown Preview:")
            print("-" * 40)
            print(markdown_simple[:200] + "..." if len(markdown_simple) > 200 else markdown_simple)
            print("-" * 40)
        else:
            print("⚠️ Simple test failed")
            
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_configuration():
    """Test LLM configuration loading"""
    print("\n🔧 Testing LLM Configuration")
    print("=" * 30)
    
    try:
        from shared.llm.utils import LLMConfig
        
        # Test RESULT_FORMATTER specific config
        config = LLMConfig.for_task("RESULT_FORMATTER")
        print(f"Provider: {config.provider_type}")
        print(f"Model: {config.default_model}")
        print(f"API Key: {'*' * 10}...{config.api_key[-4:] if config.api_key and len(config.api_key) > 4 else 'Not Set'}")
        print(f"Temperature: {config.temperature}")
        
        return config.api_key is not None
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def print_usage():
    """Print usage instructions"""
    print("📋 ResultFormatter Test Setup:")
    print("-" * 30)
    print("1. Set your API key in .env file:")
    print("   RESULT_FORMATTER_LLM_API_KEY=your-key-here")
    print("   or")
    print("   ANTHROPIC_API_KEY=your-key-here")
    print("")
    print("2. Run the test:")
    print("   python test_result_formatter.py")
    print("")


async def main():
    """Main test function"""
    print("🚀 ResultFormatter Test Suite")
    print("="*50)
    
    # Test configuration first
    config_ok = await test_configuration()
    if not config_ok:
        print("\n⚠️ Configuration issue detected. Please check your .env file.")
        print_usage()
        return
    
    # Run formatter tests
    success = await test_result_formatter()
    
    print("\n" + "="*50)
    if success:
        print("🎉 All tests passed! ResultFormatter is working correctly.")
        print("✅ The same shared formatter used by worker.py is functioning properly.")
    else:
        print("❌ Tests failed. Check the error messages above.")
        print("💡 Make sure your API key is correctly set in .env")
    print("="*50)


if __name__ == "__main__":
    # Check for python-dotenv
    try:
        from dotenv import load_dotenv
    except ImportError:
        print("❌ Missing python-dotenv. Install with: pip install python-dotenv")
        sys.exit(1)
    
    # Run tests
    asyncio.run(main())