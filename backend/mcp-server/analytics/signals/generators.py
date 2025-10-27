"""Condition detection primitives for trading strategies.

This module provides generic, reusable comparison primitives for building trading strategies.
Rather than generating buy/sell signals directly, it detects conditions (facts) that occur
in time series data. Strategies compose these primitives to build their decision logic.

Core Primitive:
- compare(): Generic comparison function that detects conditions in time series

Supported Operators:
- Crossovers: "crossover_up", "crossover_down"
- Comparisons: ">", "<", ">=", "<=", "=="
- Ranges: "between", "outside"

Additional functionality includes:
- Signal frequency analysis and distribution statistics
- Multi-source signal combination with various consensus methods
- Advanced signal filtering with customizable criteria

All functions integrate with the financial-analysis-function-library.json specification
and provide standardized outputs for the MCP analytics server.

Example:
    Building conditions for strategy composition:
    
    >>> from mcp.analytics.signals.generators import compare, combine_signals
    >>> import pandas as pd
    >>> # Detect conditions (not signals!)
    >>> rsi_data = pd.Series([30, 25, 75, 80, 45])  # RSI values
    >>> oversold = compare(rsi_data, "<", 30)
    >>> above_threshold = compare(rsi_data, ">", 70)
    >>> 
    >>> # Strategy layer decides what these conditions mean
    >>> # (not the compare function)
    
Note:
    Conditions return facts: what happened in the data.
    Strategies apply context and rules to convert conditions into trading decisions.
"""



import pandas as pd
import numpy as np
from typing import Dict, List, Any, Union, Optional
import warnings
warnings.filterwarnings('ignore')

from ..utils.data_utils import validate_return_data, validate_price_data, standardize_output
from ..indicators.momentum.indicators import calculate_rsi, calculate_macd, calculate_stochastic
from ..indicators.volatility.indicators import calculate_bollinger_bands


