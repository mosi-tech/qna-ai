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
        >>> import numpy as np
        >>> 
        >>> # Create sample daily return data for one year
        >>> dates = pd.date_range('2023-01-01', periods=252, freq='D')
        >>> daily_returns = pd.Series(np.random.normal(0.0008, 0.015, 252), index=dates)
        >>> 
        >>> # Calculate return metrics
        >>> result = calculate_returns_metrics(daily_returns)
        >>> print(f"Total Return: {result['total_return_pct']}")
        >>> print(f"Annualized Return: {result['annual_return_pct']}")
        >>> print(f"Number of Observations: {result['num_observations']}")
        >>> 
        >>> # Access cumulative return series for plotting
        >>> cumulative_series = result['cumulative_returns']
        >>> print(f"Final Cumulative Return: {cumulative_series.iloc[-1]:.3f}")
        
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
        >>> import numpy as np
        >>> 
        >>> # Create sample return data with some volatility
        >>> dates = pd.date_range('2023-01-01', periods=252, freq='D')
        >>> returns = pd.Series(np.random.normal(0.0008, 0.015, 252), index=dates)
        >>> 
        >>> # Calculate risk metrics
        >>> result = calculate_risk_metrics(returns, risk_free_rate=0.02)
        >>> print(f"Annualized Volatility: {result['volatility_pct']}")
        >>> print(f"Sharpe Ratio: {result['sharpe_ratio']:.3f}")
        >>> print(f"Maximum Drawdown: {result['max_drawdown_pct']}")
        >>> print(f"VaR 95%: {result['var_95_pct']}")
        >>> print(f"Sortino Ratio: {result['sortino_ratio']:.3f}")
        >>> 
        >>> # Check distribution characteristics
        >>> print(f"Skewness: {result['skewness']:.3f}")
        >>> print(f"Kurtosis: {result['kurtosis']:.3f}")
        
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
        >>> import numpy as np
        >>> 
        >>> # Create sample portfolio and benchmark return data
        >>> dates = pd.date_range('2023-01-01', periods=252, freq='D')
        >>> benchmark_returns = pd.Series(np.random.normal(0.0005, 0.012, 252), index=dates)
        >>> # Portfolio with some alpha and higher beta
        >>> portfolio_returns = pd.Series(
        ...     benchmark_returns * 1.2 + np.random.normal(0.0002, 0.005, 252), 
        ...     index=dates
        ... )
        >>> 
        >>> # Calculate benchmark comparison metrics
        >>> result = calculate_benchmark_metrics(portfolio_returns, benchmark_returns)
        >>> print(f"Alpha: {result['alpha_pct']}")
        >>> print(f"Beta: {result['beta']:.3f}")
        >>> print(f"Information Ratio: {result['information_ratio']:.3f}")
        >>> print(f"Tracking Error: {result['tracking_error_pct']}")
        >>> print(f"Upside Capture: {result['up_capture']:.3f}")
        >>> print(f"Downside Capture: {result['down_capture']:.3f}")
        
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
    """Analyze leveraged fund characteristics including tracking efficiency and decay effects.
    
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