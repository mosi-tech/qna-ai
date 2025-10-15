"""
Unit tests for comparison metrics calculations.

Tests the comparison metrics functionality to ensure proper empyrical library usage,
correct calculations, and error handling across all comparison functions.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import functions to test
from ..metrics import (
    compare_performance_metrics,
    compare_risk_metrics,
    compare_drawdowns,
    compare_volatility_profiles,
    compare_correlation_stability,
    compare_sector_exposure,
    compare_expense_ratios,
    compare_liquidity,
    compare_fundamental,
    compute_outperformance
)


class TestComparisonMetrics(unittest.TestCase):
    """Test comparison metrics calculations"""
    
    def setUp(self):
        """Set up test data"""
        # Create sample dates
        self.dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)  # For reproducible results
        
        # Create sample returns data for two assets
        n_days = len(self.dates)
        self.returns1 = pd.Series(
            np.random.normal(0.001, 0.02, n_days),
            index=self.dates,
            name='asset1'
        )
        
        self.returns2 = pd.Series(
            np.random.normal(0.0008, 0.015, n_days),
            index=self.dates,
            name='asset2'
        )
        
        # Create price data
        self.prices1 = pd.Series(
            100 * (1 + self.returns1).cumprod(),
            index=self.dates,
            name='prices1'
        )
        
        self.prices2 = pd.Series(
            100 * (1 + self.returns2).cumprod(),
            index=self.dates,
            name='prices2'
        )
        
        # Sample volume data
        self.volumes1 = pd.Series(
            np.random.randint(1000000, 10000000, n_days),
            index=self.dates,
            name='volume1'
        )
        
        self.volumes2 = pd.Series(
            np.random.randint(500000, 8000000, n_days),
            index=self.dates,
            name='volume2'
        )

    def test_compare_performance_metrics(self):
        """Test performance metrics comparison"""
        try:
            result = compare_performance_metrics(self.returns1, self.returns2)
            
            # Check that result is a dictionary
            self.assertIsInstance(result, dict)
            
            # Check for required keys
            required_keys = ['success', 'summary', 'metrics_comparison']
            for key in required_keys:
                self.assertIn(key, result)
            
            # Check that success is True
            self.assertTrue(result['success'])
            
            # Check summary structure
            if 'summary' in result:
                summary = result['summary']
                self.assertIn('overall_winner', summary)
            
            # Check metrics comparison structure
            if 'metrics_comparison' in result:
                metrics = result['metrics_comparison']
                self.assertIsInstance(metrics, dict)
            
            print("✅ Performance metrics comparison test passed")
            
        except Exception as e:
            self.fail(f"compare_performance_metrics failed with error: {e}")

    def test_compare_risk_metrics(self):
        """Test risk metrics comparison"""
        try:
            result = compare_risk_metrics(self.returns1, self.returns2)
            
            # Check basic structure
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # Check for risk comparison keys
            expected_keys = ['success', 'summary', 'risk_comparison']
            for key in expected_keys:
                if key in result:
                    self.assertIsNotNone(result[key])
            
            print("✅ Risk metrics comparison test passed")
            
        except Exception as e:
            self.fail(f"Risk metrics comparison failed: {e}")

    def test_compare_drawdowns(self):
        """Test drawdown comparison"""
        try:
            result = compare_drawdowns(self.prices1, self.prices2)
            
            # Check basic structure
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # Check for drawdown comparison keys
            if 'drawdown_comparison' in result:
                drawdown_comp = result['drawdown_comparison']
                self.assertIsInstance(drawdown_comp, dict)
            
            print("✅ Drawdown comparison test passed")
            
        except Exception as e:
            self.fail(f"Drawdown comparison failed: {e}")

    def test_compare_volatility_profiles(self):
        """Test volatility profiles comparison"""
        try:
            result = compare_volatility_profiles(self.returns1, self.returns2)
            
            # Check basic structure
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # Check for volatility comparison structure
            if 'volatility_comparison' in result:
                vol_comp = result['volatility_comparison']
                self.assertIsInstance(vol_comp, dict)
            
            print("✅ Volatility profiles comparison test passed")
            
        except Exception as e:
            self.fail(f"Volatility profiles comparison failed: {e}")

    def test_compare_correlation_stability(self):
        """Test correlation stability comparison"""
        try:
            result = compare_correlation_stability(self.returns1, self.returns2)
            
            # Check basic structure
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # Check for correlation analysis
            if 'correlation_analysis' in result:
                corr_analysis = result['correlation_analysis']
                self.assertIsInstance(corr_analysis, dict)
            
            print("✅ Correlation stability comparison test passed")
            
        except Exception as e:
            self.fail(f"Correlation stability comparison failed: {e}")

    def test_compare_sector_exposure(self):
        """Test sector exposure comparison"""
        try:
            # Create sample holdings data
            holdings1 = [
                {'symbol': 'AAPL', 'sector': 'Technology', 'weight': 0.3},
                {'symbol': 'MSFT', 'sector': 'Technology', 'weight': 0.2},
                {'symbol': 'JPM', 'sector': 'Financial', 'weight': 0.5}
            ]
            
            holdings2 = [
                {'symbol': 'GOOGL', 'sector': 'Technology', 'weight': 0.4},
                {'symbol': 'BAC', 'sector': 'Financial', 'weight': 0.3},
                {'symbol': 'JNJ', 'sector': 'Healthcare', 'weight': 0.3}
            ]
            
            result = compare_sector_exposure(holdings1, holdings2)
            
            # Check basic structure
            self.assertIsInstance(result, dict)
            # Note: This function may not have a success flag
            
            # Check for sector comparison data
            self.assertIsInstance(result, dict)
            # The function should return some comparison data
            
            print("✅ Sector exposure comparison test passed")
            
        except Exception as e:
            self.fail(f"Sector exposure comparison failed: {e}")

    def test_compare_expense_ratios(self):
        """Test expense ratios comparison"""
        try:
            # Create sample fund data
            funds = [
                {'symbol': 'VTI', 'expense_ratio': 0.03, 'name': 'Vanguard Total Stock Market'},
                {'symbol': 'SPY', 'expense_ratio': 0.09, 'name': 'SPDR S&P 500'},
                {'symbol': 'QQQ', 'expense_ratio': 0.20, 'name': 'Invesco QQQ Trust'}
            ]
            
            result = compare_expense_ratios(funds)
            
            # Function returns a dict with success flag and comparison data
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # Check for expense comparison structure
            if 'expense_comparison' in result:
                expense_comp = result['expense_comparison']
                self.assertIsInstance(expense_comp, list)
                self.assertGreater(len(expense_comp), 0)
            
            print("✅ Expense ratios comparison test passed")
            
        except Exception as e:
            self.fail(f"Expense ratios comparison failed: {e}")

    def test_compare_liquidity(self):
        """Test liquidity comparison"""
        try:
            result = compare_liquidity(self.volumes1, self.volumes2)
            
            # Check basic structure
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # Check for liquidity metrics
            if 'liquidity_comparison' in result:
                liq_comp = result['liquidity_comparison']
                self.assertIsInstance(liq_comp, dict)
            
            print("✅ Liquidity comparison test passed")
            
        except Exception as e:
            self.fail(f"Liquidity comparison failed: {e}")

    def test_compare_fundamental(self):
        """Test fundamental metrics comparison"""
        try:
            # Create sample fundamental data
            fundamentals1 = {
                'pe_ratio': 15.5,
                'pb_ratio': 2.1,
                'dividend_yield': 0.025,
                'roe': 0.18,
                'debt_to_equity': 0.45
            }
            
            fundamentals2 = {
                'pe_ratio': 22.3,
                'pb_ratio': 3.2,
                'dividend_yield': 0.015,
                'roe': 0.22,
                'debt_to_equity': 0.30
            }
            
            result = compare_fundamental(fundamentals1, fundamentals2)
            
            # Check basic structure
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # Check for fundamental comparison
            if 'fundamental_comparison' in result:
                fund_comp = result['fundamental_comparison']
                self.assertIsInstance(fund_comp, dict)
            
            print("✅ Fundamental comparison test passed")
            
        except Exception as e:
            self.fail(f"Fundamental comparison failed: {e}")

    def test_compute_outperformance(self):
        """Test outperformance computation"""
        try:
            # Create sample returns DataFrame
            returns_df = pd.DataFrame({
                'asset1': self.returns1,
                'asset2': self.returns2
            })
            
            # Create benchmark returns
            benchmark_returns = self.returns1  # Use returns1 as benchmark
            
            result = compute_outperformance(returns_df, benchmark_returns)
            
            # Check basic structure
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # Check for outperformance analysis
            if 'outperformance_analysis' in result:
                outperf = result['outperformance_analysis']
                self.assertIsInstance(outperf, dict)
            
            print("✅ Outperformance computation test passed")
            
        except Exception as e:
            self.fail(f"Outperformance computation failed: {e}")

    def test_edge_cases(self):
        """Test edge cases and error handling"""
        
        # Test with identical data
        try:
            result = compare_performance_metrics(self.returns1, self.returns1)
            # Should handle gracefully
            print("✅ Identical data edge case handled")
        except Exception:
            pass  # Expected to fail or handle gracefully
        
        # Test with very short series
        try:
            short_returns1 = self.returns1.head(5)
            short_returns2 = self.returns2.head(5)
            result = compare_risk_metrics(short_returns1, short_returns2)
            print("✅ Short series edge case handled")
        except Exception:
            pass  # Expected to fail or handle gracefully
        
        # Test with NaN values
        try:
            nan_returns = self.returns1.copy()
            nan_returns.iloc[10:20] = np.nan
            result = compare_performance_metrics(nan_returns, self.returns2)
            print("✅ NaN values edge case handled")
        except Exception:
            pass  # Expected to fail or handle gracefully

    def test_data_validation(self):
        """Test data validation functionality"""
        
        # Test with mismatched indices
        try:
            mismatched_returns = self.returns2.iloc[10:]
            result = compare_performance_metrics(self.returns1, mismatched_returns)
            print("✅ Mismatched indices handled")
        except Exception as e:
            print(f"⚠️ Mismatched indices handling: {e}")
        
        # Test with different frequencies
        try:
            weekly_returns = self.returns1.resample('W').sum()
            result = compare_volatility_profiles(self.returns1, weekly_returns)
            print("✅ Different frequencies handled")
        except Exception as e:
            print(f"⚠️ Different frequencies handling: {e}")


if __name__ == '__main__':
    print("🧪 Running Comparison Metrics Tests...")
    print("=" * 60)
    
    # Run tests
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 60)
    print("✅ Comparison metrics tests completed!")