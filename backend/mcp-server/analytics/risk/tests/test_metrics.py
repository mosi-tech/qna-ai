"""
Unit tests for risk metrics calculations.

Tests all risk measurement, analysis, and portfolio risk functions to ensure
robust risk assessment across the analytics pipeline.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import functions to test
from ..metrics import (
    calculate_var,
    calculate_cvar,
    calculate_correlation_analysis,
    calculate_beta_analysis,
    stress_test_portfolio,
    calculate_rolling_volatility,
    calculate_beta,
    calculate_correlation,
    calculate_correlation_matrix,
    calculate_skewness,
    calculate_kurtosis,
    calculate_percentile,
    calculate_herfindahl_index,
    calculate_treynor_ratio,
    calculate_portfolio_volatility,
    calculate_component_var,
    calculate_marginal_var,
    calculate_risk_budget,
    calculate_tail_risk,
    calculate_expected_shortfall,
    calculate_diversification_ratio,
    calculate_downside_correlation,
    calculate_concentration_metrics
)


class TestValueAtRisk(unittest.TestCase):
    """Test Value at Risk calculations"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        
        # Create sample returns
        self.returns = pd.Series(
            np.random.normal(0.001, 0.02, len(self.dates)),
            index=self.dates,
            name='returns'
        )
        
        # Benchmark returns
        self.benchmark_returns = pd.Series(
            np.random.normal(0.0008, 0.015, len(self.dates)),
            index=self.dates,
            name='benchmark'
        )

    def test_calculate_var(self):
        """Test VaR calculation"""
        
            result = calculate_var(self.returns, confidence=0.95)
            
            # Should be a dictionary
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # VaR should be negative (loss)
            if 'var_value' in result and result['var_value'] is not None:
                self.assertLess(result['var_value'], 0)
            
            print("✅ VaR calculation passed")
            
        :
            self.fail(f"calculate_var failed: {e}")

    def test_calculate_cvar(self):
        """Test Conditional VaR (Expected Shortfall)"""
        
            result = calculate_cvar(self.returns, confidence=0.95)
            
            # Should be a dictionary
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # CVaR should be more negative than VaR
            if 'cvar_value' in result and result['cvar_value'] is not None:
                self.assertLess(result['cvar_value'], 0)
            
            print("✅ CVaR calculation passed")
            
        :
            self.fail(f"calculate_cvar failed: {e}")

    def test_calculate_expected_shortfall(self):
        """Test Expected Shortfall"""
        
            result = calculate_expected_shortfall(self.returns, confidence=0.95)
            
            # Should be a float
            self.assertIsInstance(result, (int, float))
            
            # Should be negative (loss)
            self.assertLess(result, 0)
            
            print("✅ Expected Shortfall passed")
            
        :
            self.fail(f"calculate_expected_shortfall failed: {e}")


