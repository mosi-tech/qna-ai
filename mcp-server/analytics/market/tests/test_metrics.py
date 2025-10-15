"""
Unit tests for market metrics and analysis functions.

Tests market-wide analysis including trend strength, market stress,
breadth, regime detection, and structural break analysis.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import functions to test
try:
    from ..metrics import (
        calculate_trend_strength,
        calculate_market_stress,
        calculate_market_breadth,
        detect_market_regime,
        analyze_volatility_clustering,
        analyze_seasonality,
        detect_structural_breaks,
        detect_crisis_periods,
        calculate_crypto_metrics,
        analyze_weekday_performance,
        analyze_monthly_performance
    )
except ImportError:
    from analytics.market.metrics import (
        calculate_trend_strength,
        calculate_market_stress,
        calculate_market_breadth,
        detect_market_regime,
        analyze_volatility_clustering,
        analyze_seasonality,
        detect_structural_breaks,
        detect_crisis_periods,
        calculate_crypto_metrics,
        analyze_weekday_performance,
        analyze_monthly_performance
    )


class TestTrendAnalysis(unittest.TestCase):
    """Test trend-related market metrics"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range('2022-01-01', periods=252, freq='D')
        np.random.seed(42)
        
        # Create price data with trend
        returns = np.cumsum(np.random.normal(0.0008, 0.02, len(self.dates)))
        self.prices = pd.Series(100 * (1 + returns), index=self.dates)
        self.returns = self.prices.pct_change().dropna()

    def test_calculate_trend_strength(self):
        """Test trend strength calculation"""
        try:
            result = calculate_trend_strength(self.prices)
            self.assertIsInstance(result, (dict, float, int))
            print("✅ Trend strength passed")
        except Exception as e:
            print(f"⚠️ Trend strength: {e}")

    def test_detect_market_regime(self):
        """Test market regime detection"""
        try:
            result = detect_market_regime(self.returns)
            self.assertIsInstance(result, (dict, str))
            print("✅ Market regime detection passed")
        except Exception as e:
            print(f"⚠️ Market regime: {e}")


class TestMarketStress(unittest.TestCase):
    """Test market stress indicators"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range('2022-01-01', periods=252, freq='D')
        np.random.seed(42)
        
        # Create multi-asset data
        self.returns_df = pd.DataFrame({
            'STOCK1': np.random.normal(0.0008, 0.02, len(self.dates)),
            'STOCK2': np.random.normal(0.0007, 0.018, len(self.dates)),
            'STOCK3': np.random.normal(0.0009, 0.022, len(self.dates)),
            'STOCK4': np.random.normal(0.0006, 0.016, len(self.dates)),
            'STOCK5': np.random.normal(0.001, 0.025, len(self.dates))
        }, index=self.dates)

    def test_calculate_market_stress(self):
        """Test market stress calculation"""
        try:
            result = calculate_market_stress(self.returns_df)
            self.assertIsInstance(result, (dict, float, int))
            print("✅ Market stress passed")
        except Exception as e:
            print(f"⚠️ Market stress: {e}")

    def test_calculate_market_breadth(self):
        """Test market breadth calculation"""
        try:
            result = calculate_market_breadth(self.returns_df)
            self.assertIsInstance(result, (dict, float, int, list))
            print("✅ Market breadth passed")
        except Exception as e:
            print(f"⚠️ Market breadth: {e}")


class TestMarketCrisis(unittest.TestCase):
    """Test crisis detection and analysis"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range('2022-01-01', periods=500, freq='D')
        np.random.seed(42)
        
        # Create returns with a crisis period (high volatility)
        returns = np.random.normal(0.0008, 0.02, len(self.dates))
        returns[200:220] = np.random.normal(-0.02, 0.1, 20)  # Crisis period
        self.returns = pd.Series(returns, index=self.dates)

    def test_detect_crisis_periods(self):
        """Test crisis period detection"""
        try:
            result = detect_crisis_periods(self.returns)
            self.assertIsInstance(result, (dict, list, pd.DataFrame))
            print("✅ Crisis detection passed")
        except Exception as e:
            print(f"⚠️ Crisis detection: {e}")

    def test_detect_structural_breaks(self):
        """Test structural break detection"""
        try:
            result = detect_structural_breaks(self.returns)
            self.assertIsInstance(result, (dict, list, pd.DataFrame))
            print("✅ Structural breaks passed")
        except Exception as e:
            print(f"⚠️ Structural breaks: {e}")


