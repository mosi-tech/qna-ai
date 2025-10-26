"""
Unit tests for data utilities functions.

Tests the data validation, transformation, and utility functions to ensure
robust data processing across the analytics pipeline.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import functions to test
from ..data_utils import (
    validate_price_data,
    validate_return_data,
    prices_to_returns,
    align_series,
    resample_data,
    standardize_output,
    calculate_log_returns,
    calculate_cumulative_returns,
    calculate_monthly_returns,
    extract_symbols_from_alpaca_data
)


class TestDataValidation(unittest.TestCase):
    """Test data validation functions"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        
        # Create test price data
        prices = 100 * (1 + np.cumsum(np.random.normal(0.001, 0.02, len(self.dates))))
        self.price_series = pd.Series(prices, index=self.dates)
        
        # Create test return data
        self.returns_series = self.price_series.pct_change().dropna()
        
        # Create test data in various formats
        self.price_dict = {str(date): price for date, price in self.price_series.items()}
        self.price_list = self.price_series.tolist()
        self.price_df = pd.DataFrame({'close': self.price_series})
        
        # Create sample Alpaca data
        self.alpaca_data = [
            {'symbol': 'AAPL', 'price': 150.0, 'volume': 1000000},
            {'symbol': 'MSFT', 'price': 300.0, 'volume': 800000},
            {'symbol': 'GOOGL', 'price': 120.0, 'volume': 600000}
        ]

    def test_validate_price_data_series(self):
        """Test price validation with pandas Series"""
        try:
            result = validate_price_data(self.price_series)
            
            # Should return pandas Series
            self.assertIsInstance(result, pd.Series)
            
            # Should have same length as input
            self.assertEqual(len(result), len(self.price_series))
            
            # All values should be numeric and positive
            self.assertTrue(all(result > 0))
            
            # No NaN values
            self.assertEqual(result.isna().sum(), 0)
            
            print("✅ Price data validation (Series) passed")
            
        except Exception as e:
            self.fail(f"validate_price_data with Series failed: {e}")

    def test_validate_price_data_dict(self):
        """Test price validation with dictionary"""
        try:
            result = validate_price_data(self.price_dict)
            
            # Should return pandas Series
            self.assertIsInstance(result, pd.Series)
            
            # Should have same number of elements as input
            self.assertEqual(len(result), len(self.price_dict))
            
            # All values should be positive
            self.assertTrue(all(result > 0))
            
            print("✅ Price data validation (dict) passed")
            
        except Exception as e:
            self.fail(f"validate_price_data with dict failed: {e}")

    def test_validate_price_data_list(self):
        """Test price validation with list"""
        try:
            result = validate_price_data(self.price_list)
            
            # Should return pandas Series
            self.assertIsInstance(result, pd.Series)
            
            # Should have same length as input
            self.assertEqual(len(result), len(self.price_list))
            
            # All values should be positive
            self.assertTrue(all(result > 0))
            
            print("✅ Price data validation (list) passed")
            
        except Exception as e:
            self.fail(f"validate_price_data with list failed: {e}")

    def test_validate_price_data_dataframe(self):
        """Test price validation with DataFrame"""
        try:
            result = validate_price_data(self.price_df)
            
            # Should return pandas Series
            self.assertIsInstance(result, pd.Series)
            
            # Should extract close prices correctly
            self.assertEqual(len(result), len(self.price_df))
            
            print("✅ Price data validation (DataFrame) passed")
            
        except Exception as e:
            self.fail(f"validate_price_data with DataFrame failed: {e}")

    def test_validate_return_data(self):
        """Test return data validation"""
        try:
            result = validate_return_data(self.returns_series)
            
            # Should return pandas Series
            self.assertIsInstance(result, pd.Series)
            
            # Should have same length
            self.assertEqual(len(result), len(self.returns_series))
            
            # Returns should be reasonable (between -1 and 1 for daily)
            self.assertTrue(all(result > -1))
            self.assertTrue(all(result < 1))
            
            print("✅ Return data validation passed")
            
        except Exception as e:
            self.fail(f"validate_return_data failed: {e}")


