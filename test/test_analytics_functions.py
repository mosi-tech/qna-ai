#!/usr/bin/env python3
"""
Test Analytics Functions and Generate Documentation Examples

This script tests analytics functions with real data and captures
actual outputs to use in documentation examples.
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
import json

# Add mcp-server to path
sys.path.append('/Users/shivc/Documents/Workspace/JS/qna-ai-admin/mcp-server')

def test_calculate_var():
    """Test VaR calculation and capture real output"""
    try:
        from analytics.risk.metrics import calculate_var
        
        # Test data
        returns = pd.Series([0.01, -0.02, 0.015, -0.008, 0.012, -0.005, -0.018])
        
        # Call function
        result = calculate_var(returns, confidence_level=0.05, method="historical")
        
        print("=== calculate_var TEST ===")
        print("Input:")
        print(f"  returns = {returns.tolist()}")
        print(f"  confidence_level = 0.05")
        print(f"  method = 'historical'")
        print()
        print("Output:")
        print(json.dumps(result, indent=2, default=str))
        print()
        
        return True, result
        
    except Exception as e:
        print(f"❌ calculate_var failed: {e}")
        return False, None

def test_calculate_correlation():
    """Test correlation calculation and capture real output"""
    try:
        from analytics.risk.metrics import calculate_correlation
        
        # Test data
        series1 = pd.Series([0.01, -0.02, 0.015, -0.008, 0.012])
        series2 = pd.Series([0.008, -0.015, 0.012, -0.005, 0.009])
        
        # Call function
        result = calculate_correlation(series1, series2)
        
        print("=== calculate_correlation TEST ===")
        print("Input:")
        print(f"  series1 = {series1.tolist()}")
        print(f"  series2 = {series2.tolist()}")
        print()
        print("Output:")
        print(f"  result = {result}")
        print(f"  type = {type(result)}")
        print()
        
        return True, result
        
    except Exception as e:
        print(f"❌ calculate_correlation failed: {e}")
        return False, None

def test_black_scholes_option_price():
    """Test Black-Scholes option pricing and capture real output"""
    try:
        from analytics.risk.models import black_scholes_option_price
        
        # Test data
        underlying_price = 100
        strike = 105
        time_to_expiry = 0.25
        risk_free_rate = 0.05
        volatility = 0.20
        option_type = "call"
        
        # Call function
        result = black_scholes_option_price(
            underlying_price=underlying_price,
            strike=strike,
            time_to_expiry=time_to_expiry,
            risk_free_rate=risk_free_rate,
            volatility=volatility,
            option_type=option_type
        )
        
        print("=== black_scholes_option_price TEST ===")
        print("Input:")
        print(f"  underlying_price = {underlying_price}")
        print(f"  strike = {strike}")
        print(f"  time_to_expiry = {time_to_expiry}")
        print(f"  risk_free_rate = {risk_free_rate}")
        print(f"  volatility = {volatility}")
        print(f"  option_type = '{option_type}'")
        print()
        print("Output:")
        print(json.dumps(result, indent=2, default=str))
        print()
        
        return True, result
        
    except Exception as e:
        print(f"❌ black_scholes_option_price failed: {e}")
        return False, None

def test_prices_to_returns():
    """Test prices to returns conversion and capture real output"""
    try:
        from analytics.utils.data_utils import prices_to_returns
        
        # Test data
        prices = pd.Series([100, 102, 98, 105, 103], 
                          index=pd.date_range('2023-01-01', periods=5))
        
        # Call function
        result = prices_to_returns(prices, method="simple")
        
        print("=== prices_to_returns TEST ===")
        print("Input:")
        print(f"  prices = {prices.tolist()}")
        print(f"  method = 'simple'")
        print()
        print("Output:")
        print(f"  result = {result}")
        print(f"  type = {type(result)}")
        print(f"  values = {result.tolist()}")
        print()
        
        return True, result
        
    except Exception as e:
        print(f"❌ prices_to_returns failed: {e}")
        return False, None

def test_calculate_correlation_analysis():
    """Test correlation analysis and capture real output"""
    try:
        from analytics.risk.metrics import calculate_correlation_analysis
        
        # Test data - multiple return series
        returns_data = pd.DataFrame({
            'AAPL': [0.01, -0.02, 0.015, -0.008, 0.012, -0.005, 0.018],
            'MSFT': [0.008, -0.015, 0.012, -0.005, 0.009, -0.003, 0.020],
            'GOOGL': [0.012, -0.018, 0.010, -0.007, 0.015, -0.008, 0.016]
        })
        
        # Call function
        result = calculate_correlation_analysis(returns_data)
        
        print("=== calculate_correlation_analysis TEST ===")
        print("Input:")
        print(f"  returns_data.shape = {returns_data.shape}")
        print(f"  columns = {list(returns_data.columns)}")
        print()
        print("Output:")
        print(json.dumps(result, indent=2, default=str))
        print()
        
        return True, result
        
    except Exception as e:
        print(f"❌ calculate_correlation_analysis failed: {e}")
        return False, None

def test_calculate_beta_analysis():
    """Test beta analysis and capture real output"""
    try:
        from analytics.risk.metrics import calculate_beta_analysis
        
        # Test data
        asset_returns = pd.Series([0.01, -0.02, 0.015, -0.008, 0.012, -0.005, 0.018])
        market_returns = pd.Series([0.008, -0.018, 0.012, -0.006, 0.010, -0.004, 0.015])
        
        # Call function
        result = calculate_beta_analysis(asset_returns, market_returns)
        
        print("=== calculate_beta_analysis TEST ===")
        print("Input:")
        print(f"  asset_returns = {asset_returns.tolist()}")
        print(f"  market_returns = {market_returns.tolist()}")
        print(f"  risk_free_rate = 0.02 (default)")
        print()
        print("Output:")
        print(json.dumps(result, indent=2, default=str))
        print()
        
        return True, result
        
    except Exception as e:
        print(f"❌ calculate_beta_analysis failed: {e}")
        return False, None

def test_calculate_cvar():
    """Test CVaR calculation and capture real output"""
    try:
        from analytics.risk.metrics import calculate_cvar
        
        # Test data
        returns = pd.Series([0.01, -0.02, 0.015, -0.008, 0.012, -0.005, -0.018, 0.020, -0.025])
        
        # Call function
        result = calculate_cvar(returns, confidence_level=0.05)
        
        print("=== calculate_cvar TEST ===")
        print("Input:")
        print(f"  returns = {returns.tolist()}")
        print(f"  confidence_level = 0.05")
        print()
        print("Output:")
        print(json.dumps(result, indent=2, default=str))
        print()
        
        return True, result
        
    except Exception as e:
        print(f"❌ calculate_cvar failed: {e}")
        return False, None

def test_calculate_skewness():
    """Test skewness calculation and capture real output"""
    try:
        from analytics.risk.metrics import calculate_skewness
        
        # Test data with some skewness
        returns = pd.Series([0.01, -0.02, 0.015, -0.008, 0.012, -0.005, -0.018, 0.025, -0.030, 0.008])
        
        # Call function
        result = calculate_skewness(returns)
        
        print("=== calculate_skewness TEST ===")
        print("Input:")
        print(f"  returns = {returns.tolist()}")
        print()
        print("Output:")
        print(f"  result = {result}")
        print(f"  type = {type(result)}")
        print()
        
        return True, result
        
    except Exception as e:
        print(f"❌ calculate_skewness failed: {e}")
        return False, None

def test_calculate_kurtosis():
    """Test kurtosis calculation and capture real output"""
    try:
        from analytics.risk.metrics import calculate_kurtosis
        
        # Test data
        returns = pd.Series([0.01, -0.02, 0.015, -0.008, 0.012, -0.005, -0.018, 0.025, -0.030, 0.008])
        
        # Call function
        result = calculate_kurtosis(returns)
        
        print("=== calculate_kurtosis TEST ===")
        print("Input:")
        print(f"  returns = {returns.tolist()}")
        print()
        print("Output:")
        print(f"  result = {result}")
        print(f"  type = {type(result)}")
        print()
        
        return True, result
        
    except Exception as e:
        print(f"❌ calculate_kurtosis failed: {e}")
        return False, None

def test_calculate_tail_risk():
    """Test tail risk calculation and capture real output"""
    try:
        from analytics.risk.metrics import calculate_tail_risk
        
        # Test data
        returns = pd.Series([0.01, -0.02, 0.015, -0.008, 0.012, -0.005, -0.018, 0.020, -0.025])
        threshold = -0.015
        
        # Call function
        result = calculate_tail_risk(returns, threshold)
        
        print("=== calculate_tail_risk TEST ===")
        print("Input:")
        print(f"  returns = {returns.tolist()}")
        print(f"  threshold = {threshold}")
        print()
        print("Output:")
        print(json.dumps(result, indent=2, default=str))
        print()
        
        return True, result
        
    except Exception as e:
        print(f"❌ calculate_tail_risk failed: {e}")
        return False, None

def test_calculate_concentration_metrics():
    """Test concentration metrics calculation and capture real output"""
    try:
        from analytics.risk.metrics import calculate_concentration_metrics
        
        # Test data
        weights = pd.Series([0.4, 0.3, 0.2, 0.1], index=['AAPL', 'MSFT', 'GOOGL', 'AMZN'])
        
        # Call function
        result = calculate_concentration_metrics(weights)
        
        print("=== calculate_concentration_metrics TEST ===")
        print("Input:")
        print(f"  weights = {weights.tolist()}")
        print(f"  index = {list(weights.index)}")
        print()
        print("Output:")
        print(json.dumps(result, indent=2, default=str))
        print()
        
        return True, result
        
    except Exception as e:
        print(f"❌ calculate_concentration_metrics failed: {e}")
        return False, None

def test_calculate_portfolio_volatility():
    """Test portfolio volatility calculation and capture real output"""
    try:
        from analytics.risk.metrics import calculate_portfolio_volatility
        
        # Test data
        weights = pd.Series([0.4, 0.3, 0.3], index=['AAPL', 'MSFT', 'GOOGL'])
        volatilities = pd.Series([0.25, 0.22, 0.28], index=['AAPL', 'MSFT', 'GOOGL'])
        correlation_matrix = pd.DataFrame([
            [1.0, 0.7, 0.6],
            [0.7, 1.0, 0.8], 
            [0.6, 0.8, 1.0]
        ], index=['AAPL', 'MSFT', 'GOOGL'], columns=['AAPL', 'MSFT', 'GOOGL'])
        
        # Call function
        result = calculate_portfolio_volatility(weights, correlation_matrix, volatilities)
        
        print("=== calculate_portfolio_volatility TEST ===")
        print("Input:")
        print(f"  weights = {weights.tolist()}")
        print(f"  volatilities = {volatilities.tolist()}")
        print(f"  correlation_matrix shape = {correlation_matrix.shape}")
        print()
        print("Output:")
        print(f"  result = {result}")
        print(f"  type = {type(result)}")
        print()
        
        return True, result
        
    except Exception as e:
        print(f"❌ calculate_portfolio_volatility failed: {e}")
        return False, None

def test_calculate_rolling_volatility():
    """Test rolling volatility calculation and capture real output"""
    try:
        from analytics.risk.metrics import calculate_rolling_volatility
        
        # Test data - longer series for rolling window
        returns = pd.Series([0.01, -0.02, 0.015, -0.008, 0.012, -0.005, -0.018, 0.020, -0.025, 
                           0.008, -0.012, 0.018, -0.007, 0.025, -0.015, 0.010, -0.008, 0.014],
                          index=pd.date_range('2023-01-01', periods=18))
        window = 10
        
        # Call function
        result = calculate_rolling_volatility(returns, window)
        
        print("=== calculate_rolling_volatility TEST ===")
        print("Input:")
        print(f"  returns length = {len(returns)}")
        print(f"  window = {window}")
        print()
        print("Output:")
        print(f"  result = {result}")
        print(f"  type = {type(result)}")
        print(f"  length = {len(result) if hasattr(result, '__len__') else 'N/A'}")
        if hasattr(result, 'tolist'):
            print(f"  values = {result.tolist()}")
        print()
        
        return True, result
        
    except Exception as e:
        print(f"❌ calculate_rolling_volatility failed: {e}")
        return False, None

def test_calculate_downside_deviation():
    """Test downside deviation calculation and capture real output"""
    try:
        from analytics.risk.metrics import calculate_downside_deviation
        
        # Test data
        returns = pd.Series([0.01, -0.02, 0.015, -0.008, 0.012, -0.005, -0.018, 0.020, -0.025])
        target_return = 0.005  # 0.5% target
        
        # Call function
        result = calculate_downside_deviation(returns, target_return)
        
        print("=== calculate_downside_deviation TEST ===")
        print("Input:")
        print(f"  returns = {returns.tolist()}")
        print(f"  target_return = {target_return}")
        print()
        print("Output:")
        print(f"  result = {result}")
        print(f"  type = {type(result)}")
        print()
        
        return True, result
        
    except Exception as e:
        print(f"❌ calculate_downside_deviation failed: {e}")
        return False, None

def test_calculate_portfolio_var():
    """Test portfolio VaR calculation and capture real output"""
    try:
        from analytics.risk.metrics import calculate_portfolio_var
        
        # Test data
        weights = pd.Series([0.4, 0.3, 0.3])
        covariance_matrix = pd.DataFrame([
            [0.04, 0.02, 0.015],
            [0.02, 0.03, 0.018], 
            [0.015, 0.018, 0.05]
        ])
        confidence = 0.05
        
        # Call function
        result = calculate_portfolio_var(weights, covariance_matrix, confidence)
        
        print("=== calculate_portfolio_var TEST ===")
        print("Input:")
        print(f"  weights = {weights.tolist()}")
        print(f"  covariance_matrix shape = {covariance_matrix.shape}")
        print(f"  confidence = {confidence}")
        print()
        print("Output:")
        print(json.dumps(result, indent=2, default=str))
        print()
        
        return True, result
        
    except Exception as e:
        print(f"❌ calculate_portfolio_var failed: {e}")
        return False, None

def test_calculate_expected_shortfall():
    """Test expected shortfall calculation and capture real output"""
    try:
        from analytics.risk.metrics import calculate_expected_shortfall
        
        # Test data
        returns = pd.Series([0.01, -0.02, 0.015, -0.008, 0.012, -0.005, -0.018, 0.020, -0.025])
        confidence = 0.05
        
        # Call function
        result = calculate_expected_shortfall(returns, confidence)
        
        print("=== calculate_expected_shortfall TEST ===")
        print("Input:")
        print(f"  returns = {returns.tolist()}")
        print(f"  confidence = {confidence}")
        print()
        print("Output:")
        print(f"  result = {result}")
        print(f"  type = {type(result)}")
        print()
        
        return True, result
        
    except Exception as e:
        print(f"❌ calculate_expected_shortfall failed: {e}")
        return False, None

def test_calculate_component_var():
    """Test component VaR calculation and capture real output"""
    try:
        from analytics.risk.metrics import calculate_component_var
        
        # Test data
        weights = pd.Series([0.4, 0.3, 0.3])
        returns = pd.DataFrame({
            'AAPL': [0.01, -0.02, 0.015, -0.008, 0.012, -0.005, 0.018],
            'MSFT': [0.008, -0.015, 0.012, -0.005, 0.009, -0.003, 0.020],
            'GOOGL': [0.012, -0.018, 0.010, -0.007, 0.015, -0.008, 0.016]
        })
        confidence = 0.05
        
        # Call function
        result = calculate_component_var(weights, returns, confidence)
        
        print("=== calculate_component_var TEST ===")
        print("Input:")
        print(f"  weights = {weights.tolist()}")
        print(f"  returns shape = {returns.shape}")
        print(f"  confidence = {confidence}")
        print()
        print("Output:")
        print(f"  result = {result}")
        print(f"  type = {type(result)}")
        if hasattr(result, 'tolist'):
            print(f"  values = {result.tolist()}")
        print()
        
        return True, result
        
    except Exception as e:
        print(f"❌ calculate_component_var failed: {e}")
        return False, None

def test_calculate_marginal_var():
    """Test marginal VaR calculation and capture real output"""
    try:
        from analytics.risk.metrics import calculate_marginal_var
        
        # Test data
        weights = pd.Series([0.4, 0.3, 0.3])
        returns = pd.DataFrame({
            'AAPL': [0.01, -0.02, 0.015, -0.008, 0.012, -0.005, 0.018],
            'MSFT': [0.008, -0.015, 0.012, -0.005, 0.009, -0.003, 0.020],
            'GOOGL': [0.012, -0.018, 0.010, -0.007, 0.015, -0.008, 0.016]
        })
        confidence = 0.05
        
        # Call function
        result = calculate_marginal_var(weights, returns, confidence)
        
        print("=== calculate_marginal_var TEST ===")
        print("Input:")
        print(f"  weights = {weights.tolist()}")
        print(f"  returns shape = {returns.shape}")
        print(f"  confidence = {confidence}")
        print()
        print("Output:")
        print(f"  result = {result}")
        print(f"  type = {type(result)}")
        if hasattr(result, 'tolist'):
            print(f"  values = {result.tolist()}")
        print()
        
        return True, result
        
    except Exception as e:
        print(f"❌ calculate_marginal_var failed: {e}")
        return False, None

def test_calculate_beta():
    """Test beta calculation and capture real output"""
    try:
        from analytics.risk.metrics import calculate_beta
        
        # Test data
        stock_returns = pd.Series([0.01, -0.02, 0.015, -0.008, 0.012, -0.005, 0.018])
        market_returns = pd.Series([0.008, -0.018, 0.012, -0.006, 0.010, -0.004, 0.015])
        
        # Call function
        result = calculate_beta(stock_returns, market_returns)
        
        print("=== calculate_beta TEST ===")
        print("Input:")
        print(f"  stock_returns = {stock_returns.tolist()}")
        print(f"  market_returns = {market_returns.tolist()}")
        print()
        print("Output:")
        print(f"  result = {result}")
        print(f"  type = {type(result)}")
        print()
        
        return True, result
        
    except Exception as e:
        print(f"❌ calculate_beta failed: {e}")
        return False, None

def test_calculate_correlation_matrix():
    """Test correlation matrix calculation and capture real output"""
    try:
        from analytics.risk.metrics import calculate_correlation_matrix
        
        # Test data - list of series
        series_array = [
            pd.Series([0.01, -0.02, 0.015, -0.008, 0.012]),
            pd.Series([0.008, -0.015, 0.012, -0.005, 0.009]),
            pd.Series([0.012, -0.018, 0.010, -0.007, 0.015])
        ]
        
        # Call function
        result = calculate_correlation_matrix(series_array)
        
        print("=== calculate_correlation_matrix TEST ===")
        print("Input:")
        print(f"  series_array length = {len(series_array)}")
        print(f"  series shapes = {[len(s) for s in series_array]}")
        print()
        print("Output:")
        print(f"  result = {result}")
        print(f"  type = {type(result)}")
        print(f"  shape = {result.shape}")
        print()
        
        return True, result
        
    except Exception as e:
        print(f"❌ calculate_correlation_matrix failed: {e}")
        return False, None

def test_calculate_percentile():
    """Test percentile calculation and capture real output"""
    try:
        from analytics.risk.metrics import calculate_percentile
        
        # Test data
        data = pd.DataFrame({
            'open': [100, 102, 98, 105, 103],
            'high': [101, 104, 100, 107, 105],
            'low': [99, 100, 96, 103, 101],
            'close': [100.5, 103.0, 99.0, 106.0, 104.0],
            'volume': [1000, 1200, 800, 1500, 1100]
        })
        percentile = 0.05
        
        # Call function
        result = calculate_percentile(data, percentile)
        
        print("=== calculate_percentile TEST ===")
        print("Input:")
        print(f"  data shape = {data.shape}")
        print(f"  percentile = {percentile}")
        print()
        print("Output:")
        print(f"  result = {result}")
        print(f"  type = {type(result)}")
        print()
        
        return True, result
        
    except Exception as e:
        print(f"❌ calculate_percentile failed: {e}")
        return False, None

def test_calculate_herfindahl_index():
    """Test Herfindahl index calculation and capture real output"""
    try:
        from analytics.risk.metrics import calculate_herfindahl_index
        
        # Test data
        weights = pd.Series([0.4, 0.3, 0.3])
        
        # Call function
        result = calculate_herfindahl_index(weights)
        
        print("=== calculate_herfindahl_index TEST ===")
        print("Input:")
        print(f"  weights = {weights.tolist()}")
        print()
        print("Output:")
        print(f"  result = {result}")
        print(f"  type = {type(result)}")
        print()
        
        return True, result
        
    except Exception as e:
        print(f"❌ calculate_herfindahl_index failed: {e}")
        return False, None

def test_calculate_treynor_ratio():
    """Test Treynor ratio calculation and capture real output"""
    try:
        from analytics.risk.metrics import calculate_treynor_ratio
        
        # Test data
        returns = pd.Series([0.01, -0.02, 0.015, -0.008, 0.012, -0.005, -0.018, 0.020, -0.025])
        market_returns = pd.Series([0.008, -0.018, 0.012, -0.006, 0.010, -0.004, -0.015, 0.018, -0.022])
        
        # Call function
        result = calculate_treynor_ratio(returns, market_returns)
        
        print("=== calculate_treynor_ratio TEST ===")
        print("Input:")
        print(f"  returns = {returns.tolist()}")
        print(f"  market_returns = {market_returns.tolist()}")
        print(f"  risk_free_rate = 0.02 (default)")
        print()
        print("Output:")
        print(f"  result = {result}")
        print(f"  type = {type(result)}")
        print()
        
        return True, result
        
    except Exception as e:
        print(f"❌ calculate_treynor_ratio failed: {e}")
        return False, None

def test_calculate_downside_correlation():
    """Test downside correlation calculation and capture real output"""
    try:
        from analytics.risk.metrics import calculate_downside_correlation
        
        # Test data
        portfolio_returns = pd.Series([0.01, -0.02, 0.015, -0.008, 0.012, -0.005, -0.018, 0.020, -0.025])
        benchmark_returns = pd.Series([0.008, -0.018, 0.012, -0.006, 0.010, -0.004, -0.015, 0.018, -0.022])
        
        # Call function
        result = calculate_downside_correlation(portfolio_returns, benchmark_returns)
        
        print("=== calculate_downside_correlation TEST ===")
        print("Input:")
        print(f"  portfolio_returns = {portfolio_returns.tolist()}")
        print(f"  benchmark_returns = {benchmark_returns.tolist()}")
        print()
        print("Output:")
        print(json.dumps(result, indent=2, default=str))
        print()
        
        return True, result
        
    except Exception as e:
        print(f"❌ calculate_downside_correlation failed: {e}")
        return False, None

def test_compare_performance_metrics():
    """Test performance metrics comparison and capture real output"""
    try:
        from analytics.comparison.metrics import compare_performance_metrics
        
        # Test data
        returns1 = pd.Series([0.01, -0.02, 0.015, -0.008, 0.012, -0.005, -0.018, 0.02, -0.025])
        returns2 = pd.Series([0.008, -0.018, 0.012, -0.006, 0.01, -0.004, -0.015, 0.018, -0.022])
        
        # Call function
        result = compare_performance_metrics(returns1, returns2)
        
        print("=== compare_performance_metrics TEST ===")
        print("Input:")
        print(f"  returns1 = {returns1.tolist()}")
        print(f"  returns2 = {returns2.tolist()}")
        print()
        print("Output:")
        print(json.dumps(result, indent=2, default=str))
        print()
        
        return True, result
        
    except Exception as e:
        print(f"❌ compare_performance_metrics failed: {e}")
        return False, None

def main():
    """Run all tests and generate documentation examples"""
    print("🧪 TESTING ANALYTICS FUNCTIONS")
    print("=" * 50)
    print()
    
    tests = [
        test_calculate_var,
        test_calculate_correlation,
        test_black_scholes_option_price,
        test_prices_to_returns,
        test_calculate_correlation_analysis,
        test_calculate_beta_analysis,
        test_calculate_cvar,
        test_calculate_skewness,
        test_calculate_kurtosis,
        test_calculate_tail_risk,
        test_calculate_concentration_metrics,
        test_calculate_portfolio_volatility,
        test_calculate_rolling_volatility,
        test_calculate_downside_deviation,
        test_calculate_portfolio_var,
        test_calculate_expected_shortfall,
        test_calculate_component_var,
        test_calculate_marginal_var,
        test_calculate_beta,
        test_calculate_correlation_matrix,
        test_calculate_percentile,
        test_calculate_herfindahl_index,
        test_calculate_treynor_ratio,
        test_calculate_downside_correlation,
        test_compare_performance_metrics
    ]
    
    results = {}
    for test_func in tests:
        success, result = test_func()
        results[test_func.__name__] = {"success": success, "result": result}
    
    # Summary
    print("📊 TEST SUMMARY")
    print("=" * 50)
    total_tests = len(tests)
    passed_tests = sum(1 for r in results.values() if r["success"])
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result["success"] else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    print()
    print(f"Total: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Use these results for documentation.")
    else:
        print("⚠️ Some tests failed. Fix functions before updating docs.")

if __name__ == "__main__":
    main()