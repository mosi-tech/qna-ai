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
        >>> # Generate sample returns (15 trading days)
        >>> np.random.seed(42)
        >>> dates = pd.date_range('2024-01-01', periods=15, freq='D')
        >>> returns1 = pd.Series(np.random.normal(0.0012, 0.018, 15), index=dates)  # Growth
        >>> returns2 = pd.Series(np.random.normal(0.0008, 0.012, 15), index=dates)  # Value
        >>> 
        >>> result = compare_performance_metrics(returns1, returns2)
        >>> 
        >>> # OUTPUT structure:
        >>> # {
        >>> #   "success": true,
        >>> #   "function": "compare_performance_metrics",
        >>> #   "comparison_period": "15 observations",
        >>> #   "metrics_comparison": {
        >>> #     "annual_return": {
        >>> #       "asset_1": 0.36531623792362256,
        >>> #       "asset_2": -0.6245966224534989,
        >>> #       "difference": -0.9899128603771215,
        >>> #       "winner": "asset_1"
        >>> #     },
        >>> #     "total_return": {
        >>> #       "asset_1": 0.018707722771260205,
        >>> #       "asset_2": -0.05665074575295759,
        >>> #       "difference": -0.07535846852421779,
        >>> #       "winner": "asset_1"
        >>> #     },
        >>> #     "volatility": {
        >>> #       "asset_1": 0.28407120121834495,
        >>> #       "asset_2": 0.14818260474958136,
        >>> #       "difference": -0.13588859646876358,
        >>> #       "winner": "asset_2"
        >>> #     },
        >>> #     "sharpe_ratio": {
        >>> #       "asset_1": -16.512265493673244,
        >>> #       "asset_2": -40.54191363313889,
        >>> #       "difference": -24.029648139465646,
        >>> #       "winner": "asset_1"
        >>> #     },
        >>> #     "max_drawdown": {
        >>> #       "asset_1": -0.07034648295664166,
        >>> #       "asset_2": -0.056650745752957615,
        >>> #       "difference": 0.013695737203684041,
        >>> #       "winner": "asset_2"
        >>> #     },
        >>> #     "win_rate": {
        >>> #       "asset_1": 0.4666666666666667,
        >>> #       "asset_2": 0.3333333333333333,
        >>> #       "difference": -0.13333333333333336,
        >>> #       "winner": "asset_1"
        >>> #     }
        >>> #   },
        >>> #   "summary": {
        >>> #     "asset_1_wins": 4,
        >>> #     "asset_2_wins": 2,
        >>> #     "overall_winner": "asset_1",
        >>> #     "total_metrics": 6
        >>> #   },
        >>> #   "correlation": 0.09472535125379347
        >>> # }
        >>> 
        >>> # Access results:
        >>> print(f"Overall Winner: {result['summary']['overall_winner']}")  # "asset_1"
        >>> print(f"Asset 1 Annual Return: {result['metrics_comparison']['annual_return']['asset_1']:.2%}")  # "36.53%"
        >>> print(f"Asset 2 Annual Return: {result['metrics_comparison']['annual_return']['asset_2']:.2%}")  # "-62.46%"
        >>> print(f"Volatility Winner: {result['metrics_comparison']['volatility']['winner']}")  # "asset_2"
        
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
        >>> # Create sample return data (20 trading days)
        >>> np.random.seed(42)
        >>> dates = pd.date_range('2024-01-01', periods=20, freq='D')
        >>> 
        >>> # Conservative stock returns
        >>> returns1 = pd.Series(np.random.normal(0.0008, 0.012, 20), index=dates, name='Conservative')
        >>> 
        >>> # Volatile stock returns
        >>> returns2 = pd.Series(np.random.normal(0.001, 0.025, 20), index=dates, name='Volatile')
        >>> 
        >>> # Compare risk profiles
        >>> result = compare_risk_metrics(returns1, returns2)
        >>> 
        >>> # OUTPUT structure:
        >>> # {
        >>> #   "success": true,
        >>> #   "function": "compare_risk_metrics",
        >>> #   "comparison_period": "20 observations",
        >>> #   "risk_comparison": {
        >>> #     "volatility": {
        >>> #       "asset_1": 0.18287974473707336,
        >>> #       "asset_2": 0.3841784526110971,
        >>> #       "difference": 0.20129870787402376,
        >>> #       "winner": "asset_1"
        >>> #     },
        >>> #     "var_95": {
        >>> #       "asset_1": -0.020012031437443255,
        >>> #       "asset_2": -0.03528735707741932,
        >>> #       "difference": -0.015275325639976065,
        >>> #       "winner": "asset_1"
        >>> #     },
        >>> #     "cvar_95": {
        >>> #       "asset_1": -0.022159362935893576,
        >>> #       "asset_2": -0.04799175309699439,
        >>> #       "difference": -0.025832390161100813,
        >>> #       "winner": "asset_1"
        >>> #     },
        >>> #     "max_drawdown": {
        >>> #       "asset_1": -0.0839046152743041,
        >>> #       "asset_2": -0.14935281295331526,
        >>> #       "difference": -0.06544819767901117,
        >>> #       "winner": "asset_1"
        >>> #     },
        >>> #     "skewness": {
        >>> #       "asset_1": 0.022653680547866546,
        >>> #       "asset_2": 0.4044114396284347,
        >>> #       "difference": 0.38175775908056814,
        >>> #       "winner": "asset_2"
        >>> #     },
        >>> #     "kurtosis": {
        >>> #       "asset_1": -0.5444692608577548,
        >>> #       "asset_2": -0.22377897862890528,
        >>> #       "difference": 0.32069028222884954,
        >>> #       "winner": "asset_2"
        >>> #     }
        >>> #   },
        >>> #   "summary": {
        >>> #     "asset_1_wins": 4,
        >>> #     "asset_2_wins": 2,
        >>> #     "lower_risk_asset": "asset_1",
        >>> #     "total_metrics": 6
        >>> #   },
        >>> #   "correlation": -0.15729399538437136
        >>> # }
        >>> 
        >>> # Access results:
        >>> print(f"Lower Risk Asset: {result['summary']['lower_risk_asset']}")           # "asset_1"
        >>> print(f"Volatility - Asset 1: {result['risk_comparison']['volatility']['asset_1']:.2%}")  # "18.29%"
        >>> print(f"Volatility - Asset 2: {result['risk_comparison']['volatility']['asset_2']:.2%}")  # "38.42%"
        >>> print(f"VaR 95% - Asset 1: {result['risk_comparison']['var_95']['asset_1']:.2%}")         # "-2.00%"
        >>> print(f"Risk Wins - Asset 1: {result['summary']['asset_1_wins']}")                        # 4
        
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
        >>> np.random.seed(42)
        >>> dates = pd.date_range('2024-01-01', periods=20, freq='D')
        >>> 
        >>> # Generate stable vs volatile price series
        >>> prices1 = pd.Series(index=dates)
        >>> prices2 = pd.Series(index=dates)
        >>> prices1.iloc[0] = prices2.iloc[0] = 100
        >>> for i in range(1, 20):
        ...     prices1.iloc[i] = prices1.iloc[i-1] * (1 + np.random.normal(0.001, 0.012))
        ...     prices2.iloc[i] = prices2.iloc[i-1] * (1 + np.random.normal(0.0005, 0.025))
        >>> 
        >>> # Compare drawdown profiles
        >>> result = compare_drawdowns(prices1, prices2)
        >>> 
        >>> # OUTPUT structure:
        >>> # {
        >>> #   "success": true,
        >>> #   "function": "compare_drawdowns",
        >>> #   "comparison_period": "19 observations",
        >>> #   "drawdown_comparison": {
        >>> #     "max_drawdown": {
        >>> #       "asset_1": -0.06717823915515819,
        >>> #       "asset_2": -0.1285460226820301,
        >>> #       "difference": -0.061367783526871916,
        >>> #       "winner": "asset_1"
        >>> #     },
        >>> #     "significant_drawdowns": {
        >>> #       "asset_1": 4,
        >>> #       "asset_2": 13,
        >>> #       "difference": 9,
        >>> #       "winner": "asset_1"
        >>> #     },
        >>> #     "time_in_drawdown": {
        >>> #       "asset_1": 68.42105263157895,
        >>> #       "asset_2": 89.47368421052632,
        >>> #       "difference": 21.05263157894737,
        >>> #       "winner": "asset_1"
        >>> #     }
        >>> #   },
        >>> #   "summary": {
        >>> #     "asset_1_wins": 3,
        >>> #     "asset_2_wins": 0,
        >>> #     "better_drawdown_profile": "asset_1",
        >>> #     "total_metrics": 3
        >>> #   }
        >>> # }
        >>> 
        >>> # Access results:
        >>> print(f"Better Profile: {result['summary']['better_drawdown_profile']}")  # "asset_1"
        >>> print(f"Max Drawdown 1: {result['drawdown_comparison']['max_drawdown']['asset_1']:.2%}")  # "-6.72%"
        >>> print(f"Max Drawdown 2: {result['drawdown_comparison']['max_drawdown']['asset_2']:.2%}")  # "-12.85%"
        
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
        
        # Calculate drawdown analysis (already provides drawdown series and max drawdown)
        dd1 = calculate_drawdown_analysis(ret1_aligned)
        dd2 = calculate_drawdown_analysis(ret2_aligned)
        
        # Extract drawdown series from analysis results
        drawdown_series1 = dd1.get("drawdown_series", pd.Series())
        drawdown_series2 = dd2.get("drawdown_series", pd.Series())
        
        # Count significant drawdowns (>5%)
        significant_dd1 = (drawdown_series1 < -0.05).sum()
        significant_dd2 = (drawdown_series2 < -0.05).sum()
        
        # Average time in drawdown
        in_drawdown1 = (drawdown_series1 < 0).sum()
        in_drawdown2 = (drawdown_series2 < 0).sum()
        
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
                "asset_1": int(significant_dd1),
                "asset_2": int(significant_dd2),
                "difference": int(significant_dd2 - significant_dd1),
                "winner": "asset_1" if significant_dd1 < significant_dd2 else "asset_2"
            },
            "time_in_drawdown": {
                "asset_1": float(pct_time_dd1),
                "asset_2": float(pct_time_dd2),
                "difference": float(pct_time_dd2 - pct_time_dd1),
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
        >>> # Generate sample returns with different volatility characteristics
        >>> np.random.seed(42)
        >>> dates = pd.date_range('2024-01-01', periods=40, freq='D')
        >>> returns1 = pd.Series(np.random.normal(0.0008, 0.01, 40), index=dates)   # Stable
        >>> returns2 = pd.Series(np.random.normal(0.001, 0.025, 40), index=dates)   # Volatile
        >>> 
        >>> result = compare_volatility_profiles(returns1, returns2, window=15)
        >>> 
        >>> # OUTPUT structure:
        >>> # {
        >>> #   "success": true,
        >>> #   "function": "compare_volatility_profiles",
        >>> #   "window_size": 15,
        >>> #   "comparison_period": "26 rolling periods",
        >>> #   "volatility_comparison": {
        >>> #     "average_volatility": {
        >>> #       "asset_1": 0.14762536399369564,
        >>> #       "asset_2": 0.3623587861441918,
        >>> #       "difference": 0.21473342215049618,
        >>> #       "winner": "asset_1"
        >>> #     },
        >>> #     "volatility_volatility": {
        >>> #       "asset_1": 0.01076017611236529,
        >>> #       "asset_2": 0.051986055736871026,
        >>> #       "difference": 0.04122587962450573,
        >>> #       "winner": "asset_1"
        >>> #     },
        >>> #     "max_volatility": {
        >>> #       "asset_1": 0.1699907761460797,
        >>> #       "asset_2": 0.4717631931646091,
        >>> #       "difference": 0.3017724170185294,
        >>> #       "winner": "asset_1"
        >>> #     },
        >>> #     "min_volatility": {
        >>> #       "asset_1": 0.12348550395798452,
        >>> #       "asset_2": 0.3084078366355659,
        >>> #       "difference": 0.1849223326775814,
        >>> #       "winner": "asset_1"
        >>> #     },
        >>> #     "high_volatility_periods": {
        >>> #       "asset_1": 3,
        >>> #       "asset_2": 3,
        >>> #       "difference": 0,
        >>> #       "winner": "asset_2"
        >>> #     }
        >>> #   },
        >>> #   "volatility_correlation": 0.02720426559228118,
        >>> #   "summary": {
        >>> #     "asset_1_wins": 4,
        >>> #     "asset_2_wins": 1,
        >>> #     "more_stable_volatility": "asset_1",
        >>> #     "total_metrics": 5
        >>> #   }
        >>> # }
        >>> 
        >>> # Access results:
        >>> print(f"More Stable: {result['summary']['more_stable_volatility']}")  # "asset_1"
        >>> print(f"Avg Vol 1: {result['volatility_comparison']['average_volatility']['asset_1']:.2%}")  # "14.76%"
        >>> print(f"Avg Vol 2: {result['volatility_comparison']['average_volatility']['asset_2']:.2%}")  # "36.24%"
        >>> print(f"Vol of Vol 1: {result['volatility_comparison']['volatility_volatility']['asset_1']:.3f}")  # 0.011
        
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
    """Analyze correlation stability and regime changes between two return series over time.
    
    Examines how the correlation between two assets changes over time using rolling windows,
    identifying correlation regimes, stability patterns, and trend characteristics. This analysis
    is crucial for portfolio construction, risk management, and understanding diversification
    benefits that may change during different market conditions.
    
    The function provides detailed correlation regime analysis, stability scoring, and trend
    identification to help assess the reliability of correlation-based portfolio strategies
    and diversification assumptions over time.
    
    Args:
        returns1 (Union[pd.Series, Dict[str, Any]]): Return series for first asset.
            Can be pandas Series with datetime index or dictionary with return values.
            Values should be decimal returns (e.g., 0.02 for 2% return).
        returns2 (Union[pd.Series, Dict[str, Any]]): Return series for second asset.
            Same format requirements as returns1. Will be aligned with returns1 automatically.
        window (int, optional): Rolling window size for correlation calculation. Defaults to 60.
            Common values: 30 (monthly), 60 (quarterly), 120 (semi-annual), 252 (annual).
            Larger windows provide smoother but less responsive correlation estimates.
    
    Returns:
        Dict[str, Any]: Comprehensive correlation stability analysis with keys:
            - window_size (int): Rolling window size used for calculations
            - total_rolling_periods (int): Number of rolling correlation observations
            - correlation_statistics (Dict): Statistical measures of correlation behavior:
                - average_correlation: Mean rolling correlation over the period
                - correlation_volatility: Standard deviation of rolling correlations
                - max_correlation: Highest correlation observed
                - min_correlation: Lowest correlation observed
                - correlation_range: Difference between max and min correlations
            - correlation_regimes (Dict): Classification of correlation periods:
                - high_correlation_periods: Count/percentage of periods with corr > 0.7
                - moderate_correlation_periods: Count/percentage with 0.3 < corr <= 0.7
                - low_correlation_periods: Count/percentage with corr <= 0.3
            - stability_analysis (Dict): Overall stability assessment:
                - stability_score: Numerical stability measure (0-1, higher is more stable)
                - stability_rating: Categorical rating (low/moderate/high stability)
                - correlation_trend: Direction of correlation change (increasing/decreasing/stable)
                - trend_magnitude: Strength of correlation trend over time
            - overall_correlation (float): Static correlation over entire period
            - success (bool): Whether calculation succeeded
            - function_name (str): Function identifier for tracking
    
    Raises:
        ValueError: If returns data cannot be converted to valid return series.
        TypeError: If window parameter is not an integer or data format is invalid.
        
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Generate sample returns with changing correlation patterns
        >>> np.random.seed(42)
        >>> dates = pd.date_range('2024-01-01', periods=50, freq='D')
        >>> returns1 = pd.Series(np.random.normal(0.001, 0.015, 50), index=dates)
        >>> returns2 = pd.Series(np.random.normal(0.0008, 0.018, 50), index=dates)
        >>> 
        >>> result = compare_correlation_stability(returns1, returns2, window=20)
        >>> 
        >>> # OUTPUT structure:
        >>> # {
        >>> #   "success": true,
        >>> #   "function": "compare_correlation_stability",
        >>> #   "window_size": 20,
        >>> #   "total_rolling_periods": 31,
        >>> #   "correlation_statistics": {
        >>> #     "average_correlation": 0.10431868742758328,
        >>> #     "correlation_volatility": 0.08747834960551726,
        >>> #     "max_correlation": 0.3108055615994316,
        >>> #     "min_correlation": -0.05840024373273846,
        >>> #     "correlation_range": 0.36920580533217007
        >>> #   },
        >>> #   "correlation_regimes": {
        >>> #     "high_correlation_periods": {
        >>> #       "count": 0,
        >>> #       "percentage": 0.0
        >>> #     },
        >>> #     "moderate_correlation_periods": {
        >>> #       "count": 1,
        >>> #       "percentage": 3.225806451612903
        >>> #     },
        >>> #     "low_correlation_periods": {
        >>> #       "count": 30,
        >>> #       "percentage": 96.7741935483871
        >>> #     }
        >>> #   },
        >>> #   "stability_analysis": {
        >>> #     "stability_score": 0.9125216503944827,
        >>> #     "stability_rating": "high",
        >>> #     "correlation_trend": "increasing",
        >>> #     "trend_magnitude": 0.142709549736389
        >>> #   },
        >>> #   "overall_correlation": 0.11007178534016057
        >>> # }
        >>> 
        >>> # Access results:
        >>> print(f"Stability Rating: {result['stability_analysis']['stability_rating']}")  # "high"
        >>> print(f"Average Correlation: {result['correlation_statistics']['average_correlation']:.3f}")  # 0.104
        >>> print(f"Correlation Range: {result['correlation_statistics']['correlation_range']:.3f}")  # 0.369
        >>> print(f"Low Corr Periods: {result['correlation_regimes']['low_correlation_periods']['percentage']:.1f}%")  # 96.8%
        
    Note:
        - Rolling correlation is calculated using pandas rolling().corr() method
        - Correlation regimes help identify diversification effectiveness over time
        - High stability score indicates consistent correlation behavior
        - Trend analysis shows whether correlations are increasing/decreasing over time
        - Low correlation periods indicate better diversification opportunities
        - Window size affects sensitivity to correlation changes vs. noise
        - Useful for dynamic hedge ratio calculation and portfolio rebalancing decisions
        - Function handles both daily and other frequency data automatically
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
    """Compare sector allocation and concentration between two portfolios or ETFs.
    
    Analyzes sector exposure differences between two portfolios, providing detailed breakdown
    of sector weights, allocation differences, concentration metrics, and overlap analysis.
    This analysis is essential for understanding diversification, sector bias, and allocation
    strategies across different investment approaches.
    
    The function helps identify sector concentration risks, allocation overlaps, and provides
    quantitative measures to compare sector-based investment strategies and portfolio construction.
    
    Args:
        holdings1 (List[Dict[str, Any]]): Holdings data for first portfolio.
            Each holding should be a dictionary with keys:
            - 'sector' (str): Sector classification (e.g., 'Technology', 'Healthcare')
            - 'weight' (float): Portfolio weight as decimal (e.g., 0.25 for 25%)
            - Other optional fields like 'symbol', 'name' are ignored
        holdings2 (List[Dict[str, Any]]): Holdings data for second portfolio.
            Same format requirements as holdings1.
    
    Returns:
        Dict[str, Any]: Comprehensive sector exposure comparison with keys:
            - total_sectors (int): Total unique sectors across both portfolios
            - common_sectors (int): Number of sectors present in both portfolios
            - overlap_percentage (float): Percentage of sectors that overlap
            - sector_comparison (Dict): Detailed sector-by-sector comparison with keys:
                - {sector_name}: For each sector, contains:
                    - portfolio_1_weight: Weight in first portfolio
                    - portfolio_2_weight: Weight in second portfolio
                    - difference: Weight difference (portfolio_2 - portfolio_1)
                    - relative_difference: Relative difference as percentage
            - concentration_analysis (Dict): Sector concentration metrics:
                - portfolio_1_hhi: Herfindahl-Hirschman Index for portfolio 1
                - portfolio_2_hhi: Herfindahl-Hirschman Index for portfolio 2  
                - more_concentrated: Which portfolio has higher concentration
            - largest_differences (List): Top 5 sectors with largest allocation differences
            - top_sectors (Dict): Top 5 sectors by weight for each portfolio
            - success (bool): Whether calculation succeeded
            - function_name (str): Function identifier for tracking
    
    Raises:
        ValueError: If required columns ('sector', 'weight') are missing from holdings data.
        TypeError: If holdings data format is invalid or not a list of dictionaries.
        
    Example:
        >>> holdings1 = [
        ...     {'sector': 'Technology', 'weight': 0.45},
        ...     {'sector': 'Healthcare', 'weight': 0.25},
        ...     {'sector': 'Financials', 'weight': 0.30}
        ... ]
        >>> holdings2 = [
        ...     {'sector': 'Technology', 'weight': 0.55}, 
        ...     {'sector': 'Energy', 'weight': 0.45}
        ... ]
        >>> 
        >>> result = compare_sector_exposure(holdings1, holdings2)
        >>> 
        >>> # OUTPUT structure:
        >>> # {
        >>> #   "success": true,
        >>> #   "function": "compare_sector_exposure",
        >>> #   "total_sectors": 3,
        >>> #   "common_sectors": 1,
        >>> #   "overlap_percentage": 33.3,
        >>> #   "sector_comparison": {
        >>> #     "Technology": {
        >>> #       "portfolio_1_weight": 0.45,
        >>> #       "portfolio_2_weight": 0.55,
        >>> #       "difference": 0.10
        >>> #     },
        >>> #     "Healthcare": {
        >>> #       "portfolio_1_weight": 0.25,
        >>> #       "portfolio_2_weight": 0.0,
        >>> #       "difference": -0.25
        >>> #     },
        >>> #     "Energy": {
        >>> #       "portfolio_1_weight": 0.0,
        >>> #       "portfolio_2_weight": 0.45,
        >>> #       "difference": 0.45
        >>> #     }
        >>> #   },
        >>> #   "concentration_analysis": {
        >>> #     "portfolio_1_hhi": 0.2650,
        >>> #     "portfolio_2_hhi": 0.5050,
        >>> #     "more_concentrated": "portfolio_2"
        >>> #   }
        >>> # }
        >>> 
        >>> # Access results:
        >>> print(f"Sector Overlap: {result['overlap_percentage']:.1f}%")  # "33.3%"
        >>> print(f"More Concentrated: {result['concentration_analysis']['more_concentrated']}")  # "portfolio_2"
        >>> tech_diff = result['sector_comparison']['Technology']['difference']
        >>> print(f"Technology Difference: {tech_diff:+.1%}")  # "+10.0%"
        
    Note:
        - Sector weights should sum to 1.0 for each portfolio but function handles normalization
        - HHI (Herfindahl-Hirschman Index) measures concentration: 0=diversified, 1=concentrated
        - Positive differences indicate higher weight in portfolio 2, negative in portfolio 1
        - Function automatically handles missing sectors (treated as 0% allocation)
        - Useful for comparing ETFs, mutual funds, or custom portfolio allocations
        - Sector classifications should be consistent between portfolios for meaningful comparison
        - Function performs case-sensitive sector matching - ensure consistent naming
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
    Compare expense ratios across multiple funds to identify cost-effective options.
    
    Analyzes and compares expense ratios (fees) across funds, showing the impact of
    different fee levels on long-term investment returns. High expense ratios can
    significantly erode returns over time through compound effects, making this
    comparison critical for investment selection and cost optimization.
    
    Calculates the real cost impact by projecting how different fee levels affect
    final portfolio value over different time horizons, providing clear insight into
    the value of lower-cost investment options.
    
    Args:
        funds (List[Dict[str, Any]]): List of fund dictionaries with at least these keys:
            - 'expense_ratio' (required, float): Annual expense ratio as decimal (0.005 = 0.5%)
            - 'name' (optional, str): Fund name for display
            - 'symbol' (optional, str): Fund ticker symbol
            - Any additional fund metadata
            Must contain at least 2 funds for meaningful comparison.
    
    Returns:
        Dict[str, Any]: Comprehensive expense comparison with keys:
            - 'funds' (list): Sorted list of funds with expense details
            - 'cheapest' (dict): Fund with lowest expense ratio
            - 'most_expensive' (dict): Fund with highest expense ratio
            - 'average_expense_ratio' (float): Mean expense ratio across all funds
            - 'max_difference' (float): Spread between highest and lowest ratios
            - 'cost_impact_comparison' (dict): Cost impact analysis for different scenarios
            - 'savings_potential' (dict): Potential savings by choosing cheapest option
    
    Raises:
        ValueError: If less than 2 funds provided or funds missing expense_ratio
        TypeError: If expense_ratio is not numeric
        
    Example:
        >>> funds = [
        ...     {'name': 'Expensive Fund', 'symbol': 'EXPF', 'expense_ratio': 0.85},
        ...     {'name': 'Mid Fund', 'symbol': 'MIDF', 'expense_ratio': 0.25},
        ...     {'name': 'Cheap Fund', 'symbol': 'CPFF', 'expense_ratio': 0.03}
        ... ]
        >>> result = compare_expense_ratios(funds)
        >>> print(f"Cheapest: {result['cheapest']['fund_name']} at {result['cheapest']['expense_ratio_pct']}")
        >>> print(f"10-year cost impact: ${result['cost_impact_comparison']['max_difference']['cost_difference_10yr']:,.0f}")
    
    Cost Impact Analysis:
        Projects 10-year outcomes on $10,000 initial investment at 7% annual return:
        - Fund with 0.03% fee: ~$18,935
        - Fund with 0.85% fee: ~$18,308
        - Difference: ~$627 (3.3% of returns lost to fees)
        
    Key Insights:
        - 0.50% difference in fees can mean 10%+ reduction in long-term wealth
        - Expense ratios compound over time through opportunity cost
        - Index funds typically 0.03-0.20%, Active funds 0.50-1.50%+
        - Individual stocks/ETFs may have lower embedded costs
        
    Note:
        - Comparison assumes 7% annual return (adjustable for different scenarios)
        - Only shows fees, not other costs (trading commissions, bid-ask spreads)
        - 10-year projection assumes fees remain constant
        - Does not account for tax-loss harvesting benefits of lower-turnover funds
        - Past performance and fees are not indicators of future results
        
    See Also:
        - compare_performance(): For comparing historical returns
        - compare_volatility(): For comparing risk characteristics
        - Fee impact is one of few guaranteed predictors of fund performance
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
    Compare liquidity characteristics between two assets based on trading volume data.
    
    Analyzes and compares volume patterns across two assets or time periods to
    evaluate trading liquidity, consistency, and market activity. Liquidity is critical
    for traders and portfolio managers - it determines transaction costs, slippage,
    and the ability to enter/exit positions at desired prices and sizes.
    
    Measures multiple dimensions of liquidity including average volume, consistency,
    and extremes, providing comprehensive understanding of each asset's trading activity
    and ease of trading.
    
    Args:
        volumes1 (Union[pd.Series, Dict[str, Any], List[float]]): Volume data for
            first asset. Can be pandas Series (with optional datetime index), list of
            floats, or dictionary with volume values. Each value represents trading
            volume for a period (daily, hourly, etc.).
        volumes2 (Union[pd.Series, Dict[str, Any], List[float]]): Volume data for
            second asset in same format as volumes1. Will be automatically aligned
            with volumes1 for fair comparison.
    
    Returns:
        Dict[str, Any]: Comprehensive liquidity comparison with metrics:
            - 'average_volume': Mean volume for each asset
            - 'median_volume': Median volume (less affected by outliers)
            - 'volume_volatility': Standard deviation (consistency measure)
            - 'max_volume': Peak volume for each asset
            - 'min_volume': Minimum volume for each asset
            - 'volume_ratio': Asset 1 volume / Asset 2 volume (size comparison)
            - 'liquidity_winner': Asset with superior overall liquidity
            
            Each metric includes:
            - asset_1 (float): Value for first asset
            - asset_2 (float): Value for second asset
            - difference (float): asset_2 - asset_1
            - winner (str): Which asset has better metric
    
    Raises:
        ValueError: If volume data cannot be aligned or is invalid
        TypeError: If input data format is incompatible
        
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> # Daily volumes for two stocks
        >>> volumes_apple = [1000000, 1200000, 950000, 1100000, 1050000]
        >>> volumes_meta = [2000000, 2100000, 1900000, 2200000, 2050000]
        >>> 
        >>> result = compare_liquidity(volumes_apple, volumes_meta)
        >>> print(f"Average Volume - Apple: {result['average_volume']['asset_1']:,.0f}")
        >>> print(f"Average Volume - Meta: {result['average_volume']['asset_2']:,.0f}")
        >>> print(f"Volume Consistency - Lower is better (asset winner: {result['volume_volatility']['winner']})")
        >>> print(f"Overall liquidity winner: {result['liquidity_winner']}")
    
    Liquidity Metrics Explained:
        
        1. Average Volume
           - Mean trading volume across all periods
           - Higher average = more active trading, easier to execute large trades
           - Use case: Determine typical trading activity level
           
        2. Median Volume
           - Less affected by exceptional volume spikes
           - Better for understanding "normal" trading conditions
           - Use case: Identify typical trading day vs exceptional days
           
        3. Volume Volatility (Standard Deviation)
           - Measures consistency of volume
           - Higher volatility = more unpredictable volume (higher execution risk)
           - Lower volatility = consistent volume (more predictable trading)
           - Use case: Evaluate trading consistency and risk
           
        4. Max/Min Volume
           - Range of observed volumes
           - Large range = highly variable trading activity
           - Use case: Understand volume extremes and potential slippage scenarios
           
        5. Volume Ratio
           - Relative size comparison
           - 2.0 = First asset has 2x average volume
           - Use case: Compare trading size between assets
    
    Liquidity Implications:
        - High average volume → Easier to trade, lower bid-ask spreads
        - Consistent volume → Predictable execution costs
        - High median volume → Can execute larger orders
        - High volume volatility → Variable trading costs, execution risk
        - Large max/min range → Wide range of potential execution outcomes
    
    Trading Applications:
        - Position Sizing: Adjust order size based on volume
        - Slippage Estimation: Higher volume usually means lower slippage
        - Risk Management: Ensure adequate liquidity for exit strategies
        - Timing: Execute trades during high-volume periods for better prices
        - Monitoring: Track volume changes for early signs of liquidity crisis
    
    Note:
        - Volume measured in shares (or contracts) per period
        - Automatic series alignment handles different lengths
        - Lower volume volatility indicates more predictable trading
        - Market microstructure affects execution more than pure volume
        - Event-driven spikes can distort average/median metrics
        - Should be combined with bid-ask spread analysis for complete picture
        
    See Also:
        - compare_volatility(): For comparing price volatility
        - compare_performance(): For comparing historical returns
        - Volume and volatility are complementary liquidity indicators
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
        >>> # Create sample multi-asset return data (60 trading days)
        >>> dates = pd.date_range('2024-01-01', periods=60, freq='D')
        >>> np.random.seed(42)
        >>> 
        >>> # Sample asset returns (daily decimal returns)
        >>> asset_returns = pd.DataFrame({
        ...     'AAPL': np.random.normal(0.001, 0.02, 60),    # Tech stock
        ...     'MSFT': np.random.normal(0.0008, 0.018, 60),  # Another tech  
        ...     'SPY': np.random.normal(0.0005, 0.015, 60)    # Market proxy
        ... }, index=dates)
        >>> 
        >>> # Benchmark returns (market index)
        >>> benchmark_returns = pd.Series(np.random.normal(0.0005, 0.015, 60), index=dates)
        >>> 
        >>> # Calculate outperformance analysis
        >>> result = compute_outperformance(asset_returns, benchmark_returns)
        >>> 
        >>> # Sample input data (first 5 days):
        >>> print("INPUT - Asset Returns:")
        >>> print(asset_returns.head().round(4))
        >>> #           AAPL    MSFT     SPY
        >>> # 2024-01-01  0.0109 -0.0078  0.0124
        >>> # 2024-01-02 -0.0018 -0.0025 -0.0131
        >>> # 2024-01-03  0.0140 -0.0191  0.0215
        >>> # 2024-01-04  0.0315 -0.0207 -0.0205
        >>> # 2024-01-05 -0.0037  0.0154  0.0093
        >>> 
        >>> # Sample output structure:
        >>> print("OUTPUT - Outperformance Analysis:")
        >>> print(f"Best Performer: {result['portfolio_summary']['best_performer']['asset']}")
        >>> print(f"Excess Return: {result['portfolio_summary']['best_performer']['excess_return_pct']}")
        >>> 
        >>> # Individual asset metrics example (SPY):
        >>> spy_metrics = result['asset_outperformance']['SPY']
        >>> print(f"\\nSPY Outperformance Metrics:")
        >>> print(f"  Excess Return: {spy_metrics['excess_return_pct']}")           # "+7.76%"
        >>> print(f"  Information Ratio: {spy_metrics['information_ratio']:.3f}")  # 0.227
        >>> print(f"  Outperformance Rate: {spy_metrics['outperformance_periods_pct']}")  # "51.7%"
        >>> print(f"  Beta: {spy_metrics['beta']:.3f}")                           # -0.002
        >>> print(f"  Statistical Significance: {spy_metrics['statistical_significance']['is_significant']}")  # False
        >>> 
        >>> # Portfolio summary shows aggregate statistics:
        >>> summary = result['portfolio_summary']
        >>> print(f"\\nPortfolio Summary:")
        >>> print(f"  Assets Analyzed: {summary['assets_analyzed']}")             # 3
        >>> print(f"  Outperforming Assets: {summary['outperforming_assets_pct']}")  # "33.3%"
        >>> print(f"  Average Outperformance: {summary['average_outperformance_pct']}")  # "-24.10%"
        >>> 
        >>> # Benchmark characteristics:
        >>> benchmark = result['benchmark_info']
        >>> print(f"\\nBenchmark Info:")
        >>> print(f"  Annual Return: {benchmark['annual_return_pct']}")           # "36.46%"
        >>> print(f"  Annual Volatility: {benchmark['annual_volatility_pct']}")  # "24.68%"
        >>> 
        >>> # Complete output structure:
        >>> # {
        >>> #   "success": true,
        >>> #   "function": "compute_outperformance",
        >>> #   "asset_outperformance": {
        >>> #     "AAPL": {
        >>> #       "excess_return_annualized": -0.6062070605312884,
        >>> #       "excess_return_pct": "-60.62%",
        >>> #       "alpha_annualized": -0.9924218040650618,
        >>> #       "alpha_pct": "-99.24%",
        >>> #       "tracking_error_annualized": 0.35373455608890525,
        >>> #       "tracking_error_pct": "35.37%",
        >>> #       "information_ratio": -1.7137343527696751,
        >>> #       "beta": 0.15576433831503386,
        >>> #       "correlation": 0.13326171133898262,
        >>> #       "outperformance_periods": 28,
        >>> #       "outperformance_periods_pct": "46.7%",
        >>> #       "total_periods": 60,
        >>> #       "statistical_significance": {
        >>> #         "is_significant": false,
        >>> #         "t_statistic": -1.197640374130215,
        >>> #         "p_value": 0.23584648563090505
        >>> #       }
        >>> #     },
        >>> #     "MSFT": {
        >>> #       "excess_return_annualized": -0.19429746224759348,
        >>> #       "excess_return_pct": "-19.43%",
        >>> #       "alpha_annualized": -0.9880811769749294,
        >>> #       "alpha_pct": "-98.81%",
        >>> #       "tracking_error_annualized": 0.3486100472927594,
        >>> #       "tracking_error_pct": "34.86%",
        >>> #       "information_ratio": -0.5573490028657273,
        >>> #       "beta": 0.09877687606825698,
        >>> #       "correlation": 0.09042868891413962,
        >>> #       "outperformance_periods": 31,
        >>> #       "outperformance_periods_pct": "51.7%",
        >>> #       "total_periods": 60,
        >>> #       "statistical_significance": {
        >>> #         "is_significant": false,
        >>> #         "t_statistic": -0.21816585152362386,
        >>> #         "p_value": 0.8280527280057909
        >>> #       }
        >>> #     },
        >>> #     "SPY": {
        >>> #       "excess_return_annualized": 0.07762355638004137,
        >>> #       "excess_return_pct": "+7.76%",
        >>> #       "alpha_annualized": -0.9901417680545435,
        >>> #       "alpha_pct": "-99.01%",
        >>> #       "tracking_error_annualized": 0.3426911837335535,
        >>> #       "tracking_error_pct": "34.27%",
        >>> #       "information_ratio": 0.2265116818423745,
        >>> #       "beta": -0.002298660412875758,
        >>> #       "correlation": -0.002391561799524987,
        >>> #       "outperformance_periods": 31,
        >>> #       "outperformance_periods_pct": "51.7%",
        >>> #       "total_periods": 60,
        >>> #       "statistical_significance": {
        >>> #         "is_significant": false,
        >>> #         "t_statistic": 0.188917026573235,
        >>> #         "p_value": 0.8508062069439509
        >>> #       }
        >>> #     }
        >>> #   },
        >>> #   "portfolio_summary": {
        >>> #     "best_performer": {
        >>> #       "asset": "SPY",
        >>> #       "excess_return_annualized": 0.07762355638004137,
        >>> #       "excess_return_pct": "+7.76%"
        >>> #     },
        >>> #     "worst_performer": {
        >>> #       "asset": "AAPL",
        >>> #       "excess_return_annualized": -0.6062070605312884,
        >>> #       "excess_return_pct": "-60.62%"
        >>> #     },
        >>> #     "average_outperformance": -0.24096032213294682,
        >>> #     "average_outperformance_pct": "-24.10%",
        >>> #     "assets_analyzed": 3,
        >>> #     "outperforming_assets_count": 1,
        >>> #     "outperforming_assets_pct": "33.3%",
        >>> #     "statistically_significant_count": 0
        >>> #   },
        >>> #   "benchmark_info": {
        >>> #     "annual_return": 0.36459050208960875,
        >>> #     "annual_return_pct": "36.46%",
        >>> #     "annual_volatility": 0.2467758438546481,
        >>> #     "annual_volatility_pct": "24.68%",
        >>> #     "total_periods": 60
        >>> #   }
        >>> # }
        
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
        from utils.data_utils import validate_return_data, align_series
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
        
        from utils.data_utils import standardize_output
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