def generate_signals(series1: Union[pd.Series, List[float], Dict[str, Any]],
                    series2: Union[pd.Series, float, tuple],
                    operator: str) -> List[Dict]:
    """Detect when series1 meets a condition relative to series2.
    
    Scans the time series and returns all timestamps where the comparison is True.
    Does NOT interpret what the condition means - just reports when it occurs.
    
    Args:
        series1: Time series to analyze. Can be:
            - pandas Series: Preferred format with datetime index
            - List of floats: Automatically converted to Series
            - Dictionary: With 'data' key or value mapping
        series2: What to compare against. Can be:
            - pandas Series: Element-wise comparison with series1
            - float/int: Fixed threshold value (broadcast to all timestamps)
            - tuple (lower, upper): Range bounds for "between"/"outside" operators
        operator: Comparison operator. Supported:
            - "crossover_up": series1 crosses ABOVE series2
            - "crossover_down": series1 crosses BELOW series2
            - ">": series1 > series2
            - "<": series1 < series2
            - ">=": series1 >= series2
            - "<=": series1 <= series2
            - "==": series1 == series2
            - "between": lower <= series1 <= upper (series2 must be tuple)
            - "outside": series1 < lower OR series1 > upper (series2 must be tuple)
            
    Returns:
        List[Dict]: All timestamps where the condition is True:
            - timestamp: When condition occurred
            - index: Position in series
            - series1_value: Value at this time
            - series2_value: Comparison value (if applicable)
            - operator: The operator used
            
        For "between"/"outside":
            - lower_value: Lower bound
            - upper_value: Upper bound
            
    Examples:
        >>> import pandas as pd
        >>> returns = pd.Series([-0.02, -0.05, 0.03, -0.04])
        >>> down_months = generate_signals(returns, -0.03, "<")
        >>> # Returns timestamps where returns < -3%
        
        >>> rsi = pd.Series([25, 30, 70, 75])
        >>> oversold = generate_signals(rsi, 30, "<")
        >>> # Returns timestamps where RSI < 30
        
        >>> price = pd.Series([100, 105, 103, 108])
        >>> ma = pd.Series([102, 104, 104, 106])
        >>> crosses = generate_signals(price, ma, "crossover_up")
        >>> # Returns timestamps where price crosses above MA
        
        >>> momentum = pd.Series([0.5, -0.4, 1.2, -0.8])
        >>> normal = generate_signals(momentum, (-1, 1), "between")
        >>> # Returns timestamps where momentum is between -1 and 1
    """
    # Normalize series1 to Series
    if isinstance(series1, (list, dict)):
        if isinstance(series1, dict) and 'data' in series1:
            series1 = pd.Series(series1['data'])
        elif isinstance(series1, dict):
            series1 = pd.Series(list(series1.values()))
        else:
            series1 = pd.Series(series1)
    else:
        series1 = series1.copy()
        
    # Normalize series2 based on operator
    if operator in ["between", "outside"]:
        if not isinstance(series2, tuple) or len(series2) != 2:
            raise ValueError(f"Operator '{operator}' requires series2 as tuple (lower, upper)")
        lower_val, upper_val = series2
        lower_series = pd.Series([lower_val] * len(series1), index=series1.index) if isinstance(lower_val, (int, float)) else lower_val
        upper_series = pd.Series([upper_val] * len(series1), index=series1.index) if isinstance(upper_val, (int, float)) else upper_val
    else:
        if isinstance(series2, (int, float)):
            series2_values = pd.Series([series2] * len(series1), index=series1.index)
        else:
            series2_values = series2
        
    events = []
        
    if operator == "crossover_up":
        for i in range(1, len(series1)):
            if pd.isna(series1.iloc[i]) or pd.isna(series1.iloc[i-1]) or pd.isna(series2_values.iloc[i]) or pd.isna(series2_values.iloc[i-1]):
                continue
            if (series1.iloc[i-1] <= series2_values.iloc[i-1] and 
                series1.iloc[i] > series2_values.iloc[i]):
                events.append({
                    "timestamp": series1.index[i],
                    "index": i,
                    "series1_value": float(series1.iloc[i]),
                    "series2_value": float(series2_values.iloc[i]),
                    "operator": operator
                })
        
    elif operator == "crossover_down":
        for i in range(1, len(series1)):
            if pd.isna(series1.iloc[i]) or pd.isna(series1.iloc[i-1]) or pd.isna(series2_values.iloc[i]) or pd.isna(series2_values.iloc[i-1]):
                continue
            if (series1.iloc[i-1] >= series2_values.iloc[i-1] and 
                series1.iloc[i] < series2_values.iloc[i]):
                events.append({
                    "timestamp": series1.index[i],
                    "index": i,
                    "series1_value": float(series1.iloc[i]),
                    "series2_value": float(series2_values.iloc[i]),
                    "operator": operator
                })
        
    elif operator == ">":
        for i, (ts, value) in enumerate(series1.items()):
            if pd.isna(value) or pd.isna(series2_values.iloc[i]):
                continue
            if float(value) > float(series2_values.iloc[i]):
                events.append({
                    "timestamp": ts,
                    "index": i,
                    "series1_value": float(value),
                    "series2_value": float(series2_values.iloc[i]),
                    "operator": operator
                })
        
    elif operator == "<":
        for i, (ts, value) in enumerate(series1.items()):
            if pd.isna(value) or pd.isna(series2_values.iloc[i]):
                continue
            if float(value) < float(series2_values.iloc[i]):
                events.append({
                    "timestamp": ts,
                    "index": i,
                    "series1_value": float(value),
                    "series2_value": float(series2_values.iloc[i]),
                    "operator": operator
                })
        
    elif operator == ">=":
        for i, (ts, value) in enumerate(series1.items()):
            if pd.isna(value) or pd.isna(series2_values.iloc[i]):
                continue
            if float(value) >= float(series2_values.iloc[i]):
                events.append({
                    "timestamp": ts,
                    "index": i,
                    "series1_value": float(value),
                    "series2_value": float(series2_values.iloc[i]),
                    "operator": operator
                })
        
    elif operator == "<=":
        for i, (ts, value) in enumerate(series1.items()):
            if pd.isna(value) or pd.isna(series2_values.iloc[i]):
                continue
            if float(value) <= float(series2_values.iloc[i]):
                events.append({
                    "timestamp": ts,
                    "index": i,
                    "series1_value": float(value),
                    "series2_value": float(series2_values.iloc[i]),
                    "operator": operator
                })
        
    elif operator == "==":
        tolerance = 0.0
        for i, (ts, value) in enumerate(series1.items()):
            if pd.isna(value) or pd.isna(series2_values.iloc[i]):
                continue
            if abs(float(value) - float(series2_values.iloc[i])) <= tolerance:
                events.append({
                    "timestamp": ts,
                    "index": i,
                    "series1_value": float(value),
                    "series2_value": float(series2_values.iloc[i]),
                    "operator": operator
                })
        
    elif operator == "between":
        for i, (ts, value) in enumerate(series1.items()):
            if pd.isna(value) or pd.isna(lower_series.iloc[i]) or pd.isna(upper_series.iloc[i]):
                continue
            v = float(value)
            if float(lower_series.iloc[i]) <= v <= float(upper_series.iloc[i]):
                events.append({
                    "timestamp": ts,
                    "index": i,
                    "series1_value": v,
                    "lower_value": float(lower_series.iloc[i]),
                    "upper_value": float(upper_series.iloc[i]),
                    "operator": operator
                })
        
    elif operator == "outside":
        for i, (ts, value) in enumerate(series1.items()):
            if pd.isna(value) or pd.isna(lower_series.iloc[i]) or pd.isna(upper_series.iloc[i]):
                continue
            v = float(value)
            if v < float(lower_series.iloc[i]) or v > float(upper_series.iloc[i]):
                events.append({
                    "timestamp": ts,
                    "index": i,
                    "series1_value": v,
                    "lower_value": float(lower_series.iloc[i]),
                    "upper_value": float(upper_series.iloc[i]),
                    "operator": operator
                })
        
    else:
        raise ValueError(f"Unknown operator: {operator}")
        
    return events
        
