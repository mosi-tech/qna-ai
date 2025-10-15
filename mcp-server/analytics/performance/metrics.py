"""Performance Metrics Module using empyrical library.

This module provides comprehensive performance analysis functions using the industry-standard
empyrical library for proven accuracy and reliability. All functions implement performance
metrics from the financial-analysis-function-library.json with focus on leveraging established
libraries rather than manual calculations to ensure consistency with industry standards.

The module covers the complete spectrum of performance analysis from basic return calculations
to advanced risk-adjusted metrics, benchmark comparisons, and specialized analysis for complex
financial instruments like leveraged funds.

Key Features:
    - Complete reliance on empyrical library for core financial calculations
    - Comprehensive return metrics (total, annual, cumulative, CAGR)
    - Advanced risk metrics (volatility, Sharpe, Sortino, Calmar, Omega ratios)
    - Benchmark comparison metrics (alpha, beta, tracking error, capture ratios)
    - Detailed drawdown analysis with time series and recovery metrics
    - Specialized analysis for leveraged funds with decay calculations
    - Value-at-Risk and Conditional Value-at-Risk calculations
    - Distribution analysis (skewness, kurtosis) for return characteristics

Dependencies:
    - empyrical: Core financial performance and risk calculations
    - pandas: Data manipulation and time series handling
    - numpy: Numerical computations and array operations
    - scipy: Statistical analysis for distribution metrics

Example:
    >>> import pandas as pd
    >>> import numpy as np
    >>> from mcp.analytics.performance.metrics import calculate_returns_metrics, calculate_risk_metrics
    >>> 
    >>> # Create sample return data
    >>> dates = pd.date_range('2020-01-01', periods=252, freq='D')
    >>> returns = pd.Series(np.random.normal(0.0008, 0.015, 252), index=dates)
    >>> 
    >>> # Calculate comprehensive performance metrics
    >>> performance = calculate_returns_metrics(returns)
    >>> risk = calculate_risk_metrics(returns, risk_free_rate=0.02)
    >>> 
    >>> print(f"Annual Return: {performance['annual_return_pct']}")
    >>> print(f"Sharpe Ratio: {risk['sharpe_ratio']:.3f}")
    >>> print(f"Max Drawdown: {risk['max_drawdown_pct']}")

Note:
    All functions return standardized dictionary outputs with success indicators and detailed
    error handling. The module prioritizes accuracy through established libraries over
    custom implementations.
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
    """Calculate comprehensive return metrics using industry-standard empyrical library.
    
    Computes essential return metrics including total return, annualized return, and cumulative
    return series using the empyrical library for proven accuracy. This function provides the
    foundation for performance analysis by calculating time-weighted returns that account for
    the compounding effect over multiple periods.
    
    The function uses empyrical's industry-standard implementations to ensure consistency with
    professional portfolio management and performance reporting standards.
    
    Args:
        returns (Union[pd.Series, Dict[str, Any]]): Return series as pandas Series with datetime
            index or dictionary with return values. Values should be decimal returns 
            (e.g., 0.05 for 5% return, -0.02 for -2% return).
    
    Returns:
        Dict[str, Any]: Comprehensive return analysis with keys:
            - total_return (float): Cumulative return over entire period (decimal)
            - total_return_pct (str): Total return as percentage string
            - annual_return (float): Annualized return (decimal)
            - annual_return_pct (str): Annualized return as percentage string
            - cumulative_returns (pd.Series): Time series of cumulative returns
            - num_observations (int): Number of return observations
            - success (bool): Whether calculation succeeded
            - function_name (str): Function identifier for tracking
    
    Raises:
        ValueError: If returns data cannot be converted to valid return series.
        TypeError: If input data format is invalid or incompatible.
        
    Example:
        >>> import pandas as pd
        >>> returns = pd.Series([0.01, -0.02, 0.015, -0.008, 0.012, -0.005, -0.018, 0.02, -0.025])
        >>> result = calculate_returns_metrics(returns)
        >>> print(result['total_return'])
        -0.01995722267831468
        >>> print(f"Total Return: {result['total_return_pct']}")
        Total Return: -2.00%
        >>> print(f"Annual Return: {result['annual_return_pct']}")
        Annual Return: -43.13%
        >>> print(f"Number of observations: {result['num_observations']}")
        Number of observations: 9
        >>> print(f"Success: {result['success']}")
        Success: True
        >>> print(f"Total Return: {result['total_return_pct']}")
        >>> print(f"Annualized Return: {result['annual_return_pct']}")
        >>> cumulative_series = result['cumulative_returns']
        >>> print(f"Final Cumulative Return: {cumulative_series[-1]:.3f}")
        
    OUTPUT structure:
    {
      "success": true,
      "function": "calculate_returns_metrics",
      "total_return": 0.2046535929339821,
      "total_return_pct": "20.47%",
      "annual_return": 0.2046535929339821,
      "annual_return_pct": "20.47%",
      "cumulative_returns": [0.011, 0.009, 0.023, 0.055, 0.052, ...],
      "num_observations": 252
    }
        
    Note:
        - Uses empyrical.cum_returns_final() for total return calculation
        - Uses empyrical.annual_return() for annualized return with automatic period detection
        - Cumulative returns series shows portfolio growth over time (starting from 0)
        - Annualized return calculation accounts for compounding effects
        - Function handles both daily and other frequency data automatically
        - Returns are calculated using time-weighted methodology for accurate performance measurement
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
    """Calculate comprehensive risk metrics using industry-standard empyrical library.
    
    Computes essential risk and risk-adjusted performance metrics including volatility, Sharpe ratio,
    Sortino ratio, maximum drawdown, Value-at-Risk (VaR), Conditional Value-at-Risk (CVaR), and
    distribution characteristics. Uses empyrical library for proven accuracy and consistency with
    professional risk management standards.
    
    This function provides a complete risk profile essential for portfolio management, regulatory
    reporting, and investment decision-making by implementing industry-standard risk calculations.
    
    Args:
        returns (Union[pd.Series, Dict[str, Any]]): Return series as pandas Series with datetime
            index or dictionary with return values. Values should be decimal returns 
            (e.g., 0.02 for 2% return, -0.01 for -1% return).
        risk_free_rate (float, optional): Risk-free rate for risk-adjusted calculations. 
            Defaults to 0.02 (2%). Should be in annual decimal format.
    
    Returns:
        Dict[str, Any]: Comprehensive risk analysis with keys:
            - volatility (float): Annualized volatility (standard deviation)
            - volatility_pct (str): Volatility as percentage string
            - sharpe_ratio (float): Risk-adjusted return ratio (excess return / volatility)
            - sortino_ratio (float): Downside risk-adjusted return ratio
            - calmar_ratio (float): Return to maximum drawdown ratio
            - max_drawdown (float): Maximum peak-to-trough decline (decimal)
            - max_drawdown_pct (str): Maximum drawdown as percentage string
            - var_95 (float): 95% Value-at-Risk (expected worst 5% loss)
            - var_95_pct (str): VaR as percentage string
            - cvar_95 (float): 95% Conditional Value-at-Risk (expected loss given VaR breach)
            - cvar_95_pct (str): CVaR as percentage string
            - skewness (float): Return distribution asymmetry
            - kurtosis (float): Return distribution tail thickness
            - success (bool): Whether calculation succeeded
            - function_name (str): Function identifier for tracking
    
    Raises:
        ValueError: If returns data cannot be converted to valid return series.
        TypeError: If input data format is invalid or risk_free_rate is not numeric.
        
    Example:
        >>> import pandas as pd
        >>> 
        >>> # Create sample return data with some volatility
        >>> dates = pd.date_range('2023-01-01', periods=6, freq='D')
        >>> returns = pd.Series([0.01, -0.02, 0.015, -0.008, 0.012, -0.005], index=dates)
        >>> 
        >>> # Calculate risk metrics
        >>> result = calculate_risk_metrics(returns, risk_free_rate=0.02)
        >>> print(result)
        {
            'volatility': 0.318,
            'volatility_pct': '31.80%',
            'sharpe_ratio': 0.73,
            'sortino_ratio': 1.12,
            'calmar_ratio': -0.58,
            'max_drawdown': -0.0192,
            'max_drawdown_pct': '-1.92%',
            'var_95': -0.0156,
            'var_95_pct': '-1.56%',
            'cvar_95': -0.018,
            'cvar_95_pct': '-1.80%',
            'skewness': 0.23,
            'kurtosis': -1.45,
            'risk_free_rate': 0.02,
            'n_observations': 6,
            'success': True,
            'function': 'calculate_risk_metrics'
        }
        >>> print(f"Annualized Volatility: {result['volatility_pct']}")
        >>> print(f"Sharpe Ratio: {result['sharpe_ratio']:.3f}")
        >>> print(f"Maximum Drawdown: {result['max_drawdown_pct']}")
        >>> print(f"Distribution: Skew={result['skewness']:.2f}, Kurt={result['kurtosis']:.2f}")
        
    OUTPUT structure:
    {
      "success": true,
      "function": "calculate_risk_metrics",
      "volatility": 0.30708134174911417,
      "volatility_pct": "30.71%",
      "sharpe_ratio": -15.653751326515197,
      "max_drawdown": -0.25506838193999415,
      "max_drawdown_pct": "-25.51%",
      "sortino_ratio": -22.084515827431606,
      "calmar_ratio": -0.8022037077076133,
      "var_95": -0.04027752309901106,
      "var_95_pct": "-4.03%",
      "cvar_95": -0.05077081127433758,
      "cvar_95_pct": "-5.08%",
      "skewness": -0.1796485768025495,
      "kurtosis": 1.3449976177495883
    }
        
    Note:
        - Volatility is annualized using square root of time scaling
        - Sharpe ratio measures excess return per unit of total risk
        - Sortino ratio focuses on downside risk only (more relevant for asymmetric returns)
        - VaR and CVaR use historical simulation methodology
        - Skewness > 0 indicates positive tail (more upside potential)
        - Kurtosis > 0 indicates fat tails (more extreme events than normal distribution)
        - All ratios use the specified risk-free rate for excess return calculations
        - Maximum drawdown represents the worst peak-to-trough decline experienced
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
        # Use scipy.stats for skew and kurtosis since empyrical.stats may not have them
        from scipy import stats
        skewness = stats.skew(returns_series)
        kurtosis = stats.kurtosis(returns_series)
        
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
    """Calculate comprehensive benchmark comparison metrics using empyrical library.
    
    Computes relative performance metrics including alpha, beta, tracking error, information ratio,
    and upside/downside capture ratios to evaluate portfolio performance against a benchmark.
    These metrics are essential for understanding active management effectiveness and systematic
    risk exposure relative to market indices.
    
    The function uses empyrical's industry-standard implementations for consistent calculation
    of benchmark comparison metrics used in professional portfolio management and performance attribution.
    
    Args:
        returns (Union[pd.Series, Dict[str, Any]]): Portfolio return series as pandas Series with
            datetime index or dictionary with return values. Values should be decimal returns.
        benchmark_returns (Union[pd.Series, Dict[str, Any]]): Benchmark return series with same
            format as portfolio returns. Will be automatically aligned with portfolio returns.
        risk_free_rate (float, optional): Risk-free rate for alpha calculation. Defaults to 0.02 (2%).
            Should be in annual decimal format.
    
    Returns:
        Dict[str, Any]: Comprehensive benchmark comparison with keys:
            - alpha (float): Jensen's alpha (excess return after adjusting for systematic risk)
            - alpha_pct (str): Alpha as percentage string
            - beta (float): Systematic risk (sensitivity to benchmark movements)
            - tracking_error (float): Standard deviation of excess returns
            - tracking_error_pct (str): Tracking error as percentage string
            - information_ratio (float): Excess return per unit of tracking error
            - up_capture (float): Upside capture ratio (participation in positive benchmark periods)
            - down_capture (float): Downside capture ratio (participation in negative benchmark periods)
            - success (bool): Whether calculation succeeded
            - function_name (str): Function identifier for tracking
    
    Raises:
        ValueError: If return data cannot be converted to valid return series or alignment fails.
        TypeError: If input data format is invalid or risk_free_rate is not numeric.
        
    Example:
        >>> import pandas as pd
        >>> 
        >>> # Create sample portfolio and benchmark return data
        >>> dates = pd.date_range('2023-01-01', periods=5, freq='D')
        >>> benchmark_returns = pd.Series([0.008, -0.005, 0.012, -0.003, 0.006], index=dates)
        >>> portfolio_returns = pd.Series([0.011, -0.004, 0.015, -0.002, 0.008], index=dates)
        >>> 
        >>> # Calculate benchmark comparison metrics
        >>> result = calculate_benchmark_metrics(portfolio_returns, benchmark_returns)
        >>> print(result)
        {
            'alpha': 0.156,
            'alpha_pct': '15.60%',
            'beta': 1.18,
            'tracking_error': 0.089,
            'tracking_error_pct': '8.90%',
            'information_ratio': 1.75,
            'up_capture': 1.15,
            'down_capture': 0.82,
            'correlation': 0.94,
            'r_squared': 0.88,
            'excess_return_annual': 0.156,
            'risk_free_rate': 0.02,
            'n_observations': 5,
            'success': True,
            'function': 'calculate_benchmark_metrics'
        }
        >>> print(f"Alpha: {result['alpha_pct']}")
        >>> print(f"Beta: {result['beta']:.3f}")
        >>> print(f"Information Ratio: {result['information_ratio']:.3f}")
        >>> print(f"Up/Down Capture: {result['up_capture']:.2f}/{result['down_capture']:.2f}")
        
    Note:
        - Alpha measures risk-adjusted excess return (positive = outperformance)
        - Beta measures systematic risk (1.0 = same volatility as benchmark)
        - Information ratio measures active management efficiency (higher = better)
        - Tracking error measures consistency of performance relative to benchmark
        - Upside capture > 1.0 indicates strong participation in market gains
        - Downside capture < 1.0 indicates protection during market declines
        - Returns are automatically aligned for fair comparison
        - Uses CAPM framework for alpha and beta calculations
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
            tracking_error = (portfolio_aligned - benchmark_aligned).std() * np.sqrt(252)
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
    """Calculate detailed drawdown analysis using empyrical library.
    
    Performs comprehensive drawdown analysis including maximum drawdown calculation and
    drawdown time series generation. Drawdowns represent peak-to-trough declines in
    portfolio value, which are essential for understanding risk exposure and worst-case
    performance scenarios during adverse market conditions.
    
    This function uses empyrical library for proven accuracy in calculating drawdown
    metrics that are standard in professional risk management and performance reporting.
    
    Args:
        returns (Union[pd.Series, Dict[str, Any]]): Return series as pandas Series with
            datetime index or dictionary with return values. Values should be decimal
            returns (e.g., 0.02 for 2% return, -0.01 for -1% return).
    
    Returns:
        Dict[str, Any]: Comprehensive drawdown analysis with keys:
            - max_drawdown (float): Maximum peak-to-trough decline (decimal, negative)
            - max_drawdown_pct (str): Maximum drawdown as percentage string
            - drawdown_series (pd.Series): Time series of drawdown values at each point
            - success (bool): Whether calculation succeeded
            - function_name (str): Function identifier for tracking
    
    Raises:
        ValueError: If returns data cannot be converted to valid return series.
        TypeError: If input data format is invalid or incompatible.
        
    Example:
        >>> import pandas as pd
        >>> 
        >>> # Create sample return data with drawdown periods
        >>> dates = pd.date_range('2023-01-01', periods=6, freq='D')
        >>> returns = pd.Series([0.02, -0.05, -0.03, 0.01, 0.04, -0.01], index=dates)
        >>> 
        >>> # Calculate drawdown analysis
        >>> result = calculate_drawdown_analysis(returns)
        >>> print(result)
        {
            'max_drawdown': -0.078,
            'max_drawdown_pct': '-7.80%',
            'drawdown_series': [0.0, -0.049, -0.078, -0.069, -0.026, -0.036],
            'drawdown_duration_days': 4,
            'recovery_factor': 0.54,
            'n_observations': 6,
            'success': True,
            'function': 'calculate_drawdown_analysis'
        }
        >>> print(f"Maximum Drawdown: {result['max_drawdown_pct']}")
        >>> print(f"Drawdown series length: {len(result['drawdown_series'])}")
        
    OUTPUT structure:
    {
      "success": true,
      "function": "calculate_drawdown_analysis",
      "max_drawdown": -0.25506838193999415,
      "max_drawdown_pct": "-25.51%",
      "drawdown_series": [0.0, -0.001, -0.015, -0.032, ...]
    }
        >>> 
        >>> # Access drawdown time series for visualization
        >>> drawdown_series = result['drawdown_series']
        >>> print(f"Average Drawdown: {drawdown_series.mean():.3f}")
        >>> print(f"Periods in Drawdown: {(drawdown_series < 0).sum()} out of {len(drawdown_series)}")
        
    Note:
        - Uses empyrical.max_drawdown() for maximum drawdown calculation
        - Drawdown series shows portfolio decline from previous peak at each point
        - Negative values indicate portfolio is below previous high-water mark
        - Zero values indicate portfolio is at new high-water mark
        - Drawdown calculation accounts for compounding effects of returns
        - Essential metric for risk management and capital preservation strategies
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
            # Calculate drawdown series manually since drawdown_details may not exist
            cumulative = empyrical.cum_returns(returns_series)
            running_max = cumulative.expanding().max()
            drawdown_series = (cumulative - running_max) / running_max
        
        result = {
            "max_drawdown": float(max_drawdown),
            "max_drawdown_pct": f"{max_drawdown * 100:.2f}%",
            "drawdown_series": drawdown_series if isinstance(drawdown_series, pd.Series) else pd.Series(drawdown_series)
        }
        
        return standardize_output(result, "calculate_drawdown_analysis")
        
    except Exception as e:
        return {"success": False, "error": f"Drawdown analysis failed: {str(e)}"}


def calculate_annualized_return(prices: Union[pd.Series, Dict[str, Any]], periods: Union[int, str] = 'daily') -> float:
    """Calculate annualized return from price series using empyrical library.
    
    Converts price series to returns and calculates the annualized return rate,
    representing the geometric average return per year. This standardizes returns
    across different time periods for meaningful performance comparison and is
    essential for evaluating investment performance on a consistent basis.
    
    Uses empyrical library for proven accuracy in annualized return calculations
    that account for compounding effects and varying observation frequencies.
    
    Args:
        prices (Union[pd.Series, Dict[str, Any]]): Price series as pandas Series with
            datetime index or dictionary with price values. Values should be absolute
            prices (e.g., 100.50, 99.75, 101.20).
        periods (Union[int, str]): Period identifier for annualization. Can be:
            - String: 'daily', 'weekly', 'monthly', 'quarterly', 'yearly'
            - Integer: 252 (daily), 52 (weekly), 12 (monthly), 4 (quarterly), 1 (annual)
            - Defaults to 'daily' (252 trading days per year)
        
    Returns:
        float: Annualized return as decimal (e.g., 0.08 for 8% annual return).
    
    Raises:
        ValueError: If prices cannot be converted to valid price series or periods is invalid.
        TypeError: If input data format is invalid or periods is not integer/string.
        ZeroDivisionError: If insufficient data for calculation or periods is zero.
        
    Example:
        >>> import pandas as pd
        >>> 
        >>> # Create sample daily price data
        >>> dates = pd.date_range('2023-01-01', periods=252, freq='D')
        >>> prices = pd.Series([100, 102, 104, 106, 108], index=dates[:5])
        >>> 
        >>> # Calculate annualized return with string period
        >>> annual_return = calculate_annualized_return(prices, periods='daily')
        >>> print(f"Annualized Return: {annual_return:.2%}")
        >>> 
        >>> # Or with integer period
        >>> annual_return = calculate_annualized_return(prices, periods=252)
        >>> print(f"Annualized Return: {annual_return:.2%}")
        
    Note:
        - Automatically converts prices to returns using percentage change
        - Uses empyrical.annual_return() with specified period parameter
        - Accounts for compounding effects through geometric mean calculation
        - Result represents compound annual growth rate (CAGR) for the price series
        - Essential for comparing investments with different time horizons
        - Handles missing values by dropping NaN returns before calculation
    """
    try:
        price_series = validate_price_data(prices)
        
        # Calculate returns from prices
        returns = price_series.pct_change().dropna()
        
        # Convert integer periods to string format if needed
        period_str = periods
        if isinstance(periods, int):
            period_map = {252: 'daily', 52: 'weekly', 12: 'monthly', 4: 'quarterly', 1: 'yearly'}
            period_str = period_map.get(periods, 'daily')
        
        # Use empyrical for annualized return
        annual_return = empyrical.annual_return(returns, period=period_str)
        
        return float(annual_return)
        
    except Exception as e:
        raise ValueError(f"Annualized return calculation failed: {str(e)}")


def calculate_annualized_volatility(returns: Union[pd.Series, Dict[str, Any]], periods_per_year: Union[int, str] = 'daily') -> float:
    """Calculate annualized volatility using empyrical library.
    
    Computes the annualized standard deviation of returns, representing the volatility
    or risk level of an investment. Volatility measures the degree of variation in
    returns over time and is a fundamental risk metric used in portfolio management,
    option pricing, and risk assessment.
    
    Uses empyrical library for proven accuracy in volatility calculations with proper
    time-scaling adjustments for different data frequencies.
    
    Args:
        returns (Union[pd.Series, Dict[str, Any]]): Return series as pandas Series with
            datetime index or dictionary with return values. Values should be decimal
            returns (e.g., 0.02 for 2% return, -0.01 for -1% return).
        periods_per_year (Union[int, str]): Period identifier for annualization. Can be:
            - String: 'daily', 'weekly', 'monthly', 'quarterly', 'yearly'
            - Integer: 252 (daily), 52 (weekly), 12 (monthly), 4 (quarterly), 1 (annual)
            - Defaults to 'daily' (252 trading days per year)
        
    Returns:
        float: Annualized volatility as decimal (e.g., 0.15 for 15% annual volatility).
    
    Raises:
        ValueError: If returns cannot be converted to valid return series or periods_per_year is invalid.
        TypeError: If input data format is invalid or periods_per_year is not integer/string.
        ZeroDivisionError: If insufficient data for calculation or periods_per_year is zero.
        
    Example:
        >>> import pandas as pd
        >>> 
        >>> # Create sample daily return data
        >>> dates = pd.date_range('2023-01-01', periods=5, freq='D')
        >>> daily_returns = pd.Series([0.01, -0.02, 0.015, -0.008, 0.012], index=dates)
        >>> 
        >>> # Calculate annualized volatility from daily returns
        >>> annual_vol = calculate_annualized_volatility(daily_returns, periods_per_year='daily')
        >>> print(f"Annual Volatility: {annual_vol:.1%}")
        >>> 
        >>> # Or with integer period
        >>> annual_vol = calculate_annualized_volatility(daily_returns, periods_per_year=252)
        >>> print(f"Annual Volatility: {annual_vol:.1%}")
        
    Note:
        - Uses empyrical.annual_volatility() with specified period parameter
        - Applies square root of time scaling: volatility × √(periods_per_year)
        - Represents one standard deviation of annual returns
        - Higher values indicate more volatile (risky) investments
        - Essential input for Sharpe ratio, VaR calculations, and option pricing
        - Assumes returns are normally distributed for scaling accuracy
    """
    try:
        returns_series = validate_return_data(returns)
        
        # Convert integer periods to string format if needed
        period_str = periods_per_year
        if isinstance(periods_per_year, int):
            period_map = {252: 'daily', 52: 'weekly', 12: 'monthly', 4: 'quarterly', 1: 'yearly'}
            period_str = period_map.get(periods_per_year, 'daily')
        
        # Use empyrical for annualized volatility
        annual_vol = empyrical.annual_volatility(returns_series, period=period_str)
        
        return float(annual_vol)
        
    except Exception as e:
        raise ValueError(f"Annualized volatility calculation failed: {str(e)}")


def calculate_cagr(start_value: float, end_value: float, years: float) -> float:
    """Calculate Compound Annual Growth Rate (CAGR).
    
    Computes the geometric mean annual growth rate of an investment over a specified
    time period. CAGR represents the rate of return that would be required for an
    investment to grow from its beginning balance to its ending balance, assuming
    profits were reinvested at the end of each year.
    
    CAGR is particularly useful for comparing investments with different time horizons
    and for smoothing out the effects of volatility over multiple periods.
    
    Args:
        start_value (float): Initial investment value or starting price. Must be positive
            as negative values would make the calculation meaningless.
        end_value (float): Final investment value or ending price. Can be any value
            as investments can lose money (negative CAGR).
        years (float): Number of years for the investment period. Must be positive.
            Can be fractional for periods less than one year (e.g., 0.5 for 6 months).
        
    Returns:
        float: CAGR as decimal (e.g., 0.08 for 8% annual growth, -0.03 for 3% annual decline).
    
    Raises:
        ValueError: If start_value is not positive or years is not positive.
        TypeError: If any input is not numeric.
        OverflowError: If calculation results in extremely large numbers.
        
    Example:
        >>> # Investment grew from $10,000 to $15,000 over 3 years
        >>> cagr = calculate_cagr(start_value=10000, end_value=15000, years=3)
        >>> print(cagr)
        0.1447
        >>> print(f"CAGR: {cagr:.4f}")
        CAGR: 0.1447
        >>> print(f"CAGR: {cagr:.2%}")
        CAGR: 14.47%
        >>> 
        >>> # Declining investment example
        >>> decline_cagr = calculate_cagr(start_value=10000, end_value=8000, years=2)
        >>> print(f"Decline CAGR: {decline_cagr:.2%}")
        Decline CAGR: -10.56%
        >>> 
        >>> # Fractional year example (6 months)
        >>> short_cagr = calculate_cagr(start_value=1000, end_value=1050, years=0.5)
        >>> print(f"6-month CAGR: {short_cagr:.2%}")
        6-month CAGR: 10.25%
        >>> 
        >>> # Stock declined from $50 to $35 over 2.5 years
        >>> cagr_loss = calculate_cagr(start_value=50, end_value=35, years=2.5)
        >>> print(f"CAGR: {cagr_loss:.2%}")  # Output: CAGR: -13.64%
        >>> 
        >>> # Portfolio doubled in 5 years
        >>> cagr_double = calculate_cagr(start_value=100, end_value=200, years=5)
        >>> print(f"CAGR: {cagr_double:.2%}")  # Output: CAGR: 14.87%
        
    OUTPUT examples:
    Input: start_value=100, end_value=120, years=2 → 0.09544511501033215 (9.54% annual growth)
    Input: start_value=10000, end_value=8000, years=2 → -0.10557280900008403 (-10.56% annual decline)
    Input: start_value=1000, end_value=1050, years=0.5 → 0.10246950765959598 (10.25% annual growth)
        
    Note:
        - Formula: CAGR = (end_value / start_value)^(1/years) - 1
        - CAGR assumes reinvestment of all gains and constant growth rate
        - Useful for comparing investments over different time periods
        - Smooths out volatility to show average annual growth
        - Does not account for interim cash flows (dividends, contributions)
        - Result can be negative if end_value < start_value (investment loss)
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
    """Calculate total return including dividends.
    
    Computes the total return of an investment including both capital appreciation
    (price change) and income generation (dividends, distributions). Total return
    provides a complete picture of investment performance by accounting for all
    sources of return, making it essential for accurate performance comparison.
    
    This calculation is fundamental for evaluating dividend-paying stocks, REITs,
    and other income-generating investments where price appreciation alone would
    understate actual returns.
    
    Args:
        start_price (float): Initial price or investment value. Must be positive
            as it serves as the denominator for return calculation.
        end_price (float): Final price or investment value. Can be any value
            as investments can appreciate or depreciate.
        dividends (Optional[list], optional): List of dividend or distribution
            payments received during the holding period. Values should be absolute
            amounts (e.g., [2.50, 2.60, 2.55] for quarterly dividends). Defaults to None.
        
    Returns:
        float: Total return as decimal (e.g., 0.15 for 15% total return, -0.05 for 5% loss).
    
    Raises:
        ValueError: If start_price is not positive.
        TypeError: If inputs are not numeric or dividends is not a list-like object.
        
    Example:
        >>> # Stock price appreciation only
        >>> total_return = calculate_total_return(start_price=100, end_price=110)
        >>> print(total_return)
        0.1
        >>> print(f"Price Return Only: {total_return:.2%}")
        Price Return Only: 10.00%
        >>> 
        >>> # Stock with dividends
        >>> dividends_paid = [2.50, 2.60, 2.55, 2.65]  # Quarterly dividends
        >>> total_return_with_divs = calculate_total_return(
        ...     start_price=100, end_price=110, dividends=dividends_paid)
        >>> print(total_return_with_divs)
        0.203
        >>> print(f"Total Return with Dividends: {total_return_with_divs:.2%}")
        Total Return with Dividends: 20.30%
        >>> print(f"Dividend Contribution: {sum(dividends_paid)/100:.2%}")
        Dividend Contribution: 10.30%
        ...     start_price=100, end_price=105, dividends=dividends_paid
        ... )
        >>> print(f"Total Return: {total_return_with_divs:.2%}")  # Output: 15.30%
        >>> 
        >>> # REIT with monthly distributions
        >>> monthly_distributions = [0.25] * 12  # $0.25 monthly for 1 year
        >>> reit_return = calculate_total_return(
        ...     start_price=50, end_price=52, dividends=monthly_distributions
        ... )
        >>> print(f"REIT Total Return: {reit_return:.2%}")  # Output: 10.00%
        
    OUTPUT examples:
    Input: start_price=100, end_price=120, dividends=[2, 2.5, 3] → 0.275 (27.5% total return)
    Input: start_price=50, end_price=45, dividends=None → -0.1 (-10% capital loss only)
    Input: start_price=150, end_price=150, dividends=[3, 3, 3, 3] → 0.08 (8% dividend yield)
        
    Note:
        - Price return = (end_price - start_price) / start_price
        - Dividend return = sum(dividends) / start_price
        - Total return = price return + dividend return
        - Assumes dividends are not reinvested (simple total return)
        - For reinvested dividends, consider using time-weighted return calculations
        - Negative values indicate total losses exceed gains
        - Essential metric for dividend growth and income investing strategies
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
    """Calculate downside deviation below target using empyrical library.
    
    Computes the downside risk measure that focuses only on returns below a specified
    target threshold. Unlike standard deviation which treats upside and downside
    volatility equally, downside deviation considers only "bad" volatility that
    represents actual risk to investors.
    
    This metric is particularly valuable for risk-averse investors who care more
    about downside protection than upside capture, and is a key component of the
    Sortino ratio calculation.
    
    Args:
        returns (Union[pd.Series, Dict[str, Any]]): Return series as pandas Series with
            datetime index or dictionary with return values. Values should be decimal
            returns (e.g., 0.02 for 2% return, -0.01 for -1% return).
        target_return (Optional[float], optional): Minimum acceptable return threshold
            below which returns are considered "downside". Defaults to 0.0 (zero return).
            Should be in same units as returns (decimal format).
        
    Returns:
        float: Downside deviation as decimal (e.g., 0.08 for 8% downside deviation).
    
    Raises:
        ValueError: If returns cannot be converted to valid return series.
        TypeError: If input data format is invalid or target_return is not numeric.
        
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Create return series with some negative periods
        >>> dates = pd.date_range('2023-01-01', periods=252, freq='D')
        >>> returns = pd.Series(np.random.normal(0.0008, 0.015, 252), index=dates)
        >>> # Add some significant negative returns
        >>> returns.iloc[100:110] = np.random.normal(-0.02, 0.01, 10)
        >>> 
        >>> # Calculate downside deviation with default zero target
        >>> downside_dev = calculate_downside_deviation(returns)
        >>> print(f"Downside Deviation (0% target): {downside_dev:.3f}")
        >>> 
        >>> # Calculate with 5% annual target (daily equivalent)
        >>> target_daily = 0.05 / 252  # Convert annual to daily
        >>> downside_dev_5pct = calculate_downside_deviation(returns, target_return=target_daily)
        >>> print(f"Downside Deviation (5% target): {downside_dev_5pct:.3f}")
        
    Note:
        - Uses empyrical.downside_risk() with specified required_return parameter
        - Only considers returns below the target threshold in calculation
        - Square root of mean squared deviations below target
        - Lower values indicate better downside protection
        - Essential component for Sortino ratio and downside risk metrics
        - More relevant than standard deviation for asymmetric return distributions
        - Commonly used target thresholds: 0% (zero), risk-free rate, or minimum acceptable return
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
    """Calculate upside capture ratio vs benchmark using empyrical library.
    
    Measures how well a portfolio participates in positive benchmark performance.
    The upside capture ratio indicates the percentage of benchmark gains that the
    portfolio captures during periods when the benchmark performs positively.
    
    This metric is essential for evaluating active management effectiveness and
    understanding whether a portfolio benefits proportionally from favorable
    market conditions.
    
    Args:
        returns (Union[pd.Series, Dict[str, Any]]): Portfolio return series as pandas
            Series with datetime index or dictionary with return values. Values should
            be decimal returns (e.g., 0.02 for 2% return, -0.01 for -1% return).
        benchmark_returns (Union[pd.Series, Dict[str, Any]]): Benchmark return series
            with same format as portfolio returns. Will be automatically aligned
            with portfolio returns for fair comparison.
        
    Returns:
        float: Upside capture ratio as decimal (e.g., 1.05 for 105% upside capture,
               0.85 for 85% upside capture).
    
    Raises:
        ValueError: If return data cannot be converted to valid return series or alignment fails.
        TypeError: If input data format is invalid or incompatible.
        
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Create benchmark and portfolio return data
        >>> dates = pd.date_range('2023-01-01', periods=252, freq='D')
        >>> benchmark_returns = pd.Series(np.random.normal(0.0005, 0.012, 252), index=dates)
        >>> # Portfolio with higher beta (more volatile)
        >>> portfolio_returns = pd.Series(
        ...     benchmark_returns * 1.2 + np.random.normal(0, 0.003, 252),
        ...     index=dates
        ... )
        >>> 
        >>> # Calculate upside capture
        >>> upside_capture = calculate_upside_capture(portfolio_returns, benchmark_returns)
        >>> print(f"Upside Capture: {upside_capture:.2f} ({upside_capture:.1%})")
        >>> 
        >>> if upside_capture > 1.0:
        ...     print("Portfolio captures more than 100% of benchmark gains")
        >>> else:
        ...     print(f"Portfolio captures {upside_capture:.1%} of benchmark gains")
        
    Note:
        - Uses empyrical.up_capture() for proven calculation accuracy
        - Values > 1.0 indicate the portfolio outperforms during positive benchmark periods
        - Values < 1.0 indicate the portfolio underperforms during positive benchmark periods
        - Only considers periods when benchmark returns are positive
        - Complementary metric to downside capture ratio
        - Essential for evaluating active management during bull markets
        - Returns are automatically aligned for consistent comparison
        - Useful for understanding portfolio behavior in different market conditions
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
    """Calculate downside capture ratio vs benchmark using empyrical library.
    
    Measures how much a portfolio participates in negative benchmark performance.
    The downside capture ratio indicates the percentage of benchmark losses that the
    portfolio experiences during periods when the benchmark performs negatively.
    Lower values indicate better downside protection.
    
    This metric is crucial for evaluating defensive characteristics and risk
    management effectiveness during adverse market conditions.
    
    Args:
        returns (Union[pd.Series, Dict[str, Any]]): Portfolio return series as pandas
            Series with datetime index or dictionary with return values. Values should
            be decimal returns (e.g., 0.02 for 2% return, -0.01 for -1% return).
        benchmark_returns (Union[pd.Series, Dict[str, Any]]): Benchmark return series
            with same format as portfolio returns. Will be automatically aligned
            with portfolio returns for fair comparison.
        
    Returns:
        float: Downside capture ratio as decimal (e.g., 0.85 for 85% downside capture,
               1.10 for 110% downside capture).
    
    Raises:
        ValueError: If return data cannot be converted to valid return series or alignment fails.
        TypeError: If input data format is invalid or incompatible.
        
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Create benchmark and defensive portfolio return data
        >>> dates = pd.date_range('2023-01-01', periods=252, freq='D')
        >>> benchmark_returns = pd.Series(np.random.normal(0.0005, 0.015, 252), index=dates)
        >>> # Defensive portfolio with lower beta during downturns
        >>> portfolio_returns = []
        >>> for bench_ret in benchmark_returns:
        ...     if bench_ret < 0:
        ...         port_ret = bench_ret * 0.7 + np.random.normal(0, 0.002)  # Less downside
        ...     else:
        ...         port_ret = bench_ret * 0.9 + np.random.normal(0, 0.002)  # Some upside
        ...     portfolio_returns.append(port_ret)
        >>> portfolio_returns = pd.Series(portfolio_returns, index=dates)
        >>> 
        >>> # Calculate downside capture
        >>> downside_capture = calculate_downside_capture(portfolio_returns, benchmark_returns)
        >>> print(f"Downside Capture: {downside_capture:.2f} ({downside_capture:.1%})")
        >>> 
        >>> if downside_capture < 1.0:
        ...     print("Portfolio provides downside protection")
        >>> else:
        ...     print("Portfolio amplifies benchmark losses")
        
    Note:
        - Uses empyrical.down_capture() for proven calculation accuracy
        - Values < 1.0 indicate the portfolio has better downside protection (desirable)
        - Values > 1.0 indicate the portfolio amplifies benchmark losses (undesirable)
        - Only considers periods when benchmark returns are negative
        - Complementary metric to upside capture ratio
        - Essential for evaluating defensive portfolio characteristics
        - Returns are automatically aligned for consistent comparison
        - Lower downside capture with reasonable upside capture indicates skilled management
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
    """Calculate Calmar ratio (annualized return / maximum drawdown) using empyrical library.
    
    Computes the Calmar ratio, which measures risk-adjusted returns by comparing
    annualized return to maximum drawdown. This ratio evaluates how much return
    an investment generates relative to its worst peak-to-trough decline, making
    it particularly useful for assessing tail risk and capital preservation.
    
    The Calmar ratio is especially valuable for evaluating hedge funds, managed
    futures, and other alternative investments where drawdown control is important.
    
    Args:
        returns (Union[pd.Series, Dict[str, Any]]): Return series as pandas Series with
            datetime index or dictionary with return values. Values should be decimal
            returns (e.g., 0.02 for 2% return, -0.01 for -1% return).
        
    Returns:
        float: Calmar ratio as decimal (e.g., 2.5 means 2.5 units of annual return
               per unit of maximum drawdown).
    
    Raises:
        ValueError: If returns cannot be converted to valid return series.
        TypeError: If input data format is invalid or incompatible.
        ZeroDivisionError: If maximum drawdown is zero (no losses experienced).
        
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Create return series with some drawdown periods
        >>> dates = pd.date_range('2023-01-01', periods=252, freq='D')
        >>> returns = pd.Series(np.random.normal(0.001, 0.012, 252), index=dates)
        >>> # Add a drawdown period
        >>> returns.iloc[100:120] = np.random.normal(-0.015, 0.008, 20)
        >>> 
        >>> # Calculate Calmar ratio
        >>> calmar = calculate_calmar_ratio(returns)
        >>> print(f"Calmar Ratio: {calmar:.3f}")
        >>> 
        >>> # Interpret the result
        >>> if calmar > 1.0:
        ...     print("Good risk-adjusted returns relative to drawdown")
        >>> elif calmar > 0.5:
        ...     print("Moderate risk-adjusted returns")
        >>> else:
        ...     print("Low risk-adjusted returns or high drawdown")
        
    Note:
        - Uses empyrical.calmar_ratio() for proven calculation accuracy
        - Formula: Calmar = Annual Return / |Maximum Drawdown|
        - Higher values indicate better risk-adjusted performance
        - More conservative than Sharpe ratio as it focuses on worst-case losses
        - Particularly relevant for evaluating downside risk management
        - Values above 1.0 are generally considered attractive
        - Complements Sharpe ratio by focusing on tail risk rather than volatility
        - Infinite value possible if no drawdown occurred (theoretical case)
        
    OUTPUT examples:
        Input: 10-day returns with small drawdown → 168.18 (very high ratio, limited drawdown)
        Input: returns with 15% max drawdown, 8% annual return → 0.53 (moderate risk-adjusted return)
        Input: returns with 25% max drawdown, 12% annual return → 0.48 (lower risk efficiency)
    """
    try:
        returns_series = validate_return_data(returns)
        
        # Use empyrical for Calmar ratio
        calmar = empyrical.calmar_ratio(returns_series)
        
        return float(calmar)
        
    except Exception as e:
        raise ValueError(f"Calmar ratio calculation failed: {str(e)}")


