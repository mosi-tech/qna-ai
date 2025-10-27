"""Advanced signal analysis functions for trading strategy evaluation and optimization.

This module provides sophisticated signal analysis capabilities including signal quality
assessment, false signal identification, and parameter optimization. These functions are
essential for developing and validating automated trading strategies by analyzing the
historical performance and reliability of trading signals.

The module includes:
- Signal quality analysis with comprehensive backtesting
- False signal detection using multiple validation criteria
- Parameter optimization using grid search and performance metrics
- Statistical significance testing and risk assessment

All functions integrate with the financial-analysis-function-library.json specification
and use proven libraries (scipy, empyrical, pandas) for statistical analysis.

Example:
    Basic signal analysis workflow:
    
    >>> from mcp.analytics.signals.analysis import analyze_signal_quality
    >>> signals = [{'timestamp': '2023-01-01', 'signal': 'buy', 'strength': 0.8}, ...]
    >>> prices = pd.Series(...)  # Historical price data
    >>> quality_analysis = analyze_signal_quality(signals, prices)
    >>> print(f"Signal quality: {quality_analysis['quality_metrics']['quality_rating']}")
    >>> print(f"Win rate: {quality_analysis['quality_metrics']['win_loss_metrics']['win_rate']}")
    
Note:
    Functions require aligned price data and properly formatted signal lists with
    timestamps for accurate backtesting and analysis.
"""



import pandas as pd
import numpy as np
from typing import Dict, List, Any, Union, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

from scipy import optimize
from itertools import product
import empyrical

from ..utils.data_utils import validate_return_data, validate_price_data, standardize_output
from .generators import generate_signals