def calculate_signal_frequency(signals: List[Dict[str, Any]], 
                              timeframe: str = "daily") -> Dict[str, Any]:
    """Calculate comprehensive signal frequency statistics and distribution patterns.
    
    This function analyzes the temporal distribution of trading signals to understand
    signal generation patterns, clustering, and consistency. It provides insights into
    signal frequency that are crucial for risk management and strategy evaluation.
    
    Args:
        signals: List of signal dictionaries to analyze. Each signal must contain:
            - 'timestamp': Signal generation time (string or datetime)
            - 'signal': Signal type ('buy', 'sell', etc.)
            Optional fields: 'strength', 'method' for additional analysis
        timeframe: Time aggregation level for frequency analysis. Options:
            - "daily": Group signals by calendar day
            - "weekly": Group signals by calendar week
            - "monthly": Group signals by calendar month
            Defaults to "daily".
            
    Returns:
        Dict[str, Any]: Signal frequency analysis including:
            - timeframe: Aggregation level used
            - analysis_period: Start/end dates and total periods covered
            - frequency_statistics: Signals per period (avg, max, min, std dev)
            - time_between_signals: Average, median, min, max days between signals
            - signal_distribution: Breakdown by type, method, and clustering patterns
            - strength_analysis: Signal strength statistics (if available)
            
        Clustering analysis includes:
            - periods_with_signals: Count of active periods
            - periods_without_signals: Count of inactive periods
            - signal_concentration: Standard deviation of signals per period
            - most_active_period: Period with highest signal count
            
    Raises:
        ValueError: If timeframe is invalid or signals lack required 'timestamp' field.
        Exception: If frequency calculation fails due to data issues.
        
    Example:
        >>> signals = [
        ...     {'timestamp': '2023-01-02', 'signal': 'buy', 'strength': 0.8},
        ...     {'timestamp': '2023-01-02', 'signal': 'buy', 'strength': 0.6},  # Same day
        ...     {'timestamp': '2023-01-05', 'signal': 'sell', 'strength': 0.9},
        ...     {'timestamp': '2023-01-12', 'signal': 'buy', 'strength': 0.7}
        ... ]
        >>> freq_analysis = calculate_signal_frequency(signals, timeframe="daily")
        >>> print(f"Average signals per day: {freq_analysis['frequency_statistics']['signals_per_period']['average']:.1f}")
        >>> print(f"Average days between signals: {freq_analysis['frequency_statistics']['time_between_signals']['average_days']:.1f}")
        >>> print(f"Buy percentage: {freq_analysis['signal_distribution']['by_type']['percentages']['buy']:.1f}%")
        
    Note:
        - Timestamps automatically converted to pandas datetime for analysis
        - Empty signal lists return zero statistics with no errors
        - Time between signals calculated using consecutive signal timestamps
        - Signal clustering helps identify burst periods vs steady generation
        - Strength analysis only available if signals contain 'strength' field
        - Method distribution analysis available if signals contain 'method' field
        - All time differences reported in days for consistency
    """
    if not signals:
        return standardize_output({
            "timeframe": timeframe,
            "total_signals": 0,
            "frequency_statistics": {},
            "signal_distribution": {}
        }, "calculate_signal_frequency")
        
    # Convert to DataFrame for easier analysis
    signals_df = pd.DataFrame(signals)
        
    # Ensure timestamp column exists
    if 'timestamp' not in signals_df.columns:
        raise ValueError("Signals must contain 'timestamp' field")
        
    # Convert timestamps to datetime if needed
    signals_df['timestamp'] = pd.to_datetime(signals_df['timestamp'])
    signals_df = signals_df.sort_values('timestamp')
        
    # Create time period grouping
    if timeframe == "daily":
        signals_df['period'] = signals_df['timestamp'].dt.date
    elif timeframe == "weekly":
        signals_df['period'] = signals_df['timestamp'].dt.to_period('W')
    elif timeframe == "monthly":
        signals_df['period'] = signals_df['timestamp'].dt.to_period('M')
    else:
        raise ValueError(f"Unknown timeframe: {timeframe}")
        
    # Calculate frequency statistics
    total_signals = len(signals_df)
    unique_periods = signals_df['period'].nunique()
        
    # Signals per period
    signals_per_period = signals_df.groupby('period').size()
    avg_signals_per_period = signals_per_period.mean()
    max_signals_per_period = signals_per_period.max()
    min_signals_per_period = signals_per_period.min()
        
    # Signal type distribution
    signal_type_counts = signals_df['signal'].value_counts()
    signal_type_percentages = (signal_type_counts / total_signals * 100).round(2)
        
    # Time between signals
    time_diffs = signals_df['timestamp'].diff().dropna()
    if len(time_diffs) > 0:
        avg_time_between_signals = time_diffs.mean()
        median_time_between_signals = time_diffs.median()
        min_time_between_signals = time_diffs.min()
        max_time_between_signals = time_diffs.max()
    else:
        avg_time_between_signals = pd.NaT
        median_time_between_signals = pd.NaT
        min_time_between_signals = pd.NaT
        max_time_between_signals = pd.NaT
        
    # Signal clustering analysis
    periods_with_signals = signals_per_period[signals_per_period > 0]
    signal_clustering = {
        "periods_with_signals": len(periods_with_signals),
        "periods_without_signals": unique_periods - len(periods_with_signals),
        "signal_concentration": float(signals_per_period.std()) if len(signals_per_period) > 1 else 0,
        "most_active_period": str(signals_per_period.idxmax()) if len(signals_per_period) > 0 else None,
        "most_active_period_count": int(signals_per_period.max()) if len(signals_per_period) > 0 else 0
    }
        
    # Method distribution (if available)
    method_distribution = {}
    if 'method' in signals_df.columns:
        method_counts = signals_df['method'].value_counts()
        method_distribution = {
            "counts": method_counts.to_dict(),
            "percentages": (method_counts / total_signals * 100).round(2).to_dict()
        }
        
    # Strength statistics (if available)
    strength_stats = {}
    if 'strength' in signals_df.columns:
        strength_values = signals_df['strength'].dropna()
        if len(strength_values) > 0:
            strength_stats = {
                "average_strength": float(strength_values.mean()),
                "median_strength": float(strength_values.median()),
                "min_strength": float(strength_values.min()),
                "max_strength": float(strength_values.max()),
                "std_strength": float(strength_values.std())
            }
        
    result = {
        "timeframe": timeframe,
        "analysis_period": {
            "start_date": str(signals_df['timestamp'].min().date()),
            "end_date": str(signals_df['timestamp'].max().date()),
            "total_periods": unique_periods
        },
        "frequency_statistics": {
            "total_signals": total_signals,
            "signals_per_period": {
                "average": float(avg_signals_per_period),
                "maximum": int(max_signals_per_period),
                "minimum": int(min_signals_per_period),
                "std_dev": float(signals_per_period.std()) if len(signals_per_period) > 1 else 0
            },
            "time_between_signals": {
                "average_days": float(avg_time_between_signals.total_seconds() / 86400) if pd.notna(avg_time_between_signals) else None,
                "median_days": float(median_time_between_signals.total_seconds() / 86400) if pd.notna(median_time_between_signals) else None,
                "min_days": float(min_time_between_signals.total_seconds() / 86400) if pd.notna(min_time_between_signals) else None,
                "max_days": float(max_time_between_signals.total_seconds() / 86400) if pd.notna(max_time_between_signals) else None
            }
        },
        "signal_distribution": {
            "by_type": {
                "counts": signal_type_counts.to_dict(),
                "percentages": signal_type_percentages.to_dict()
            },
            "by_method": method_distribution,
            "signal_clustering": signal_clustering
        },
        "strength_analysis": strength_stats
    }
        
    return standardize_output(result, "calculate_signal_frequency")
        