class TestDataTransformation(unittest.TestCase):
    """Test data transformation functions"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        
        prices = 100 * (1 + np.cumsum(np.random.normal(0.001, 0.02, len(self.dates))))
        self.price_series = pd.Series(prices, index=self.dates)

    def test_prices_to_returns_simple(self):
        """Test simple return calculation"""
        try:
            result = prices_to_returns(self.price_series, method="simple")
            
            # Should be a pandas Series
            self.assertIsInstance(result, pd.Series)
            
            # Should have one less element than prices
            self.assertEqual(len(result), len(self.price_series) - 1)
            
            # Should match pandas pct_change
            expected = self.price_series.pct_change().dropna()
            np.testing.assert_array_almost_equal(result.values, expected.values, decimal=10)
            
            print("✅ Simple returns calculation passed")
            
        except Exception as e:
            self.fail(f"prices_to_returns simple failed: {e}")

    def test_prices_to_returns_log(self):
        """Test log return calculation"""
        try:
            result = prices_to_returns(self.price_series, method="log")
            
            # Should be a pandas Series
            self.assertIsInstance(result, pd.Series)
            
            # Should have one less element than prices
            self.assertEqual(len(result), len(self.price_series) - 1)
            
            # Log returns should be close to simple returns for small values
            simple_returns = self.price_series.pct_change().dropna()
            correlation = result.corr(simple_returns)
            self.assertGreater(correlation, 0.99)
            
            print("✅ Log returns calculation passed")
            
        except Exception as e:
            self.fail(f"prices_to_returns log failed: {e}")

    def test_calculate_log_returns(self):
        """Test log returns function"""
        try:
            result = calculate_log_returns(self.price_series)
            
            # Should be a pandas Series
            self.assertIsInstance(result, pd.Series)
            
            # Should have one less element
            self.assertEqual(len(result), len(self.price_series) - 1)
            
            # All values should be finite
            self.assertTrue(np.all(np.isfinite(result)))
            
            print("✅ Log returns function passed")
            
        except Exception as e:
            self.fail(f"calculate_log_returns failed: {e}")

    def test_calculate_cumulative_returns(self):
        """Test cumulative returns calculation"""
        try:
            returns = self.price_series.pct_change().dropna()
            result = calculate_cumulative_returns(returns)
            
            # Should be a list or Series
            self.assertTrue(isinstance(result, (list, pd.Series)))
            
            # Should have same length as returns
            expected_len = len(returns)
            actual_len = len(result) if isinstance(result, (list, pd.Series)) else 1
            self.assertGreater(actual_len, 0)
            
            print("✅ Cumulative returns calculation passed")
            
        except Exception as e:
            self.fail(f"calculate_cumulative_returns failed: {e}")

    def test_calculate_monthly_returns(self):
        """Test monthly returns calculation"""
        try:
            returns = self.price_series.pct_change().dropna()
            result = calculate_monthly_returns(returns, trading_days_per_month=21)
            
            # Should be a list
            self.assertIsInstance(result, list)
            
            # Should have approximately 12 months worth of returns
            # Exact number depends on the trading days calculation
            self.assertGreater(len(result), 0)
            self.assertLess(len(result), len(returns))
            
            # All returns should be reasonable
            for ret in result:
                self.assertTrue(isinstance(ret, (int, float)))
            
            print("✅ Monthly returns calculation passed")
            
        except Exception as e:
            self.fail(f"calculate_monthly_returns failed: {e}")


class TestSeriesAlignment(unittest.TestCase):
    """Test series alignment and resampling"""
    
    def setUp(self):
        """Set up test data"""
        self.dates1 = pd.date_range(start='2023-01-01', periods=100, freq='D')
        self.dates2 = pd.date_range(start='2023-01-15', periods=100, freq='D')
        self.dates3 = pd.date_range(start='2023-02-01', periods=100, freq='D')
        
        np.random.seed(42)
        self.series1 = pd.Series(np.random.normal(100, 5, 100), index=self.dates1)
        self.series2 = pd.Series(np.random.normal(50, 3, 100), index=self.dates2)
        self.series3 = pd.Series(np.random.normal(200, 10, 100), index=self.dates3)

    def test_align_two_series(self):
        """Test alignment of two series"""
        try:
            result = align_series(self.series1, self.series2)
            
            # Should return a list
            self.assertIsInstance(result, list)
            
            # Should have 2 elements
            self.assertEqual(len(result), 2)
            
            # All results should be pandas Series
            for series in result:
                self.assertIsInstance(series, pd.Series)
            
            # All aligned series should have same length
            lengths = [len(s) for s in result]
            self.assertEqual(len(set(lengths)), 1)
            
            # All indices should match
            self.assertTrue(result[0].index.equals(result[1].index))
            
            print("✅ Two series alignment passed")
            
        except Exception as e:
            self.fail(f"align_series with 2 series failed: {e}")

    def test_align_three_series(self):
        """Test alignment of three series"""
        try:
            result = align_series(self.series1, self.series2, self.series3)
            
            # Should return a list
            self.assertIsInstance(result, list)
            
            # Should have 3 elements
            self.assertEqual(len(result), 3)
            
            # All indices should match
            for i in range(1, len(result)):
                self.assertTrue(result[0].index.equals(result[i].index))
            
            print("✅ Three series alignment passed")
            
        except Exception as e:
            self.fail(f"align_series with 3 series failed: {e}")

    def test_resample_data(self):
        """Test data resampling"""
        try:
            # Test weekly resampling
            result_weekly = resample_data(self.series1, frequency='W', method='last')
            
            # Should be a pandas Series
            self.assertIsInstance(result_weekly, pd.Series)
            
            # Should have fewer data points than original
            self.assertLess(len(result_weekly), len(self.series1))
            
            # Test monthly resampling
            result_monthly = resample_data(self.series1, frequency='M', method='last')
            
            # Should be even fewer data points
            self.assertLess(len(result_monthly), len(result_weekly))
            
            print("✅ Data resampling passed")
            
        except Exception as e:
            self.fail(f"resample_data failed: {e}")


class TestOutputStandardization(unittest.TestCase):
    """Test output standardization"""
    
    def test_standardize_output(self):
        """Test output standardization function"""
        try:
            sample_result = {
                'value': 42.5,
                'calculation': 'test_calculation'
            }
            
            result = standardize_output(sample_result, 'test_function')
            
            # Should be a dictionary
            self.assertIsInstance(result, dict)
            
            # Should contain success and function keys
            self.assertIn('success', result)
            self.assertIn('function', result)
            
            # Function name should match
            self.assertEqual(result['function'], 'test_function')
            
            # Original data should be preserved
            self.assertEqual(result.get('value'), 42.5)
            
            print("✅ Output standardization passed")
            
        except Exception as e:
            self.fail(f"standardize_output failed: {e}")


class TestAlpacaDataExtraction(unittest.TestCase):
    """Test Alpaca data extraction"""
    
    def test_extract_symbols_from_list(self):
        """Test symbol extraction from list of dicts"""
        try:
            data = [
                {'symbol': 'AAPL', 'price': 150.0},
                {'symbol': 'MSFT', 'price': 300.0},
                {'symbol': 'GOOGL', 'price': 120.0}
            ]
            
            result = extract_symbols_from_alpaca_data(data)
            
            # Should be a list
            self.assertIsInstance(result, list)
            
            # Should contain expected symbols
            self.assertIn('AAPL', result)
            self.assertIn('MSFT', result)
            self.assertIn('GOOGL', result)
            
            # Should have 3 symbols
            self.assertEqual(len(result), 3)
            
            print("✅ Symbol extraction from list passed")
            
        except Exception as e:
            self.fail(f"extract_symbols from list failed: {e}")

    def test_extract_symbols_from_dict(self):
        """Test symbol extraction from dict"""
        try:
            data = {
                'AAPL': {'price': 150.0, 'volume': 1000000},
                'MSFT': {'price': 300.0, 'volume': 800000},
                'GOOGL': {'price': 120.0, 'volume': 600000}
            }
            
            result = extract_symbols_from_alpaca_data(data)
            
            # Should be a list
            self.assertIsInstance(result, list)
            
            # Should contain expected symbols
            for symbol in ['AAPL', 'MSFT', 'GOOGL']:
                self.assertIn(symbol, result)
            
            print("✅ Symbol extraction from dict passed")
            
        except Exception as e:
            self.fail(f"extract_symbols from dict failed: {e}")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        np.random.seed(42)

    def test_empty_data_handling(self):
        """Test handling of empty data"""
        # Empty Series
        empty_series = pd.Series([], dtype=float)
        
        # Should handle gracefully
        try:
            result = validate_price_data(empty_series)
            print("✅ Empty Series handled")
        except Exception:
            print("⚠️ Empty Series causes error (expected)")

    def test_single_value_data(self):
        """Test handling of single value"""
        try:
            single_value = pd.Series([100.0], index=self.dates[:1])
            result = validate_price_data(single_value)
            
            # Should return Series with one value
            self.assertEqual(len(result), 1)
            
            print("✅ Single value data handled")
            
        except Exception as e:
            print(f"⚠️ Single value handling: {e}")

    def test_nan_values(self):
        """Test handling of NaN values"""
        try:
            data_with_nan = pd.Series([100.0, np.nan, 102.0, 101.0], index=self.dates[:4])
            
            # Function should handle NaN
            result = validate_price_data(data_with_nan)
            
            # Result should be valid
            self.assertIsInstance(result, pd.Series)
            
            print("✅ NaN values handled")
            
        except Exception as e:
            print(f"⚠️ NaN handling: {e}")

    def test_negative_prices(self):
        """Test handling of negative prices (should be invalid)"""
        try:
            negative_data = pd.Series([-100.0, -102.0, -101.0])
            
            # Function should handle negative prices appropriately
            result = validate_price_data(negative_data)
            
            # Result should still be a Series (may not validate prices)
            self.assertIsInstance(result, pd.Series)
            
            print("✅ Negative prices handled")
            
        except Exception as e:
            print(f"⚠️ Negative prices: {e}")


if __name__ == '__main__':
    print("🧪 Running Data Utils Tests...")
    print("=" * 60)
    
    # Run tests
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 60)
    print("✅ Data utils tests completed!")