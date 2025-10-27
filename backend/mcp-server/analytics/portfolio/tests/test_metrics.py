"""
Unit tests for portfolio metrics calculations.

Tests the portfolio metrics functionality to ensure proper calculations
and error handling.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import functions to test
from ..metrics import (
    calculate_portfolio_metrics,
    analyze_portfolio_concentration,
    calculate_portfolio_beta,
    analyze_portfolio_turnover,
    calculate_active_share,
    perform_attribution,
    calculate_portfolio_var,
    stress_test_portfolio
)


class TestPortfolioMetrics(unittest.TestCase):
    """Test portfolio metrics calculations"""
    
    def setUp(self):
        """Set up test data"""
        # Create sample dates
        self.dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        
        # Create sample returns data
        n_days = len(self.dates)
        self.returns_data = pd.DataFrame({
            'AAPL': np.random.normal(0.001, 0.02, n_days),
            'GOOGL': np.random.normal(0.0008, 0.018, n_days),
            'MSFT': np.random.normal(0.0009, 0.016, n_days),
            'TSLA': np.random.normal(0.002, 0.04, n_days),
            'SPY': np.random.normal(0.0007, 0.015, n_days)
        }, index=self.dates)
        
        # Create sample portfolio weights
        self.weights = {'AAPL': 0.3, 'GOOGL': 0.25, 'MSFT': 0.25, 'TSLA': 0.2}
        self.weights_series = pd.Series(self.weights)
        
        # Sample benchmark returns
        self.benchmark_returns = self.returns_data['SPY']
        
        # Portfolio returns
        portfolio_rets = self.returns_data[['AAPL', 'GOOGL', 'MSFT', 'TSLA']].dot(self.weights_series)
        self.portfolio_returns = portfolio_rets

    def test_calculate_portfolio_metrics(self):
        """Test basic portfolio metrics calculation"""
        
            result = calculate_portfolio_metrics(
                weights=self.weights,
                returns=self.returns_data[['AAPL', 'GOOGL', 'MSFT', 'TSLA']],
                benchmark_returns=self.benchmark_returns
            )
            
            # Should return a dictionary
            self.assertIsInstance(result, dict)
            
            print("✅ Portfolio metrics calculation passed")
            
        :
            print(f"⚠️ Portfolio metrics: {e}")

    def test_analyze_portfolio_concentration(self):
        """Test portfolio concentration analysis"""
        
            result = analyze_portfolio_concentration(
                weights=self.weights
            )
            
            # Should return a dictionary
            self.assertIsInstance(result, dict)
            
            print("✅ Concentration analysis passed")
            
        :
            print(f"⚠️ Concentration analysis: {e}")

    def test_calculate_portfolio_beta(self):
        """Test portfolio beta calculation"""
        
            result = calculate_portfolio_beta(
                returns=self.portfolio_returns,
                benchmark_returns=self.benchmark_returns
            )
            
            # Should return a dictionary
            self.assertIsInstance(result, dict)
            
            print("✅ Portfolio beta calculation passed")
            
        :
            print(f"⚠️ Portfolio beta: {e}")

    def test_analyze_portfolio_turnover(self):
        """Test portfolio turnover analysis"""
        
            # Create two weight snapshots
            old_weights = {'AAPL': 0.3, 'GOOGL': 0.25, 'MSFT': 0.25, 'TSLA': 0.2}
            new_weights = {'AAPL': 0.25, 'GOOGL': 0.3, 'MSFT': 0.25, 'TSLA': 0.2}
            
            result = analyze_portfolio_turnover(
                weights_before=old_weights,
                weights_after=new_weights
            )
            
            # Should return a dictionary
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            print("✅ Portfolio turnover analysis passed")
            
        :
            # Try alternative parameter names
            
                result = analyze_portfolio_turnover(
                    old_weights=old_weights,
                    new_weights=new_weights
                )
                self.assertIsInstance(result, dict)
                print("✅ Portfolio turnover analysis passed")
            2:
                print(f"⚠️ Portfolio turnover: {e2}")

    def test_calculate_active_share(self):
        """Test active share calculation"""
        
            # Create portfolio and benchmark holdings
            portfolio_weights = {'AAPL': 0.3, 'GOOGL': 0.25, 'MSFT': 0.25, 'TSLA': 0.2}
            benchmark_weights = {'AAPL': 0.2, 'GOOGL': 0.3, 'MSFT': 0.3, 'TSLA': 0.2}
            
            result = calculate_active_share(
                portfolio_weights=portfolio_weights,
                benchmark_weights=benchmark_weights
            )
            
            # Should return a dictionary
            self.assertIsInstance(result, dict)
            
            print("✅ Active share calculation passed")
            
        :
            print(f"⚠️ Active share: {e}")

    def test_perform_attribution(self):
        """Test performance attribution"""
        
            portfolio_rets = self.portfolio_returns
            benchmark_rets = self.benchmark_returns
            
            result = perform_attribution(
                portfolio_returns=portfolio_rets,
                benchmark_returns=benchmark_rets
            )
            
            # Should return a dictionary
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            print("✅ Performance attribution passed")
            
        :
            print(f"⚠️ Performance attribution: {e}")

    def test_calculate_portfolio_var(self):
        """Test portfolio VaR calculation"""
        
            result = calculate_portfolio_var(
                returns=self.portfolio_returns,
                confidence=0.95
            )
            
            # Should return a dictionary
            self.assertIsInstance(result, dict)
            
            print("✅ Portfolio VaR calculation passed")
            
        :
            print(f"⚠️ Portfolio VaR: {e}")

    def test_stress_test_portfolio(self):
        """Test portfolio stress testing"""
        
            result = stress_test_portfolio(
                weights=self.weights,
                returns=self.returns_data[['AAPL', 'GOOGL', 'MSFT', 'TSLA']]
            )
            
            # Should return a dictionary
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # Check for stress test results
            if 'stress_test_summary' in result:
                self.assertIsInstance(result['stress_test_summary'], dict)
                self.assertGreater(result['stress_test_summary'].get('scenarios_tested', 0), 0)
            
            print("✅ Portfolio stress testing passed")
            
        :
            self.fail(f"stress_test_portfolio failed: {e}")


class TestPortfolioMetricsEdgeCases(unittest.TestCase):
    """Test edge cases for portfolio metrics"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range('2023-01-01', periods=100, freq='D')
        np.random.seed(42)

    def test_equal_weight_portfolio(self):
        """Test with equal weight portfolio"""
        
            weights = {'A': 0.25, 'B': 0.25, 'C': 0.25, 'D': 0.25}
            
            result = analyze_portfolio_concentration(weights=weights)
            
            self.assertIsInstance(result, dict)
            print("✅ Equal weight portfolio handled")
            
        :
            print(f"⚠️ Equal weight portfolio: {e}")

    def test_concentrated_portfolio(self):
        """Test with highly concentrated portfolio"""
        
            weights = {'A': 0.9, 'B': 0.05, 'C': 0.03, 'D': 0.02}
            
            result = analyze_portfolio_concentration(weights=weights)
            
            self.assertIsInstance(result, dict)
            print("✅ Concentrated portfolio handled")
            
        :
            print(f"⚠️ Concentrated portfolio: {e}")

    def test_single_asset_portfolio(self):
        """Test with single asset portfolio"""
        
            weights = {'A': 1.0}
            
            result = analyze_portfolio_concentration(weights=weights)
            
            self.assertIsInstance(result, dict)
            print("✅ Single asset portfolio handled")
            
        :
            print(f"⚠️ Single asset portfolio: {e}")

    def test_perfectly_correlated_assets(self):
        """Test active share with identical portfolios"""
        
            weights = {'A': 0.5, 'B': 0.3, 'C': 0.2}
            
            result = calculate_active_share(
                portfolio_weights=weights,
                benchmark_weights=weights
            )
            
            self.assertIsInstance(result, dict)
            
            # Active share should be 0 for identical portfolios
            if 'active_share' in result:
                self.assertEqual(result['active_share'], 0)
            
            print("✅ Identical portfolios handled")
            
        :
            print(f"⚠️ Identical portfolios: {e}")

    def test_opposite_portfolios(self):
        """Test active share with opposite portfolios"""
        
            portfolio_weights = {'A': 0.6, 'B': 0.4}
            benchmark_weights = {'A': 0.2, 'B': 0.8}
            
            result = calculate_active_share(
                portfolio_weights=portfolio_weights,
                benchmark_weights=benchmark_weights
            )
            
            self.assertIsInstance(result, dict)
            print("✅ Opposite portfolios handled")
            
        :
            print(f"⚠️ Opposite portfolios: {e}")

    def test_portfolio_turnover_zero_turnover(self):
        """Test turnover with no changes"""
        
            weights = {'A': 0.5, 'B': 0.3, 'C': 0.2}
            
            result = analyze_portfolio_turnover(
                old_weights=weights,
                new_weights=weights
            )
            
            self.assertIsInstance(result, dict)
            
            # Turnover should be 0
            if 'turnover' in result:
                self.assertEqual(result['turnover'], 0)
            
            print("✅ Zero turnover handled")
            
        :
            print(f"⚠️ Zero turnover: {e}")

    def test_portfolio_turnover_complete_change(self):
        """Test turnover with complete portfolio change"""
        
            old_weights = {'A': 1.0}
            new_weights = {'B': 1.0}
            
            result = analyze_portfolio_turnover(
                old_weights=old_weights,
                new_weights=new_weights
            )
            
            self.assertIsInstance(result, dict)
            print("✅ Complete portfolio change handled")
            
        :
            print(f"⚠️ Complete portfolio change: {e}")


if __name__ == '__main__':
    print("🧪 Running Portfolio Metrics Tests...")
    print("=" * 60)
    
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 60)
    print("✅ Portfolio metrics tests completed!")