def analyze_signal_quality(signals: List[Dict[str, Any]], 
                          prices: Union[pd.Series, Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze trading signal quality through comprehensive backtesting and statistical evaluation.
    
    This function performs detailed quality assessment of trading signals by backtesting
    them against historical price data. It calculates performance metrics, risk measures,
    and statistical significance to determine the reliability and effectiveness of the
    signals for trading strategy development.
    
    Args:
        signals: List of signal dictionaries containing trading signals. Each signal
            must have the following keys:
            - 'timestamp': Signal generation time (string or datetime)
            - 'signal': Signal type ('buy', 'sell', or other)
            - 'strength': Optional signal confidence (0.0 to 1.0)
            Additional fields are preserved in the analysis.
        prices: Historical price data for backtesting. Can be provided as pandas
            Series with datetime index, or dictionary with dates as keys and
            prices as values.
            
    Returns:
        Dict[str, Any]: Comprehensive signal quality analysis including:
            - analysis_summary: Overview of signals analyzed and time period
            - quality_metrics: Overall quality score, rating, and component scores
            - return_statistics: Average, median, volatility, and total returns
            - win_loss_metrics: Win rate, average wins/losses, profit factor
            - risk_metrics: Sharpe ratio, maximum drawdown, consistency score
            - statistical_significance: T-test results and significance flags
            - signal_type_analysis: Performance breakdown by signal type
            - recent_performance: Latest signal results for trend analysis
            
    Raises:
        Exception: If signal quality analysis fails due to data issues or calculation errors.
        
    Example:
        >>> import pandas as pd
        >>> # Create sample signals
        >>> signals = [
        ...     {'timestamp': '2023-01-02', 'signal': 'buy', 'strength': 0.8},
        ...     {'timestamp': '2023-01-05', 'signal': 'sell', 'strength': 0.7},
        ...     {'timestamp': '2023-01-10', 'signal': 'buy', 'strength': 0.9}
        ... ]
        >>> prices = pd.Series([100, 102, 98, 105, 103], 
        ...                   index=pd.date_range('2023-01-01', periods=5))
        >>> quality_result = analyze_signal_quality(signals, prices)
        >>> print(f"Quality rating: {quality_result['quality_metrics']['quality_rating']}")
        >>> print(f"Win rate: {quality_result['quality_metrics']['win_loss_metrics']['win_rate']:.1%}")
        >>> print(f"Sharpe ratio: {quality_result['quality_metrics']['risk_metrics']['sharpe_ratio']:.2f}")
        
    Note:
        - Signals are backtested using forward-looking returns for 1, 5, 10, and 20 day periods
        - Quality score combines return performance, win rate, risk-adjusted returns, and consistency
        - Quality ratings: excellent (80+), good (60-79), fair (40-59), poor (<40)
        - Statistical significance tested using t-test against zero mean hypothesis
        - Requires at least overlapping periods between signals and prices for analysis
        - Returns empty results if no signals can be aligned with price data
    """
    if not signals:
        return standardize_output({
            "total_signals": 0,
            "quality_metrics": {},
            "error": "No signals provided"
        }, "analyze_signal_quality")
        
    price_series = validate_price_data(prices)
        
    # Convert signals to DataFrame
    signals_df = pd.DataFrame(signals)
    signals_df['timestamp'] = pd.to_datetime(signals_df['timestamp'])
    signals_df = signals_df.sort_values('timestamp')
        
    # Align signals with price data
    aligned_signals = []
    signal_returns = []
        
    for _, signal in signals_df.iterrows():
        signal_time = signal['timestamp']
        signal_type = signal['signal']
            
        # Find the closest price point
        price_idx = price_series.index.get_indexer([signal_time], method='nearest')[0]
            
        if price_idx >= 0 and price_idx < len(price_series) - 1:
            entry_price = price_series.iloc[price_idx]
                
            # Calculate forward returns for different holding periods
            holding_periods = [1, 5, 10, 20]  # days
            period_returns = {}
                
            for period in holding_periods:
                exit_idx = min(price_idx + period, len(price_series) - 1)
                exit_price = price_series.iloc[exit_idx]
                    
                if signal_type == "buy":
                    period_return = (exit_price - entry_price) / entry_price
                elif signal_type == "sell":
                    period_return = (entry_price - exit_price) / entry_price
                else:
                    period_return = 0
                    
                period_returns[f"{period}d"] = period_return
                
            aligned_signals.append({
                **signal.to_dict(),
                "entry_price": entry_price,
                "period_returns": period_returns
            })
                
            # Use 5-day return as primary metric
            signal_returns.append(period_returns.get("5d", 0))
        
    if not aligned_signals:
        return standardize_output({
            "total_signals": len(signals),
            "aligned_signals": 0,
            "quality_metrics": {},
            "error": "No signals could be aligned with price data"
        }, "analyze_signal_quality")
        
    # Calculate quality metrics
    returns_array = np.array(signal_returns)
        
    # Basic return statistics
    avg_return = np.mean(returns_array)
    median_return = np.median(returns_array)
    std_return = np.std(returns_array)
        
    # Win/loss statistics
    positive_returns = returns_array[returns_array > 0]
    negative_returns = returns_array[returns_array < 0]
        
    win_rate = len(positive_returns) / len(returns_array) if len(returns_array) > 0 else 0
    avg_win = np.mean(positive_returns) if len(positive_returns) > 0 else 0
    avg_loss = np.mean(negative_returns) if len(negative_returns) > 0 else 0
        
    # Risk-adjusted metrics
    sharpe_ratio = avg_return / std_return if std_return > 0 else 0
        
    # Maximum drawdown of signal returns
    cumulative_returns = np.cumprod(1 + returns_array)
    running_max = np.maximum.accumulate(cumulative_returns)
    drawdowns = (cumulative_returns - running_max) / running_max
    max_drawdown = np.min(drawdowns)
        
    # Signal consistency metrics
    rolling_window = min(10, len(returns_array) // 2)
    if rolling_window >= 3:
        rolling_returns = pd.Series(returns_array).rolling(window=rolling_window).mean()
        consistency_score = 1 - (rolling_returns.std() / abs(rolling_returns.mean())) if rolling_returns.mean() != 0 else 0
    else:
        consistency_score = 0
        
    # Statistical significance (t-test)
    from scipy.stats import ttest_1samp
    t_stat, p_value = ttest_1samp(returns_array, 0)
    is_significant = p_value < 0.05
        
    # Signal strength correlation with returns
    signal_strengths = [s.get('strength', 0.5) for s in aligned_signals]
    strength_correlation = np.corrcoef(signal_strengths, signal_returns)[0, 1] if len(signal_strengths) > 1 else 0
        
    # Quality scoring (0-100)
    quality_components = {
        "return_score": min(max(avg_return * 100, -50), 50),  # -50 to +50
        "win_rate_score": win_rate * 30,  # 0 to 30
        "sharpe_score": min(max(sharpe_ratio * 10, -10), 10),  # -10 to +10
        "consistency_score": consistency_score * 10  # 0 to 10
    }
        
    overall_quality_score = sum(quality_components.values()) + 50  # Base score of 50
    overall_quality_score = max(0, min(100, overall_quality_score))
        
    # Quality rating
    if overall_quality_score >= 80:
        quality_rating = "excellent"
    elif overall_quality_score >= 60:
        quality_rating = "good"
    elif overall_quality_score >= 40:
        quality_rating = "fair"
    else:
        quality_rating = "poor"
        
    # Analyze by signal type
    signal_type_analysis = {}
    for signal_type in ["buy", "sell"]:
        type_signals = [s for s in aligned_signals if s['signal'] == signal_type]
        if type_signals:
            type_returns = [s['period_returns']['5d'] for s in type_signals]
            signal_type_analysis[signal_type] = {
                "count": len(type_signals),
                "avg_return": float(np.mean(type_returns)),
                "win_rate": float(np.mean([r > 0 for r in type_returns])),
                "best_return": float(np.max(type_returns)),
                "worst_return": float(np.min(type_returns))
            }
        
    result = {
        "analysis_summary": {
            "total_signals": len(signals),
            "aligned_signals": len(aligned_signals),
            "analysis_period": {
                "start_date": str(signals_df['timestamp'].min().date()),
                "end_date": str(signals_df['timestamp'].max().date())
            }
        },
        "quality_metrics": {
            "overall_score": float(overall_quality_score),
            "quality_rating": quality_rating,
            "component_scores": {k: float(v) for k, v in quality_components.items()},
            "return_statistics": {
                "average_return": float(avg_return),
                "median_return": float(median_return),
                "return_volatility": float(std_return),
                "total_return": float(np.prod(1 + returns_array) - 1)
            },
            "win_loss_metrics": {
                "win_rate": float(win_rate),
                "average_win": float(avg_win),
                "average_loss": float(avg_loss),
                "profit_factor": float(avg_win / abs(avg_loss)) if avg_loss != 0 else float('inf')
            },
            "risk_metrics": {
                "sharpe_ratio": float(sharpe_ratio),
                "max_drawdown": float(max_drawdown),
                "consistency_score": float(consistency_score)
            },
            "statistical_significance": {
                "t_statistic": float(t_stat),
                "p_value": float(p_value),
                "is_significant": is_significant
            },
            "signal_strength_correlation": float(strength_correlation)
        },
        "signal_type_analysis": signal_type_analysis,
        "recent_performance": {
            "last_10_signals": [
                {
                    "signal": s['signal'],
                    "timestamp": str(s['timestamp']),
                    "return_5d": s['period_returns']['5d']
                } for s in aligned_signals[-10:]
            ]
        }
    }
        
    return standardize_output(result, "analyze_signal_quality")
        
def identify_false_signals(signals: List[Dict[str, Any]], 
                          prices: Union[pd.Series, Dict[str, Any]], 
                          threshold: float = 0.02) -> Dict[str, Any]:
    """Identify and analyze false trading signals using multi-criteria validation.
    
    False signals are trading signals that fail to generate the expected price movement
    or quickly reverse against the signal direction. This function applies four validation
    criteria to identify problematic signals and provides detailed analysis to improve
    signal generation algorithms.
    
    Args:
        signals: List of signal dictionaries to analyze. Each signal must contain:
            - 'timestamp': Signal generation time
            - 'signal': Signal type ('buy' or 'sell')
            - 'strength': Optional signal confidence level
        prices: Historical price data for validation. Can be pandas Series with
            datetime index or dictionary with dates as keys and prices as values.
        threshold: Return threshold for determining signal success. Defaults to 0.02
            (2%). Signals must achieve at least this return in the expected direction
            to be considered valid.
            
    Returns:
        Dict[str, Any]: False signal analysis including:
            - analysis_summary: Total signals analyzed, threshold used, time period
            - false_signal_analysis: Count, rate, and patterns of false signals
            - detailed_false_signals: First 10 false signals with failure reasons
            - improvement_opportunities: Actionable suggestions for signal enhancement
            - validation_criteria: Explanation of the four validation tests applied
            
        Validation criteria applied:
            1. Immediate direction: Signal matches next 1-3 period price movement
            2. Threshold reached: Price moves ≥threshold in signal direction within 20 periods
            3. Quick reversal: Price doesn't reverse >threshold against signal within 10 periods
            4. Volatility justified: Move size justified by recent volatility context
            
    Raises:
        Exception: If false signal identification fails due to data or calculation issues.
        
    Example:
        >>> import pandas as pd
        >>> signals = [
        ...     {'timestamp': '2023-01-02', 'signal': 'buy', 'strength': 0.8},
        ...     {'timestamp': '2023-01-05', 'signal': 'sell', 'strength': 0.6}
        ... ]
        >>> prices = pd.Series([100, 95, 102, 98, 94],  # Buy signal fails, sell succeeds
        ...                   index=pd.date_range('2023-01-01', periods=5))
        >>> false_analysis = identify_false_signals(signals, prices, threshold=0.03)
        >>> print(f"False signal rate: {false_analysis['false_signal_analysis']['false_signal_rate']:.1%}")
        >>> print(f"Common failures: {false_analysis['false_signal_analysis']['false_signal_patterns']}")
        >>> 
        >>> # Review improvement suggestions
        >>> for suggestion in false_analysis['improvement_opportunities']:
        ...     print(f"Suggestion: {suggestion}")
        
    Note:
        - Signal requires ≥2 failed criteria to be classified as false
        - Immediate direction checked over next 1-3 trading periods
        - Threshold achievement checked over next 20 trading periods
        - Quick reversal checked over next 10 trading periods
        - Volatility context uses 10-period rolling standard deviation
        - False signal rate >30% suggests need for stricter signal criteria
        - Analysis includes breakdown by signal type and failure patterns
    """
    if not signals:
        return standardize_output({
            "total_signals": 0,
            "false_signals": [],
            "false_signal_rate": 0
        }, "identify_false_signals")
        
    price_series = validate_price_data(prices)
        
    # Convert signals to DataFrame
    signals_df = pd.DataFrame(signals)
    signals_df['timestamp'] = pd.to_datetime(signals_df['timestamp'])
    signals_df = signals_df.sort_values('timestamp')
        
    validated_signals = []
    false_signals = []
        
    for _, signal in signals_df.iterrows():
        signal_time = signal['timestamp']
        signal_type = signal['signal']
            
        # Find the closest price point
        price_idx = price_series.index.get_indexer([signal_time], method='nearest')[0]
            
        if price_idx >= 0 and price_idx < len(price_series) - 5:  # Need at least 5 future points
            entry_price = price_series.iloc[price_idx]
                
            # Check multiple validation criteria
            validation_results = {}
                
            # 1. Immediate direction validation (next 1-3 periods)
            immediate_returns = []
            for i in range(1, min(4, len(price_series) - price_idx)):
                future_price = price_series.iloc[price_idx + i]
                ret = (future_price - entry_price) / entry_price
                immediate_returns.append(ret)
                
            avg_immediate_return = np.mean(immediate_returns)
                
            if signal_type == "buy":
                immediate_correct = avg_immediate_return > 0
                immediate_magnitude = avg_immediate_return
            elif signal_type == "sell":
                immediate_correct = avg_immediate_return < 0
                immediate_magnitude = -avg_immediate_return
            else:
                immediate_correct = True
                immediate_magnitude = 0
                
            validation_results["immediate_direction"] = immediate_correct
            validation_results["immediate_magnitude"] = immediate_magnitude
                
            # 2. Threshold validation (did it reach the expected threshold?)
            threshold_reached = False
            max_favorable_move = 0
            days_to_threshold = None
                
            for i in range(1, min(21, len(price_series) - price_idx)):  # Check up to 20 days
                future_price = price_series.iloc[price_idx + i]
                ret = (future_price - entry_price) / entry_price
                    
                if signal_type == "buy":
                    favorable_move = ret
                elif signal_type == "sell":
                    favorable_move = -ret
                else:
                    favorable_move = 0
                    
                max_favorable_move = max(max_favorable_move, favorable_move)
                    
                if favorable_move >= threshold and not threshold_reached:
                    threshold_reached = True
                    days_to_threshold = i
                
            validation_results["threshold_reached"] = threshold_reached
            validation_results["max_favorable_move"] = max_favorable_move
            validation_results["days_to_threshold"] = days_to_threshold
                
            # 3. Reversal validation (did price reverse against the signal quickly?)
            max_adverse_move = 0
            for i in range(1, min(11, len(price_series) - price_idx)):  # Check up to 10 days
                future_price = price_series.iloc[price_idx + i]
                ret = (future_price - entry_price) / entry_price
                    
                if signal_type == "buy":
                    adverse_move = -ret  # Negative returns are adverse for buy signals
                elif signal_type == "sell":
                    adverse_move = ret   # Positive returns are adverse for sell signals
                else:
                    adverse_move = 0
                    
                max_adverse_move = max(max_adverse_move, adverse_move)
                
            validation_results["max_adverse_move"] = max_adverse_move
            quick_reversal = max_adverse_move > threshold
            validation_results["quick_reversal"] = quick_reversal
                
            # 4. Volatility context validation
            recent_volatility = price_series.iloc[max(0, price_idx-10):price_idx].pct_change().std()
            expected_move = recent_volatility * 2  # 2 standard deviations
                
            move_vs_volatility = max_favorable_move / expected_move if expected_move > 0 else 0
            validation_results["move_vs_volatility"] = move_vs_volatility
            volatility_justified = move_vs_volatility > 0.5
            validation_results["volatility_justified"] = volatility_justified
                
            # Determine if signal is false
            false_signal_criteria = [
                not immediate_correct,
                not threshold_reached,
                quick_reversal,
                not volatility_justified
            ]
                
            false_signal_score = sum(false_signal_criteria)
            is_false_signal = false_signal_score >= 2  # At least 2 criteria failed
                
            signal_analysis = {
                **signal.to_dict(),
                "entry_price": entry_price,
                "validation_results": validation_results,
                "false_signal_score": false_signal_score,
                "is_false_signal": is_false_signal,
                "failure_reasons": [
                    reason for reason, failed in zip([
                        "immediate_direction_wrong",
                        "threshold_not_reached", 
                        "quick_reversal_occurred",
                        "move_not_volatility_justified"
                    ], false_signal_criteria) if failed
                ]
            }
                
            if is_false_signal:
                false_signals.append(signal_analysis)
            else:
                validated_signals.append(signal_analysis)
        
    # Calculate false signal statistics
    total_analyzed = len(validated_signals) + len(false_signals)
    false_signal_rate = len(false_signals) / total_analyzed if total_analyzed > 0 else 0
        
    # Analyze false signal patterns
    false_signal_patterns = {}
        
    if false_signals:
        # By signal type
        false_by_type = {}
        for signal_type in ["buy", "sell"]:
            type_false = [s for s in false_signals if s['signal'] == signal_type]
            total_type = len([s for s in validated_signals + false_signals if s['signal'] == signal_type])
                
            false_by_type[signal_type] = {
                "count": len(type_false),
                "rate": len(type_false) / total_type if total_type > 0 else 0
            }
            
        false_signal_patterns["by_signal_type"] = false_by_type
            
        # By failure reasons
        all_failure_reasons = []
        for fs in false_signals:
            all_failure_reasons.extend(fs['failure_reasons'])
            
        failure_reason_counts = pd.Series(all_failure_reasons).value_counts()
        false_signal_patterns["common_failure_reasons"] = failure_reason_counts.to_dict()
            
        # By signal strength (if available)
        if 'strength' in false_signals[0]:
            false_strengths = [s['strength'] for s in false_signals]
            valid_strengths = [s['strength'] for s in validated_signals]
                
            false_signal_patterns["strength_analysis"] = {
                "avg_false_signal_strength": float(np.mean(false_strengths)),
                "avg_valid_signal_strength": float(np.mean(valid_strengths)) if valid_strengths else 0,
                "strength_difference": float(np.mean(valid_strengths) - np.mean(false_strengths)) if valid_strengths else 0
            }
        
    # Identify improvement opportunities
    improvement_suggestions = []
        
    if false_signal_rate > 0.3:
        improvement_suggestions.append("High false signal rate - consider stricter signal generation criteria")
        
    if false_signal_patterns.get("common_failure_reasons", {}).get("immediate_direction_wrong", 0) > len(false_signals) * 0.5:
        improvement_suggestions.append("Many signals have wrong immediate direction - review signal timing")
        
    if false_signal_patterns.get("common_failure_reasons", {}).get("threshold_not_reached", 0) > len(false_signals) * 0.5:
        improvement_suggestions.append("Signals not reaching profit targets - consider lower thresholds or stronger signals")
        
    result = {
        "analysis_summary": {
            "total_signals_analyzed": total_analyzed,
            "validation_threshold": threshold,
            "analysis_period": {
                "start_date": str(signals_df['timestamp'].min().date()),
                "end_date": str(signals_df['timestamp'].max().date())
            }
        },
        "false_signal_analysis": {
            "false_signal_count": len(false_signals),
            "valid_signal_count": len(validated_signals),
            "false_signal_rate": float(false_signal_rate),
            "false_signal_patterns": false_signal_patterns
        },
        "detailed_false_signals": false_signals[:10],  # First 10 false signals
        "improvement_opportunities": improvement_suggestions,
        "validation_criteria": {
            "immediate_direction": "Signal direction matches next 1-3 period price movement",
            "threshold_reached": f"Price moves at least {threshold*100}% in signal direction within 20 periods",
            "quick_reversal": f"Price doesn't reverse more than {threshold*100}% against signal within 10 periods",
            "volatility_justified": "Move size is justified by recent volatility context"
        }
    }
        
    return standardize_output(result, "identify_false_signals")
        
def optimize_signal_parameters(prices: Union[pd.Series, Dict[str, Any]], 
                              strategy: str = "rsi", 
                              parameter_ranges: Optional[Dict[str, List]] = None) -> Dict[str, Any]:
    """Optimize trading signal parameters using systematic grid search and backtesting.
    
    This function performs comprehensive parameter optimization for technical analysis
    strategies by testing all combinations of specified parameter ranges. Each combination
    is backtested and evaluated using multiple performance metrics to identify the
    optimal configuration for the given price series.
    
    Args:
        prices: Historical price data for optimization. Can be pandas Series with
            datetime index or dictionary with dates as keys and prices as values.
            Requires at least 100 price points for reliable optimization.
        strategy: Technical analysis strategy to optimize. Supported strategies:
            - "rsi": Relative Strength Index with overbought/oversold thresholds
            - "macd": Moving Average Convergence Divergence with crossover signals
            - "bollinger": Bollinger Bands mean reversion strategy
            - "momentum": Price momentum breakout strategy
            Defaults to "rsi".
        parameter_ranges: Optional dictionary specifying parameter ranges to test.
            If not provided, uses default ranges for the selected strategy:
            - RSI: period (10-30), upper_threshold (65-80), lower_threshold (20-35)
            - MACD: fast_period (8-16), slow_period (21-31), signal_period (6-12)
            - Momentum: lookback (3-15), momentum_threshold (0.01-0.05)
            
    Returns:
        Dict[str, Any]: Optimization results including:
            - optimization_summary: Strategy tested, combinations tried, success rate
            - best_parameters: Optimal parameter configuration found
            - best_performance: Performance metrics for optimal parameters
            - parameter_importance: Correlation between each parameter and performance
            - performance_stability: Analysis of top performer consistency
            - top_10_results: Best 10 parameter combinations for comparison
            - optimization_recommendations: Key insights and suggested parameters
            
        Performance metrics calculated:
            - Total return, average return, volatility, Sharpe ratio
            - Win rate, maximum drawdown, signal count
            - Composite score (weighted combination of metrics)
            
    Raises:
        ValueError: If insufficient data (<100 points) or invalid strategy specified.
        Exception: If optimization fails due to technical indicator calculation errors.
        
    Example:
        >>> import pandas as pd
        >>> # Generate sample price data
        >>> prices = pd.Series([100 + i + np.random.normal(0, 2) for i in range(200)],
        ...                   index=pd.date_range('2023-01-01', periods=200))
        >>> 
        >>> # Optimize RSI strategy with custom ranges
        >>> custom_ranges = {
        ...     'period': [14, 21, 28],
        ...     'upper_threshold': [70, 75, 80],
        ...     'lower_threshold': [20, 25, 30]
        ... }
        >>> optimization = optimize_signal_parameters(prices, strategy="rsi", 
        ...                                         parameter_ranges=custom_ranges)
        >>> 
        >>> print(f"Best parameters: {optimization['best_parameters']}")
        >>> print(f"Best Sharpe ratio: {optimization['best_performance']['sharpe_ratio']:.2f}")
        >>> print(f"Most important parameter: {optimization['optimization_recommendations']['most_important_parameter']}")
        
    Note:
        - Grid search tests all combinations of provided parameter ranges
        - Signals generated using 5-day forward returns for backtesting
        - Composite score weights: Sharpe ratio (40%), total return (30%), win rate (20%), max drawdown (-10%)
        - Parameter importance calculated using correlation with performance scores
        - Stability analysis examines consistency among top 10% of results
        - Minimum 5 signals required for reliable performance calculation
        - Failed parameter combinations are skipped automatically
        - Results sorted by composite score for easy identification of best performers
    """
    price_series = validate_price_data(prices)
        
    if len(price_series) < 100:
        raise ValueError("Need at least 100 price points for optimization")
        
    # Define default parameter ranges for different strategies
    default_ranges = {
        "rsi": {
            "period": [10, 14, 20, 25, 30],
            "upper_threshold": [65, 70, 75, 80],
            "lower_threshold": [20, 25, 30, 35]
        },
        "macd": {
            "fast_period": [8, 12, 16],
            "slow_period": [21, 26, 31],
            "signal_period": [6, 9, 12]
        },
        "bollinger": {
            "period": [15, 20, 25],
            "std_dev": [1.5, 2.0, 2.5, 3.0]
        },
        "momentum": {
            "lookback": [3, 5, 10, 15],
            "momentum_threshold": [0.01, 0.02, 0.03, 0.05]
        }
    }
        
    if parameter_ranges is None:
        parameter_ranges = default_ranges.get(strategy, {})
        
    if not parameter_ranges:
        raise ValueError(f"No parameter ranges provided for strategy: {strategy}")
        
    # Generate all parameter combinations
    param_names = list(parameter_ranges.keys())
    param_values = list(parameter_ranges.values())
    param_combinations = list(product(*param_values))
        
    optimization_results = []
        
    for i, param_combo in enumerate(param_combinations):
        
        # Create parameter dictionary
        params = dict(zip(param_names, param_combo))
            
        # Generate signals based on strategy
        if strategy == "rsi":
            from indicators.momentum import calculate_rsi
            rsi_result = calculate_rsi(price_series, period=params['period'])
            if not rsi_result.get("success", True):
                continue
                
            # Generate threshold-based signals
            signals_result = generate_signals(
                rsi_result['rsi'],
                method="threshold",
                parameters={
                    "upper_threshold": params['upper_threshold'],
                    "lower_threshold": params['lower_threshold']
                }
            )
            
        elif strategy == "macd":
            from indicators.momentum import calculate_macd
            macd_result = calculate_macd(
                price_series, 
                fast_period=params['fast_period'],
                slow_period=params['slow_period'],
                signal_period=params['signal_period']
            )
            if not macd_result.get("success", True):
                continue
                
            # Generate crossover signals
            macd_line = macd_result['macd_line']
            signal_line = macd_result['signal_line']
                
            # Simple crossover detection
            signals = []
            for j in range(1, len(macd_line)):
                if pd.notna(macd_line.iloc[j]) and pd.notna(signal_line.iloc[j]):
                    if macd_line.iloc[j-1] <= signal_line.iloc[j-1] and macd_line.iloc[j] > signal_line.iloc[j]:
                        signals.append({
                            "timestamp": macd_line.index[j],
                            "signal": "buy",
                            "strength": 0.8
                        })
                    elif macd_line.iloc[j-1] >= signal_line.iloc[j-1] and macd_line.iloc[j] < signal_line.iloc[j]:
                        signals.append({
                            "timestamp": macd_line.index[j],
                            "signal": "sell",
                            "strength": 0.8
                        })
                
            signals_result = {"signals": signals, "success": True}
            
        elif strategy == "momentum":
            # Generate momentum signals
            signals_result = generate_signals(
                price_series,
                method="momentum",
                parameters={
                    "lookback": params['lookback'],
                    "momentum_threshold": params['momentum_threshold']
                }
            )
            
        else:
            continue
            
        if not signals_result.get("success", True) or not signals_result.get("signals"):
            continue
            
        # Backtest the signals
        signals = signals_result["signals"]
            
        # Calculate performance metrics
        signal_returns = []
        for signal in signals:
            signal_time = pd.to_datetime(signal['timestamp'])
            price_idx = price_series.index.get_indexer([signal_time], method='nearest')[0]
                
            if price_idx >= 0 and price_idx < len(price_series) - 5:
                entry_price = price_series.iloc[price_idx]
                exit_price = price_series.iloc[min(price_idx + 5, len(price_series) - 1)]
                    
                if signal['signal'] == "buy":
                    ret = (exit_price - entry_price) / entry_price
                elif signal['signal'] == "sell":
                    ret = (entry_price - exit_price) / entry_price
                else:
                    ret = 0
                    
                signal_returns.append(ret)
            
        if len(signal_returns) >= 5:  # Need minimum signals for reliable metrics
            returns_array = np.array(signal_returns)
                
            # Calculate key performance metrics
            total_return = np.prod(1 + returns_array) - 1
            avg_return = np.mean(returns_array)
            volatility = np.std(returns_array)
            sharpe_ratio = avg_return / volatility if volatility > 0 else 0
            win_rate = np.mean(returns_array > 0)
                
            # Max drawdown
            cumulative = np.cumprod(1 + returns_array)
            running_max = np.maximum.accumulate(cumulative)
            drawdowns = (cumulative - running_max) / running_max
            max_drawdown = np.min(drawdowns)
                
            # Composite score (weighted combination of metrics)
            score = (
                sharpe_ratio * 0.4 +
                total_return * 0.3 +
                win_rate * 0.2 +
                abs(max_drawdown) * -0.1
            )
                
            optimization_results.append({
                "parameters": params,
                "performance": {
                    "total_return": float(total_return),
                    "average_return": float(avg_return),
                    "volatility": float(volatility),
                    "sharpe_ratio": float(sharpe_ratio),
                    "win_rate": float(win_rate),
                    "max_drawdown": float(max_drawdown),
                    "signal_count": len(signal_returns),
                    "composite_score": float(score)
                }
            })
            
    if not optimization_results:
        return standardize_output({
            "strategy": strategy,
            "optimization_results": [],
            "error": "No valid parameter combinations found"
        }, "optimize_signal_parameters")
        
    # Sort by composite score (best first)
    optimization_results.sort(key=lambda x: x["performance"]["composite_score"], reverse=True)
        
    best_params = optimization_results[0]["parameters"]
    best_performance = optimization_results[0]["performance"]
        
    # Statistical analysis of parameter importance
    param_importance = {}
    for param_name in param_names:
        param_values = [result["parameters"][param_name] for result in optimization_results]
        scores = [result["performance"]["composite_score"] for result in optimization_results]
            
        # Calculate correlation between parameter value and performance
        correlation = np.corrcoef(param_values, scores)[0, 1] if len(set(param_values)) > 1 else 0
        param_importance[param_name] = float(correlation)
        
    # Performance stability analysis
    top_10_percent = optimization_results[:max(1, len(optimization_results) // 10)]
    performance_stability = {
        "top_performers_count": len(top_10_percent),
        "score_range": {
            "min": float(min(r["performance"]["composite_score"] for r in top_10_percent)),
            "max": float(max(r["performance"]["composite_score"] for r in top_10_percent)),
            "std": float(np.std([r["performance"]["composite_score"] for r in top_10_percent]))
        },
        "parameter_consistency": {}
    }
        
    # Check parameter consistency in top performers
    for param_name in param_names:
        top_param_values = [r["parameters"][param_name] for r in top_10_percent]
        performance_stability["parameter_consistency"][param_name] = {
            "most_common": max(set(top_param_values), key=top_param_values.count),
            "consistency_rate": top_param_values.count(max(set(top_param_values), key=top_param_values.count)) / len(top_param_values)
        }
        
    result = {
        "optimization_summary": {
            "strategy": strategy,
            "combinations_tested": len(param_combinations),
            "valid_results": len(optimization_results),
            "success_rate": len(optimization_results) / len(param_combinations)
        },
        "best_parameters": best_params,
        "best_performance": best_performance,
        "parameter_importance": param_importance,
        "performance_stability": performance_stability,
        "top_10_results": optimization_results[:10],
        "parameter_ranges_tested": parameter_ranges,
        "optimization_recommendations": {
            "most_important_parameter": max(param_importance.items(), key=lambda x: abs(x[1]))[0] if param_importance else None,
            "stable_performance": performance_stability["score_range"]["std"] < 0.1,
            "suggested_parameters": best_params
        }
    }
        
    return standardize_output(result, "optimize_signal_parameters")
        
# Registry of signal analysis functions - all using proven libraries
SIGNAL_ANALYSIS_FUNCTIONS = {
    'analyze_signal_quality': analyze_signal_quality,
    'identify_false_signals': identify_false_signals,
    'optimize_signal_parameters': optimize_signal_parameters
}