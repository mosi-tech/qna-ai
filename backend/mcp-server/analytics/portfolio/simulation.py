"""Portfolio strategy simulation using industry-standard libraries.

This module provides comprehensive portfolio and investment strategy simulation
functionality including Dollar Cost Averaging (DCA) strategies, portfolio
backtesting, and Monte Carlo simulation. All calculations leverage established
libraries from requirements.txt (empyrical, numpy) to ensure accuracy and
avoid code duplication.

Functions are designed to integrate with the financial-analysis-function-library.json
specification and provide standardized outputs for the MCP analytics server.

Example:
    Basic strategy simulation workflow:
    
    >>> from mcp.analytics.portfolio.simulation import simulate_dca_strategy
    >>> import pandas as pd
    >>> price_data = pd.Series(...)  # Historical price data
    >>> dca_results = simulate_dca_strategy(price_data, investment_amount=1000)
    >>> print(f"Total return: {dca_results['total_return_pct']}")
    
Note:
    All simulation functions use empyrical for performance calculations
    and provide comprehensive metrics for strategy evaluation.
"""



import pandas as pd
import numpy as np
from typing import Dict, List, Any, Union, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Use libraries from requirements.txt - empyrical is guaranteed to be available
import empyrical

from ..utils.data_utils import validate_price_data, prices_to_returns, standardize_output
from ..performance.metrics import calculate_returns_metrics, calculate_risk_metrics


def simulate_dca_strategy(prices: Union[pd.Series, Dict[str, Any]], 
                         investment_amount: float = 1000,
                         frequency: str = "M",
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None) -> Dict[str, Any]:
    """Simulate Dollar Cost Averaging (DCA) investment strategy.
    
    Dollar Cost Averaging involves investing a fixed amount at regular intervals
    regardless of market conditions. This function simulates the strategy by
    calculating shares purchased at each interval, tracking portfolio value over
    time, and computing comprehensive performance metrics using the empyrical library.
    
    Args:
        prices: Historical price data for the asset. Can be provided as pandas
            Series with dates as index, or dictionary with dates as keys and
            prices as values.
        investment_amount: Fixed dollar amount to invest at each interval.
            Defaults to $1000.
        frequency: Investment frequency for DCA strategy. Options:
            - "D": Daily investment
            - "W": Weekly investment (first trading day of week)
            - "M": Monthly investment (first trading day of month)
            Defaults to "M" (monthly).
        start_date: Optional start date for simulation. If provided, only
            price data from this date onwards will be used. Format: 'YYYY-MM-DD'.
        end_date: Optional end date for simulation. If provided, only
            price data up to this date will be used. Format: 'YYYY-MM-DD'.
            
    Returns:
        Dict[str, Any]: DCA simulation results including:
            - total_investment: Total amount invested over the period
            - final_portfolio_value: Final value of accumulated shares
            - total_shares: Total shares accumulated through DCA
            - average_cost_basis: Average price paid per share
            - Performance metrics: Total return, annual return, volatility, Sharpe ratio
            - Risk metrics: Maximum drawdown, Calmar ratio
            - Strategy details: Investment frequency, number of investments, time series data
            
    Raises:
        ValueError: If invalid frequency specified or no data in date range.
        Exception: If DCA simulation fails due to data or calculation issues.
        
    Example:
        >>> import pandas as pd
        >>> # Simulate monthly DCA of $1000 into AAPL
        >>> aapl_prices = pd.Series(...)  # Historical AAPL prices
        >>> dca_result = simulate_dca_strategy(aapl_prices, investment_amount=1000, frequency="M")
        >>> print(f"Total invested: ${dca_result['total_investment']:,.0f}")
        >>> print(f"Final value: ${dca_result['final_portfolio_value']:,.0f}")
        >>> print(f"Total return: {dca_result['total_return_pct']}")
        >>> print(f"Average cost: ${dca_result['average_cost_basis']:.2f}")
        
    Note:
        - Investments occur at the first available price in each period
        - Shares are accumulated and valued at current market prices
        - Performance metrics calculated using empyrical library when available
        - Returns include both capital appreciation and the dollar-cost averaging effect
        - Strategy assumes immediate investment (no cash drag)
    """
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
        
    # Use internal analytics functions for performance metrics
    returns_metrics = calculate_returns_metrics(portfolio_returns)
    risk_metrics = calculate_risk_metrics(portfolio_returns)
        
    # Extract metrics from internal function results
    total_return = returns_metrics['total_return']
    annual_return = returns_metrics['annual_return']
    annual_vol = risk_metrics['volatility']
    sharpe_ratio = risk_metrics['sharpe_ratio']
    max_drawdown = risk_metrics['max_drawdown']
    calmar_ratio = risk_metrics['calmar_ratio']
        
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
        