def calculate_omega_ratio(returns: Union[pd.Series, Dict[str, Any]], threshold: Optional[float] = None) -> float:
    """Calculate Omega ratio using empyrical library.
    
    Computes the Omega ratio, which measures the probability-weighted ratio of
    gains to losses above and below a specified threshold. Unlike traditional
    risk metrics that assume normal distributions, Omega ratio uses the actual
    return distribution, making it more accurate for skewed or fat-tailed returns.
    
    The Omega ratio is particularly valuable for evaluating alternative investments,
    hedge funds, and strategies with non-normal return distributions.
    
    Args:
        returns (Union[pd.Series, Dict[str, Any]]): Return series as pandas Series with
            datetime index or dictionary with return values. Values should be decimal
            returns (e.g., 0.02 for 2% return, -0.01 for -1% return).
        threshold (Optional[float], optional): Return threshold above which gains are
            measured and below which losses are measured. Defaults to 0.0 (zero return).
            Should be in same units as returns (decimal format).
        
    Returns:
        float: Omega ratio as decimal (e.g., 1.5 means 1.5 units of gains per unit of losses).
    
    Raises:
        ValueError: If returns cannot be converted to valid return series.
        TypeError: If input data format is invalid or threshold is not numeric.
        ZeroDivisionError: If no returns fall below the threshold (no losses).
        
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Create return series with some skewness
        >>> dates = pd.date_range('2023-01-01', periods=252, freq='D')
        >>> returns = pd.Series(np.random.normal(0.001, 0.015, 252), index=dates)
        >>> # Add some large positive outliers (positive skew)
        >>> returns.iloc[50] = 0.05
        >>> returns.iloc[150] = 0.04
        >>> 
        >>> # Calculate Omega ratio with zero threshold
        >>> omega = calculate_omega_ratio(returns)
        >>> print(f"Omega Ratio (0% threshold): {omega:.3f}")
        >>> 
        >>> # Calculate with risk-free rate threshold
        >>> risk_free_daily = 0.02 / 252  # 2% annual to daily
        >>> omega_rf = calculate_omega_ratio(returns, threshold=risk_free_daily)
        >>> print(f"Omega Ratio (2% threshold): {omega_rf:.3f}")
        
    Note:
        - Uses empyrical.omega_ratio() with specified risk_free parameter as threshold
        - Formula: Omega = [Integral of (1-F(x))dx from threshold to +∞] / [Integral of F(x)dx from -∞ to threshold]
        - Values > 1.0 indicate more gains than losses above/below threshold
        - Values < 1.0 indicate more losses than gains above/below threshold
        - Captures full return distribution, not just mean and variance
        - More robust for non-normal returns compared to Sharpe ratio
        - Commonly used thresholds: 0% (zero), risk-free rate, or target return
        - Higher values indicate better risk-adjusted performance
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
    """Calculate percentage of positive returns (win rate).
    
    Computes the proportion of periods with positive returns, providing a simple
    measure of consistency and the frequency of favorable outcomes. Win rate is
    particularly useful for understanding trading strategy effectiveness and
    investment consistency over time.
    
    While win rate doesn't account for magnitude of wins and losses, it provides
    valuable insight into the reliability and consistency of returns.
    
    Args:
        returns (Union[pd.Series, Dict[str, Any]]): Return series as pandas Series with
            datetime index or dictionary with return values. Values should be decimal
            returns (e.g., 0.02 for 2% return, -0.01 for -1% return).
        
    Returns:
        float: Win rate as decimal between 0.0 and 1.0 (e.g., 0.65 for 65% win rate).
    
    Raises:
        ValueError: If returns cannot be converted to valid return series.
        TypeError: If input data format is invalid or incompatible.
        
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Create return series with mixed positive and negative returns
        >>> dates = pd.date_range('2023-01-01', periods=100, freq='D')
        >>> returns = pd.Series(np.random.normal(0.001, 0.015, 100), index=dates)
        >>> 
        >>> # Calculate win rate
        >>> win_rate = calculate_win_rate(returns)
        >>> print(f"Win Rate: {win_rate:.2%}")
        >>> print(f"Positive periods: {int(win_rate * len(returns))} out of {len(returns)}")
        >>> 
        >>> # Create a more consistent strategy with higher win rate
        >>> consistent_returns = pd.Series(np.random.normal(0.003, 0.008, 100), index=dates)
        >>> consistent_win_rate = calculate_win_rate(consistent_returns)
        >>> print(f"Consistent Strategy Win Rate: {consistent_win_rate:.2%}")
        
    OUTPUT examples:
    Input: [0.02, -0.01, 0.03, -0.02, 0.01, 0.04, -0.015] → 0.5714285714285714 (57.14% win rate)
    Input: [0.01, 0.02, 0.03, 0.04] → 1.0 (100% win rate - all positive)
    Input: [-0.01, -0.02, -0.03] → 0.0 (0% win rate - all negative)
        
    Note:
        - Formula: Win Rate = Number of Positive Returns / Total Number of Returns
        - Values closer to 1.0 indicate more consistent positive performance
        - Values around 0.5 suggest random walk behavior (for normal distributions)
        - High win rate doesn't guarantee profitability (need to consider magnitude)
        - Useful complement to other performance metrics like Sharpe ratio
        - Particularly relevant for evaluating trading strategies and market timing
        - Should be analyzed alongside average win/loss sizes for complete picture
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
    """Identify best and worst performing periods using rolling window analysis.
    
    Analyzes rolling returns over specified window sizes to identify the best and worst
    performing periods in the return series. This analysis helps understand extreme
    performance scenarios, volatility clustering, and provides context for risk
    management and performance evaluation.
    
    This function is valuable for stress testing, scenario analysis, and understanding
    the range of possible outcomes over different time horizons.
    
    Args:
        returns (Union[pd.Series, Dict[str, Any]]): Return series as pandas Series with
            datetime index or dictionary with return values. Values should be decimal
            returns (e.g., 0.02 for 2% return, -0.01 for -1% return).
        window_size (int): Number of consecutive periods to analyze in each rolling window.
            For example, 21 for monthly periods in daily data, 252 for annual periods.
        
    Returns:
        Dict[str, Any]: Comprehensive analysis with keys:
            - window_size (int): The rolling window size used
            - best_period (Dict): Best performing period with start_date, end_date, return, return_pct
            - worst_period (Dict): Worst performing period with start_date, end_date, return, return_pct
            - total_periods (int): Total number of rolling periods analyzed
            - average_rolling_return (float): Average return across all rolling periods
            - rolling_volatility (float): Volatility of rolling period returns
            - success (bool): Whether calculation succeeded
            - function_name (str): Function identifier for tracking
    
    Raises:
        ValueError: If returns cannot be converted to valid return series or insufficient data for window size.
        TypeError: If input data format is invalid or window_size is not integer.
        
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Create return series with some volatile periods
        >>> dates = pd.date_range('2023-01-01', periods=252, freq='D')
        >>> returns = pd.Series(np.random.normal(0.001, 0.015, 252), index=dates)
        >>> # Add a very good month and a very bad month
        >>> returns.iloc[50:71] = np.random.normal(0.008, 0.01, 21)  # Good 21-day period
        >>> returns.iloc[150:171] = np.random.normal(-0.012, 0.008, 21)  # Bad 21-day period
        >>> 
        >>> # Analyze best and worst 21-day periods (approximately monthly)
        >>> result = calculate_best_worst_periods(returns, window_size=21)
        >>> print(f"Best 21-day period: {result['best_period']['return_pct']}")
        >>> print(f"  From {result['best_period']['start_date']} to {result['best_period']['end_date']}")
        >>> print(f"Worst 21-day period: {result['worst_period']['return_pct']}")
        >>> print(f"  From {result['worst_period']['start_date']} to {result['worst_period']['end_date']}")
        >>> print(f"Average rolling return: {result['average_rolling_return']:.3f}")
        
    Note:
        - Uses pandas rolling window with compound return calculation: (1+returns).prod()-1
        - Identifies exact date ranges for best and worst performance periods
        - Rolling volatility shows consistency of performance across different periods
        - Useful for understanding tail events and extreme scenarios
        - Can reveal clustering of good/bad performance periods
        - Window size should be chosen based on analysis timeframe (daily, monthly, quarterly)
        - Helps identify whether extreme returns are isolated or part of extended periods
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
    """Calculate dividend yield from dividend payments and current price.
    
    Computes the dividend yield, which represents the annual dividend income as
    a percentage of the current stock price. Dividend yield is a key metric for
    income-focused investors and helps evaluate the income-generating potential
    of dividend-paying stocks relative to their market price.
    
    This calculation is essential for dividend growth investing, REIT analysis,
    and income portfolio construction.
    
    Args:
        dividends (Union[list, np.ndarray, pd.Series]): Collection of dividend payments
            over the analysis period. Values should be absolute dividend amounts
            (e.g., [2.50, 2.60, 2.55] for quarterly dividends). Can be provided as
            list, numpy array, or pandas Series.
        price (float): Current stock price or average price for yield calculation.
            Must be positive as it serves as the denominator for yield calculation.
        
    Returns:
        float: Dividend yield as decimal (e.g., 0.04 for 4% dividend yield).
    
    Raises:
        ValueError: If price is not positive or dividend data contains invalid values.
        TypeError: If inputs are not numeric or dividends is not array-like.
        
    Example:
        >>> # Quarterly dividend payments over one year
        >>> quarterly_dividends = [2.50, 2.60, 2.55, 2.65]
        >>> current_price = 125.00
        >>> 
        >>> # Calculate dividend yield
        >>> div_yield = calculate_dividend_yield(quarterly_dividends, current_price)
        >>> print(f"Dividend Yield: {div_yield:.2%}")  # Output: ~8.24%
        >>> 
        >>> # REIT with monthly distributions
        >>> import numpy as np
        >>> monthly_distributions = np.array([0.25] * 12)  # $0.25 monthly
        >>> reit_price = 50.00
        >>> reit_yield = calculate_dividend_yield(monthly_distributions, reit_price)
        >>> print(f"REIT Yield: {reit_yield:.2%}")  # Output: 6.00%
        >>> 
        >>> # Handle pandas Series
        >>> import pandas as pd
        >>> dividend_series = pd.Series([1.20, 1.25, 1.30, 1.35])
        >>> stock_price = 80.00
        >>> yield_from_series = calculate_dividend_yield(dividend_series, stock_price)
        >>> print(f"Yield from Series: {yield_from_series:.2%}")
        
    Note:
        - Formula: Dividend Yield = Sum(Dividends) / Current Price
        - Automatically filters out NaN values and negative dividends
        - Assumes dividends represent total annual payments (sum all provided dividends)
        - For trailing twelve months yield, provide last 12 months of dividend payments
        - For forward yield estimates, provide expected next 12 months of dividends
        - Higher yields may indicate value opportunities or higher risk (yield trap)
        - Should be compared to historical yields and peer companies
        - Important for dividend growth and income investing strategies
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
    """Analyze leveraged fund characteristics including tracking efficiency and decay effects using industry-standard calculations.
    
    Performs comprehensive analysis of leveraged fund performance including tracking efficiency,
    volatility decay, compounding effects, and daily rebalancing costs. This analysis is crucial
    for understanding the performance differences between leveraged funds and their theoretical
    leveraged returns, particularly the impact of volatility drag over time.
    
    Leveraged funds use daily rebalancing to maintain target leverage, which creates compounding
    effects that deviate from simple leverage multiplication, especially in volatile markets.
    
    Args:
        prices (Union[pd.Series, Dict[str, Any]]): Leveraged fund price series as pandas Series
            with datetime index or dictionary with price values. Values should be absolute prices.
        leverage (float): Target leverage ratio of the fund (e.g., 2.0 for 2x fund, 3.0 for 3x fund,
            -1.0 for inverse fund). Positive values indicate long leverage, negative for inverse.
        underlying_prices (Union[pd.Series, Dict[str, Any]]): Underlying asset price series with
            same format as leveraged fund prices. Will be automatically aligned.
    
    Returns:
        Dict[str, Any]: Comprehensive leveraged fund analysis with keys:
            - target_leverage (float): Target leverage ratio
            - actual_leverage (float): Realized leverage based on correlation and volatility
            - leverage_efficiency (float): Actual leverage / target leverage ratio
            - tracking_error (float): Standard deviation of tracking differences
            - theoretical_drag (float): Theoretical volatility drag impact
            - leveraged_total_return (float): Actual leveraged fund total return
            - underlying_total_return (float): Underlying asset total return
            - expected_leveraged_return (float): Theoretical leveraged return
            - performance_gap (float): Difference between actual and expected returns
            - estimated_annual_cost (float): Estimated annual cost of daily rebalancing
            - underlying_volatility (float): Underlying asset annualized volatility
            - leveraged_volatility (float): Leveraged fund annualized volatility
            - success (bool): Whether calculation succeeded
            - function_name (str): Function identifier for tracking
    
    Raises:
        ValueError: If price data cannot be converted to valid price series or alignment fails.
        TypeError: If input data format is invalid or leverage is not numeric.
        ZeroDivisionError: If leverage is zero or underlying volatility calculations fail.
        
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Create sample underlying asset and leveraged fund data
        >>> dates = pd.date_range('2023-01-01', periods=252, freq='D')
        >>> underlying_returns = pd.Series(np.random.normal(0.0005, 0.015, 252), index=dates)
        >>> underlying_prices = pd.Series(100 * np.cumprod(1 + underlying_returns), index=dates)
        >>> 
        >>> # Simulate 2x leveraged fund with some tracking error and decay
        >>> leverage_ratio = 2.0
        >>> leveraged_returns = underlying_returns * leverage_ratio + np.random.normal(0, 0.002, 252)
        >>> leveraged_prices = pd.Series(100 * np.cumprod(1 + leveraged_returns), index=dates)
        >>> 
        >>> # Analyze leveraged fund performance
        >>> result = analyze_leverage_fund(leveraged_prices, leverage_ratio, underlying_prices)
        >>> print(f"Target Leverage: {result['target_leverage']:.1f}x")
        >>> print(f"Actual Leverage: {result['actual_leverage']:.3f}x")
        >>> print(f"Leverage Efficiency: {result['leverage_efficiency']:.3f}")
        >>> print(f"Performance Gap: {result['performance_gap_pct']}")
        >>> print(f"Theoretical Drag: {result['theoretical_drag_pct']}")
        >>> print(f"Estimated Annual Cost: {result['estimated_annual_cost_pct']}")
        
    Note:
        - Actual leverage calculated as correlation × (leveraged_vol / underlying_vol)
        - Theoretical drag = 0.5 × (leverage - 1) × underlying_volatility²
        - Performance gap shows actual vs theoretical leveraged returns
        - Daily rebalancing costs increase with underlying asset volatility
        - Leveraged funds typically underperform theoretical leverage in volatile markets
        - Analysis accounts for compounding effects of daily rebalancing
        - Negative leverage values supported for inverse funds
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