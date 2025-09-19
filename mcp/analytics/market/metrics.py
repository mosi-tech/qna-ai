"""
Market Analysis Metrics using empyrical and pandas

Market analysis functions from financial-analysis-function-library.json market_analysis category.
Both simple atomic functions and complex analytical functions.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Union, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Use empyrical library from requirements.txt - no wheel reinvention
import empyrical
from scipy import stats
from scipy.signal import find_peaks
from sklearn.cluster import KMeans

from ..utils.data_utils import validate_return_data, validate_price_data, align_series, standardize_output
from ..risk.metrics import calculate_correlation, calculate_var, calculate_volatility
from ..indicators.technical import calculate_adx


def calculate_trend_strength(prices: Union[pd.Series, Dict[str, Any]], 
                           method: str = "adx") -> Dict[str, Any]:
    """
    Measure trend strength using various methods.
    
    From financial-analysis-function-library.json market_analysis category
    Uses existing technical indicators - no code duplication
    
    Args:
        prices: Price series data
        method: Method to use ("adx", "regression", "momentum")
        
    Returns:
        Dict: Trend strength analysis
    """
    try:
        price_series = validate_price_data(prices)
        
        if len(price_series) < 20:
            raise ValueError("Insufficient data for trend strength calculation")
        
        # Convert to OHLC format for ADX if needed
        if method == "adx":
            # For ADX we need OHLC, use price as close and create synthetic OHLC
            ohlc_data = []
            returns = price_series.pct_change().dropna()
            
            for i, (date, close) in enumerate(price_series.items()):
                if i == 0:
                    continue
                    
                # Create synthetic OHLC from price movement
                prev_close = price_series.iloc[i-1]
                daily_return = returns.iloc[i-1] if i-1 < len(returns) else 0
                
                # Synthetic high/low based on volatility
                volatility = abs(daily_return)
                high = close + (volatility * close * 0.5)
                low = close - (volatility * close * 0.5)
                open_price = prev_close
                
                ohlc_data.append({
                    'open': open_price,
                    'high': max(high, close, open_price),
                    'low': min(low, close, open_price),
                    'close': close,
                    'volume': 1000000  # Synthetic volume
                })
            
            ohlc_df = pd.DataFrame(ohlc_data, index=price_series.index[1:])
            adx_result = calculate_adx(ohlc_df)
            
            current_adx = adx_result['adx'][-1] if len(adx_result['adx']) > 0 else 0
            avg_adx = np.mean(adx_result['adx'][-20:]) if len(adx_result['adx']) >= 20 else current_adx
            
            # ADX interpretation
            if current_adx > 40:
                strength_rating = "very_strong"
            elif current_adx > 25:
                strength_rating = "strong"
            elif current_adx > 15:
                strength_rating = "moderate"
            else:
                strength_rating = "weak"
            
            trend_strength = {
                "method": "adx",
                "current_strength": float(current_adx),
                "average_strength_20d": float(avg_adx),
                "strength_rating": strength_rating,
                "adx_details": {
                    "plus_di": float(adx_result['plus_di'][-1]) if len(adx_result['plus_di']) > 0 else 0,
                    "minus_di": float(adx_result['minus_di'][-1]) if len(adx_result['minus_di']) > 0 else 0
                }
            }
            
        elif method == "regression":
            # Linear regression trend strength
            x = np.arange(len(price_series))
            y = price_series.values
            
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            # R-squared as trend strength
            r_squared = r_value ** 2
            
            # Trend direction
            trend_direction = "up" if slope > 0 else "down"
            
            # Strength rating based on R-squared
            if r_squared > 0.8:
                strength_rating = "very_strong"
            elif r_squared > 0.6:
                strength_rating = "strong"
            elif r_squared > 0.4:
                strength_rating = "moderate"
            else:
                strength_rating = "weak"
            
            trend_strength = {
                "method": "regression",
                "r_squared": float(r_squared),
                "slope": float(slope),
                "p_value": float(p_value),
                "trend_direction": trend_direction,
                "strength_rating": strength_rating,
                "is_significant": p_value < 0.05
            }
            
        elif method == "momentum":
            # Momentum-based trend strength
            returns = price_series.pct_change().dropna()
            
            # Calculate momentum indicators
            momentum_5d = (price_series.iloc[-1] / price_series.iloc[-6] - 1) if len(price_series) > 5 else 0
            momentum_20d = (price_series.iloc[-1] / price_series.iloc[-21] - 1) if len(price_series) > 20 else 0
            momentum_60d = (price_series.iloc[-1] / price_series.iloc[-61] - 1) if len(price_series) > 60 else 0
            
            # Trend consistency (% of positive returns)
            positive_returns = (returns > 0).sum()
            trend_consistency = positive_returns / len(returns)
            
            # Average momentum
            avg_momentum = np.mean([abs(momentum_5d), abs(momentum_20d), abs(momentum_60d)])
            
            if avg_momentum > 0.15:
                strength_rating = "very_strong"
            elif avg_momentum > 0.10:
                strength_rating = "strong"
            elif avg_momentum > 0.05:
                strength_rating = "moderate"
            else:
                strength_rating = "weak"
            
            trend_strength = {
                "method": "momentum",
                "momentum_5d": float(momentum_5d),
                "momentum_20d": float(momentum_20d),
                "momentum_60d": float(momentum_60d),
                "average_momentum": float(avg_momentum),
                "trend_consistency": float(trend_consistency),
                "strength_rating": strength_rating
            }
            
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Add common metrics
        current_price = float(price_series.iloc[-1])
        period_high = float(price_series.max())
        period_low = float(price_series.min())
        
        trend_strength.update({
            "current_price": current_price,
            "period_high": period_high,
            "period_low": period_low,
            "distance_from_high": float((period_high - current_price) / period_high),
            "distance_from_low": float((current_price - period_low) / period_low),
            "data_points": len(price_series)
        })
        
        return standardize_output(trend_strength, "calculate_trend_strength")
        
    except Exception as e:
        return {"success": False, "error": f"Trend strength calculation failed: {str(e)}"}


def calculate_market_stress(returns: Union[pd.Series, Dict[str, Any]], 
                           benchmark_returns: Union[pd.Series, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate market stress indicators.
    
    From financial-analysis-function-library.json market_analysis category
    Uses empyrical and scipy - no code duplication
    
    Args:
        returns: Asset return series
        benchmark_returns: Benchmark return series (e.g., market index)
        
    Returns:
        Dict: Market stress analysis
    """
    try:
        returns_series = validate_return_data(returns)
        benchmark_series = validate_return_data(benchmark_returns)
        
        # Align series
        ret_aligned, bench_aligned = align_series(returns_series, benchmark_series)
        
        if len(ret_aligned) < 20:
            raise ValueError("Insufficient data for stress calculation")
        
        # Calculate stress indicators
        
        # 1. Correlation breakdown (stress when correlation decreases)
        rolling_corr = ret_aligned.rolling(window=20).corr(bench_aligned).dropna()
        avg_correlation = rolling_corr.mean()
        current_correlation = rolling_corr.iloc[-1] if len(rolling_corr) > 0 else 0
        correlation_stress = max(0, avg_correlation - current_correlation)
        
        # 2. Volatility stress (elevated volatility)
        rolling_vol = ret_aligned.rolling(window=20).std() * np.sqrt(252)
        avg_volatility = rolling_vol.mean()
        current_volatility = rolling_vol.iloc[-1] if len(rolling_vol) > 0 else 0
        volatility_stress = max(0, (current_volatility - avg_volatility) / avg_volatility) if avg_volatility > 0 else 0
        
        # 3. Tail risk stress (extreme negative returns)
        negative_returns = ret_aligned[ret_aligned < 0]
        if len(negative_returns) > 0:
            var_95 = negative_returns.quantile(0.05)  # 5th percentile (VaR)
            recent_returns = ret_aligned.tail(5)
            extreme_count = (recent_returns < var_95).sum()
            tail_stress = extreme_count / 5  # Proportion of recent extreme events
        else:
            tail_stress = 0
            var_95 = 0
        
        # 4. Drawdown stress
        cumulative_returns = (1 + ret_aligned).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        current_drawdown = abs(drawdown.iloc[-1])
        max_drawdown = abs(drawdown.min())
        drawdown_stress = current_drawdown / max_drawdown if max_drawdown > 0 else 0
        
        # 5. Beta stress (beta instability)
        rolling_beta = []
        window = 30
        for i in range(window, len(ret_aligned)):
            ret_window = ret_aligned.iloc[i-window:i]
            bench_window = bench_aligned.iloc[i-window:i]
            if bench_window.var() > 0:
                beta = ret_window.cov(bench_window) / bench_window.var()
                rolling_beta.append(beta)
        
        if len(rolling_beta) > 1:
            beta_volatility = np.std(rolling_beta)
            beta_stress = min(beta_volatility, 2.0)  # Cap at 2.0
        else:
            beta_stress = 0
        
        # Composite stress index (0-1 scale)
        stress_components = {
            "correlation_stress": float(correlation_stress),
            "volatility_stress": float(min(volatility_stress, 2.0)),  # Cap at 200%
            "tail_stress": float(tail_stress),
            "drawdown_stress": float(drawdown_stress),
            "beta_stress": float(beta_stress)
        }
        
        # Weighted composite stress index
        weights = {
            "correlation_stress": 0.2,
            "volatility_stress": 0.3,
            "tail_stress": 0.2,
            "drawdown_stress": 0.2,
            "beta_stress": 0.1
        }
        
        composite_stress = sum(stress_components[key] * weights[key] for key in weights.keys())
        composite_stress = min(composite_stress, 1.0)  # Cap at 1.0
        
        # Stress level interpretation
        if composite_stress > 0.7:
            stress_level = "extreme"
        elif composite_stress > 0.5:
            stress_level = "high"
        elif composite_stress > 0.3:
            stress_level = "moderate"
        else:
            stress_level = "low"
        
        result = {
            "composite_stress_index": float(composite_stress),
            "stress_level": stress_level,
            "stress_components": stress_components,
            "current_metrics": {
                "correlation": float(current_correlation),
                "volatility": float(current_volatility),
                "current_drawdown": float(current_drawdown),
                "var_95": float(var_95)
            },
            "benchmark_comparison": {
                "correlation_vs_average": float(current_correlation - avg_correlation),
                "volatility_vs_average": float(current_volatility - avg_volatility),
                "average_correlation": float(avg_correlation),
                "average_volatility": float(avg_volatility)
            },
            "data_points": len(ret_aligned)
        }
        
        return standardize_output(result, "calculate_market_stress")
        
    except Exception as e:
        return {"success": False, "error": f"Market stress calculation failed: {str(e)}"}