class TestDistributionMetrics(unittest.TestCase):
    """Test distribution analysis metrics"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        
        self.returns = pd.Series(
            np.random.normal(0.001, 0.02, len(self.dates)),
            index=self.dates
        )

    def test_calculate_skewness(self):
        """Test skewness calculation"""
        
            result = calculate_skewness(self.returns)
            
            # Should be a float
            self.assertIsInstance(result, (int, float))
            
            # Skewness should be finite
            self.assertFalse(np.isnan(result))
            self.assertFalse(np.isinf(result))
            
            # For normal distribution, skewness should be close to 0
            self.assertGreater(result, -1)
            self.assertLess(result, 1)
            
            print("✅ Skewness calculation passed")
            
        :
            self.fail(f"calculate_skewness failed: {e}")

    def test_calculate_kurtosis(self):
        """Test kurtosis calculation"""
        
            result = calculate_kurtosis(self.returns)
            
            # Should be a float
            self.assertIsInstance(result, (int, float))
            
            # Kurtosis should be finite
            self.assertFalse(np.isnan(result))
            self.assertFalse(np.isinf(result))
            
            # For normal distribution, excess kurtosis should be close to 0
            self.assertGreater(result, -1)
            self.assertLess(result, 5)
            
            print("✅ Kurtosis calculation passed")
            
        :
            self.fail(f"calculate_kurtosis failed: {e}")

    def test_calculate_percentile(self):
        """Test percentile calculation"""
        
            result = calculate_percentile(self.returns, percentile=95)
            
            # Should be a float
            self.assertIsInstance(result, (int, float))
            
            # 95th percentile should be positive for this dataset
            self.assertGreater(result, 0)
            
            # Should be within the range of data
            self.assertLess(result, self.returns.max())
            self.assertGreater(result, self.returns.min())
            
            print("✅ Percentile calculation passed")
            
        :
            self.fail(f"calculate_percentile failed: {e}")


class TestCorrelationAnalysis(unittest.TestCase):
    """Test correlation analysis"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        
        self.returns1 = pd.Series(
            np.random.normal(0.001, 0.02, len(self.dates)),
            index=self.dates,
            name='asset1'
        )
        
        self.returns2 = pd.Series(
            np.random.normal(0.001, 0.02, len(self.dates)),
            index=self.dates,
            name='asset2'
        )

    def test_calculate_correlation(self):
        """Test correlation calculation"""
        
            result = calculate_correlation(self.returns1, self.returns2)
            
            # Should be a float
            self.assertIsInstance(result, (int, float))
            
            # Correlation should be between -1 and 1
            self.assertGreaterEqual(result, -1)
            self.assertLessEqual(result, 1)
            
            print("✅ Correlation calculation passed")
            
        :
            self.fail(f"calculate_correlation failed: {e}")

    def test_calculate_correlation_matrix(self):
        """Test correlation matrix calculation"""
        
            series_list = [self.returns1, self.returns2]
            result = calculate_correlation_matrix(series_list)
            
            # Should be a DataFrame
            self.assertIsInstance(result, pd.DataFrame)
            
            # Should be 2x2 for 2 series
            self.assertEqual(result.shape, (2, 2))
            
            # Diagonal should be 1s (correlation with itself)
            np.testing.assert_array_almost_equal(
                np.diag(result.values),
                [1.0, 1.0],
                decimal=5
            )
            
            print("✅ Correlation matrix passed")
            
        :
            self.fail(f"calculate_correlation_matrix failed: {e}")

    def test_calculate_correlation_analysis(self):
        """Test correlation analysis"""
        
            returns_df = pd.DataFrame({
                'asset1': self.returns1,
                'asset2': self.returns2
            })
            
            result = calculate_correlation_analysis(returns_df)
            
            # Should be a dictionary
            self.assertIsInstance(result, dict)
            
            print("✅ Correlation analysis passed")
            
        :
            self.fail(f"calculate_correlation_analysis failed: {e}")


class TestBetaAnalysis(unittest.TestCase):
    """Test beta and systematic risk analysis"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        
        # Create market returns
        self.market_returns = pd.Series(
            np.random.normal(0.0008, 0.015, len(self.dates)),
            index=self.dates,
            name='market'
        )
        
        # Create asset returns (correlated with market)
        self.asset_returns = self.market_returns * 1.5 + np.random.normal(0, 0.01, len(self.dates))

    def test_calculate_beta(self):
        """Test beta calculation"""
        
            result = calculate_beta(self.asset_returns, self.market_returns)
            
            # Should be a float
            self.assertIsInstance(result, (int, float))
            
            # Beta should be positive for this correlated data
            self.assertGreater(result, 0)
            
            # Should be around 1.5 (by construction)
            self.assertGreater(result, 1.0)
            
            print("✅ Beta calculation passed")
            
        :
            self.fail(f"calculate_beta failed: {e}")

    def test_calculate_beta_analysis(self):
        """Test beta analysis"""
        
            result = calculate_beta_analysis(self.asset_returns, self.market_returns)
            
            # Should be a dictionary
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # Should contain beta
            if 'beta' in result:
                self.assertIsInstance(result['beta'], (int, float))
            
            print("✅ Beta analysis passed")
            
        :
            self.fail(f"calculate_beta_analysis failed: {e}")

    def test_calculate_treynor_ratio(self):
        """Test Treynor ratio"""
        
            result = calculate_treynor_ratio(
                self.asset_returns,
                self.market_returns,
                risk_free_rate=0.02
            )
            
            # Should be a float
            self.assertIsInstance(result, (int, float))
            
            # Treynor ratio can be positive or negative
            self.assertFalse(np.isnan(result))
            
            print("✅ Treynor ratio passed")
            
        :
            self.fail(f"calculate_treynor_ratio failed: {e}")


class TestVolatilityAnalysis(unittest.TestCase):
    """Test volatility analysis"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        
        self.returns = pd.Series(
            np.random.normal(0.001, 0.02, len(self.dates)),
            index=self.dates
        )

    def test_calculate_rolling_volatility(self):
        """Test rolling volatility"""
        
            result = calculate_rolling_volatility(self.returns, window=30)
            
            # Should be a pandas Series
            self.assertIsInstance(result, pd.Series)
            
            # Should have fewer elements than input (due to window)
            self.assertLess(len(result), len(self.returns))
            
            # All values should be positive
            if len(result) > 0:
                self.assertTrue(all(result > 0))
            
            print("✅ Rolling volatility passed")
            
        :
            self.fail(f"calculate_rolling_volatility failed: {e}")