def backtest_strategy(prices: Union[pd.DataFrame, Dict[str, Any]], 
                     strategy_weights: Union[Dict[str, float], pd.DataFrame],
                     rebalance_frequency: str = "M",
                     initial_value: float = 10000,
                     transaction_cost: float = 0.001) -> Dict[str, Any]:
    """Backtest a portfolio strategy with rebalancing and transaction costs.
    
    This function simulates the historical performance of a portfolio strategy
    by applying specified weights to asset returns, accounting for rebalancing
    frequency and transaction costs. Provides comprehensive performance analysis
    using the empyrical library for proven metrics calculations.
    
    Args:
        prices: Historical price data for portfolio assets. Can be provided as
            pandas DataFrame with dates as index and assets as columns, or
            dictionary with asset names as keys and price series as values.
        strategy_weights: Portfolio allocation strategy. Can be:
            - Dict[str, float]: Static weights applied throughout the period
            - pd.DataFrame: Time-varying weights with dates as index and assets as columns
        rebalance_frequency: Frequency of portfolio rebalancing. Options:
            - "D": Daily rebalancing (transaction costs applied daily)
            - "W": Weekly rebalancing (transaction costs applied weekly)
            - "M": Monthly rebalancing (transaction costs applied monthly)
            - "Q": Quarterly rebalancing (transaction costs applied quarterly)
            Defaults to "M" (monthly).
        initial_value: Starting portfolio value in dollars. Defaults to $10,000.
        transaction_cost: Transaction cost as fraction of portfolio value on
            rebalancing dates. Defaults to 0.001 (0.1% or 10 basis points).
            
    Returns:
        Dict[str, Any]: Backtest results including:
            - Performance metrics: Total return, annual return, volatility, Sharpe ratio
            - Risk metrics: Maximum drawdown, Calmar ratio, VaR, skewness, kurtosis
            - Strategy analysis: Hit rate, win/loss ratios, transaction costs impact
            - Time series: Portfolio values and returns over the backtest period
            - Advanced metrics: Sortino ratio, stability, tail ratio (if empyrical available)
            
    Raises:
        Exception: If strategy backtest fails due to data issues or calculation errors.
        
    Example:
        >>> import pandas as pd
        >>> # Backtest 60/40 stock/bond portfolio
        >>> prices = pd.DataFrame({'SPY': [...], 'AGG': [...]})
        >>> weights = {'SPY': 0.6, 'AGG': 0.4}
        >>> results = backtest_strategy(prices, weights, rebalance_frequency="M")
        >>> print(f"Annual return: {results['annual_return_pct']}")
        >>> print(f"Sharpe ratio: {results['sharpe_ratio']:.2f}")
        >>> print(f"Max drawdown: {results['max_drawdown_pct']}")
        
    Note:
        - Portfolio returns calculated as weighted sum of asset returns
        - Transaction costs applied on rebalancing dates only
        - Time-varying weights are forward-filled for missing dates
        - All weights normalized to sum to 1 at each point in time
        - Uses empyrical library for comprehensive performance metrics
    """
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
        
    # Use internal analytics functions for comprehensive performance metrics
    returns_metrics = calculate_returns_metrics(portfolio_returns)
    risk_metrics = calculate_risk_metrics(portfolio_returns)
        
    # Extract metrics from internal function results
    total_return = returns_metrics['total_return']
    annual_return = returns_metrics['annual_return']
    annual_vol = risk_metrics['volatility']
    sharpe_ratio = risk_metrics['sharpe_ratio']
    sortino_ratio = risk_metrics['sortino_ratio']
    max_drawdown = risk_metrics['max_drawdown']
    calmar_ratio = risk_metrics['calmar_ratio']
    var_95 = risk_metrics['var_95']
    skewness = risk_metrics['skewness']
    kurtosis = risk_metrics['kurtosis']
        
    # Additional empyrical metrics not in standard risk metrics
    stability = empyrical.stability_of_timeseries(portfolio_returns)
    tail_ratio = empyrical.tail_ratio(portfolio_returns)
        
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
        "sortino_ratio": float(sortino_ratio),
        "max_drawdown": float(max_drawdown),
        "max_drawdown_pct": f"{max_drawdown * 100:.2f}%",
        "calmar_ratio": float(calmar_ratio),
        "var_95": float(var_95),
        "var_95_pct": f"{var_95 * 100:.2f}%",
        "skewness": float(skewness),
        "kurtosis": float(kurtosis),
        "stability": float(stability),
        "tail_ratio": float(tail_ratio),
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
        
    return standardize_output(result, "backtest_strategy")
        
