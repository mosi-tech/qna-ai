"""
Comprehensive unit tests for risk metrics - Version 2.
Tests all 23 risk analysis functions with correct parameter signatures.
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
    """Test VaR and Expected Shortfall"""
    
    def setUp(self):
        self.dates = pd.date_range('2023-01-01', periods=100, freq='D')
        np.random.seed(42)
        self.returns = pd.Series(np.random.normal(0.001, 0.02, 100), index=self.dates)

    def test_calculate_var(self):
        """Test VaR with correct parameters"""
        
            result = calculate_var(self.returns, confidence_level=0.05, method='historical')
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            print("✅ VaR calculation passed")
        :
            self.fail(f"VaR failed: {e}")

    def test_calculate_cvar(self):
        """Test CVaR with correct parameters"""
        
            result = calculate_cvar(self.returns, confidence_level=0.05)
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            print("✅ CVaR calculation passed")
        :
            self.fail(f"CVaR failed: {e}")

    def test_calculate_expected_shortfall(self):
        """Test Expected Shortfall"""
        
            result = calculate_expected_shortfall(self.returns, confidence=0.05)
            self.assertIsInstance(result, (int, float))
            self.assertLess(result, 0)  # Should be negative
            print("✅ Expected Shortfall passed")
        :
            self.fail(f"Expected Shortfall failed: {e}")


class TestDistributionMetrics(unittest.TestCase):
    """Test distribution analysis"""
    
    def setUp(self):
        self.dates = pd.date_range('2023-01-01', periods=100, freq='D')
        np.random.seed(42)
        self.returns = pd.Series(np.random.normal(0.001, 0.02, 100), index=self.dates)

    def test_calculate_skewness(self):
        
            result = calculate_skewness(self.returns)
            self.assertIsInstance(result, (int, float))
            self.assertFalse(np.isnan(result))
            print("✅ Skewness passed")
        :
            self.fail(f"Skewness failed: {e}")

    def test_calculate_kurtosis(self):
        
            result = calculate_kurtosis(self.returns)
            self.assertIsInstance(result, (int, float))
            self.assertFalse(np.isnan(result))
            print("✅ Kurtosis passed")
        :
            self.fail(f"Kurtosis failed: {e}")

    def test_calculate_percentile(self):
        
            result = calculate_percentile(self.returns, percentile=95)
            self.assertIsInstance(result, (int, float))
            self.assertGreater(result, self.returns.min())
            self.assertLess(result, self.returns.max())
            print("✅ Percentile passed")
        :
            self.fail(f"Percentile failed: {e}")


class TestCorrelationBeta(unittest.TestCase):
    """Test correlation and beta analysis"""
    
    def setUp(self):
        self.dates = pd.date_range('2023-01-01', periods=100, freq='D')
        np.random.seed(42)
        self.returns1 = pd.Series(np.random.normal(0.001, 0.02, 100), index=self.dates)
        self.returns2 = pd.Series(np.random.normal(0.001, 0.02, 100), index=self.dates)

    def test_calculate_correlation(self):
        
            result = calculate_correlation(self.returns1, self.returns2)
            self.assertIsInstance(result, (int, float))
            self.assertGreaterEqual(result, -1)
            self.assertLessEqual(result, 1)
            print("✅ Correlation passed")
        :
            self.fail(f"Correlation failed: {e}")

    def test_calculate_correlation_matrix(self):
        
            result = calculate_correlation_matrix([self.returns1, self.returns2])
            self.assertIsInstance(result, pd.DataFrame)
            self.assertEqual(result.shape, (2, 2))
            print("✅ Correlation matrix passed")
        :
            self.fail(f"Correlation matrix failed: {e}")

    def test_calculate_correlation_analysis(self):
        
            df = pd.DataFrame({'a': self.returns1, 'b': self.returns2})
            result = calculate_correlation_analysis(df)
            self.assertIsInstance(result, dict)
            print("✅ Correlation analysis passed")
        :
            self.fail(f"Correlation analysis failed: {e}")

    def test_calculate_beta(self):
        
            result = calculate_beta(self.returns1, self.returns2)
            self.assertIsInstance(result, (int, float))
            print("✅ Beta calculation passed")
        :
            self.fail(f"Beta failed: {e}")

    def test_calculate_beta_analysis(self):
        
            result = calculate_beta_analysis(self.returns1, self.returns2)
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            print("✅ Beta analysis passed")
        :
            self.fail(f"Beta analysis failed: {e}")

    def test_calculate_treynor_ratio(self):
        
            result = calculate_treynor_ratio(self.returns1, self.returns2, risk_free_rate=0.02)
            self.assertIsInstance(result, (int, float))
            print("✅ Treynor ratio passed")
        :
            self.fail(f"Treynor ratio failed: {e}")


class TestVolatilityConcentration(unittest.TestCase):
    """Test volatility and concentration metrics"""
    
    def setUp(self):
        self.dates = pd.date_range('2023-01-01', periods=100, freq='D')
        np.random.seed(42)
        self.returns = pd.Series(np.random.normal(0.001, 0.02, 100), index=self.dates)
        self.weights = np.array([0.3, 0.5, 0.2])

    def test_calculate_rolling_volatility(self):
        
            result = calculate_rolling_volatility(self.returns, window=30)
            self.assertIsInstance(result, pd.Series)
            self.assertLess(len(result), len(self.returns))
            print("✅ Rolling volatility passed")
        :
            self.fail(f"Rolling volatility failed: {e}")

    def test_calculate_herfindahl_index(self):
        
            result = calculate_herfindahl_index(self.weights)
            self.assertIsInstance(result, (int, float))
            self.assertGreater(result, 0)
            self.assertLess(result, 1)
            print("✅ Herfindahl index passed")
        :
            self.fail(f"Herfindahl index failed: {e}")

    def test_calculate_concentration_metrics(self):
        
            result = calculate_concentration_metrics(self.weights)
            self.assertIsInstance(result, dict)
            self.assertIn('herfindahl_index', result)
            print("✅ Concentration metrics passed")
        :
            self.fail(f"Concentration metrics failed: {e}")

    def test_calculate_diversification_ratio(self):
        
            result = calculate_diversification_ratio(portfolio_vol=0.015, weighted_avg_vol=0.018)
            self.assertIsInstance(result, (int, float))
            self.assertGreater(result, 0)
            print("✅ Diversification ratio passed")
        :
            self.fail(f"Diversification ratio failed: {e}")


class TestPortfolioVolatility(unittest.TestCase):
    """Test portfolio volatility and risk budget"""
    
    def setUp(self):
        self.weights = np.array([0.3, 0.5, 0.2])
        self.cov_matrix = pd.DataFrame({
            'a': [0.0004, 0.00015, 0.0002],
            'b': [0.00015, 0.000225, 0.00012],
            'c': [0.0002, 0.00012, 0.000625]
        }, index=['a', 'b', 'c'])
        self.volatilities = pd.Series([0.02, 0.015, 0.025], index=['a', 'b', 'c'])

    def test_calculate_portfolio_volatility(self):
        
            result = calculate_portfolio_volatility(self.weights, self.cov_matrix, self.volatilities)
            self.assertIsInstance(result, (int, float))
            self.assertGreater(result, 0)
            print("✅ Portfolio volatility passed")
        :
            self.fail(f"Portfolio volatility failed: {e}")

    def test_calculate_component_var(self):
        
            dates = pd.date_range('2023-01-01', periods=100, freq='D')
            returns_df = pd.DataFrame({
                'a': np.random.normal(0.001, 0.02, 100),
                'b': np.random.normal(0.001, 0.02, 100),
                'c': np.random.normal(0.001, 0.02, 100)
            }, index=dates)
            result = calculate_component_var(self.weights, returns_df, confidence=0.05)
            self.assertIsInstance(result, (list, np.ndarray))
            print("✅ Component VaR passed")
        :
            self.fail(f"Component VaR failed: {e}")

    def test_calculate_marginal_var(self):
        
            dates = pd.date_range('2023-01-01', periods=100, freq='D')
            returns_df = pd.DataFrame({
                'a': np.random.normal(0.001, 0.02, 100),
                'b': np.random.normal(0.001, 0.02, 100),
                'c': np.random.normal(0.001, 0.02, 100)
            }, index=dates)
            result = calculate_marginal_var(self.weights, returns_df, confidence=0.05)
            self.assertIsInstance(result, (list, np.ndarray))
            print("✅ Marginal VaR passed")
        :
            self.fail(f"Marginal VaR failed: {e}")

    def test_calculate_risk_budget(self):
        
            risk_contribs = np.array([0.005, 0.008, 0.003])
            result = calculate_risk_budget(self.weights, risk_contribs)
            self.assertIsInstance(result, (list, np.ndarray))
            print("✅ Risk budget passed")
        :
            self.fail(f"Risk budget failed: {e}")


class TestTailAndDownsideRisk(unittest.TestCase):
    """Test tail risk and downside-specific metrics"""
    
    def setUp(self):
        self.dates = pd.date_range('2023-01-01', periods=100, freq='D')
        np.random.seed(42)
        self.returns = pd.Series(np.random.normal(0.001, 0.02, 100), index=self.dates)
        self.benchmark = pd.Series(np.random.normal(0.001, 0.02, 100), index=self.dates)

    def test_calculate_tail_risk(self):
        
            result = calculate_tail_risk(self.returns, threshold=0.05)
            self.assertIsInstance(result, dict)
            print("✅ Tail risk passed")
        :
            self.fail(f"Tail risk failed: {e}")

    def test_calculate_downside_correlation(self):
        
            result = calculate_downside_correlation(self.returns, self.benchmark)
            self.assertIsInstance(result, dict)
            print("✅ Downside correlation passed")
        :
            self.fail(f"Downside correlation failed: {e}")


class TestStressTest(unittest.TestCase):
    """Test stress testing"""
    
    def setUp(self):
        self.dates = pd.date_range('2023-01-01', periods=100, freq='D')
        np.random.seed(42)
        self.returns = pd.Series(np.random.normal(0.001, 0.02, 100), index=self.dates)

    def test_stress_test_portfolio(self):
        
            result = stress_test_portfolio(self.returns)
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            print("✅ Stress test passed")
        :
            self.fail(f"Stress test failed: {e}")


if __name__ == '__main__':
    print("🧪 Running Risk Metrics Tests (V2)...")
    print("=" * 65)
    
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 65)
    print("✅ Risk metrics tests completed!")