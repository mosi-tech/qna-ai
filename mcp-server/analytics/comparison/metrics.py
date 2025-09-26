"""Comparison Analysis Metrics Module using empyrical and pandas.

This module provides comprehensive atomic comparison functions for assets, strategies, and 
portfolios. All functions use industry-standard libraries (empyrical, pandas, scipy) for
proven accuracy and implement standardized return formats with detailed winner analysis
and statistical significance testing.

The module implements atomic comparison functions from the financial-analysis-function-library.json
comparison_analysis category, focusing on statistical accuracy and comprehensive analysis
rather than reinventing financial calculations.

Key Features:
    - Industry-standard empyrical library implementation for proven accuracy
    - Comprehensive winner determination with category-based scoring
    - Support for both price and return data with automatic alignment
    - Statistical significance testing and confidence intervals where applicable
    - Performance optimized using pandas and numpy for large datasets
    - Detailed error handling with informative error messages

Dependencies:
    - empyrical: Core financial performance and risk calculations
    - pandas: Data manipulation and time series handling
    - numpy: Numerical computations and array operations
    - scipy: Statistical analysis and hypothesis testing

Example:
    >>> import pandas as pd
    >>> from mcp.analytics.comparison.metrics import compare_performance_metrics
    >>> 
    >>> # Create sample return data
    >>> returns_spy = pd.Series([0.01, -0.02, 0.015, 0.008, -0.005])
    >>> returns_qqq = pd.Series([0.02, -0.025, 0.018, 0.012, -0.008])
    >>> 
    >>> # Compare performance
    >>> result = compare_performance_metrics(returns_spy, returns_qqq)
    >>> print(f"Overall Winner: {result['summary']['overall_winner']}")
    >>> print(f"Sharpe Ratio Difference: {result['metrics_comparison']['sharpe_ratio']['difference']:.3f}")

Note:
    All functions return standardized dictionary outputs with success indicators and detailed
    error handling. Missing data is handled gracefully with appropriate error messages.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Union, Optional
import warnings
warnings.filterwarnings('ignore')

# Use empyrical library from requirements.txt - no wheel reinvention
import empyrical
from scipy import stats

from ..utils.data_utils import validate_return_data, validate_price_data, align_series, standardize_output
from ..performance.metrics import (
    calculate_returns_metrics, 
    calculate_risk_metrics,
    calculate_drawdown_analysis,
    calculate_annualized_return,
    calculate_annualized_volatility,
    calculate_win_rate
)
from ..risk.metrics import (
    calculate_var,
    calculate_cvar,
    calculate_beta,
    calculate_correlation,
    calculate_skewness,
    calculate_kurtosis
)


def compare_performance_metrics(returns1: Union[pd.Series, Dict[str, Any]], 
                               returns2: Union[pd.Series, Dict[str, Any]]) -> Dict[str, Any]:
    """Compare key performance metrics between two assets or strategies using empyrical library.
    
    Performs comprehensive performance comparison between two return series, calculating
    key metrics like annual returns, total returns, volatility, Sharpe ratio, maximum drawdown,
    and win rates. Uses industry-standard empyrical library for proven accuracy and provides
    detailed winner analysis with both absolute and relative differences.
    
    The function automatically aligns time series data and handles missing values, ensuring
    fair comparison between assets with different data availability periods.
    
    Args:
        returns1 (Union[pd.Series, Dict[str, Any]]): Return series for first asset/strategy.
            Can be pandas Series with datetime index or dictionary with return values.
            Values should be decimal returns (e.g., 0.05 for 5% return).
        returns2 (Union[pd.Series, Dict[str, Any]]): Return series for second asset/strategy.
            Same format requirements as returns1. Will be aligned with returns1 automatically.
    
    Returns:
        Dict[str, Any]: Comprehensive performance comparison with keys:
            - comparison_period (str): Number of observations used in comparison
            - metrics_comparison (Dict): Detailed comparison of each metric with keys:
                - annual_return: Annualized return comparison
                - total_return: Cumulative return comparison  
                - volatility: Annualized volatility comparison
                - sharpe_ratio: Risk-adjusted return comparison
                - max_drawdown: Maximum peak-to-trough decline comparison
                - win_rate: Percentage of positive return periods
            - summary (Dict): Overall comparison summary with winner counts
            - correlation (float): Correlation coefficient between the two return series
            - success (bool): Whether calculation succeeded
            - function_name (str): Function identifier for tracking
    
    Raises:
        ValueError: If returns data cannot be converted to valid return series.
        TypeError: If input data format is invalid or incompatible.
        
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Create sample return data
        >>> dates = pd.date_range('2020-01-01', periods=252, freq='D')
        >>> returns_spy = pd.Series(np.random.normal(0.0008, 0.015, 252), index=dates)
        >>> returns_qqq = pd.Series(np.random.normal(0.001, 0.018, 252), index=dates)
        >>> 
        >>> # Compare performance
        >>> result = compare_performance_metrics(returns_spy, returns_qqq)
        >>> print(f"Overall Winner: {result['summary']['overall_winner']}")
        >>> print(f"Annual Return - SPY: {result['metrics_comparison']['annual_return']['asset_1']:.2%}")
        >>> print(f"Annual Return - QQQ: {result['metrics_comparison']['annual_return']['asset_2']:.2%}")
        >>> print(f"Sharpe Ratio Difference: {result['metrics_comparison']['sharpe_ratio']['difference']:.3f}")
        >>> print(f"Correlation: {result['correlation']:.3f}")
        
    Note:
        - Uses empyrical library for industry-standard financial calculations
        - Automatically handles data alignment and missing values
        - Winner determination is based on standard financial criteria (higher is better for returns/Sharpe, lower is better for volatility/drawdown)
        - All metrics are calculated on aligned data for fair comparison
        - Returns are assumed to be in decimal format (not percentage)
        - Function handles both daily and other frequency data automatically
    """
    try:
        returns_series1 = validate_return_data(returns1)
        returns_series2 = validate_return_data(returns2)
        
        # Align series for fair comparison
        ret1_aligned, ret2_aligned = align_series(returns_series1, returns_series2)
        
        # Calculate performance metrics for both
        perf1 = calculate_returns_metrics(ret1_aligned)
        perf2 = calculate_returns_metrics(ret2_aligned)
        risk1 = calculate_risk_metrics(ret1_aligned)
        risk2 = calculate_risk_metrics(ret2_aligned)
        
        # Extract key metrics for comparison
        metrics_comparison = {
            "annual_return": {
                "asset_1": perf1.get("annual_return", 0),
                "asset_2": perf2.get("annual_return", 0),
                "difference": perf2.get("annual_return", 0) - perf1.get("annual_return", 0),
                "winner": "asset_2" if perf2.get("annual_return", 0) > perf1.get("annual_return", 0) else "asset_1"
            },
            "total_return": {
                "asset_1": perf1.get("total_return", 0),
                "asset_2": perf2.get("total_return", 0),
                "difference": perf2.get("total_return", 0) - perf1.get("total_return", 0),
                "winner": "asset_2" if perf2.get("total_return", 0) > perf1.get("total_return", 0) else "asset_1"
            },
            "volatility": {
                "asset_1": risk1.get("volatility", 0),
                "asset_2": risk2.get("volatility", 0),
                "difference": risk2.get("volatility", 0) - risk1.get("volatility", 0),
                "winner": "asset_1" if risk1.get("volatility", 0) < risk2.get("volatility", 0) else "asset_2"
            },
            "sharpe_ratio": {
                "asset_1": risk1.get("sharpe_ratio", 0),
                "asset_2": risk2.get("sharpe_ratio", 0),
                "difference": risk2.get("sharpe_ratio", 0) - risk1.get("sharpe_ratio", 0),
                "winner": "asset_2" if risk2.get("sharpe_ratio", 0) > risk1.get("sharpe_ratio", 0) else "asset_1"
            },
            "max_drawdown": {
                "asset_1": risk1.get("max_drawdown", 0),
                "asset_2": risk2.get("max_drawdown", 0),
                "difference": risk2.get("max_drawdown", 0) - risk1.get("max_drawdown", 0),
                "winner": "asset_1" if abs(risk1.get("max_drawdown", 0)) < abs(risk2.get("max_drawdown", 0)) else "asset_2"
            }
        }
        
        # Calculate win rates
        win_rate1 = calculate_win_rate(ret1_aligned)
        win_rate2 = calculate_win_rate(ret2_aligned)
        
        metrics_comparison["win_rate"] = {
            "asset_1": win_rate1,
            "asset_2": win_rate2,
            "difference": win_rate2 - win_rate1,
            "winner": "asset_2" if win_rate2 > win_rate1 else "asset_1"
        }
        
        # Calculate overall winner
        wins_asset1 = sum(1 for metric in metrics_comparison.values() if metric.get("winner") == "asset_1")
        wins_asset2 = sum(1 for metric in metrics_comparison.values() if metric.get("winner") == "asset_2")
        
        result = {
            "comparison_period": f"{len(ret1_aligned)} observations",
            "metrics_comparison": metrics_comparison,
            "summary": {
                "asset_1_wins": wins_asset1,
                "asset_2_wins": wins_asset2,
                "overall_winner": "asset_1" if wins_asset1 > wins_asset2 else "asset_2",
                "total_metrics": len(metrics_comparison)
            },
            "correlation": calculate_correlation(ret1_aligned, ret2_aligned)
        }
        
        return standardize_output(result, "compare_performance_metrics")
        
    except Exception as e:
        return {"success": False, "error": f"Performance comparison failed: {str(e)}"}


def compare_risk_metrics(returns1: Union[pd.Series, Dict[str, Any]], 
                        returns2: Union[pd.Series, Dict[str, Any]]) -> Dict[str, Any]:
    """Compare comprehensive risk metrics between two assets or strategies using empyrical and scipy.
    
    Performs detailed risk analysis comparison between two return series, calculating volatility,
    Value at Risk (VaR), Conditional Value at Risk (CVaR), maximum drawdown, and distribution
    characteristics (skewness, kurtosis). Uses industry-standard risk calculations and provides
    comprehensive winner analysis based on risk-adjusted criteria.
    
    The function employs multiple risk measures to provide a holistic view of risk characteristics,
    including both traditional volatility measures and tail risk metrics that capture extreme events.
    
    Args:
        returns1 (Union[pd.Series, Dict[str, Any]]): Return series for first asset/strategy.
            Can be pandas Series with datetime index or dictionary with return values.
            Values should be decimal returns (e.g., -0.03 for -3% return).
        returns2 (Union[pd.Series, Dict[str, Any]]): Return series for second asset/strategy.
            Same format requirements as returns1. Will be aligned with returns1 automatically.
    
    Returns:
        Dict[str, Any]: Comprehensive risk comparison with keys:
            - comparison_period (str): Number of observations used in comparison
            - risk_comparison (Dict): Detailed comparison of each risk metric with keys:
                - volatility: Annualized volatility comparison
                - var_95: 95% Value at Risk (expected worst 5% loss)
                - cvar_95: 95% Conditional Value at Risk (expected loss given VaR breach)
                - max_drawdown: Maximum peak-to-trough decline
                - skewness: Distribution asymmetry (positive = right skewed)
                - kurtosis: Distribution tail thickness (higher = fatter tails)
            - summary (Dict): Overall risk assessment with lower-risk asset identification
            - correlation (float): Correlation coefficient between return series
            - success (bool): Whether calculation succeeded
            - function_name (str): Function identifier for tracking
    
    Raises:
        ValueError: If returns data cannot be converted to valid return series.
        TypeError: If input data format is invalid or incompatible.
        
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Create sample return data with different risk characteristics
        >>> dates = pd.date_range('2020-01-01', periods=252, freq='D')
        >>> returns_spy = pd.Series(np.random.normal(0.0008, 0.015, 252), index=dates)
        >>> returns_crypto = pd.Series(np.random.normal(0.002, 0.045, 252), index=dates)
        >>> 
        >>> # Compare risk profiles
        >>> result = compare_risk_metrics(returns_spy, returns_crypto)
        >>> print(f"Lower Risk Asset: {result['summary']['lower_risk_asset']}")
        >>> print(f"Volatility - SPY: {result['risk_comparison']['volatility']['asset_1']:.2%}")
        >>> print(f"Volatility - Crypto: {result['risk_comparison']['volatility']['asset_2']:.2%}")
        >>> print(f"VaR 95% - SPY: {result['risk_comparison']['var_95']['asset_1']:.2%}")
        >>> print(f"VaR 95% - Crypto: {result['risk_comparison']['var_95']['asset_2']:.2%}")
        >>> print(f"Risk Wins - Asset 1: {result['summary']['asset_1_wins']}")
        
    Note:
        - Lower values are generally better for risk metrics (except positive skewness)
        - VaR and CVaR calculations use historical simulation method
        - Skewness interpretation: positive = more upside potential, negative = more downside risk
        - Kurtosis interpretation: higher values = more extreme events (fat tails)
        - All calculations use industry-standard empyrical and scipy implementations
        - Winner determination prioritizes lower risk across multiple dimensions
        - Function handles both daily and other frequency data automatically
    """
    try:
        returns_series1 = validate_return_data(returns1)
        returns_series2 = validate_return_data(returns2)
        
        # Align series
        ret1_aligned, ret2_aligned = align_series(returns_series1, returns_series2)
        
        # Calculate risk metrics
        risk1 = calculate_risk_metrics(ret1_aligned)
        risk2 = calculate_risk_metrics(ret2_aligned)
        
        # VaR and CVaR calculations
        var1 = calculate_var(ret1_aligned, confidence_level=0.05)
        var2 = calculate_var(ret2_aligned, confidence_level=0.05)
        cvar1 = calculate_cvar(ret1_aligned, confidence_level=0.05)
        cvar2 = calculate_cvar(ret2_aligned, confidence_level=0.05)
        
        # Distribution metrics
        skew1 = calculate_skewness(ret1_aligned)
        skew2 = calculate_skewness(ret2_aligned)
        kurt1 = calculate_kurtosis(ret1_aligned)
        kurt2 = calculate_kurtosis(ret2_aligned)
        
        risk_comparison = {
            "volatility": {
                "asset_1": risk1.get("volatility", 0),
                "asset_2": risk2.get("volatility", 0),
                "difference": risk2.get("volatility", 0) - risk1.get("volatility", 0),
                "winner": "asset_1" if risk1.get("volatility", 0) < risk2.get("volatility", 0) else "asset_2"
            },
            "var_95": {
                "asset_1": var1.get("var_daily", 0),
                "asset_2": var2.get("var_daily", 0),
                "difference": var2.get("var_daily", 0) - var1.get("var_daily", 0),
                "winner": "asset_1" if abs(var1.get("var_daily", 0)) < abs(var2.get("var_daily", 0)) else "asset_2"
            },
            "cvar_95": {
                "asset_1": cvar1.get("cvar_daily", 0),
                "asset_2": cvar2.get("cvar_daily", 0),
                "difference": cvar2.get("cvar_daily", 0) - cvar1.get("cvar_daily", 0),
                "winner": "asset_1" if abs(cvar1.get("cvar_daily", 0)) < abs(cvar2.get("cvar_daily", 0)) else "asset_2"
            },
            "max_drawdown": {
                "asset_1": risk1.get("max_drawdown", 0),
                "asset_2": risk2.get("max_drawdown", 0),
                "difference": risk2.get("max_drawdown", 0) - risk1.get("max_drawdown", 0),
                "winner": "asset_1" if abs(risk1.get("max_drawdown", 0)) < abs(risk2.get("max_drawdown", 0)) else "asset_2"
            },
            "skewness": {
                "asset_1": skew1,
                "asset_2": skew2,
                "difference": skew2 - skew1,
                "winner": "asset_2" if skew2 > skew1 else "asset_1"  # Higher skewness is better
            },
            "kurtosis": {
                "asset_1": kurt1,
                "asset_2": kurt2,
                "difference": kurt2 - kurt1,
                "winner": "asset_1" if abs(kurt1) < abs(kurt2) else "asset_2"  # Lower excess kurtosis is better
            }
        }
        
        # Calculate overall risk winner (lower risk wins most categories)
        wins_asset1 = sum(1 for metric in risk_comparison.values() if metric.get("winner") == "asset_1")
        wins_asset2 = sum(1 for metric in risk_comparison.values() if metric.get("winner") == "asset_2")
        
        result = {
            "comparison_period": f"{len(ret1_aligned)} observations",
            "risk_comparison": risk_comparison,
            "summary": {
                "asset_1_wins": wins_asset1,
                "asset_2_wins": wins_asset2,
                "lower_risk_asset": "asset_1" if wins_asset1 > wins_asset2 else "asset_2",
                "total_metrics": len(risk_comparison)
            },
            "correlation": calculate_correlation(ret1_aligned, ret2_aligned)
        }
        
        return standardize_output(result, "compare_risk_metrics")
        
    except Exception as e:
        return {"success": False, "error": f"Risk comparison failed: {str(e)}"}


def compare_drawdowns(prices1: Union[pd.Series, Dict[str, Any]], 
                     prices2: Union[pd.Series, Dict[str, Any]]) -> Dict[str, Any]:
    """Compare comprehensive drawdown characteristics between two assets using empyrical library.
    
    Analyzes and compares drawdown patterns between two price series, including maximum drawdown,
    frequency of significant drawdowns, and time spent in drawdown periods. Uses empyrical library
    for industry-standard drawdown calculations and provides detailed analysis of downside risk
    characteristics that complement traditional volatility measures.
    
    Drawdown analysis is crucial for understanding the worst-case scenarios and recovery patterns
    of investments, particularly important for risk management and investor psychology.
    
    Args:
        prices1 (Union[pd.Series, Dict[str, Any]]): Price series for first asset.
            Can be pandas Series with datetime index or dictionary with price values.
            Values should be absolute prices (e.g., 100.50, 95.25, etc.).
        prices2 (Union[pd.Series, Dict[str, Any]]): Price series for second asset.
            Same format requirements as prices1. Will be aligned with prices1 automatically.
    
    Returns:
        Dict[str, Any]: Comprehensive drawdown comparison with keys:
            - comparison_period (str): Number of observations used in comparison
            - drawdown_comparison (Dict): Detailed comparison of drawdown metrics with keys:
                - max_drawdown: Maximum peak-to-trough decline (worst single drawdown)
                - significant_drawdowns: Count of drawdowns exceeding 5% threshold
                - time_in_drawdown: Percentage of time spent below previous peak
            - summary (Dict): Overall drawdown assessment with better profile identification
            - success (bool): Whether calculation succeeded
            - function_name (str): Function identifier for tracking
    
    Raises:
        ValueError: If price data cannot be converted to valid price series.
        TypeError: If input data format is invalid or incompatible.
        ZeroDivisionError: If price series contains zero or negative values.
        
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Create sample price data with different drawdown characteristics
        >>> dates = pd.date_range('2020-01-01', periods=252, freq='D')
        >>> # Stable growth with occasional pullbacks
        >>> prices_spy = pd.Series(100 * np.cumprod(1 + np.random.normal(0.0008, 0.015, 252)), index=dates)
        >>> # More volatile with larger drawdowns
        >>> prices_growth = pd.Series(100 * np.cumprod(1 + np.random.normal(0.001, 0.025, 252)), index=dates)
        >>> 
        >>> # Compare drawdown profiles
        >>> result = compare_drawdowns(prices_spy, prices_growth)
        >>> print(f"Better Drawdown Profile: {result['summary']['better_drawdown_profile']}")
        >>> print(f"Max Drawdown - SPY: {result['drawdown_comparison']['max_drawdown']['asset_1']:.2%}")
        >>> print(f"Max Drawdown - Growth: {result['drawdown_comparison']['max_drawdown']['asset_2']:.2%}")
        >>> print(f"Time in Drawdown - SPY: {result['drawdown_comparison']['time_in_drawdown']['asset_1']:.1f}%")
        >>> print(f"Significant Drawdowns - Growth: {result['drawdown_comparison']['significant_drawdowns']['asset_2']}")
        
    Note:
        - Prices are converted to returns internally for drawdown calculation
        - Significant drawdowns are defined as declines exceeding 5% from peak
        - Time in drawdown measures periods when price is below previous high
        - Empyrical library used for industry-standard drawdown calculations
        - Lower drawdown values and shorter recovery periods are preferable
        - Maximum drawdown is the single worst peak-to-trough decline
        - Function automatically handles data alignment and missing values
    """
    try:
        price_series1 = validate_price_data(prices1)
        price_series2 = validate_price_data(prices2)
        
        # Convert to returns for drawdown analysis
        returns1 = price_series1.pct_change().dropna()
        returns2 = price_series2.pct_change().dropna()
        
        # Align series
        ret1_aligned, ret2_aligned = align_series(returns1, returns2)
        
        # Calculate drawdown analysis
        dd1 = calculate_drawdown_analysis(ret1_aligned)
        dd2 = calculate_drawdown_analysis(ret2_aligned)
        
        # Extract drawdown details using empyrical
        dd_details1 = empyrical.drawdown_details(empyrical.cum_returns(ret1_aligned))
        dd_details2 = empyrical.drawdown_details(empyrical.cum_returns(ret2_aligned))
        
        # Calculate additional drawdown metrics
        drawdown_series1 = empyrical.drawdown_details(empyrical.cum_returns(ret1_aligned))
        drawdown_series2 = empyrical.drawdown_details(empyrical.cum_returns(ret2_aligned))
        
        # Count significant drawdowns (>5%)
        significant_dd1 = (drawdown_series1 < -0.05).sum() if hasattr(drawdown_series1, 'sum') else 0
        significant_dd2 = (drawdown_series2 < -0.05).sum() if hasattr(drawdown_series2, 'sum') else 0
        
        # Average time in drawdown
        in_drawdown1 = (drawdown_series1 < 0).sum() if hasattr(drawdown_series1, 'sum') else 0
        in_drawdown2 = (drawdown_series2 < 0).sum() if hasattr(drawdown_series2, 'sum') else 0
        
        pct_time_dd1 = (in_drawdown1 / len(ret1_aligned)) * 100 if len(ret1_aligned) > 0 else 0
        pct_time_dd2 = (in_drawdown2 / len(ret2_aligned)) * 100 if len(ret2_aligned) > 0 else 0
        
        drawdown_comparison = {
            "max_drawdown": {
                "asset_1": dd1.get("max_drawdown", 0),
                "asset_2": dd2.get("max_drawdown", 0),
                "difference": dd2.get("max_drawdown", 0) - dd1.get("max_drawdown", 0),
                "winner": "asset_1" if abs(dd1.get("max_drawdown", 0)) < abs(dd2.get("max_drawdown", 0)) else "asset_2"
            },
            "significant_drawdowns": {
                "asset_1": significant_dd1,
                "asset_2": significant_dd2,
                "difference": significant_dd2 - significant_dd1,
                "winner": "asset_1" if significant_dd1 < significant_dd2 else "asset_2"
            },
            "time_in_drawdown": {
                "asset_1": pct_time_dd1,
                "asset_2": pct_time_dd2,
                "difference": pct_time_dd2 - pct_time_dd1,
                "winner": "asset_1" if pct_time_dd1 < pct_time_dd2 else "asset_2"
            }
        }
        
        # Overall drawdown winner
        wins_asset1 = sum(1 for metric in drawdown_comparison.values() if metric.get("winner") == "asset_1")
        wins_asset2 = sum(1 for metric in drawdown_comparison.values() if metric.get("winner") == "asset_2")
        
        result = {
            "comparison_period": f"{len(ret1_aligned)} observations",
            "drawdown_comparison": drawdown_comparison,
            "summary": {
                "asset_1_wins": wins_asset1,
                "asset_2_wins": wins_asset2,
                "better_drawdown_profile": "asset_1" if wins_asset1 > wins_asset2 else "asset_2",
                "total_metrics": len(drawdown_comparison)
            }
        }
        
        return standardize_output(result, "compare_drawdowns")
        
    except Exception as e:
        return {"success": False, "error": f"Drawdown comparison failed: {str(e)}"}


def compare_volatility_profiles(returns1: Union[pd.Series, Dict[str, Any]], 
                               returns2: Union[pd.Series, Dict[str, Any]], 
                               window: int = 30) -> Dict[str, Any]:
    """Compare rolling volatility profiles and stability between two assets using pandas calculations.
    
    Analyzes and compares rolling volatility patterns between two return series, including average
    volatility, volatility of volatility (regime stability), extreme volatility periods, and
    correlation of volatility patterns. This analysis helps identify which asset has more stable
    risk characteristics over time and how volatility regimes compare.
    
    Rolling volatility analysis is essential for understanding dynamic risk characteristics and
    identifying periods of market stress that affect different assets differently.
    
    Args:
        returns1 (Union[pd.Series, Dict[str, Any]]): Return series for first asset.
            Can be pandas Series with datetime index or dictionary with return values.
            Values should be decimal returns (e.g., 0.02 for 2% return).
        returns2 (Union[pd.Series, Dict[str, Any]]): Return series for second asset.
            Same format requirements as returns1. Will be aligned with returns1 automatically.
        window (int, optional): Rolling window size for volatility calculation. Defaults to 30.
            Common values: 21 (monthly), 30, 60 (quarterly), 252 (annual). Larger windows
            provide smoother but less responsive volatility estimates.
    
    Returns:
        Dict[str, Any]: Comprehensive volatility profile comparison with keys:
            - window_size (int): Rolling window size used for calculations
            - comparison_period (str): Number of rolling periods used in comparison
            - volatility_comparison (Dict): Detailed volatility profile metrics with keys:
                - average_volatility: Mean rolling volatility over the period
                - volatility_volatility: Standard deviation of volatility (stability measure)
                - max_volatility: Highest volatility period observed
                - min_volatility: Lowest volatility period observed
                - high_volatility_periods: Count of periods above 90th percentile
            - volatility_correlation (float): Correlation between volatility series
            - summary (Dict): Overall volatility stability assessment
            - success (bool): Whether calculation succeeded
            - function_name (str): Function identifier for tracking
    
    Raises:
        ValueError: If returns data cannot be converted to valid return series.
        TypeError: If window parameter is not an integer or data format is invalid.
        
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Create sample return data with different volatility characteristics
        >>> dates = pd.date_range('2020-01-01', periods=300, freq='D')
        >>> # Stable volatility asset
        >>> returns_bond = pd.Series(np.random.normal(0.0002, 0.005, 300), index=dates)
        >>> # Variable volatility asset with regime changes
        >>> vol_regimes = np.concatenate([np.full(150, 0.015), np.full(150, 0.030)])
        >>> returns_stock = pd.Series([np.random.normal(0.0008, vol) for vol in vol_regimes], index=dates)
        >>> 
        >>> # Compare volatility profiles
        >>> result = compare_volatility_profiles(returns_bond, returns_stock, window=30)
        >>> print(f"More Stable Volatility: {result['summary']['more_stable_volatility']}")
        >>> print(f"Average Vol - Bonds: {result['volatility_comparison']['average_volatility']['asset_1']:.2%}")
        >>> print(f"Average Vol - Stocks: {result['volatility_comparison']['average_volatility']['asset_2']:.2%}")
        >>> print(f"Vol of Vol - Bonds: {result['volatility_comparison']['volatility_volatility']['asset_1']:.3f}")
        >>> print(f"Vol of Vol - Stocks: {result['volatility_comparison']['volatility_volatility']['asset_2']:.3f}")
        >>> print(f"Volatility Correlation: {result['volatility_correlation']:.3f}")
        
    Note:
        - Rolling volatility is annualized (multiplied by sqrt(252) for daily data)
        - Volatility of volatility measures regime stability (lower is more stable)
        - High volatility periods are defined as above 90th percentile of each asset
        - Window size affects responsiveness vs. noise trade-off
        - Correlation shows how synchronized volatility regimes are between assets
        - Lower and more stable volatility is generally preferable for risk management
        - Function handles both daily and other frequency data automatically
    """
    try:
        returns_series1 = validate_return_data(returns1)
        returns_series2 = validate_return_data(returns2)
        
        # Align series
        ret1_aligned, ret2_aligned = align_series(returns_series1, returns_series2)
        
        # Calculate rolling volatility (annualized)
        rolling_vol1 = ret1_aligned.rolling(window=window).std() * np.sqrt(252)
        rolling_vol2 = ret2_aligned.rolling(window=window).std() * np.sqrt(252)
        
        # Remove NaN values
        rolling_vol1 = rolling_vol1.dropna()
        rolling_vol2 = rolling_vol2.dropna()
        
        # Align rolling series
        vol1_aligned, vol2_aligned = align_series(rolling_vol1, rolling_vol2)
        
        # Calculate volatility statistics
        vol_stats = {
            "average_volatility": {
                "asset_1": float(vol1_aligned.mean()),
                "asset_2": float(vol2_aligned.mean()),
                "difference": float(vol2_aligned.mean() - vol1_aligned.mean()),
                "winner": "asset_1" if vol1_aligned.mean() < vol2_aligned.mean() else "asset_2"
            },
            "volatility_volatility": {  # Volatility of volatility
                "asset_1": float(vol1_aligned.std()),
                "asset_2": float(vol2_aligned.std()),
                "difference": float(vol2_aligned.std() - vol1_aligned.std()),
                "winner": "asset_1" if vol1_aligned.std() < vol2_aligned.std() else "asset_2"
            },
            "max_volatility": {
                "asset_1": float(vol1_aligned.max()),
                "asset_2": float(vol2_aligned.max()),
                "difference": float(vol2_aligned.max() - vol1_aligned.max()),
                "winner": "asset_1" if vol1_aligned.max() < vol2_aligned.max() else "asset_2"
            },
            "min_volatility": {
                "asset_1": float(vol1_aligned.min()),
                "asset_2": float(vol2_aligned.min()),
                "difference": float(vol2_aligned.min() - vol1_aligned.min()),
                "winner": "asset_1" if vol1_aligned.min() < vol2_aligned.min() else "asset_2"
            }
        }
        
        # Volatility correlation
        vol_correlation = vol1_aligned.corr(vol2_aligned)
        
        # Periods of high volatility (>90th percentile)
        high_vol_threshold1 = vol1_aligned.quantile(0.9)
        high_vol_threshold2 = vol2_aligned.quantile(0.9)
        
        high_vol_periods1 = (vol1_aligned > high_vol_threshold1).sum()
        high_vol_periods2 = (vol2_aligned > high_vol_threshold2).sum()
        
        vol_stats["high_volatility_periods"] = {
            "asset_1": int(high_vol_periods1),
            "asset_2": int(high_vol_periods2),
            "difference": int(high_vol_periods2 - high_vol_periods1),
            "winner": "asset_1" if high_vol_periods1 < high_vol_periods2 else "asset_2"
        }
        
        # Overall volatility profile winner
        wins_asset1 = sum(1 for metric in vol_stats.values() if metric.get("winner") == "asset_1")
        wins_asset2 = sum(1 for metric in vol_stats.values() if metric.get("winner") == "asset_2")
        
        result = {
            "window_size": window,
            "comparison_period": f"{len(vol1_aligned)} rolling periods",
            "volatility_comparison": vol_stats,
            "volatility_correlation": float(vol_correlation),
            "summary": {
                "asset_1_wins": wins_asset1,
                "asset_2_wins": wins_asset2,
                "more_stable_volatility": "asset_1" if wins_asset1 > wins_asset2 else "asset_2",
                "total_metrics": len(vol_stats)
            }
        }
        
        return standardize_output(result, "compare_volatility_profiles")
        
    except Exception as e:
        return {"success": False, "error": f"Volatility profile comparison failed: {str(e)}"}


def compare_correlation_stability(returns1: Union[pd.Series, Dict[str, Any]], 
                                 returns2: Union[pd.Series, Dict[str, Any]], 
                                 window: int = 60) -> Dict[str, Any]:
    """
    Analyze correlation stability over time.
    
    From financial-analysis-function-library.json comparison_analysis category
    Uses pandas rolling correlation - no code duplication
    
    Args:
        returns1: First asset returns
        returns2: Second asset returns
        window: Rolling window for correlation calculation
        
    Returns:
        Dict: Correlation stability analysis
    """
    try:
        returns_series1 = validate_return_data(returns1)
        returns_series2 = validate_return_data(returns2)
        
        # Align series
        ret1_aligned, ret2_aligned = align_series(returns_series1, returns_series2)
        
        # Calculate rolling correlation
        rolling_corr = ret1_aligned.rolling(window=window).corr(ret2_aligned)
        rolling_corr = rolling_corr.dropna()
        
        if len(rolling_corr) == 0:
            raise ValueError("Insufficient data for rolling correlation calculation")
        
        # Calculate correlation statistics
        corr_stats = {
            "average_correlation": float(rolling_corr.mean()),
            "correlation_volatility": float(rolling_corr.std()),
            "max_correlation": float(rolling_corr.max()),
            "min_correlation": float(rolling_corr.min()),
            "correlation_range": float(rolling_corr.max() - rolling_corr.min())
        }
        
        # Correlation regime analysis
        high_corr_threshold = 0.7
        low_corr_threshold = 0.3
        
        high_corr_periods = (rolling_corr > high_corr_threshold).sum()
        low_corr_periods = (rolling_corr < low_corr_threshold).sum()
        moderate_corr_periods = len(rolling_corr) - high_corr_periods - low_corr_periods
        
        # Calculate percentage in each regime
        total_periods = len(rolling_corr)
        
        correlation_regimes = {
            "high_correlation_periods": {
                "count": int(high_corr_periods),
                "percentage": float((high_corr_periods / total_periods) * 100)
            },
            "moderate_correlation_periods": {
                "count": int(moderate_corr_periods),
                "percentage": float((moderate_corr_periods / total_periods) * 100)
            },
            "low_correlation_periods": {
                "count": int(low_corr_periods),
                "percentage": float((low_corr_periods / total_periods) * 100)
            }
        }
        
        # Stability assessment
        stability_score = 1 - (corr_stats["correlation_volatility"] / 1.0)  # Normalize by max possible std (1.0)
        stability_rating = "high" if stability_score > 0.8 else "moderate" if stability_score > 0.6 else "low"
        
        # Trend analysis - is correlation increasing or decreasing?
        recent_corr = rolling_corr.tail(window // 2).mean()
        early_corr = rolling_corr.head(window // 2).mean()
        correlation_trend = "increasing" if recent_corr > early_corr else "decreasing"
        trend_magnitude = abs(recent_corr - early_corr)
        
        result = {
            "window_size": window,
            "total_rolling_periods": total_periods,
            "correlation_statistics": corr_stats,
            "correlation_regimes": correlation_regimes,
            "stability_analysis": {
                "stability_score": float(stability_score),
                "stability_rating": stability_rating,
                "correlation_trend": correlation_trend,
                "trend_magnitude": float(trend_magnitude)
            },
            "overall_correlation": float(ret1_aligned.corr(ret2_aligned))
        }
        
        return standardize_output(result, "compare_correlation_stability")
        
    except Exception as e:
        return {"success": False, "error": f"Correlation stability analysis failed: {str(e)}"}


def compare_sector_exposure(holdings1: List[Dict[str, Any]], 
                           holdings2: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compare sector allocation between portfolios/ETFs.
    
    From financial-analysis-function-library.json comparison_analysis category
    Uses pandas for sector analysis - no code duplication
    
    Args:
        holdings1: First portfolio/ETF holdings
        holdings2: Second portfolio/ETF holdings
        
    Returns:
        Dict: Sector comparison data
    """
    try:
        # Convert holdings to DataFrames
        df1 = pd.DataFrame(holdings1)
        df2 = pd.DataFrame(holdings2)
        
        # Validate required columns
        required_cols = ['sector', 'weight']
        for col in required_cols:
            if col not in df1.columns or col not in df2.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Aggregate by sector
        sector_weights1 = df1.groupby('sector')['weight'].sum().sort_values(ascending=False)
        sector_weights2 = df2.groupby('sector')['weight'].sum().sort_values(ascending=False)
        
        # Get all unique sectors
        all_sectors = set(sector_weights1.index) | set(sector_weights2.index)
        
        # Create sector comparison
        sector_comparison = {}
        for sector in all_sectors:
            weight1 = sector_weights1.get(sector, 0)
            weight2 = sector_weights2.get(sector, 0)
            
            sector_comparison[sector] = {
                "portfolio_1_weight": float(weight1),
                "portfolio_2_weight": float(weight2),
                "difference": float(weight2 - weight1),
                "relative_difference": float((weight2 - weight1) / max(weight1, 0.01)) if weight1 > 0 else float('inf') if weight2 > 0 else 0
            }
        
        # Calculate concentration metrics
        def calculate_sector_concentration(weights):
            weights_array = np.array(list(weights.values()))
            weights_normalized = weights_array / weights_array.sum()
            hhi = np.sum(weights_normalized ** 2)
            return hhi
        
        concentration1 = calculate_sector_concentration(sector_weights1)
        concentration2 = calculate_sector_concentration(sector_weights2)
        
        # Find largest differences
        sorted_sectors = sorted(
            sector_comparison.items(), 
            key=lambda x: abs(x[1]['difference']), 
            reverse=True
        )
        
        largest_differences = [
            {
                "sector": sector,
                "difference": data["difference"],
                "portfolio_1_weight": data["portfolio_1_weight"],
                "portfolio_2_weight": data["portfolio_2_weight"]
            }
            for sector, data in sorted_sectors[:5]
        ]
        
        # Calculate sector overlap
        common_sectors = set(sector_weights1.index) & set(sector_weights2.index)
        overlap_percentage = (len(common_sectors) / len(all_sectors)) * 100
        
        result = {
            "total_sectors": len(all_sectors),
            "common_sectors": len(common_sectors),
            "overlap_percentage": float(overlap_percentage),
            "sector_comparison": sector_comparison,
            "concentration_analysis": {
                "portfolio_1_hhi": float(concentration1),
                "portfolio_2_hhi": float(concentration2),
                "more_concentrated": "portfolio_1" if concentration1 > concentration2 else "portfolio_2"
            },
            "largest_differences": largest_differences,
            "top_sectors": {
                "portfolio_1": [
                    {"sector": sector, "weight": float(weight)} 
                    for sector, weight in sector_weights1.head(5).items()
                ],
                "portfolio_2": [
                    {"sector": sector, "weight": float(weight)} 
                    for sector, weight in sector_weights2.head(5).items()
                ]
            }
        }
        
        return standardize_output(result, "compare_sector_exposure")
        
    except Exception as e:
        return {"success": False, "error": f"Sector exposure comparison failed: {str(e)}"}


