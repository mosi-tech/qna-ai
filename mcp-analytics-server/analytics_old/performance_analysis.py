"""
Performance Analysis Functions

Functions for calculating performance and risk-adjusted metrics, matching the 
categorical structure from financial-analysis-function-library.json

From financial-analysis-function-library.json category: performance_analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Union, Optional, List


def calculateSharpeRatio(
    returns: Union[pd.Series, Dict[str, Any]],
    risk_free_rate: float = 0.02,
    trading_days_per_year: int = 252
) -> Dict[str, Any]:
    """
    Calculate Sharpe ratio (risk-adjusted return).
    
    From financial-analysis-function-library.json
    
    Args:
        returns: pd.Series of returns or result from other functions
        risk_free_rate: Annual risk-free rate as decimal
        trading_days_per_year: Number of trading days per year
        
    Returns:
        {
            "sharpe_ratio": float,
            "excess_return": float,
            "volatility": float,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(returns, dict) and "returns" in returns:
            series = returns["returns"]
        elif isinstance(returns, dict) and "filtered_data" in returns:
            series = returns["filtered_data"]
        elif isinstance(returns, dict) and "resampled_data" in returns:
            series = returns["resampled_data"]
        elif isinstance(returns, pd.Series):
            series = returns
        else:
            return {"success": False, "error": "Invalid returns format"}
        
        if len(series) < 2:
            return {"success": False, "error": "Need at least 2 observations"}
        
        # Calculate components
        daily_rf_rate = risk_free_rate / trading_days_per_year
        excess_returns = series - daily_rf_rate
        
        mean_excess = excess_returns.mean()
        volatility = excess_returns.std()
        
        if volatility == 0:
            return {"success": False, "error": "Zero volatility - cannot calculate Sharpe ratio"}
        
        # Annualized Sharpe ratio
        sharpe_ratio = (mean_excess / volatility) * np.sqrt(trading_days_per_year)
        
        # Annualized excess return
        annualized_excess = mean_excess * trading_days_per_year
        annualized_volatility = volatility * np.sqrt(trading_days_per_year)
        
        return {
            "success": True,
            "sharpe_ratio": float(sharpe_ratio),
            "excess_return": float(annualized_excess),
            "volatility": float(annualized_volatility),
            "risk_free_rate": risk_free_rate
        }
        
    except Exception as e:
        return {"success": False, "error": f"Sharpe ratio calculation failed: {str(e)}"}


def calculateSortinoRatio(
    returns: Union[pd.Series, Dict[str, Any]],
    risk_free_rate: float = 0.02,
    trading_days_per_year: int = 252
) -> Dict[str, Any]:
    """
    Calculate Sortino ratio (downside risk-adjusted return).
    
    From financial-analysis-function-library.json
    
    Args:
        returns: pd.Series of returns or result from other functions
        risk_free_rate: Annual risk-free rate as decimal
        trading_days_per_year: Number of trading days per year
        
    Returns:
        {
            "sortino_ratio": float,
            "excess_return": float,
            "downside_deviation": float,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(returns, dict) and "returns" in returns:
            series = returns["returns"]
        elif isinstance(returns, dict) and "filtered_data" in returns:
            series = returns["filtered_data"]
        elif isinstance(returns, dict) and "resampled_data" in returns:
            series = returns["resampled_data"]
        elif isinstance(returns, pd.Series):
            series = returns
        else:
            return {"success": False, "error": "Invalid returns format"}
        
        if len(series) < 2:
            return {"success": False, "error": "Need at least 2 observations"}
        
        # Calculate components
        daily_rf_rate = risk_free_rate / trading_days_per_year
        excess_returns = series - daily_rf_rate
        
        # Only consider negative excess returns for downside deviation
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0:
            return {"success": False, "error": "No downside returns - cannot calculate Sortino ratio"}
        
        mean_excess = excess_returns.mean()
        downside_deviation = np.sqrt((downside_returns ** 2).mean())
        
        # Annualized Sortino ratio
        sortino_ratio = (mean_excess / downside_deviation) * np.sqrt(trading_days_per_year)
        
        # Annualized metrics
        annualized_excess = mean_excess * trading_days_per_year
        annualized_downside_dev = downside_deviation * np.sqrt(trading_days_per_year)
        
        return {
            "success": True,
            "sortino_ratio": float(sortino_ratio),
            "excess_return": float(annualized_excess),
            "downside_deviation": float(annualized_downside_dev),
            "downside_days": len(downside_returns),
            "total_days": len(series)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Sortino ratio calculation failed: {str(e)}"}


def calculateCAGR(
    start_value: Union[float, Dict[str, Any]], 
    end_value: Union[float, None] = None, 
    years: Union[float, None] = None
) -> Dict[str, Any]:
    """
    Calculate Compound Annual Growth Rate.
    
    From financial-analysis-function-library.json
    
    Args:
        start_value: Starting value or price series
        end_value: Ending value (if start_value is a number)
        years: Number of years (if start_value is a number)
        
    Returns:
        {
            "cagr": float,
            "cagr_pct": str,
            "total_return": float,
            "years": float,
            "success": bool
        }
    """
    try:
        # Handle different input formats
        if isinstance(start_value, dict) and "prices" in start_value:
            # Price series format
            series = start_value["prices"]
            if len(series) < 2:
                return {"success": False, "error": "Need at least 2 price observations"}
            
            start_val = float(series.iloc[0])
            end_val = float(series.iloc[-1])
            
            # Calculate years from date index if available
            if hasattr(series.index[0], 'year'):
                start_date = series.index[0]
                end_date = series.index[-1]
                years_calc = (end_date - start_date).days / 365.25
            else:
                years_calc = len(series) / 252  # Assume daily data, 252 trading days per year
                
        elif isinstance(start_value, (int, float)) and end_value is not None and years is not None:
            # Direct values format
            start_val = float(start_value)
            end_val = float(end_value)
            years_calc = float(years)
        else:
            return {"success": False, "error": "Invalid input format"}
        
        if start_val <= 0 or end_val <= 0:
            return {"success": False, "error": "Values must be positive"}
        
        if years_calc <= 0:
            return {"success": False, "error": "Years must be positive"}
        
        # Calculate CAGR
        total_return = (end_val / start_val) - 1
        cagr = (end_val / start_val) ** (1 / years_calc) - 1
        
        return {
            "success": True,
            "cagr": float(cagr),
            "cagr_pct": f"{cagr * 100:.2f}%",
            "total_return": float(total_return),
            "total_return_pct": f"{total_return * 100:.2f}%",
            "years": float(years_calc),
            "start_value": float(start_val),
            "end_value": float(end_val)
        }
        
    except Exception as e:
        return {"success": False, "error": f"CAGR calculation failed: {str(e)}"}


def calculateInformationRatio(
    returns: Union[pd.Series, Dict[str, Any]],
    benchmark_returns: Union[pd.Series, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate Information Ratio vs benchmark.
    
    From financial-analysis-function-library.json
    
    Args:
        returns: Portfolio return series
        benchmark_returns: Benchmark return series
        
    Returns:
        {
            "information_ratio": float,
            "excess_return": float,
            "tracking_error": float,
            "num_observations": int,
            "success": bool
        }
    """
    try:
        # Handle input formats
        def extract_series(data):
            if isinstance(data, dict) and "returns" in data:
                return data["returns"]
            elif isinstance(data, dict) and "filtered_data" in data:
                return data["filtered_data"]
            elif isinstance(data, pd.Series):
                return data
            else:
                raise ValueError("Invalid data format")
        
        portfolio_series = extract_series(returns)
        benchmark_series = extract_series(benchmark_returns)
        
        # Align the series
        aligned_data = pd.DataFrame({
            'portfolio': portfolio_series,
            'benchmark': benchmark_series
        }).dropna()
        
        if len(aligned_data) < 10:
            return {"success": False, "error": "Need at least 10 aligned observations"}
        
        portfolio_aligned = aligned_data['portfolio']
        benchmark_aligned = aligned_data['benchmark']
        
        # Calculate excess returns
        excess_returns = portfolio_aligned - benchmark_aligned
        
        # Calculate Information Ratio components
        mean_excess_return = excess_returns.mean()
        tracking_error = excess_returns.std()
        
        if tracking_error == 0:
            return {"success": False, "error": "Zero tracking error - cannot calculate Information Ratio"}
        
        information_ratio = mean_excess_return / tracking_error
        
        # Annualize metrics
        annualized_excess = mean_excess_return * 252
        annualized_tracking_error = tracking_error * np.sqrt(252)
        annualized_ir = annualized_excess / annualized_tracking_error
        
        return {
            "success": True,
            "information_ratio": float(annualized_ir),
            "excess_return": float(annualized_excess),
            "excess_return_pct": f"{annualized_excess * 100:.2f}%",
            "tracking_error": float(annualized_tracking_error),
            "tracking_error_pct": f"{annualized_tracking_error * 100:.2f}%",
            "num_observations": len(aligned_data)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Information ratio calculation failed: {str(e)}"}


def calculateTreynorRatio(
    returns: Union[pd.Series, Dict[str, Any]],
    market_returns: Union[pd.Series, Dict[str, Any]],
    risk_free_rate: float = 0.02
) -> Dict[str, Any]:
    """
    Calculate Treynor ratio.
    
    From financial-analysis-function-library.json
    
    Args:
        returns: Portfolio return series
        market_returns: Market return series
        risk_free_rate: Annual risk-free rate as decimal
        
    Returns:
        {
            "treynor_ratio": float,
            "excess_return": float,
            "beta": float,
            "num_observations": int,
            "success": bool
        }
    """
    try:
        # Handle input formats
        def extract_series(data):
            if isinstance(data, dict) and "returns" in data:
                return data["returns"]
            elif isinstance(data, dict) and "filtered_data" in data:
                return data["filtered_data"]
            elif isinstance(data, pd.Series):
                return data
            else:
                raise ValueError("Invalid data format")
        
        portfolio_series = extract_series(returns)
        market_series = extract_series(market_returns)
        
        # Align the series
        aligned_data = pd.DataFrame({
            'portfolio': portfolio_series,
            'market': market_series
        }).dropna()
        
        if len(aligned_data) < 10:
            return {"success": False, "error": "Need at least 10 aligned observations"}
        
        portfolio_aligned = aligned_data['portfolio']
        market_aligned = aligned_data['market']
        
        # Calculate beta
        covariance = np.cov(portfolio_aligned, market_aligned)[0, 1]
        market_variance = np.var(market_aligned)
        
        if market_variance == 0:
            return {"success": False, "error": "Market variance is zero"}
        
        beta = covariance / market_variance
        
        if beta == 0:
            return {"success": False, "error": "Zero beta - cannot calculate Treynor ratio"}
        
        # Calculate Treynor ratio components
        daily_rf_rate = risk_free_rate / 252
        portfolio_excess = portfolio_aligned.mean() - daily_rf_rate
        
        # Annualized Treynor ratio
        annualized_excess = portfolio_excess * 252
        treynor_ratio = annualized_excess / beta
        
        return {
            "success": True,
            "treynor_ratio": float(treynor_ratio),
            "excess_return": float(annualized_excess),
            "excess_return_pct": f"{annualized_excess * 100:.2f}%",
            "beta": float(beta),
            "risk_free_rate": risk_free_rate,
            "num_observations": len(aligned_data)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Treynor ratio calculation failed: {str(e)}"}


def calculateCalmarRatio(
    returns: Union[pd.Series, Dict[str, Any]],
    trading_days_per_year: int = 252
) -> Dict[str, Any]:
    """
    Calculate Calmar ratio (annualized return / max drawdown).
    
    From financial-analysis-function-library.json
    
    Args:
        returns: pd.Series of returns or result from other functions
        trading_days_per_year: Number of trading days per year
        
    Returns:
        {
            "calmar_ratio": float,
            "annualized_return": float,
            "max_drawdown": float,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(returns, dict) and "returns" in returns:
            series = returns["returns"]
        elif isinstance(returns, dict) and "filtered_data" in returns:
            series = returns["filtered_data"]
        elif isinstance(returns, dict) and "resampled_data" in returns:
            series = returns["resampled_data"]
        elif isinstance(returns, pd.Series):
            series = returns
        else:
            return {"success": False, "error": "Invalid returns format"}
        
        if len(series) < 2:
            return {"success": False, "error": "Need at least 2 observations"}
        
        # Calculate annualized return
        total_return = (1 + series).prod() - 1
        years = len(series) / trading_days_per_year
        annualized_return = (1 + total_return) ** (1/years) - 1
        
        # Calculate max drawdown
        cumulative = (1 + series).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        if max_drawdown == 0:
            return {"success": False, "error": "Zero max drawdown - cannot calculate Calmar ratio"}
        
        calmar_ratio = annualized_return / abs(max_drawdown)
        
        return {
            "success": True,
            "calmar_ratio": float(calmar_ratio),
            "annualized_return": float(annualized_return),
            "max_drawdown": float(max_drawdown),
            "max_drawdown_pct": f"{max_drawdown * 100:.2f}%"
        }
        
    except Exception as e:
        return {"success": False, "error": f"Calmar ratio calculation failed: {str(e)}"}


def calculateAlpha(
    returns: Union[pd.Series, Dict[str, Any]],
    market_returns: Union[pd.Series, Dict[str, Any]],
    risk_free_rate: float = 0.02
) -> Dict[str, Any]:
    """
    Calculate Jensen's Alpha vs market.
    
    From financial-analysis-function-library.json
    
    Args:
        returns: Portfolio return series
        market_returns: Market return series  
        risk_free_rate: Annual risk-free rate as decimal
        
    Returns:
        {
            "alpha": float,
            "alpha_pct": str,
            "beta": float,
            "r_squared": float,
            "success": bool
        }
    """
    try:
        # Handle input formats
        def extract_series(data):
            if isinstance(data, dict) and "returns" in data:
                return data["returns"]
            elif isinstance(data, dict) and "filtered_data" in data:
                return data["filtered_data"]
            elif isinstance(data, pd.Series):
                return data
            else:
                raise ValueError("Invalid data format")
        
        portfolio_series = extract_series(returns)
        market_series = extract_series(market_returns)
        
        # Align the series
        aligned_data = pd.DataFrame({
            'portfolio': portfolio_series,
            'market': market_series
        }).dropna()
        
        if len(aligned_data) < 10:
            return {"success": False, "error": "Need at least 10 aligned observations"}
        
        portfolio_aligned = aligned_data['portfolio']
        market_aligned = aligned_data['market']
        
        # Calculate daily risk-free rate
        daily_rf_rate = risk_free_rate / 252
        
        # Calculate excess returns
        portfolio_excess = portfolio_aligned - daily_rf_rate
        market_excess = market_aligned - daily_rf_rate
        
        # Calculate beta and alpha using CAPM regression
        covariance = np.cov(portfolio_excess, market_excess)[0, 1]
        market_variance = np.var(market_excess)
        
        if market_variance == 0:
            return {"success": False, "error": "Market variance is zero"}
        
        beta = covariance / market_variance
        correlation = np.corrcoef(portfolio_excess, market_excess)[0, 1]
        r_squared = correlation ** 2
        
        # Alpha = Portfolio excess return - Beta * Market excess return
        portfolio_mean_excess = portfolio_excess.mean()
        market_mean_excess = market_excess.mean()
        alpha_daily = portfolio_mean_excess - (beta * market_mean_excess)
        
        # Annualize alpha
        alpha_annual = alpha_daily * 252
        
        return {
            "success": True,
            "alpha": float(alpha_annual),
            "alpha_pct": f"{alpha_annual * 100:.2f}%",
            "beta": float(beta),
            "r_squared": float(r_squared),
            "num_observations": len(aligned_data)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Alpha calculation failed: {str(e)}"}


def calculateAnnualizedReturn(
    prices: Union[pd.Series, List[float], Dict[str, Any]], 
    periods: int = 252
) -> Dict[str, Any]:
    """
    Calculate annualized return from price series.
    
    From financial-analysis-function-library.json
    
    Args:
        prices: Price data or return series
        periods: Number of periods per year (252 for daily, 52 for weekly, 12 for monthly)
        
    Returns:
        {
            "annualized_return": float,
            "total_return": float,
            "periods_held": int,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(prices, dict) and "prices" in prices:
            series = prices["prices"]
        elif isinstance(prices, dict) and "returns" in prices:
            series = prices["returns"]
            # For return series, calculate cumulative returns first
            series = (1 + series).cumprod()
        elif isinstance(prices, (list, np.ndarray)):
            series = pd.Series(prices)
        elif isinstance(prices, pd.Series):
            series = prices
        else:
            return {"success": False, "error": "Invalid price format"}
        
        if len(series) < 2:
            return {"success": False, "error": "Need at least 2 observations"}
        
        # Calculate total return
        start_price = series.iloc[0]
        end_price = series.iloc[-1]
        
        if start_price <= 0:
            return {"success": False, "error": "Starting price must be positive"}
        
        total_return = (end_price / start_price) - 1
        periods_held = len(series) - 1
        years = periods_held / periods
        
        if years <= 0:
            return {"success": False, "error": "Invalid time period"}
        
        # Calculate annualized return
        annualized_return = (1 + total_return) ** (1 / years) - 1
        
        return {
            "success": True,
            "annualized_return": float(annualized_return),
            "annualized_return_pct": f"{annualized_return * 100:.2f}%",
            "total_return": float(total_return),
            "total_return_pct": f"{total_return * 100:.2f}%",
            "periods_held": periods_held,
            "years": float(years)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Annualized return calculation failed: {str(e)}"}


def calculateAnnualizedVolatility(
    returns: Union[pd.Series, List[float], Dict[str, Any]], 
    periods_per_year: int = 252
) -> Dict[str, Any]:
    """
    Calculate annualized volatility.
    
    From financial-analysis-function-library.json
    
    Args:
        returns: Return series data
        periods_per_year: Number of periods per year (252 for daily, 52 for weekly, 12 for monthly)
        
    Returns:
        {
            "annualized_volatility": float,
            "volatility_pct": str,
            "num_observations": int,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(returns, dict) and "returns" in returns:
            series = returns["returns"]
        elif isinstance(returns, dict) and "log_returns" in returns:
            series = returns["log_returns"]
        elif isinstance(returns, (list, np.ndarray)):
            series = pd.Series(returns)
        elif isinstance(returns, pd.Series):
            series = returns
        else:
            return {"success": False, "error": "Invalid returns format"}
        
        if len(series) < 2:
            return {"success": False, "error": "Need at least 2 observations"}
        
        # Calculate volatility
        volatility = series.std()
        annualized_volatility = volatility * np.sqrt(periods_per_year)
        
        return {
            "success": True,
            "annualized_volatility": float(annualized_volatility),
            "volatility_pct": f"{annualized_volatility * 100:.2f}%",
            "daily_volatility": float(volatility),
            "num_observations": len(series),
            "periods_per_year": periods_per_year
        }
        
    except Exception as e:
        return {"success": False, "error": f"Annualized volatility calculation failed: {str(e)}"}


def calculateTotalReturn(
    start_price: Union[float, Dict[str, Any]], 
    end_price: Optional[float] = None, 
    dividends: Optional[List[float]] = None
) -> Dict[str, Any]:
    """
    Calculate total return including dividends.
    
    From financial-analysis-function-library.json
    
    Args:
        start_price: Starting price or price series
        end_price: Ending price (if start_price is a number)
        dividends: List of dividend payments during the period
        
    Returns:
        {
            "total_return": float,
            "price_return": float,
            "dividend_yield": float,
            "success": bool
        }
    """
    try:
        # Handle different input formats
        if isinstance(start_price, dict) and "prices" in start_price:
            # Price series format
            series = start_price["prices"]
            if len(series) < 2:
                return {"success": False, "error": "Need at least 2 price observations"}
            
            start_val = float(series.iloc[0])
            end_val = float(series.iloc[-1])
            dividends_list = dividends or []
            
        elif isinstance(start_price, (int, float)) and end_price is not None:
            # Direct values format
            start_val = float(start_price)
            end_val = float(end_price)
            dividends_list = dividends or []
        else:
            return {"success": False, "error": "Invalid input format"}
        
        if start_val <= 0:
            return {"success": False, "error": "Starting price must be positive"}
        
        # Calculate price return
        price_return = (end_val / start_val) - 1
        
        # Calculate dividend yield
        total_dividends = sum(dividends_list) if dividends_list else 0
        dividend_yield = total_dividends / start_val
        
        # Calculate total return
        total_return = price_return + dividend_yield
        
        return {
            "success": True,
            "total_return": float(total_return),
            "total_return_pct": f"{total_return * 100:.2f}%",
            "price_return": float(price_return),
            "price_return_pct": f"{price_return * 100:.2f}%",
            "dividend_yield": float(dividend_yield),
            "dividend_yield_pct": f"{dividend_yield * 100:.2f}%",
            "start_price": float(start_val),
            "end_price": float(end_val),
            "total_dividends": float(total_dividends)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Total return calculation failed: {str(e)}"}


def calculateWinRate(
    returns: Union[pd.Series, List[float], Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate percentage of positive returns.
    
    From financial-analysis-function-library.json
    
    Args:
        returns: Return series data
        
    Returns:
        {
            "win_rate": float,
            "win_rate_pct": str,
            "winning_periods": int,
            "total_periods": int,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(returns, dict) and "returns" in returns:
            series = returns["returns"]
        elif isinstance(returns, dict) and "log_returns" in returns:
            series = returns["log_returns"]
        elif isinstance(returns, (list, np.ndarray)):
            series = pd.Series(returns)
        elif isinstance(returns, pd.Series):
            series = returns
        else:
            return {"success": False, "error": "Invalid returns format"}
        
        if len(series) == 0:
            return {"success": False, "error": "No return data"}
        
        # Calculate win rate
        winning_periods = (series > 0).sum()
        total_periods = len(series)
        win_rate = winning_periods / total_periods
        
        # Additional statistics
        avg_winner = series[series > 0].mean() if winning_periods > 0 else 0
        avg_loser = series[series < 0].mean() if (series < 0).sum() > 0 else 0
        
        return {
            "success": True,
            "win_rate": float(win_rate),
            "win_rate_pct": f"{win_rate * 100:.2f}%",
            "winning_periods": int(winning_periods),
            "losing_periods": int((series < 0).sum()),
            "neutral_periods": int((series == 0).sum()),
            "total_periods": int(total_periods),
            "avg_winner": float(avg_winner),
            "avg_loser": float(avg_loser)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Win rate calculation failed: {str(e)}"}


# Registry for MCP server
PERFORMANCE_ANALYSIS_FUNCTIONS = {
    'calculateSharpeRatio': calculateSharpeRatio,
    'calculateSortinoRatio': calculateSortinoRatio,
    'calculateCAGR': calculateCAGR,
    'calculateInformationRatio': calculateInformationRatio,
    'calculateTreynorRatio': calculateTreynorRatio,
    'calculateCalmarRatio': calculateCalmarRatio,
    'calculateAlpha': calculateAlpha,
    'calculateAnnualizedReturn': calculateAnnualizedReturn,
    'calculateAnnualizedVolatility': calculateAnnualizedVolatility,
    'calculateTotalReturn': calculateTotalReturn,
    'calculateWinRate': calculateWinRate
}