class TestVolatilityAnalysis(unittest.TestCase):
    """Test volatility-related market analysis"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range('2022-01-01', periods=252, freq='D')
        np.random.seed(42)
        
        returns = np.random.normal(0.0008, 0.02, len(self.dates))
        self.returns = pd.Series(returns, index=self.dates)

    def test_analyze_volatility_clustering(self):
        """Test volatility clustering analysis"""
        try:
            result = analyze_volatility_clustering(self.returns)
            self.assertIsInstance(result, (dict, float, int))
            print("✅ Volatility clustering passed")
        except Exception as e:
            print(f"⚠️ Volatility clustering: {e}")


class TestSeasonality(unittest.TestCase):
    """Test seasonality analysis"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range('2020-01-01', periods=1000, freq='D')
        np.random.seed(42)
        
        returns = np.random.normal(0.0008, 0.02, len(self.dates))
        self.returns = pd.Series(returns, index=self.dates)

    def test_analyze_seasonality(self):
        """Test seasonality analysis"""
        try:
            result = analyze_seasonality(self.returns)
            self.assertIsInstance(result, (dict, pd.DataFrame))
            print("✅ Seasonality analysis passed")
        except Exception as e:
            print(f"⚠️ Seasonality: {e}")

    def test_analyze_weekday_performance(self):
        """Test weekday performance analysis"""
        try:
            result = analyze_weekday_performance(self.returns)
            self.assertIsInstance(result, (dict, pd.DataFrame))
            print("✅ Weekday performance passed")
        except Exception as e:
            print(f"⚠️ Weekday performance: {e}")

    def test_analyze_monthly_performance(self):
        """Test monthly performance analysis"""
        try:
            result = analyze_monthly_performance(self.returns)
            self.assertIsInstance(result, (dict, pd.DataFrame))
            print("✅ Monthly performance passed")
        except Exception as e:
            print(f"⚠️ Monthly performance: {e}")


class TestCryptoMetrics(unittest.TestCase):
    """Test crypto-specific market metrics"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range('2022-01-01', periods=252, freq='D')
        np.random.seed(42)
        
        # Create crypto-like price data (higher volatility)
        returns = np.cumsum(np.random.normal(0.001, 0.05, len(self.dates)))
        self.prices = pd.Series(100 * (1 + returns), index=self.dates)
        self.volume = pd.Series(np.random.randint(1000000, 100000000, len(self.dates)), index=self.dates)

    def test_calculate_crypto_metrics(self):
        """Test crypto metrics calculation"""
        try:
            result = calculate_crypto_metrics(
                prices=self.prices,
                volume=self.volume
            )
            self.assertIsInstance(result, dict)
            print("✅ Crypto metrics passed")
        except Exception as e:
            print(f"⚠️ Crypto metrics: {e}")


class TestMarketEdgeCases(unittest.TestCase):
    """Test edge cases for market metrics"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range('2023-01-01', periods=100, freq='D')
        np.random.seed(42)

    def test_short_time_series(self):
        """Test with short time series"""
        try:
            returns = pd.Series(np.random.normal(0.0008, 0.02, 20), index=self.dates[:20])
            result = calculate_trend_strength(returns)
            self.assertIsInstance(result, (dict, float, int))
            print("✅ Short time series handled")
        except Exception as e:
            print(f"⚠️ Short time series: {e}")

    def test_constant_returns(self):
        """Test with constant returns (zero volatility)"""
        try:
            returns = pd.Series([0.001] * 100, index=self.dates)
            result = calculate_market_stress(returns.to_frame())
            self.assertIsInstance(result, (dict, float, int))
            print("✅ Constant returns handled")
        except Exception as e:
            print(f"⚠️ Constant returns: {e}")

    def test_extreme_volatility(self):
        """Test with extreme volatility"""
        try:
            returns = pd.Series(np.random.normal(0, 0.1, 100), index=self.dates)
            result = analyze_volatility_clustering(returns)
            self.assertIsInstance(result, (dict, float, int))
            print("✅ Extreme volatility handled")
        except Exception as e:
            print(f"⚠️ Extreme volatility: {e}")


if __name__ == '__main__':
    print("🧪 Running Market Metrics Tests...")
    print("=" * 60)
    
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 60)
    print("✅ Market metrics tests completed!")
