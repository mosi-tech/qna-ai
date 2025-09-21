"""
Performance Metrics using empyrical library

All performance calculations using empyrical from requirements.txt
From financial-analysis-function-library.json
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Union, Optional
import warnings
warnings.filterwarnings('ignore')

# Use empyrical library from requirements.txt - no wheel reinvention
import empyrical

from ..utils.data_utils import validate_return_data, validate_price_data, standardize_output


def calculate_returns_metrics(returns: Union[pd.Series, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate comprehensive return metrics using empyrical.
    
    From financial-analysis-function-library.json
    Uses empyrical library instead of manual calculations - no code duplication
    
    Args:
        returns: Return series
        
    Returns:
        Dict: Comprehensive return metrics
    """
    try:
        returns_series = validate_return_data(returns)
        
        # Use empyrical library - leveraging requirements.txt
        total_return = empyrical.cum_returns_final(returns_series)
        annual_return = empyrical.annual_return(returns_series)
        cumulative_returns = empyrical.cum_returns(returns_series)
        
        result = {
            "total_return": float(total_return),
            "total_return_pct": f"{total_return * 100:.2f}%",
            "annual_return": float(annual_return),
            "annual_return_pct": f"{annual_return * 100:.2f}%",
            "cumulative_returns": cumulative_returns,
            "num_observations": len(returns_series)
        }
        
        return standardize_output(result, "calculate_returns_metrics")
        
    except Exception as e:
        return {"success": False, "error": f"Returns calculation failed: {str(e)}"}


def calculate_risk_metrics(returns: Union[pd.Series, Dict[str, Any]], 
                          risk_free_rate: float = 0.02) -> Dict[str, Any]:
    """
    Calculate comprehensive risk metrics using empyrical.
    
    From financial-analysis-function-library.json
    Uses empyrical library instead of manual calculations - no code duplication
    
    Args:
        returns: Return series
        risk_free_rate: Risk-free rate
        
    Returns:
        Dict: Comprehensive risk metrics
    """
    try:
        returns_series = validate_return_data(returns)
        
        # Use empyrical library - leveraging requirements.txt
        volatility = empyrical.annual_volatility(returns_series)
        sharpe_ratio = empyrical.sharpe_ratio(returns_series, risk_free=risk_free_rate)
        sortino_ratio = empyrical.sortino_ratio(returns_series, required_return=risk_free_rate)
        max_drawdown = empyrical.max_drawdown(returns_series)
        calmar_ratio = empyrical.calmar_ratio(returns_series)
        var_95 = empyrical.value_at_risk(returns_series, cutoff=0.05)
        cvar_95 = empyrical.conditional_value_at_risk(returns_series, cutoff=0.05)
        skewness = empyrical.stats.skew(returns_series)
        kurtosis = empyrical.stats.kurtosis(returns_series)
        
        result = {
            "volatility": float(volatility),
            "volatility_pct": f"{volatility * 100:.2f}%",
            "sharpe_ratio": float(sharpe_ratio),
            "max_drawdown": float(max_drawdown),
            "max_drawdown_pct": f"{max_drawdown * 100:.2f}%",
            "sortino_ratio": float(sortino_ratio),
            "calmar_ratio": float(calmar_ratio),
            "var_95": float(var_95),
            "var_95_pct": f"{var_95 * 100:.2f}%",
            "cvar_95": float(cvar_95),
            "cvar_95_pct": f"{cvar_95 * 100:.2f}%",
            "skewness": float(skewness),
            "kurtosis": float(kurtosis)
        }
        
        return standardize_output(result, "calculate_risk_metrics")
        
    except Exception as e:
        return {"success": False, "error": f"Risk calculation failed: {str(e)}"}


