#!/usr/bin/env python3
"""
Technical Analysis Framework - Shared utilities and decorators for all TA functions.
Single source of truth for error handling, data validation, and response formatting.
"""

import pandas as pd
import numpy as np
import functools
import logging
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime

from ..utils.data_validation import validate_and_convert_data, validate_numeric_columns
from ..utils.format_utils import format_success_response, format_error_response

logger = logging.getLogger(__name__)

# Custom exceptions for technical analysis
class DataQualityError(Exception):
    """Raised when data quality is insufficient for analysis."""
    pass

class InsufficientDataError(Exception):
    """Raised when there's not enough data for the requested analysis."""
    pass

def mcp_resilient(min_periods: int = 1, required_columns: List[str] = None):
    """
    Decorator for resilient technical analysis functions with comprehensive error handling.
    
    Args:
        min_periods: Minimum number of data points required
        required_columns: List of required column names
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Dict[str, Any]:
            function_name = func.__name__
            start_time = datetime.now()
            
            try:
                # Extract data from first argument (assuming it's always data)
                if not args:
                    raise ValueError("No data provided")
                
                data = args[0]
                
                # Validate and convert data
                df = validate_and_convert_data(data, required_columns or ['close'])
                
                # Check minimum periods requirement
                if len(df) < min_periods:
                    raise InsufficientDataError(
                        f"Insufficient data: need at least {min_periods} periods, got {len(df)}"
                    )
                
                # Check data quality
                null_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
                if null_percentage > 20:  # More than 20% null values
                    raise DataQualityError(
                        f"Poor data quality: {null_percentage:.1f}% null values"
                    )
                
                # Replace first argument with validated DataFrame
                new_args = (df,) + args[1:]
                
                # Execute the function
                result = func(*new_args, **kwargs)
                
                # Add metadata to result if it's a dictionary
                if isinstance(result, dict):
                    execution_time = (datetime.now() - start_time).total_seconds()
                    result.update({
                        'function_name': function_name,
                        'execution_time_seconds': execution_time,
                        'data_periods': len(df),
                        'data_quality_score': calculate_data_quality_score(df),
                        'analysis_timestamp': datetime.now().isoformat()
                    })
                
                return result
                
            except (DataQualityError, InsufficientDataError) as e:
                logger.warning(f"{function_name}: {str(e)}")
                return format_error_response(
                    function_name=function_name,
                    error_message=str(e),
                    error_type=type(e).__name__,
                    context={'min_periods': min_periods, 'required_columns': required_columns}
                )
                
            except Exception as e:
                logger.error(f"{function_name}: Unexpected error - {str(e)}")
                return format_error_response(
                    function_name=function_name,
                    error_message=f"Technical analysis failed: {str(e)}",
                    error_type="TechnicalAnalysisError",
                    context={'min_periods': min_periods}
                )
        
        return wrapper
    return decorator

def calculate_data_quality_score(df: pd.DataFrame) -> float:
    """Calculate a data quality score (0-100) based on completeness and consistency."""
    try:
        # Completeness score (based on null values)
        completeness = ((len(df) * len(df.columns)) - df.isnull().sum().sum()) / (len(df) * len(df.columns))
        
        # Consistency score (based on realistic price relationships)
        consistency = 1.0
        if 'high' in df.columns and 'low' in df.columns and 'close' in df.columns:
            # Check for invalid OHLC relationships
            invalid_hlc = ((df['high'] < df['low']) | 
                          (df['close'] > df['high']) | 
                          (df['close'] < df['low'])).sum()
            consistency = max(0, 1 - (invalid_hlc / len(df)))
        
        # Final quality score
        quality_score = (completeness * 0.7 + consistency * 0.3) * 100
        return float(min(100, max(0, quality_score)))
        
    except Exception:
        return 50.0  # Default middle score if calculation fails

def safe_ta_calculation(calculation_func: Callable, *args, **kwargs) -> Any:
    """
    Safely execute a technical analysis calculation with error handling.
    """
    try:
        result = calculation_func(*args, **kwargs)
        
        # Handle pandas Series/DataFrame results
        if hasattr(result, 'dropna'):
            result = result.dropna()
            if len(result) == 0:
                return None
        
        # Check for NaN/infinite values
        if hasattr(result, 'iloc') and len(result) > 0:
            if pd.isna(result.iloc[-1]) or np.isinf(result.iloc[-1]):
                return None
        
        return result
        
    except Exception as e:
        logger.warning(f"Safe TA calculation failed: {str(e)}")
        return None

def standardize_ta_response(
    function_name: str,
    indicator_name: str, 
    current_value: float,
    signal: str,
    data: Dict[str, Any],
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Standardize technical analysis response format across all indicators.
    
    Args:
        function_name: Name of the calling function
        indicator_name: Display name of the indicator (e.g., "RSI", "MACD")
        current_value: Current indicator value
        signal: Signal interpretation (e.g., "overbought", "bullish", "neutral")
        data: Core indicator data and analysis
        metadata: Additional metadata (parameters, etc.)
    
    Returns:
        Standardized response dictionary
    """
    return format_success_response(
        function_name=function_name,
        data={
            'indicator': indicator_name,
            'current_value': float(current_value) if current_value is not None else None,
            'signal': signal,
            **data
        },
        library_used="ta,pandas,numpy",
        parameters=metadata or {}
    )

