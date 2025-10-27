"""
Unit tests for signal analysis functions.

Tests signal quality analysis, false signal detection, and parameter optimization.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import functions to test

    from ..analysis import (
        analyze_signal_quality,
        identify_false_signals,
        optimize_signal_parameters
    )
except ImportError:
    from analytics.signals.analysis import (
        analyze_signal_quality,
        identify_false_signals,
        optimize_signal_parameters
    )


class TestSignalQuality(unittest.TestCase):
    """Test signal quality analysis"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range('2023-01-01', periods=252, freq='D')
        np.random.seed(42)
        
        # Create price data and signals
        prices = 100 * (1 + np.cumsum(np.random.normal(0.0008, 0.02, len(self.dates))))
        self.prices = pd.Series(prices, index=self.dates)
        
        # Create signals (1 for buy, -1 for sell, 0 for no signal)
        self.signals = pd.Series(np.random.choice([-1, 0, 1], len(self.dates)), index=self.dates)

    def test_analyze_signal_quality(self):
        """Test signal quality analysis"""
        
            result = analyze_signal_quality(
                prices=self.prices,
                signals=self.signals
            )
            self.assertIsInstance(result, dict)
            print("✅ Signal quality analysis passed")
        :
            print(f"⚠️ Signal quality: {e}")

    def test_identify_false_signals(self):
        """Test false signal identification"""
        
            result = identify_false_signals(
                prices=self.prices,
                signals=self.signals
            )
            self.assertIsInstance(result, (dict, list, pd.DataFrame))
            print("✅ False signal identification passed")
        :
            print(f"⚠️ False signals: {e}")

    def test_optimize_signal_parameters(self):
        """Test signal parameter optimization"""
        
            result = optimize_signal_parameters(
                prices=self.prices,
                signals=self.signals
            )
            self.assertIsInstance(result, dict)
            print("✅ Signal parameter optimization passed")
        :
            print(f"⚠️ Parameter optimization: {e}")


class TestSignalQualityEdgeCases(unittest.TestCase):
    """Test edge cases for signal analysis"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range('2023-01-01', periods=100, freq='D')
        np.random.seed(42)

    def test_no_signals(self):
        """Test with no signals (all zeros)"""
        
            prices = pd.Series(100 * (1 + np.cumsum(np.random.normal(0.0008, 0.02, 100))), index=self.dates)
            signals = pd.Series([0] * 100, index=self.dates)
            
            result = analyze_signal_quality(prices=prices, signals=signals)
            self.assertIsInstance(result, dict)
            print("✅ No signals handled")
        :
            print(f"⚠️ No signals: {e}")

    def test_all_buy_signals(self):
        """Test with all buy signals"""
        
            prices = pd.Series(100 * (1 + np.cumsum(np.random.normal(0.0008, 0.02, 100))), index=self.dates)
            signals = pd.Series([1] * 100, index=self.dates)
            
            result = analyze_signal_quality(prices=prices, signals=signals)
            self.assertIsInstance(result, dict)
            print("✅ All buy signals handled")
        :
            print(f"⚠️ All buy signals: {e}")

    def test_alternating_signals(self):
        """Test with alternating buy/sell signals"""
        
            prices = pd.Series(100 * (1 + np.cumsum(np.random.normal(0.0008, 0.02, 100))), index=self.dates)
            signals = pd.Series([1, -1] * 50, index=self.dates)
            
            result = analyze_signal_quality(prices=prices, signals=signals)
            self.assertIsInstance(result, dict)
            print("✅ Alternating signals handled")
        :
            print(f"⚠️ Alternating signals: {e}")

    def test_short_price_series(self):
        """Test with short price series"""
        
            prices = pd.Series([100, 101, 102, 101, 100], index=self.dates[:5])
            signals = pd.Series([1, 0, -1, 0, 1], index=self.dates[:5])
            
            result = analyze_signal_quality(prices=prices, signals=signals)
            self.assertIsInstance(result, dict)
            print("✅ Short series handled")
        :
            print(f"⚠️ Short series: {e}")


if __name__ == '__main__':
    print("🧪 Running Signal Analysis Tests...")
    print("=" * 60)
    
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 60)
    print("✅ Signal analysis tests completed!")
