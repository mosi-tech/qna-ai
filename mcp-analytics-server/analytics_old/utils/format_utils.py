"""
Output formatting utilities for MCP analytics server.
Provides consistent response formatting across all analytics functions.
"""

from typing import Dict, Any, Optional, List, Union
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def format_success_response(function_name: str, data: Any, library_used: str, 
                           parameters: Dict = None, additional_metadata: Dict = None) -> Dict:
    """
    Format consistent success response structure for analytics functions.
    
    Args:
        function_name: Name of the analytics function
        data: Main result data to return
        library_used: Libraries/methods used for calculation
        parameters: Input parameters used
        additional_metadata: Extra metadata to include
        
    Returns:
        dict: Standardized success response
    """
    response = {
        "success": True,
        "data": data,
        "metadata": {
            "function": function_name,
            "library_used": library_used,
            "timestamp": datetime.now().isoformat(),
            "parameters": parameters or {}
        }
    }
    
    # Add additional metadata if provided
    if additional_metadata:
        response["metadata"].update(additional_metadata)
    
    return response

def format_error_response(function_name: str, error_message: str, 
                         context: Dict = None, error_type: str = "AnalyticsError") -> Dict:
    """
    Format consistent error response structure for analytics functions.
    
    Args:
        function_name: Name of the analytics function that failed
        error_message: Error description
        context: Additional context about the error
        error_type: Type/category of error
        
    Returns:
        dict: Standardized error response
    """
    response = {
        "success": False,
        "error": error_message,
        "error_type": error_type,
        "function": function_name,
        "timestamp": datetime.now().isoformat()
    }
    
    if context:
        response["context"] = context
    
    logger.error(f"Function {function_name} failed: {error_message}")
    
    return response

def format_signal_data(signals: List[Dict], confidence_scores: List[float] = None, 
                      metadata: Dict = None) -> Dict:
    """
    Format trading signal data consistently across functions.
    
    Args:
        signals: List of signal dictionaries
        confidence_scores: Optional confidence scores for each signal
        metadata: Additional signal metadata
        
    Returns:
        dict: Formatted signal data structure
    """
    formatted_signals = []
    
    for i, signal in enumerate(signals):
        formatted_signal = {
            "signal_id": i + 1,
            "type": signal.get("type", "unknown"),
            "strength": signal.get("strength", 0.0),
            "timestamp": signal.get("timestamp", datetime.now().isoformat()),
            "symbol": signal.get("symbol", ""),
            "price_level": signal.get("price_level", 0.0),
            "details": {k: v for k, v in signal.items() 
                       if k not in ["type", "strength", "timestamp", "symbol", "price_level"]}
        }
        
        # Add confidence score if provided
        if confidence_scores and i < len(confidence_scores):
            formatted_signal["confidence"] = confidence_scores[i]
        
        formatted_signals.append(formatted_signal)
    
    result = {
        "signals": formatted_signals,
        "signal_count": len(formatted_signals),
        "summary": {
            "total_signals": len(formatted_signals),
            "bullish_signals": len([s for s in formatted_signals if "bullish" in s.get("type", "").lower()]),
            "bearish_signals": len([s for s in formatted_signals if "bearish" in s.get("type", "").lower()]),
            "average_strength": sum(s.get("strength", 0) for s in formatted_signals) / len(formatted_signals) if formatted_signals else 0
        }
    }
    
    if metadata:
        result["metadata"] = metadata
    
    return result

