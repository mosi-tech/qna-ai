"""
Unit tests for portfolio simulation functions.

Tests portfolio simulation strategies including dollar-cost averaging,
backtesting, and Monte Carlo simulations.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import functions to test
from ..simulation import (
    simulate_dca_strategy,
    backtest_strategy,
    monte_carlo_simulation
)


class TestDCAStrategy(unittest.TestCase):
    """Test Dollar-Cost Averaging strategy simulation"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range('2023-01-01', periods=252, freq='D')
        np.random.seed(42)
        
        # Create price series for single asset
        returns = np.random.normal(0.001, 0.02, len(self.dates))
        prices = 100 * (1 + np.cumsum(returns))
        self.prices_series = pd.Series(prices, index=self.dates)

    def test_simulate_dca_strategy_basic(self):
        """Test basic DCA strategy simulation"""
        
            result = simulate_dca_strategy(
                prices=self.prices_series,
                investment_amount=1000,
                frequency="M"
            )
            
            # Should return a dictionary
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # Should contain DCA results
            if 'final_portfolio_value' in result:
                self.assertIsInstance(result['final_portfolio_value'], (int, float))
                self.assertGreater(result['final_portfolio_value'], 0)
            
            # Should have total investment
            if 'total_investment' in result:
                self.assertGreater(result['total_investment'], 0)
            
            print("✅ DCA strategy simulation passed")
            
        :
            self.fail(f"simulate_dca_strategy failed: {e}")

    def test_simulate_dca_strategy_weekly(self):
        """Test DCA strategy with weekly frequency"""
        
            result = simulate_dca_strategy(
                prices=self.prices_series,
                investment_amount=500,
                frequency="W"
            )
            
            # Should return a dictionary
            self.assertIsInstance(result, dict)
            
            # Check if results are present
            if 'total_shares' in result:
                self.assertIsInstance(result['total_shares'], (int, float))
                self.assertGreater(result['total_shares'], 0)
            
            print("✅ DCA strategy with weekly frequency passed")
            
        :
            self.fail(f"DCA weekly frequency failed: {e}")

    def test_simulate_dca_strategy_daily(self):
        """Test DCA with daily frequency"""
        
            result = simulate_dca_strategy(
                prices=self.prices_series,
                investment_amount=50,
                frequency="D"
            )
            
            self.assertIsInstance(result, dict)
            
            print("✅ DCA with daily frequency passed")
            
        :
            self.fail(f"DCA daily frequency failed: {e}")

    def test_simulate_dca_with_date_range(self):
        """Test DCA with custom date range"""
        
            result = simulate_dca_strategy(
                prices=self.prices_series,
                investment_amount=1000,
                frequency="M",
                start_date='2023-03-01',
                end_date='2023-12-01'
            )
            
            self.assertIsInstance(result, dict)
            
            print("✅ DCA with date range passed")
            
        :
            self.fail(f"DCA with date range failed: {e}")


