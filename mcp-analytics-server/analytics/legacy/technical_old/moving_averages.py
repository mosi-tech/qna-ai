"""
Moving averages and related technical indicators.
Refactored to use utility framework and eliminate code duplication.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional

# Import utility modules for standardized operations
from ..utils.data_validation import validate_and_convert_data, validate_numeric_columns
from ..utils.format_utils import format_success_response, format_error_response
from ..utils.technical_utils import calculate_trend_strength


class MovingAverages:
    """Calculate various moving averages and related technical indicators."""
    
    @staticmethod
    def simple_moving_average(prices: List[float], window: int = 20) -> Dict[str, Any]:
        """
        Calculate Simple Moving Average (SMA).
        Refactored to use utility framework.
        
        Args:
            prices: List of closing prices
            window: Moving average window size
            
        Returns:
            Dictionary with SMA analysis
        """
        try:
            # Use utility for data validation and conversion
            df = validate_and_convert_data(prices, required_columns=None)
            if isinstance(df, pd.DataFrame):
                price_series = df.iloc[:, 0]  # Take first column
            else:
                price_series = pd.Series(prices)
            
            if len(price_series) < window:
                return format_error_response(
                    function_name="simple_moving_average",
                    error_message=f"Insufficient data: need at least {window} observations",
                    context={"data_length": len(price_series), "required": window}
                )
            
            sma = price_series.rolling(window=window).mean()
            sma_clean = sma.dropna()
            
            if sma_clean.empty:
                return format_error_response(
                    function_name="simple_moving_average",
                    error_message="No valid SMA calculations",
                    context={"window": window}
                )
            
            # Calculate price position relative to SMA
            current_price = prices[-1]
            current_sma = sma_clean.iloc[-1]
            price_vs_sma = ((current_price - current_sma) / current_sma) * 100
            
            # Count periods above/below SMA
            above_sma = sum(1 for i, price in enumerate(prices[-len(sma_clean):]) if price > sma_clean.iloc[i])
            below_sma = len(sma_clean) - above_sma
            
            # Calculate SMA slope (trend direction)
            sma_slope = (sma_clean.iloc[-1] - sma_clean.iloc[-5]) / 5 if len(sma_clean) >= 5 else 0
            sma_slope_percent = (sma_slope / sma_clean.iloc[-5]) * 100 if len(sma_clean) >= 5 and sma_clean.iloc[-5] != 0 else 0
            
            analysis_data = {
                "sma_values": sma_clean.tolist(),
                "current_sma": float(current_sma),
                "current_price": float(current_price),
                "price_vs_sma_percent": float(price_vs_sma),
                "price_position": "Above SMA" if price_vs_sma > 0 else "Below SMA",
                "periods_above_sma": above_sma,
                "periods_below_sma": below_sma,
                "above_sma_percentage": (above_sma / len(sma_clean)) * 100,
                "sma_slope": float(sma_slope),
                "sma_slope_percent": float(sma_slope_percent),
                "sma_trend": "Rising" if sma_slope > 0 else "Falling" if sma_slope < 0 else "Flat",
                "observations": len(sma_clean)
            }
            
            return format_success_response(
                function_name="simple_moving_average",
                data=analysis_data,
                library_used="pandas",
                parameters={"window": window}
            )
            
        except Exception as e:
            return format_error_response(
                function_name="simple_moving_average", 
                error_message=str(e),
                context={"window": window}
            )
    
    @staticmethod
    def exponential_moving_average(prices: List[float], window: int = 20, alpha: Optional[float] = None) -> Dict[str, Any]:
        """
        Calculate Exponential Moving Average (EMA).
        
        Args:
            prices: List of closing prices
            window: EMA window size
            alpha: Smoothing factor (if None, uses 2/(window+1))
            
        Returns:
            Dictionary with EMA analysis
        """
        if len(prices) < window:
            return {"error": f"Insufficient data: need at least {window} observations"}
        
        if alpha is None:
            alpha = 2.0 / (window + 1)
        
        price_series = pd.Series(prices)
        ema = price_series.ewm(alpha=alpha, adjust=False).mean()
        
        # Calculate EMA metrics similar to SMA
        current_price = prices[-1]
        current_ema = ema.iloc[-1]
        price_vs_ema = ((current_price - current_ema) / current_ema) * 100
        
        # Count periods above/below EMA
        above_ema = sum(1 for i, price in enumerate(prices) if price > ema.iloc[i])
        below_ema = len(prices) - above_ema
        
        # EMA slope
        ema_slope = (ema.iloc[-1] - ema.iloc[-5]) / 5 if len(ema) >= 5 else 0
        ema_slope_percent = (ema_slope / ema.iloc[-5]) * 100 if len(ema) >= 5 and ema.iloc[-5] != 0 else 0
        
        return {
            "ema_values": ema.tolist(),
            "current_ema": float(current_ema),
            "current_price": float(current_price),
            "price_vs_ema_percent": float(price_vs_ema),
            "price_position": "Above EMA" if price_vs_ema > 0 else "Below EMA",
            "periods_above_ema": above_ema,
            "periods_below_ema": below_ema,
            "above_ema_percentage": (above_ema / len(prices)) * 100,
            "ema_slope": float(ema_slope),
            "ema_slope_percent": float(ema_slope_percent),
            "ema_trend": "Rising" if ema_slope > 0 else "Falling" if ema_slope < 0 else "Flat",
            "alpha": alpha,
            "window": window,
            "observations": len(ema)
        }
    
    @staticmethod
    def moving_average_crossovers(prices: List[float], short_window: int = 10, long_window: int = 30) -> Dict[str, Any]:
        """
        Analyze moving average crossovers between short and long-term MAs.
        
        Args:
            prices: List of closing prices
            short_window: Short-term MA window
            long_window: Long-term MA window
            
        Returns:
            Dictionary with crossover analysis
        """
        if len(prices) < long_window:
            return {"error": f"Insufficient data: need at least {long_window} observations"}
        
        price_series = pd.Series(prices)
        
        # Calculate both MAs
        short_ma = price_series.rolling(window=short_window).mean()
        long_ma = price_series.rolling(window=long_window).mean()
        
        # Remove NaN values
        valid_idx = ~(short_ma.isna() | long_ma.isna())
        short_ma_clean = short_ma[valid_idx]
        long_ma_clean = long_ma[valid_idx]
        
        if len(short_ma_clean) < 10:
            return {"error": "Insufficient clean data for crossover analysis"}
        
        # Calculate crossovers
        ma_diff = short_ma_clean - long_ma_clean
        crossovers = []
        
        for i in range(1, len(ma_diff)):
            if ma_diff.iloc[i-1] <= 0 and ma_diff.iloc[i] > 0:
                # Golden cross (bullish)
                crossovers.append({
                    "type": "golden_cross",
                    "index": i + long_window - 1,  # Adjust for original index
                    "short_ma": float(short_ma_clean.iloc[i]),
                    "long_ma": float(long_ma_clean.iloc[i]),
                    "signal": "bullish"
                })
            elif ma_diff.iloc[i-1] >= 0 and ma_diff.iloc[i] < 0:
                # Death cross (bearish)
                crossovers.append({
                    "type": "death_cross",
                    "index": i + long_window - 1,  # Adjust for original index
                    "short_ma": float(short_ma_clean.iloc[i]),
                    "long_ma": float(long_ma_clean.iloc[i]),
                    "signal": "bearish"
                })
        
        # Current status
        current_diff = ma_diff.iloc[-1]
        current_status = "bullish" if current_diff > 0 else "bearish"
        
        # Calculate crossover success rates (simplified)
        golden_crosses = [c for c in crossovers if c["type"] == "golden_cross"]
        death_crosses = [c for c in crossovers if c["type"] == "death_cross"]
        
        return {
            "crossovers": crossovers[-10:],  # Last 10 crossovers
            "total_crossovers": len(crossovers),
            "golden_crosses": len(golden_crosses),
            "death_crosses": len(death_crosses),
            "current_status": current_status,
            "current_ma_spread": float(current_diff),
            "current_ma_spread_percent": float((current_diff / long_ma_clean.iloc[-1]) * 100),
            "short_ma_current": float(short_ma_clean.iloc[-1]),
            "long_ma_current": float(long_ma_clean.iloc[-1]),
            "short_window": short_window,
            "long_window": long_window,
            "recent_crossover": crossovers[-1] if crossovers else None
        }
    
    @staticmethod
    def moving_average_envelope(prices: List[float], window: int = 20, envelope_percent: float = 2.0) -> Dict[str, Any]:
        """
        Calculate moving average envelope (MA with upper and lower bands).
        
        Args:
            prices: List of closing prices
            window: MA window size
            envelope_percent: Envelope percentage (e.g., 2.0 for ±2%)
            
        Returns:
            Dictionary with envelope analysis
        """
        if len(prices) < window:
            return {"error": f"Insufficient data: need at least {window} observations"}
        
        price_series = pd.Series(prices)
        ma = price_series.rolling(window=window).mean()
        
        # Calculate envelope bands
        envelope_factor = envelope_percent / 100
        upper_band = ma * (1 + envelope_factor)
        lower_band = ma * (1 - envelope_factor)
        
        # Remove NaN values
        valid_idx = ~ma.isna()
        ma_clean = ma[valid_idx]
        upper_clean = upper_band[valid_idx]
        lower_clean = lower_band[valid_idx]
        prices_clean = price_series[valid_idx]
        
        if len(ma_clean) < 5:
            return {"error": "Insufficient clean data for envelope analysis"}
        
        # Analyze price position within envelope
        above_upper = sum(1 for i, price in enumerate(prices_clean) if price > upper_clean.iloc[i])
        below_lower = sum(1 for i, price in enumerate(prices_clean) if price < lower_clean.iloc[i])
        within_envelope = len(prices_clean) - above_upper - below_lower
        
        # Current position
        current_price = prices[-1]
        current_ma = ma_clean.iloc[-1]
        current_upper = upper_clean.iloc[-1]
        current_lower = lower_clean.iloc[-1]
        
        if current_price > current_upper:
            position = "Above upper band"
            position_type = "overbought"
        elif current_price < current_lower:
            position = "Below lower band"
            position_type = "oversold"
        else:
            position = "Within envelope"
            position_type = "normal"
        
        # Calculate envelope squeeze periods (when bands are narrow)
        envelope_width = ((upper_clean - lower_clean) / ma_clean) * 100
        avg_width = envelope_width.mean()
        narrow_periods = sum(1 for width in envelope_width if width < avg_width * 0.8)
        
        return {
            "moving_average": ma_clean.tolist(),
            "upper_band": upper_clean.tolist(),
            "lower_band": lower_clean.tolist(),
            "current_price": float(current_price),
            "current_ma": float(current_ma),
            "current_upper_band": float(current_upper),
            "current_lower_band": float(current_lower),
            "current_position": position,
            "position_type": position_type,
            "periods_above_upper": above_upper,
            "periods_below_lower": below_lower,
            "periods_within_envelope": within_envelope,
            "envelope_containment_rate": (within_envelope / len(prices_clean)) * 100,
            "envelope_width_current": float(envelope_width.iloc[-1]),
            "envelope_width_average": float(avg_width),
            "narrow_envelope_periods": narrow_periods,
            "envelope_percent": envelope_percent,
            "window": window
        }
    
    @staticmethod
    def adaptive_moving_average(prices: List[float], window: int = 20, efficiency_ratio_period: int = 10) -> Dict[str, Any]:
        """
        Calculate Adaptive Moving Average (Kaufman's AMA).
        
        Args:
            prices: List of closing prices
            window: Base window for smoothing
            efficiency_ratio_period: Period for efficiency ratio calculation
            
        Returns:
            Dictionary with AMA analysis
        """
        if len(prices) < max(window, efficiency_ratio_period) + 10:
            return {"error": "Insufficient data for adaptive moving average"}
        
        price_series = pd.Series(prices)
        
        # Calculate Efficiency Ratio (ER)
        direction = abs(price_series - price_series.shift(efficiency_ratio_period))
        volatility = price_series.diff().abs().rolling(window=efficiency_ratio_period).sum()
        efficiency_ratio = direction / volatility
        
        # Smoothing constants
        fastest_sc = 2.0 / (2 + 1)   # Fastest smoothing constant
        slowest_sc = 2.0 / (30 + 1)  # Slowest smoothing constant
        
        # Calculate smoothing constant
        sc = ((efficiency_ratio * (fastest_sc - slowest_sc)) + slowest_sc) ** 2
        
        # Calculate AMA
        ama = pd.Series(index=price_series.index, dtype=float)
        ama.iloc[0] = price_series.iloc[0]  # Initialize with first price
        
        for i in range(1, len(price_series)):
            if pd.notna(sc.iloc[i]):
                ama.iloc[i] = ama.iloc[i-1] + sc.iloc[i] * (price_series.iloc[i] - ama.iloc[i-1])
            else:
                ama.iloc[i] = ama.iloc[i-1]
        
        # Clean data
        ama_clean = ama.dropna()
        if len(ama_clean) < 5:
            return {"error": "Insufficient clean data for AMA analysis"}
        
        # Current metrics
        current_price = prices[-1]
        current_ama = ama_clean.iloc[-1]
        current_er = efficiency_ratio.iloc[-1] if not pd.isna(efficiency_ratio.iloc[-1]) else 0
        
        # Calculate AMA slope and trend
        ama_slope = (ama_clean.iloc[-1] - ama_clean.iloc[-5]) / 5 if len(ama_clean) >= 5 else 0
        
        return {
            "ama_values": ama_clean.tolist(),
            "efficiency_ratios": efficiency_ratio.dropna().tolist(),
            "current_ama": float(current_ama),
            "current_price": float(current_price),
            "current_efficiency_ratio": float(current_er),
            "price_vs_ama_percent": float(((current_price - current_ama) / current_ama) * 100),
            "ama_slope": float(ama_slope),
            "ama_trend": "Rising" if ama_slope > 0 else "Falling" if ama_slope < 0 else "Flat",
            "market_efficiency": "High" if current_er > 0.3 else "Medium" if current_er > 0.1 else "Low",
            "adaptive_responsiveness": "High" if current_er > 0.5 else "Medium" if current_er > 0.2 else "Low",
            "window": window,
            "efficiency_ratio_period": efficiency_ratio_period,
            "observations": len(ama_clean)
        }