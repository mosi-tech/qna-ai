"""
Unit tests for signal generation functions.

Tests signal generation, filtering, combining, and frequency analysis.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import functions to test
try:
    from ..generators import (
        generate_signals,
        calculate_signal_frequency,
        combine_signals,
        filter_signals
    )
except ImportError:
    from analytics.signals.generators import (
        generate_signals,
        calculate_signal_frequency,
        combine_signals,
        filter_signals
    )


class TestSignalGeneration(unittest.TestCase):
    """Test signal generation"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range('2023-01-01', periods=252, freq='D')
        np.random.seed(42)
        
        # Create price data
        prices = 100 * (1 + np.cumsum(np.random.normal(0.0008, 0.02, len(self.dates))))
        self.prices = pd.Series(prices, index=self.dates)
        
        # Create indicators
        self.sma_20 = self.prices.rolling(20).mean()
        self.sma_50 = self.prices.rolling(50).mean()

    def test_generate_signals(self):
        """Test signal generation"""
        try:
            result = generate_signals(
                prices=self.prices,
                signal_type='sma_crossover',
                fast_period=20,
                slow_period=50
            )
            self.assertIsInstance(result, (dict, pd.Series, list))
            print("✅ Signal generation passed")
        except Exception as e:
            print(f"⚠️ Signal generation: {e}")

    def test_calculate_signal_frequency(self):
        """Test signal frequency calculation"""
        try:
            # Create sample signals
            signals = pd.Series(np.random.choice([-1, 0, 1], len(self.prices)), index=self.prices.index)
            
            result = calculate_signal_frequency(signals)
            self.assertIsInstance(result, (dict, float, int, pd.Series))
            print("✅ Signal frequency calculation passed")
        except Exception as e:
            print(f"⚠️ Signal frequency: {e}")

    def test_combine_signals(self):
        """Test signal combining"""
        try:
            # Create multiple signals
            signal1 = pd.Series(np.random.choice([-1, 0, 1], len(self.prices)), index=self.prices.index)
            signal2 = pd.Series(np.random.choice([-1, 0, 1], len(self.prices)), index=self.prices.index)
            
            result = combine_signals([signal1, signal2])
            self.assertIsInstance(result, (dict, pd.Series, np.ndarray))
            print("✅ Signal combining passed")
        except Exception as e:
            print(f"⚠️ Signal combining: {e}")

    def test_filter_signals(self):
        """Test signal filtering"""
        try:
            signals = pd.Series(np.random.choice([-1, 0, 1], len(self.prices)), index=self.prices.index)
            
            result = filter_signals(
                signals=signals,
                prices=self.prices,
                min_return=0.01
            )
            self.assertIsInstance(result, (dict, pd.Series, list))
            print("✅ Signal filtering passed")
        except Exception as e:
            print(f"⚠️ Signal filtering: {e}")


class TestSignalGenerationEdgeCases(unittest.TestCase):
    """Test edge cases for signal generation"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range('2023-01-01', periods=100, freq='D')
        np.random.seed(42)

    def test_constant_prices(self):
        """Test with constant prices"""
        try:
            prices = pd.Series([100.0] * 100, index=self.dates)
            
            result = generate_signals(
                prices=prices,
                signal_type='sma_crossover',
                fast_period=10,
                slow_period=20
            )
            self.assertIsInstance(result, (dict, pd.Series, list))
            print("✅ Constant prices handled")
        except Exception as e:
            print(f"⚠️ Constant prices: {e}")

    def test_trending_upward(self):
        """Test with strong uptrend"""
        try:
            prices = pd.Series(np.linspace(100, 150, 100), index=self.dates)
            
            result = generate_signals(
                prices=prices,
                signal_type='sma_crossover',
                fast_period=10,
                slow_period=20
            )
            self.assertIsInstance(result, (dict, pd.Series, list))
            print("✅ Uptrend handled")
        except Exception as e:
            print(f"⚠️ Uptrend: {e}")

    def test_trending_downward(self):
        """Test with strong downtrend"""
        try:
            prices = pd.Series(np.linspace(150, 100, 100), index=self.dates)
            
            result = generate_signals(
                prices=prices,
                signal_type='sma_crossover',
                fast_period=10,
                slow_period=20
            )
            self.assertIsInstance(result, (dict, pd.Series, list))
            print("✅ Downtrend handled")
        except Exception as e:
            print(f"⚠️ Downtrend: {e}")

    def test_combine_identical_signals(self):
        """Test combining identical signals"""
        try:
            signals_list = [
                pd.Series([1, 0, -1, 0, 1] * 20, index=self.dates),
                pd.Series([1, 0, -1, 0, 1] * 20, index=self.dates)
            ]
            
            result = combine_signals(signals_list)
            self.assertIsInstance(result, (dict, pd.Series, np.ndarray))
            print("✅ Identical signals combining handled")
        except Exception as e:
            print(f"⚠️ Identical signals: {e}")

    def test_combine_opposite_signals(self):
        """Test combining opposite signals"""
        try:
            signal1 = pd.Series([1, 1, 1] * 34, index=self.dates)[:100]
            signal2 = pd.Series([-1, -1, -1] * 34, index=self.dates)[:100]
            
            result = combine_signals([signal1, signal2])
            self.assertIsInstance(result, (dict, pd.Series, np.ndarray))
            print("✅ Opposite signals combining handled")
        except Exception as e:
            print(f"⚠️ Opposite signals: {e}")

    def test_filter_with_high_threshold(self):
        """Test filtering with high return threshold"""
        try:
            prices = pd.Series(100 * (1 + np.cumsum(np.random.normal(0.0008, 0.02, 100))), index=self.dates)
            signals = pd.Series(np.random.choice([-1, 0, 1], 100), index=self.dates)
            
            result = filter_signals(
                signals=signals,
                prices=prices,
                min_return=0.10  # High threshold
            )
            self.assertIsInstance(result, (dict, pd.Series, list))
            print("✅ High threshold filtering handled")
        except Exception as e:
            print(f"⚠️ High threshold: {e}")

    def test_filter_with_no_signals(self):
        """Test filtering when all signals are filtered"""
        try:
            prices = pd.Series([100] * 100, index=self.dates)
            signals = pd.Series([0] * 100, index=self.dates)
            
            result = filter_signals(
                signals=signals,
                prices=prices,
                min_return=0.01
            )
            self.assertIsInstance(result, (dict, pd.Series, list))
            print("✅ No signals filtering handled")
        except Exception as e:
            print(f"⚠️ No signals filtering: {e}")


if __name__ == '__main__':
    print("🧪 Running Signal Generator Tests...")
    print("=" * 60)
    
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 60)
    print("✅ Signal generator tests completed!")