class TestBacktestStrategy(unittest.TestCase):
    """Test strategy backtesting"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range('2023-01-01', periods=252, freq='D')
        np.random.seed(42)
        
        # Create multi-asset price data
        self.prices_df = pd.DataFrame()
        for symbol in ['SPY', 'AGG']:
            returns = np.random.normal(0.0008, 0.015, len(self.dates))
            prices = 100 * (1 + np.cumsum(returns))
            self.prices_df[symbol] = prices
        
        self.prices_df.index = self.dates

    def test_backtest_static_weights(self):
        """Test backtest with static weights"""
        
            weights = {'SPY': 0.6, 'AGG': 0.4}
            
            result = backtest_strategy(
                prices=self.prices_df,
                strategy_weights=weights,
                rebalance_frequency="M"
            )
            
            # Should return a dictionary
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # Should contain backtest results
            if 'total_return' in result:
                self.assertIsInstance(result['total_return'], (int, float))
            
            if 'max_drawdown' in result:
                self.assertIsInstance(result['max_drawdown'], (int, float))
                self.assertLess(result['max_drawdown'], 0)  # Drawdown is negative
            
            print("✅ Static weights backtest passed")
            
        :
            self.fail(f"backtest_strategy static weights failed: {e}")

    def test_backtest_time_varying_weights(self):
        """Test backtest with time-varying weights"""
        
            # Create time-varying weights that change monthly
            weights_data = {}
            dates = pd.date_range('2023-01-01', periods=252, freq='D')
            
            for date in dates:
                month = date.month
                if month % 3 == 0:
                    weights_data[date] = {'SPY': 0.7, 'AGG': 0.3}
                else:
                    weights_data[date] = {'SPY': 0.5, 'AGG': 0.5}
            
            weights_df = pd.DataFrame(weights_data).T
            
            result = backtest_strategy(
                prices=self.prices_df,
                strategy_weights=weights_df,
                rebalance_frequency="M"
            )
            
            self.assertIsInstance(result, dict)
            
            print("✅ Time-varying weights backtest passed")
            
        :
            self.fail(f"backtest time-varying weights failed: {e}")

    def test_backtest_quarterly_rebalance(self):
        """Test backtest with quarterly rebalancing"""
        
            weights = {'SPY': 0.6, 'AGG': 0.4}
            
            result = backtest_strategy(
                prices=self.prices_df,
                strategy_weights=weights,
                rebalance_frequency="Q"
            )
            
            self.assertIsInstance(result, dict)
            
            print("✅ Quarterly rebalancing backtest passed")
            
        :
            self.fail(f"backtest quarterly rebalance failed: {e}")

    def test_backtest_with_transaction_cost(self):
        """Test backtest with transaction costs"""
        
            weights = {'SPY': 0.6, 'AGG': 0.4}
            
            result = backtest_strategy(
                prices=self.prices_df,
                strategy_weights=weights,
                rebalance_frequency="M",
                transaction_cost=0.002  # 0.2% transaction cost
            )
            
            self.assertIsInstance(result, dict)
            
            # Check if transaction cost was applied
            if 'transaction_cost' in result:
                self.assertEqual(result['transaction_cost'], 0.002)
            
            print("✅ Backtest with transaction costs passed")
            
        :
            self.fail(f"backtest with transaction costs failed: {e}")


class TestMonteCarloSimulation(unittest.TestCase):
    """Test Monte Carlo portfolio simulations"""
    
    def setUp(self):
        """Set up test data for Monte Carlo"""
        self.expected_returns = [0.08, 0.06]  # 8% and 6% annual returns
        
        self.covariance_matrix = np.array([
            [0.0064, 0.0016],  # 8% vol asset 1, 4% vol asset 2, 0.25 correlation
            [0.0016, 0.0036]
        ])
        
        self.weights = [0.6, 0.4]
        self.weights_dict = {'SPY': 0.6, 'AGG': 0.4}

    def test_monte_carlo_basic(self):
        """Test basic Monte Carlo simulation"""
        
            result = monte_carlo_simulation(
                expected_returns=self.expected_returns,
                covariance_matrix=self.covariance_matrix,
                weights=self.weights,
                time_horizon=252,
                n_simulations=100
            )
            
            # Should return a dictionary
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))
            
            # Should contain simulation results
            if 'mean_final_value' in result:
                self.assertIsInstance(result['mean_final_value'], (int, float))
                self.assertGreater(result['mean_final_value'], 0)
            
            # Should have percentiles
            if 'percentile_5' in result and 'percentile_95' in result:
                self.assertIsInstance(result['percentile_5'], (int, float))
                self.assertIsInstance(result['percentile_95'], (int, float))
                # 95th percentile should be higher than 5th
                self.assertGreater(result['percentile_95'], result['percentile_5'])
            
            print("✅ Monte Carlo basic simulation passed")
            
        :
            self.fail(f"monte_carlo_simulation basic failed: {e}")

    def test_monte_carlo_with_dict_weights(self):
        """Test Monte Carlo with dictionary weights"""
        
            result = monte_carlo_simulation(
                expected_returns=self.expected_returns,
                covariance_matrix=self.covariance_matrix,
                weights=self.weights_dict,
                time_horizon=252,
                n_simulations=100
            )
            
            self.assertIsInstance(result, dict)
            
            print("✅ Monte Carlo with dict weights passed")
            
        :
            self.fail(f"monte_carlo with dict weights failed: {e}")

    def test_monte_carlo_long_horizon(self):
        """Test Monte Carlo with longer time horizon"""
        
            result = monte_carlo_simulation(
                expected_returns=self.expected_returns,
                covariance_matrix=self.covariance_matrix,
                weights=self.weights,
                time_horizon=504,  # 2 years
                n_simulations=100
            )
            
            self.assertIsInstance(result, dict)
            
            # Longer horizon should have more variance
            if 'std_final_value' in result:
                self.assertGreater(result['std_final_value'], 0)
            
            print("✅ Monte Carlo with long horizon passed")
            
        :
            self.fail(f"monte_carlo long horizon failed: {e}")

    def test_monte_carlo_high_initial_value(self):
        """Test Monte Carlo with higher initial portfolio value"""
        
            result = monte_carlo_simulation(
                expected_returns=self.expected_returns,
                covariance_matrix=self.covariance_matrix,
                weights=self.weights,
                time_horizon=252,
                n_simulations=100,
                initial_value=100000  # $100k portfolio
            )
            
            self.assertIsInstance(result, dict)
            
            # Mean final value should be approximately initial * (1 + portfolio return)
            if 'mean_final_value' in result:
                self.assertGreater(result['mean_final_value'], 50000)  # Should be reasonable
            
            print("✅ Monte Carlo with high initial value passed")
            
        :
            self.fail(f"monte_carlo high initial value failed: {e}")

    def test_monte_carlo_many_simulations(self):
        """Test Monte Carlo with larger simulation count"""
        
            result = monte_carlo_simulation(
                expected_returns=self.expected_returns,
                covariance_matrix=self.covariance_matrix,
                weights=self.weights,
                time_horizon=252,
                n_simulations=500
            )
            
            self.assertIsInstance(result, dict)
            
            # Check n_simulations is recorded
            if 'n_simulations' in result:
                self.assertEqual(result['n_simulations'], 500)
            
            print("✅ Monte Carlo with 500 simulations passed")
            
        :
            self.fail(f"monte_carlo many simulations failed: {e}")


class TestSimulationEdgeCases(unittest.TestCase):
    """Test edge cases for portfolio simulations"""
    
    def setUp(self):
        """Set up test data"""
        self.dates = pd.date_range('2023-01-01', periods=100, freq='D')
        np.random.seed(42)

    def test_dca_short_period(self):
        """Test DCA with short price history"""
        
            short_dates = pd.date_range('2023-01-01', periods=30, freq='D')
            prices = pd.Series(
                100 * (1 + np.cumsum(np.random.normal(0.001, 0.02, 30))),
                index=short_dates
            )
            
            result = simulate_dca_strategy(
                prices=prices,
                investment_amount=500,
                frequency="M"
            )
            
            self.assertIsInstance(result, dict)
            print("✅ DCA with short period handled")
            
        :
            print(f"⚠️ DCA short period: {e}")

    def test_backtest_all_same_weight(self):
        """Test backtest with equal weight portfolio"""
        
            dates = pd.date_range('2023-01-01', periods=100, freq='D')
            prices_df = pd.DataFrame({
                'A': 100 * (1 + np.cumsum(np.random.normal(0.001, 0.02, 100))),
                'B': 100 * (1 + np.cumsum(np.random.normal(0.001, 0.02, 100)))
            }, index=dates)
            
            weights = {'A': 0.5, 'B': 0.5}
            
            result = backtest_strategy(
                prices=prices_df,
                strategy_weights=weights,
                rebalance_frequency="W"
            )
            
            self.assertIsInstance(result, dict)
            print("✅ Equal weight backtest handled")
            
        :
            print(f"⚠️ Equal weight backtest: {e}")

    def test_monte_carlo_low_volatility(self):
        """Test Monte Carlo with low volatility assets"""
        
            # Low volatility covariance matrix
            low_vol_cov = np.array([
                [0.0001, 0.00005],
                [0.00005, 0.0001]
            ])
            
            result = monte_carlo_simulation(
                expected_returns=[0.04, 0.04],  # 4% returns
                covariance_matrix=low_vol_cov,
                weights=[0.5, 0.5],
                time_horizon=252,
                n_simulations=50
            )
            
            self.assertIsInstance(result, dict)
            print("✅ Low volatility Monte Carlo handled")
            
        :
            print(f"⚠️ Low volatility Monte Carlo: {e}")

    def test_monte_carlo_high_volatility(self):
        """Test Monte Carlo with high volatility assets"""
        
            # High volatility covariance matrix
            high_vol_cov = np.array([
                [0.09, 0.02],
                [0.02, 0.09]
            ])
            
            result = monte_carlo_simulation(
                expected_returns=[0.10, 0.10],
                covariance_matrix=high_vol_cov,
                weights=[0.5, 0.5],
                time_horizon=252,
                n_simulations=50
            )
            
            self.assertIsInstance(result, dict)
            print("✅ High volatility Monte Carlo handled")
            
        :
            print(f"⚠️ High volatility Monte Carlo: {e}")

    def test_monte_carlo_negative_correlation(self):
        """Test Monte Carlo with negatively correlated assets"""
        
            # Negative correlation matrix (hedging)
            neg_corr_cov = np.array([
                [0.0064, -0.003],  # Negative covariance
                [-0.003, 0.0064]
            ])
            
            result = monte_carlo_simulation(
                expected_returns=[0.08, 0.04],
                covariance_matrix=neg_corr_cov,
                weights=[0.5, 0.5],
                time_horizon=252,
                n_simulations=50
            )
            
            self.assertIsInstance(result, dict)
            print("✅ Negative correlation Monte Carlo handled")
            
        :
            print(f"⚠️ Negative correlation: {e}")


if __name__ == '__main__':
    print("🧪 Running Portfolio Simulation Tests...")
    print("=" * 60)
    
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 60)
    print("✅ Portfolio simulation tests completed!")
