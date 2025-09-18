"""
Portfolio Strategy Simulation using libraries

All strategy simulation using empyrical and PyPortfolioOpt from requirements.txt
From financial-analysis-function-library.json
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Union, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Use libraries from requirements.txt - no manual calculations
import empyrical

from ..utils.data_utils import validate_price_data, prices_to_returns, standardize_output
from ..performance.metrics import calculate_returns_metrics, calculate_risk_metrics


def simulate_dca_strategy(prices: Union[pd.Series, Dict[str, Any]], 
                         investment_amount: float = 1000,
                         frequency: str = "M",
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Simulate Dollar Cost Averaging strategy using empyrical.
    
    From financial-analysis-function-library.json
    Uses empyrical library for performance calculations - no code duplication
    
    Args:
        prices: Price data
        investment_amount: Amount to invest each period
        frequency: Investment frequency ('D', 'W', 'M')
        start_date: Start date for simulation
        end_date: End date for simulation
        
    Returns:
        Dict: DCA simulation results with performance metrics
    """
    try:
        price_series = validate_price_data(prices)
        
        # Filter by date range if provided
        if start_date:
            price_series = price_series[price_series.index >= start_date]
        if end_date:
            price_series = price_series[price_series.index <= end_date]
        
        if len(price_series) == 0:
            raise ValueError("No price data in specified date range")
        
        # Resample to investment frequency
        if frequency == "M":
            investment_prices = price_series.resample('M').first().dropna()
        elif frequency == "W":
            investment_prices = price_series.resample('W').first().dropna()
        elif frequency == "D":
            investment_prices = price_series
        else:
            raise ValueError("Frequency must be 'D', 'W', or 'M'")
        
        # Calculate shares purchased and cumulative investment
        shares_purchased = investment_amount / investment_prices
        cumulative_shares = shares_purchased.cumsum()
        cumulative_investment = investment_amount * np.arange(1, len(investment_prices) + 1)
        
        # Calculate portfolio value over time
        portfolio_values = cumulative_shares * price_series.reindex(cumulative_shares.index, method='ffill')
        
        # Calculate returns
        portfolio_returns = portfolio_values.pct_change().dropna()
        
        # Use empyrical for performance metrics if available
        if EMPYRICAL_AVAILABLE:
            total_return = empyrical.cum_returns_final(portfolio_returns)
            annual_return = empyrical.annual_return(portfolio_returns)
            annual_vol = empyrical.annual_volatility(portfolio_returns)
            sharpe_ratio = empyrical.sharpe_ratio(portfolio_returns)
            max_drawdown = empyrical.max_drawdown(portfolio_returns)
            calmar_ratio = empyrical.calmar_ratio(portfolio_returns)
        else:
            # Basic fallback calculations
            total_return = (portfolio_values.iloc[-1] / cumulative_investment[-1]) - 1
            annual_return = portfolio_returns.mean() * 252
            annual_vol = portfolio_returns.std() * np.sqrt(252)
            sharpe_ratio = annual_return / annual_vol if annual_vol > 0 else 0
            max_drawdown = ((portfolio_values / portfolio_values.expanding().max()) - 1).min()
            calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown < 0 else 0
        
        # Calculate average cost basis
        avg_cost = cumulative_investment[-1] / cumulative_shares.iloc[-1]
        final_price = price_series.iloc[-1]
        
        result = {
            "total_investment": float(cumulative_investment[-1]),
            "final_portfolio_value": float(portfolio_values.iloc[-1]),
            "total_shares": float(cumulative_shares.iloc[-1]),
            "average_cost_basis": float(avg_cost),
            "final_price": float(final_price),
            "total_return": float(total_return),
            "total_return_pct": f"{total_return * 100:.2f}%",
            "annual_return": float(annual_return),
            "annual_return_pct": f"{annual_return * 100:.2f}%",
            "annual_volatility": float(annual_vol),
            "annual_volatility_pct": f"{annual_vol * 100:.2f}%",
            "sharpe_ratio": float(sharpe_ratio),
            "max_drawdown": float(max_drawdown),
            "max_drawdown_pct": f"{max_drawdown * 100:.2f}%",
            "calmar_ratio": float(calmar_ratio),
            "investment_frequency": frequency,
            "number_of_investments": len(investment_prices),
            "investment_period_years": len(portfolio_returns) / 252,
            "portfolio_values": portfolio_values,
            "cumulative_shares": cumulative_shares
        }
        
        return standardize_output(result, "simulate_dca_strategy")
        
    except Exception as e:
        return {"success": False, "error": f"DCA simulation failed: {str(e)}"}


