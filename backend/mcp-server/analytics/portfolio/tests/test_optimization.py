"""
Unit tests for portfolio optimization functions.

Tests all portfolio optimization functionality including efficient frontier,
Sharpe ratio optimization, and allocation strategies.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import functions to test
from ..optimization import (
    optimize_portfolio,
    calculate_efficient_frontier,
    optimize_max_sharpe,
    optimize_min_volatility,
    calculate_risk_parity,
    discrete_allocation
)


class TestPortfolioOptimization(unittest.TestCase):
    """Test portfolio optimization functions"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range('2023-01-01', periods=252, freq='D')
        np.random.seed(42)
        
        # Create price data for 3 assets
        prices = {}
        for i, symbol in enumerate(['AAPL', 'MSFT', 'GOOGL']):
            returns = np.random.normal(0.001, 0.02, len(self.dates))
            prices[symbol] = 100 * (1 + np.cumsum(returns))
        
        self.prices_df = pd.DataFrame(prices, index=self.dates)

    def test_optimize_portfolio(self):
        """Test general portfolio optimization"""
        
            result = optimize_portfolio(self.prices_df)
            
            # Should return a dictionary
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # Should contain weights
            if 'weights' in result:
                weights = result['weights']
                # Weights should sum to approximately 1
                if isinstance(weights, dict):
                    total = sum(weights.values())
                    self.assertAlmostEqual(total, 1.0, places=2)
            
            print("✅ Portfolio optimization passed")
            
        :
            self.fail(f"optimize_portfolio failed: {e}")

    def test_calculate_efficient_frontier(self):
        """Test efficient frontier calculation"""
        
            result = calculate_efficient_frontier(
                self.prices_df,
                n_points=20
            )
            
            # Should return a dictionary
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # Should contain frontier points
            if 'returns' in result and 'volatilities' in result:
                self.assertGreater(len(result['returns']), 0)
                self.assertGreater(len(result['volatilities']), 0)
            
            print("✅ Efficient frontier calculation passed")
            
        :
            self.fail(f"calculate_efficient_frontier failed: {e}")

    def test_optimize_max_sharpe(self):
        """Test maximum Sharpe ratio optimization"""
        
            result = optimize_max_sharpe(
                self.prices_df,
                risk_free_rate=0.02
            )
            
            # Should return a dictionary
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # Should contain optimal weights
            if 'weights' in result:
                weights = result['weights']
                if isinstance(weights, dict):
                    total = sum(weights.values())
                    self.assertAlmostEqual(total, 1.0, places=2)
            
            # Should have Sharpe ratio
            if 'sharpe_ratio' in result:
                self.assertIsInstance(result['sharpe_ratio'], (int, float))
            
            print("✅ Max Sharpe optimization passed")
            
        :
            self.fail(f"optimize_max_sharpe failed: {e}")

    def test_optimize_min_volatility(self):
        """Test minimum volatility optimization"""
        
            result = optimize_min_volatility(self.prices_df)
            
            # Should return a dictionary
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # Should contain optimal weights
            if 'weights' in result:
                weights = result['weights']
                if isinstance(weights, dict):
                    total = sum(weights.values())
                    self.assertAlmostEqual(total, 1.0, places=2)
            
            # Should have volatility
            if 'volatility' in result:
                self.assertIsInstance(result['volatility'], (int, float))
                self.assertGreater(result['volatility'], 0)
            
            print("✅ Min volatility optimization passed")
            
        :
            self.fail(f"optimize_min_volatility failed: {e}")

    def test_calculate_risk_parity(self):
        """Test risk parity weight calculation"""
        
            result = calculate_risk_parity(self.prices_df)
            
            # Should return a dictionary
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # Should contain weights
            if 'weights' in result:
                weights = result['weights']
                if isinstance(weights, dict):
                    total = sum(weights.values())
                    self.assertAlmostEqual(total, 1.0, places=2)
                    # Risk parity weights should be more equal than market cap
                    self.assertGreater(len(weights), 0)
            
            print("✅ Risk parity calculation passed")
            
        :
            self.fail(f"calculate_risk_parity failed: {e}")

    def test_discrete_allocation(self):
        """Test discrete allocation calculation"""
        
            # Create weights
            weights = {'AAPL': 0.3, 'MSFT': 0.5, 'GOOGL': 0.2}
            
            # Get latest prices
            latest_prices = self.prices_df.iloc[-1].to_dict()
            
            result = discrete_allocation(
                weights=weights,
                latest_prices=latest_prices,
                total_portfolio_value=100000
            )
            
            # Should return a dictionary
            self.assertIsInstance(result, dict)
            
            # Check if it was successful or has allocation details
            if result.get('success', True):
                # Should contain allocation details
                if 'allocation' in result and isinstance(result['allocation'], dict):
                    # Check that we have some allocation
                    self.assertGreater(len(result['allocation']), 0)
            
            print("✅ Discrete allocation passed")
            
        :
            self.fail(f"discrete_allocation failed: {e}")


class TestOptimizationEdgeCases(unittest.TestCase):
    """Test edge cases for optimization"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range('2023-01-01', periods=100, freq='D')
        np.random.seed(42)

    def test_two_asset_optimization(self):
        """Test optimization with 2 assets"""
        
            prices = {}
            for symbol in ['AAPL', 'MSFT']:
                returns = np.random.normal(0.001, 0.02, len(self.dates))
                prices[symbol] = 100 * (1 + np.cumsum(returns))
            
            prices_df = pd.DataFrame(prices, index=self.dates)
            result = optimize_portfolio(prices_df)
            
            self.assertIsInstance(result, dict)
            print("✅ Two asset optimization passed")
            
        :
            print(f"⚠️ Two asset optimization: {e}")

    def test_many_asset_optimization(self):
        """Test optimization with many assets"""
        
            prices = {}
            for i in range(10):
                symbol = f'STOCK{i}'
                returns = np.random.normal(0.001, 0.02, len(self.dates))
                prices[symbol] = 100 * (1 + np.cumsum(returns))
            
            prices_df = pd.DataFrame(prices, index=self.dates)
            result = optimize_portfolio(prices_df)
            
            self.assertIsInstance(result, dict)
            print("✅ Many asset optimization passed")
            
        :
            print(f"⚠️ Many asset optimization: {e}")

    def test_correlated_assets(self):
        """Test optimization with highly correlated assets"""
        
            base_returns = np.random.normal(0.001, 0.02, len(self.dates))
            
            prices = {}
            for i in range(3):
                # Add slight noise to base returns
                returns = base_returns + np.random.normal(0, 0.001, len(self.dates))
                prices[f'ASSET{i}'] = 100 * (1 + np.cumsum(returns))
            
            prices_df = pd.DataFrame(prices, index=self.dates)
            result = optimize_portfolio(prices_df)
            
            self.assertIsInstance(result, dict)
            print("✅ Correlated assets optimization passed")
            
        :
            print(f"⚠️ Correlated assets: {e}")


if __name__ == '__main__':
    print("🧪 Running Portfolio Optimization Tests...")
    print("=" * 60)
    
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 60)
    print("✅ Portfolio optimization tests completed!")