def format_portfolio_metrics(metrics: Dict, positions_count: int = 0, 
                            total_value: float = 0.0) -> Dict:
    """
    Format portfolio analysis metrics consistently.
    
    Args:
        metrics: Portfolio metrics dictionary
        positions_count: Number of positions in portfolio
        total_value: Total portfolio value
        
    Returns:
        dict: Formatted portfolio metrics
    """
    formatted_metrics = {
        "portfolio_summary": {
            "total_positions": positions_count,
            "total_value": round(total_value, 2),
            "currency": "USD"
        },
        "risk_metrics": {},
        "performance_metrics": {},
        "concentration_metrics": {},
        "detailed_metrics": metrics
    }
    
    # Categorize metrics by type
    risk_keys = ["var", "volatility", "beta", "sharpe_ratio", "max_drawdown", "downside_deviation"]
    performance_keys = ["total_return", "annualized_return", "alpha", "information_ratio", "calmar_ratio"]
    concentration_keys = ["hhi", "concentration", "largest_position", "top_5_concentration"]
    
    for key, value in metrics.items():
        key_lower = key.lower()
        if any(risk_key in key_lower for risk_key in risk_keys):
            formatted_metrics["risk_metrics"][key] = value
        elif any(perf_key in key_lower for perf_key in performance_keys):
            formatted_metrics["performance_metrics"][key] = value
        elif any(conc_key in key_lower for conc_key in concentration_keys):
            formatted_metrics["concentration_metrics"][key] = value
    
    return formatted_metrics

def format_technical_analysis_result(indicator_name: str, current_value: float, 
                                   signal: str, historical_data: List = None,
                                   support_resistance: Dict = None) -> Dict:
    """
    Format technical analysis results consistently.
    
    Args:
        indicator_name: Name of the technical indicator
        current_value: Current indicator value
        signal: Trading signal (bullish/bearish/neutral)
        historical_data: Historical indicator values
        support_resistance: Support and resistance levels
        
    Returns:
        dict: Formatted technical analysis result
    """
    result = {
        "indicator": indicator_name,
        "current_value": round(current_value, 4) if isinstance(current_value, (int, float)) else current_value,
        "signal": signal.lower() if isinstance(signal, str) else "neutral",
        "signal_strength": _calculate_signal_strength(signal),
        "interpretation": _get_signal_interpretation(indicator_name, signal)
    }
    
    if historical_data:
        result["historical_values"] = [round(val, 4) if isinstance(val, (int, float)) else val 
                                     for val in historical_data[-10:]]  # Last 10 values
    
    if support_resistance:
        result["levels"] = support_resistance
    
    return result

def format_backtest_results(strategy_name: str, returns: List[float], 
                           benchmark_returns: List[float] = None,
                           trades: List[Dict] = None, metrics: Dict = None) -> Dict:
    """
    Format backtesting results consistently.
    
    Args:
        strategy_name: Name of the trading strategy
        returns: Strategy returns list
        benchmark_returns: Benchmark returns for comparison
        trades: List of individual trades
        metrics: Strategy performance metrics
        
    Returns:
        dict: Formatted backtest results
    """
    import numpy as np
    
    total_return = ((1 + np.array(returns)).prod() - 1) * 100 if returns else 0
    win_rate = 0
    avg_win = 0
    avg_loss = 0
    
    if trades:
        winning_trades = [t for t in trades if t.get("pnl", 0) > 0]
        losing_trades = [t for t in trades if t.get("pnl", 0) < 0]
        
        win_rate = len(winning_trades) / len(trades) * 100 if trades else 0
        avg_win = np.mean([t["pnl"] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t["pnl"] for t in losing_trades]) if losing_trades else 0
    
    result = {
        "strategy_name": strategy_name,
        "performance_summary": {
            "total_return_percent": round(total_return, 2),
            "total_trades": len(trades) if trades else 0,
            "win_rate_percent": round(win_rate, 2),
            "average_win": round(avg_win, 2),
            "average_loss": round(avg_loss, 2),
            "profit_factor": round(abs(avg_win / avg_loss), 2) if avg_loss != 0 else float('inf')
        },
        "detailed_metrics": metrics or {}
    }
    
    if benchmark_returns:
        benchmark_total_return = ((1 + np.array(benchmark_returns)).prod() - 1) * 100
        result["benchmark_comparison"] = {
            "benchmark_total_return_percent": round(benchmark_total_return, 2),
            "excess_return_percent": round(total_return - benchmark_total_return, 2),
            "outperformed_benchmark": total_return > benchmark_total_return
        }
    
    if trades:
        result["trade_history"] = trades[-20:]  # Last 20 trades
    
    return result

