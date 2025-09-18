"""
Strategy Simulation Functions

Functions for backtesting and simulating trading strategies, matching the 
categorical structure from financial-analysis-function-library.json

From financial-analysis-function-library.json category: strategy_simulation

IMPORTANT: This module reuses existing functions from portfolio/ directory
and leverages libraries from requirements.txt to avoid code duplication.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Union, Optional, Callable
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Use libraries from requirements.txt
try:
    from scipy.optimize import minimize
    from scipy import stats
    from pypfopt import EfficientFrontier, risk_models, expected_returns
    from pypfopt.discrete_allocation import DiscreteAllocation
    import empyrical
except ImportError as e:
    print(f"Warning: Some optimization libraries not available: {e}")

# Import existing performance metric functions to avoid duplication
# From financial-analysis-function-library.json
from .portfolio.performance_metrics import (
    calculate_total_return, calculate_annualized_return, calculate_volatility,
    calculate_sharpe_ratio, calculate_sortino_ratio, calculate_calmar_ratio,
    calculate_max_drawdown, calculate_var, calculate_cvar, calculate_cagr
)

# Import portfolio calculation utilities  
from .portfolio.data_processing import calculate_portfolio_returns


def backtestTechnicalStrategy(
    price_data: Union[pd.DataFrame, Dict[str, Any]],
    buy_signals: Union[pd.Series, List[bool], Dict[str, Any]],
    sell_signals: Union[pd.Series, List[bool], Dict[str, Any]],
    initial_capital: float = 100000,
    transaction_cost: float = 0.001
) -> Dict[str, Any]:
    """
    Backtest a technical trading strategy.
    
    From financial-analysis-function-library.json
    
    Args:
        price_data: OHLC price data
        buy_signals: Boolean series of buy signals
        sell_signals: Boolean series of sell signals
        initial_capital: Starting capital amount
        transaction_cost: Transaction cost as decimal (0.001 = 0.1%)
        
    Returns:
        {
            "total_return": float,
            "annual_return": float,
            "volatility": float,
            "sharpe_ratio": float,
            "max_drawdown": float,
            "num_trades": int,
            "win_rate": float,
            "profit_factor": float,
            "portfolio_value": pd.Series,
            "trades": List[Dict],
            "success": bool
        }
    """
    try:
        # Handle input formats
        if isinstance(price_data, dict) and "close" in price_data:
            prices = pd.Series(price_data["close"])
        elif isinstance(price_data, pd.DataFrame):
            prices = price_data['close'] if 'close' in price_data.columns else price_data.iloc[:, 0]
        else:
            return {"success": False, "error": "Invalid price data format"}
        
        # Handle signal formats
        def extract_signals(signals):
            if isinstance(signals, dict) and "signals" in signals:
                return pd.Series(signals["signals"], dtype=bool)
            elif isinstance(signals, (list, np.ndarray)):
                return pd.Series(signals, dtype=bool)
            elif isinstance(signals, pd.Series):
                return signals.astype(bool)
            else:
                raise ValueError("Invalid signal format")
        
        buy_series = extract_signals(buy_signals)
        sell_series = extract_signals(sell_signals)
        
        # Align all data
        data_df = pd.DataFrame({
            'price': prices,
            'buy': buy_series,
            'sell': sell_series
        }).fillna(False)
        
        if len(data_df) < 10:
            return {"success": False, "error": "Need at least 10 data points"}
        
        # Initialize backtesting variables
        cash = initial_capital
        shares = 0
        portfolio_value = []
        trades = []
        position = 'cash'  # 'cash' or 'long'
        
        # Run backtest
        for i, row in data_df.iterrows():
            current_price = row['price']
            
            # Calculate current portfolio value
            current_value = cash + (shares * current_price)
            portfolio_value.append(current_value)
            
            # Process buy signals
            if row['buy'] and position == 'cash' and cash > 0:
                # Buy maximum shares possible
                cost_per_share = current_price * (1 + transaction_cost)
                shares_to_buy = int(cash / cost_per_share)
                
                if shares_to_buy > 0:
                    total_cost = shares_to_buy * cost_per_share
                    cash -= total_cost
                    shares += shares_to_buy
                    position = 'long'
                    
                    trades.append({
                        'date': i,
                        'type': 'buy',
                        'price': current_price,
                        'shares': shares_to_buy,
                        'cost': total_cost,
                        'portfolio_value': current_value
                    })
            
            # Process sell signals
            elif row['sell'] and position == 'long' and shares > 0:
                # Sell all shares
                sale_price = current_price * (1 - transaction_cost)
                total_proceeds = shares * sale_price
                cash += total_proceeds
                
                trades.append({
                    'date': i,
                    'type': 'sell',
                    'price': current_price,
                    'shares': shares,
                    'proceeds': total_proceeds,
                    'portfolio_value': current_value
                })
                
                shares = 0
                position = 'cash'
        
        # Final portfolio value
        portfolio_series = pd.Series(portfolio_value, index=data_df.index)
        final_value = portfolio_series.iloc[-1]
        
        # Calculate metrics
        total_return = (final_value / initial_capital) - 1
        
        # Calculate returns for other metrics
        portfolio_returns = portfolio_series.pct_change().dropna()
        annual_return = (1 + total_return) ** (252 / len(portfolio_returns)) - 1 if len(portfolio_returns) > 0 else 0
        volatility = portfolio_returns.std() * np.sqrt(252) if len(portfolio_returns) > 1 else 0
        
        # Sharpe ratio (assuming 2% risk-free rate)
        excess_returns = portfolio_returns - (0.02 / 252)
        sharpe_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252) if excess_returns.std() != 0 else 0
        
        # Max drawdown
        cumulative = portfolio_series / portfolio_series.iloc[0]
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = abs(drawdown.min())
        
        # Trade analysis
        buy_trades = [t for t in trades if t['type'] == 'buy']
        sell_trades = [t for t in trades if t['type'] == 'sell']
        num_complete_trades = min(len(buy_trades), len(sell_trades))
        
        # Win rate and profit factor
        win_rate = 0
        profit_factor = 1
        
        if num_complete_trades > 0:
            trade_profits = []
            for i in range(num_complete_trades):
                buy_price = buy_trades[i]['price']
                sell_price = sell_trades[i]['price']
                profit = (sell_price - buy_price) / buy_price
                trade_profits.append(profit)
            
            winning_trades = [p for p in trade_profits if p > 0]
            losing_trades = [p for p in trade_profits if p <= 0]
            
            win_rate = len(winning_trades) / len(trade_profits)
            
            if len(losing_trades) > 0 and sum(losing_trades) != 0:
                profit_factor = abs(sum(winning_trades)) / abs(sum(losing_trades))
        
        return {
            "success": True,
            "total_return": float(total_return),
            "total_return_pct": f"{total_return * 100:.2f}%",
            "annual_return": float(annual_return),
            "annual_return_pct": f"{annual_return * 100:.2f}%",
            "volatility": float(volatility),
            "volatility_pct": f"{volatility * 100:.2f}%",
            "sharpe_ratio": float(sharpe_ratio),
            "max_drawdown": float(max_drawdown),
            "max_drawdown_pct": f"{max_drawdown * 100:.2f}%",
            "num_trades": num_complete_trades,
            "win_rate": float(win_rate),
            "win_rate_pct": f"{win_rate * 100:.2f}%",
            "profit_factor": float(profit_factor),
            "initial_capital": initial_capital,
            "final_value": float(final_value),
            "portfolio_value": portfolio_series,
            "trades": trades
        }
        
    except Exception as e:
        return {"success": False, "error": f"Backtest failed: {str(e)}"}


def monteCarloSimulation(
    expected_return: float,
    volatility: float,
    periods: int,
    simulations: int = 1000,
    initial_value: float = 100000
) -> Dict[str, Any]:
    """
    Run Monte Carlo simulation for future returns.
    
    From financial-analysis-function-library.json
    
    Args:
        expected_return: Expected annual return as decimal
        volatility: Annual volatility as decimal
        periods: Number of periods to simulate (e.g., 252 for trading days)
        simulations: Number of simulation runs
        initial_value: Starting portfolio value
        
    Returns:
        {
            "simulated_paths": np.ndarray,
            "final_values": np.ndarray,
            "percentiles": Dict[str, float],
            "mean_final_value": float,
            "probability_of_loss": float,
            "value_at_risk_95": float,
            "expected_shortfall": float,
            "success": bool
        }
    """
    try:
        if simulations < 100:
            return {"success": False, "error": "Need at least 100 simulations"}
        
        if periods < 1:
            return {"success": False, "error": "Need at least 1 period"}
        
        # Convert annual metrics to daily
        daily_return = expected_return / 252
        daily_volatility = volatility / np.sqrt(252)
        
        # Initialize results array
        simulated_paths = np.zeros((simulations, periods + 1))
        simulated_paths[:, 0] = initial_value
        
        # Generate random returns
        np.random.seed(42)  # For reproducible results
        random_returns = np.random.normal(daily_return, daily_volatility, (simulations, periods))
        
        # Calculate cumulative paths
        for i in range(periods):
            simulated_paths[:, i + 1] = simulated_paths[:, i] * (1 + random_returns[:, i])
        
        # Extract final values
        final_values = simulated_paths[:, -1]
        
        # Calculate statistics
        percentiles = {
            "5th": np.percentile(final_values, 5),
            "10th": np.percentile(final_values, 10),
            "25th": np.percentile(final_values, 25),
            "50th": np.percentile(final_values, 50),
            "75th": np.percentile(final_values, 75),
            "90th": np.percentile(final_values, 90),
            "95th": np.percentile(final_values, 95)
        }
        
        mean_final_value = np.mean(final_values)
        probability_of_loss = np.sum(final_values < initial_value) / simulations
        
        # Risk metrics
        value_at_risk_95 = initial_value - percentiles["5th"]
        
        # Expected shortfall (average of worst 5% outcomes)
        worst_5_percent = final_values[final_values <= percentiles["5th"]]
        expected_shortfall = initial_value - np.mean(worst_5_percent) if len(worst_5_percent) > 0 else 0
        
        # Calculate annualized return statistics
        returns = (final_values / initial_value) - 1
        annualized_returns = (1 + returns) ** (252 / periods) - 1
        
        return {
            "success": True,
            "simulated_paths": simulated_paths,
            "final_values": final_values,
            "percentiles": percentiles,
            "mean_final_value": float(mean_final_value),
            "median_final_value": float(percentiles["50th"]),
            "probability_of_loss": float(probability_of_loss),
            "probability_of_loss_pct": f"{probability_of_loss * 100:.1f}%",
            "value_at_risk_95": float(value_at_risk_95),
            "expected_shortfall": float(expected_shortfall),
            "parameters": {
                "expected_return": expected_return,
                "volatility": volatility,
                "periods": periods,
                "simulations": simulations,
                "initial_value": initial_value
            },
            "annualized_return_stats": {
                "mean": float(np.mean(annualized_returns)),
                "std": float(np.std(annualized_returns)),
                "min": float(np.min(annualized_returns)),
                "max": float(np.max(annualized_returns))
            }
        }
        
    except Exception as e:
        return {"success": False, "error": f"Monte Carlo simulation failed: {str(e)}"}


def backtestBuyAndHold(
    price_data: Union[pd.Series, Dict[str, Any]],
    initial_capital: float = 100000,
    dividend_yield: float = 0.0
) -> Dict[str, Any]:
    """
    Backtest a simple buy-and-hold strategy.
    
    From financial-analysis-function-library.json
    
    Args:
        price_data: Price series or OHLC data
        initial_capital: Starting capital amount
        dividend_yield: Annual dividend yield as decimal
        
    Returns:
        {
            "total_return": float,
            "annual_return": float,
            "volatility": float,
            "sharpe_ratio": float,
            "max_drawdown": float,
            "portfolio_value": pd.Series,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(price_data, dict) and "close" in price_data:
            prices = pd.Series(price_data["close"])
        elif isinstance(price_data, dict) and "prices" in price_data:
            prices = price_data["prices"]
        elif isinstance(price_data, pd.Series):
            prices = price_data
        else:
            return {"success": False, "error": "Invalid price data format"}
        
        if len(prices) < 2:
            return {"success": False, "error": "Need at least 2 price observations"}
        
        # Calculate shares purchased at start
        initial_price = prices.iloc[0]
        shares = initial_capital / initial_price
        
        # Calculate portfolio value over time
        portfolio_value = prices * shares
        
        # Add dividends if specified
        if dividend_yield > 0:
            daily_dividend_yield = dividend_yield / 252
            dividend_payments = portfolio_value * daily_dividend_yield
            portfolio_value = portfolio_value.cumsum() + dividend_payments.cumsum()
        
        # Calculate metrics
        final_value = portfolio_value.iloc[-1]
        total_return = (final_value / initial_capital) - 1
        
        # Calculate returns for other metrics
        portfolio_returns = portfolio_value.pct_change().dropna()
        
        # Annualized return
        years = len(prices) / 252
        annual_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        
        # Volatility
        volatility = portfolio_returns.std() * np.sqrt(252) if len(portfolio_returns) > 1 else 0
        
        # Sharpe ratio (assuming 2% risk-free rate)
        excess_returns = portfolio_returns - (0.02 / 252)
        sharpe_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252) if excess_returns.std() != 0 else 0
        
        # Max drawdown
        cumulative = portfolio_value / portfolio_value.iloc[0]
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = abs(drawdown.min())
        
        return {
            "success": True,
            "total_return": float(total_return),
            "total_return_pct": f"{total_return * 100:.2f}%",
            "annual_return": float(annual_return),
            "annual_return_pct": f"{annual_return * 100:.2f}%",
            "volatility": float(volatility),
            "volatility_pct": f"{volatility * 100:.2f}%",
            "sharpe_ratio": float(sharpe_ratio),
            "max_drawdown": float(max_drawdown),
            "max_drawdown_pct": f"{max_drawdown * 100:.2f}%",
            "initial_capital": initial_capital,
            "final_value": float(final_value),
            "shares_owned": float(shares),
            "dividend_yield": dividend_yield,
            "portfolio_value": portfolio_value,
            "years": float(years)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Buy-and-hold backtest failed: {str(e)}"}


def compareStrategies(
    strategies: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Compare multiple backtested strategies.
    
    From financial-analysis-function-library.json
    
    Args:
        strategies: Dict of {strategy_name: backtest_result}
        
    Returns:
        {
            "comparison_table": pd.DataFrame,
            "best_strategy": Dict,
            "rankings": Dict,
            "success": bool
        }
    """
    try:
        if len(strategies) < 2:
            return {"success": False, "error": "Need at least 2 strategies to compare"}
        
        # Extract metrics from each strategy
        comparison_data = {}
        
        for name, result in strategies.items():
            if not result.get("success", False):
                continue
                
            comparison_data[name] = {
                "Total Return": result.get("total_return", 0),
                "Annual Return": result.get("annual_return", 0),
                "Volatility": result.get("volatility", 0),
                "Sharpe Ratio": result.get("sharpe_ratio", 0),
                "Max Drawdown": result.get("max_drawdown", 0),
                "Win Rate": result.get("win_rate", 0),
                "Num Trades": result.get("num_trades", 0)
            }
        
        if len(comparison_data) == 0:
            return {"success": False, "error": "No successful strategies to compare"}
        
        # Create comparison DataFrame
        comparison_df = pd.DataFrame(comparison_data).T
        
        # Rankings (higher is better for most metrics, lower for volatility and drawdown)
        rankings = {}
        
        for metric in comparison_df.columns:
            if metric in ["Volatility", "Max Drawdown"]:
                # Lower is better
                rankings[metric] = comparison_df[metric].rank(ascending=True).to_dict()
            else:
                # Higher is better
                rankings[metric] = comparison_df[metric].rank(ascending=False).to_dict()
        
        # Calculate overall score (simple average of rankings)
        overall_scores = {}
        for strategy in comparison_df.index:
            score = np.mean([rankings[metric][strategy] for metric in rankings.keys()])
            overall_scores[strategy] = score
        
        best_strategy_name = min(overall_scores.keys(), key=lambda x: overall_scores[x])
        best_strategy = {
            "name": best_strategy_name,
            "metrics": comparison_df.loc[best_strategy_name].to_dict(),
            "overall_rank": overall_scores[best_strategy_name]
        }
        
        return {
            "success": True,
            "comparison_table": comparison_df,
            "best_strategy": best_strategy,
            "rankings": rankings,
            "overall_scores": overall_scores,
            "num_strategies": len(comparison_data)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Strategy comparison failed: {str(e)}"}


def simulateDCA(
    prices: Union[pd.Series, List[float], Dict[str, Any]],
    monthly_amount: float = 1000,
    start_date: str = None,
    frequency: str = "monthly"
) -> Dict[str, Any]:
    """
    Simulate dollar-cost averaging strategy.
    
    From financial-analysis-function-library.json
    Possible duplicate implementation - reuses existing performance metric functions
    
    Args:
        prices: Price series data
        monthly_amount: Amount to invest per period
        start_date: Start date for DCA (if not specified, starts from beginning)
        frequency: Investment frequency ('monthly', 'weekly', 'daily')
        
    Returns:
        {
            "total_invested": float,
            "final_value": float,
            "total_return": float,
            "shares_accumulated": float,
            "average_price": float,
            "investment_schedule": List[Dict],
            "portfolio_value": pd.Series,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(prices, dict) and "prices" in prices:
            price_series = prices["prices"]
        elif isinstance(prices, (list, np.ndarray)):
            price_series = pd.Series(prices)
        elif isinstance(prices, pd.Series):
            price_series = prices
        else:
            return {"success": False, "error": "Invalid price format"}
        
        if len(price_series) < 2:
            return {"success": False, "error": "Need at least 2 price observations"}
        
        # Set frequency parameters
        freq_map = {
            "daily": 1,
            "weekly": 7,
            "monthly": 30,  # Approximate
            "quarterly": 90
        }
        
        if frequency not in freq_map:
            return {"success": False, "error": f"Unsupported frequency: {frequency}"}
        
        investment_frequency = freq_map[frequency]
        
        # Determine investment dates
        investment_indices = range(0, len(price_series), investment_frequency)
        
        # Simulate DCA investments
        total_invested = 0
        total_shares = 0
        investment_schedule = []
        
        for i, price_idx in enumerate(investment_indices):
            if price_idx >= len(price_series):
                break
                
            current_price = price_series.iloc[price_idx]
            shares_purchased = monthly_amount / current_price
            total_shares += shares_purchased
            total_invested += monthly_amount
            
            # Record this investment
            investment_record = {
                "investment_number": i + 1,
                "date_index": price_idx,
                "price": float(current_price),
                "amount_invested": float(monthly_amount),
                "shares_purchased": float(shares_purchased),
                "cumulative_shares": float(total_shares),
                "cumulative_invested": float(total_invested),
                "portfolio_value": float(total_shares * current_price)
            }
            
            investment_schedule.append(investment_record)
        
        # Calculate portfolio value over entire period
        portfolio_value_series = pd.Series(index=price_series.index, dtype=float)
        
        current_shares = 0
        investment_idx = 0
        
        for i, price in enumerate(price_series):
            # Check if we should make an investment
            if investment_idx < len(investment_schedule) and i == investment_schedule[investment_idx]["date_index"]:
                current_shares = investment_schedule[investment_idx]["cumulative_shares"]
                investment_idx += 1
            
            # Calculate portfolio value
            portfolio_value_series.iloc[i] = current_shares * price
        
        # Use existing functions for performance metrics - from financial-analysis-function-library.json
        portfolio_returns = portfolio_value_series.pct_change().dropna()
        
        # Reuse existing performance calculation functions to avoid duplication
        total_return_result = calculate_total_return(portfolio_returns)
        annual_return_result = calculate_annualized_return(portfolio_returns)
        volatility_result = calculate_volatility(portfolio_returns, annualized=True)
        max_drawdown_result = calculate_max_drawdown(portfolio_value_series)
        sharpe_result = calculate_sharpe_ratio(portfolio_returns)
        
        # Basic calculations
        final_value = total_shares * price_series.iloc[-1]
        simple_total_return = (final_value / total_invested) - 1 if total_invested > 0 else 0
        average_price = total_invested / total_shares if total_shares > 0 else 0
        
        return {
            "success": True,
            "total_invested": float(total_invested),
            "final_value": float(final_value),
            "total_return": float(simple_total_return),
            "total_return_pct": f"{simple_total_return * 100:.2f}%",
            "annual_return": annual_return_result.get("annualized_return", 0),
            "annual_return_pct": annual_return_result.get("annualized_return_pct", "0.00%"),
            "volatility": volatility_result.get("volatility", 0),
            "volatility_pct": volatility_result.get("volatility_pct", "0.00%"),
            "sharpe_ratio": sharpe_result.get("sharpe_ratio", 0),
            "max_drawdown": max_drawdown_result.get("max_drawdown", 0),
            "max_drawdown_pct": max_drawdown_result.get("max_drawdown_pct", "0.00%"),
            "shares_accumulated": float(total_shares),
            "average_price": float(average_price),
            "final_price": float(price_series.iloc[-1]),
            "num_investments": len(investment_schedule),
            "frequency": frequency,
            "investment_schedule": investment_schedule,
            "portfolio_value": portfolio_value_series,
            # Include detailed performance analysis
            "performance_details": {
                "total_return_analysis": total_return_result,
                "annual_return_analysis": annual_return_result,
                "volatility_analysis": volatility_result,
                "drawdown_analysis": max_drawdown_result,
                "sharpe_analysis": sharpe_result
            }
        }
        
    except Exception as e:
        return {"success": False, "error": f"DCA simulation failed: {str(e)}"}


def simulateLumpSum(
    prices: Union[pd.Series, List[float], Dict[str, Any]],
    amount: float,
    investment_date: Union[str, int] = 0
) -> Dict[str, Any]:
    """
    Simulate lump sum investment.
    
    From financial-analysis-function-library.json
    
    Args:
        prices: Price series data
        amount: Lump sum amount to invest
        investment_date: Date/index to invest (default: start)
        
    Returns:
        {
            "invested_amount": float,
            "final_value": float,
            "total_return": float,
            "shares_purchased": float,
            "investment_price": float,
            "portfolio_value": pd.Series,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(prices, dict) and "prices" in prices:
            price_series = prices["prices"]
        elif isinstance(prices, (list, np.ndarray)):
            price_series = pd.Series(prices)
        elif isinstance(prices, pd.Series):
            price_series = prices
        else:
            return {"success": False, "error": "Invalid price format"}
        
        if len(price_series) < 2:
            return {"success": False, "error": "Need at least 2 price observations"}
        
        # Determine investment index
        if isinstance(investment_date, int):
            investment_idx = investment_date
        else:
            # For string dates, use start for simplicity
            investment_idx = 0
        
        if investment_idx >= len(price_series):
            return {"success": False, "error": "Investment date beyond data range"}
        
        # Calculate investment
        investment_price = price_series.iloc[investment_idx]
        shares_purchased = amount / investment_price
        
        # Calculate portfolio value over time
        # Before investment: portfolio value is 0
        # After investment: portfolio value = shares * current price
        portfolio_value = pd.Series(index=price_series.index, dtype=float)
        
        for i, price in enumerate(price_series):
            if i < investment_idx:
                portfolio_value.iloc[i] = 0  # No investment yet
            else:
                portfolio_value.iloc[i] = shares_purchased * price
        
        # Final calculations
        final_value = portfolio_value.iloc[-1]
        total_return = (final_value / amount) - 1
        
        # Performance metrics (calculated from investment date onwards)
        post_investment_values = portfolio_value.iloc[investment_idx:]
        returns = post_investment_values.pct_change().dropna()
        
        periods_invested = len(post_investment_values)
        annual_return = (1 + total_return) ** (252 / periods_invested) - 1 if periods_invested > 0 else 0
        volatility = returns.std() * np.sqrt(252) if len(returns) > 1 else 0
        
        # Max drawdown from investment point
        investment_values = post_investment_values / post_investment_values.iloc[0]
        running_max = investment_values.expanding().max()
        drawdown = (investment_values - running_max) / running_max
        max_drawdown = abs(drawdown.min())
        
        return {
            "success": True,
            "invested_amount": float(amount),
            "final_value": float(final_value),
            "total_return": float(total_return),
            "total_return_pct": f"{total_return * 100:.2f}%",
            "annual_return": float(annual_return),
            "annual_return_pct": f"{annual_return * 100:.2f}%",
            "volatility": float(volatility),
            "max_drawdown": float(max_drawdown),
            "max_drawdown_pct": f"{max_drawdown * 100:.2f}%",
            "shares_purchased": float(shares_purchased),
            "investment_price": float(investment_price),
            "final_price": float(price_series.iloc[-1]),
            "investment_index": investment_idx,
            "periods_invested": periods_invested,
            "portfolio_value": portfolio_value
        }
        
    except Exception as e:
        return {"success": False, "error": f"Lump sum simulation failed: {str(e)}"}


def simulateRebalancing(
    prices: Union[pd.DataFrame, Dict[str, pd.Series]],
    target_weights: Union[List[float], Dict[str, float]],
    rebalance_frequency: str = "monthly",
    initial_capital: float = 100000,
    transaction_cost: float = 0.001
) -> Dict[str, Any]:
    """
    Simulate portfolio rebalancing strategy.
    
    From financial-analysis-function-library.json
    
    Args:
        prices: Price data for multiple assets (DataFrame or dict of Series)
        target_weights: Target portfolio weights
        rebalance_frequency: How often to rebalance ('daily', 'weekly', 'monthly', 'quarterly')
        initial_capital: Starting capital
        transaction_cost: Transaction cost per trade as decimal
        
    Returns:
        {
            "final_value": float,
            "total_return": float,
            "rebalance_dates": List,
            "portfolio_weights": pd.DataFrame,
            "portfolio_value": pd.Series,
            "transaction_costs": float,
            "success": bool
        }
    """
    try:
        # Handle input formats
        if isinstance(prices, dict):
            price_df = pd.DataFrame(prices)
        elif isinstance(prices, pd.DataFrame):
            price_df = prices
        else:
            return {"success": False, "error": "Invalid price data format"}
        
        # Handle weights
        if isinstance(target_weights, dict):
            # Ensure weights align with price columns
            if not all(asset in price_df.columns for asset in target_weights.keys()):
                return {"success": False, "error": "Weight assets don't match price data assets"}
            weight_series = pd.Series(target_weights)
        elif isinstance(target_weights, list):
            if len(target_weights) != len(price_df.columns):
                return {"success": False, "error": "Number of weights must match number of assets"}
            weight_series = pd.Series(target_weights, index=price_df.columns)
        else:
            return {"success": False, "error": "Invalid weights format"}
        
        # Normalize weights
        weight_series = weight_series / weight_series.sum()
        
        # Clean data
        price_df = price_df.dropna()
        if len(price_df) < 2:
            return {"success": False, "error": "Need at least 2 observations"}
        
        # Set rebalancing frequency
        freq_map = {
            "daily": 1,
            "weekly": 7,
            "monthly": 22,  # Trading days
            "quarterly": 66
        }
        
        if rebalance_frequency not in freq_map:
            return {"success": False, "error": f"Unsupported frequency: {rebalance_frequency}"}
        
        rebalance_period = freq_map[rebalance_frequency]
        
        # Initialize portfolio
        num_assets = len(weight_series)
        portfolio_value = []
        portfolio_weights = pd.DataFrame(index=price_df.index, columns=price_df.columns)
        rebalance_dates = []
        total_transaction_costs = 0
        
        # Initial allocation
        cash = initial_capital
        shares = pd.Series(0.0, index=price_df.columns)
        
        # Buy initial shares according to target weights
        first_prices = price_df.iloc[0]
        for asset in price_df.columns:
            target_value = initial_capital * weight_series[asset]
            shares[asset] = target_value / (first_prices[asset] * (1 + transaction_cost))
            cost = shares[asset] * first_prices[asset] * (1 + transaction_cost)
            cash -= cost
            total_transaction_costs += cost * transaction_cost
        
        rebalance_dates.append(price_df.index[0])
        
        # Simulate portfolio over time
        for i, (date, prices) in enumerate(price_df.iterrows()):
            # Calculate current portfolio value
            current_value = (shares * prices).sum() + cash
            portfolio_value.append(current_value)
            
            # Calculate current weights
            asset_values = shares * prices
            current_weights = asset_values / current_value
            portfolio_weights.loc[date] = current_weights
            
            # Check if it's time to rebalance
            if i > 0 and i % rebalance_period == 0:
                # Rebalance to target weights
                target_values = current_value * weight_series
                
                for asset in price_df.columns:
                    current_asset_value = shares[asset] * prices[asset]
                    target_asset_value = target_values[asset]
                    
                    if abs(current_asset_value - target_asset_value) > current_value * 0.01:  # 1% threshold
                        # Calculate shares to buy/sell
                        target_shares = target_asset_value / (prices[asset] * (1 + transaction_cost))
                        shares_to_trade = target_shares - shares[asset]
                        
                        if shares_to_trade > 0:  # Buy
                            trade_cost = shares_to_trade * prices[asset] * (1 + transaction_cost)
                            if cash >= trade_cost:
                                cash -= trade_cost
                                shares[asset] += shares_to_trade
                                total_transaction_costs += trade_cost * transaction_cost
                        else:  # Sell
                            shares_to_sell = abs(shares_to_trade)
                            if shares[asset] >= shares_to_sell:
                                proceeds = shares_to_sell * prices[asset] * (1 - transaction_cost)
                                cash += proceeds
                                shares[asset] -= shares_to_sell
                                total_transaction_costs += shares_to_sell * prices[asset] * transaction_cost
                
                rebalance_dates.append(date)
        
        # Final calculations
        portfolio_series = pd.Series(portfolio_value, index=price_df.index)
        final_value = portfolio_series.iloc[-1]
        total_return = (final_value / initial_capital) - 1
        
        # Performance metrics
        returns = portfolio_series.pct_change().dropna()
        annual_return = (1 + total_return) ** (252 / len(returns)) - 1 if len(returns) > 0 else 0
        volatility = returns.std() * np.sqrt(252) if len(returns) > 1 else 0
        
        # Sharpe ratio
        excess_returns = returns - (0.02 / 252)
        sharpe_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252) if excess_returns.std() != 0 else 0
        
        # Max drawdown
        cumulative = portfolio_series / portfolio_series.iloc[0]
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = abs(drawdown.min())
        
        return {
            "success": True,
            "initial_capital": float(initial_capital),
            "final_value": float(final_value),
            "total_return": float(total_return),
            "total_return_pct": f"{total_return * 100:.2f}%",
            "annual_return": float(annual_return),
            "annual_return_pct": f"{annual_return * 100:.2f}%",
            "volatility": float(volatility),
            "sharpe_ratio": float(sharpe_ratio),
            "max_drawdown": float(max_drawdown),
            "max_drawdown_pct": f"{max_drawdown * 100:.2f}%",
            "num_rebalances": len(rebalance_dates),
            "transaction_costs": float(total_transaction_costs),
            "transaction_cost_pct": f"{(total_transaction_costs / initial_capital) * 100:.2f}%",
            "rebalance_frequency": rebalance_frequency,
            "target_weights": weight_series.to_dict(),
            "rebalance_dates": [str(date) for date in rebalance_dates],
            "portfolio_value": portfolio_series,
            "portfolio_weights": portfolio_weights
        }
        
    except Exception as e:
        return {"success": False, "error": f"Rebalancing simulation failed: {str(e)}"}


def optimizePortfolio(
    returns: Union[pd.DataFrame, Dict[str, pd.Series]],
    method: str = "max_sharpe",
    risk_free_rate: float = 0.02,
    constraints: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Optimize portfolio weights using various methods.
    
    From financial-analysis-function-library.json
    Uses PyPortfolioOpt library from requirements.txt to avoid code duplication
    
    Args:
        returns: Return data for assets (DataFrame or dict of Series)
        method: Optimization method ('max_sharpe', 'min_volatility', 'equal_weight', 'risk_parity')
        risk_free_rate: Risk-free rate for Sharpe ratio calculation
        constraints: Additional constraints (min_weight, max_weight, etc.)
        
    Returns:
        {
            "optimal_weights": Dict[str, float],
            "expected_return": float,
            "volatility": float,
            "sharpe_ratio": float,
            "optimization_method": str,
            "success": bool
        }
    """
    try:
        # Handle input formats
        if isinstance(returns, dict):
            returns_df = pd.DataFrame(returns)
        elif isinstance(returns, pd.DataFrame):
            returns_df = returns
        else:
            return {"success": False, "error": "Invalid returns data format"}
        
        returns_df = returns_df.dropna()
        if len(returns_df) < 10:
            return {"success": False, "error": "Need at least 10 return observations"}
        
        # Set default constraints
        if constraints is None:
            constraints = {}
        
        # Use PyPortfolioOpt library from requirements.txt - avoiding manual calculation duplication
        try:
            # Calculate expected returns and covariance matrix using PyPortfolioOpt
            mu = expected_returns.mean_historical_return(returns_df)
            S = risk_models.sample_cov(returns_df)
            
            # Create EfficientFrontier object
            ef = EfficientFrontier(mu, S)
            
            # Set constraints
            min_weight = constraints.get("min_weight", 0.0)
            max_weight = constraints.get("max_weight", 1.0)
            
            if min_weight > 0 or max_weight < 1:
                ef.add_constraint(lambda w: w >= min_weight)
                ef.add_constraint(lambda w: w <= max_weight)
            
            # Portfolio optimization based on method
            if method == "max_sharpe":
                weights = ef.max_sharpe(risk_free_rate=risk_free_rate)
            elif method == "min_volatility":
                weights = ef.min_volatility()
            elif method == "equal_weight":
                n_assets = len(returns_df.columns)
                weights = {asset: 1.0/n_assets for asset in returns_df.columns}
            elif method == "risk_parity":
                # Risk parity using inverse volatility weighting (simplified)
                vol_inv = 1 / returns_df.std()
                weights_series = vol_inv / vol_inv.sum()
                weights = weights_series.to_dict()
            else:
                return {"success": False, "error": f"Unsupported optimization method: {method}"}
            
            # Clean weights and get performance
            if method in ["max_sharpe", "min_volatility"]:
                cleaned_weights = ef.clean_weights()
                portfolio_performance = ef.portfolio_performance(risk_free_rate=risk_free_rate, verbose=False)
                expected_return, volatility, sharpe = portfolio_performance
                optimal_weights = cleaned_weights
            else:
                # For equal_weight and risk_parity, calculate performance manually
                weights_array = np.array(list(weights.values()))
                expected_return = np.sum(mu * weights_array)
                volatility = np.sqrt(np.dot(weights_array.T, np.dot(S, weights_array)))
                sharpe = (expected_return - risk_free_rate) / volatility if volatility > 0 else 0
                optimal_weights = weights
            
        except ImportError:
            # Fallback to simple methods if PyPortfolioOpt not available
            print("PyPortfolioOpt not available, using simplified optimization")
            
            # Calculate statistics manually as fallback
            mean_returns = returns_df.mean() * 252  # Annualized
            cov_matrix = returns_df.cov() * 252  # Annualized
            
            if method == "equal_weight":
                n_assets = len(returns_df.columns)
                optimal_weights = {asset: 1.0/n_assets for asset in returns_df.columns}
            elif method == "risk_parity":
                vol_inv = 1 / returns_df.std()
                weights_series = vol_inv / vol_inv.sum()
                optimal_weights = weights_series.to_dict()
            else:
                return {"success": False, "error": "Advanced optimization requires PyPortfolioOpt library"}
            
            # Calculate performance
            weights_array = np.array(list(optimal_weights.values()))
            expected_return = np.sum(mean_returns * weights_array)
            volatility = np.sqrt(np.dot(weights_array.T, np.dot(cov_matrix, weights_array)))
            sharpe = (expected_return - risk_free_rate) / volatility if volatility > 0 else 0
        
        # Additional metrics using existing functions - from financial-analysis-function-library.json
        weights_series = pd.Series(optimal_weights)
        diversification_ratio = np.sum(weights_series * np.sqrt(np.diag(S))) / volatility if 'S' in locals() else 1.0
        
        return {
            "success": True,
            "optimal_weights": optimal_weights,
            "expected_return": float(expected_return),
            "expected_return_pct": f"{expected_return * 100:.2f}%",
            "volatility": float(volatility),
            "volatility_pct": f"{volatility * 100:.2f}%",
            "sharpe_ratio": float(sharpe),
            "diversification_ratio": float(diversification_ratio),
            "optimization_method": method,
            "risk_free_rate": risk_free_rate,
            "constraints": constraints,
            "num_assets": len(optimal_weights),
            "weight_stats": {
                "max_weight": float(max(optimal_weights.values())),
                "min_weight": float(min(optimal_weights.values())),
                "weight_concentration": float(sum(w**2 for w in optimal_weights.values()))  # Herfindahl index
            }
        }
        
    except Exception as e:
        return {"success": False, "error": f"Portfolio optimization failed: {str(e)}"}


def efficientFrontier(
    returns: Union[pd.DataFrame, Dict[str, pd.Series]],
    risk_free_rate: float = 0.02,
    num_portfolios: int = 100
) -> Dict[str, Any]:
    """
    Calculate efficient frontier.
    
    From financial-analysis-function-library.json
    Uses PyPortfolioOpt library from requirements.txt for proper efficient frontier calculation
    
    Args:
        returns: Return data for assets
        risk_free_rate: Risk-free rate
        num_portfolios: Number of portfolios to generate
        
    Returns:
        {
            "frontier_returns": List[float],
            "frontier_volatilities": List[float],
            "frontier_sharpe_ratios": List[float],
            "frontier_weights": List[Dict],
            "optimal_portfolio": Dict,
            "min_vol_portfolio": Dict,
            "success": bool
        }
    """
    try:
        # Handle input formats
        if isinstance(returns, dict):
            returns_df = pd.DataFrame(returns)
        elif isinstance(returns, pd.DataFrame):
            returns_df = returns
        else:
            return {"success": False, "error": "Invalid returns data format"}
        
        returns_df = returns_df.dropna()
        if len(returns_df) < 10:
            return {"success": False, "error": "Need at least 10 return observations"}
        
        try:
            # Use PyPortfolioOpt for proper efficient frontier calculation - from requirements.txt
            mu = expected_returns.mean_historical_return(returns_df)
            S = risk_models.sample_cov(returns_df)
            
            # Generate efficient frontier using PyPortfolioOpt
            frontier_returns = []
            frontier_volatilities = []
            frontier_sharpe_ratios = []
            frontier_weights = []
            
            # Generate target returns for efficient frontier
            min_ret = mu.min()
            max_ret = mu.max()
            target_returns = np.linspace(min_ret, max_ret, num_portfolios)
            
            for target_return in target_returns:
                try:
                    ef = EfficientFrontier(mu, S)
                    ef.efficient_return(target_return)
                    weights = ef.clean_weights()
                    performance = ef.portfolio_performance(risk_free_rate=risk_free_rate, verbose=False)
                    
                    expected_return, volatility, sharpe = performance
                    
                    frontier_returns.append(expected_return)
                    frontier_volatilities.append(volatility)
                    frontier_sharpe_ratios.append(sharpe)
                    frontier_weights.append(weights)
                    
                except Exception:
                    # Skip infeasible portfolios
                    continue
            
            if len(frontier_returns) == 0:
                return {"success": False, "error": "Could not generate efficient frontier"}
            
            # Find optimal portfolios using existing optimization functions - reuse code
            max_sharpe_result = optimizePortfolio(returns_df, method="max_sharpe", risk_free_rate=risk_free_rate)
            min_vol_result = optimizePortfolio(returns_df, method="min_volatility", risk_free_rate=risk_free_rate)
            
            optimal_portfolio = {
                "weights": max_sharpe_result.get("optimal_weights", {}),
                "expected_return": max_sharpe_result.get("expected_return", 0),
                "volatility": max_sharpe_result.get("volatility", 0),
                "sharpe_ratio": max_sharpe_result.get("sharpe_ratio", 0)
            }
            
            min_vol_portfolio = {
                "weights": min_vol_result.get("optimal_weights", {}),
                "expected_return": min_vol_result.get("expected_return", 0),
                "volatility": min_vol_result.get("volatility", 0),
                "sharpe_ratio": min_vol_result.get("sharpe_ratio", 0)
            }
            
        except ImportError:
            # Fallback to random portfolio generation if PyPortfolioOpt not available
            print("PyPortfolioOpt not available, using random portfolio generation")
            
            # Calculate statistics manually
            mean_returns = returns_df.mean() * 252  # Annualized
            cov_matrix = returns_df.cov() * 252  # Annualized
            n_assets = len(returns_df.columns)
            
            # Generate random portfolios for efficient frontier
            np.random.seed(42)
            
            frontier_returns = []
            frontier_volatilities = []
            frontier_sharpe_ratios = []
            frontier_weights = []
            
            for _ in range(num_portfolios):
                # Generate random weights
                weights = np.random.random(n_assets)
                weights = weights / np.sum(weights)  # Normalize
                
                # Calculate portfolio metrics
                portfolio_return = np.sum(mean_returns * weights)
                portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_vol if portfolio_vol > 0 else 0
                
                frontier_returns.append(portfolio_return)
                frontier_volatilities.append(portfolio_vol)
                frontier_sharpe_ratios.append(sharpe_ratio)
                frontier_weights.append({asset: weight for asset, weight in zip(returns_df.columns, weights)})
            
            # Find optimal portfolios
            max_sharpe_idx = np.argmax(frontier_sharpe_ratios)
            min_vol_idx = np.argmin(frontier_volatilities)
            
            optimal_portfolio = {
                "weights": frontier_weights[max_sharpe_idx],
                "expected_return": frontier_returns[max_sharpe_idx],
                "volatility": frontier_volatilities[max_sharpe_idx],
                "sharpe_ratio": frontier_sharpe_ratios[max_sharpe_idx]
            }
            
            min_vol_portfolio = {
                "weights": frontier_weights[min_vol_idx],
                "expected_return": frontier_returns[min_vol_idx],
                "volatility": frontier_volatilities[min_vol_idx],
                "sharpe_ratio": frontier_sharpe_ratios[min_vol_idx]
            }
        
        # Calculate efficient frontier statistics
        return_range = {
            "min": min(frontier_returns),
            "max": max(frontier_returns),
            "mean": np.mean(frontier_returns)
        }
        
        vol_range = {
            "min": min(frontier_volatilities),
            "max": max(frontier_volatilities),
            "mean": np.mean(frontier_volatilities)
        }
        
        return {
            "success": True,
            "frontier_returns": frontier_returns,
            "frontier_volatilities": frontier_volatilities,
            "frontier_sharpe_ratios": frontier_sharpe_ratios,
            "frontier_weights": frontier_weights,
            "optimal_portfolio": optimal_portfolio,
            "min_vol_portfolio": min_vol_portfolio,
            "num_portfolios": len(frontier_returns),
            "risk_free_rate": risk_free_rate,
            "return_range": return_range,
            "volatility_range": vol_range,
            "max_sharpe_ratio": max(frontier_sharpe_ratios) if frontier_sharpe_ratios else 0,
            "min_volatility": min(frontier_volatilities) if frontier_volatilities else 0,
            "asset_names": list(returns_df.columns)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Efficient frontier calculation failed: {str(e)}"}


# Registry for MCP server
STRATEGY_SIMULATION_FUNCTIONS = {
    'backtestTechnicalStrategy': backtestTechnicalStrategy,
    'monteCarloSimulation': monteCarloSimulation,
    'backtestBuyAndHold': backtestBuyAndHold,
    'compareStrategies': compareStrategies,
    'simulateDCA': simulateDCA,
    'simulateLumpSum': simulateLumpSum,
    'simulateRebalancing': simulateRebalancing,
    'optimizePortfolio': optimizePortfolio,
    'efficientFrontier': efficientFrontier
}