#!/usr/bin/env python3
"""
Test script for retail analysis tools
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.tier_1_information import current_price_stats, company_profile
import json

def test_current_price_stats():
    """Test the current_price_stats function"""
    print("Testing current_price_stats function...")
    
    try:
        result = current_price_stats("AAPL")
        
        print("✅ Function executed successfully")
        print("📊 Result structure:")
        print(json.dumps(result, indent=2, default=str))
        
        # Validate result structure
        assert "symbol" in result
        assert "analytics_metrics" in result
        assert "current_price" in result
        assert "mcp_functions_used" in result
        assert result["symbol"] == "AAPL"
        assert "success" in result
        assert result["success"] == True
        assert result["current_price"] == 150.25
        assert "52_week_range" in result["analytics_metrics"]
        assert "volatility_metrics" in result["analytics_metrics"]
        assert "trend_metrics" in result["analytics_metrics"]
        
        print("✅ All structure validations passed")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_company_profile():
    """Test the company_profile function"""
    print("\nTesting company_profile function...")
    
    try:
        result = company_profile("MSFT")
        
        print("✅ Function executed successfully")
        print("📊 Result structure:")
        print(json.dumps(result, indent=2, default=str))
        
        # Validate result structure
        assert "symbol" in result
        assert result["symbol"] == "MSFT"
        assert "success" in result
        
        print("✅ All structure validations passed")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing Retail Analysis Tools")
    print("=" * 50)
    
    success_count = 0
    total_tests = 2
    
    if test_current_price_stats():
        success_count += 1
    
    if test_company_profile():
        success_count += 1
    
    print("=" * 50)
    print(f"📈 Test Results: {success_count}/{total_tests} passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)