"""
Portfolio Strategy Simulation Functions

Backtesting and Monte Carlo simulation functions for portfolio strategies.
Functions for testing trading strategies and simulating future scenarios.

Extended with Strategy Simulation functions from financial-analysis-function-library.json
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Union, Optional, Callable
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


# Strategy Simulation Functions from financial-analysis-function-library.json
def backtest_technical_strategy(
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


def monte_carlo_simulation(
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


def backtest_buy_and_hold(
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


def compare_strategies(
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


# Registry for MCP server
STRATEGY_SIMULATION_FUNCTIONS = {
    'backtest_technical_strategy': backtest_technical_strategy,
    'monte_carlo_simulation': monte_carlo_simulation,
    'backtest_buy_and_hold': backtest_buy_and_hold,
    'compare_strategies': compare_strategies
}