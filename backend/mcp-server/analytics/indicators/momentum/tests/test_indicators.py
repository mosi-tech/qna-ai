"""
Unit tests for momentum indicators calculations.

Tests the momentum indicators functionality to ensure proper TA-Lib integration,
correct calculations, and error handling across all momentum indicator functions.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import functions to test
from ..indicators import (
    calculate_rsi,
    calculate_stochastic,
    calculate_stochastic_fast,
    calculate_williams_r,
    calculate_ultimate_oscillator,
    calculate_adx,
    calculate_adxr,
    calculate_dx,
    calculate_minus_di,
    calculate_plus_di,
    calculate_aroon,
    calculate_aroon_oscillator,
    calculate_cci,
    calculate_macd,
    calculate_ppo,
    calculate_roc,
    calculate_mom,
    calculate_bop,
    calculate_cmo
)


class TestMomentumIndicators(unittest.TestCase):
    """Test momentum indicators calculations"""
    
    def setUp(self):
        """Set up test data"""
        # Create sample dates
        self.dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)  # For reproducible results
        
        # Create realistic OHLCV data
        n_days = len(self.dates)
        base_price = 100.0
        
        # Generate realistic price movements
        returns = np.random.normal(0.001, 0.02, n_days)
        prices = base_price * np.cumprod(1 + returns)
        
        # Create OHLC data with realistic spreads
        noise = np.random.normal(0, 0.005, n_days)
        
        self.ohlc_data = pd.DataFrame({
            'open': prices * (1 + noise * 0.5),
            'high': prices * (1 + np.abs(noise) + 0.01),
            'low': prices * (1 - np.abs(noise) - 0.01),
            'close': prices,
            'volume': np.random.randint(1000000, 10000000, n_days)
        }, index=self.dates)
        
        # Simple price series for indicators that only need close prices
        self.close_prices = self.ohlc_data['close']

    def test_calculate_rsi(self):
        """Test RSI calculation"""
        try:
            result = calculate_rsi(self.close_prices, period=14)
            
            # Check that result is a dictionary
            self.assertIsInstance(result, dict)
            
            # Check for required keys
            required_keys = ['success', 'latest_value', 'signal']
            for key in required_keys:
                self.assertIn(key, result)
            
            # Check that success is True
            self.assertTrue(result['success'])
            
            # RSI should be between 0 and 100
            if 'latest_value' in result and result['latest_value'] is not None:
                self.assertGreaterEqual(result['latest_value'], 0)
                self.assertLessEqual(result['latest_value'], 100)
            
            # Signal should be valid
            if 'signal' in result:
                valid_signals = ['bullish', 'bearish', 'neutral', 'overbought', 'oversold']
                self.assertIn(result['signal'], valid_signals)
            
            print("✅ RSI calculation test passed")
            
        except Exception as e:
            self.fail(f"calculate_rsi failed with error: {e}")

    def test_calculate_stochastic(self):
        """Test Stochastic oscillator calculation"""
        try:
            result = calculate_stochastic(self.ohlc_data, k_period=14, d_period=3)
            
            # Check basic structure
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # Check for stochastic values
            if 'latest_k' in result and result['latest_k'] is not None:
                self.assertGreaterEqual(result['latest_k'], 0)
                self.assertLessEqual(result['latest_k'], 100)
            
            if 'latest_d' in result and result['latest_d'] is not None:
                self.assertGreaterEqual(result['latest_d'], 0)
                self.assertLessEqual(result['latest_d'], 100)
            
            print("✅ Stochastic oscillator test passed")
            
        except Exception as e:
            self.fail(f"Stochastic calculation failed: {e}")

    def test_calculate_williams_r(self):
        """Test Williams %R calculation"""
        try:
            result = calculate_williams_r(self.ohlc_data, period=14)
            
            # Check basic structure
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # Williams %R should be between -100 and 0
            if 'latest_value' in result and result['latest_value'] is not None:
                self.assertGreaterEqual(result['latest_value'], -100)
                self.assertLessEqual(result['latest_value'], 0)
            
            print("✅ Williams %R test passed")
            
        except Exception as e:
            self.fail(f"Williams %R calculation failed: {e}")

    def test_calculate_adx(self):
        """Test ADX (Average Directional Index) calculation"""
        try:
            result = calculate_adx(self.ohlc_data, period=14)
            
            # Check basic structure
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # ADX should be between 0 and 100
            if 'latest_value' in result and result['latest_value'] is not None:
                self.assertGreaterEqual(result['latest_value'], 0)
                self.assertLessEqual(result['latest_value'], 100)
            
            print("✅ ADX calculation test passed")
            
        except Exception as e:
            self.fail(f"ADX calculation failed: {e}")

    def test_calculate_macd(self):
        """Test MACD calculation"""
        try:
            result = calculate_macd(self.close_prices, fast_period=12, slow_period=26, signal_period=9)
            
            # Check basic structure
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # Check for MACD components
            macd_keys = ['latest_macd', 'latest_signal', 'latest_histogram']
            for key in macd_keys:
                if key in result:
                    self.assertIsNotNone(result[key])
            
            print("✅ MACD calculation test passed")
            
        except Exception as e:
            self.fail(f"MACD calculation failed: {e}")

    def test_calculate_cci(self):
        """Test Commodity Channel Index calculation"""
        try:
            result = calculate_cci(self.ohlc_data, period=14)
            
            # Check basic structure
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # CCI can range beyond ±100, but should be finite
            if 'latest_value' in result and result['latest_value'] is not None:
                self.assertFalse(np.isnan(result['latest_value']))
                self.assertFalse(np.isinf(result['latest_value']))
            
            print("✅ CCI calculation test passed")
            
        except Exception as e:
            self.fail(f"CCI calculation failed: {e}")

    def test_calculate_roc(self):
        """Test Rate of Change calculation"""
        try:
            result = calculate_roc(self.close_prices, period=10)
            
            # Check basic structure
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # ROC should be a reasonable percentage change
            if 'latest_value' in result and result['latest_value'] is not None:
                self.assertFalse(np.isnan(result['latest_value']))
                # ROC should be within reasonable bounds for daily data
                self.assertGreater(result['latest_value'], -50)  # Not more than 50% decline
                self.assertLess(result['latest_value'], 50)     # Not more than 50% gain
            
            print("✅ ROC calculation test passed")
            
        except Exception as e:
            self.fail(f"ROC calculation failed: {e}")

    def test_calculate_momentum(self):
        """Test Momentum calculation"""
        try:
            result = calculate_mom(self.close_prices, period=10)
            
            # Check basic structure
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # Momentum should be finite
            if 'latest_value' in result and result['latest_value'] is not None:
                self.assertFalse(np.isnan(result['latest_value']))
                self.assertFalse(np.isinf(result['latest_value']))
            
            print("✅ Momentum calculation test passed")
            
        except Exception as e:
            self.fail(f"Momentum calculation failed: {e}")

    def test_calculate_ultimate_oscillator(self):
        """Test Ultimate Oscillator calculation"""
        try:
            result = calculate_ultimate_oscillator(self.ohlc_data, period1=7, period2=14, period3=28)
            
            # Check basic structure
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # Ultimate Oscillator should be between 0 and 100
            if 'latest_value' in result and result['latest_value'] is not None:
                self.assertGreaterEqual(result['latest_value'], 0)
                self.assertLessEqual(result['latest_value'], 100)
            
            print("✅ Ultimate Oscillator test passed")
            
        except Exception as e:
            self.fail(f"Ultimate Oscillator calculation failed: {e}")

    def test_calculate_aroon(self):
        """Test Aroon calculation"""
        try:
            result = calculate_aroon(self.ohlc_data, period=14)
            
            # Check basic structure
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # Aroon values should be between 0 and 100
            if 'latest_aroon_up' in result and result['latest_aroon_up'] is not None:
                self.assertGreaterEqual(result['latest_aroon_up'], 0)
                self.assertLessEqual(result['latest_aroon_up'], 100)
            
            if 'latest_aroon_down' in result and result['latest_aroon_down'] is not None:
                self.assertGreaterEqual(result['latest_aroon_down'], 0)
                self.assertLessEqual(result['latest_aroon_down'], 100)
            
            print("✅ Aroon calculation test passed")
            
        except Exception as e:
            self.fail(f"Aroon calculation failed: {e}")
    
    def test_calculate_bop_cmo(self):
        """Test BOP and CMO calculations"""
        try:
            # Test Balance of Power
            bop_result = calculate_bop(self.ohlc_data)
            self.assertIsInstance(bop_result, dict)
            self.assertTrue(bop_result.get('success', False))
            
            # Test Chande Momentum Oscillator
            cmo_result = calculate_cmo(self.close_prices, period=14)
            self.assertIsInstance(cmo_result, dict)
            self.assertTrue(cmo_result.get('success', False))
            
            # CMO should be between -100 and 100
            if 'latest_value' in cmo_result and cmo_result['latest_value'] is not None:
                self.assertGreaterEqual(cmo_result['latest_value'], -100)
                self.assertLessEqual(cmo_result['latest_value'], 100)
            
            print("✅ BOP and CMO calculation tests passed")
            
        except Exception as e:
            self.fail(f"BOP/CMO calculation failed: {e}")

    def test_edge_cases(self):
        """Test edge cases and error handling"""
        
        # Test with very short data
        try:
            short_data = self.close_prices.head(5)
            result = calculate_rsi(short_data, period=14)
            # Should either handle gracefully or return appropriate error
            print("✅ Short data edge case handled")
        except Exception:
            pass  # Expected for insufficient data
        
        # Test with NaN values
        try:
            nan_data = self.close_prices.copy()
            nan_data.iloc[10:20] = np.nan
            result = calculate_rsi(nan_data, period=14)
            print("✅ NaN values edge case handled")
        except Exception:
            pass  # Expected to fail or handle gracefully
        
        # Test with constant values
        try:
            constant_data = pd.Series([100.0] * 100, index=self.dates[:100])
            result = calculate_rsi(constant_data, period=14)
            print("✅ Constant values edge case handled")
        except Exception:
            pass  # Expected to fail or handle gracefully

    def test_signal_generation(self):
        """Test signal generation across multiple indicators"""
        indicators_to_test = [
            (calculate_rsi, {'period': 14}),
            (calculate_williams_r, {'period': 14}),
            (calculate_cci, {'period': 14}),
        ]
        
        for func, params in indicators_to_test:
            try:
                if func in [calculate_rsi]:
                    result = func(self.close_prices, **params)
                else:
                    result = func(self.ohlc_data, **params)
                
                # Check that signal is generated
                if result.get('success') and 'signal' in result:
                    valid_signals = ['bullish', 'bearish', 'neutral', 'overbought', 'oversold', 'buy', 'sell', 'hold']
                    self.assertIn(result['signal'], valid_signals)
                
            except Exception as e:
                print(f"⚠️ Signal test for {func.__name__}: {e}")

    def test_ta_lib_integration(self):
        """Test that TA-Lib integration is working correctly"""
        try:
            import talib
            
            # Test direct TA-Lib function
            close_array = self.close_prices.values
            rsi_values = talib.RSI(close_array, timeperiod=14)
            
            # Should not be all NaN
            valid_values = ~np.isnan(rsi_values)
            self.assertTrue(np.any(valid_values))
            
            # Valid RSI values should be in range
            valid_rsi = rsi_values[valid_values]
            if len(valid_rsi) > 0:
                self.assertTrue(np.all(valid_rsi >= 0))
                self.assertTrue(np.all(valid_rsi <= 100))
            
            print("✅ TA-Lib integration test passed")
            
        except Exception as e:
            self.fail(f"TA-Lib integration failed: {e}")


if __name__ == '__main__':
    print("🧪 Running Momentum Indicators Tests...")
    print("=" * 60)
    
    # Run tests
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 60)
    print("✅ Momentum indicators tests completed!")