def combine_signals(signals_list: List[List[Dict[str, Any]]], 
                   method: str = "majority") -> Dict[str, Any]:
    """Combine multiple signal sources using various consensus methods.
    
    This function merges signals from multiple sources (e.g., different technical
    indicators or timeframes) to create a unified signal stream. It uses temporal
    alignment and various consensus methods to reduce false signals and improve
    signal quality through diversification.
    
    Args:
        signals_list: List of signal lists to combine. Each list should contain
            signal dictionaries with 'timestamp', 'signal', and optionally 'strength'.
            Requires at least 2 non-empty signal lists for combination.
        method: Signal combination methodology. Available methods:
            - "majority": Require majority agreement (>50%) for signal generation
            - "unanimous": Require all sources to agree for signal generation
            - "weighted": Use strength-weighted voting (requires 'strength' field)
            - "any": Generate buy if any source says buy, else sell if any says sell
            Defaults to "majority".
            
    Returns:
        Dict[str, Any]: Signal combination results including:
            - combination_method: Method used for combining signals
            - input_sources: Number of input signal lists
            - combined_signals: List of consensus signals with metadata
            - combination_statistics: Reduction rates, confidence levels, distribution
            - source_statistics: Signal counts from each input source
            
        Each combined signal contains:
            - timestamp: Consensus signal time (rounded to nearest minute)
            - signal: Consensus signal type ('buy' or 'sell')
            - strength: Average strength of agreeing sources
            - confidence: Confidence level based on agreement percentage
            - sources_count: Number of sources contributing to this signal
            - source_signals: Detailed breakdown of contributing source signals
            
    Raises:
        ValueError: If fewer than 2 signal lists provided or insufficient valid signals.
        Exception: If signal combination fails due to data processing issues.
        
    Example:
        >>> # Combine RSI and MACD signals
        >>> rsi_signals = [
        ...     {'timestamp': '2023-01-02 10:00', 'signal': 'buy', 'strength': 0.8},
        ...     {'timestamp': '2023-01-05 14:30', 'signal': 'sell', 'strength': 0.7}
        ... ]
        >>> macd_signals = [
        ...     {'timestamp': '2023-01-02 10:01', 'signal': 'buy', 'strength': 0.6},  # Near same time
        ...     {'timestamp': '2023-01-05 14:25', 'signal': 'buy', 'strength': 0.5}   # Disagrees
        ... ]
        >>> combined = combine_signals([rsi_signals, macd_signals], method="majority")
        >>> print(f"Combined signals: {len(combined['combined_signals'])}")
        >>> print(f"Signal reduction: {combined['combination_statistics']['signal_reduction_percentage']:.1f}%")
        >>> 
        >>> # Try unanimous consensus
        >>> unanimous = combine_signals([rsi_signals, macd_signals], method="unanimous")
        >>> print(f"Unanimous signals: {len(unanimous['combined_signals'])}")
        
    Note:
        - Signals aligned by timestamp with 1-minute precision for grouping
        - Only periods with signals from multiple sources are considered
        - Signal reduction typically occurs as consensus filters out weak signals
        - Confidence reflects the degree of agreement among sources
        - Weighted method requires all signals to have 'strength' field
        - 'Any' method prioritizes buy signals over sell signals
        - Timestamps rounded to nearest minute to handle slight timing differences
        - Source signals preserved in output for traceability
    """
    if not signals_list or len(signals_list) < 2:
        raise ValueError("Need at least 2 signal lists to combine")
        
    # Convert all signal lists to DataFrames
    signal_dfs = []
    for i, signals in enumerate(signals_list):
        if not signals:
            continue
                
        df = pd.DataFrame(signals)
        df['source'] = f"source_{i}"
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        signal_dfs.append(df)
        
    if len(signal_dfs) < 2:
        raise ValueError("Need at least 2 non-empty signal lists")
        
    # Combine all signals and group by timestamp
    all_signals = pd.concat(signal_dfs, ignore_index=True)
    all_signals = all_signals.sort_values('timestamp')
        
    # Group signals by timestamp (allowing for small time differences)
    all_signals['timestamp_rounded'] = all_signals['timestamp'].dt.floor('1min')  # Round to nearest minute
    grouped_signals = all_signals.groupby('timestamp_rounded')
        
    combined_signals = []
        
    for timestamp, group in grouped_signals:
        if len(group) < 2:  # Need signals from multiple sources
            continue
            
        signal_counts = group['signal'].value_counts()
        total_sources = len(signal_dfs)
        sources_with_signals = group['source'].nunique()
            
        # Calculate signal weights (if strength is available)
        if 'strength' in group.columns:
            weighted_signals = group.groupby('signal')['strength'].mean()
        else:
            weighted_signals = signal_counts / len(group)
            
        combined_signal = None
        confidence = 0.0
            
        if method == "majority":
            # Majority vote
            if len(signal_counts) > 0:
                majority_signal = signal_counts.index[0]
                majority_count = signal_counts.iloc[0]
                    
                if majority_count > len(group) / 2:
                    combined_signal = majority_signal
                    confidence = majority_count / len(group)
            
        elif method == "unanimous":
            # All sources must agree
            if len(signal_counts) == 1:
                combined_signal = signal_counts.index[0]
                confidence = 1.0
            
        elif method == "weighted":
            # Weighted by signal strength
            if len(weighted_signals) > 0:
                strongest_signal = weighted_signals.index[weighted_signals.argmax()]
                combined_signal = strongest_signal
                confidence = float(weighted_signals.max())
            
        elif method == "any":
            # Any buy signal triggers buy, otherwise sell if any sell
            if 'buy' in signal_counts:
                combined_signal = "buy"
                confidence = signal_counts.get('buy', 0) / len(group)
            elif 'sell' in signal_counts:
                combined_signal = "sell"
                confidence = signal_counts.get('sell', 0) / len(group)
            
        else:
            raise ValueError(f"Unknown combination method: {method}")
            
        if combined_signal:
            # Calculate combined strength
            signal_strengths = group[group['signal'] == combined_signal]['strength'].dropna()
            avg_strength = signal_strengths.mean() if len(signal_strengths) > 0 else confidence
                
            combined_signals.append({
                "timestamp": timestamp,
                "signal": combined_signal,
                "strength": float(avg_strength),
                "confidence": float(confidence),
                "sources_count": sources_with_signals,
                "method": method,
                "source_signals": group[['source', 'signal', 'strength']].to_dict('records')
            })
        
    # Calculate combination statistics
    total_combined = len(combined_signals)
    original_total = sum(len(signals) for signals in signals_list)
        
    signal_reduction = ((original_total - total_combined) / original_total * 100) if original_total > 0 else 0
        
    if combined_signals:
        avg_confidence = np.mean([s['confidence'] for s in combined_signals])
        avg_sources = np.mean([s['sources_count'] for s in combined_signals])
            
        combined_signal_counts = pd.Series([s['signal'] for s in combined_signals]).value_counts()
    else:
        avg_confidence = 0
        avg_sources = 0
        combined_signal_counts = pd.Series()
        
    result = {
        "combination_method": method,
        "input_sources": len(signals_list),
        "combined_signals": combined_signals,
        "combination_statistics": {
            "original_total_signals": original_total,
            "combined_total_signals": total_combined,
            "signal_reduction_percentage": float(signal_reduction),
            "average_confidence": float(avg_confidence),
            "average_sources_per_signal": float(avg_sources),
            "signal_type_distribution": combined_signal_counts.to_dict()
        },
        "source_statistics": {
            f"source_{i}": len(signals) for i, signals in enumerate(signals_list)
        }
    }
        
    return standardize_output(result, "combine_signals")
        
