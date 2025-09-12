"""
Trend analysis module using linear regression and technical indicators.
Refactored to use utility framework and eliminate code duplication.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from scipy import stats

# Import utility modules for standardized operations
from ..utils.data_validation import validate_and_convert_data, validate_numeric_columns
from ..utils.format_utils import format_success_response, format_error_response
from ..utils.technical_utils import calculate_trend_strength


class TrendAnalyzer:
    """Analyze price trends using various technical methods."""
    
    @staticmethod
    def linear_trend_analysis(prices: List[float], timestamps: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Perform linear regression trend analysis on price series.
        Refactored to use utility framework.
        
        Args:
            prices: List of closing prices
            timestamps: Optional list of timestamps
            
        Returns:
            Dictionary with comprehensive trend analysis
        """
        try:
            # Use utility for data validation and conversion
            df = validate_and_convert_data(prices, required_columns=None)
            if isinstance(df, pd.DataFrame):
                price_series = df.iloc[:, 0]  # Take first column
            else:
                price_series = pd.Series(prices)
            
            if len(price_series) < 10:
                return format_error_response(
                    function_name="linear_trend_analysis",
                    error_message="Insufficient data for trend analysis (minimum 10 points)",
                    context={"data_length": len(price_series)}
                )
            
            # Create time series
            x = np.arange(len(price_series))
            y = price_series.values
            
            # Remove any NaN values
            mask = ~np.isnan(y)
            x_clean = x[mask]
            y_clean = y[mask]
            
            if len(y_clean) < 10:
                return format_error_response(
                    function_name="linear_trend_analysis",
                    error_message="Insufficient clean data after removing NaN values",
                    context={"clean_data_length": len(y_clean)}
                )
            
            # Linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_clean, y_clean)
            
            # Calculate trend metrics
            angle_rad = np.arctan(slope)
            angle_deg = np.degrees(angle_rad)
            
            # Trend classification
            trend_category = TrendAnalyzer._classify_trend_angle(angle_deg)
            trend_strength = TrendAnalyzer._classify_trend_strength(r_value ** 2)
            
            # Calculate total return and annualized slope
            total_return = ((y_clean[-1] - y_clean[0]) / y_clean[0]) * 100
            daily_slope_percent = (slope / np.mean(y_clean)) * 100
            
            # Calculate trend line values
            trend_line = slope * x_clean + intercept
            residuals = y_clean - trend_line
            
            # Additional metrics
            trend_consistency = 1 - (np.std(residuals) / np.mean(y_clean))
            
            return {
                "slope": float(slope),
                "slope_percent_daily": float(daily_slope_percent),
                "intercept": float(intercept),
                "r_squared": float(r_value ** 2),
                "r_value": float(r_value),
                "p_value": float(p_value),
                "std_error": float(std_err),
                "trend_angle_degrees": float(angle_deg),
                "trend_category": trend_category,
                "trend_strength": trend_strength,
                "total_return_percent": float(total_return),
                "trend_consistency": float(trend_consistency),
                "statistical_significance": "Significant" if p_value < 0.05 else "Not significant",
                "trend_line_values": trend_line.tolist(),
                "residuals": residuals.tolist(),
                "mean_absolute_error": float(np.mean(np.abs(residuals))),
                "direction": "Upward" if slope > 0 else "Downward" if slope < 0 else "Sideways",
                "observations": len(y_clean)
            }
        
        except Exception as e:
            return format_error_response(
                function_name="linear_trend_analysis",
                error_message=str(e),
                context={"input_length": len(prices) if hasattr(prices, '__len__') else 0}
            )
    
    @staticmethod
    def trend_breakout_analysis(prices: List[float], window: int = 20) -> Dict[str, Any]:
        """
        Analyze trend breakouts and breakdowns.
        
        Args:
            prices: List of closing prices
            window: Window size for trend channel calculation
            
        Returns:
            Dictionary with breakout analysis
        """
        if len(prices) < window * 2:
            return {"error": f"Insufficient data: need at least {window * 2} observations"}
        
        price_series = pd.Series(prices)
        
        # Calculate rolling max and min for trend channel
        rolling_max = price_series.rolling(window=window).max()
        rolling_min = price_series.rolling(window=window).min()
        
        # Calculate trend channel width
        channel_width = ((rolling_max - rolling_min) / rolling_max) * 100
        
        # Identify breakouts (price above recent high)
        breakouts = []
        breakdowns = []
        
        for i in range(window, len(prices)):
            current_price = prices[i]
            recent_high = rolling_max.iloc[i-1]  # Previous window high
            recent_low = rolling_min.iloc[i-1]   # Previous window low
            
            if current_price > recent_high:
                breakout_strength = ((current_price - recent_high) / recent_high) * 100
                breakouts.append({
                    "index": i,
                    "price": current_price,
                    "previous_high": recent_high,
                    "breakout_strength": breakout_strength
                })
            
            if current_price < recent_low:
                breakdown_strength = ((recent_low - current_price) / recent_low) * 100
                breakdowns.append({
                    "index": i,
                    "price": current_price,
                    "previous_low": recent_low,
                    "breakdown_strength": breakdown_strength
                })
        
        # Calculate success rates (follow-through after breakouts)
        successful_breakouts = 0
        successful_breakdowns = 0
        
        for breakout in breakouts:
            # Check if price continued higher in next 5 days
            start_idx = breakout["index"]
            if start_idx + 5 < len(prices):
                future_prices = prices[start_idx+1:start_idx+6]
                if max(future_prices) > breakout["price"]:
                    successful_breakouts += 1
        
        for breakdown in breakdowns:
            # Check if price continued lower in next 5 days
            start_idx = breakdown["index"]
            if start_idx + 5 < len(prices):
                future_prices = prices[start_idx+1:start_idx+6]
                if min(future_prices) < breakdown["price"]:
                    successful_breakdowns += 1
        
        return {
            "breakouts": breakouts[-10:],  # Last 10 breakouts
            "breakdowns": breakdowns[-10:],  # Last 10 breakdowns
            "total_breakouts": len(breakouts),
            "total_breakdowns": len(breakdowns),
            "breakout_success_rate": (successful_breakouts / len(breakouts) * 100) if breakouts else 0,
            "breakdown_success_rate": (successful_breakdowns / len(breakdowns) * 100) if breakdowns else 0,
            "avg_channel_width": float(channel_width.mean()),
            "current_channel_width": float(channel_width.iloc[-1]),
            "trend_volatility": "High" if channel_width.mean() > 5 else "Medium" if channel_width.mean() > 2 else "Low",
            "window_size": window
        }
    
    @staticmethod
    def trend_momentum_analysis(prices: List[float], short_window: int = 10, long_window: int = 30) -> Dict[str, Any]:
        """
        Analyze trend momentum using rate of change.
        
        Args:
            prices: List of closing prices
            short_window: Short-term momentum window
            long_window: Long-term momentum window
            
        Returns:
            Dictionary with momentum analysis
        """
        if len(prices) < long_window:
            return {"error": f"Insufficient data: need at least {long_window} observations"}
        
        price_series = pd.Series(prices)
        
        # Calculate rate of change for different periods
        roc_short = price_series.pct_change(periods=short_window) * 100
        roc_long = price_series.pct_change(periods=long_window) * 100
        
        # Calculate momentum divergence
        momentum_divergence = roc_short - roc_long
        
        # Calculate acceleration (second derivative)
        price_velocity = price_series.pct_change() * 100
        price_acceleration = price_velocity.diff()
        
        # Identify momentum phases
        current_short_momentum = roc_short.iloc[-1]
        current_long_momentum = roc_long.iloc[-1]
        current_divergence = momentum_divergence.iloc[-1]
        
        # Momentum classification
        momentum_phase = TrendAnalyzer._classify_momentum_phase(
            current_short_momentum, current_long_momentum, current_divergence
        )
        
        return {
            "short_term_momentum": float(current_short_momentum),
            "long_term_momentum": float(current_long_momentum),
            "momentum_divergence": float(current_divergence),
            "momentum_phase": momentum_phase,
            "current_acceleration": float(price_acceleration.iloc[-1]),
            "avg_acceleration": float(price_acceleration.mean()),
            "momentum_consistency": {
                "short_term_positive_periods": int(sum(roc_short > 0)),
                "long_term_positive_periods": int(sum(roc_long > 0)),
                "divergence_positive_periods": int(sum(momentum_divergence > 0))
            },
            "momentum_strength": "Strong" if abs(current_short_momentum) > 2 else "Medium" if abs(current_short_momentum) > 0.5 else "Weak",
            "trend_sustainability": "High" if current_short_momentum * current_long_momentum > 0 else "Low",
            "short_window": short_window,
            "long_window": long_window
        }
    
    @staticmethod
    def trend_reversal_signals(prices: List[float], window: int = 14) -> Dict[str, Any]:
        """
        Identify potential trend reversal signals.
        
        Args:
            prices: List of closing prices
            window: Window size for calculations
            
        Returns:
            Dictionary with reversal signal analysis
        """
        if len(prices) < window * 3:
            return {"error": f"Insufficient data for reversal analysis"}
        
        price_series = pd.Series(prices)
        
        # Calculate various reversal indicators
        
        # 1. Divergence between price and momentum
        momentum = price_series.pct_change(periods=window) * 100
        price_trend = price_series.rolling(window=window).mean()
        
        # 2. Exhaustion signals (extreme moves followed by consolidation)
        daily_returns = price_series.pct_change() * 100
        rolling_vol = daily_returns.rolling(window=window).std()
        extreme_moves = abs(daily_returns) > rolling_vol * 2
        
        # 3. Support/resistance tests
        rolling_high = price_series.rolling(window=window).max()
        rolling_low = price_series.rolling(window=window).min()
        
        resistance_tests = price_series >= rolling_high * 0.99  # Within 1% of high
        support_tests = price_series <= rolling_low * 1.01      # Within 1% of low
        
        # Recent signals
        recent_extreme_moves = int(extreme_moves.tail(5).sum())
        recent_resistance_tests = int(resistance_tests.tail(5).sum())
        recent_support_tests = int(support_tests.tail(5).sum())
        
        # Reversal probability scoring
        reversal_score = 0
        current_price = prices[-1]
        recent_high = rolling_high.iloc[-1]
        recent_low = rolling_low.iloc[-1]
        
        # Price near resistance
        if current_price >= recent_high * 0.98:
            reversal_score += 25
            
        # Price near support
        if current_price <= recent_low * 1.02:
            reversal_score += 25
            
        # Recent extreme volatility
        if recent_extreme_moves >= 2:
            reversal_score += 20
            
        # Momentum divergence
        if len(momentum) > 10:
            recent_momentum = momentum.tail(5).mean()
            if abs(recent_momentum) < momentum.std() * 0.5:  # Low momentum
                reversal_score += 15
        
        # Multiple tests of same level
        if recent_resistance_tests >= 2 or recent_support_tests >= 2:
            reversal_score += 15
        
        return {
            "reversal_probability_score": min(reversal_score, 100),  # Cap at 100
            "reversal_signal_strength": "Strong" if reversal_score > 60 else "Medium" if reversal_score > 30 else "Weak",
            "recent_extreme_moves": recent_extreme_moves,
            "recent_resistance_tests": recent_resistance_tests,
            "recent_support_tests": recent_support_tests,
            "distance_from_high_percent": float(((recent_high - current_price) / recent_high) * 100),
            "distance_from_low_percent": float(((current_price - recent_low) / recent_low) * 100),
            "current_momentum": float(momentum.iloc[-1]) if len(momentum) > 0 else 0,
            "momentum_strength": "High" if abs(momentum.iloc[-1]) > momentum.std() else "Low",
            "key_levels": {
                "resistance": float(recent_high),
                "support": float(recent_low),
                "current_price": float(current_price)
            }
        }
    
    @staticmethod
    def _classify_trend_angle(angle_degrees: float) -> str:
        """Classify trend based on angle."""
        if angle_degrees > 45:
            return "steep_upward"
        elif angle_degrees > 15:
            return "moderate_upward"
        elif angle_degrees > -15:
            return "sideways"
        elif angle_degrees > -45:
            return "moderate_downward"
        else:
            return "steep_downward"
    
    @staticmethod
    def _classify_trend_strength(r_squared: float) -> str:
        """Classify trend strength based on R-squared."""
        if r_squared > 0.8:
            return "very_strong"
        elif r_squared > 0.6:
            return "strong"
        elif r_squared > 0.4:
            return "moderate"
        elif r_squared > 0.2:
            return "weak"
        else:
            return "very_weak"
    
    @staticmethod
    def _classify_momentum_phase(short_mom: float, long_mom: float, divergence: float) -> str:
        """Classify momentum phase."""
        if short_mom > 0 and long_mom > 0:
            if divergence > 0:
                return "accelerating_uptrend"
            else:
                return "decelerating_uptrend"
        elif short_mom < 0 and long_mom < 0:
            if divergence < 0:
                return "accelerating_downtrend"
            else:
                return "decelerating_downtrend"
        elif short_mom > 0 and long_mom < 0:
            return "early_uptrend_reversal"
        elif short_mom < 0 and long_mom > 0:
            return "early_downtrend_reversal"
        else:
            return "sideways_momentum"