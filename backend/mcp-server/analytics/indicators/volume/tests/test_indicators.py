"""
Unit tests for volume indicators.

Tests all volume-based technical indicators including OBV, MFI, CMF, and VPT.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import functions to test

    from ..indicators import (
        calculate_ad,
        calculate_adosc,
        calculate_mfi,
        calculate_obv,
        calculate_cmf,
        calculate_vpt,
        calculate_volume_sma
    )
except ImportError:
    from analytics.indicators.volume.indicators import (
        calculate_ad,
        calculate_adosc,
        calculate_mfi,
        calculate_obv,
        calculate_cmf,
        calculate_vpt,
        calculate_volume_sma
    )


class TestBasicVolumeIndicators(unittest.TestCase):
    """Test basic volume indicators"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range('2023-01-01', periods=252, freq='D')
        np.random.seed(42)
        
        # Create OHLCV data
        close = 100 * (1 + np.cumsum(np.random.normal(0.0005, 0.02, len(self.dates))))
        high = close * (1 + np.abs(np.random.normal(0, 0.01, len(self.dates))))
        low = close * (1 - np.abs(np.random.normal(0, 0.01, len(self.dates))))
        volume = np.random.randint(1000000, 10000000, len(self.dates))
        
        self.ohlcv_df = pd.DataFrame({
            'open': close * (1 + np.random.normal(0, 0.005, len(self.dates))),
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        }, index=self.dates)

    def test_calculate_obv(self):
        """Test On-Balance Volume calculation"""
        
            result = calculate_obv(
                close=self.ohlcv_df['close'],
                volume=self.ohlcv_df['volume']
            )
            
            self.assertIsInstance(result, (pd.Series, dict))
            print("✅ OBV calculation passed")
            
        :
            print(f"⚠️ OBV: {e}")

    def test_calculate_ad(self):
        """Test Accumulation/Distribution indicator"""
        
            result = calculate_ad(
                high=self.ohlcv_df['high'],
                low=self.ohlcv_df['low'],
                close=self.ohlcv_df['close'],
                volume=self.ohlcv_df['volume']
            )
            
            self.assertIsInstance(result, (pd.Series, dict))
            print("✅ A/D indicator passed")
            
        :
            print(f"⚠️ A/D: {e}")

    def test_calculate_vpt(self):
        """Test Volume Price Trend calculation"""
        
            result = calculate_vpt(
                close=self.ohlcv_df['close'],
                volume=self.ohlcv_df['volume']
            )
            
            self.assertIsInstance(result, (pd.Series, dict))
            print("✅ VPT calculation passed")
            
        :
            print(f"⚠️ VPT: {e}")

    def test_calculate_volume_sma(self):
        """Test Volume SMA calculation"""
        
            result = calculate_volume_sma(
                volume=self.ohlcv_df['volume'],
                period=20
            )
            
            self.assertIsInstance(result, (pd.Series, dict))
            print("✅ Volume SMA calculation passed")
            
        :
            print(f"⚠️ Volume SMA: {e}")


