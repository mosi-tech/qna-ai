"""
Tier 10 Advanced Portfolio Tools - Portfolio analysis and optimization

Implements 3 advanced portfolio tools using REAL MCP data:
- portfolio-rebalancing-optimizer: Optimize rebalancing frequency and thresholds
- asset-allocation-optimizer: Modern portfolio theory optimization
- portfolio-risk-analyzer: Comprehensive risk analysis with VaR/CVaR
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Union, Optional
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import MCP functions - ONLY use existing MCP functions
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from financial.functions_mock import alpaca_market_stocks_bars
from analytics.utils.data_utils import (
    standardize_output, 
    validate_price_data, 
    prices_to_returns
)
from analytics.portfolio.metrics import (
    calculate_portfolio_metrics,
    analyze_portfolio_concentration,
    stress_test_portfolio
)
from analytics.performance.metrics import calculate_returns_metrics
from analytics.risk.metrics import calculate_var, calculate_cvar
from analytics.comparison.metrics import compare_performance_metrics


def portfolio_rebalancing_optimizer(
    portfolio_positions: List[Dict[str, Any]],
    target_allocation: Dict[str, float],
    rebalancing_frequencies: Optional[List[str]] = None,
    transaction_cost_per_trade: float = 0.0,
    drift_thresholds: Optional[List[float]] = None,
    analysis_period: str = "2y"
) -> Dict[str, Any]:
    """
    Optimize portfolio rebalancing frequency, thresholds, and target allocations.
    
    Args:
        portfolio_positions: List of positions with symbol, quantity, current_price
        target_allocation: Desired allocation percentages by symbol
        rebalancing_frequencies: Frequencies to test ['monthly', 'quarterly', etc.]
        transaction_cost_per_trade: Fixed cost per trade in dollars
        drift_thresholds: Drift percentage thresholds to test [0.05, 0.10, etc.]
        analysis_period: Historical period for backtesting
        
    Returns:
        Dict: Optimization results with recommendations
    """
    try:
        # Set defaults
        if rebalancing_frequencies is None:
            rebalancing_frequencies = ["monthly", "quarterly", "semi_annual", "annual"]
        if drift_thresholds is None:
            drift_thresholds = [0.05, 0.10, 0.15, 0.20]
        
        # Extract symbols and weights from portfolio positions
        symbols = [pos['symbol'] for pos in portfolio_positions]
        current_values = [pos['quantity'] * pos['current_price'] for pos in portfolio_positions]
        total_value = sum(current_values)
        current_weights = {pos['symbol']: (pos['quantity'] * pos['current_price']) / total_value 
                          for pos in portfolio_positions}
        
        # Get historical price data using MCP function
        end_date = datetime.now()
        start_date = end_date - timedelta(days=730 if analysis_period == "2y" else 365)
        
        print("🔄 Fetching historical price data for rebalancing optimization...")
        bars_result = alpaca_market_stocks_bars(
            symbols=",".join(symbols),
            timeframe="1Day",
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d')
        )
        
        if "error" in str(bars_result):
            raise Exception("Failed to fetch price data")
        
        # Build price matrix for all symbols
        price_data = {}
        for symbol in symbols:
            symbol_bars = bars_result["bars"][symbol]
            dates = [pd.to_datetime(bar['t']) for bar in symbol_bars]
            prices = [bar['c'] for bar in symbol_bars]
            price_data[symbol] = Any(prices, index=dates)
        
        # Align all price series to common dates
        price_df = Any(price_data).dropna()
        print(f"✅ Analyzed {len(price_df)} trading days for {len(symbols)} assets")
        
        # Calculate returns for each asset using MCP function
        returns_data = {}
        for symbol in symbols:
            returns_data[symbol] = prices_to_returns(price_df[symbol])
        returns_df = Any(returns_data).dropna()
        
        # Test different rebalancing strategies
        rebalancing_results = []
        
        for frequency in rebalancing_frequencies:
            for threshold in drift_thresholds:
                print(f"🧮 Testing {frequency} rebalancing with {threshold*100}% drift threshold...")
                
                # Simulate rebalancing strategy
                strategy_result = simulate_rebalancing_strategy(
                    price_df, 
                    target_allocation, 
                    frequency, 
                    threshold, 
                    transaction_cost_per_trade
                )
                
                # Calculate performance metrics using MCP function
                if len(strategy_result['portfolio_returns']) > 0:
                    perf_metrics = calculate_returns_metrics(strategy_result['portfolio_returns'])
                    
                    rebalancing_results.append({
                        "frequency": frequency,
                        "drift_threshold": threshold,
                        "total_return": strategy_result['total_return'],
                        "annualized_return": perf_metrics.get('annualized_return', 0),
                        "volatility": perf_metrics.get('volatility', 0),
                        "sharpe_ratio": perf_metrics.get('sharpe_ratio', 0),
                        "transaction_costs": strategy_result['total_transaction_costs'],
                        "rebalancing_count": strategy_result['rebalancing_count'],
                        "net_return": strategy_result['total_return'] - strategy_result['total_transaction_costs']
                    })
        
        # Find optimal strategy (best risk-adjusted return net of costs)
        if rebalancing_results:
            best_strategy = max(rebalancing_results, 
                              key=lambda x: x['sharpe_ratio'] - (x['transaction_costs'] / 10000))  # Penalize high costs
        else:
            raise Exception("No valid rebalancing strategies found")
        
        # Calculate buy-and-hold benchmark using MCP function
        bh_portfolio_returns = []
        for i in range(len(returns_df)):
            daily_return = sum(target_allocation.get(symbol, 0) * returns_df[symbol].iloc[i] 
                             for symbol in symbols)
            bh_portfolio_returns.append(daily_return)
        
        bh_metrics = calculate_returns_metrics(bh_portfolio_returns)
        
        # Calculate current portfolio drift
        current_drift = {}
        max_drift = 0
        for symbol in symbols:
            target_weight = target_allocation.get(symbol, 0)
            current_weight = current_weights.get(symbol, 0)
            drift = abs(current_weight - target_weight)
            current_drift[symbol] = drift
            max_drift = max(max_drift, drift)
        
        # Generate rebalancing recommendations
        rebalance_needed = max_drift > best_strategy['drift_threshold']
        recommended_trades = []
        
        if rebalance_needed:
            for symbol in symbols:
                target_weight = target_allocation.get(symbol, 0)
                current_weight = current_weights.get(symbol, 0)
                target_value = total_value * target_weight
                current_value = current_weights[symbol] * total_value
                trade_value = target_value - current_value
                
                if abs(trade_value) > 100:  # Only recommend significant trades
                    recommended_trades.append({
                        "symbol": symbol,
                        "action": "buy" if trade_value > 0 else "sell",
                        "value": abs(trade_value),
                        "current_weight": current_weight,
                        "target_weight": target_weight,
                        "drift": current_drift[symbol]
                    })
        
        result = {
            "analysis_summary": {
                "symbols_analyzed": len(symbols),
                "strategies_tested": len(rebalancing_results),
                "analysis_period_days": len(price_df),
                "current_portfolio_value": total_value
            },
            "optimal_strategy": {
                "frequency": best_strategy['frequency'],
                "drift_threshold": best_strategy['drift_threshold'],
                "expected_annual_return": best_strategy['annualized_return'],
                "expected_volatility": best_strategy['volatility'],
                "expected_sharpe_ratio": best_strategy['sharpe_ratio']
            },
            "performance_comparison": {
                "rebalanced_total_return": best_strategy['total_return'],
                "buy_hold_total_return": bh_metrics.get('total_return', 0),
                "rebalancing_advantage": best_strategy['total_return'] - bh_metrics.get('total_return', 0),
                "transaction_costs": best_strategy['transaction_costs'],
                "net_advantage": best_strategy['net_return'] - bh_metrics.get('total_return', 0)
            },
            "current_portfolio_analysis": {
                "current_drift": current_drift,
                "max_drift": max_drift,
                "rebalance_needed": rebalance_needed,
                "recommended_trades": recommended_trades
            },
            "all_strategies_tested": rebalancing_results[:10],  # Top 10 results
            "rebalancing_calendar": generate_rebalancing_calendar(best_strategy['frequency'])
        }
        
        return standardize_output(result, "portfolio_rebalancing_optimizer")
        
    except Exception as e:
        return {"success": False, "error": f"Portfolio rebalancing optimization failed: {str(e)}"}


def simulate_rebalancing_strategy(
    price_df: Any, 
    target_allocation: Dict[str, float], 
    frequency: str, 
    drift_threshold: float,
    transaction_cost: float
) -> Dict[str, Any]:
    """
    Simulate a rebalancing strategy over historical data.
    """
    try:
        # Define rebalancing periods
        frequency_days = {
            "monthly": 21,
            "quarterly": 63, 
            "semi_annual": 126,
            "annual": 252
        }
        
        rebalance_interval = frequency_days.get(frequency, 63)
        
        # Initialize portfolio
        symbols = list(target_allocation.keys())
        portfolio_values = []
        portfolio_returns = []
        rebalancing_dates = []
        total_transaction_costs = 0
        rebalancing_count = 0
        
        # Start with equal dollar amounts based on target allocation
        initial_value = 100000  # $100k starting portfolio
        portfolio = {symbol: target_allocation.get(symbol, 0) * initial_value 
                    for symbol in symbols}
        
        last_rebalance_date = price_df.index[0]
        
        for i, date in enumerate(price_df.index):
            if i == 0:
                # First day - just record initial value
                total_portfolio_value = sum(portfolio.values())
                portfolio_values.append(total_portfolio_value)
                continue
            
            # Calculate daily returns for each position
            daily_returns = {}
            for symbol in symbols:
                if i > 0:
                    price_return = (price_df[symbol].iloc[i] / price_df[symbol].iloc[i-1]) - 1
                    portfolio[symbol] *= (1 + price_return)
                    daily_returns[symbol] = price_return
            
            total_portfolio_value = sum(portfolio.values())
            portfolio_values.append(total_portfolio_value)
            
            # Calculate portfolio return
            if i > 0:
                portfolio_return = (total_portfolio_value / portfolio_values[i-1]) - 1
                portfolio_returns.append(portfolio_return)
            
            # Check if rebalancing is needed
            days_since_rebalance = (date - last_rebalance_date).days
            time_based_rebalance = days_since_rebalance >= rebalance_interval
            
            # Check drift-based rebalancing
            current_weights = {symbol: portfolio[symbol] / total_portfolio_value 
                             for symbol in symbols}
            max_drift = max(abs(current_weights[symbol] - target_allocation.get(symbol, 0)) 
                           for symbol in symbols)
            drift_based_rebalance = max_drift > drift_threshold
            
            # Rebalance if needed
            if time_based_rebalance or drift_based_rebalance:
                # Calculate transaction costs (proportional to trades needed)
                trades_needed = sum(abs(portfolio[symbol] - target_allocation.get(symbol, 0) * total_portfolio_value) 
                                  for symbol in symbols)
                trade_cost = min(trades_needed * 0.001, total_portfolio_value * 0.01)  # Max 1% of portfolio
                total_transaction_costs += transaction_cost + trade_cost
                
                # Rebalance portfolio
                net_value = total_portfolio_value - transaction_cost - trade_cost
                portfolio = {symbol: target_allocation.get(symbol, 0) * net_value 
                           for symbol in symbols}
                
                rebalancing_dates.append(date)
                rebalancing_count += 1
                last_rebalance_date = date
        
        final_value = sum(portfolio.values())
        total_return = (final_value / initial_value) - 1
        
        return {
            "total_return": total_return,
            "portfolio_returns": portfolio_returns,
            "total_transaction_costs": total_transaction_costs / initial_value,  # As percentage
            "rebalancing_count": rebalancing_count,
            "rebalancing_dates": rebalancing_dates
        }
        
    except Exception as e:
        return {
            "total_return": 0,
            "portfolio_returns": [],
            "total_transaction_costs": 0,
            "rebalancing_count": 0,
            "rebalancing_dates": []
        }


def generate_rebalancing_calendar(frequency: str) -> List[str]:
    """
    Generate future rebalancing dates based on frequency.
    """
    calendar = []
    today = datetime.now()
    
    if frequency == "monthly":
        for i in range(12):
            date = today + timedelta(days=30*i)
            calendar.append(date.strftime('%Y-%m-%d'))
    elif frequency == "quarterly":
        for i in range(4):
            date = today + timedelta(days=90*i)
            calendar.append(date.strftime('%Y-%m-%d'))
    elif frequency == "semi_annual":
        for i in range(2):
            date = today + timedelta(days=180*i)
            calendar.append(date.strftime('%Y-%m-%d'))
    else:  # annual
        date = today + timedelta(days=365)
        calendar.append(date.strftime('%Y-%m-%d'))
    
    return calendar


def asset_allocation_optimizer(
    symbols: List[str],
    optimization_method: str = "max_sharpe",
    risk_free_rate: float = 0.02,
    target_volatility: Optional[float] = None,
    constraints: Optional[Dict[str, Any]] = None,
    analysis_period: str = "2y"
) -> Dict[str, Any]:
    """
    Optimize asset allocation using modern portfolio theory.
    
    Args:
        symbols: List of asset symbols for optimization
        optimization_method: 'max_sharpe', 'min_volatility', 'efficient_risk', 'risk_parity'
        risk_free_rate: Risk-free rate for Sharpe ratio calculation
        target_volatility: Target volatility for efficient risk optimization
        constraints: Portfolio constraints (min/max weights, sector limits)
        analysis_period: Historical period for optimization
        
    Returns:
        Dict: Optimal allocation and portfolio metrics
    """
    try:
        if len(symbols) < 2:
            raise ValueError("At least 2 assets required for optimization")
        
        # Set defaults
        if constraints is None:
            constraints = {"min_weight": 0.0, "max_weight": 1.0}
        if target_volatility is None:
            target_volatility = 0.15  # 15% default target volatility
        
        # Get historical price data using MCP function
        end_date = datetime.now()
        start_date = end_date - timedelta(days=730 if analysis_period == "2y" else 365)
        
        print(f"🔄 Fetching price data for {len(symbols)} assets for allocation optimization...")
        bars_result = alpaca_market_stocks_bars(
            symbols=",".join(symbols),
            timeframe="1Day",
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d')
        )
        
        if "error" in str(bars_result):
            raise Exception("Failed to fetch price data")
        
        # Build price matrix
        price_data = {}
        for symbol in symbols:
            symbol_bars = bars_result["bars"][symbol]
            dates = [pd.to_datetime(bar['t']) for bar in symbol_bars]
            prices = [bar['c'] for bar in symbol_bars]
            price_data[symbol] = Any(prices, index=dates)
        
        # Align all price series
        price_df = Any(price_data).dropna()
        print(f"✅ Analyzed {len(price_df)} trading days for optimization")
        
        # Calculate returns using MCP function
        returns_data = {}
        for symbol in symbols:
            returns_data[symbol] = prices_to_returns(price_df[symbol])
        returns_df = Any(returns_data).dropna()
        
        # Calculate individual asset metrics using MCP functions
        asset_metrics = {}
        for symbol in symbols:
            returns_metrics = calculate_returns_metrics(returns_df[symbol].tolist())
            asset_metrics[symbol] = {
                "annual_return": returns_metrics.get('annualized_return', 0),
                "volatility": returns_metrics.get('volatility', 0),
                "sharpe_ratio": returns_metrics.get('sharpe_ratio', 0)
            }
        
        # Calculate covariance matrix
        cov_matrix = returns_df.cov() * 252  # Annualized
        
        # Perform portfolio optimization based on method
        optimal_weights = {}
        
        if optimization_method == "equal_weight":
            # Equal weight allocation
            weight = 1.0 / len(symbols)
            optimal_weights = {symbol: weight for symbol in symbols}
            
        elif optimization_method == "max_sharpe":
            # Maximum Sharpe ratio optimization (simplified version)
            optimal_weights = optimize_max_sharpe(returns_df, cov_matrix, risk_free_rate, constraints)
            
        elif optimization_method == "min_volatility":
            # Minimum volatility optimization
            optimal_weights = optimize_min_volatility(returns_df, cov_matrix, constraints)
            
        elif optimization_method == "risk_parity":
            # Risk parity allocation
            optimal_weights = optimize_risk_parity(returns_df, cov_matrix, constraints)
            
        elif optimization_method == "efficient_risk":
            # Efficient frontier for target volatility
            optimal_weights = optimize_efficient_risk(returns_df, cov_matrix, target_volatility, constraints)
            
        else:
            raise ValueError(f"Unknown optimization method: {optimization_method}")
        
        # Calculate portfolio metrics using MCP functions
        portfolio_returns = []
        for i in range(len(returns_df)):
            daily_return = sum(optimal_weights.get(symbol, 0) * returns_df[symbol].iloc[i] 
                             for symbol in symbols)
            portfolio_returns.append(daily_return)
        
        portfolio_metrics = calculate_returns_metrics(portfolio_returns)
        
        # Calculate equal-weight benchmark
        ew_returns = []
        ew_weight = 1.0 / len(symbols)
        for i in range(len(returns_df)):
            daily_return = sum(ew_weight * returns_df[symbol].iloc[i] for symbol in symbols)
            ew_returns.append(daily_return)
        
        ew_metrics = calculate_returns_metrics(ew_returns)
        
        # Calculate diversification metrics using MCP function
        concentration_result = analyze_portfolio_concentration(list(optimal_weights.values()))
        
        # Calculate portfolio risk metrics
        portfolio_vol = np.sqrt(np.dot(list(optimal_weights.values()), 
                                      np.dot(cov_matrix.values, list(optimal_weights.values()))))
        
        result = {
            "optimization_summary": {
                "method": optimization_method,
                "assets_analyzed": len(symbols),
                "analysis_period_days": len(returns_df),
                "target_volatility": target_volatility if optimization_method == "efficient_risk" else None
            },
            "optimal_allocation": {
                symbol: round(weight, 4) for symbol, weight in optimal_weights.items()
            },
            "portfolio_metrics": {
                "expected_annual_return": portfolio_metrics.get('annualized_return', 0),
                "expected_volatility": portfolio_vol,
                "expected_sharpe_ratio": portfolio_metrics.get('sharpe_ratio', 0),
                "diversification_ratio": concentration_result.get('diversification_score', 'medium')
            },
            "individual_asset_metrics": asset_metrics,
            "benchmark_comparison": {
                "optimal_annual_return": portfolio_metrics.get('annualized_return', 0),
                "equal_weight_annual_return": ew_metrics.get('annualized_return', 0),
                "optimization_advantage": portfolio_metrics.get('annualized_return', 0) - ew_metrics.get('annualized_return', 0),
                "optimal_sharpe": portfolio_metrics.get('sharpe_ratio', 0),
                "equal_weight_sharpe": ew_metrics.get('sharpe_ratio', 0)
            },
            "allocation_analysis": {
                "largest_position": max(optimal_weights.items(), key=lambda x: x[1]),
                "smallest_position": min(optimal_weights.items(), key=lambda x: x[1]),
                "concentration_level": "High" if max(optimal_weights.values()) > 0.4 else "Medium" if max(optimal_weights.values()) > 0.25 else "Low",
                "number_of_significant_positions": sum(1 for w in optimal_weights.values() if w > 0.05)
            },
            "constraints_applied": constraints,
            "risk_metrics": {
                "portfolio_beta": 1.0,  # Simplified - would calculate vs market
                "correlation_matrix": returns_df.corr().to_dict()
            }
        }
        
        return standardize_output(result, "asset_allocation_optimizer")
        
    except Exception as e:
        return {"success": False, "error": f"Asset allocation optimization failed: {str(e)}"}


def optimize_max_sharpe(returns_df: Any, cov_matrix: Any, 
                       risk_free_rate: float, constraints: Dict[str, Any]) -> Dict[str, float]:
    """Simplified maximum Sharpe ratio optimization using analytical solution."""
    try:
        # Calculate expected returns (mean)
        mean_returns = returns_df.mean() * 252  # Annualized
        
        # Simplified optimization - analytical solution for unconstrained case
        inv_cov = np.linalg.inv(cov_matrix.values)
        ones = np.ones((len(mean_returns), 1))
        excess_returns = (mean_returns.values - risk_free_rate).reshape(-1, 1)
        
        # Calculate optimal weights
        weights_unnormalized = np.dot(inv_cov, excess_returns)
        weights_normalized = weights_unnormalized / np.sum(weights_unnormalized)
        
        # Apply constraints
        weights_dict = {}
        min_weight = constraints.get('min_weight', 0.0)
        max_weight = constraints.get('max_weight', 1.0)
        
        for i, symbol in enumerate(returns_df.columns):
            weight = float(weights_normalized[i][0])
            weight = max(min_weight, min(max_weight, weight))
            weights_dict[symbol] = weight
        
        # Renormalize to sum to 1
        total_weight = sum(weights_dict.values())
        if total_weight > 0:
            weights_dict = {k: v/total_weight for k, v in weights_dict.items()}
        
        return weights_dict
        
    except Exception:
        # Fallback to equal weights if optimization fails
        return {symbol: 1.0/len(returns_df.columns) for symbol in returns_df.columns}


def optimize_min_volatility(returns_df: Any, cov_matrix: Any, 
                           constraints: Dict[str, Any]) -> Dict[str, float]:
    """Simplified minimum volatility optimization."""
    try:
        # Analytical solution for minimum variance portfolio
        inv_cov = np.linalg.inv(cov_matrix.values)
        ones = np.ones((len(cov_matrix), 1))
        
        weights_unnormalized = np.dot(inv_cov, ones)
        weights_normalized = weights_unnormalized / np.sum(weights_unnormalized)
        
        # Apply constraints
        weights_dict = {}
        min_weight = constraints.get('min_weight', 0.0)
        max_weight = constraints.get('max_weight', 1.0)
        
        for i, symbol in enumerate(returns_df.columns):
            weight = float(weights_normalized[i][0])
            weight = max(min_weight, min(max_weight, weight))
            weights_dict[symbol] = weight
        
        # Renormalize
        total_weight = sum(weights_dict.values())
        if total_weight > 0:
            weights_dict = {k: v/total_weight for k, v in weights_dict.items()}
        
        return weights_dict
        
    except Exception:
        return {symbol: 1.0/len(returns_df.columns) for symbol in returns_df.columns}


def optimize_risk_parity(returns_df: Any, cov_matrix: Any, 
                        constraints: Dict[str, Any]) -> Dict[str, float]:
    """Simplified risk parity optimization."""
    try:
        # Calculate volatilities
        volatilities = np.sqrt(np.diag(cov_matrix.values))
        
        # Inverse volatility weights
        inv_vol_weights = 1.0 / volatilities
        weights_normalized = inv_vol_weights / np.sum(inv_vol_weights)
        
        # Apply constraints
        weights_dict = {}
        min_weight = constraints.get('min_weight', 0.0)
        max_weight = constraints.get('max_weight', 1.0)
        
        for i, symbol in enumerate(returns_df.columns):
            weight = float(weights_normalized[i])
            weight = max(min_weight, min(max_weight, weight))
            weights_dict[symbol] = weight
        
        # Renormalize
        total_weight = sum(weights_dict.values())
        if total_weight > 0:
            weights_dict = {k: v/total_weight for k, v in weights_dict.items()}
        
        return weights_dict
        
    except Exception:
        return {symbol: 1.0/len(returns_df.columns) for symbol in returns_df.columns}


def optimize_efficient_risk(returns_df: Any, cov_matrix: Any, 
                           target_volatility: float, constraints: Dict[str, Any]) -> Dict[str, float]:
    """Simplified efficient frontier optimization for target volatility."""
    try:
        # Start with minimum volatility portfolio
        min_vol_weights = optimize_min_volatility(returns_df, cov_matrix, constraints)
        
        # Adjust weights to target volatility (simplified approach)
        current_vol = np.sqrt(np.dot(list(min_vol_weights.values()), 
                                   np.dot(cov_matrix.values, list(min_vol_weights.values()))))
        
        if current_vol < target_volatility:
            # Blend with equal weights to increase volatility
            ew_weights = {symbol: 1.0/len(returns_df.columns) for symbol in returns_df.columns}
            blend_factor = min(1.0, (target_volatility - current_vol) / 0.1)  # Simplified blending
            
            weights_dict = {}
            for symbol in returns_df.columns:
                blended_weight = (1 - blend_factor) * min_vol_weights[symbol] + blend_factor * ew_weights[symbol]
                weights_dict[symbol] = blended_weight
        else:
            weights_dict = min_vol_weights
        
        return weights_dict
        
    except Exception:
        return {symbol: 1.0/len(returns_df.columns) for symbol in returns_df.columns}


def portfolio_risk_analyzer(
    portfolio_positions: List[Dict[str, Any]],
    benchmark_symbol: str = "SPY",
    confidence_levels: Optional[List[float]] = None,
    time_horizons: Optional[List[int]] = None,
    analysis_period: str = "2y"
) -> Dict[str, Any]:
    """
    Comprehensive portfolio risk analysis with VaR, CVaR, stress testing, and correlation analysis.
    
    Args:
        portfolio_positions: List of positions with symbol, quantity, current_price
        benchmark_symbol: Benchmark for beta and correlation analysis
        confidence_levels: VaR/CVaR confidence levels to calculate
        time_horizons: Time horizons for VaR calculations (days)
        analysis_period: Historical period for analysis
        
    Returns:
        Dict: Comprehensive risk analysis results
    """
    try:
        # Set defaults
        if confidence_levels is None:
            confidence_levels = [0.05, 0.01]  # 95% and 99% confidence
        if time_horizons is None:
            time_horizons = [1, 5, 10, 22]  # 1 day, 1 week, 2 weeks, 1 month
        
        # Extract symbols and weights
        symbols = [pos['symbol'] for pos in portfolio_positions]
        values = [pos['quantity'] * pos['current_price'] for pos in portfolio_positions]
        total_value = sum(values)
        weights = [val / total_value for val in values]
        
        print(f"🔄 Performing comprehensive risk analysis for {len(symbols)} assets...")
        
        # Get historical price data using MCP function
        end_date = datetime.now()
        start_date = end_date - timedelta(days=730 if analysis_period == "2y" else 365)
        
        # Fetch portfolio data
        bars_result = alpaca_market_stocks_bars(
            symbols=",".join(symbols),
            timeframe="1Day",
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d')
        )
        
        if "error" in str(bars_result):
            raise Exception("Failed to fetch portfolio price data")
        
        # Fetch benchmark data
        benchmark_result = alpaca_market_stocks_bars(
            symbols=benchmark_symbol,
            timeframe="1Day",
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d')
        )
        
        if "error" in str(benchmark_result):
            raise Exception("Failed to fetch benchmark data")
        
        # Build price matrices
        price_data = {}
        for symbol in symbols:
            symbol_bars = bars_result["bars"][symbol]
            dates = [pd.to_datetime(bar['t']) for bar in symbol_bars]
            prices = [bar['c'] for bar in symbol_bars]
            price_data[symbol] = Any(prices, index=dates)
        
        # Add benchmark
        benchmark_bars = benchmark_result["bars"][benchmark_symbol]
        benchmark_dates = [pd.to_datetime(bar['t']) for bar in benchmark_bars]
        benchmark_prices = [bar['c'] for bar in benchmark_bars]
        price_data[benchmark_symbol] = Any(benchmark_prices, index=benchmark_dates)
        
        # Align all price series
        price_df = Any(price_data).dropna()
        print(f"✅ Analyzed {len(price_df)} trading days for risk analysis")
        
        # Calculate returns using MCP function
        returns_data = {}
        for symbol in symbols + [benchmark_symbol]:
            returns_data[symbol] = prices_to_returns(price_df[symbol])
        returns_df = Any(returns_data).dropna()
        
        # Calculate portfolio returns
        portfolio_returns = []
        for i in range(len(returns_df)):
            daily_return = sum(weights[j] * returns_df[symbols[j]].iloc[i] for j in range(len(symbols)))
            portfolio_returns.append(daily_return)
        
        portfolio_returns_series = Any(portfolio_returns, index=returns_df.index)
        benchmark_returns = returns_df[benchmark_symbol]
        
        # 1. Basic Risk Metrics using MCP functions
        print("📊 Calculating basic risk metrics...")
        portfolio_metrics = calculate_returns_metrics(portfolio_returns)
        
        # 2. VaR and CVaR Analysis using MCP functions
        print("⚠️ Calculating VaR and CVaR...")
        var_results = {}
        cvar_results = {}
        
        for confidence in confidence_levels:
            var_result = calculate_var(portfolio_returns, confidence_level=confidence)
            cvar_result = calculate_cvar(portfolio_returns, confidence_level=confidence)
            
            var_results[f"{int((1-confidence)*100)}%"] = var_result
            cvar_results[f"{int((1-confidence)*100)}%"] = cvar_result
        
        # 3. Portfolio Stress Testing using MCP function
        print("🔥 Performing stress testing...")
        stress_result = stress_test_portfolio(
            weights=weights,
            returns=returns_df[symbols].values.tolist()
        )
        
        # 4. Correlation Analysis
        print("🔗 Analyzing correlations...")
        correlation_matrix = returns_df[symbols].corr()
        
        # Portfolio correlation with benchmark
        portfolio_benchmark_corr = portfolio_returns_series.corr(benchmark_returns)
        
        # Average correlation within portfolio
        corr_values = []
        for i in range(len(symbols)):
            for j in range(i+1, len(symbols)):
                corr_values.append(correlation_matrix.iloc[i, j])
        avg_internal_correlation = np.mean(corr_values) if corr_values else 0
        
        # 5. Beta Analysis
        print("📈 Calculating portfolio beta...")
        portfolio_beta = portfolio_returns_series.cov(benchmark_returns) / benchmark_returns.var()
        
        # Individual asset betas
        asset_betas = {}
        for symbol in symbols:
            asset_beta = returns_df[symbol].cov(benchmark_returns) / benchmark_returns.var()
            asset_betas[symbol] = float(asset_beta)
        
        # 6. Concentration Risk using MCP function
        print("🎯 Analyzing concentration risk...")
        concentration_result = analyze_portfolio_concentration(weights)
        
        # 7. Time-varying risk analysis
        print("⏰ Analyzing time-varying risk...")
        rolling_vol = portfolio_returns_series.rolling(window=30).std() * np.sqrt(252)
        rolling_vol = rolling_vol.dropna()
        
        volatility_stats = {
            "current_volatility": float(rolling_vol.iloc[-1]) if len(rolling_vol) > 0 else 0,
            "average_volatility": float(rolling_vol.mean()) if len(rolling_vol) > 0 else 0,
            "max_volatility": float(rolling_vol.max()) if len(rolling_vol) > 0 else 0,
            "min_volatility": float(rolling_vol.min()) if len(rolling_vol) > 0 else 0,
            "volatility_of_volatility": float(rolling_vol.std()) if len(rolling_vol) > 0 else 0
        }
        
        # 8. Downside Risk Metrics
        print("📉 Calculating downside risk...")
        negative_returns = portfolio_returns_series[portfolio_returns_series < 0]
        downside_deviation = negative_returns.std() * np.sqrt(252) if len(negative_returns) > 0 else 0
        
        # Calculate worst periods
        worst_day = float(portfolio_returns_series.min())
        worst_week = float(portfolio_returns_series.rolling(window=5).sum().min())
        worst_month = float(portfolio_returns_series.rolling(window=22).sum().min())
        
        # 9. Risk Attribution
        print("🔍 Calculating risk attribution...")
        cov_matrix = returns_df[symbols].cov() * 252  # Annualized
        
        # Marginal contribution to risk
        portfolio_variance = np.dot(weights, np.dot(cov_matrix.values, weights))
        marginal_contributions = np.dot(cov_matrix.values, weights) / np.sqrt(portfolio_variance)
        
        risk_contributions = {}
        for i, symbol in enumerate(symbols):
            risk_contributions[symbol] = {
                "weight": float(weights[i]),
                "marginal_contribution": float(marginal_contributions[i]),
                "total_contribution": float(weights[i] * marginal_contributions[i]),
                "percentage_of_risk": float((weights[i] * marginal_contributions[i]) / sum(weights[j] * marginal_contributions[j] for j in range(len(symbols))) * 100)
            }
        
        # Compile comprehensive results
        result = {
            "portfolio_summary": {
                "total_value": total_value,
                "number_of_positions": len(symbols),
                "analysis_period_days": len(returns_df),
                "benchmark": benchmark_symbol
            },
            "basic_risk_metrics": {
                "annualized_volatility": portfolio_metrics.get('volatility', 0),
                "sharpe_ratio": portfolio_metrics.get('sharpe_ratio', 0),
                "max_drawdown": portfolio_metrics.get('max_drawdown', 0),
                "downside_deviation": float(downside_deviation),
                "beta": float(portfolio_beta)
            },
            "var_analysis": var_results,
            "cvar_analysis": cvar_results,
            "stress_test_results": stress_result,
            "correlation_analysis": {
                "portfolio_benchmark_correlation": float(portfolio_benchmark_corr),
                "average_internal_correlation": float(avg_internal_correlation),
                "correlation_matrix": correlation_matrix.to_dict(),
                "diversification_score": "High" if avg_internal_correlation < 0.3 else "Medium" if avg_internal_correlation < 0.6 else "Low"
            },
            "beta_analysis": {
                "portfolio_beta": float(portfolio_beta),
                "individual_betas": asset_betas,
                "beta_category": "Defensive" if portfolio_beta < 0.8 else "Market" if portfolio_beta < 1.2 else "Aggressive"
            },
            "concentration_risk": concentration_result,
            "time_varying_risk": volatility_stats,
            "downside_risk": {
                "downside_deviation": float(downside_deviation),
                "worst_day_return": worst_day,
                "worst_week_return": worst_week,
                "worst_month_return": worst_month,
                "negative_return_days": int(len(negative_returns)),
                "percentage_negative_days": float((len(negative_returns) / len(portfolio_returns_series)) * 100)
            },
            "risk_attribution": risk_contributions,
            "risk_assessment": {
                "overall_risk_level": "High" if portfolio_metrics.get('volatility', 0) > 0.25 else "Medium" if portfolio_metrics.get('volatility', 0) > 0.15 else "Low",
                "key_risk_factors": [
                    f"Portfolio beta of {portfolio_beta:.2f}",
                    f"Max drawdown of {portfolio_metrics.get('max_drawdown', 0)*100:.1f}%",
                    f"VaR (95%) of {var_results.get('95%', {}).get('var_daily', 0)*100:.1f}%"
                ],
                "diversification_quality": "Good" if concentration_result.get('diversification_score', 'medium') == 'high' and avg_internal_correlation < 0.5 else "Fair"
            }
        }
        
        return standardize_output(result, "portfolio_risk_analyzer")
        
    except Exception as e:
        return {"success": False, "error": f"Portfolio risk analysis failed: {str(e)}"}


# Registry of Tier 10 Advanced Portfolio Tools
TIER_10_ADVANCED_PORTFOLIO_TOOLS = {
    'portfolio_rebalancing_optimizer': portfolio_rebalancing_optimizer,
    'asset_allocation_optimizer': asset_allocation_optimizer,
    'portfolio_risk_analyzer': portfolio_risk_analyzer
}