def calculate_benchmark_metrics(returns: Union[pd.Series, Dict[str, Any]],
                                benchmark_returns: Union[pd.Series, Dict[str, Any]],
                                risk_free_rate: float = 0.02) -> Dict[str, Any]:
    """
    Calculate benchmark comparison metrics using empyrical.
    
    From financial-analysis-function-library.json
    Uses empyrical library instead of manual calculations - no code duplication
    
    Args:
        returns: Portfolio returns
        benchmark_returns: Benchmark returns
        risk_free_rate: Risk-free rate
        
    Returns:
        Dict: Benchmark comparison metrics
    """
    try:
        portfolio_returns = validate_return_data(returns)
        benchmark_returns = validate_return_data(benchmark_returns)
        
        # Align series
        from ..utils.data_utils import align_series
        portfolio_aligned, benchmark_aligned = align_series(portfolio_returns, benchmark_returns)
        
        if empyrical is None:
            # Basic calculations
            excess_returns = portfolio_aligned - benchmark_aligned
            tracking_error = excess_returns.std() * np.sqrt(252)
            information_ratio = excess_returns.mean() * 252 / tracking_error if tracking_error > 0 else 0
            
            # Beta calculation
            covariance = np.cov(portfolio_aligned, benchmark_aligned)[0, 1]
            benchmark_variance = np.var(benchmark_aligned)
            beta = covariance / benchmark_variance if benchmark_variance > 0 else 1
            
            alpha = portfolio_aligned.mean() * 252 - (risk_free_rate + beta * (benchmark_aligned.mean() * 252 - risk_free_rate))
        else:
            # Use empyrical library - leveraging requirements.txt
            alpha = empyrical.alpha(portfolio_aligned, benchmark_aligned, risk_free=risk_free_rate)
            beta = empyrical.beta(portfolio_aligned, benchmark_aligned)
            tracking_error = empyrical.tracking_error(portfolio_aligned, benchmark_aligned)
            information_ratio = empyrical.excess_sharpe(portfolio_aligned, benchmark_aligned)
            up_capture = empyrical.up_capture(portfolio_aligned, benchmark_aligned)
            down_capture = empyrical.down_capture(portfolio_aligned, benchmark_aligned)
        
        result = {
            "alpha": float(alpha),
            "alpha_pct": f"{alpha * 100:.2f}%",
            "beta": float(beta),
            "tracking_error": float(tracking_error),
            "tracking_error_pct": f"{tracking_error * 100:.2f}%",
            "information_ratio": float(information_ratio),
        }
        
        # Add advanced metrics if empyrical available
        if empyrical is not None:
            result.update({
                "up_capture": float(up_capture),
                "down_capture": float(down_capture)
            })
        
        return standardize_output(result, "calculate_benchmark_metrics")
        
    except Exception as e:
        return {"success": False, "error": f"Benchmark comparison failed: {str(e)}"}