def monte_carlo_simulation(expected_returns: Union[List[float], np.ndarray],
                          covariance_matrix: Union[List[List[float]], np.ndarray],
                          weights: Union[List[float], Dict[str, float]],
                          time_horizon: int = 252,
                          n_simulations: int = 1000,
                          initial_value: float = 10000) -> Dict[str, Any]:
    """Perform Monte Carlo simulation of portfolio performance.
    
    Monte Carlo simulation generates thousands of possible future portfolio
    value paths based on expected returns and risk characteristics. This function
    uses numpy for efficient random sampling and provides statistical analysis
    of potential outcomes including percentile distributions and risk metrics.
    
    Args:
        expected_returns: Expected annual returns for each asset in the portfolio.
            Can be provided as list or numpy array. Order must match weights and
            covariance matrix.
        covariance_matrix: Asset return covariance matrix. Can be provided as
            nested list or numpy array. Must be square matrix with dimensions
            matching the number of assets.
        weights: Portfolio allocation weights. Can be provided as list (order
            must match expected_returns) or dictionary mapping positions.
        time_horizon: Number of trading days to simulate forward. Defaults to
            252 (approximately one trading year). Use 22 for monthly, 63 for quarterly.
        n_simulations: Number of simulation paths to generate. More simulations
            provide more stable statistics but increase computation time.
            Defaults to 1000.
        initial_value: Starting portfolio value in dollars. Defaults to $10,000.
            
    Returns:
        Dict[str, Any]: Monte Carlo simulation results including:
            - Statistical summary: Mean, std dev, min, max of final portfolio values
            - Percentile analysis: 5th, 10th, 25th, 50th, 75th, 90th, 95th percentiles
            - Risk analysis: Probability of loss, expected shortfall in worst 5% scenarios
            - Portfolio characteristics: Expected return, volatility used in simulation
            - Simulation parameters: Time horizon, number of paths, initial value
            
    Raises:
        Exception: If Monte Carlo simulation fails due to invalid inputs or numerical issues.
        
    Example:
        >>> import numpy as np
        >>> # Simulate 3-asset portfolio
        >>> expected_rets = [0.08, 0.06, 0.04]  # 8%, 6%, 4% expected returns
        >>> cov_matrix = np.array([[0.04, 0.01, 0.01],
        ...                        [0.01, 0.02, 0.005],
        ...                        [0.01, 0.005, 0.01]])
        >>> weights = [0.5, 0.3, 0.2]
        >>> results = monte_carlo_simulation(expected_rets, cov_matrix, weights)
        >>> print(f"Expected final value: ${results['mean_final_value']:,.0f}")
        >>> print(f"5th percentile: ${results['percentile_5']:,.0f}")
        >>> print(f"Probability of loss: {results['probability_of_loss_pct']}")
        
    Note:
        - Assumes normal distribution of returns (log-normal for prices)
        - Uses daily return simulation with sqrt(252) volatility scaling
        - Random seed set to 42 for reproducible results
        - Expected shortfall calculated as average of worst 5% outcomes
        - Portfolio statistics calculated from individual asset characteristics
    """
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
        
# Registry of simulation functions - all using proven libraries
PORTFOLIO_SIMULATION_FUNCTIONS = {
    'simulate_dca_strategy': simulate_dca_strategy,
    'backtest_strategy': backtest_strategy,
    'monte_carlo_simulation': monte_carlo_simulation
}