def format_correlation_analysis(correlation_matrix: Dict, significance_tests: Dict = None,
                               strong_correlations: List[Dict] = None) -> Dict:
    """
    Format correlation analysis results consistently.
    
    Args:
        correlation_matrix: Correlation matrix as dict
        significance_tests: P-values for correlations
        strong_correlations: List of notable correlations
        
    Returns:
        dict: Formatted correlation analysis
    """
    result = {
        "correlation_matrix": correlation_matrix,
        "summary": {
            "assets_analyzed": len(correlation_matrix.keys()) if correlation_matrix else 0,
            "highest_correlation": 0,
            "lowest_correlation": 0,
            "average_correlation": 0
        }
    }
    
    # Calculate summary statistics
    if correlation_matrix:
        all_correlations = []
        for asset1, correlations in correlation_matrix.items():
            for asset2, corr in correlations.items():
                if asset1 != asset2 and isinstance(corr, (int, float)):
                    all_correlations.append(corr)
        
        if all_correlations:
            result["summary"]["highest_correlation"] = round(max(all_correlations), 4)
            result["summary"]["lowest_correlation"] = round(min(all_correlations), 4)
            result["summary"]["average_correlation"] = round(sum(all_correlations) / len(all_correlations), 4)
    
    if significance_tests:
        result["significance_tests"] = significance_tests
    
    if strong_correlations:
        result["notable_correlations"] = strong_correlations
    
    return result

def _calculate_signal_strength(signal: str) -> float:
    """Calculate numeric signal strength from text signal."""
    signal_lower = signal.lower() if isinstance(signal, str) else ""
    
    if "strong" in signal_lower:
        return 0.8
    elif "bullish" in signal_lower or "bearish" in signal_lower:
        return 0.6
    elif "weak" in signal_lower:
        return 0.3
    elif "neutral" in signal_lower:
        return 0.0
    else:
        return 0.5

def _get_signal_interpretation(indicator_name: str, signal: str) -> str:
    """Get human-readable interpretation of technical signals."""
    interpretations = {
        "rsi": {
            "bullish": "RSI indicates oversold conditions, potential buying opportunity",
            "bearish": "RSI indicates overbought conditions, potential selling opportunity",
            "neutral": "RSI in neutral range, no clear directional bias"
        },
        "macd": {
            "bullish": "MACD showing bullish momentum, uptrend likely to continue",
            "bearish": "MACD showing bearish momentum, downtrend likely to continue", 
            "neutral": "MACD showing mixed signals, trend unclear"
        },
        "bollinger": {
            "bullish": "Price near lower Bollinger Band, potential mean reversion upward",
            "bearish": "Price near upper Bollinger Band, potential mean reversion downward",
            "neutral": "Price within normal Bollinger Band range"
        }
    }
    
    indicator_key = indicator_name.lower()
    for key in interpretations:
        if key in indicator_key:
            return interpretations[key].get(signal.lower(), "No interpretation available")
    
    return f"{signal.title()} signal detected for {indicator_name}"

def sanitize_for_json(obj: Any) -> Any:
    """
    Sanitize data structure for JSON serialization.
    
    Args:
        obj: Object to sanitize
        
    Returns:
        JSON-serializable object
    """
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    elif hasattr(obj, 'isoformat'):  # datetime objects
        return obj.isoformat()
    elif hasattr(obj, 'item'):  # numpy scalars
        return obj.item()
    elif str(type(obj)).startswith('<class \'numpy.'):  # numpy arrays
        return obj.tolist() if hasattr(obj, 'tolist') else str(obj)
    elif obj != obj:  # NaN check
        return None
    elif obj == float('inf') or obj == float('-inf'):
        return None
    else:
        return obj