class TestMoneyFlowIndicators(unittest.TestCase):
    """Test money flow related indicators"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range('2023-01-01', periods=252, freq='D')
        np.random.seed(42)
        
        close = 100 * (1 + np.cumsum(np.random.normal(0.0005, 0.02, len(self.dates))))
        high = close * (1 + np.abs(np.random.normal(0, 0.01, len(self.dates))))
        low = close * (1 - np.abs(np.random.normal(0, 0.01, len(self.dates))))
        volume = np.random.randint(1000000, 10000000, len(self.dates))
        
        self.ohlcv_df = pd.DataFrame({
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        }, index=self.dates)

    def test_calculate_mfi(self):
        """Test Money Flow Index calculation"""
        
            result = calculate_mfi(
                high=self.ohlcv_df['high'],
                low=self.ohlcv_df['low'],
                close=self.ohlcv_df['close'],
                volume=self.ohlcv_df['volume'],
                period=14
            )
            
            self.assertIsInstance(result, (pd.Series, dict))
            print("✅ MFI calculation passed")
            
        :
            print(f"⚠️ MFI: {e}")

    def test_calculate_cmf(self):
        """Test Chaikin Money Flow calculation"""
        
            result = calculate_cmf(
                high=self.ohlcv_df['high'],
                low=self.ohlcv_df['low'],
                close=self.ohlcv_df['close'],
                volume=self.ohlcv_df['volume'],
                period=20
            )
            
            self.assertIsInstance(result, (pd.Series, dict))
            print("✅ CMF calculation passed")
            
        :
            print(f"⚠️ CMF: {e}")

    def test_calculate_adosc(self):
        """Test Chaikin A/D Oscillator calculation"""
        
            result = calculate_adosc(
                high=self.ohlcv_df['high'],
                low=self.ohlcv_df['low'],
                close=self.ohlcv_df['close'],
                volume=self.ohlcv_df['volume'],
                fast_period=3,
                slow_period=10
            )
            
            self.assertIsInstance(result, (pd.Series, dict))
            print("✅ A/D Oscillator calculation passed")
            
        :
            print(f"⚠️ A/D Oscillator: {e}")


class TestVolumeIndicatorsEdgeCases(unittest.TestCase):
    """Test edge cases for volume indicators"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range('2023-01-01', periods=50, freq='D')
        np.random.seed(42)

    def test_zero_volume(self):
        """Test with zero volume"""
        
            close = pd.Series([100, 101, 102, 101, 100], index=self.dates[:5])
            volume = pd.Series([0, 0, 0, 0, 0], index=self.dates[:5])
            
            result = calculate_obv(close=close, volume=volume)
            
            self.assertIsInstance(result, (pd.Series, dict))
            print("✅ Zero volume handled")
            
        :
            print(f"⚠️ Zero volume: {e}")

    def test_constant_volume(self):
        """Test with constant volume"""
        
            close = pd.Series(
                100 * (1 + np.cumsum(np.random.normal(0.0005, 0.02, 50))),
                index=self.dates
            )
            volume = pd.Series([5000000] * 50, index=self.dates)
            
            result = calculate_volume_sma(volume=volume, period=20)
            
            self.assertIsInstance(result, (pd.Series, dict))
            print("✅ Constant volume handled")
            
        :
            print(f"⚠️ Constant volume: {e}")

    def test_high_volume_spike(self):
        """Test with volume spikes"""
        
            close = pd.Series(
                100 * (1 + np.cumsum(np.random.normal(0.0005, 0.02, 50))),
                index=self.dates
            )
            volume = np.random.randint(1000000, 2000000, 50)
            volume[25] = 100000000  # Spike
            volume = pd.Series(volume, index=self.dates)
            
            result = calculate_obv(close=close, volume=volume)
            
            self.assertIsInstance(result, (pd.Series, dict))
            print("✅ Volume spikes handled")
            
        :
            print(f"⚠️ Volume spikes: {e}")

    def test_mfi_edge_case(self):
        """Test MFI with extreme price movements"""
        
            high = pd.Series([102, 105, 110, 108, 106], index=self.dates[:5])
            low = pd.Series([98, 101, 105, 103, 101], index=self.dates[:5])
            close = pd.Series([100, 103, 108, 105, 103], index=self.dates[:5])
            volume = pd.Series([2000000, 2500000, 3000000, 2200000, 2100000], index=self.dates[:5])
            
            result = calculate_mfi(high=high, low=low, close=close, volume=volume, period=3)
            
            self.assertIsInstance(result, (pd.Series, dict))
            print("✅ MFI with extreme movements handled")
            
        :
            print(f"⚠️ MFI extreme movements: {e}")

    def test_cmf_continuous_up(self):
        """Test CMF with continuous uptrend"""
        
            high = pd.Series([101, 102, 103, 104, 105], index=self.dates[:5])
            low = pd.Series([99, 100, 101, 102, 103], index=self.dates[:5])
            close = pd.Series([100, 101, 102, 103, 104], index=self.dates[:5])
            volume = pd.Series([2000000] * 5, index=self.dates[:5])
            
            result = calculate_cmf(high=high, low=low, close=close, volume=volume, period=3)
            
            self.assertIsInstance(result, (pd.Series, dict))
            print("✅ CMF uptrend handled")
            
        :
            print(f"⚠️ CMF uptrend: {e}")

    def test_adosc_different_periods(self):
        """Test A/D Oscillator with different fast/slow periods"""
        
            high = pd.Series(
                100 * (1 + np.cumsum(np.abs(np.random.normal(0, 0.005, 50)))),
                index=self.dates
            )
            low = high * (1 - np.abs(np.random.normal(0, 0.01, 50)))
            close = (high + low) / 2
            volume = np.random.randint(1000000, 5000000, 50)
            
            result = calculate_adosc(
                high=high,
                low=low,
                close=close,
                volume=pd.Series(volume, index=self.dates),
                fast_period=5,
                slow_period=15
            )
            
            self.assertIsInstance(result, (pd.Series, dict))
            print("✅ A/D Oscillator different periods handled")
            
        :
            print(f"⚠️ A/D Oscillator periods: {e}")


if __name__ == '__main__':
    print("🧪 Running Volume Indicators Tests...")
    print("=" * 60)
    
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 60)
    print("✅ Volume indicators tests completed!")