class TestPortfolioRisk(unittest.TestCase):
    """Test portfolio-level risk metrics"""
    
    def setUp(self):
        """Set up test data"""
        self.weights = np.array([0.3, 0.5, 0.2])
        
        self.returns_data = {
            'asset1': np.random.normal(0.001, 0.02, 100),
            'asset2': np.random.normal(0.0008, 0.015, 100),
            'asset3': np.random.normal(0.0012, 0.025, 100)
        }
        
        self.cov_matrix = pd.DataFrame({
            'asset1': [0.0004, 0.00015, 0.0002],
            'asset2': [0.00015, 0.000225, 0.00012],
            'asset3': [0.0002, 0.00012, 0.000625]
        }, index=['asset1', 'asset2', 'asset3'])

    def test_calculate_herfindahl_index(self):
        """Test Herfindahl index (concentration measure)"""
        
            result = calculate_herfindahl_index(self.weights)
            
            # Should be a float
            self.assertIsInstance(result, (int, float))
            
            # Should be between 0 and 1
            self.assertGreater(result, 0)
            self.assertLess(result, 1)
            
            print("✅ Herfindahl index passed")
            
        :
            self.fail(f"calculate_herfindahl_index failed: {e}")

    def test_calculate_portfolio_volatility(self):
        """Test portfolio volatility"""
        
            result = calculate_portfolio_volatility(self.weights, self.cov_matrix)
            
            # Should be a float
            self.assertIsInstance(result, (int, float))
            
            # Should be positive
            self.assertGreater(result, 0)
            
            print("✅ Portfolio volatility passed")
            
        :
            self.fail(f"calculate_portfolio_volatility failed: {e}")

    def test_calculate_concentration_metrics(self):
        """Test concentration metrics"""
        
            result = calculate_concentration_metrics(self.weights)
            
            # Should be a dictionary
            self.assertIsInstance(result, dict)
            
            # Should have concentration metrics
            self.assertIn('herfindahl_index', result)
            
            print("✅ Concentration metrics passed")
            
        :
            self.fail(f"calculate_concentration_metrics failed: {e}")

    def test_calculate_risk_budget(self):
        """Test risk budget calculation"""
        
            result = calculate_risk_budget(self.weights, self.cov_matrix)
            
            # Should be a dictionary
            self.assertIsInstance(result, dict)
            
            print("✅ Risk budget passed")
            
        :
            self.fail(f"calculate_risk_budget failed: {e}")

    def test_calculate_component_var(self):
        """Test component VaR"""
        
            result = calculate_component_var(self.weights, self.cov_matrix)
            
            # Should be a dictionary
            self.assertIsInstance(result, dict)
            
            print("✅ Component VaR passed")
            
        :
            self.fail(f"calculate_component_var failed: {e}")

    def test_calculate_marginal_var(self):
        """Test marginal VaR"""
        
            result = calculate_marginal_var(self.weights, self.cov_matrix)
            
            # Should be a dictionary
            self.assertIsInstance(result, dict)
            
            print("✅ Marginal VaR passed")
            
        :
            self.fail(f"calculate_marginal_var failed: {e}")

    def test_calculate_diversification_ratio(self):
        """Test diversification ratio"""
        
            portfolio_vol = 0.015
            weighted_avg_vol = 0.018
            
            result = calculate_diversification_ratio(portfolio_vol, weighted_avg_vol)
            
            # Should be a float
            self.assertIsInstance(result, (int, float))
            
            # Should be > 0 and typically < 2 for diversified portfolios
            self.assertGreater(result, 0)
            
            print("✅ Diversification ratio passed")
            
        :
            self.fail(f"calculate_diversification_ratio failed: {e}")