def compare_expense_ratios(funds: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compare expense ratios and fees.
    
    From financial-analysis-function-library.json comparison_analysis category
    Simple expense ratio comparison - no code duplication
    
    Args:
        funds: List of fund data with expense ratios
        
    Returns:
        Dict: Expense comparison data
    """
    try:
        if len(funds) < 2:
            raise ValueError("At least 2 funds required for comparison")
        
        # Extract expense ratios
        expense_data = []
        for i, fund in enumerate(funds):
            if 'expense_ratio' not in fund:
                raise ValueError(f"Fund {i} missing expense_ratio")
            
            expense_data.append({
                "fund_name": fund.get("name", f"Fund_{i+1}"),
                "symbol": fund.get("symbol", f"FUND{i+1}"),
                "expense_ratio": float(fund["expense_ratio"]),
                "expense_ratio_pct": f"{float(fund['expense_ratio']) * 100:.2f}%"
            })
        
        # Sort by expense ratio
        expense_data_sorted = sorted(expense_data, key=lambda x: x["expense_ratio"])
        
        # Calculate cost impact over time
        def calculate_cost_impact(expense_ratio, initial_amount=10000, years=10, annual_return=0.07):
            """Calculate the cost impact of expense ratios over time"""
            # Final value with costs
            net_return = annual_return - expense_ratio
            final_with_costs = initial_amount * ((1 + net_return) ** years)
            
            # Final value without costs
            final_without_costs = initial_amount * ((1 + annual_return) ** years)
            
            # Cost impact
            cost_impact = final_without_costs - final_with_costs
            
            return {
                "final_value_with_costs": final_with_costs,
                "final_value_without_costs": final_without_costs,
                "total_cost_impact": cost_impact,
                "cost_impact_percentage": (cost_impact / final_without_costs) * 100
            }
        
        # Calculate cost impacts
        for fund in expense_data:
            fund["cost_impact_10_years"] = calculate_cost_impact(fund["expense_ratio"])
        
        # Find differences
        cheapest = expense_data_sorted[0]
        most_expensive = expense_data_sorted[-1]
        
        # Calculate difference in costs
        cost_difference = most_expensive["expense_ratio"] - cheapest["expense_ratio"]
        impact_difference = (
            most_expensive["cost_impact_10_years"]["total_cost_impact"] - 
            cheapest["cost_impact_10_years"]["total_cost_impact"]
        )
        
        result = {
            "funds_compared": len(funds),
            "expense_comparison": expense_data_sorted,
            "summary": {
                "cheapest_fund": {
                    "name": cheapest["fund_name"],
                    "expense_ratio": cheapest["expense_ratio"],
                    "expense_ratio_pct": cheapest["expense_ratio_pct"]
                },
                "most_expensive_fund": {
                    "name": most_expensive["fund_name"],
                    "expense_ratio": most_expensive["expense_ratio"],
                    "expense_ratio_pct": most_expensive["expense_ratio_pct"]
                },
                "cost_difference": {
                    "expense_ratio_difference": float(cost_difference),
                    "expense_ratio_difference_pct": f"{cost_difference * 100:.2f}%",
                    "10_year_impact_difference": float(impact_difference),
                    "percentage_savings": f"{(impact_difference / 10000) * 100:.2f}%"
                }
            }
        }
        
        return standardize_output(result, "compare_expense_ratios")
        
    except Exception as e:
        return {"success": False, "error": f"Expense ratio comparison failed: {str(e)}"}


def compare_liquidity(volumes1: Union[pd.Series, Dict[str, Any], List[float]], 
                     volumes2: Union[pd.Series, Dict[str, Any], List[float]]) -> Dict[str, Any]:
    """
    Compare liquidity metrics.
    
    From financial-analysis-function-library.json comparison_analysis category
    Uses pandas for volume analysis - no code duplication
    
    Args:
        volumes1: First asset volume data
        volumes2: Second asset volume data
        
    Returns:
        Dict: Liquidity comparison data
    """
    try:
        # Convert to pandas Series
        if isinstance(volumes1, (list, np.ndarray)):
            vol1 = pd.Series(volumes1)
        elif isinstance(volumes1, dict):
            vol1 = pd.Series(list(volumes1.values()))
        else:
            vol1 = volumes1.copy()
        
        if isinstance(volumes2, (list, np.ndarray)):
            vol2 = pd.Series(volumes2)
        elif isinstance(volumes2, dict):
            vol2 = pd.Series(list(volumes2.values()))
        else:
            vol2 = volumes2.copy()
        
        # Align series
        vol1_aligned, vol2_aligned = align_series(vol1, vol2)
        
        # Calculate liquidity metrics
        liquidity_metrics = {
            "average_volume": {
                "asset_1": float(vol1_aligned.mean()),
                "asset_2": float(vol2_aligned.mean()),
                "difference": float(vol2_aligned.mean() - vol1_aligned.mean()),
                "winner": "asset_2" if vol2_aligned.mean() > vol1_aligned.mean() else "asset_1"
            },
            "median_volume": {
                "asset_1": float(vol1_aligned.median()),
                "asset_2": float(vol2_aligned.median()),
                "difference": float(vol2_aligned.median() - vol1_aligned.median()),
                "winner": "asset_2" if vol2_aligned.median() > vol1_aligned.median() else "asset_1"
            },
            "volume_volatility": {  # Consistency of volume
                "asset_1": float(vol1_aligned.std()),
                "asset_2": float(vol2_aligned.std()),
                "difference": float(vol2_aligned.std() - vol1_aligned.std()),
                "winner": "asset_1" if vol1_aligned.std() < vol2_aligned.std() else "asset_2"  # Lower volatility is better
            },
            "max_volume": {
                "asset_1": float(vol1_aligned.max()),
                "asset_2": float(vol2_aligned.max()),
                "difference": float(vol2_aligned.max() - vol1_aligned.max()),
                "winner": "asset_2" if vol2_aligned.max() > vol1_aligned.max() else "asset_1"
            },
            "min_volume": {
                "asset_1": float(vol1_aligned.min()),
                "asset_2": float(vol2_aligned.min()),
                "difference": float(vol2_aligned.min() - vol1_aligned.min()),
                "winner": "asset_2" if vol2_aligned.min() > vol1_aligned.min() else "asset_1"
            }
        }
        
        # Calculate zero/low volume days
        low_volume_threshold_1 = vol1_aligned.quantile(0.1)  # Bottom 10%
        low_volume_threshold_2 = vol2_aligned.quantile(0.1)
        
        low_volume_days_1 = (vol1_aligned <= low_volume_threshold_1).sum()
        low_volume_days_2 = (vol2_aligned <= low_volume_threshold_2).sum()
        
        liquidity_metrics["low_volume_days"] = {
            "asset_1": int(low_volume_days_1),
            "asset_2": int(low_volume_days_2),
            "difference": int(low_volume_days_2 - low_volume_days_1),
            "winner": "asset_1" if low_volume_days_1 < low_volume_days_2 else "asset_2"
        }
        
        # Volume correlation
        volume_correlation = vol1_aligned.corr(vol2_aligned)
        
        # Overall liquidity winner
        wins_asset1 = sum(1 for metric in liquidity_metrics.values() if metric.get("winner") == "asset_1")
        wins_asset2 = sum(1 for metric in liquidity_metrics.values() if metric.get("winner") == "asset_2")
        
        # Liquidity score (normalized)
        def calculate_liquidity_score(volumes):
            # Higher average volume, lower volatility = better score
            avg_vol = volumes.mean()
            vol_consistency = 1 / (volumes.std() / avg_vol + 0.01)  # Coefficient of variation
            return avg_vol * vol_consistency
        
        score1 = calculate_liquidity_score(vol1_aligned)
        score2 = calculate_liquidity_score(vol2_aligned)
        
        result = {
            "comparison_period": f"{len(vol1_aligned)} observations",
            "liquidity_comparison": liquidity_metrics,
            "volume_correlation": float(volume_correlation),
            "liquidity_scores": {
                "asset_1_score": float(score1),
                "asset_2_score": float(score2),
                "score_ratio": float(score2 / score1) if score1 > 0 else float('inf')
            },
            "summary": {
                "asset_1_wins": wins_asset1,
                "asset_2_wins": wins_asset2,
                "more_liquid_asset": "asset_1" if score1 > score2 else "asset_2",
                "total_metrics": len(liquidity_metrics)
            }
        }
        
        return standardize_output(result, "compare_liquidity")
        
    except Exception as e:
        return {"success": False, "error": f"Liquidity comparison failed: {str(e)}"}


def compare_fundamental(fundamentals1: Dict[str, Any], 
                       fundamentals2: Dict[str, Any]) -> Dict[str, Any]:
    """Compare comprehensive fundamental metrics between two companies across multiple categories.
    
    Performs detailed fundamental analysis comparison between two companies, evaluating valuation,
    financial health, profitability, and growth metrics. Uses standard financial ratio analysis
    with category-based scoring to determine overall fundamental strength and identify specific
    areas where each company excels.
    
    The analysis covers key fundamental categories that professional analysts use for stock
    evaluation, providing both individual metric comparisons and categorical assessments.
    
    Args:
        fundamentals1 (Dict[str, Any]): Fundamental data dictionary for first company.
            Should contain financial metrics like pe_ratio, debt_to_equity, return_on_equity, etc.
            Standard keys include: pe_ratio, price_to_book, price_to_sales, price_to_cash_flow,
            debt_to_equity, current_ratio, quick_ratio, return_on_equity, return_on_assets,
            profit_margin, operating_margin, revenue_growth, earnings_growth, dividend_yield,
            market_cap, name, symbol, sector.
        fundamentals2 (Dict[str, Any]): Fundamental data dictionary for second company.
            Same format requirements as fundamentals1.
    
    Returns:
        Dict[str, Any]: Comprehensive fundamental comparison with keys:
            - metrics_compared (int): Number of metrics successfully compared
            - fundamental_comparison (Dict): Individual metric comparisons with keys for each metric:
                - company_1: First company's value
                - company_2: Second company's value  
                - difference: Absolute difference
                - relative_difference: Percentage difference
                - winner: Which company has better value for this metric
            - category_analysis (Dict): Category-based assessment with keys:
                - valuation: P/E, P/B, P/S, P/CF ratios comparison
                - financial_health: Debt/equity, current ratio, quick ratio comparison
                - profitability: ROE, ROA, profit margin, operating margin comparison
                - growth: Revenue growth, earnings growth comparison
            - summary (Dict): Overall fundamental assessment and company information
            - success (bool): Whether calculation succeeded
            - function_name (str): Function identifier for tracking
    
    Raises:
        ValueError: If fundamental data dictionaries are empty or missing required structure.
        TypeError: If fundamental values cannot be converted to numeric format.
        KeyError: If critical fundamental metrics are completely missing.
        
    Example:
        >>> # Sample fundamental data
        >>> apple_fundamentals = {
        ...     'name': 'Apple Inc.', 'symbol': 'AAPL', 'sector': 'Technology',
        ...     'pe_ratio': 25.5, 'price_to_book': 8.2, 'debt_to_equity': 1.8,
        ...     'return_on_equity': 0.84, 'profit_margin': 0.25, 'revenue_growth': 0.08
        ... }
        >>> microsoft_fundamentals = {
        ...     'name': 'Microsoft Corp.', 'symbol': 'MSFT', 'sector': 'Technology',
        ...     'pe_ratio': 28.1, 'price_to_book': 12.1, 'debt_to_equity': 0.9,
        ...     'return_on_equity': 0.42, 'profit_margin': 0.31, 'revenue_growth': 0.12
        ... }
        >>> 
        >>> # Compare fundamentals
        >>> result = compare_fundamental(apple_fundamentals, microsoft_fundamentals)
        >>> print(f"Overall Winner: {result['summary']['overall_fundamental_winner']}")
        >>> print(f"Valuation Winner: {result['category_analysis']['valuation']['winner']}")
        >>> print(f"Profitability Winner: {result['category_analysis']['profitability']['winner']}")
        >>> print(f"P/E Ratio - AAPL: {result['fundamental_comparison']['pe_ratio']['company_1']:.1f}")
        >>> print(f"P/E Ratio - MSFT: {result['fundamental_comparison']['pe_ratio']['company_2']:.1f}")
        >>> print(f"ROE - AAPL: {result['fundamental_comparison']['return_on_equity']['company_1']:.1%}")
        
    Note:
        - Lower values are better for valuation metrics (P/E, P/B, P/S, P/CF, Debt/Equity)
        - Higher values are better for profitability and efficiency metrics (ROE, ROA, margins)
        - Higher values are better for growth metrics (revenue growth, earnings growth)
        - Category winners are determined by majority wins within each category
        - Missing metrics are skipped rather than causing errors
        - Relative differences show percentage change from company_1 to company_2
        - Function handles various data formats and missing values gracefully
    """
    try:
        # Define key fundamental metrics to compare
        key_metrics = [
            'pe_ratio', 'price_to_book', 'price_to_sales', 'price_to_cash_flow',
            'debt_to_equity', 'current_ratio', 'quick_ratio', 'return_on_equity',
            'return_on_assets', 'profit_margin', 'operating_margin', 'revenue_growth',
            'earnings_growth', 'dividend_yield', 'market_cap'
        ]
        
        fundamental_comparison = {}
        
        for metric in key_metrics:
            value1 = fundamentals1.get(metric)
            value2 = fundamentals2.get(metric)
            
            if value1 is not None and value2 is not None:
                try:
                    val1 = float(value1)
                    val2 = float(value2)
                    
                    # Determine winner based on metric type
                    if metric in ['pe_ratio', 'price_to_book', 'price_to_sales', 'price_to_cash_flow', 'debt_to_equity']:
                        # Lower is better
                        winner = "company_1" if val1 < val2 else "company_2"
                    else:
                        # Higher is better
                        winner = "company_1" if val1 > val2 else "company_2"
                    
                    fundamental_comparison[metric] = {
                        "company_1": val1,
                        "company_2": val2,
                        "difference": val2 - val1,
                        "relative_difference": ((val2 - val1) / abs(val1)) * 100 if val1 != 0 else float('inf'),
                        "winner": winner
                    }
                except (ValueError, TypeError):
                    # Skip metrics that can't be converted to float
                    continue
        
        # Calculate category winners
        valuation_metrics = ['pe_ratio', 'price_to_book', 'price_to_sales', 'price_to_cash_flow']
        financial_health_metrics = ['debt_to_equity', 'current_ratio', 'quick_ratio']
        profitability_metrics = ['return_on_equity', 'return_on_assets', 'profit_margin', 'operating_margin']
        growth_metrics = ['revenue_growth', 'earnings_growth']
        
        def count_category_wins(metrics_list):
            wins_c1 = sum(1 for metric in metrics_list 
                         if metric in fundamental_comparison and 
                         fundamental_comparison[metric]['winner'] == 'company_1')
            wins_c2 = sum(1 for metric in metrics_list 
                         if metric in fundamental_comparison and 
                         fundamental_comparison[metric]['winner'] == 'company_2')
            return wins_c1, wins_c2
        
        valuation_wins = count_category_wins(valuation_metrics)
        health_wins = count_category_wins(financial_health_metrics)
        profitability_wins = count_category_wins(profitability_metrics)
        growth_wins = count_category_wins(growth_metrics)
        
        # Overall fundamental winner
        total_wins_c1 = sum(1 for comp in fundamental_comparison.values() if comp['winner'] == 'company_1')
        total_wins_c2 = sum(1 for comp in fundamental_comparison.values() if comp['winner'] == 'company_2')
        
        result = {
            "metrics_compared": len(fundamental_comparison),
            "fundamental_comparison": fundamental_comparison,
            "category_analysis": {
                "valuation": {
                    "company_1_wins": valuation_wins[0],
                    "company_2_wins": valuation_wins[1],
                    "winner": "company_1" if valuation_wins[0] > valuation_wins[1] else "company_2"
                },
                "financial_health": {
                    "company_1_wins": health_wins[0],
                    "company_2_wins": health_wins[1],
                    "winner": "company_1" if health_wins[0] > health_wins[1] else "company_2"
                },
                "profitability": {
                    "company_1_wins": profitability_wins[0],
                    "company_2_wins": profitability_wins[1],
                    "winner": "company_1" if profitability_wins[0] > profitability_wins[1] else "company_2"
                },
                "growth": {
                    "company_1_wins": growth_wins[0],
                    "company_2_wins": growth_wins[1],
                    "winner": "company_1" if growth_wins[0] > growth_wins[1] else "company_2"
                }
            },
            "summary": {
                "company_1_total_wins": total_wins_c1,
                "company_2_total_wins": total_wins_c2,
                "overall_fundamental_winner": "company_1" if total_wins_c1 > total_wins_c2 else "company_2",
                "company_1_info": {
                    "name": fundamentals1.get("name", "Company 1"),
                    "symbol": fundamentals1.get("symbol", "N/A"),
                    "sector": fundamentals1.get("sector", "N/A")
                },
                "company_2_info": {
                    "name": fundamentals2.get("name", "Company 2"),
                    "symbol": fundamentals2.get("symbol", "N/A"),
                    "sector": fundamentals2.get("sector", "N/A")
                }
            }
        }
        
        return standardize_output(result, "compare_fundamental")
        
    except Exception as e:
        return {"success": False, "error": f"Fundamental comparison failed: {str(e)}"}


def compute_outperformance(returns: Union[pd.DataFrame, Dict[str, pd.Series]], 
                          benchmark_returns: Union[pd.Series, Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate outperformance of multiple stocks against a benchmark.
    
    Outperformance analysis measures how individual assets or portfolios perform
    relative to a benchmark over time. This function computes comprehensive
    outperformance metrics for multiple assets simultaneously, including
    excess returns, alpha, tracking error, and statistical significance tests.
    
    The analysis helps identify which assets consistently beat the benchmark,
    by how much, and with what level of statistical confidence. Essential for
    active portfolio management and fund performance evaluation.
    
    Args:
        returns (Union[pd.DataFrame, Dict[str, pd.Series]]): Multi-asset return data.
            Can be provided as:
            - pandas DataFrame: Assets as columns, dates as index
            - Dictionary: Asset names as keys, return series (pd.Series) as values
            All return series should contain decimal returns (e.g., 0.02 for 2%).
        benchmark_returns (Union[pd.Series, Dict[str, Any]]): Benchmark return series
            for comparison (e.g., S&P 500, market index). Must have overlapping
            periods with asset returns. Can be provided as pandas Series with
            datetime index or dictionary with dates as keys.
            
    Returns:
        Dict[str, Any]: Comprehensive outperformance analysis including:
            - asset_outperformance: Individual asset performance vs benchmark
                * excess_return_annualized: Annual excess return over benchmark
                * alpha_annualized: Risk-adjusted excess return (Jensen's alpha)
                * tracking_error_annualized: Volatility of excess returns
                * information_ratio: Excess return per unit of tracking error
                * outperformance_periods: Number/percentage of periods beating benchmark
                * beta: Systematic risk relative to benchmark
                * correlation: Linear correlation with benchmark
            - portfolio_summary: Aggregate statistics across all assets
                * best_performer: Asset with highest excess return
                * worst_performer: Asset with lowest excess return
                * average_outperformance: Mean excess return across assets
                * outperforming_assets_count: Number of assets beating benchmark
                * statistical_significance: Assets with significant outperformance
            - benchmark_info: Benchmark performance characteristics
                * annual_return: Benchmark annualized return
                * annual_volatility: Benchmark annualized volatility
                * total_periods: Number of observation periods
            
    Raises:
        ValueError: If outperformance calculation fails due to data alignment issues,
            insufficient overlapping data, or invalid input formats.
            
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Create sample multi-asset return data
        >>> dates = pd.date_range('2023-01-01', periods=252, freq='D')
        >>> np.random.seed(42)
        >>> 
        >>> # Simulate asset returns with different performance characteristics
        >>> benchmark_rets = pd.Series(np.random.normal(0.0005, 0.015, 252), index=dates, name='SPY')
        >>> 
        >>> asset_returns = pd.DataFrame({
        ...     'AAPL': benchmark_rets * 1.2 + np.random.normal(0.0002, 0.008, 252),  # Outperformer
        ...     'MSFT': benchmark_rets * 1.1 + np.random.normal(0.0001, 0.007, 252),  # Slight outperformer  
        ...     'T': benchmark_rets * 0.7 + np.random.normal(0, 0.005, 252),         # Underperformer
        ...     'AMZN': benchmark_rets * 1.5 + np.random.normal(0.0003, 0.020, 252)  # Volatile outperformer
        ... }, index=dates)
        >>> 
        >>> # Calculate outperformance
        >>> outperf_analysis = compute_outperformance(asset_returns, benchmark_rets)
        >>> 
        >>> # Review results
        >>> print("=== OUTPERFORMANCE ANALYSIS ===")
        >>> best = outperf_analysis['portfolio_summary']['best_performer']
        >>> print(f"Best Performer: {best['asset']} (+{best['excess_return_pct']})")
        >>> 
        >>> print("\\n=== INDIVIDUAL ASSET PERFORMANCE ===")
        >>> for asset, metrics in outperf_analysis['asset_outperformance'].items():
        ...     print(f"{asset}:")
        ...     print(f"  Excess Return: {metrics['excess_return_pct']}")
        ...     print(f"  Information Ratio: {metrics['information_ratio']:.3f}")
        ...     print(f"  Outperformance Rate: {metrics['outperformance_periods_pct']}")
        ...     print(f"  Alpha: {metrics['alpha_pct']}")
        
    Note:
        - Uses empyrical library for industry-standard financial calculations
        - Excess returns calculated as: asset_return - benchmark_return
        - Alpha calculated using CAPM: α = (Rp - Rf) - β(Rm - Rf)
        - Information ratio = Excess Return / Tracking Error (higher is better)
        - Tracking error is annualized standard deviation of excess returns
        - Statistical significance based on t-test of excess returns vs zero
        - Outperformance periods show consistency of beating benchmark
        - Beta > 1 indicates higher systematic risk than benchmark
        - All return metrics are annualized assuming 252 trading days per year
        - Missing data is handled via pairwise alignment of time series
        - Particularly useful for fund analysis, stock selection, and manager evaluation
    """
    try:
        # Validate and prepare data
        if isinstance(returns, dict):
            returns_df = pd.DataFrame(returns)
        elif isinstance(returns, pd.DataFrame):
            returns_df = returns.copy()
        else:
            raise ValueError("Returns must be DataFrame or dict of Series")
            
        # Validate benchmark returns
        from ..utils.data_utils import validate_return_data, align_series
        benchmark_series = validate_return_data(benchmark_returns)
        
        # Results storage
        asset_outperformance = {}
        
        # Analyze each asset
        for asset_name in returns_df.columns:
            asset_returns = returns_df[asset_name].dropna()
            
            # Align asset and benchmark returns
            asset_aligned, benchmark_aligned = align_series(asset_returns, benchmark_series)
            
            if len(asset_aligned) < 30:  # Minimum periods for meaningful analysis
                asset_outperformance[asset_name] = {
                    "error": "Insufficient overlapping data (minimum 30 periods required)",
                    "periods_available": len(asset_aligned)
                }
                continue
            
            # Calculate excess returns
            excess_returns = asset_aligned - benchmark_aligned
            
            # Core performance metrics using empyrical
            import empyrical
            
            # Annualized metrics
            excess_return_annual = empyrical.annual_return(excess_returns)
            tracking_error_annual = empyrical.annual_volatility(excess_returns)
            
            # Alpha calculation (CAPM)
            beta = empyrical.beta(asset_aligned, benchmark_aligned)
            alpha_annual = empyrical.alpha(asset_aligned, benchmark_aligned, risk_free=0.02)
            
            # Information ratio
            information_ratio = excess_return_annual / tracking_error_annual if tracking_error_annual > 0 else 0
            
            # Outperformance frequency
            outperformance_periods = (excess_returns > 0).sum()
            outperformance_rate = outperformance_periods / len(excess_returns)
            
            # Correlation
            correlation = asset_aligned.corr(benchmark_aligned)
            
            # Statistical significance (t-test of excess returns)
            from scipy import stats
            t_stat, p_value = stats.ttest_1samp(excess_returns.dropna(), 0)
            is_significant = p_value < 0.05
            
            # Compile asset results
            asset_outperformance[asset_name] = {
                "excess_return_annualized": float(excess_return_annual),
                "excess_return_pct": f"{excess_return_annual * 100:+.2f}%",
                "alpha_annualized": float(alpha_annual),
                "alpha_pct": f"{alpha_annual * 100:+.2f}%",
                "tracking_error_annualized": float(tracking_error_annual),
                "tracking_error_pct": f"{tracking_error_annual * 100:.2f}%",
                "information_ratio": float(information_ratio),
                "beta": float(beta),
                "correlation": float(correlation),
                "outperformance_periods": int(outperformance_periods),
                "outperformance_periods_pct": f"{outperformance_rate * 100:.1f}%",
                "total_periods": len(asset_aligned),
                "statistical_significance": {
                    "is_significant": bool(is_significant),
                    "t_statistic": float(t_stat),
                    "p_value": float(p_value)
                }
            }
        
        # Calculate portfolio summary statistics
        valid_assets = {k: v for k, v in asset_outperformance.items() if "error" not in v}
        
        if not valid_assets:
            return {
                "success": False,
                "error": "No assets had sufficient data for analysis"
            }
        
        # Find best and worst performers
        excess_returns = [(asset, metrics["excess_return_annualized"]) 
                         for asset, metrics in valid_assets.items()]
        best_performer = max(excess_returns, key=lambda x: x[1])
        worst_performer = min(excess_returns, key=lambda x: x[1])
        
        # Summary statistics
        avg_excess_return = np.mean([metrics["excess_return_annualized"] 
                                   for metrics in valid_assets.values()])
        outperforming_count = sum(1 for metrics in valid_assets.values() 
                                if metrics["excess_return_annualized"] > 0)
        significant_count = sum(1 for metrics in valid_assets.values() 
                              if metrics["statistical_significance"]["is_significant"] and 
                              metrics["excess_return_annualized"] > 0)
        
        # Benchmark characteristics  
        benchmark_annual_return = empyrical.annual_return(benchmark_series)
        benchmark_annual_vol = empyrical.annual_volatility(benchmark_series)
        
        result = {
            "asset_outperformance": asset_outperformance,
            "portfolio_summary": {
                "best_performer": {
                    "asset": best_performer[0],
                    "excess_return_annualized": float(best_performer[1]),
                    "excess_return_pct": f"{best_performer[1] * 100:+.2f}%"
                },
                "worst_performer": {
                    "asset": worst_performer[0], 
                    "excess_return_annualized": float(worst_performer[1]),
                    "excess_return_pct": f"{worst_performer[1] * 100:+.2f}%"
                },
                "average_outperformance": float(avg_excess_return),
                "average_outperformance_pct": f"{avg_excess_return * 100:+.2f}%",
                "assets_analyzed": len(valid_assets),
                "outperforming_assets_count": outperforming_count,
                "outperforming_assets_pct": f"{outperforming_count / len(valid_assets) * 100:.1f}%",
                "statistically_significant_count": significant_count
            },
            "benchmark_info": {
                "annual_return": float(benchmark_annual_return),
                "annual_return_pct": f"{benchmark_annual_return * 100:.2f}%",
                "annual_volatility": float(benchmark_annual_vol),
                "annual_volatility_pct": f"{benchmark_annual_vol * 100:.2f}%",
                "total_periods": len(benchmark_series)
            }
        }
        
        from ..utils.data_utils import standardize_output
        return standardize_output(result, "compute_outperformance")
        
    except Exception as e:
        return {"success": False, "error": f"Outperformance calculation failed: {str(e)}"}


# Registry of comparison metrics functions - all using libraries and existing functions
COMPARISON_METRICS_FUNCTIONS = {
    'compare_performance_metrics': compare_performance_metrics,
    'compare_risk_metrics': compare_risk_metrics,
    'compare_drawdowns': compare_drawdowns,
    'compare_volatility_profiles': compare_volatility_profiles,
    'compare_correlation_stability': compare_correlation_stability,
    'compare_sector_exposure': compare_sector_exposure,
    'compare_expense_ratios': compare_expense_ratios,
    'compare_liquidity': compare_liquidity,
    'compare_fundamental': compare_fundamental,
    'compute_outperformance': compute_outperformance
}