def backtest_strategy(prices: Union[pd.DataFrame, Dict[str, Any]], 
                     strategy_weights: Union[Dict[str, float], pd.DataFrame],
                     rebalance_frequency: str = "M",
                     initial_value: float = 10000,
                     transaction_cost: float = 0.001) -> Dict[str, Any]:
    """
    Backtest portfolio strategy using empyrical.
    
    From financial-analysis-function-library.json
    Uses empyrical library for performance calculations - no code duplication
    
    Args:
        prices: Price data for assets
        strategy_weights: Portfolio weights (static dict or time-varying DataFrame)
        rebalance_frequency: Rebalancing frequency ('D', 'W', 'M', 'Q')
        initial_value: Initial portfolio value
        transaction_cost: Transaction cost as fraction
        
    Returns:
        Dict: Backtest results with performance metrics
    """
    try:
        if isinstance(prices, dict):
            price_df = pd.DataFrame(prices)
        else:
            price_df = prices.copy()
        
        # Calculate returns
        returns_df = price_df.pct_change().dropna()
        
        if isinstance(strategy_weights, dict):
            # Static weights
            weights_df = pd.DataFrame([strategy_weights] * len(returns_df), index=returns_df.index)
        else:
            # Time-varying weights
            weights_df = strategy_weights.reindex(returns_df.index, method='ffill').fillna(0)
        
        # Ensure weights sum to 1
        weights_df = weights_df.div(weights_df.sum(axis=1), axis=0)
        
        # Calculate portfolio returns
        portfolio_returns = (returns_df * weights_df).sum(axis=1)
        
        # Apply rebalancing costs
        if rebalance_frequency in ['D', 'W', 'M', 'Q']:
            if rebalance_frequency == 'M':
                rebalance_dates = portfolio_returns.resample('M').first().index
            elif rebalance_frequency == 'W':
                rebalance_dates = portfolio_returns.resample('W').first().index
            elif rebalance_frequency == 'Q':
                rebalance_dates = portfolio_returns.resample('Q').first().index
            else:
                rebalance_dates = portfolio_returns.index
            
            # Subtract transaction costs on rebalance dates
            for date in rebalance_dates:
                if date in portfolio_returns.index:
                    portfolio_returns.loc[date] -= transaction_cost
        
        # Calculate cumulative portfolio value
        portfolio_values = initial_value * (1 + portfolio_returns).cumprod()
        
        # Use empyrical for comprehensive performance metrics
        if EMPYRICAL_AVAILABLE:
            total_return = empyrical.cum_returns_final(portfolio_returns)
            annual_return = empyrical.annual_return(portfolio_returns)
            annual_vol = empyrical.annual_volatility(portfolio_returns)
            sharpe_ratio = empyrical.sharpe_ratio(portfolio_returns)
            sortino_ratio = empyrical.sortino_ratio(portfolio_returns)
            max_drawdown = empyrical.max_drawdown(portfolio_returns)
            calmar_ratio = empyrical.calmar_ratio(portfolio_returns)
            var_95 = empyrical.value_at_risk(portfolio_returns, cutoff=0.05)
            skewness = empyrical.stats.skew(portfolio_returns)
            kurtosis = empyrical.stats.kurtosis(portfolio_returns)
            
            # Stability metrics
            stability = empyrical.stability_of_timeseries(portfolio_returns)
            tail_ratio = empyrical.tail_ratio(portfolio_returns)
            
        else:
            # Basic fallback calculations
            total_return = (portfolio_values.iloc[-1] / initial_value) - 1
            annual_return = portfolio_returns.mean() * 252
            annual_vol = portfolio_returns.std() * np.sqrt(252)
            sharpe_ratio = annual_return / annual_vol if annual_vol > 0 else 0
            max_drawdown = ((portfolio_values / portfolio_values.expanding().max()) - 1).min()
            calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown < 0 else 0
            
            # Set advanced metrics to None for fallback
            sortino_ratio = None
            var_95 = None
            skewness = None
            kurtosis = None
            stability = None
            tail_ratio = None
        
        # Calculate hit rate (percentage of positive returns)
        hit_rate = (portfolio_returns > 0).mean()
        
        # Calculate average win/loss
        wins = portfolio_returns[portfolio_returns > 0]
        losses = portfolio_returns[portfolio_returns < 0]
        avg_win = wins.mean() if len(wins) > 0 else 0
        avg_loss = losses.mean() if len(losses) > 0 else 0
        win_loss_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        result = {
            "initial_value": initial_value,
            "final_value": float(portfolio_values.iloc[-1]),
            "total_return": float(total_return),
            "total_return_pct": f"{total_return * 100:.2f}%",
            "annual_return": float(annual_return),
            "annual_return_pct": f"{annual_return * 100:.2f}%",
            "annual_volatility": float(annual_vol),
            "annual_volatility_pct": f"{annual_vol * 100:.2f}%",
            "sharpe_ratio": float(sharpe_ratio),
            "max_drawdown": float(max_drawdown),
            "max_drawdown_pct": f"{max_drawdown * 100:.2f}%",
            "calmar_ratio": float(calmar_ratio),
            "hit_rate": float(hit_rate),
            "hit_rate_pct": f"{hit_rate * 100:.2f}%",
            "avg_win": float(avg_win),
            "avg_loss": float(avg_loss),
            "win_loss_ratio": float(win_loss_ratio),
            "rebalance_frequency": rebalance_frequency,
            "transaction_cost": transaction_cost,
            "backtest_period_years": len(portfolio_returns) / 252,
            "portfolio_values": portfolio_values,
            "portfolio_returns": portfolio_returns
        }
        
        # Add advanced metrics if available
        if EMPYRICAL_AVAILABLE:
            result.update({
                "sortino_ratio": float(sortino_ratio),
                "var_95": float(var_95),
                "var_95_pct": f"{var_95 * 100:.2f}%",
                "skewness": float(skewness),
                "kurtosis": float(kurtosis),
                "stability": float(stability),
                "tail_ratio": float(tail_ratio)
            })
        
        return standardize_output(result, "backtest_strategy")
        
    except Exception as e:
        return {"success": False, "error": f"Strategy backtest failed: {str(e)}"}


