"""
Advanced technical analysis using the 'ta' library.
Demonstrates proper use of established TA library instead of custom implementations.
Refactored to use utility framework and eliminate code duplication.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import ta
import warnings
warnings.filterwarnings('ignore')

# Import utility modules for standardized operations
from ..utils.data_validation import validate_and_convert_data, validate_numeric_columns
from ..utils.format_utils import format_success_response, format_error_response
from ..utils.technical_utils import (
    calculate_multiple_timeframe_rsi, calculate_trend_strength,
    calculate_volatility_metrics, detect_support_resistance_levels
)


class TechnicalAnalysisTA:
    """
    Technical analysis using the 'ta' library for all standard indicators.
    Avoids reinventing the wheel by leveraging industry-standard implementations.
    """
    
    def __init__(self):
        pass
    
    def comprehensive_technical_analysis(self, price_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Comprehensive technical analysis using multiple ta library indicators.
        Refactored to use utility framework.
        
        Args:
            price_data: List of OHLCV dictionaries with keys 't', 'o', 'h', 'l', 'c', 'v'
            
        Returns:
            Dictionary with all technical indicators and analysis
        """
        try:
            # Use utility for data validation and conversion
            df = validate_and_convert_data(price_data, required_columns=['open', 'high', 'low', 'close'])
            
            if len(df) < 20:
                return format_error_response(
                    function_name="comprehensive_technical_analysis",
                    error_message="Insufficient data for technical analysis (minimum 20 periods)",
                    context={"data_length": len(df)}
                )
            
            # === MOMENTUM INDICATORS (using utilities) ===
            
            # RSI - Use utility for multi-timeframe analysis
            rsi_data = calculate_multiple_timeframe_rsi(df, periods=[14, 21])
            df['rsi'] = ta.momentum.rsi(df['close'], window=14)  # Keep for backwards compatibility
            
            # Stochastic Oscillator
            stoch = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close'])
            df['stoch_k'] = stoch.stoch()
            df['stoch_d'] = stoch.stoch_signal()
            
            # Williams %R
            df['williams_r'] = ta.momentum.williams_r(df['high'], df['low'], df['close'])
            
            # ROC (Rate of Change)
            df['roc'] = ta.momentum.roc(df['close'], window=12)
            
            # === TREND INDICATORS ===
            
            # MACD
            macd = ta.trend.MACD(df['close'])
            df['macd'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()
            df['macd_histogram'] = macd.macd_diff()
            
            # ADX (Average Directional Index)
            adx = ta.trend.ADXIndicator(df['high'], df['low'], df['close'])
            df['adx'] = adx.adx()
            df['adx_pos'] = adx.adx_pos()
            df['adx_neg'] = adx.adx_neg()
            
            # Parabolic SAR
            df['sar'] = ta.trend.PSARIndicator(df['high'], df['low'], df['close']).psar()
            
            # CCI (Commodity Channel Index)
            df['cci'] = ta.trend.cci(df['high'], df['low'], df['close'])
            
            # === VOLATILITY INDICATORS ===
            
            # Bollinger Bands
            bollinger = ta.volatility.BollingerBands(df['close'])
            df['bb_upper'] = bollinger.bollinger_hband()
            df['bb_middle'] = bollinger.bollinger_mavg()
            df['bb_lower'] = bollinger.bollinger_lband()
            df['bb_width'] = bollinger.bollinger_wband()
            df['bb_percent'] = bollinger.bollinger_pband()
            
            # Average True Range
            df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'])
            
            # Keltner Channels
            keltner = ta.volatility.KeltnerChannel(df['high'], df['low'], df['close'])
            df['keltner_upper'] = keltner.keltner_channel_hband()
            df['keltner_middle'] = keltner.keltner_channel_mband()
            df['keltner_lower'] = keltner.keltner_channel_lband()
            
            # === VOLUME INDICATORS ===
            
            # On-Balance Volume
            df['obv'] = ta.volume.on_balance_volume(df['close'], df['volume'])
            
            # Volume SMA
            df['volume_sma'] = ta.volume.volume_sma(df['close'], df['volume'])
            
            # Chaikin Money Flow
            df['cmf'] = ta.volume.chaikin_money_flow(df['high'], df['low'], df['close'], df['volume'])
            
            # === MOVING AVERAGES ===
            
            # Simple Moving Averages
            df['sma_20'] = ta.trend.sma_indicator(df['close'], window=20)
            df['sma_50'] = ta.trend.sma_indicator(df['close'], window=50)
            df['sma_200'] = ta.trend.sma_indicator(df['close'], window=200) if len(df) >= 200 else np.nan
            
            # Exponential Moving Averages
            df['ema_12'] = ta.trend.ema_indicator(df['close'], window=12)
            df['ema_26'] = ta.trend.ema_indicator(df['close'], window=26)
            
            # === ANALYSIS AND SIGNALS ===
            
            current_idx = len(df) - 1
            current_data = df.iloc[current_idx]
            
            # Current indicator values
            current_indicators = {
                "rsi": float(current_data['rsi']) if not pd.isna(current_data['rsi']) else None,
                "macd": float(current_data['macd']) if not pd.isna(current_data['macd']) else None,
                "macd_signal": float(current_data['macd_signal']) if not pd.isna(current_data['macd_signal']) else None,
                "adx": float(current_data['adx']) if not pd.isna(current_data['adx']) else None,
                "bb_percent": float(current_data['bb_percent']) if not pd.isna(current_data['bb_percent']) else None,
                "stoch_k": float(current_data['stoch_k']) if not pd.isna(current_data['stoch_k']) else None,
                "atr": float(current_data['atr']) if not pd.isna(current_data['atr']) else None,
            }
            
            # Signal analysis
            signals = self._analyze_signals(df, current_idx)
            
            # Recent indicator values (last 10 periods)
            recent_values = {}
            for indicator in ['rsi', 'macd', 'adx', 'bb_percent', 'stoch_k']:
                recent_values[indicator] = df[indicator].dropna().tail(10).tolist()
            
            return {
                "current_indicators": current_indicators,
                "signals": signals,
                "recent_values": recent_values,
                "analysis_date": str(current_data['timestamp']) if 'timestamp' in current_data.index else None,
                "periods_analyzed": len(df),
                "library_used": "ta (Technical Analysis Library)"
            }
            
        except Exception as e:
            return {"error": f"Technical analysis failed: {str(e)}"}
    
    def analyze_accumulation_distribution(self, price_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze Accumulation/Distribution Line to identify institutional buying/selling patterns.
        
        Args:
            price_data: List of OHLCV dictionaries with keys 't', 'o', 'h', 'l', 'c', 'v'
            
        Returns:
            Dictionary with A/D line analysis and accumulation/distribution signals
        """
        try:
            # Convert to DataFrame
            df = pd.DataFrame(price_data)
            df['timestamp'] = df['t']
            df['open'] = pd.to_numeric(df['o'])
            df['high'] = pd.to_numeric(df['h'])
            df['low'] = pd.to_numeric(df['l'])
            df['close'] = pd.to_numeric(df['c'])
            df['volume'] = pd.to_numeric(df.get('v', 0))
            
            if len(df) < 10:
                return {"error": "Insufficient data for A/D analysis (minimum 10 periods)"}
            
            # Calculate Accumulation/Distribution Line using ta library
            df['ad_line'] = ta.volume.acc_dist_index(df['high'], df['low'], df['close'], df['volume'])
            
            # Calculate A/D line trend and momentum
            df['ad_sma_20'] = df['ad_line'].rolling(20).mean()
            df['ad_momentum'] = df['ad_line'].diff(5)  # 5-period momentum
            
            # Price analysis for divergence detection
            df['price_sma_20'] = df['close'].rolling(20).mean()
            df['price_momentum'] = df['close'].diff(5)
            
            # Remove NaN values
            df_clean = df.dropna()
            
            if len(df_clean) < 5:
                return {"error": "Insufficient clean data for A/D analysis"}
            
            # Current values
            current_ad = df_clean['ad_line'].iloc[-1]
            current_price = df_clean['close'].iloc[-1]
            ad_trend = df_clean['ad_momentum'].iloc[-1]
            price_trend = df_clean['price_momentum'].iloc[-1]
            
            # Accumulation/Distribution determination
            if ad_trend > 0:
                ad_signal = "accumulation"
                institutional_flow = "buying"
            elif ad_trend < 0:
                ad_signal = "distribution" 
                institutional_flow = "selling"
            else:
                ad_signal = "neutral"
                institutional_flow = "sideways"
            
            # Divergence analysis
            price_direction = "up" if price_trend > 0 else "down" if price_trend < 0 else "sideways"
            ad_direction = "up" if ad_trend > 0 else "down" if ad_trend < 0 else "sideways"
            
            divergence = "none"
            if price_direction == "up" and ad_direction == "down":
                divergence = "bearish_divergence"
            elif price_direction == "down" and ad_direction == "up":
                divergence = "bullish_divergence"
            
            # Strength analysis
            ad_values = df_clean['ad_line'].values
            ad_range = np.max(ad_values) - np.min(ad_values)
            current_position = (current_ad - np.min(ad_values)) / ad_range if ad_range > 0 else 0.5
            
            strength = "weak"
            if abs(ad_trend) > np.std(df_clean['ad_momentum']) * 1.5:
                strength = "strong"
            elif abs(ad_trend) > np.std(df_clean['ad_momentum']) * 0.5:
                strength = "moderate"
            
            # Recent A/D line values for visualization
            recent_ad_values = df_clean['ad_line'].tail(10).tolist()
            recent_dates = df_clean['timestamp'].tail(10).tolist()
            
            analysis_data = {
                "ad_line_current": float(current_ad),
                "ad_signal": ad_signal,
                "institutional_flow": institutional_flow,
                "strength": strength,
                "divergence_analysis": {
                    "divergence_type": divergence,
                    "price_trend": price_direction,
                    "ad_trend": ad_direction,
                    "price_momentum": float(price_trend),
                    "ad_momentum": float(ad_trend)
                },
                "ad_position_percentile": float(current_position * 100),
                "recent_ad_values": [float(x) for x in recent_ad_values],
                "recent_dates": recent_dates,
                "volume_analysis": {
                    "avg_volume": float(df_clean['volume'].mean()),
                    "recent_volume": float(df_clean['volume'].iloc[-1]),
                    "volume_trend": "increasing" if df_clean['volume'].iloc[-1] > df_clean['volume'].mean() else "decreasing"
                },
                "trading_recommendation": self._get_ad_recommendation(ad_signal, divergence, strength),
                "periods_analyzed": len(df_clean)
            }
            
            return format_success_response(
                function_name="analyze_accumulation_distribution",
                data=analysis_data,
                library_used="ta.volume",
                parameters={"calculation_method": "ta.volume.acc_dist_index"}
            )
            
        except Exception as e:
            return format_error_response(
                function_name="analyze_accumulation_distribution",
                error_message=str(e),
                context={"input_type": type(price_data).__name__}
            )
    
    def _get_ad_recommendation(self, signal: str, divergence: str, strength: str) -> str:
        """Generate trading recommendation based on A/D analysis."""
        if divergence == "bullish_divergence" and strength in ["moderate", "strong"]:
            return "Consider buying - bullish divergence with strong institutional support"
        elif divergence == "bearish_divergence" and strength in ["moderate", "strong"]:
            return "Consider selling - bearish divergence suggests institutional distribution"
        elif signal == "accumulation" and strength == "strong":
            return "Strong accumulation detected - institutional buying pressure"
        elif signal == "distribution" and strength == "strong":
            return "Strong distribution detected - institutional selling pressure"
        elif signal == "accumulation":
            return "Moderate accumulation - some institutional buying interest"
        elif signal == "distribution":
            return "Moderate distribution - some institutional selling pressure"
        else:
            return "Neutral - wait for clearer institutional direction"
    
    def analyze_adx_trend_strength(self, price_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze ADX (Average Directional Index) to identify trend strength and direction.
        Refactored to use utility framework.
        
        Args:
            price_data: List of OHLCV dictionaries with keys 't', 'o', 'h', 'l', 'c', 'v'
            
        Returns:
            Dictionary with ADX trend strength analysis and directional indicators
        """
        try:
            # Use utility for data validation and conversion
            df = validate_and_convert_data(price_data, required_columns=['high', 'low', 'close'])
            
            if len(df) < 20:
                return format_error_response(
                    function_name="analyze_adx_trend_strength",
                    error_message="Insufficient data for ADX analysis (minimum 20 periods)",
                    context={"data_length": len(df)}
                )
            
            # Use utility for comprehensive trend strength analysis (includes ADX)
            trend_data = calculate_trend_strength(df)
            
            # Additional detailed ADX calculations for this specific function
            
            # Calculate ADX and Directional Indicators using ta library
            df['adx'] = ta.trend.adx(df['high'], df['low'], df['close'], window=14)
            df['adx_pos'] = ta.trend.adx_pos(df['high'], df['low'], df['close'], window=14)  # +DI
            df['adx_neg'] = ta.trend.adx_neg(df['high'], df['low'], df['close'], window=14)  # -DI
            
            # Calculate ADX slope for trend strength momentum
            df['adx_slope'] = df['adx'].diff(5)  # 5-period slope
            
            # Remove NaN values
            df_clean = df.dropna()
            
            if len(df_clean) < 5:
                return {"error": "Insufficient clean data for ADX analysis"}
            
            # Current values
            current_adx = df_clean['adx'].iloc[-1]
            current_plus_di = df_clean['adx_pos'].iloc[-1]
            current_minus_di = df_clean['adx_neg'].iloc[-1]
            adx_slope = df_clean['adx_slope'].iloc[-1]
            current_price = df_clean['close'].iloc[-1]
            
            # Trend strength classification
            if current_adx >= 25:
                if current_adx >= 40:
                    trend_strength = "very_strong"
                else:
                    trend_strength = "strong"
            elif current_adx >= 20:
                trend_strength = "moderate"
            else:
                trend_strength = "weak"
            
            # Trend direction analysis
            if current_plus_di > current_minus_di:
                trend_direction = "uptrend"
                directional_strength = (current_plus_di - current_minus_di) / current_plus_di if current_plus_di > 0 else 0
            elif current_minus_di > current_plus_di:
                trend_direction = "downtrend" 
                directional_strength = (current_minus_di - current_plus_di) / current_minus_di if current_minus_di > 0 else 0
            else:
                trend_direction = "sideways"
                directional_strength = 0
            
            # ADX momentum analysis
            if adx_slope > 2:
                adx_momentum = "strengthening"
            elif adx_slope < -2:
                adx_momentum = "weakening"
            else:
                adx_momentum = "stable"
            
            # Trend quality score (combination of ADX level and directional spread)
            di_spread = abs(current_plus_di - current_minus_di)
            trend_quality = (current_adx + di_spread) / 2 if current_adx > 0 else 0
            
            # Historical ADX analysis
            adx_values = df_clean['adx'].values
            adx_avg = np.mean(adx_values)
            adx_percentile = (np.sum(adx_values <= current_adx) / len(adx_values)) * 100
            
            # Recent values for visualization
            recent_adx = df_clean['adx'].tail(10).tolist()
            recent_plus_di = df_clean['adx_pos'].tail(10).tolist()
            recent_minus_di = df_clean['adx_neg'].tail(10).tolist()
            recent_dates = df_clean['timestamp'].tail(10).tolist()
            
            return {
                "adx_current": float(current_adx),
                "trend_strength": trend_strength,
                "trend_direction": trend_direction,
                "directional_strength": float(directional_strength),
                "adx_momentum": adx_momentum,
                "trend_quality_score": float(trend_quality),
                "directional_indicators": {
                    "plus_di": float(current_plus_di),
                    "minus_di": float(current_minus_di),
                    "di_spread": float(di_spread),
                    "dominant_direction": "+DI" if current_plus_di > current_minus_di else "-DI"
                },
                "adx_analysis": {
                    "adx_slope": float(adx_slope),
                    "adx_percentile": float(adx_percentile),
                    "adx_average": float(adx_avg),
                    "above_trend_threshold": current_adx >= 25
                },
                "recent_values": {
                    "adx": [float(x) for x in recent_adx],
                    "plus_di": [float(x) for x in recent_plus_di],
                    "minus_di": [float(x) for x in recent_minus_di],
                    "dates": recent_dates
                },
                "trading_signals": {
                    "signal_strength": "strong" if current_adx >= 25 and di_spread > 5 else "moderate" if current_adx >= 20 else "weak",
                    "trend_entry": self._get_adx_trend_entry(trend_direction, trend_strength, adx_momentum),
                    "risk_level": "low" if current_adx >= 30 else "medium" if current_adx >= 20 else "high"
                },
                "trading_recommendation": self._get_adx_recommendation(trend_direction, trend_strength, adx_momentum, di_spread),
                "periods_analyzed": len(df_clean),
                "calculation_method": "ta.trend.adx (14-period default)"
            }
            
        except Exception as e:
            return {"error": f"ADX analysis failed: {str(e)}"}
    
    def _get_adx_trend_entry(self, direction: str, strength: str, momentum: str) -> str:
        """Generate trend entry signal based on ADX analysis."""
        if direction == "uptrend" and strength in ["strong", "very_strong"] and momentum in ["strengthening", "stable"]:
            return "bullish_trend_entry"
        elif direction == "downtrend" and strength in ["strong", "very_strong"] and momentum in ["strengthening", "stable"]:
            return "bearish_trend_entry"  
        elif direction != "sideways" and strength == "moderate":
            return "moderate_trend_entry"
        else:
            return "no_clear_signal"
    
    def _get_adx_recommendation(self, direction: str, strength: str, momentum: str, di_spread: float) -> str:
        """Generate trading recommendation based on ADX trend analysis."""
        if direction == "uptrend" and strength == "very_strong" and di_spread > 10:
            return "Strong uptrend confirmed - consider long positions with trend following strategy"
        elif direction == "downtrend" and strength == "very_strong" and di_spread > 10:
            return "Strong downtrend confirmed - consider short positions or avoid long entries"
        elif direction == "uptrend" and strength == "strong" and momentum == "strengthening":
            return "Building uptrend momentum - good for trend following entries"
        elif direction == "downtrend" and strength == "strong" and momentum == "strengthening":
            return "Building downtrend momentum - caution on long positions"
        elif strength == "moderate" and momentum == "strengthening":
            return f"Moderate {direction} developing - wait for stronger confirmation"
        elif strength == "weak":
            return "Weak trend conditions - range-bound market, avoid trend following strategies"
        elif momentum == "weakening":
            return f"Trend momentum weakening in {direction} - consider profit taking or position reduction"
        else:
            return "Mixed signals - monitor for clearer trend development"
    
    def detect_three_black_crows(self, price_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect Three Black Crows bearish reversal pattern.
        
        Args:
            price_data: List of OHLCV dictionaries with keys 't', 'o', 'h', 'l', 'c', 'v'
            
        Returns:
            Dictionary with Three Black Crows pattern analysis and bearish signals
        """
        try:
            # Convert to DataFrame
            df = pd.DataFrame(price_data)
            df['timestamp'] = df['t']
            df['open'] = pd.to_numeric(df['o'])
            df['high'] = pd.to_numeric(df['h'])
            df['low'] = pd.to_numeric(df['l'])
            df['close'] = pd.to_numeric(df['c'])
            df['volume'] = pd.to_numeric(df.get('v', 0))
            
            if len(df) < 10:
                return {"error": "Insufficient data for Three Black Crows pattern detection (minimum 10 periods)"}
            
            # Calculate candle properties
            df['body'] = df['close'] - df['open']
            df['body_pct'] = (df['body'] / df['open']) * 100
            df['is_red'] = df['close'] < df['open']
            df['candle_range'] = df['high'] - df['low']
            df['upper_wick'] = df['high'] - np.maximum(df['open'], df['close'])
            df['lower_wick'] = np.minimum(df['open'], df['close']) - df['low']
            df['body_to_range'] = np.abs(df['body']) / df['candle_range']
            
            # Rolling analysis for pattern detection
            df['sma_20'] = df['close'].rolling(20).mean()
            df['volume_sma'] = df['volume'].rolling(10).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            patterns_found = []
            
            # Scan for Three Black Crows pattern (need at least 3 candles)
            for i in range(2, len(df)):
                candle1 = df.iloc[i-2]  # First crow
                candle2 = df.iloc[i-1]  # Second crow  
                candle3 = df.iloc[i]    # Third crow
                
                # Three Black Crows criteria
                criteria = {
                    'three_red_candles': all([candle1['is_red'], candle2['is_red'], candle3['is_red']]),
                    'progressively_lower_closes': (candle2['close'] < candle1['close']) and (candle3['close'] < candle2['close']),
                    'significant_bodies': all([abs(c['body_pct']) > 1.0 for c in [candle1, candle2, candle3]]),
                    'good_body_ratios': all([c['body_to_range'] > 0.6 for c in [candle1, candle2, candle3]]),
                    'opens_within_body': (candle1['close'] < candle2['open'] < candle1['open']) and (candle2['close'] < candle3['open'] < candle2['open'])
                }
                
                pattern_quality = sum(criteria.values())
                
                if pattern_quality >= 4:  # At least 4 out of 5 criteria met
                    # Additional context analysis
                    prior_trend = "uptrend" if candle1['close'] > candle1['sma_20'] else "downtrend"
                    volume_confirmation = np.mean([c['volume_ratio'] for c in [candle1, candle2, candle3]]) > 1.1
                    
                    # Pattern strength analysis
                    total_decline = ((candle1['close'] - candle3['close']) / candle1['close']) * 100
                    avg_body_size = np.mean([abs(c['body_pct']) for c in [candle1, candle2, candle3]])
                    
                    pattern = {
                        'date': candle3['timestamp'],
                        'pattern_start_date': candle1['timestamp'],
                        'pattern_quality_score': pattern_quality,
                        'criteria_met': criteria,
                        'price_levels': {
                            'pattern_high': float(candle1['high']),
                            'pattern_low': float(candle3['low']),
                            'first_close': float(candle1['close']),
                            'final_close': float(candle3['close'])
                        },
                        'pattern_metrics': {
                            'total_decline_pct': float(total_decline),
                            'avg_body_size_pct': float(avg_body_size),
                            'volume_confirmed': volume_confirmation,
                            'avg_volume_ratio': float(np.mean([c['volume_ratio'] for c in [candle1, candle2, candle3]]))
                        },
                        'trend_context': {
                            'prior_trend': prior_trend,
                            'at_resistance': candle1['close'] > candle1['sma_20'],
                            'trend_reversal_signal': prior_trend == "uptrend"
                        },
                        'bearish_strength': self._calculate_bearish_strength(pattern_quality, total_decline, volume_confirmation, prior_trend == "uptrend")
                    }
                    
                    patterns_found.append(pattern)
            
            # Get most recent and strongest patterns
            if patterns_found:
                patterns_found.sort(key=lambda x: x['date'], reverse=True)
                most_recent = patterns_found[0]
                strongest = max(patterns_found, key=lambda x: x['bearish_strength'])
            else:
                most_recent = None
                strongest = None
            
            # Overall analysis
            pattern_count = len(patterns_found)
            recent_pattern_found = pattern_count > 0 and patterns_found[0]['date'] == df.iloc[-1]['timestamp']
            
            return {
                "patterns_detected": pattern_count,
                "recent_pattern_active": recent_pattern_found,
                "most_recent_pattern": most_recent,
                "strongest_pattern": strongest,
                "all_patterns": patterns_found[-5:] if len(patterns_found) > 5 else patterns_found,  # Last 5
                "bearish_signal_strength": strongest['bearish_strength'] if strongest else "none",
                "trading_recommendation": self._get_three_black_crows_recommendation(most_recent, pattern_count),
                "risk_assessment": {
                    "pattern_reliability": "high" if pattern_count > 0 and most_recent and most_recent['pattern_quality_score'] >= 4 else "moderate",
                    "volume_confirmation": most_recent['pattern_metrics']['volume_confirmed'] if most_recent else False,
                    "trend_context": most_recent['trend_context']['prior_trend'] if most_recent else "unknown"
                },
                "market_signals": {
                    "bearish_reversal_probable": recent_pattern_found and most_recent and most_recent['trend_context']['trend_reversal_signal'],
                    "selling_pressure": "high" if pattern_count > 1 else "moderate" if pattern_count == 1 else "low",
                    "continuation_likely": recent_pattern_found and most_recent and most_recent['pattern_metrics']['volume_confirmed']
                },
                "periods_analyzed": len(df),
                "calculation_method": "pandas OHLC pattern recognition"
            }
            
        except Exception as e:
            return {"error": f"Three Black Crows detection failed: {str(e)}"}
    
    def _calculate_bearish_strength(self, quality_score: int, decline_pct: float, volume_confirmed: bool, trend_reversal: bool) -> str:
        """Calculate bearish strength based on pattern characteristics."""
        strength_score = 0
        
        # Quality contribution
        strength_score += quality_score * 20  # Max 100 points
        
        # Decline magnitude
        if abs(decline_pct) > 5:
            strength_score += 40
        elif abs(decline_pct) > 3:
            strength_score += 25
        elif abs(decline_pct) > 1:
            strength_score += 15
        
        # Volume confirmation
        if volume_confirmed:
            strength_score += 25
        
        # Trend context (reversal more significant)
        if trend_reversal:
            strength_score += 15
        
        # Classify strength
        if strength_score >= 140:
            return "very_strong"
        elif strength_score >= 110:
            return "strong"
        elif strength_score >= 80:
            return "moderate"
        else:
            return "weak"
    
    def _get_three_black_crows_recommendation(self, recent_pattern: dict, pattern_count: int) -> str:
        """Generate trading recommendation based on Three Black Crows analysis."""
        if not recent_pattern:
            return "No Three Black Crows pattern detected - monitor for bearish reversal signals"
        
        strength = recent_pattern['bearish_strength']
        volume_confirmed = recent_pattern['pattern_metrics']['volume_confirmed']
        trend_reversal = recent_pattern['trend_context']['trend_reversal_signal']
        
        if strength == "very_strong" and volume_confirmed and trend_reversal:
            return "Strong bearish reversal signal - consider reducing long positions or initiating shorts"
        elif strength == "strong" and volume_confirmed:
            return "Significant bearish pressure - caution on long positions, watch for continuation"
        elif strength == "strong" and trend_reversal:
            return "Bearish reversal pattern confirmed - consider defensive positioning"
        elif strength in ["moderate", "strong"]:
            return "Moderate bearish signal - monitor for follow-through selling"
        else:
            return "Weak bearish pattern - wait for stronger confirmation before acting"
    
    def analyze_price_volume_breakouts(self, price_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze coordinated price and volume breakout patterns.
        
        Args:
            price_data: List of OHLCV dictionaries with keys 't', 'o', 'h', 'l', 'c', 'v'
            
        Returns:
            Dictionary with price-volume breakout analysis and institutional flow signals
        """
        try:
            # Convert to DataFrame
            df = pd.DataFrame(price_data)
            df['timestamp'] = df['t']
            df['open'] = pd.to_numeric(df['o'])
            df['high'] = pd.to_numeric(df['h'])
            df['low'] = pd.to_numeric(df['l'])
            df['close'] = pd.to_numeric(df['c'])
            df['volume'] = pd.to_numeric(df.get('v', 0))
            
            if len(df) < 20:
                return {"error": "Insufficient data for price-volume breakout analysis (minimum 20 periods)"}
            
            # Calculate technical indicators for breakout identification
            df['sma_20'] = df['close'].rolling(20).mean()
            df['sma_50'] = df['close'].rolling(50).mean() if len(df) >= 50 else df['close'].rolling(len(df)//2).mean()
            df['volume_sma_20'] = df['volume'].rolling(20).mean()
            df['volume_sma_50'] = df['volume'].rolling(50).mean() if len(df) >= 50 else df['volume'].rolling(len(df)//2).mean()
            
            # Calculate price levels and ranges
            df['high_20'] = df['high'].rolling(20).max()
            df['low_20'] = df['low'].rolling(20).min()
            df['range_20'] = df['high_20'] - df['low_20']
            
            # Volume analysis
            df['volume_ratio'] = df['volume'] / df['volume_sma_20']
            df['volume_expansion'] = (df['volume'] - df['volume_sma_20']) / df['volume_sma_20'] * 100
            df['volume_percentile'] = df['volume'].rolling(20).rank(pct=True) * 100
            
            # Price momentum and breakout indicators
            df['price_change'] = df['close'].pct_change() * 100
            df['above_sma20'] = df['close'] > df['sma_20']
            df['above_sma50'] = df['close'] > df['sma_50']
            df['near_high'] = (df['close'] - df['low_20']) / df['range_20'] > 0.8  # Within 20% of 20-day high
            
            # Breakout detection
            df['price_breakout'] = (df['close'] > df['high_20'].shift(1)) & (df['price_change'] > 2.0)
            df['volume_breakout'] = df['volume_ratio'] > 1.5  # Volume 50% above average
            df['coordinated_breakout'] = df['price_breakout'] & df['volume_breakout']
            
            # Remove NaN values
            df_clean = df.dropna()
            
            if len(df_clean) < 10:
                return {"error": "Insufficient clean data for breakout analysis"}
            
            # Current market state
            current = df_clean.iloc[-1]
            recent_periods = df_clean.tail(5)
            
            # Breakout analysis
            breakouts_detected = df_clean['coordinated_breakout'].sum()
            recent_breakout = current['coordinated_breakout'] or recent_periods['coordinated_breakout'].any()
            
            # Volume confirmation analysis
            current_volume_ratio = current['volume_ratio']
            current_volume_percentile = current['volume_percentile']
            avg_volume_ratio = recent_periods['volume_ratio'].mean()
            
            # Price momentum analysis
            current_momentum = current['price_change']
            recent_momentum = recent_periods['price_change'].mean()
            momentum_acceleration = current_momentum > recent_momentum * 1.2
            
            # Institutional flow analysis (volume patterns)
            institutional_indicators = {
                'high_volume_days': (recent_periods['volume_ratio'] > 2.0).sum(),
                'volume_accumulation': recent_periods['volume_expansion'].mean() > 20,
                'sustained_volume': (recent_periods['volume_ratio'] > 1.2).sum() >= 3,
                'volume_trend': recent_periods['volume_ratio'].is_monotonic_increasing
            }
            
            institutional_score = sum(institutional_indicators.values()) / len(institutional_indicators) * 100
            
            # Breakout strength classification
            breakout_strength = self._calculate_breakout_strength(
                current['price_breakout'], current['volume_breakout'],
                current_volume_ratio, current_momentum, institutional_score
            )
            
            # Support/resistance analysis
            resistance_level = df_clean['high_20'].iloc[-1]
            support_level = df_clean['low_20'].iloc[-1]
            price_position = (current['close'] - support_level) / (resistance_level - support_level) * 100
            
            # Sustainability analysis
            sustainability_factors = {
                'volume_confirmation': current_volume_ratio > 1.5,
                'momentum_strength': current_momentum > 3.0,
                'trend_alignment': current['above_sma20'] and current['above_sma50'],
                'institutional_flow': institutional_score > 60,
                'breakout_magnitude': current['price_change'] > 5.0
            }
            
            sustainability_score = sum(sustainability_factors.values()) / len(sustainability_factors) * 100
            
            # Recent breakout events for context
            recent_breakouts = df_clean[df_clean['coordinated_breakout']].tail(3)
            breakout_history = []
            
            for idx, breakout in recent_breakouts.iterrows():
                breakout_history.append({
                    'date': breakout['timestamp'],
                    'price_change': float(breakout['price_change']),
                    'volume_ratio': float(breakout['volume_ratio']),
                    'breakout_level': float(breakout['close'])
                })
            
            return {
                "breakout_status": "active" if recent_breakout else "no_breakout",
                "breakout_strength": breakout_strength,
                "coordinated_breakouts_detected": int(breakouts_detected),
                "current_analysis": {
                    "price_breakout": bool(current['price_breakout']),
                    "volume_breakout": bool(current['volume_breakout']),
                    "coordinated_breakout": bool(current['coordinated_breakout']),
                    "price_momentum": float(current_momentum),
                    "volume_ratio": float(current_volume_ratio),
                    "volume_percentile": float(current_volume_percentile)
                },
                "institutional_flow": {
                    "institutional_score": float(institutional_score),
                    "indicators": institutional_indicators,
                    "flow_strength": "strong" if institutional_score > 75 else "moderate" if institutional_score > 50 else "weak"
                },
                "technical_levels": {
                    "resistance_level": float(resistance_level),
                    "support_level": float(support_level),
                    "current_price": float(current['close']),
                    "price_position_pct": float(price_position)
                },
                "sustainability_analysis": {
                    "sustainability_score": float(sustainability_score),
                    "factors": sustainability_factors,
                    "probability": "high" if sustainability_score > 80 else "moderate" if sustainability_score > 60 else "low"
                },
                "volume_analysis": {
                    "current_volume_expansion": float(current['volume_expansion']),
                    "avg_recent_volume_ratio": float(avg_volume_ratio),
                    "volume_trend": "increasing" if institutional_indicators['volume_trend'] else "mixed",
                    "accumulation_detected": institutional_indicators['volume_accumulation']
                },
                "breakout_history": breakout_history,
                "trading_recommendation": self._get_breakout_recommendation(breakout_strength, sustainability_score, institutional_score),
                "risk_assessment": {
                    "breakout_reliability": "high" if breakout_strength == "very_strong" and sustainability_score > 75 else "moderate",
                    "volume_confirmation": current_volume_ratio > 1.5,
                    "momentum_alignment": momentum_acceleration
                },
                "periods_analyzed": len(df_clean),
                "calculation_method": "pandas technical analysis with volume confirmation"
            }
            
        except Exception as e:
            return {"error": f"Price-volume breakout analysis failed: {str(e)}"}
    
    def _calculate_breakout_strength(self, price_breakout: bool, volume_breakout: bool, 
                                   volume_ratio: float, momentum: float, institutional_score: float) -> str:
        """Calculate breakout strength based on price and volume characteristics."""
        strength_score = 0
        
        # Price breakout contribution
        if price_breakout:
            strength_score += 30
            if momentum > 5:
                strength_score += 20
            elif momentum > 3:
                strength_score += 15
            elif momentum > 1:
                strength_score += 10
        
        # Volume breakout contribution
        if volume_breakout:
            strength_score += 25
            if volume_ratio > 3.0:
                strength_score += 20
            elif volume_ratio > 2.0:
                strength_score += 15
            elif volume_ratio > 1.5:
                strength_score += 10
        
        # Institutional flow contribution
        strength_score += institutional_score * 0.25  # Scale to max 25 points
        
        # Classify strength
        if strength_score >= 85:
            return "very_strong"
        elif strength_score >= 70:
            return "strong"
        elif strength_score >= 50:
            return "moderate"
        else:
            return "weak"
    
    def _get_breakout_recommendation(self, strength: str, sustainability: float, institutional: float) -> str:
        """Generate trading recommendation based on breakout analysis."""
        if strength == "very_strong" and sustainability > 80 and institutional > 70:
            return "Strong buy signal - coordinated price-volume breakout with institutional support"
        elif strength == "strong" and sustainability > 70:
            return "Buy consideration - solid breakout pattern with good sustainability factors"
        elif strength == "strong" and institutional > 75:
            return "Monitor closely - strong institutional flow may drive continued momentum"
        elif strength == "moderate" and sustainability > 60:
            return "Cautious optimism - moderate breakout with reasonable sustainability"
        elif strength in ["moderate", "strong"]:
            return "Wait for volume confirmation - price movement needs volume validation"
        else:
            return "Avoid - weak breakout pattern with low probability of sustainability"
    
    def _analyze_signals(self, df: pd.DataFrame, current_idx: int) -> Dict[str, Any]:
        """Analyze current trading signals based on technical indicators."""
        
        current = df.iloc[current_idx]
        previous = df.iloc[current_idx - 1] if current_idx > 0 else current
        
        signals = {
            "momentum_signals": {},
            "trend_signals": {},
            "volatility_signals": {},
            "overall_sentiment": "neutral"
        }
        
        # RSI Signals
        rsi_current = current['rsi']
        if not pd.isna(rsi_current):
            if rsi_current < 30:
                signals["momentum_signals"]["rsi"] = "oversold_bullish"
            elif rsi_current > 70:
                signals["momentum_signals"]["rsi"] = "overbought_bearish"
            else:
                signals["momentum_signals"]["rsi"] = "neutral"
        
        # MACD Signals
        macd_current = current['macd']
        macd_signal_current = current['macd_signal']
        macd_prev = previous['macd']
        macd_signal_prev = previous['macd_signal']
        
        if all(not pd.isna(x) for x in [macd_current, macd_signal_current, macd_prev, macd_signal_prev]):
            # MACD crossover detection
            if macd_prev <= macd_signal_prev and macd_current > macd_signal_current:
                signals["trend_signals"]["macd"] = "bullish_crossover"
            elif macd_prev >= macd_signal_prev and macd_current < macd_signal_current:
                signals["trend_signals"]["macd"] = "bearish_crossover"
            else:
                signals["trend_signals"]["macd"] = "no_crossover"
        
        # Bollinger Bands Signals
        bb_percent = current['bb_percent']
        if not pd.isna(bb_percent):
            if bb_percent < 0.2:
                signals["volatility_signals"]["bollinger"] = "near_lower_band"
            elif bb_percent > 0.8:
                signals["volatility_signals"]["bollinger"] = "near_upper_band"
            else:
                signals["volatility_signals"]["bollinger"] = "middle_range"
        
        # Stochastic Signals
        stoch_k = current['stoch_k']
        stoch_d = current['stoch_d']
        if not pd.isna(stoch_k) and not pd.isna(stoch_d):
            if stoch_k < 20 and stoch_d < 20:
                signals["momentum_signals"]["stochastic"] = "oversold"
            elif stoch_k > 80 and stoch_d > 80:
                signals["momentum_signals"]["stochastic"] = "overbought"
            else:
                signals["momentum_signals"]["stochastic"] = "neutral"
        
        # Overall sentiment (simplified)
        bullish_signals = 0
        bearish_signals = 0
        
        for category in signals:
            if category != "overall_sentiment":
                for signal_type, signal_value in signals[category].items():
                    if "bullish" in signal_value or "oversold" in signal_value:
                        bullish_signals += 1
                    elif "bearish" in signal_value or "overbought" in signal_value:
                        bearish_signals += 1
        
        if bullish_signals > bearish_signals:
            signals["overall_sentiment"] = "bullish"
        elif bearish_signals > bullish_signals:
            signals["overall_sentiment"] = "bearish"
        
        return signals
    
    def multi_timeframe_analysis(self, daily_data: List[Dict], 
                               weekly_data: List[Dict] = None,
                               monthly_data: List[Dict] = None) -> Dict[str, Any]:
        """
        Multi-timeframe analysis using ta library indicators.
        
        Args:
            daily_data: Daily OHLCV data
            weekly_data: Weekly OHLCV data (optional)
            monthly_data: Monthly OHLCV data (optional)
            
        Returns:
            Multi-timeframe technical analysis
        """
        try:
            results = {
                "timeframes": {},
                "alignment_analysis": {}
            }
            
            # Analyze daily timeframe
            daily_analysis = self.comprehensive_technical_analysis(daily_data)
            if "error" not in daily_analysis:
                results["timeframes"]["daily"] = daily_analysis
            
            # Analyze weekly timeframe if provided
            if weekly_data:
                weekly_analysis = self.comprehensive_technical_analysis(weekly_data)
                if "error" not in weekly_analysis:
                    results["timeframes"]["weekly"] = weekly_analysis
            
            # Analyze monthly timeframe if provided
            if monthly_data:
                monthly_analysis = self.comprehensive_technical_analysis(monthly_data)
                if "error" not in monthly_analysis:
                    results["timeframes"]["monthly"] = monthly_analysis
            
            # Alignment analysis
            if len(results["timeframes"]) > 1:
                results["alignment_analysis"] = self._analyze_timeframe_alignment(results["timeframes"])
            
            return results
            
        except Exception as e:
            return {"error": f"Multi-timeframe analysis failed: {str(e)}"}
    
    def _analyze_timeframe_alignment(self, timeframes: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze alignment between different timeframes."""
        
        alignment = {
            "rsi_alignment": {},
            "trend_alignment": {},
            "overall_alignment": "unknown"
        }
        
        # Extract RSI values from different timeframes
        rsi_values = {}
        trend_signals = {}
        
        for timeframe, data in timeframes.items():
            if "current_indicators" in data and data["current_indicators"].get("rsi"):
                rsi_values[timeframe] = data["current_indicators"]["rsi"]
            
            if "signals" in data and "overall_sentiment" in data["signals"]:
                trend_signals[timeframe] = data["signals"]["overall_sentiment"]
        
        # RSI alignment analysis
        if len(rsi_values) >= 2:
            rsi_list = list(rsi_values.values())
            rsi_std = np.std(rsi_list)
            alignment["rsi_alignment"] = {
                "values": rsi_values,
                "standard_deviation": float(rsi_std),
                "alignment_strength": "strong" if rsi_std < 10 else "weak"
            }
        
        # Trend alignment analysis
        if len(trend_signals) >= 2:
            unique_trends = set(trend_signals.values())
            alignment["trend_alignment"] = {
                "signals": trend_signals,
                "consensus": len(unique_trends) == 1,
                "dominant_trend": max(trend_signals.values(), key=list(trend_signals.values()).count)
            }
        
        return alignment


def create_ta_instance():
    """Factory function to create TechnicalAnalysisTA instance."""
    return TechnicalAnalysisTA()