def calculate_market_breadth(returns_matrix: List[List[float]]) -> Dict[str, Any]:
    """
    Calculate market breadth indicators.
    
    From financial-analysis-function-library.json market_analysis category
    Uses pandas and numpy - no code duplication
    
    Args:
        returns_matrix: Matrix of returns for multiple assets (each row is an asset)
        
    Returns:
        Dict: Market breadth analysis
    """
    try:
        # Convert to DataFrame
        if isinstance(returns_matrix, list):
            returns_df = pd.DataFrame(returns_matrix).T  # Transpose so each column is an asset
        else:
            returns_df = pd.DataFrame(returns_matrix)
        
        if returns_df.empty or len(returns_df.columns) < 2:
            raise ValueError("Need at least 2 assets for breadth calculation")
        
        # Calculate breadth indicators
        
        # 1. Advance/Decline Ratio
        advances = (returns_df > 0).sum(axis=1)  # Assets with positive returns each day
        declines = (returns_df < 0).sum(axis=1)   # Assets with negative returns each day
        unchanged = (returns_df == 0).sum(axis=1) # Assets unchanged
        
        # Avoid division by zero
        ad_ratio = advances / (declines + 0.001)  # Add small epsilon
        
        # 2. Percentage of stocks above their moving average
        ma_20 = returns_df.rolling(window=20).mean()
        above_ma = (returns_df.iloc[-1] > ma_20.iloc[-1]).sum()
        pct_above_ma = above_ma / len(returns_df.columns)
        
        # 3. New highs vs new lows (over last 20 periods)
        if len(returns_df) >= 20:
            period_highs = returns_df.rolling(window=20).max()
            period_lows = returns_df.rolling(window=20).min()
            
            current_values = returns_df.iloc[-1]
            new_highs = (current_values >= period_highs.iloc[-1]).sum()
            new_lows = (current_values <= period_lows.iloc[-1]).sum()
            
            new_high_low_ratio = new_highs / (new_lows + 0.001)
        else:
            new_highs = 0
            new_lows = 0
            new_high_low_ratio = 1.0
        
        # 4. Breadth momentum (rate of change in advance/decline)
        if len(ad_ratio) >= 5:
            breadth_momentum = ad_ratio.iloc[-1] - ad_ratio.iloc[-6]
        else:
            breadth_momentum = 0
        
        # 5. Participation rate (% of assets moving in same direction as market)
        market_return = returns_df.mean(axis=1)  # Simple average as market proxy
        same_direction = ((returns_df > 0) & (market_return > 0).values[:, None]) | \
                        ((returns_df < 0) & (market_return < 0).values[:, None])
        participation_rate = same_direction.mean()
        
        # Current breadth metrics
        current_metrics = {
            "advances": int(advances.iloc[-1]) if len(advances) > 0 else 0,
            "declines": int(declines.iloc[-1]) if len(declines) > 0 else 0,
            "unchanged": int(unchanged.iloc[-1]) if len(unchanged) > 0 else 0,
            "advance_decline_ratio": float(ad_ratio.iloc[-1]) if len(ad_ratio) > 0 else 1.0,
            "percent_above_ma20": float(pct_above_ma),
            "new_highs": int(new_highs),
            "new_lows": int(new_lows),
            "new_high_low_ratio": float(new_high_low_ratio),
            "participation_rate": float(participation_rate.iloc[-1]) if len(participation_rate) > 0 else 0
        }
        
        # Historical averages
        avg_metrics = {
            "avg_ad_ratio": float(ad_ratio.mean()),
            "avg_participation_rate": float(participation_rate.mean()),
            "breadth_momentum": float(breadth_momentum)
        }
        
        # Breadth strength assessment
        strength_score = 0
        
        # Positive factors
        if current_metrics["advance_decline_ratio"] > 1.5:
            strength_score += 1
        if current_metrics["percent_above_ma20"] > 0.6:
            strength_score += 1
        if current_metrics["new_high_low_ratio"] > 2.0:
            strength_score += 1
        if current_metrics["participation_rate"] > 0.6:
            strength_score += 1
        if breadth_momentum > 0.2:
            strength_score += 1
        
        # Breadth strength rating
        if strength_score >= 4:
            breadth_strength = "very_strong"
        elif strength_score >= 3:
            breadth_strength = "strong"
        elif strength_score >= 2:
            breadth_strength = "moderate"
        else:
            breadth_strength = "weak"
        
        result = {
            "total_assets": len(returns_df.columns),
            "observation_periods": len(returns_df),
            "current_breadth": current_metrics,
            "historical_averages": avg_metrics,
            "breadth_analysis": {
                "strength_score": strength_score,
                "max_score": 5,
                "breadth_strength": breadth_strength,
                "is_broad_based": current_metrics["participation_rate"] > 0.5,
                "is_momentum_positive": breadth_momentum > 0
            }
        }
        
        return standardize_output(result, "calculate_market_breadth")
        
    except Exception as e:
        return {"success": False, "error": f"Market breadth calculation failed: {str(e)}"}


