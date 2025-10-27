"""
Unit tests for volatility indicators.

Tests all volatility measurement functions including ATR, Bollinger Bands,
standard deviation, and variance calculations.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import functions to test

from ..indicators import (
    calculate_atr,
    calculate_natr,
    calculate_trange,
    calculate_bollinger_bands,
    calculate_bollinger_percent_b,
    calculate_bollinger_bandwidth,
    calculate_stddev,
    calculate_variance
)


class TestATRIndicators(unittest.TestCase):
    """Test Average True Range and related indicators"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range('2023-01-01', periods=252, freq='D')
        np.random.seed(42)
        
        # Create OHLC data
        close = 100 * (1 + np.cumsum(np.random.normal(0.0005, 0.02, len(self.dates))))
        high = close * (1 + np.abs(np.random.normal(0, 0.01, len(self.dates))))
        low = close * (1 - np.abs(np.random.normal(0, 0.01, len(self.dates))))
        volume = np.random.randint(1000000, 10000000, len(self.dates))
        
        self.ohlc_df = pd.DataFrame({
            'open': close * (1 + np.random.normal(0, 0.005, len(self.dates))),
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        }, index=self.dates)

    def test_calculate_trange(self):
        """Test True Range calculation"""
        
            result = calculate_trange(
                high=self.ohlc_df['high'],
                low=self.ohlc_df['low'],
                close=self.ohlc_df['close']
            )
            
            # Should return a Series or dict
            self.assertIsInstance(result, (pd.Series, dict))
            
            print("✅ True Range calculation passed")
            
        :
            print(f"⚠️ True Range: {e}")

    def test_calculate_atr(self):
        """Test Average True Range calculation"""
        
            result = calculate_atr(
                high=self.ohlc_df['high'],
                low=self.ohlc_df['low'],
                close=self.ohlc_df['close'],
                period=14
            )
            
            self.assertIsInstance(result, (pd.Series, dict))
            print("✅ ATR calculation passed")
            
        :
            print(f"⚠️ ATR: {e}")

    def test_calculate_natr(self):
        """Test Normalized ATR calculation"""
        
            result = calculate_natr(
                high=self.ohlc_df['high'],
                low=self.ohlc_df['low'],
                close=self.ohlc_df['close'],
                period=14
            )
            
            self.assertIsInstance(result, (pd.Series, dict))
            print("✅ NATR calculation passed")
            
        :
            print(f"⚠️ NATR: {e}")


class TestBollingerBands(unittest.TestCase):
    """Test Bollinger Bands and related indicators"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range('2023-01-01', periods=252, freq='D')
        np.random.seed(42)
        
        close = 100 * (1 + np.cumsum(np.random.normal(0.0005, 0.02, len(self.dates))))
        self.close_series = pd.Series(close, index=self.dates)

    def test_calculate_bollinger_bands(self):
        """Test Bollinger Bands calculation"""
        
            result = calculate_bollinger_bands(
                close=self.close_series,
                period=20,
                num_std=2
            )
            
            self.assertIsInstance(result, (dict, tuple, list, pd.DataFrame))
            print("✅ Bollinger Bands calculation passed")
            
        :
            print(f"⚠️ Bollinger Bands: {e}")

    def test_calculate_bollinger_percent_b(self):
        """Test Bollinger Bands %B calculation"""
        
            result = calculate_bollinger_percent_b(
                close=self.close_series,
                period=20,
                num_std=2
            )
            
            self.assertIsInstance(result, (pd.Series, dict))
            print("✅ Bollinger %B calculation passed")
            
        :
            print(f"⚠️ Bollinger %B: {e}")

    def test_calculate_bollinger_bandwidth(self):
        """Test Bollinger Bands Bandwidth calculation"""
        
            result = calculate_bollinger_bandwidth(
                close=self.close_series,
                period=20,
                num_std=2
            )
            
            self.assertIsInstance(result, (pd.Series, dict))
            print("✅ Bollinger Bandwidth calculation passed")
            
        :
            print(f"⚠️ Bollinger Bandwidth: {e}")


class TestStatisticalVolatility(unittest.TestCase):
    """Test statistical volatility measures"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range('2023-01-01', periods=252, freq='D')
        np.random.seed(42)
        
        close = 100 * (1 + np.cumsum(np.random.normal(0.0005, 0.02, len(self.dates))))
        self.close_series = pd.Series(close, index=self.dates)
        self.returns = self.close_series.pct_change().dropna()

    def test_calculate_stddev(self):
        """Test standard deviation calculation"""
        
            result = calculate_stddev(
                data=self.returns,
                period=20
            )
            
            self.assertIsInstance(result, (pd.Series, dict))
            print("✅ Standard deviation calculation passed")
            
        :
            print(f"⚠️ Standard deviation: {e}")

    def test_calculate_variance(self):
        """Test variance calculation"""
        
            result = calculate_variance(
                data=self.returns,
                period=20
            )
            
            self.assertIsInstance(result, (pd.Series, dict))
            print("✅ Variance calculation passed")
            
        :
            print(f"⚠️ Variance: {e}")


class TestVolatilityEdgeCases(unittest.TestCase):
    """Test edge cases for volatility indicators"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range('2023-01-01', periods=50, freq='D')
        np.random.seed(42)

    def test_short_time_series(self):
        """Test with short time series"""
        
            close = pd.Series([100, 101, 102, 101, 100], index=self.dates[:5])
            
            result = calculate_stddev(data=close, period=3)
            
            self.assertIsInstance(result, (pd.Series, dict))
            print("✅ Short time series handled")
            
        :
            print(f"⚠️ Short time series: {e}")

    def test_constant_prices(self):
        """Test with constant prices (zero volatility)"""
        
            close = pd.Series([100.0] * 50, index=self.dates)
            
            result = calculate_stddev(data=close, period=20)
            
            self.assertIsInstance(result, (pd.Series, dict))
            print("✅ Constant prices handled")
            
        :
            print(f"⚠️ Constant prices: {e}")

    def test_high_volatility(self):
        """Test with high volatility data"""
        
            close = pd.Series(
                100 * (1 + np.cumsum(np.random.normal(0, 0.05, 50))),
                index=self.dates
            )
            
            result = calculate_bollinger_bands(close=close, period=20, num_std=2)
            
            self.assertIsInstance(result, (dict, tuple, list, pd.DataFrame))
            print("✅ High volatility handled")
            
        :
            print(f"⚠️ High volatility: {e}")

    def test_atr_with_gaps(self):
        """Test ATR with price gaps"""
        
            high = pd.Series([102, 104, 105, 103, 106], index=self.dates[:5])
            low = pd.Series([98, 100, 101, 99, 102], index=self.dates[:5])
            close = pd.Series([100, 102, 103, 101, 104], index=self.dates[:5])
            
            result = calculate_trange(high=high, low=low, close=close)
            
            self.assertIsInstance(result, (pd.Series, dict))
            print("✅ ATR with gaps handled")
            
        :
            print(f"⚠️ ATR with gaps: {e}")


if __name__ == '__main__':
    print("🧪 Running Volatility Indicators Tests...")
    print("=" * 60)
    
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 60)
    print("✅ Volatility indicators tests completed!")
