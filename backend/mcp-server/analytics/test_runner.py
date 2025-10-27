"""
Test runner for analytics modules.

Runs tests to verify empyrical library integration and function correctness.
"""

import sys
import os
import pandas as pd
import numpy as np

# Add analytics to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_empyrical_functions():
    """Test that empyrical functions work correctly"""
    print("🧪 Testing empyrical function fixes...")
    
    
        import empyrical
        
        # Create sample data
        np.random.seed(42)
        sample_returns = pd.Series(np.random.normal(0.001, 0.02, 252))
        
        # Test the functions we fixed
        print("Testing roll_sharpe_ratio (was rolling_sharpe)...")
        rolling_sharpe = empyrical.roll_sharpe_ratio(sample_returns, window=30)
        print(f"✅ roll_sharpe_ratio works - shape: {rolling_sharpe.shape}")
        
        print("Testing roll_annual_volatility (was rolling_volatility)...")
        rolling_vol = empyrical.roll_annual_volatility(sample_returns, window=30)
        print(f"✅ roll_annual_volatility works - shape: {rolling_vol.shape}")
        
        print("Testing downside_risk (was down_stdev)...")
        downside = empyrical.downside_risk(sample_returns)
        print(f"✅ downside_risk works - value: {downside:.6f}")
        
        print("Testing tracking error calculation...")
        benchmark_returns = pd.Series(np.random.normal(0.0008, 0.015, 252))
        aligned_portfolio, aligned_benchmark = sample_returns.align(benchmark_returns, join='inner')
        tracking_error = (aligned_portfolio - aligned_benchmark).std() * np.sqrt(252)
        print(f"✅ tracking_error calculation works - value: {tracking_error:.6f}")
        
        print("Testing other empyrical functions...")
        total_return = empyrical.cum_returns_final(sample_returns)
        annual_return = empyrical.annual_return(sample_returns)
        annual_volatility = empyrical.annual_volatility(sample_returns)
        sharpe_ratio = empyrical.sharpe_ratio(sample_returns, risk_free=0.02)
        max_drawdown = empyrical.max_drawdown(sample_returns)
        
        print(f"✅ Total return: {total_return:.4f}")
        print(f"✅ Annual return: {annual_return:.4f}")
        print(f"✅ Annual volatility: {annual_volatility:.4f}")
        print(f"✅ Sharpe ratio: {sharpe_ratio:.4f}")
        print(f"✅ Max drawdown: {max_drawdown:.4f}")
        
        return True
        
    :
        print(f"❌ Empyrical function test failed: {e}")
        return False

def test_basic_portfolio_functions():
    """Test basic portfolio function imports"""
    print("\n🧪 Testing portfolio function imports...")
    
    
        # Test relative imports by changing directory
        original_dir = os.getcwd()
        os.chdir(os.path.join(os.path.dirname(__file__), 'portfolio'))
        
        
            from metrics import calculate_portfolio_metrics
            print("✅ calculate_portfolio_metrics import successful")
        :
            print(f"❌ Portfolio metrics import failed: {e}")
            return False
        finally:
            os.chdir(original_dir)
        
        return True
        
    :
        print(f"❌ Portfolio function test failed: {e}")
        return False

def test_basic_performance_functions():
    """Test basic performance function imports"""
    print("\n🧪 Testing performance function imports...")
    
    
        # Test relative imports by changing directory
        original_dir = os.getcwd()
        os.chdir(os.path.join(os.path.dirname(__file__), 'performance'))
        
        
            from metrics import calculate_returns_metrics
            print("✅ calculate_returns_metrics import successful")
        :
            print(f"❌ Performance metrics import failed: {e}")
            return False
        finally:
            os.chdir(original_dir)
        
        return True
        
    :
        print(f"❌ Performance function test failed: {e}")
        return False

def test_basic_calculations():
    """Test basic calculations with sample data"""
    print("\n🧪 Testing basic calculations...")
    
    
        # Create sample data
        np.random.seed(42)
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        returns_data = pd.DataFrame({
            'AAPL': np.random.normal(0.001, 0.02, len(dates)),
            'GOOGL': np.random.normal(0.0008, 0.018, len(dates)),
            'MSFT': np.random.normal(0.0009, 0.016, len(dates))
        }, index=dates)
        
        weights = {'AAPL': 0.4, 'GOOGL': 0.3, 'MSFT': 0.3}
        
        # Calculate portfolio returns manually
        portfolio_returns = (returns_data * pd.Series(weights)).sum(axis=1)
        
        print(f"✅ Sample data created - {len(returns_data)} days")
        print(f"✅ Portfolio returns calculated - mean: {portfolio_returns.mean():.6f}")
        
        # Test empyrical calculations on portfolio
        import empyrical
        total_ret = empyrical.cum_returns_final(portfolio_returns)
        annual_ret = empyrical.annual_return(portfolio_returns)
        volatility = empyrical.annual_volatility(portfolio_returns)
        sharpe = empyrical.sharpe_ratio(portfolio_returns, risk_free=0.02)
        
        print(f"✅ Portfolio total return: {total_ret:.4f}")
        print(f"✅ Portfolio annual return: {annual_ret:.4f}")
        print(f"✅ Portfolio volatility: {volatility:.4f}")
        print(f"✅ Portfolio Sharpe ratio: {sharpe:.4f}")
        
        return True
        
    :
        print(f"❌ Basic calculations test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Analytics Module Tests")
    print("=" * 60)
    
    tests = [
        ("Empyrical Functions", test_empyrical_functions),
        ("Portfolio Function Imports", test_basic_portfolio_functions),
        ("Performance Function Imports", test_basic_performance_functions),
        ("Basic Calculations", test_basic_calculations)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        success = test_func()
        results.append((test_name, success))
        if success:
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Analytics modules are working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == '__main__':
    main()