def detect_crossovers(series1: pd.Series, series2: pd.Series, lookback: int = 50) -> List[Dict]:
    """
    Generic crossover detection between two series.
    
    Args:
        series1: First series (e.g., fast MA)
        series2: Second series (e.g., slow MA)
        lookback: Number of recent crossovers to return
    
    Returns:
        List of crossover events with dates and values
    """
    crossovers = []
    
    # Align series
    aligned = pd.concat([series1, series2], axis=1, keys=['series1', 'series2']).dropna()
    
    if len(aligned) < 2:
        return crossovers
    
    for i in range(1, len(aligned)):
        prev_s1, prev_s2 = aligned.iloc[i-1]
        curr_s1, curr_s2 = aligned.iloc[i]
        
        # Bullish crossover (series1 crosses above series2)
        if prev_s1 <= prev_s2 and curr_s1 > curr_s2:
            crossovers.append({
                'date': aligned.index[i],
                'type': 'bullish_crossover',
                'series1_value': float(curr_s1),
                'series2_value': float(curr_s2)
            })
        
        # Bearish crossover (series1 crosses below series2)
        elif prev_s1 >= prev_s2 and curr_s1 < curr_s2:
            crossovers.append({
                'date': aligned.index[i],
                'type': 'bearish_crossover', 
                'series1_value': float(curr_s1),
                'series2_value': float(curr_s2)
            })
    
    return crossovers[-lookback:] if crossovers else []

def detect_divergences(price_series: pd.Series, indicator_series: pd.Series, 
                      window: int = 20, lookback: int = 10) -> List[Dict]:
    """
    Generic divergence detection between price and indicator.
    
    Args:
        price_series: Price series (usually close prices)
        indicator_series: Indicator series
        window: Window for finding local peaks/troughs
        lookback: Number of recent divergences to return
    
    Returns:
        List of divergence events
    """
    divergences = []
    
    # Find local peaks and troughs
    price_peaks = []
    indicator_peaks = []
    
    for i in range(window, len(price_series) - window):
        # Check for price peak
        if (price_series.iloc[i] == price_series.iloc[i-window:i+window+1].max()):
            price_peaks.append((price_series.index[i], price_series.iloc[i]))
            indicator_peaks.append((indicator_series.index[i], indicator_series.iloc[i]))
    
    # Detect bearish divergence (price higher highs, indicator lower highs)
    if len(price_peaks) >= 2:
        for i in range(1, len(price_peaks)):
            if (price_peaks[i][1] > price_peaks[i-1][1] and 
                indicator_peaks[i][1] < indicator_peaks[i-1][1]):
                
                divergences.append({
                    'date': price_peaks[i][0],
                    'type': 'bearish_divergence',
                    'price': float(price_peaks[i][1]),
                    'indicator': float(indicator_peaks[i][1]),
                    'strength': abs(price_peaks[i][1] - price_peaks[i-1][1]) / price_peaks[i-1][1]
                })
    
    # Find troughs for bullish divergence
    price_troughs = []
    indicator_troughs = []
    
    for i in range(window, len(price_series) - window):
        if (price_series.iloc[i] == price_series.iloc[i-window:i+window+1].min()):
            price_troughs.append((price_series.index[i], price_series.iloc[i]))
            indicator_troughs.append((indicator_series.index[i], indicator_series.iloc[i]))
    
    # Detect bullish divergence (price lower lows, indicator higher lows)
    if len(price_troughs) >= 2:
        for i in range(1, len(price_troughs)):
            if (price_troughs[i][1] < price_troughs[i-1][1] and 
                indicator_troughs[i][1] > indicator_troughs[i-1][1]):
                
                divergences.append({
                    'date': price_troughs[i][0],
                    'type': 'bullish_divergence',
                    'price': float(price_troughs[i][1]),
                    'indicator': float(indicator_troughs[i][1]),
                    'strength': abs(price_troughs[i-1][1] - price_troughs[i][1]) / price_troughs[i-1][1]
                })
    
    return divergences[-lookback:] if divergences else []

def calculate_signal_strength(signals: List[str]) -> str:
    """
    Calculate overall signal strength from multiple individual signals.
    
    Args:
        signals: List of signal strings
    
    Returns:
        Overall signal strength ('strong', 'moderate', 'weak', 'none')
    """
    if not signals:
        return 'none'
    
    # Count signal types
    bullish_signals = sum(1 for s in signals if any(word in s.lower() 
                         for word in ['bullish', 'buy', 'oversold', 'support']))
    bearish_signals = sum(1 for s in signals if any(word in s.lower() 
                         for word in ['bearish', 'sell', 'overbought', 'resistance']))
    
    total_signals = len(signals)
    
    # Determine strength based on signal count and consensus
    if total_signals >= 3:
        if abs(bullish_signals - bearish_signals) >= 2:
            return 'strong'
        else:
            return 'moderate'
    elif total_signals >= 1:
        return 'moderate' if abs(bullish_signals - bearish_signals) >= 1 else 'weak'
    else:
        return 'weak'

def generate_trading_recommendation(signals: List[str], confidence: str) -> str:
    """
    Generate actionable trading recommendation based on signals and confidence.
    
    Args:
        signals: List of trading signals
        confidence: Confidence level ('high', 'medium', 'low')
    
    Returns:
        Trading recommendation string
    """
    if not signals:
        return "No clear signals - stay neutral"
    
    bullish_count = sum(1 for s in signals if any(word in s.lower() 
                       for word in ['bullish', 'buy', 'oversold']))
    bearish_count = sum(1 for s in signals if any(word in s.lower() 
                       for word in ['bearish', 'sell', 'overbought']))
    
    if bullish_count > bearish_count:
        if confidence == 'high':
            return "Strong buy signal - high confidence"
        elif confidence == 'medium':
            return "Buy signal - moderate confidence"
        else:
            return "Weak buy signal - low confidence"
    elif bearish_count > bullish_count:
        if confidence == 'high':
            return "Strong sell signal - high confidence"
        elif confidence == 'medium':
            return "Sell signal - moderate confidence"
        else:
            return "Weak sell signal - low confidence"
    else:
        return "Mixed signals - wait for confirmation"