def monte_carlo_simulation(expected_returns: Union[List[float], np.ndarray],
                          covariance_matrix: Union[List[List[float]], np.ndarray],
                          weights: Union[List[float], Dict[str, float]],
                          time_horizon: int = 252,
                          n_simulations: int = 1000,
                          initial_value: float = 10000) -> Dict[str, Any]:
    """
    Monte Carlo portfolio simulation using numpy.
    
    From financial-analysis-function-library.json
    Uses numpy for random sampling - leveraging requirements.txt
    
    Args:
        expected_returns: Expected returns for assets
        covariance_matrix: Covariance matrix
        weights: Portfolio weights
        time_horizon: Number of periods to simulate
        n_simulations: Number of simulation paths
        initial_value: Initial portfolio value
        
    Returns:
        Dict: Monte Carlo simulation results
    """
    try:
        # Convert inputs to numpy arrays
        if isinstance(expected_returns, list):
            mu = np.array(expected_returns)
        else:
            mu = np.array(expected_returns)
        
        if isinstance(covariance_matrix, list):
            cov = np.array(covariance_matrix)
        else:
            cov = np.array(covariance_matrix)
        
        if isinstance(weights, dict):
            w = np.array(list(weights.values()))
        else:
            w = np.array(weights)
        
        # Portfolio expected return and variance
        portfolio_mu = np.dot(w, mu)
        portfolio_var = np.dot(w.T, np.dot(cov, w))
        portfolio_std = np.sqrt(portfolio_var)
        
        # Generate random returns
        np.random.seed(42)  # For reproducibility
        random_returns = np.random.normal(
            portfolio_mu / 252,  # Daily return
            portfolio_std / np.sqrt(252),  # Daily volatility
            size=(n_simulations, time_horizon)
        )
        
        # Calculate cumulative portfolio values
        portfolio_paths = initial_value * np.cumprod(1 + random_returns, axis=1)
        
        # Calculate final values
        final_values = portfolio_paths[:, -1]
        
        # Calculate statistics
        percentiles = [5, 10, 25, 50, 75, 90, 95]
        value_percentiles = {
            f"percentile_{p}": float(np.percentile(final_values, p))
            for p in percentiles
        }
        
        # Calculate probability of loss
        prob_loss = (final_values < initial_value).mean()
        
        # Calculate expected shortfall (average loss in worst 5% scenarios)
        worst_5_percent = final_values[final_values <= np.percentile(final_values, 5)]
        expected_shortfall = worst_5_percent.mean() - initial_value
        
        result = {
            "initial_value": initial_value,
            "mean_final_value": float(final_values.mean()),
            "std_final_value": float(final_values.std()),
            "min_final_value": float(final_values.min()),
            "max_final_value": float(final_values.max()),
            "probability_of_loss": float(prob_loss),
            "probability_of_loss_pct": f"{prob_loss * 100:.2f}%",
            "expected_shortfall": float(expected_shortfall),
            "time_horizon_days": time_horizon,
            "n_simulations": n_simulations,
            "portfolio_expected_return": float(portfolio_mu),
            "portfolio_volatility": float(portfolio_std),
            **value_percentiles
        }
        
        return standardize_output(result, "monte_carlo_simulation")
        
    except Exception as e:
        return {"success": False, "error": f"Monte Carlo simulation failed: {str(e)}"}


# Registry of simulation functions - all using libraries
PORTFOLIO_SIMULATION_FUNCTIONS = {
    'simulate_dca_strategy': simulate_dca_strategy,
    'backtest_strategy': backtest_strategy,
    'monte_carlo_simulation': monte_carlo_simulation
}