def detect_market_regime(prices: Union[pd.Series, Dict[str, Any]], 
                        method: str = "volatility_trend") -> Dict[str, Any]:
    """
    Detect market regimes (bull/bear/sideways).
    
    From financial-analysis-function-library.json market_analysis category
    Complex analytical function combining multiple analytics - uses existing functions
    
    Args:
        prices: Price series data
        method: Detection method ("volatility_trend", "returns_clustering", "technical")
        
    Returns:
        Dict: Market regime detection results
    """
    try:
        price_series = validate_price_data(prices)
        returns = price_series.pct_change().dropna()
        
        if len(returns) < 60:
            raise ValueError("Need at least 60 observations for regime detection")
        
        regimes = []
        
        if method == "volatility_trend":
            # Regime detection based on volatility and trend
            window = 30
            
            # Calculate rolling metrics
            rolling_returns = returns.rolling(window=window).mean()
            rolling_vol = returns.rolling(window=window).std() * np.sqrt(252)
            
            # Get trend strength for each window
            trend_strengths = []
            for i in range(window, len(price_series)):
                price_window = price_series.iloc[i-window:i]
                trend_result = calculate_trend_strength(price_window, method="regression")
                if trend_result.get("success", True):
                    trend_strengths.append(trend_result.get("r_squared", 0))
                else:
                    trend_strengths.append(0)
            
            trend_strength_series = pd.Series(trend_strengths, index=price_series.index[window:])
            
            # Align all series
            min_length = min(len(rolling_returns.dropna()), len(rolling_vol.dropna()), len(trend_strength_series))
            start_idx = max(rolling_returns.first_valid_index(), rolling_vol.first_valid_index(), trend_strength_series.first_valid_index())
            
            aligned_returns = rolling_returns.loc[start_idx:][:min_length]
            aligned_vol = rolling_vol.loc[start_idx:][:min_length]
            aligned_trend = trend_strength_series.loc[start_idx:][:min_length]
            
            # Regime classification
            for i, (date, ret) in enumerate(aligned_returns.items()):
                vol = aligned_vol.iloc[i]
                trend = aligned_trend.iloc[i]
                
                # Bull market: positive returns, strong trend
                if ret > 0.05 and trend > 0.4:
                    regime = "bull"
                # Bear market: negative returns, strong downtrend  
                elif ret < -0.05 and trend > 0.4:
                    regime = "bear"
                # High volatility regime
                elif vol > aligned_vol.quantile(0.8):
                    regime = "volatile"
                # Sideways market: low trend strength
                else:
                    regime = "sideways"
                    
                regimes.append({
                    "date": date,
                    "regime": regime,
                    "rolling_return": float(ret),
                    "rolling_volatility": float(vol),
                    "trend_strength": float(trend)
                })
                
        elif method == "returns_clustering":
            # K-means clustering of return characteristics
            window = 30
            features = []
            dates = []
            
            for i in range(window, len(returns)):
                ret_window = returns.iloc[i-window:i]
                
                # Feature vector: mean return, volatility, skewness, max drawdown
                mean_ret = ret_window.mean()
                vol = ret_window.std()
                skew = ret_window.skew()
                
                # Max drawdown in window
                cum_ret = (1 + ret_window).cumprod()
                rolling_max = cum_ret.expanding().max()
                drawdown = (cum_ret - rolling_max) / rolling_max
                max_dd = drawdown.min()
                
                features.append([mean_ret, vol, skew, max_dd])
                dates.append(returns.index[i])
            
            # Perform clustering
            features_array = np.array(features)
            # Normalize features
            features_normalized = (features_array - features_array.mean(axis=0)) / features_array.std(axis=0)
            
            # K-means with 4 clusters (bull, bear, sideways, volatile)
            kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(features_normalized)
            
            # Interpret clusters based on characteristics
            cluster_characteristics = {}
            for cluster_id in range(4):
                cluster_mask = clusters == cluster_id
                cluster_features = features_array[cluster_mask]
                
                mean_return = cluster_features[:, 0].mean()
                mean_vol = cluster_features[:, 1].mean()
                mean_skew = cluster_features[:, 2].mean()
                mean_dd = cluster_features[:, 3].mean()
                
                # Classify cluster
                if mean_return > 0.01 and mean_dd > -0.05:
                    regime_name = "bull"
                elif mean_return < -0.01 and mean_dd < -0.10:
                    regime_name = "bear"
                elif mean_vol > features_array[:, 1].mean() * 1.5:
                    regime_name = "volatile"
                else:
                    regime_name = "sideways"
                    
                cluster_characteristics[cluster_id] = regime_name
            
            # Create regime timeline
            for i, (date, cluster) in enumerate(zip(dates, clusters)):
                regimes.append({
                    "date": date,
                    "regime": cluster_characteristics[cluster],
                    "cluster_id": int(cluster),
                    "features": {
                        "mean_return": float(features[i][0]),
                        "volatility": float(features[i][1]),
                        "skewness": float(features[i][2]),
                        "max_drawdown": float(features[i][3])
                    }
                })
                
        elif method == "technical":
            # Technical analysis based regime detection
            window = 20
            
            # Calculate technical indicators
            sma_20 = price_series.rolling(window=20).mean()
            sma_50 = price_series.rolling(window=50).mean() if len(price_series) > 50 else sma_20
            
            # Bollinger Bands
            bb_std = price_series.rolling(window=20).std()
            bb_upper = sma_20 + (bb_std * 2)
            bb_lower = sma_20 - (bb_std * 2)
            
            for i in range(max(20, 50), len(price_series)):
                current_price = price_series.iloc[i]
                
                # Price vs moving averages
                above_sma20 = current_price > sma_20.iloc[i]
                above_sma50 = current_price > sma_50.iloc[i]
                
                # Bollinger Band position
                bb_position = (current_price - bb_lower.iloc[i]) / (bb_upper.iloc[i] - bb_lower.iloc[i])
                
                # Recent volatility
                recent_vol = returns.iloc[i-19:i].std() * np.sqrt(252)
                
                # Regime determination
                if above_sma20 and above_sma50 and bb_position > 0.5:
                    regime = "bull"
                elif not above_sma20 and not above_sma50 and bb_position < 0.3:
                    regime = "bear"
                elif recent_vol > returns.std() * np.sqrt(252) * 1.5:
                    regime = "volatile"
                else:
                    regime = "sideways"
                
                regimes.append({
                    "date": price_series.index[i],
                    "regime": regime,
                    "price": float(current_price),
                    "sma20": float(sma_20.iloc[i]),
                    "sma50": float(sma_50.iloc[i]),
                    "bb_position": float(bb_position),
                    "volatility": float(recent_vol)
                })
        
        # Regime statistics
        regime_df = pd.DataFrame(regimes)
        regime_counts = regime_df['regime'].value_counts()
        regime_percentages = (regime_counts / len(regime_df) * 100).round(2)
        
        # Current regime
        current_regime = regimes[-1]['regime'] if regimes else "unknown"
        
        # Regime transitions
        transitions = []
        for i in range(1, len(regimes)):
            if regimes[i]['regime'] != regimes[i-1]['regime']:
                transitions.append({
                    "date": regimes[i]['date'],
                    "from_regime": regimes[i-1]['regime'],
                    "to_regime": regimes[i]['regime']
                })
        
        result = {
            "method": method,
            "total_periods": len(regimes),
            "current_regime": current_regime,
            "regime_timeline": regimes[-10:],  # Last 10 periods
            "regime_statistics": {
                "counts": regime_counts.to_dict(),
                "percentages": regime_percentages.to_dict()
            },
            "regime_transitions": transitions[-5:],  # Last 5 transitions
            "regime_stability": {
                "total_transitions": len(transitions),
                "avg_regime_duration": len(regimes) / max(len(transitions), 1),
                "most_common_regime": regime_counts.index[0] if len(regime_counts) > 0 else "unknown"
            }
        }
        
        return standardize_output(result, "detect_market_regime")
        
    except Exception as e:
        return {"success": False, "error": f"Market regime detection failed: {str(e)}"}


