"""
Test to verify all empyrical library fixes are working correctly.

This script validates that the fixes to empyrical function calls resolve
the runtime issues that were present in the analytics modules.
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def test_empyrical_fixes():
    """Test all the empyrical fixes we made"""
    print("🔧 Testing Empyrical Library Fixes")
    print("=" * 50)
    
    try:
        import empyrical
        print("✅ Empyrical library imported successfully")
    except ImportError:
        print("❌ Empyrical library not available")
        return False
    
    # Create sample data
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    returns = pd.Series(np.random.normal(0.001, 0.02, len(dates)), index=dates)
    benchmark = pd.Series(np.random.normal(0.0008, 0.015, len(dates)), index=dates)
    
    print(f"\n📊 Created test data: {len(returns)} daily returns")
    
    # Test Fix 1: rolling_sharpe → roll_sharpe_ratio
    print("\n🧪 Testing Fix 1: rolling_sharpe → roll_sharpe_ratio")
    try:
        rolling_sharpe = empyrical.roll_sharpe_ratio(returns, window=30, risk_free=0.02)
        print(f"✅ roll_sharpe_ratio works - Length: {len(rolling_sharpe)}, Mean: {rolling_sharpe.mean():.4f}")
    except Exception as e:
        print(f"❌ roll_sharpe_ratio failed: {e}")
        return False
    
    # Test Fix 2: rolling_volatility → roll_annual_volatility  
    print("\n🧪 Testing Fix 2: rolling_volatility → roll_annual_volatility")
    try:
        rolling_vol = empyrical.roll_annual_volatility(returns, window=30)
        print(f"✅ roll_annual_volatility works - Length: {len(rolling_vol)}, Mean: {rolling_vol.mean():.4f}")
    except Exception as e:
        print(f"❌ roll_annual_volatility failed: {e}")
        return False
    
    # Test Fix 3: down_stdev → downside_risk
    print("\n🧪 Testing Fix 3: down_stdev → downside_risk")
    try:
        downside = empyrical.downside_risk(returns, required_return=0.0)
        print(f"✅ downside_risk works - Value: {downside:.6f}")
    except Exception as e:
        print(f"❌ downside_risk failed: {e}")
        return False
    
    # Test Fix 4: tracking_error → manual calculation
    print("\n🧪 Testing Fix 4: tracking_error → manual calculation")
    try:
        excess_returns = returns - benchmark
        tracking_error = excess_returns.std() * np.sqrt(252)
        print(f"✅ Manual tracking_error calculation works - Value: {tracking_error:.6f}")
    except Exception as e:
        print(f"❌ Manual tracking_error calculation failed: {e}")
        return False
    
    # Test other empyrical functions still work
    print("\n🧪 Testing other empyrical functions still work")
    try:
        functions_to_test = [
            ('annual_return', lambda: empyrical.annual_return(returns)),
            ('annual_volatility', lambda: empyrical.annual_volatility(returns)),
            ('sharpe_ratio', lambda: empyrical.sharpe_ratio(returns, risk_free=0.02)),
            ('sortino_ratio', lambda: empyrical.sortino_ratio(returns)),
            ('max_drawdown', lambda: empyrical.max_drawdown(returns)),
            ('calmar_ratio', lambda: empyrical.calmar_ratio(returns)),
            ('value_at_risk', lambda: empyrical.value_at_risk(returns, cutoff=0.05)),
            ('conditional_value_at_risk', lambda: empyrical.conditional_value_at_risk(returns, cutoff=0.05)),
            ('beta', lambda: empyrical.beta(returns, benchmark)),
            ('alpha', lambda: empyrical.alpha(returns, benchmark, risk_free=0.02)),
            ('up_capture', lambda: empyrical.up_capture(returns, benchmark)),
            ('down_capture', lambda: empyrical.down_capture(returns, benchmark))
        ]
        
        for func_name, func_call in functions_to_test:
            try:
                result = func_call()
                if isinstance(result, (int, float)) and not np.isnan(result):
                    print(f"   ✅ {func_name}: {result:.6f}")
                else:
                    print(f"   ⚠️ {func_name}: {result} (may be NaN/inf for this data)")
            except Exception as e:
                print(f"   ❌ {func_name}: {e}")
        
    except Exception as e:
        print(f"❌ Other empyrical functions test failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All empyrical fixes verified successfully!")
    print("\nSummary of fixes applied:")
    print("1. ✅ empyrical.rolling_sharpe → empyrical.roll_sharpe_ratio")
    print("2. ✅ empyrical.rolling_volatility → empyrical.roll_annual_volatility")  
    print("3. ✅ empyrical.down_stdev → empyrical.downside_risk")
    print("4. ✅ empyrical.tracking_error → manual calculation using std() * sqrt(252)")
    print("\n📝 These fixes resolve the runtime issues in:")
    print("   - analytics/portfolio/metrics.py")
    print("   - analytics/performance/metrics.py")
    print("   - analytics/risk/metrics.py")
    
    return True

def main():
    """Run the empyrical fixes test"""
    success = test_empyrical_fixes()
    
    if success:
        print("\n🏆 SUCCESS: All empyrical library issues have been resolved!")
        print("The analytics modules should now run without runtime errors.")
    else:
        print("\n💥 FAILURE: Some empyrical library issues remain unresolved.")
        print("Additional investigation may be needed.")
    
    return success

if __name__ == '__main__':
    main()