def calculate_drawdown_analysis(returns: Union[pd.Series, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate detailed drawdown analysis using empyrical.
    
    From financial-analysis-function-library.json
    Uses empyrical library instead of manual calculations - no code duplication
    
    Args:
        returns: Return series
        
    Returns:
        Dict: Drawdown analysis
    """
    try:
        returns_series = validate_return_data(returns)
        
        if empyrical is None:
            # Basic calculations
            cumulative = (1 + returns_series).cumprod()
            running_max = cumulative.expanding().max()
            drawdown_series = (cumulative - running_max) / running_max
            max_drawdown = drawdown_series.min()
        else:
            # Use empyrical library - leveraging requirements.txt
            max_drawdown = empyrical.max_drawdown(returns_series)
            drawdown_series = empyrical.drawdown_details(empyrical.cum_returns(returns_series))
        
        result = {
            "max_drawdown": float(max_drawdown),
            "max_drawdown_pct": f"{max_drawdown * 100:.2f}%",
            "drawdown_series": drawdown_series if isinstance(drawdown_series, pd.Series) else pd.Series(drawdown_series)
        }
        
        return standardize_output(result, "calculate_drawdown_analysis")
        
    except Exception as e:
        return {"success": False, "error": f"Drawdown analysis failed: {str(e)}"}


def calculate_annualized_return(prices: Union[pd.Series, Dict[str, Any]], periods: int) -> float:
    """
    Calculate annualized return from price series.
    
    From financial-analysis-function-library.json performance_analysis category
    Uses empyrical library instead of manual calculations - no code duplication
    
    Args:
        prices: Price series
        periods: Number of periods per year (252 for daily, 12 for monthly)
        
    Returns:
        float: Annualized return
    """
    try:
        price_series = validate_price_data(prices)
        
        # Calculate returns from prices
        returns = price_series.pct_change().dropna()
        
        # Use empyrical for annualized return
        annual_return = empyrical.annual_return(returns, period=periods)
        
        return float(annual_return)
        
    except Exception as e:
        raise ValueError(f"Annualized return calculation failed: {str(e)}")


def calculate_annualized_volatility(returns: Union[pd.Series, Dict[str, Any]], periods_per_year: int) -> float:
    """
    Calculate annualized volatility.
    
    From financial-analysis-function-library.json performance_analysis category
    Uses empyrical library instead of manual calculations - no code duplication
    
    Args:
        returns: Return series
        periods_per_year: Number of periods per year
        
    Returns:
        float: Annualized volatility
    """
    try:
        returns_series = validate_return_data(returns)
        
        # Use empyrical for annualized volatility
        annual_vol = empyrical.annual_volatility(returns_series, period=periods_per_year)
        
        return float(annual_vol)
        
    except Exception as e:
        raise ValueError(f"Annualized volatility calculation failed: {str(e)}")


def calculate_cagr(start_value: float, end_value: float, years: float) -> float:
    """
    Calculate Compound Annual Growth Rate.
    
    From financial-analysis-function-library.json performance_analysis category
    Simple CAGR calculation using numpy - no code duplication
    
    Args:
        start_value: Starting value
        end_value: Ending value
        years: Number of years
        
    Returns:
        float: CAGR as decimal
    """
    try:
        if start_value <= 0:
            raise ValueError("Start value must be positive")
        if years <= 0:
            raise ValueError("Years must be positive")
        
        # CAGR formula: (end_value / start_value)^(1/years) - 1
        cagr = np.power(end_value / start_value, 1.0 / years) - 1
        
        return float(cagr)
        
    except Exception as e:
        raise ValueError(f"CAGR calculation failed: {str(e)}")


def calculate_total_return(start_price: float, end_price: float, dividends: Optional[list] = None) -> float:
    """
    Calculate total return including dividends.
    
    From financial-analysis-function-library.json performance_analysis category
    Simple calculation using numpy - no code duplication
    
    Args:
        start_price: Starting price
        end_price: Ending price
        dividends: Optional list of dividend payments
        
    Returns:
        float: Total return as decimal
    """
    try:
        if start_price <= 0:
            raise ValueError("Start price must be positive")
        
        # Price return
        price_return = (end_price - start_price) / start_price
        
        # Dividend return
        dividend_return = 0.0
        if dividends and len(dividends) > 0:
            total_dividends = np.sum(dividends)
            dividend_return = total_dividends / start_price
        
        # Total return
        total_return = price_return + dividend_return
        
        return float(total_return)
        
    except Exception as e:
        raise ValueError(f"Total return calculation failed: {str(e)}")


def calculate_downside_deviation(returns: Union[pd.Series, Dict[str, Any]], target_return: Optional[float] = None) -> float:
    """
    Calculate downside deviation below target.
    
    From financial-analysis-function-library.json performance_analysis category
    Uses empyrical library instead of manual calculations - no code duplication
    
    Args:
        returns: Return series
        target_return: Target return threshold (default: 0)
        
    Returns:
        float: Downside deviation
    """
    try:
        returns_series = validate_return_data(returns)
        
        if target_return is None:
            target_return = 0.0
        
        # Use empyrical for downside deviation
        downside_dev = empyrical.downside_risk(returns_series, required_return=target_return)
        
        return float(downside_dev)
        
    except Exception as e:
        raise ValueError(f"Downside deviation calculation failed: {str(e)}")


def calculate_upside_capture(returns: Union[pd.Series, Dict[str, Any]], 
                           benchmark_returns: Union[pd.Series, Dict[str, Any]]) -> float:
    """
    Calculate upside capture ratio vs benchmark.
    
    From financial-analysis-function-library.json performance_analysis category
    Uses empyrical library instead of manual calculations - no code duplication
    
    Args:
        returns: Portfolio returns
        benchmark_returns: Benchmark returns
        
    Returns:
        float: Upside capture ratio
    """
    try:
        portfolio_returns = validate_return_data(returns)
        benchmark_series = validate_return_data(benchmark_returns)
        
        # Align series
        from ..utils.data_utils import align_series
        portfolio_aligned, benchmark_aligned = align_series(portfolio_returns, benchmark_series)
        
        # Use empyrical for upside capture
        upside_capture = empyrical.up_capture(portfolio_aligned, benchmark_aligned)
        
        return float(upside_capture)
        
    except Exception as e:
        raise ValueError(f"Upside capture calculation failed: {str(e)}")


def calculate_downside_capture(returns: Union[pd.Series, Dict[str, Any]], 
                             benchmark_returns: Union[pd.Series, Dict[str, Any]]) -> float:
    """
    Calculate downside capture ratio vs benchmark.
    
    From financial-analysis-function-library.json performance_analysis category
    Uses empyrical library instead of manual calculations - no code duplication
    
    Args:
        returns: Portfolio returns
        benchmark_returns: Benchmark returns
        
    Returns:
        float: Downside capture ratio
    """
    try:
        portfolio_returns = validate_return_data(returns)
        benchmark_series = validate_return_data(benchmark_returns)
        
        # Align series
        from ..utils.data_utils import align_series
        portfolio_aligned, benchmark_aligned = align_series(portfolio_returns, benchmark_series)
        
        # Use empyrical for downside capture
        downside_capture = empyrical.down_capture(portfolio_aligned, benchmark_aligned)
        
        return float(downside_capture)
        
    except Exception as e:
        raise ValueError(f"Downside capture calculation failed: {str(e)}")


def calculate_calmar_ratio(returns: Union[pd.Series, Dict[str, Any]]) -> float:
    """
    Calculate Calmar ratio (return/max drawdown).
    
    From financial-analysis-function-library.json performance_analysis category
    Uses empyrical library instead of manual calculations - no code duplication
    
    Args:
        returns: Return series
        
    Returns:
        float: Calmar ratio
    """
    try:
        returns_series = validate_return_data(returns)
        
        # Use empyrical for Calmar ratio
        calmar = empyrical.calmar_ratio(returns_series)
        
        return float(calmar)
        
    except Exception as e:
        raise ValueError(f"Calmar ratio calculation failed: {str(e)}")


def calculate_omega_ratio(returns: Union[pd.Series, Dict[str, Any]], threshold: Optional[float] = None) -> float:
    """
    Calculate Omega ratio.
    
    From financial-analysis-function-library.json performance_analysis category
    Uses empyrical library instead of manual calculations - no code duplication
    
    Args:
        returns: Return series
        threshold: Return threshold (default: 0)
        
    Returns:
        float: Omega ratio
    """
    try:
        returns_series = validate_return_data(returns)
        
        if threshold is None:
            threshold = 0.0
        
        # Use empyrical for Omega ratio
        omega = empyrical.omega_ratio(returns_series, risk_free=threshold)
        
        return float(omega)
        
    except Exception as e:
        raise ValueError(f"Omega ratio calculation failed: {str(e)}")


def calculate_win_rate(returns: Union[pd.Series, Dict[str, Any]]) -> float:
    """
    Calculate percentage of positive returns.
    
    From financial-analysis-function-library.json performance_analysis category
    Simple calculation using pandas - no code duplication
    
    Args:
        returns: Return series
        
    Returns:
        float: Win rate as decimal (0.0 to 1.0)
    """
    try:
        returns_series = validate_return_data(returns)
        
        # Count positive returns
        positive_returns = (returns_series > 0).sum()
        total_returns = len(returns_series)
        
        if total_returns == 0:
            return 0.0
        
        win_rate = positive_returns / total_returns
        
        return float(win_rate)
        
    except Exception as e:
        raise ValueError(f"Win rate calculation failed: {str(e)}")


def calculate_best_worst_periods(returns: Union[pd.Series, Dict[str, Any]], window_size: int) -> Dict[str, Any]:
    """
    Identify best and worst performing periods.
    
    From financial-analysis-function-library.json performance_analysis category
    Uses pandas rolling calculations - no code duplication
    
    Args:
        returns: Return series
        window_size: Rolling window size for periods
        
    Returns:
        Dict: Best and worst period data
    """
    try:
        returns_series = validate_return_data(returns)
        
        if len(returns_series) < window_size:
            raise ValueError(f"Not enough data points for window size {window_size}")
        
        # Calculate rolling returns for specified window
        rolling_returns = returns_series.rolling(window=window_size).apply(
            lambda x: (1 + x).prod() - 1, raw=False
        ).dropna()
        
        if len(rolling_returns) == 0:
            raise ValueError("No valid rolling periods calculated")
        
        # Find best and worst periods
        best_period_idx = rolling_returns.idxmax()
        worst_period_idx = rolling_returns.idxmin()
        
        best_return = rolling_returns.loc[best_period_idx]
        worst_return = rolling_returns.loc[worst_period_idx]
        
        # Calculate period start dates
        best_start = returns_series.index[returns_series.index.get_loc(best_period_idx) - window_size + 1]
        worst_start = returns_series.index[returns_series.index.get_loc(worst_period_idx) - window_size + 1]
        
        result = {
            "window_size": window_size,
            "best_period": {
                "start_date": str(best_start),
                "end_date": str(best_period_idx),
                "return": float(best_return),
                "return_pct": f"{best_return * 100:.2f}%"
            },
            "worst_period": {
                "start_date": str(worst_start),
                "end_date": str(worst_period_idx),
                "return": float(worst_return),
                "return_pct": f"{worst_return * 100:.2f}%"
            },
            "total_periods": len(rolling_returns),
            "average_rolling_return": float(rolling_returns.mean()),
            "rolling_volatility": float(rolling_returns.std())
        }
        
        return standardize_output(result, "calculate_best_worst_periods")
        
    except Exception as e:
        raise ValueError(f"Best/worst periods calculation failed: {str(e)}")


def calculate_dividend_yield(dividends: Union[list, np.ndarray, pd.Series], price: float) -> float:
    """
    Calculate dividend yield.
    
    From financial-analysis-function-library.json specialized_analysis category
    Simple dividend yield calculation using numpy - no code duplication
    
    Args:
        dividends: List or array of dividend payments over period
        price: Current stock price
        
    Returns:
        float: Dividend yield as decimal
    """
    try:
        if price <= 0:
            raise ValueError("Price must be positive")
        
        # Convert dividends to numpy array
        if isinstance(dividends, (list, pd.Series)):
            dividend_array = np.array(dividends)
        else:
            dividend_array = np.array(dividends)
        
        # Remove NaN values and negative dividends
        dividend_clean = dividend_array[~np.isnan(dividend_array)]
        dividend_clean = dividend_clean[dividend_clean >= 0]
        
        # Calculate total annual dividends
        total_dividends = np.sum(dividend_clean)
        
        # Calculate dividend yield
        dividend_yield = total_dividends / price
        
        return float(dividend_yield)
        
    except Exception as e:
        raise ValueError(f"Dividend yield calculation failed: {str(e)}")


def analyze_leverage_fund(prices: Union[pd.Series, Dict[str, Any]], 
                         leverage: float, 
                         underlying_prices: Union[pd.Series, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze leveraged fund characteristics and performance.
    
    From financial-analysis-function-library.json specialized_analysis category
    Uses pandas and numpy for leveraged fund analysis - no code duplication
    
    Args:
        prices: Leveraged fund price series
        leverage: Target leverage ratio (e.g., 2.0 for 2x, 3.0 for 3x)
        underlying_prices: Underlying asset price series
        
    Returns:
        Dict: Leveraged fund analysis data
    """
    try:
        leveraged_prices = validate_price_data(prices)
        underlying_series = validate_price_data(underlying_prices)
        
        # Align series
        from ..utils.data_utils import align_series, prices_to_returns
        leveraged_aligned, underlying_aligned = align_series(leveraged_prices, underlying_series)
        
        # Calculate returns
        leveraged_returns = prices_to_returns(leveraged_aligned)
        underlying_returns = prices_to_returns(underlying_aligned)
        
        # Calculate tracking metrics
        actual_leverage = leveraged_returns.corr(underlying_returns) * (leveraged_returns.std() / underlying_returns.std())
        
        # Calculate daily leverage decay
        expected_returns = underlying_returns * leverage
        tracking_error = (leveraged_returns - expected_returns).std() * np.sqrt(252)
        
        # Calculate compounding drag effect
        underlying_vol = underlying_returns.std() * np.sqrt(252)
        theoretical_drag = 0.5 * (leverage - 1) * (underlying_vol ** 2)
        
        # Performance comparison
        leveraged_total = (1 + leveraged_returns).prod() - 1
        underlying_total = (1 + underlying_returns).prod() - 1
        expected_total = (1 + underlying_returns * leverage).prod() - 1
        
        # Daily rebalancing cost estimation
        daily_vol = underlying_returns.std()
        estimated_daily_cost = (leverage - 1) * (daily_vol ** 2) / 2
        annualized_cost = estimated_daily_cost * 252
        
        result = {
            "target_leverage": float(leverage),
            "actual_leverage": float(actual_leverage),
            "leverage_efficiency": float(actual_leverage / leverage) if leverage != 0 else 0,
            "tracking_error": float(tracking_error),
            "tracking_error_pct": f"{tracking_error * 100:.2f}%",
            "theoretical_drag": float(theoretical_drag),
            "theoretical_drag_pct": f"{theoretical_drag * 100:.2f}%",
            "leveraged_total_return": float(leveraged_total),
            "leveraged_total_return_pct": f"{leveraged_total * 100:.2f}%",
            "underlying_total_return": float(underlying_total),
            "underlying_total_return_pct": f"{underlying_total * 100:.2f}%",
            "expected_leveraged_return": float(expected_total),
            "expected_leveraged_return_pct": f"{expected_total * 100:.2f}%",
            "performance_gap": float(leveraged_total - expected_total),
            "performance_gap_pct": f"{(leveraged_total - expected_total) * 100:.2f}%",
            "estimated_annual_cost": float(annualized_cost),
            "estimated_annual_cost_pct": f"{annualized_cost * 100:.2f}%",
            "underlying_volatility": float(underlying_vol),
            "underlying_volatility_pct": f"{underlying_vol * 100:.2f}%",
            "leveraged_volatility": float(leveraged_returns.std() * np.sqrt(252)),
            "leveraged_volatility_pct": f"{leveraged_returns.std() * np.sqrt(252) * 100:.2f}%"
        }
        
        return standardize_output(result, "analyze_leverage_fund")
        
    except Exception as e:
        return {"success": False, "error": f"Leveraged fund analysis failed: {str(e)}"}


# Registry using library-based functions - no manual calculations
PERFORMANCE_METRICS_FUNCTIONS = {
    'calculate_returns_metrics': calculate_returns_metrics,
    'calculate_risk_metrics': calculate_risk_metrics,
    'calculate_benchmark_metrics': calculate_benchmark_metrics,
    'calculate_drawdown_analysis': calculate_drawdown_analysis,
    'calculate_annualized_return': calculate_annualized_return,
    'calculate_annualized_volatility': calculate_annualized_volatility,
    'calculate_cagr': calculate_cagr,
    'calculate_total_return': calculate_total_return,
    'calculate_downside_deviation': calculate_downside_deviation,
    'calculate_upside_capture': calculate_upside_capture,
    'calculate_downside_capture': calculate_downside_capture,
    'calculate_calmar_ratio': calculate_calmar_ratio,
    'calculate_omega_ratio': calculate_omega_ratio,
    'calculate_win_rate': calculate_win_rate,
    'calculate_best_worst_periods': calculate_best_worst_periods,
    'calculate_dividend_yield': calculate_dividend_yield,
    'analyze_leverage_fund': analyze_leverage_fund
}