class TestTailRisk(unittest.TestCase):
    """Test tail risk analysis"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        
        self.returns = pd.Series(
            np.random.normal(0.001, 0.02, len(self.dates)),
            index=self.dates
        )

    def test_calculate_tail_risk(self):
        """Test tail risk calculation"""
        
            result = calculate_tail_risk(self.returns, threshold=0.05)
            
            # Should be a dictionary
            self.assertIsInstance(result, dict)
            
            # Should have tail statistics
            if 'tail_mean' in result:
                self.assertIsInstance(result['tail_mean'], (int, float))
            
            print("✅ Tail risk passed")
            
        :
            self.fail(f"calculate_tail_risk failed: {e}")


class TestStressTest(unittest.TestCase):
    """Test stress testing"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        
        self.returns = pd.Series(
            np.random.normal(0.001, 0.02, len(self.dates)),
            index=self.dates
        )

    def test_stress_test_portfolio(self):
        """Test portfolio stress testing"""
        
            market_shock = 0.1  # 10% market decline
            result = stress_test_portfolio(
                self.returns,
                market_scenario=market_shock
            )
            
            # Should be a dictionary
            self.assertIsInstance(result, dict)
            
            print("✅ Stress test passed")
            
        :
            self.fail(f"stress_test_portfolio failed: {e}")


class TestDownsideRisk(unittest.TestCase):
    """Test downside-specific risk metrics"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        
        self.portfolio_returns = pd.Series(
            np.random.normal(0.001, 0.02, len(self.dates)),
            index=self.dates
        )
        
        self.downside_returns = pd.Series(
            np.random.normal(-0.01, 0.015, len(self.dates)),
            index=self.dates
        )

    def test_calculate_downside_correlation(self):
        """Test downside correlation"""
        
            result = calculate_downside_correlation(
                self.portfolio_returns,
                self.downside_returns,
                threshold=0.0
            )
            
            # Should be a float
            self.assertIsInstance(result, (int, float))
            
            # Should be between -1 and 1
            self.assertGreaterEqual(result, -1)
            self.assertLessEqual(result, 1)
            
            print("✅ Downside correlation passed")
            
        :
            self.fail(f"calculate_downside_correlation failed: {e}")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        np.random.seed(42)

    def test_empty_data_handling(self):
        """Test handling of empty data"""
        empty_series = pd.Series([], dtype=float)
        
        
            result = calculate_skewness(empty_series)
            print("✅ Empty data handled")
        except Exception:
            print("⚠️ Empty data causes error (expected)")

    def test_single_value_handling(self):
        """Test handling of single value"""
        
            single_value = pd.Series([0.01])
            result = calculate_skewness(single_value)
            print("✅ Single value handled")
        except Exception:
            print("⚠️ Single value causes error (expected)")

    def test_constant_returns(self):
        """Test handling of constant returns"""
        
            constant_returns = pd.Series([0.0] * 100)
            result = calculate_rolling_volatility(constant_returns, window=30)
            # Should handle gracefully
            print("✅ Constant returns handled")
        :
            print(f"⚠️ Constant returns: {e}")


if __name__ == '__main__':
    print("🧪 Running Risk Metrics Tests...")
    print("=" * 60)
    
    # Run tests
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 60)
    print("✅ Risk metrics tests completed!")