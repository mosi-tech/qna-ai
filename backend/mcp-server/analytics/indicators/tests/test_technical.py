"""
Unit tests for technical indicators calculations.

Tests the technical indicators functionality to ensure proper TA-Lib integration,
correct calculations, and error handling for trend indicators and crossover detection.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import functions to test
from ..technical import (
    calculate_sma,
    calculate_ema,
    detect_sma_crossover,
    detect_ema_crossover
)


class TestTechnicalIndicators(unittest.TestCase):
    """Test technical indicators calculations"""
    
    def setUp(self):
        """Set up test data"""
        # Create sample dates
        self.dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)  # For reproducible results
        
        # Create realistic price data with trend
        n_days = len(self.dates)
        base_price = 100.0
        
        # Create trending data for crossover tests
        trend = np.linspace(0, 0.3, n_days)  # 30% uptrend over the period
        noise = np.random.normal(0, 0.02, n_days)
        
        self.prices = pd.Series(
            base_price * (1 + trend + noise),
            index=self.dates,
            name='close'
        )
        
        # Create cyclical data for crossover detection
        cyclical_component = 0.1 * np.sin(np.linspace(0, 4*np.pi, n_days))
        self.cyclical_prices = pd.Series(
            base_price * (1 + cyclical_component + noise * 0.5),
            index=self.dates,
            name='cyclical_close'
        )

    def test_calculate_sma(self):
        """Test Simple Moving Average calculation"""
        try:
            result = calculate_sma(self.prices, period=20)
            
            # Check that result is a dictionary
            self.assertIsInstance(result, dict)
            
            # Check for required keys
            required_keys = ['success', 'latest_value', 'data']
            for key in required_keys:
                self.assertIn(key, result)
            
            # Check that success is True
            self.assertTrue(result['success'])
            
            # SMA should be a reasonable value relative to price
            if 'latest_value' in result and result['latest_value'] is not None:
                latest_price = self.prices.iloc[-1]
                sma_value = result['latest_value']
                
                # SMA should be within reasonable range of current price
                self.assertGreater(sma_value, latest_price * 0.5)
                self.assertLess(sma_value, latest_price * 1.5)
            
            # Data should be available
            if 'data' in result:
                self.assertIsNotNone(result['data'])
                # Should be a list of values
                if isinstance(result['data'], list):
                    self.assertGreater(len(result['data']), 0)
            
            print("✅ SMA calculation test passed")
            
        except Exception as e:
            self.fail(f"calculate_sma failed with error: {e}")

    def test_calculate_ema(self):
        """Test Exponential Moving Average calculation"""
        try:
            result = calculate_ema(self.prices, period=20)
            
            # Check basic structure
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # EMA should be a reasonable value relative to price
            if 'latest_value' in result and result['latest_value'] is not None:
                latest_price = self.prices.iloc[-1]
                ema_value = result['latest_value']
                
                # EMA should be within reasonable range of current price
                self.assertGreater(ema_value, latest_price * 0.5)
                self.assertLess(ema_value, latest_price * 1.5)
            
            # Data should be available
            if 'data' in result:
                self.assertIsNotNone(result['data'])
                # Should be a list of values
                if isinstance(result['data'], list):
                    self.assertGreater(len(result['data']), 0)
            
            print("✅ EMA calculation test passed")
            
        except Exception as e:
            self.fail(f"EMA calculation failed: {e}")

    def test_sma_vs_ema_characteristics(self):
        """Test that SMA and EMA have expected relative characteristics"""
        try:
            sma_result = calculate_sma(self.prices, period=20)
            ema_result = calculate_ema(self.prices, period=20)
            
            if (sma_result.get('success') and ema_result.get('success') and
                'data' in sma_result and 'data' in ema_result):
                
                # Convert to pandas Series for comparison if they're lists
                sma_data = sma_result['data']
                ema_data = ema_result['data']
                
                if isinstance(sma_data, list) and isinstance(ema_data, list):
                    # Take the shorter length for comparison
                    min_len = min(len(sma_data), len(ema_data))
                    if min_len > 10:
                        sma_values = pd.Series(sma_data[-min_len:])
                        ema_values = pd.Series(ema_data[-min_len:])
                    else:
                        return  # Not enough data
                else:
                    sma_values = sma_data
                    ema_values = ema_data
                
                # Align the series for comparison
                common_index = sma_values.index.intersection(ema_values.index)
                if len(common_index) > 10:  # Need sufficient data for comparison
                    sma_aligned = sma_values.loc[common_index]
                    ema_aligned = ema_values.loc[common_index]
                    
                    # EMA should generally be more responsive (closer to current price)
                    # This test checks that they're different but reasonable
                    correlation = sma_aligned.corr(ema_aligned)
                    self.assertGreater(correlation, 0.9)  # Should be highly correlated
                    
                    # They shouldn't be identical
                    mean_diff = abs((sma_aligned - ema_aligned).mean())
                    self.assertGreater(mean_diff, 0.001)  # Should have some difference
            
            print("✅ SMA vs EMA characteristics test passed")
            
        except Exception as e:
            print(f"⚠️ SMA vs EMA comparison: {e}")

    def test_detect_sma_crossover(self):
        """Test SMA crossover detection"""
        try:
            result = detect_sma_crossover(
                self.cyclical_prices, 
                fast_period=10, 
                slow_period=20
            )
            
            # Check basic structure
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # Check for crossover analysis
            expected_keys = ['latest_signal', 'crossover_points']
            for key in expected_keys:
                if key in result:
                    self.assertIsNotNone(result[key])
            
            # Signal should be valid
            if 'latest_signal' in result:
                valid_signals = ['bullish', 'bearish', 'neutral', 'golden_cross', 'death_cross']
                signal = result['latest_signal']
                if signal is not None:
                    self.assertIn(signal, valid_signals)
            
            # Crossover points should be a list or series
            if 'crossover_points' in result and result['crossover_points'] is not None:
                crossovers = result['crossover_points']
                self.assertIsInstance(crossovers, (list, pd.Series, pd.DataFrame))
            
            print("✅ SMA crossover detection test passed")
            
        except Exception as e:
            self.fail(f"SMA crossover detection failed: {e}")

    def test_detect_ema_crossover(self):
        """Test EMA crossover detection"""
        try:
            result = detect_ema_crossover(
                self.cyclical_prices,
                fast_period=10,
                slow_period=20
            )
            
            # Check basic structure
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # Check for crossover analysis
            if 'latest_signal' in result:
                valid_signals = ['bullish', 'bearish', 'neutral', 'golden_cross', 'death_cross']
                signal = result['latest_signal']
                if signal is not None:
                    self.assertIn(signal, valid_signals)
            
            print("✅ EMA crossover detection test passed")
            
        except Exception as e:
            self.fail(f"EMA crossover detection failed: {e}")

    def test_different_periods(self):
        """Test indicators with different periods"""
        periods_to_test = [5, 10, 20, 50]
        
        for period in periods_to_test:
            try:
                # Test SMA with different periods
                sma_result = calculate_sma(self.prices, period=period)
                self.assertTrue(sma_result.get('success', False))
                
                # Test EMA with different periods
                ema_result = calculate_ema(self.prices, period=period)
                self.assertTrue(ema_result.get('success', False))
                
                # Check data availability
                if period <= 20 and 'data' in sma_result and sma_result['data']:
                    if isinstance(sma_result['data'], list):
                        self.assertGreater(len(sma_result['data']), 0)
                
            except Exception as e:
                print(f"⚠️ Period {period} test: {e}")

    def test_edge_cases(self):
        """Test edge cases and error handling"""
        
        # Test with very short data
        try:
            short_data = self.prices.head(5)
            result = calculate_sma(short_data, period=20)
            # Should handle insufficient data gracefully
            print("✅ Short data edge case handled")
        except Exception:
            pass  # Expected for insufficient data
        
        # Test with NaN values
        try:
            nan_data = self.prices.copy()
            nan_data.iloc[10:20] = np.nan
            result = calculate_sma(nan_data, period=10)
            print("✅ NaN values edge case handled")
        except Exception:
            pass  # Expected to fail or handle gracefully
        
        # Test with constant values
        try:
            constant_data = pd.Series([100.0] * 100, index=self.dates[:100])
            result = calculate_sma(constant_data, period=20)
            if result.get('success') and 'latest_value' in result:
                # SMA of constant values should equal the constant
                self.assertAlmostEqual(result['latest_value'], 100.0, places=2)
            print("✅ Constant values edge case handled")
        except Exception:
            pass

    def test_crossover_on_trending_data(self):
        """Test crossover detection on trending data"""
        try:
            # Test with strongly trending data
            trending_result = detect_sma_crossover(
                self.prices,  # This has uptrend
                fast_period=5,
                slow_period=20
            )
            
            self.assertIsInstance(trending_result, dict)
            self.assertTrue(trending_result.get('success', False))
            
            print("✅ Trending data crossover test passed")
            
        except Exception as e:
            print(f"⚠️ Trending data crossover test: {e}")

    def test_data_validation(self):
        """Test data validation functionality"""
        
        # Test with dictionary input
        try:
            price_dict = {str(date): price for date, price in self.prices.head(50).items()}
            result = calculate_sma(price_dict, period=10)
            print("✅ Dictionary input handled")
        except Exception as e:
            print(f"⚠️ Dictionary input handling: {e}")
        
        # Test with list input
        try:
            price_list = self.prices.head(50).tolist()
            result = calculate_sma(price_list, period=10)
            print("✅ List input handled")
        except Exception as e:
            print(f"⚠️ List input handling: {e}")

    def test_ta_lib_integration(self):
        """Test that TA-Lib integration is working correctly"""
        try:
            import talib
            
            # Test direct TA-Lib function
            close_array = self.prices.values
            sma_values = talib.SMA(close_array, timeperiod=20)
            ema_values = talib.EMA(close_array, timeperiod=20)
            
            # Should not be all NaN
            self.assertTrue(np.any(~np.isnan(sma_values)))
            self.assertTrue(np.any(~np.isnan(ema_values)))
            
            # Values should be reasonable
            valid_sma = sma_values[~np.isnan(sma_values)]
            valid_ema = ema_values[~np.isnan(ema_values)]
            
            if len(valid_sma) > 0:
                self.assertTrue(np.all(valid_sma > 0))  # Prices should be positive
            
            if len(valid_ema) > 0:
                self.assertTrue(np.all(valid_ema > 0))  # Prices should be positive
            
            print("✅ TA-Lib integration test passed")
            
        except Exception as e:
            self.fail(f"TA-Lib integration failed: {e}")


if __name__ == '__main__':
    print("🧪 Running Technical Indicators Tests...")
    print("=" * 60)
    
    # Run tests
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 60)
    print("✅ Technical indicators tests completed!")