def filter_signals(signals: List[Dict[str, Any]], 
                  filters: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Filter trading signals based on customizable criteria for quality improvement.
    
    This function applies multiple filtering criteria to remove low-quality or
    unwanted signals from a signal stream. It supports various filter types
    including strength thresholds, time ranges, frequency limits, and custom
    functions to create cleaner, higher-quality signal streams.
    
    Args:
        signals: List of signal dictionaries to filter. Each signal should contain
            'timestamp' and 'signal' at minimum. Additional fields like 'strength',
            'method' enable additional filtering options.
        filters: List of filter configuration dictionaries. Each filter must have
            a 'type' field and relevant parameters. Supported filter types:
            
            - strength: Filter by signal strength range
              Parameters: min_strength (default 0), max_strength (default 1)
            - signal_type: Filter by allowed signal types
              Parameters: allowed_signals (list, default ['buy', 'sell'])
            - time_range: Filter by date/time range
              Parameters: start_date, end_date (optional datetime strings)
            - frequency: Remove signals too close together
              Parameters: min_interval_hours (default 24)
            - method: Filter by signal generation method
              Parameters: allowed_methods (list of method names)
            - custom: Apply custom filtering function
              Parameters: function (callable that takes signal dict, returns bool)
              
    Returns:
        Dict[str, Any]: Signal filtering results including:
            - filters_applied: Number of filters applied
            - original_count: Number of signals before filtering
            - final_count: Number of signals after all filters
            - removed_count: Total signals removed
            - removal_percentage: Percentage of signals filtered out
            - filtered_signals: List of signals passing all filters
            - filter_statistics: Detailed breakdown of removals by each filter
            - final_distribution: Signal type distribution after filtering
            - filter_efficiency: Retention rate and final signal statistics
            
    Raises:
        Exception: If signal filtering fails due to invalid filter configuration or data issues.
        
    Example:
        >>> signals = [
        ...     {'timestamp': '2023-01-01 09:00', 'signal': 'buy', 'strength': 0.9},
        ...     {'timestamp': '2023-01-01 10:00', 'signal': 'buy', 'strength': 0.3},  # Low strength
        ...     {'timestamp': '2023-01-01 11:00', 'signal': 'sell', 'strength': 0.8}, # Too frequent
        ...     {'timestamp': '2023-01-03 14:00', 'signal': 'sell', 'strength': 0.7}
        ... ]
        >>> 
        >>> # Apply multiple filters
        >>> filters = [
        ...     {"type": "strength", "min_strength": 0.5},  # Remove weak signals
        ...     {"type": "frequency", "min_interval_hours": 24}  # Space out signals
        ... ]
        >>> filtered = filter_signals(signals, filters)
        >>> print(f"Filtered from {filtered['original_count']} to {filtered['final_count']} signals")
        >>> print(f"Removal rate: {filtered['removal_percentage']:.1f}%")
        >>> 
        >>> # Time range filter example
        >>> time_filter = [{"type": "time_range", "start_date": "2023-01-02", "end_date": "2023-01-31"}]
        >>> recent_signals = filter_signals(signals, time_filter)
        
    Note:
        - Filters applied sequentially in the order provided
        - Each filter operates on the result of the previous filter
        - Frequency filter maintains chronological order and removes later signals
        - Custom filters receive entire signal dictionary for maximum flexibility
        - Time range filters accept various datetime string formats
        - Empty signal lists return gracefully with zero statistics
        - Filter statistics show removal count and criteria for each filter
        - All timestamps converted to pandas datetime for consistent processing
    """
    if not signals:
        return standardize_output({
            "original_count": 0,
            "filtered_signals": [],
            "filter_statistics": {}
        }, "filter_signals")
        
    # Convert to DataFrame for easier filtering
    signals_df = pd.DataFrame(signals)
    signals_df['timestamp'] = pd.to_datetime(signals_df['timestamp'])
    original_count = len(signals_df)
        
    filtered_df = signals_df.copy()
    filter_stats = {}
        
    for filter_config in filters:
        filter_type = filter_config.get("type")
            
        if filter_type == "strength":
            # Filter by signal strength
            min_strength = filter_config.get("min_strength", 0)
            max_strength = filter_config.get("max_strength", 1)
                
            if 'strength' in filtered_df.columns:
                before_count = len(filtered_df)
                filtered_df = filtered_df[
                    (filtered_df['strength'] >= min_strength) & 
                    (filtered_df['strength'] <= max_strength)
                ]
                after_count = len(filtered_df)
                filter_stats["strength_filter"] = {
                    "removed": before_count - after_count,
                    "criteria": f"strength between {min_strength} and {max_strength}"
                }
            
        elif filter_type == "signal_type":
            # Filter by signal type
            allowed_signals = filter_config.get("allowed_signals", ["buy", "sell"])
                
            before_count = len(filtered_df)
            filtered_df = filtered_df[filtered_df['signal'].isin(allowed_signals)]
            after_count = len(filtered_df)
            filter_stats["signal_type_filter"] = {
                "removed": before_count - after_count,
                "criteria": f"signals in {allowed_signals}"
            }
            
        elif filter_type == "time_range":
            # Filter by time range
            start_date = filter_config.get("start_date")
            end_date = filter_config.get("end_date")
                
            before_count = len(filtered_df)
                
            if start_date:
                start_date = pd.to_datetime(start_date)
                filtered_df = filtered_df[filtered_df['timestamp'] >= start_date]
                
            if end_date:
                end_date = pd.to_datetime(end_date)
                filtered_df = filtered_df[filtered_df['timestamp'] <= end_date]
                
            after_count = len(filtered_df)
            filter_stats["time_range_filter"] = {
                "removed": before_count - after_count,
                "criteria": f"time between {start_date} and {end_date}"
            }
            
        elif filter_type == "frequency":
            # Filter by signal frequency (remove too frequent signals)
            min_interval_hours = filter_config.get("min_interval_hours", 24)
                
            before_count = len(filtered_df)
                
            # Sort by timestamp and remove signals that are too close together
            filtered_df = filtered_df.sort_values('timestamp')
                
            keep_indices = []
            last_timestamp = None
                
            for idx, row in filtered_df.iterrows():
                current_timestamp = row['timestamp']
                    
                if last_timestamp is None:
                    keep_indices.append(idx)
                    last_timestamp = current_timestamp
                else:
                    time_diff = (current_timestamp - last_timestamp).total_seconds() / 3600
                    if time_diff >= min_interval_hours:
                        keep_indices.append(idx)
                        last_timestamp = current_timestamp
                
            filtered_df = filtered_df.loc[keep_indices]
            after_count = len(filtered_df)
            filter_stats["frequency_filter"] = {
                "removed": before_count - after_count,
                "criteria": f"minimum {min_interval_hours} hours between signals"
            }
            
        elif filter_type == "method":
            # Filter by signal generation method
            allowed_methods = filter_config.get("allowed_methods", [])
                
            if 'method' in filtered_df.columns and allowed_methods:
                before_count = len(filtered_df)
                filtered_df = filtered_df[filtered_df['method'].isin(allowed_methods)]
                after_count = len(filtered_df)
                filter_stats["method_filter"] = {
                    "removed": before_count - after_count,
                    "criteria": f"methods in {allowed_methods}"
                }
            
        elif filter_type == "custom":
            # Custom filter using provided function
            filter_func = filter_config.get("function")
            if filter_func and callable(filter_func):
                before_count = len(filtered_df)
                mask = filtered_df.apply(filter_func, axis=1)
                filtered_df = filtered_df[mask]
                after_count = len(filtered_df)
                filter_stats["custom_filter"] = {
                    "removed": before_count - after_count,
                    "criteria": "custom function"
                }
        
    # Convert back to list of dictionaries
    filtered_signals = filtered_df.to_dict('records')
        
    # Calculate overall statistics
    final_count = len(filtered_signals)
    total_removed = original_count - final_count
    removal_percentage = (total_removed / original_count * 100) if original_count > 0 else 0
        
    # Signal distribution after filtering
    if filtered_signals:
        signal_distribution = pd.Series([s['signal'] for s in filtered_signals]).value_counts()
    else:
        signal_distribution = pd.Series()
        
    result = {
        "filters_applied": len(filters),
        "original_count": original_count,
        "final_count": final_count,
        "removed_count": total_removed,
        "removal_percentage": float(removal_percentage),
        "filtered_signals": filtered_signals,
        "filter_statistics": filter_stats,
        "final_distribution": signal_distribution.to_dict(),
        "filter_efficiency": {
            "signals_retained": final_count,
            "retention_rate": float((final_count / original_count * 100)) if original_count > 0 else 0
        }
    }
        
    return standardize_output(result, "filter_signals")
        
# Registry of condition detection and signal functions
SIGNAL_GENERATORS_FUNCTIONS = {
    'generate_signals': generate_signals,
    'calculate_signal_frequency': calculate_signal_frequency,
    'combine_signals': combine_signals,
    'filter_signals': filter_signals
}