def analyze_volatility_clustering(returns: Union[pd.Series, Dict[str, Any]], 
                                window: int = 20) -> Dict[str, Any]:
    """
    Analyze volatility clustering patterns.
    
    From financial-analysis-function-library.json market_analysis category
    Complex analytical function using statistical analysis - uses existing functions
    
    Args:
        returns: Return series data
        window: Rolling window for volatility calculation
        
    Returns:
        Dict: Volatility clustering analysis
    """
    try:
        returns_series = validate_return_data(returns)
        
        if len(returns_series) < window * 3:
            raise ValueError(f"Need at least {window * 3} observations for clustering analysis")
        
        # Calculate rolling volatility
        rolling_vol = returns_series.rolling(window=window).std() * np.sqrt(252)
        rolling_vol = rolling_vol.dropna()
        
        # Detect high volatility periods (clusters)
        vol_threshold = rolling_vol.quantile(0.75)  # Top 25%
        high_vol_periods = rolling_vol > vol_threshold
        
        # Find volatility clusters (consecutive high volatility periods)
        clusters = []
        in_cluster = False
        cluster_start = None
        cluster_end = None
        
        for date, is_high_vol in high_vol_periods.items():
            if is_high_vol and not in_cluster:
                # Start of new cluster
                in_cluster = True
                cluster_start = date
            elif not is_high_vol and in_cluster:
                # End of cluster
                in_cluster = False
                cluster_end = high_vol_periods.index[high_vol_periods.index.get_loc(date) - 1]
                
                cluster_duration = (high_vol_periods.index.get_loc(cluster_end) - 
                                  high_vol_periods.index.get_loc(cluster_start) + 1)
                
                clusters.append({
                    "start_date": cluster_start,
                    "end_date": cluster_end,
                    "duration": cluster_duration,
                    "avg_volatility": float(rolling_vol.loc[cluster_start:cluster_end].mean()),
                    "max_volatility": float(rolling_vol.loc[cluster_start:cluster_end].max())
                })
        
        # Handle case where we're currently in a cluster
        if in_cluster and cluster_start is not None:
            cluster_end = high_vol_periods.index[-1]
            cluster_duration = (high_vol_periods.index.get_loc(cluster_end) - 
                              high_vol_periods.index.get_loc(cluster_start) + 1)
            clusters.append({
                "start_date": cluster_start,
                "end_date": cluster_end,
                "duration": cluster_duration,
                "avg_volatility": float(rolling_vol.loc[cluster_start:cluster_end].mean()),
                "max_volatility": float(rolling_vol.loc[cluster_start:cluster_end].max()),
                "is_current": True
            })
        
        # Volatility clustering statistics
        if clusters:
            cluster_durations = [c['duration'] for c in clusters]
            avg_cluster_duration = np.mean(cluster_durations)
            max_cluster_duration = max(cluster_durations)
            
            # Time between clusters
            if len(clusters) > 1:
                intervals = []
                for i in range(1, len(clusters)):
                    prev_end = high_vol_periods.index.get_loc(clusters[i-1]['end_date'])
                    curr_start = high_vol_periods.index.get_loc(clusters[i]['start_date'])
                    intervals.append(curr_start - prev_end)
                avg_interval = np.mean(intervals)
            else:
                avg_interval = 0
        else:
            avg_cluster_duration = 0
            max_cluster_duration = 0
            avg_interval = 0
        
        # Autocorrelation in squared returns (ARCH effect indicator)
        returns_squared = returns_series ** 2
        autocorr_lags = min(10, len(returns_squared) // 4)
        autocorrelations = []
        
        for lag in range(1, autocorr_lags + 1):
            if len(returns_squared) > lag:
                corr = returns_squared.corr(returns_squared.shift(lag))
                autocorrelations.append(float(corr) if not np.isnan(corr) else 0)
        
        # Overall clustering strength
        avg_autocorr = np.mean(autocorrelations) if autocorrelations else 0
        clustering_strength = "high" if avg_autocorr > 0.1 else "moderate" if avg_autocorr > 0.05 else "low"
        
        # Current volatility state
        current_vol = rolling_vol.iloc[-1]
        vol_percentile = (rolling_vol <= current_vol).mean()
        
        if vol_percentile > 0.9:
            current_state = "extreme_high"
        elif vol_percentile > 0.75:
            current_state = "high"
        elif vol_percentile > 0.25:
            current_state = "normal"
        else:
            current_state = "low"
        
        result = {
            "window_size": window,
            "total_periods": len(rolling_vol),
            "volatility_threshold": float(vol_threshold),
            "clustering_analysis": {
                "total_clusters": len(clusters),
                "avg_cluster_duration": float(avg_cluster_duration),
                "max_cluster_duration": int(max_cluster_duration),
                "avg_interval_between_clusters": float(avg_interval),
                "clustering_strength": clustering_strength,
                "avg_autocorrelation": float(avg_autocorr)
            },
            "recent_clusters": clusters[-3:] if clusters else [],  # Last 3 clusters
            "current_volatility_state": {
                "current_volatility": float(current_vol),
                "volatility_percentile": float(vol_percentile),
                "state": current_state,
                "in_high_vol_cluster": bool(high_vol_periods.iloc[-1])
            },
            "volatility_statistics": {
                "mean_volatility": float(rolling_vol.mean()),
                "std_volatility": float(rolling_vol.std()),
                "min_volatility": float(rolling_vol.min()),
                "max_volatility": float(rolling_vol.max()),
                "volatility_of_volatility": float(rolling_vol.std() / rolling_vol.mean())
            }
        }
        
        return standardize_output(result, "analyze_volatility_clustering")
        
    except Exception as e:
        return {"success": False, "error": f"Volatility clustering analysis failed: {str(e)}"}


def analyze_seasonality(returns: Union[pd.Series, Dict[str, Any]], 
                       dates: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Analyze seasonal return patterns.
    
    From financial-analysis-function-library.json market_analysis category
    Complex analytical function using time series analysis - uses existing functions
    
    Args:
        returns: Return series data
        dates: Optional list of date strings (if not in returns index)
        
    Returns:
        Dict: Seasonality analysis
    """
    try:
        returns_series = validate_return_data(returns)
        
        # Ensure we have datetime index
        if dates:
            date_index = pd.to_datetime(dates)
            returns_series.index = date_index[:len(returns_series)]
        elif not isinstance(returns_series.index, pd.DatetimeIndex):
            # Try to parse existing index as dates
            returns_series.index = pd.to_datetime(returns_series.index)
        
        if len(returns_series) < 252:  # Need at least 1 year of data
            raise ValueError("Need at least 1 year of data for seasonality analysis")
        
        # Create DataFrame with time components
        df = pd.DataFrame({
            'returns': returns_series,
            'year': returns_series.index.year,
            'month': returns_series.index.month,
            'quarter': returns_series.index.quarter,
            'day_of_week': returns_series.index.dayofweek,
            'day_of_month': returns_series.index.day,
            'week_of_year': returns_series.index.isocalendar().week
        })
        
        # Monthly seasonality
        monthly_stats = df.groupby('month')['returns'].agg([
            'mean', 'std', 'count'
        ]).round(6)
        monthly_stats['annualized_return'] = monthly_stats['mean'] * 12
        monthly_stats['t_stat'] = monthly_stats['mean'] / (monthly_stats['std'] / np.sqrt(monthly_stats['count']))
        
        # Find best and worst months
        best_month = monthly_stats['mean'].idxmax()
        worst_month = monthly_stats['mean'].idxmin()
        
        # Statistical significance tests
        from scipy.stats import f_oneway, ttest_1samp
        
        # ANOVA test for monthly effects
        monthly_groups = [df[df['month'] == month]['returns'].dropna() for month in range(1, 13)]
        monthly_groups = [group for group in monthly_groups if len(group) > 5]  # Filter small groups
        
        if len(monthly_groups) >= 3:
            f_stat, p_value_monthly = f_oneway(*monthly_groups)
            monthly_significant = p_value_monthly < 0.05
        else:
            f_stat, p_value_monthly = 0, 1
            monthly_significant = False
        
        # Calendar anomalies
        january_effect = df[df['month'] == 1]['returns'].mean() - df['returns'].mean()
        summer_months = df[df['month'].isin([5, 6, 7, 8, 9])]['returns'].mean()
        winter_months = df[~df['month'].isin([5, 6, 7, 8, 9])]['returns'].mean()
        sell_in_may_effect = winter_months - summer_months
        
        result = {
            "data_period": {
                "start_date": str(returns_series.index[0].date()),
                "end_date": str(returns_series.index[-1].date()),
                "total_observations": len(returns_series),
                "years_covered": len(df['year'].unique())
            },
            "monthly_seasonality": {
                "statistics": monthly_stats.to_dict(),
                "best_month": int(best_month),
                "worst_month": int(worst_month),
                "is_significant": monthly_significant,
                "f_statistic": float(f_stat),
                "p_value": float(p_value_monthly)
            },
            "calendar_anomalies": {
                "january_effect": float(january_effect),
                "sell_in_may_effect": float(sell_in_may_effect),
                "winter_return": float(winter_months),
                "summer_return": float(summer_months)
            },
            "seasonality_summary": {
                "overall_strength": "strong" if monthly_significant else "weak",
                "most_pronounced_effect": "monthly" if monthly_significant else "none",
                "best_performing_period": f"Month {best_month}",
                "worst_performing_period": f"Month {worst_month}"
            }
        }
        
        return standardize_output(result, "analyze_seasonality")
        
    except Exception as e:
        return {"success": False, "error": f"Seasonality analysis failed: {str(e)}"}


def detect_structural_breaks(prices: Union[pd.Series, Dict[str, Any]], 
                           min_segment_length: int = 30) -> Dict[str, Any]:
    """
    Detect structural breaks in time series.
    
    From financial-analysis-function-library.json market_analysis category
    Complex analytical function using statistical break detection - uses scipy
    
    Args:
        prices: Price series data
        min_segment_length: Minimum length of segments between breaks
        
    Returns:
        Dict: Structural break detection results
    """
    try:
        price_series = validate_price_data(prices)
        
        if len(price_series) < min_segment_length * 3:
            raise ValueError(f"Need at least {min_segment_length * 3} observations for break detection")
        
        returns = price_series.pct_change().dropna()
        log_prices = np.log(price_series)
        
        # CUSUM test for mean shifts
        def cusum_test(data, threshold=1.5):
            """CUSUM test for detecting mean shifts"""
            n = len(data)
            mean_data = data.mean()
            std_data = data.std()
            
            cusum_pos = np.zeros(n)
            cusum_neg = np.zeros(n)
            
            for i in range(1, n):
                cusum_pos[i] = max(0, cusum_pos[i-1] + (data.iloc[i] - mean_data) / std_data - threshold/2)
                cusum_neg[i] = max(0, cusum_neg[i-1] - (data.iloc[i] - mean_data) / std_data - threshold/2)
            
            # Find break points
            pos_breaks = find_peaks(cusum_pos, height=threshold)[0]
            neg_breaks = find_peaks(cusum_neg, height=threshold)[0]
            
            all_breaks = np.concatenate([pos_breaks, neg_breaks])
            all_breaks = np.unique(all_breaks)
            
            return all_breaks
        
        # Apply break detection
        breaks = cusum_test(returns)
        
        # Filter breaks that are too close together
        filtered_breaks = []
        for break_point in breaks:
            if not filtered_breaks or break_point - filtered_breaks[-1] >= min_segment_length:
                filtered_breaks.append(break_point)
        
        # Analyze segments between breaks
        segments = []
        start_idx = 0
        
        for i, break_point in enumerate(filtered_breaks + [len(price_series)]):
            end_idx = min(break_point, len(price_series) - 1)
            
            if end_idx - start_idx >= min_segment_length:
                segment_prices = price_series.iloc[start_idx:end_idx]
                segment_returns = returns.iloc[start_idx:end_idx-1] if end_idx > start_idx else pd.Series()
                
                if len(segment_returns) > 0:
                    segment_stats = {
                        "start_date": str(segment_prices.index[0]),
                        "end_date": str(segment_prices.index[-1]),
                        "duration": len(segment_prices),
                        "total_return": float((segment_prices.iloc[-1] / segment_prices.iloc[0]) - 1),
                        "annualized_return": float(segment_returns.mean() * 252),
                        "volatility": float(segment_returns.std() * np.sqrt(252)),
                        "max_drawdown": float(empyrical.max_drawdown(segment_returns))
                    }
                    segments.append(segment_stats)
            
            start_idx = end_idx
        
        # Break point details
        break_details = []
        for i, break_idx in enumerate(filtered_breaks):
            if break_idx < len(price_series):
                break_details.append({
                    "break_date": str(price_series.index[break_idx]),
                    "break_index": int(break_idx),
                    "price_at_break": float(price_series.iloc[break_idx])
                })
        
        # Overall analysis
        total_breaks = len(filtered_breaks)
        avg_segment_length = len(price_series) / (total_breaks + 1) if total_breaks > 0 else len(price_series)
        
        # Regime stability
        if total_breaks == 0:
            stability = "very_stable"
        elif total_breaks <= 2:
            stability = "stable"
        elif total_breaks <= 5:
            stability = "moderate"
        else:
            stability = "unstable"
        
        result = {
            "detection_parameters": {
                "min_segment_length": min_segment_length,
                "total_observations": len(price_series)
            },
            "structural_breaks": {
                "total_breaks": total_breaks,
                "break_details": break_details,
                "average_segment_length": float(avg_segment_length),
                "regime_stability": stability
            },
            "segments": segments
        }
        
        return standardize_output(result, "detect_structural_breaks")
        
    except Exception as e:
        return {"success": False, "error": f"Structural break detection failed: {str(e)}"}


def detect_crisis_periods(returns: Union[pd.Series, Dict[str, Any]], 
                         threshold: float = -0.15) -> Dict[str, Any]:
    """
    Identify crisis periods based on volatility/drawdowns.
    
    From financial-analysis-function-library.json market_analysis category
    Complex analytical function using multiple crisis indicators - uses existing functions
    
    Args:
        returns: Return series data
        threshold: Drawdown threshold for crisis detection (default -15%)
        
    Returns:
        Dict: Crisis period detection results
    """
    try:
        returns_series = validate_return_data(returns)
        
        if len(returns_series) < 60:
            raise ValueError("Need at least 60 observations for crisis detection")
        
        # Calculate cumulative returns and drawdowns
        cumulative_returns = (1 + returns_series).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        
        # Drawdown-based crisis detection
        crisis_periods = []
        in_crisis = False
        crisis_start = None
        
        for date, dd in drawdown.items():
            if dd <= threshold and not in_crisis:
                # Start of crisis
                in_crisis = True
                crisis_start = date
            elif dd > threshold * 0.5 and in_crisis:  # Recovery threshold
                # End of crisis
                in_crisis = False
                crisis_end = date
                
                # Calculate crisis statistics
                crisis_returns = returns_series.loc[crisis_start:crisis_end]
                crisis_duration = len(crisis_returns)
                max_dd = drawdown.loc[crisis_start:crisis_end].min()
                
                crisis_periods.append({
                    "start_date": str(crisis_start),
                    "end_date": str(crisis_end),
                    "duration_days": crisis_duration,
                    "max_drawdown": float(max_dd),
                    "total_return": float((cumulative_returns.loc[crisis_end] / cumulative_returns.loc[crisis_start]) - 1),
                    "volatility": float(crisis_returns.std() * np.sqrt(252))
                })
        
        # Handle ongoing crisis
        if in_crisis and crisis_start is not None:
            crisis_returns = returns_series.loc[crisis_start:]
            max_dd = drawdown.loc[crisis_start:].min()
            
            crisis_periods.append({
                "start_date": str(crisis_start),
                "end_date": str(returns_series.index[-1]),
                "duration_days": len(crisis_returns),
                "max_drawdown": float(max_dd),
                "total_return": float((cumulative_returns.iloc[-1] / cumulative_returns.loc[crisis_start]) - 1),
                "volatility": float(crisis_returns.std() * np.sqrt(252)),
                "is_ongoing": True
            })
        
        # Crisis statistics
        total_crisis_days = sum(crisis['duration_days'] for crisis in crisis_periods)
        crisis_frequency = len(crisis_periods) / (len(returns_series) / 252) if len(returns_series) > 252 else 0
        
        # Current market state
        current_dd = drawdown.iloc[-1]
        if current_dd <= threshold:
            current_state = "in_crisis"
        elif current_dd <= threshold * 0.5:
            current_state = "recovery"
        else:
            current_state = "normal"
        
        result = {
            "detection_parameters": {
                "drawdown_threshold": threshold,
                "total_observations": len(returns_series)
            },
            "crisis_periods": {
                "total_crises": len(crisis_periods),
                "crisis_events": crisis_periods[-5:]  # Last 5 crises
            },
            "crisis_statistics": {
                "crisis_frequency_per_year": float(crisis_frequency),
                "total_crisis_days": total_crisis_days,
                "percent_time_in_crisis": float((total_crisis_days / len(returns_series)) * 100),
                "worst_crisis_drawdown": float(min([c['max_drawdown'] for c in crisis_periods], default=0))
            },
            "current_market_state": {
                "state": current_state,
                "current_drawdown": float(current_dd)
            }
        }
        
        return standardize_output(result, "detect_crisis_periods")
        
    except Exception as e:
        return {"success": False, "error": f"Crisis period detection failed: {str(e)}"}


# Registry of market analysis functions - both simple and complex
MARKET_ANALYSIS_FUNCTIONS = {
    'calculate_trend_strength': calculate_trend_strength,
    'calculate_market_stress': calculate_market_stress,
    'calculate_market_breadth': calculate_market_breadth,
    'detect_market_regime': detect_market_regime,
    'analyze_volatility_clustering': analyze_volatility_clustering,
    'analyze_seasonality': analyze_seasonality,
    'detect_structural_breaks': detect_structural_breaks,
    'detect_crisis_periods': detect_crisis_periods
}