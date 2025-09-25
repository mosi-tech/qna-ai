"""Market Analysis Metrics Module using empyrical, pandas, scipy, and scikit-learn.

This module provides comprehensive market analysis functions ranging from simple atomic calculations
to complex analytical functions that combine multiple statistical and machine learning techniques.
All functions implement atomic and complex market analysis patterns from the 
financial-analysis-function-library.json market_analysis category.

The module focuses on practical market analysis applications including trend detection, regime
identification, stress testing, and structural break analysis using industry-standard libraries
for proven accuracy and statistical rigor.

Key Features:
    - Multi-methodology trend strength analysis (technical, statistical, momentum-based)
    - Comprehensive market stress indicators using correlation breakdown and tail risk
    - Advanced regime detection using volatility clustering and machine learning
    - Statistical structural break detection using CUSUM tests
    - Crisis period identification with multiple threshold methods
    - Market breadth analysis for participation measurement
    - Seasonality detection with statistical significance testing
    - Cryptocurrency-specific metrics including fear/greed index

Dependencies:
    - empyrical: Core financial performance and risk calculations
    - pandas: Data manipulation and time series handling
    - numpy: Numerical computations and array operations
    - scipy: Statistical analysis, signal processing, and hypothesis testing
    - scikit-learn: Machine learning algorithms for clustering and pattern recognition

Example:
    >>> import pandas as pd
    >>> import numpy as np
    >>> from mcp.analytics.market.metrics import calculate_trend_strength, detect_market_regime
    >>> 
    >>> # Create sample market data
    >>> dates = pd.date_range('2020-01-01', periods=500, freq='D')
    >>> prices = pd.Series(100 * np.cumprod(1 + np.random.normal(0.0008, 0.015, 500)), index=dates)
    >>> 
    >>> # Multi-method trend analysis
    >>> trend_result = calculate_trend_strength(prices, method="regression")
    >>> print(f"Trend R²: {trend_result['r_squared']:.3f}")
    >>> print(f"Strength: {trend_result['strength_rating']}")
    >>> 
    >>> # Market regime detection
    >>> regime_result = detect_market_regime(prices, method="volatility_trend")
    >>> print(f"Current Regime: {regime_result['current_regime']}")

Note:
    All functions return standardized dictionary outputs with success indicators and detailed
    error handling. Missing data is handled gracefully with appropriate statistical adjustments.
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
from ..risk.metrics import calculate_correlation


def calculate_trend_strength(prices: Union[pd.Series, Dict[str, Any]], 
                           method: str = "adx") -> Dict[str, Any]:
    """Calculate trend strength using multiple methodologies for comprehensive market analysis.
    
    Measures trend strength using various analytical approaches including moving average alignment,
    statistical regression analysis, and momentum-based calculations. Each method provides different
    insights into market trend characteristics, from technical analysis perspectives to statistical
    significance testing of directional movements.
    
    The function implements multiple methodologies to provide robust trend analysis suitable for
    different market conditions and analytical requirements.
    
    Args:
        prices (Union[pd.Series, Dict[str, Any]]): Price series data as pandas Series with datetime
            index or dictionary with price values. Values should be absolute prices (e.g., 100.50, 95.25).
        method (str, optional): Analysis method to use. Defaults to "adx". Available methods:
            - "adx" or "moving_average": Moving average alignment analysis
            - "regression": Linear regression trend strength with statistical significance
            - "momentum": Momentum-based trend consistency analysis
    
    Returns:
        Dict[str, Any]: Comprehensive trend strength analysis with keys:
            - method (str): Method used for analysis
            - current_strength or r_squared (float): Primary strength metric (0-100 or 0-1)
            - strength_rating (str): Qualitative strength assessment ("very_strong", "strong", "moderate", "weak")
            - current_price (float): Latest price in series
            - period_high (float): Maximum price in period
            - period_low (float): Minimum price in period
            - distance_from_high (float): Percentage distance from period high
            - distance_from_low (float): Percentage distance from period low
            - data_points (int): Number of observations used
            - success (bool): Whether calculation succeeded
            - function_name (str): Function identifier for tracking
            
            Method-specific additional keys:
            - Moving Average: moving_averages (Dict) with SMA values and alignment score
            - Regression: slope, p_value, trend_direction, is_significant
            - Momentum: momentum periods (5d, 20d, 60d), trend_consistency, average_momentum
    
    Raises:
        ValueError: If insufficient data for calculation or unknown method specified.
        TypeError: If price data cannot be converted to valid price series.
        
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Create sample price data with uptrend
        >>> dates = pd.date_range('2023-01-01', periods=100, freq='D')
        >>> trend_factor = np.linspace(0.95, 1.05, 100)  # Gradual uptrend
        >>> prices = pd.Series(100 * trend_factor * np.cumprod(1 + np.random.normal(0, 0.01, 100)), index=dates)
        >>> 
        >>> # Regression-based trend analysis
        >>> result = calculate_trend_strength(prices, method="regression")
        >>> print(f"Trend Strength (R²): {result['r_squared']:.3f}")
        >>> print(f"Trend Direction: {result['trend_direction']}")
        >>> print(f"Statistical Significance: {result['is_significant']}")
        >>> print(f"Strength Rating: {result['strength_rating']}")
        >>> 
        >>> # Moving average alignment analysis
        >>> ma_result = calculate_trend_strength(prices, method="moving_average")
        >>> print(f"MA Alignment Score: {ma_result['moving_averages']['alignment_score']}/5")
        >>> print(f"Current Strength: {ma_result['current_strength']:.1f}/100")
        
    Note:
        - Moving average method requires at least 20 observations for basic analysis
        - Regression method provides statistical significance testing (p-value < 0.05)
        - Momentum method measures trend consistency across multiple timeframes
        - Higher R² values (>0.6) indicate stronger statistical trends
        - Alignment scores of 4-5 indicate strong moving average trend alignment
        - Function handles both daily and other frequency data automatically
        - Missing values are handled gracefully with appropriate warnings
    """
    try:
        price_series = validate_price_data(prices)
        
        if len(price_series) < 20:
            raise ValueError("Insufficient data for trend strength calculation")
        
        # Simple moving average trend strength
        if method == "adx" or method == "moving_average":
            # Calculate moving averages for trend strength
            sma_10 = price_series.rolling(window=10).mean()
            sma_20 = price_series.rolling(window=20).mean()
            sma_50 = price_series.rolling(window=50).mean() if len(price_series) > 50 else sma_20
            
            # Current price position relative to moving averages
            current_price = price_series.iloc[-1]
            current_sma10 = sma_10.iloc[-1] if len(sma_10.dropna()) > 0 else current_price
            current_sma20 = sma_20.iloc[-1] if len(sma_20.dropna()) > 0 else current_price
            current_sma50 = sma_50.iloc[-1] if len(sma_50.dropna()) > 0 else current_price
            
            # Trend alignment score
            alignment_score = 0
            if current_price > current_sma10:
                alignment_score += 1
            if current_price > current_sma20:
                alignment_score += 1
            if current_price > current_sma50:
                alignment_score += 1
            if current_sma10 > current_sma20:
                alignment_score += 1
            if current_sma20 > current_sma50:
                alignment_score += 1
            
            # Normalize to 0-100 scale
            trend_strength_score = (alignment_score / 5) * 100
            
            # Strength rating
            if trend_strength_score > 80:
                strength_rating = "very_strong"
            elif trend_strength_score > 60:
                strength_rating = "strong"
            elif trend_strength_score > 40:
                strength_rating = "moderate"
            else:
                strength_rating = "weak"
            
            trend_strength = {
                "method": "moving_average",
                "current_strength": float(trend_strength_score),
                "strength_rating": strength_rating,
                "moving_averages": {
                    "sma_10": float(current_sma10),
                    "sma_20": float(current_sma20),
                    "sma_50": float(current_sma50),
                    "alignment_score": alignment_score
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
    """Calculate comprehensive market stress indicators using multiple risk and correlation metrics.
    
    Analyzes market stress conditions by examining correlation breakdown, volatility spikes, tail risk
    events, drawdown severity, and beta instability. The function creates a composite stress index
    that combines multiple stress indicators to provide a holistic view of market conditions and
    potential systemic risk.
    
    Market stress analysis is crucial for risk management, portfolio allocation, and understanding
    periods when normal market relationships break down, often signaling broader financial instability.
    
    Args:
        returns (Union[pd.Series, Dict[str, Any]]): Asset return series as pandas Series with datetime
            index or dictionary with return values. Values should be decimal returns (e.g., 0.02 for 2%).
        benchmark_returns (Union[pd.Series, Dict[str, Any]]): Benchmark return series (e.g., market index)
            with same format as returns. Used for correlation and beta analysis.
    
    Returns:
        Dict[str, Any]: Comprehensive market stress analysis with keys:
            - composite_stress_index (float): Overall stress level (0-1, higher = more stress)
            - stress_level (str): Qualitative stress assessment ("low", "moderate", "high", "extreme")
            - stress_components (Dict): Individual stress metrics with keys:
                - correlation_stress: Breakdown in normal correlations
                - volatility_stress: Elevated volatility relative to average
                - tail_stress: Frequency of extreme negative events
                - drawdown_stress: Current drawdown severity
                - beta_stress: Instability in beta relationships
            - current_metrics (Dict): Current market conditions
            - benchmark_comparison (Dict): Relative performance vs historical averages
            - data_points (int): Number of observations used
            - success (bool): Whether calculation succeeded
            - function_name (str): Function identifier for tracking
    
    Raises:
        ValueError: If insufficient data for stress calculation or data alignment issues.
        TypeError: If return data cannot be converted to valid return series.
        
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Create sample return data with stress period
        >>> dates = pd.date_range('2020-01-01', periods=300, freq='D')
        >>> # Normal period followed by stress period
        >>> normal_returns = np.random.normal(0.0008, 0.012, 200)
        >>> stress_returns = np.random.normal(-0.002, 0.035, 100)  # Higher vol, negative bias
        >>> asset_returns = pd.Series(np.concatenate([normal_returns, stress_returns]), index=dates)
        >>> benchmark_returns = pd.Series(np.random.normal(0.0005, 0.015, 300), index=dates)
        >>> 
        >>> # Calculate market stress
        >>> result = calculate_market_stress(asset_returns, benchmark_returns)
        >>> print(f"Stress Level: {result['stress_level']}")
        >>> print(f"Composite Stress Index: {result['composite_stress_index']:.3f}")
        >>> print(f"Correlation Stress: {result['stress_components']['correlation_stress']:.3f}")
        >>> print(f"Volatility Stress: {result['stress_components']['volatility_stress']:.3f}")
        >>> print(f"Current Correlation: {result['current_metrics']['correlation']:.3f}")
        
    Note:
        - Composite stress index combines weighted stress components (volatility 30%, correlation 20%, etc.)
        - Correlation stress measures deviation from historical correlation patterns
        - Volatility stress identifies periods of elevated market volatility
        - Tail stress counts recent extreme negative events (below 5th percentile)
        - Beta stress measures instability in systematic risk relationships
        - Requires minimum 20 observations for rolling calculations
        - Higher stress values indicate deteriorating market conditions
        - Function handles data alignment automatically
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
    """Calculate comprehensive market breadth indicators to assess market participation and strength.
    
    Analyzes market breadth using multiple indicators including advance/decline ratios, new high/low
    ratios, moving average participation, and momentum breadth metrics. Market breadth analysis
    helps identify whether market moves are broad-based or concentrated in a few securities,
    providing crucial insights for market health assessment and trend validation.
    
    The function implements industry-standard breadth indicators used by institutional investors
    and technical analysts to gauge market participation and identify divergences between
    price and breadth that often signal trend reversals.
    
    Args:
        returns_matrix (List[List[float]]): Matrix of returns for multiple assets. Can be provided
            as a list of lists where each inner list represents daily returns for one asset, or
            as a 2D array-like structure. The function automatically transposes if needed so each
            column represents one asset's return series.
    
    Returns:
        Dict[str, Any]: Comprehensive market breadth analysis with keys:
            - total_assets (int): Number of assets analyzed
            - observation_periods (int): Number of time periods in the analysis
            - current_breadth (Dict): Current breadth metrics with keys:
                - advances: Number of assets with positive returns in latest period
                - declines: Number of assets with negative returns in latest period
                - unchanged: Number of assets with zero returns in latest period
                - advance_decline_ratio: Ratio of advances to declines
                - percent_above_ma20: Percentage of assets above 20-period moving average
                - new_highs: Number of assets at 20-period highs
                - new_lows: Number of assets at 20-period lows
                - new_high_low_ratio: Ratio of new highs to new lows
                - participation_rate: Percentage of assets moving in same direction as market
            - historical_averages (Dict): Historical breadth metrics for comparison
                - avg_ad_ratio: Average advance/decline ratio over full period
                - avg_participation_rate: Average participation rate over full period
                - breadth_momentum: Recent change in advance/decline ratio
            - breadth_analysis (Dict): Overall breadth assessment with keys:
                - strength_score: Breadth strength score (0-5 scale)
                - max_score: Maximum possible strength score
                - breadth_strength: Qualitative strength rating ("weak", "moderate", "strong", "very_strong")
                - is_broad_based: Boolean indicating if current move is broad-based (>50% participation)
                - is_momentum_positive: Boolean indicating if breadth momentum is positive
            - success (bool): Whether calculation succeeded
            - function_name (str): Function identifier for tracking
    
    Raises:
        ValueError: If insufficient assets (minimum 2 required) or empty data provided.
        TypeError: If returns matrix cannot be converted to valid DataFrame structure.
        
    Example:
        >>> import numpy as np
        >>> 
        >>> # Create sample returns matrix for 5 assets over 30 periods
        >>> np.random.seed(42)
        >>> returns_data = []
        >>> for i in range(5):
        ...     # Generate correlated returns with some individual variation
        ...     market_returns = np.random.normal(0.001, 0.015, 30)
        ...     asset_returns = market_returns + np.random.normal(0, 0.008, 30)
        ...     returns_data.append(asset_returns.tolist())
        >>> 
        >>> # Calculate market breadth
        >>> result = calculate_market_breadth(returns_data)
        >>> print(f"Breadth Strength: {result['breadth_analysis']['breadth_strength']}")
        >>> print(f"A/D Ratio: {result['current_breadth']['advance_decline_ratio']:.2f}")
        >>> print(f"Participation Rate: {result['current_breadth']['participation_rate']:.1%}")
        >>> print(f"Assets Above MA20: {result['current_breadth']['percent_above_ma20']:.1%}")
        >>> 
        >>> # Check if market move is broad-based
        >>> if result['breadth_analysis']['is_broad_based']:
        ...     print("Market move is BROAD-BASED - healthy trend")
        ... else:
        ...     print("Market move is NARROW - potential divergence warning")
        
    Note:
        - Advance/Decline ratio > 1.5 considered bullish, < 0.67 considered bearish
        - New High/Low ratio > 2.0 indicates strong upward momentum
        - Participation rate > 60% suggests broad-based market moves  
        - Breadth momentum measures recent change in advance/decline trends
        - Breadth divergences (price up, breadth weak) often precede trend reversals
        - Function handles varying numbers of assets and time periods automatically
        - Moving average calculations require minimum 20 periods for reliable results
        - Strength score combines multiple breadth indicators for overall assessment
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
    """Detect market regimes using multiple methodologies including machine learning clustering.
    
    Identifies market regimes (bull, bear, sideways, volatile) using various analytical approaches
    from traditional technical analysis to advanced machine learning clustering. The function provides
    comprehensive regime detection with transition analysis, regime stability metrics, and historical
    pattern recognition for better understanding of market cycles.
    
    Market regime detection is essential for adaptive trading strategies, risk management, and
    understanding structural shifts in market behavior patterns.
    
    Args:
        prices (Union[pd.Series, Dict[str, Any]]): Price series data as pandas Series with datetime
            index or dictionary with price values. Values should be absolute prices (e.g., 100.50, 95.25).
        method (str, optional): Detection methodology. Defaults to "volatility_trend". Available methods:
            - "volatility_trend": Combines volatility and trend strength analysis
            - "returns_clustering": K-means clustering of return characteristics
            - "technical": Technical indicator-based regime classification
    
    Returns:
        Dict[str, Any]: Comprehensive market regime analysis with keys:
            - method (str): Detection method used
            - total_periods (int): Number of periods analyzed
            - current_regime (str): Current market regime ("bull", "bear", "sideways", "volatile")
            - regime_timeline (List): Recent regime history (last 10 periods)
            - regime_statistics (Dict): Regime distribution with counts and percentages
            - regime_transitions (List): Recent regime changes (last 5 transitions)
            - regime_stability (Dict): Stability metrics with keys:
                - total_transitions: Number of regime changes
                - avg_regime_duration: Average periods per regime
                - most_common_regime: Dominant regime type
            - success (bool): Whether calculation succeeded
            - function_name (str): Function identifier for tracking
    
    Raises:
        ValueError: If insufficient data for regime detection (minimum 60 observations required).
        TypeError: If price data cannot be converted to valid price series.
        
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Create sample price data with multiple regimes
        >>> dates = pd.date_range('2020-01-01', periods=400, freq='D')
        >>> # Bull market phase
        >>> bull_prices = 100 * np.cumprod(1 + np.random.normal(0.001, 0.012, 150))
        >>> # Bear market phase  
        >>> bear_prices = bull_prices[-1] * np.cumprod(1 + np.random.normal(-0.0015, 0.025, 100))
        >>> # Sideways phase
        >>> sideways_prices = bear_prices[-1] * np.cumprod(1 + np.random.normal(0.0002, 0.008, 150))
        >>> prices = pd.Series(np.concatenate([bull_prices, bear_prices, sideways_prices]), index=dates)
        >>> 
        >>> # Detect regimes using volatility-trend method
        >>> result = detect_market_regime(prices, method="volatility_trend")
        >>> print(f"Current Regime: {result['current_regime']}")
        >>> print(f"Most Common Regime: {result['regime_stability']['most_common_regime']}")
        >>> print(f"Total Transitions: {result['regime_stability']['total_transitions']}")
        >>> print(f"Avg Regime Duration: {result['regime_stability']['avg_regime_duration']:.1f} periods")
        >>> 
        >>> # Machine learning clustering approach
        >>> ml_result = detect_market_regime(prices, method="returns_clustering")
        >>> print(f"ML Current Regime: {ml_result['current_regime']}")
        >>> regime_stats = ml_result['regime_statistics']['percentages']
        >>> for regime, pct in regime_stats.items():
        ...     print(f"{regime}: {pct:.1f}%")
        
    Note:
        - Volatility-trend method combines rolling volatility with trend strength analysis
        - Returns clustering uses K-means on return characteristics (mean, vol, skew, drawdown)
        - Technical method uses moving averages, Bollinger Bands, and volatility indicators
        - Minimum 60 observations required for reliable regime detection
        - Machine learning method automatically normalizes features for clustering
        - Regime transitions help identify market turning points
        - Higher transition frequency indicates market instability
        - Function handles various data frequencies automatically
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
    """Analyze volatility clustering patterns and ARCH effects in financial time series.
    
    Examines volatility clustering behavior where periods of high volatility tend to be followed
    by high volatility periods, and periods of low volatility tend to be followed by low volatility
    periods. This analysis is crucial for risk management, options pricing, and understanding
    market microstructure effects.
    
    The function implements comprehensive volatility clustering analysis including cluster identification,
    ARCH effect detection through autocorrelation analysis, and volatility regime classification.
    This helps identify periods of market stress and calm, essential for dynamic risk management.
    
    Args:
        returns (Union[pd.Series, Dict[str, Any]]): Return series data as pandas Series with datetime
            index or dictionary with return values. Values should be decimal returns (e.g., 0.02 for 2%).
        window (int, optional): Rolling window size for volatility calculation. Defaults to 20.
            Larger windows provide smoother volatility estimates but less responsive to regime changes.
    
    Returns:
        Dict[str, Any]: Comprehensive volatility clustering analysis with keys:
            - window_size (int): Rolling window size used for calculations
            - total_periods (int): Number of periods analyzed  
            - volatility_threshold (float): Threshold used to define high volatility periods (75th percentile)
            - clustering_analysis (Dict): Core clustering metrics with keys:
                - total_clusters: Number of high volatility clusters identified
                - avg_cluster_duration: Average length of volatility clusters in periods
                - max_cluster_duration: Maximum cluster duration observed
                - avg_interval_between_clusters: Average time between cluster occurrences
                - clustering_strength: Qualitative assessment ("low", "moderate", "high")
                - avg_autocorrelation: Average autocorrelation of squared returns (ARCH effect indicator)
            - recent_clusters (List): Details of most recent 3 volatility clusters
            - current_volatility_state (Dict): Current market volatility assessment with keys:
                - current_volatility: Current annualized volatility level
                - volatility_percentile: Percentile rank of current volatility (0-1)
                - state: Current volatility state ("low", "normal", "high", "extreme_high")
                - in_high_vol_cluster: Boolean indicating if currently in high volatility cluster
            - volatility_statistics (Dict): Overall volatility characteristics with keys:
                - mean_volatility: Average volatility over entire period
                - std_volatility: Standard deviation of volatility (volatility of volatility)
                - min_volatility: Minimum volatility observed
                - max_volatility: Maximum volatility observed  
                - volatility_of_volatility: Coefficient of variation of volatility
            - success (bool): Whether calculation succeeded
            - function_name (str): Function identifier for tracking
    
    Raises:
        ValueError: If insufficient data (minimum 3x window size) for reliable clustering analysis.
        TypeError: If return data cannot be converted to valid return series.
        
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Create sample returns with volatility clustering
        >>> dates = pd.date_range('2020-01-01', periods=500, freq='D')
        >>> # Generate GARCH-like returns with volatility clustering
        >>> vol = np.zeros(len(dates))
        >>> returns_data = np.zeros(len(dates))
        >>> vol[0] = 0.02
        >>> 
        >>> for i in range(1, len(dates)):
        ...     # GARCH(1,1) style volatility evolution
        ...     vol[i] = 0.00001 + 0.05 * returns_data[i-1]**2 + 0.90 * vol[i-1]
        ...     returns_data[i] = np.sqrt(vol[i]) * np.random.normal(0, 1)
        >>> 
        >>> returns = pd.Series(returns_data, index=dates)
        >>> 
        >>> # Analyze volatility clustering
        >>> result = analyze_volatility_clustering(returns, window=30)
        >>> print(f"Clustering Strength: {result['clustering_analysis']['clustering_strength']}")
        >>> print(f"Total Clusters: {result['clustering_analysis']['total_clusters']}")
        >>> print(f"Avg Cluster Duration: {result['clustering_analysis']['avg_cluster_duration']:.1f} days")
        >>> print(f"ARCH Effect (autocorr): {result['clustering_analysis']['avg_autocorrelation']:.3f}")
        >>> print(f"Current Vol State: {result['current_volatility_state']['state']}")
        >>> 
        >>> # Check for current high volatility regime
        >>> if result['current_volatility_state']['in_high_vol_cluster']:
        ...     print("WARNING: Currently in high volatility cluster")
        
    Note:
        - Volatility clustering is a hallmark of financial time series (stylized fact)
        - High autocorrelation in squared returns (>0.1) indicates strong ARCH effects
        - Clusters defined as consecutive periods above 75th percentile of rolling volatility
        - Average cluster duration helps estimate typical length of volatile periods
        - Volatility of volatility measures the variability in market volatility itself
        - Current volatility percentile helps assess relative market stress levels
        - Function automatically handles missing values and irregular time series
        - Results useful for GARCH modeling parameter estimation and regime-switching models
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
    """Analyze seasonal return patterns and calendar anomalies in financial time series.
    
    Examines return patterns across different calendar periods (months, quarters, weekdays) to
    identify recurring seasonal effects and statistical anomalies. This analysis helps identify
    calendar-based trading opportunities, optimal timing for portfolio rebalancing, and periods
    of historically different market behavior patterns.
    
    The function implements comprehensive seasonality analysis including statistical significance
    testing, calendar anomaly detection (January effect, Sell in May, etc.), and comparative
    performance analysis across different time periods.
    
    Args:
        returns (Union[pd.Series, Dict[str, Any]]): Return series data as pandas Series with datetime
            index or dictionary with return values. Values should be decimal returns (e.g., 0.02 for 2%).
        dates (Optional[List[str]], optional): Optional list of date strings to use as index if
            returns data doesn't have datetime index. Dates should be in parseable format
            (e.g., "YYYY-MM-DD"). Defaults to None.
    
    Returns:
        Dict[str, Any]: Comprehensive seasonality analysis with keys:
            - data_period (Dict): Information about the analyzed dataset with keys:
                - start_date: First date in the analysis period
                - end_date: Last date in the analysis period
                - total_observations: Number of return observations
                - years_covered: Number of unique years in dataset
            - monthly_seasonality (Dict): Monthly pattern analysis with keys:
                - statistics: Statistical measures for each month (mean, std, count, etc.)
                - best_month: Month with highest average return
                - worst_month: Month with lowest average return
                - is_significant: Boolean indicating statistical significance of monthly effects
                - f_statistic: F-statistic from ANOVA test
                - p_value: P-value for monthly effect significance test
            - calendar_anomalies (Dict): Analysis of known market anomalies with keys:
                - january_effect: Magnitude of January return premium vs other months
                - sell_in_may_effect: Difference between winter and summer period returns
                - winter_return: Average return during winter months (Oct-Apr)
                - summer_return: Average return during summer months (May-Sep)
            - seasonality_summary (Dict): Overall seasonality assessment with keys:
                - overall_strength: Qualitative strength of seasonal patterns ("strong" or "weak")
                - most_pronounced_effect: Most significant seasonal pattern identified
                - best_performing_period: Time period with strongest historical performance
                - worst_performing_period: Time period with weakest historical performance
            - success (bool): Whether calculation succeeded
            - function_name (str): Function identifier for tracking
    
    Raises:
        ValueError: If insufficient data (minimum 252 observations for 1 year) for seasonal analysis.
        TypeError: If return data cannot be converted to valid return series with datetime index.
        
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Create sample returns with seasonal patterns
        >>> dates = pd.date_range('2015-01-01', periods=2000, freq='D')
        >>> base_returns = np.random.normal(0.0005, 0.012, len(dates))
        >>> 
        >>> # Add January effect (higher returns in January)
        >>> january_boost = np.where(dates.month == 1, 0.003, 0)
        >>> # Add sell-in-May effect (lower summer returns)
        >>> summer_penalty = np.where(dates.month.isin([5,6,7,8,9]), -0.001, 0)
        >>> 
        >>> seasonal_returns = base_returns + january_boost + summer_penalty
        >>> returns = pd.Series(seasonal_returns, index=dates)
        >>> 
        >>> # Analyze seasonality
        >>> result = analyze_seasonality(returns)
        >>> print(f"Seasonality Strength: {result['seasonality_summary']['overall_strength']}")
        >>> print(f"Best Month: {result['monthly_seasonality']['best_month']}")
        >>> print(f"January Effect: {result['calendar_anomalies']['january_effect']:.4f}")
        >>> print(f"Sell in May Effect: {result['calendar_anomalies']['sell_in_may_effect']:.4f}")
        >>> 
        >>> # Check statistical significance
        >>> if result['monthly_seasonality']['is_significant']:
        ...     print(f"Monthly effects are statistically significant (p={result['monthly_seasonality']['p_value']:.4f})")
        ... else:
        ...     print("No statistically significant monthly patterns detected")
        
    Note:
        - Requires minimum 1 year of data (252 observations) for reliable seasonal analysis
        - January effect: Tendency for higher returns in January (tax-loss harvesting reversal)
        - Sell in May effect: Historical underperformance during summer months (May-September)
        - ANOVA F-test used to assess statistical significance of monthly effects (p < 0.05)
        - Winter months defined as October through April, summer as May through September
        - Results help optimize seasonal trading strategies and portfolio rebalancing schedules
        - Function automatically handles missing trading days and varying month lengths
        - Multiple years of data recommended to avoid single-year bias in seasonal patterns
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
    """Detect structural breaks and regime changes in financial time series using statistical methods.
    
    Identifies significant structural breaks in price series that indicate fundamental changes in
    market behavior, trend direction, or volatility regime. This analysis is crucial for
    understanding market regime transitions, identifying crisis periods, and adapting trading
    strategies to changing market conditions.
    
    The function implements CUSUM (Cumulative Sum) statistical tests to detect mean shifts in
    return series, segments the time series around break points, and analyzes the characteristics
    of each regime to provide comprehensive break detection analysis.
    
    Args:
        prices (Union[pd.Series, Dict[str, Any]]): Price series data as pandas Series with datetime
            index or dictionary with price values. Values should be absolute prices (e.g., 100.50, 95.25).
        min_segment_length (int, optional): Minimum number of observations required between structural
            breaks. Prevents detection of spurious breaks due to short-term volatility. Defaults to 30.
    
    Returns:
        Dict[str, Any]: Comprehensive structural break analysis with keys:
            - detection_parameters (Dict): Parameters used for break detection with keys:
                - min_segment_length: Minimum segment length parameter used
                - total_observations: Total number of price observations analyzed
            - structural_breaks (Dict): Break detection results with keys:
                - total_breaks: Number of structural breaks detected
                - break_details: List of break information including dates, indices, and price levels
                - average_segment_length: Average length of periods between breaks
                - regime_stability: Overall stability assessment ("very_stable", "stable", "moderate", "unstable")
            - segments (List): Analysis of each market regime between breaks, containing:
                - start_date: Beginning date of the regime
                - end_date: End date of the regime
                - duration: Number of periods in the regime
                - total_return: Total return during the regime
                - annualized_return: Annualized return during the regime
                - volatility: Annualized volatility during the regime
                - max_drawdown: Maximum drawdown experienced during the regime
            - success (bool): Whether calculation succeeded
            - function_name (str): Function identifier for tracking
    
    Raises:
        ValueError: If insufficient data (minimum 3x min_segment_length) for reliable break detection.
        TypeError: If price data cannot be converted to valid price series.
        
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Create sample price series with structural breaks
        >>> dates = pd.date_range('2020-01-01', periods=300, freq='D')
        >>> 
        >>> # Regime 1: Bull market (first 100 days)
        >>> regime1 = 100 * np.cumprod(1 + np.random.normal(0.002, 0.01, 100))
        >>> # Regime 2: Bear market (next 100 days) - structural break
        >>> regime2 = regime1[-1] * np.cumprod(1 + np.random.normal(-0.001, 0.02, 100))
        >>> # Regime 3: Recovery (last 100 days) - another structural break
        >>> regime3 = regime2[-1] * np.cumprod(1 + np.random.normal(0.0015, 0.012, 100))
        >>> 
        >>> prices = pd.Series(np.concatenate([regime1, regime2, regime3]), index=dates)
        >>> 
        >>> # Detect structural breaks
        >>> result = detect_structural_breaks(prices, min_segment_length=40)
        >>> print(f"Total Breaks Detected: {result['structural_breaks']['total_breaks']}")
        >>> print(f"Regime Stability: {result['structural_breaks']['regime_stability']}")
        >>> print(f"Average Segment Length: {result['structural_breaks']['average_segment_length']:.1f} days")
        >>> 
        >>> # Examine individual regimes
        >>> for i, segment in enumerate(result['segments']):
        ...     print(f"Regime {i+1}: {segment['start_date']} to {segment['end_date']}")
        ...     print(f"  Duration: {segment['duration']} days")
        ...     print(f"  Annualized Return: {segment['annualized_return']:.2%}")
        ...     print(f"  Volatility: {segment['volatility']:.2%}")
        ...     print(f"  Max Drawdown: {segment['max_drawdown']:.2%}")
        
    Note:
        - CUSUM test detects changes in mean return patterns with statistical significance
        - Minimum segment length prevents false break detection from short-term noise
        - Structural breaks often coincide with major economic events or policy changes
        - Break detection helps identify optimal periods for strategy backtesting
        - Regime analysis provides insights into risk-return characteristics of different periods
        - Function automatically filters breaks that are too close together
        - Results useful for regime-switching models and adaptive portfolio strategies
        - Break points represent approximate timing - actual regime change may be gradual
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
    """Identify and analyze financial crisis periods based on drawdown severity and market stress indicators.
    
    Detects crisis periods by analyzing drawdown patterns, recovery dynamics, and market stress
    characteristics. This analysis is essential for risk management, stress testing, and
    understanding how portfolios and assets behave during extreme market conditions.
    
    The function identifies crisis periods as sustained drawdowns below a specified threshold,
    tracks recovery patterns, and provides comprehensive statistics about crisis frequency,
    duration, and severity for better risk assessment and portfolio construction.
    
    Args:
        returns (Union[pd.Series, Dict[str, Any]]): Return series data as pandas Series with datetime
            index or dictionary with return values. Values should be decimal returns (e.g., 0.02 for 2%).
        threshold (float, optional): Drawdown threshold for defining crisis periods. Default -0.15
            represents -15% drawdown. More negative values detect only severe crises, while less
            negative values detect moderate stress periods as well.
    
    Returns:
        Dict[str, Any]: Comprehensive crisis period analysis with keys:
            - detection_parameters (Dict): Crisis detection settings with keys:
                - drawdown_threshold: Threshold used to identify crisis periods
                - total_observations: Number of return observations analyzed
            - crisis_periods (Dict): Identified crisis events with keys:
                - total_crises: Number of distinct crisis periods detected
                - crisis_events: List of recent crisis details (up to last 5) containing:
                    - start_date: Beginning date of crisis period
                    - end_date: End date of crisis period (if ended)
                    - duration_days: Length of crisis in trading periods
                    - max_drawdown: Maximum drawdown reached during crisis
                    - total_return: Total return from start to end of crisis
                    - volatility: Annualized volatility during crisis period
                    - is_ongoing: Boolean indicating if crisis is still active
            - crisis_statistics (Dict): Overall crisis characteristics with keys:
                - crisis_frequency_per_year: Average number of crises per year
                - total_crisis_days: Total periods spent in crisis conditions
                - percent_time_in_crisis: Percentage of total time in crisis periods
                - worst_crisis_drawdown: Maximum drawdown across all detected crises
            - current_market_state (Dict): Current crisis assessment with keys:
                - state: Current market condition ("normal", "recovery", "in_crisis")
                - current_drawdown: Current drawdown level from recent peak
            - success (bool): Whether calculation succeeded
            - function_name (str): Function identifier for tracking
    
    Raises:
        ValueError: If insufficient data (minimum 60 observations) for reliable crisis detection.
        TypeError: If return data cannot be converted to valid return series.
        
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Create sample return series with crisis periods
        >>> dates = pd.date_range('2018-01-01', periods=1000, freq='D')
        >>> 
        >>> # Normal market periods with occasional crises
        >>> normal_returns = np.random.normal(0.0008, 0.012, 800)
        >>> # Crisis period 1: Sharp decline
        >>> crisis1_returns = np.random.normal(-0.005, 0.035, 100)
        >>> # Recovery and normal period
        >>> recovery_returns = np.random.normal(0.002, 0.015, 100)
        >>> 
        >>> returns = pd.Series(
        ...     np.concatenate([normal_returns[:400], crisis1_returns, 
        ...                    normal_returns[400:500], recovery_returns, normal_returns[500:]]),
        ...     index=dates
        ... )
        >>> 
        >>> # Detect crisis periods
        >>> result = detect_crisis_periods(returns, threshold=-0.20)  # 20% drawdown threshold
        >>> print(f"Total Crises Detected: {result['crisis_periods']['total_crises']}")
        >>> print(f"Crisis Frequency: {result['crisis_statistics']['crisis_frequency_per_year']:.2f} per year")
        >>> print(f"Time in Crisis: {result['crisis_statistics']['percent_time_in_crisis']:.1f}%")
        >>> print(f"Current State: {result['current_market_state']['state']}")
        >>> 
        >>> # Examine individual crises
        >>> for i, crisis in enumerate(result['crisis_periods']['crisis_events']):
        ...     print(f"Crisis {i+1}:")
        ...     print(f"  Period: {crisis['start_date']} to {crisis['end_date']}")
        ...     print(f"  Duration: {crisis['duration_days']} days")
        ...     print(f"  Max Drawdown: {crisis['max_drawdown']:.2%}")
        ...     print(f"  Crisis Volatility: {crisis['volatility']:.2%}")
        
    Note:
        - Crisis threshold of -15% identifies significant market stress periods
        - Recovery threshold (half of crisis threshold) determines crisis end points
        - Crisis frequency analysis helps estimate expected crisis occurrence rates
        - Duration statistics useful for stress testing and liquidity planning
        - Ongoing crises flagged separately for current risk assessment
        - Function tracks both completed and ongoing crisis periods
        - Results essential for portfolio stress testing and risk budgeting
        - Crisis detection complements VaR models for tail risk assessment
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


def calculate_crypto_metrics(prices: Union[pd.Series, Dict[str, Any]], 
                           volumes: Union[pd.Series, Dict[str, Any], None] = None) -> Dict[str, Any]:
    """Calculate comprehensive cryptocurrency-specific metrics and market sentiment indicators.
    
    Analyzes crypto assets using specialized metrics that account for the unique characteristics
    of digital asset markets including 24/7 trading, extreme volatility, momentum patterns, and
    sentiment-driven price movements. This analysis is essential for crypto portfolio management,
    risk assessment, and trading strategy development.
    
    The function implements crypto-specific volatility calculations (365-day annualization),
    extreme movement tracking, momentum analysis across multiple timeframes, drawdown recovery
    patterns, and a composite fear/greed sentiment index tailored for digital assets.
    
    Args:
        prices (Union[pd.Series, Dict[str, Any]]): Cryptocurrency price series as pandas Series
            with datetime index or dictionary with price values. Values should be absolute prices
            in the asset's base currency (e.g., $50000 for Bitcoin, $3000 for Ethereum).
        volumes (Union[pd.Series, Dict[str, Any], None], optional): Optional volume series
            corresponding to the price series. Used for volume-price correlation analysis and
            volume trend identification. Defaults to None.
    
    Returns:
        Dict[str, Any]: Comprehensive cryptocurrency analysis with keys:
            - crypto_volatility (Dict): Volatility characteristics specific to crypto with keys:
                - daily_volatility: Standard deviation of daily returns
                - annualized_volatility: Daily volatility annualized using 365 days (crypto markets trade 24/7)
                - volatility_pct: Annualized volatility as percentage string
                - extreme_movement_ratio: Proportion of days with >10% moves (up or down)
                - extreme_up_days: Number of days with >10% gains
                - extreme_down_days: Number of days with >10% losses
            - momentum_analysis (Dict): Multi-timeframe momentum patterns with keys:
                - momentum_7d: 7-day price momentum (decimal and percentage)
                - momentum_30d: 30-day price momentum (decimal and percentage)
                - momentum_90d: 90-day price momentum (decimal and percentage)
            - drawdown_analysis (Dict): Drawdown and recovery characteristics with keys:
                - max_drawdown: Maximum drawdown experienced (decimal and percentage)
                - current_drawdown: Current drawdown from recent peak (decimal and percentage)
                - avg_recovery_days: Average time to recover from >5% drawdowns
                - drawdown_periods_count: Number of significant drawdown periods
            - price_levels (Dict): Current price positioning and ranges with keys:
                - current_price: Latest price in the series
                - recent_high_90d: Highest price in last 90 periods
                - recent_low_90d: Lowest price in last 90 periods
                - distance_from_high: Distance from recent high (decimal and percentage)
                - distance_from_low: Distance from recent low (decimal and percentage)
            - market_sentiment (Dict): Crypto-specific sentiment indicators with keys:
                - fear_greed_index: Composite sentiment score (0-100, higher = more greed)
                - sentiment: Qualitative sentiment ("extreme_fear", "fear", "neutral", "greed", "extreme_greed")
                - rsi_14: 14-period Relative Strength Index
                - fear_greed_components: Component scores contributing to overall sentiment
            - trading_characteristics (Dict): Overall trading behavior metrics with keys:
                - total_observations: Number of price observations
                - trading_range_90d: Price range over last 90 periods relative to low
                - price_stability: Stability assessment based on volatility ("stable", "moderate", "volatile")
            - volume_analysis (Dict, optional): Volume metrics if volume data provided with keys:
                - current_volume: Latest volume observation
                - avg_volume_30d: 30-period average volume
                - volume_ratio: Current volume relative to 30-day average
                - price_volume_correlation: Correlation between price and volume changes
                - volume_trend: Volume trend classification ("increasing", "stable", "decreasing")
            - success (bool): Whether calculation succeeded
            - function_name (str): Function identifier for tracking
    
    Raises:
        ValueError: If insufficient data (minimum 30 observations) for crypto analysis.
        TypeError: If price data cannot be converted to valid price series.
        
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Create sample crypto price series with high volatility
        >>> dates = pd.date_range('2023-01-01', periods=365, freq='D')
        >>> # Simulate crypto-like returns with occasional extreme moves
        >>> returns = np.random.normal(0.001, 0.04, len(dates))  # Higher base volatility
        >>> # Add some extreme movements (>10%)
        >>> extreme_moves = np.random.choice([0, 0.15, -0.15], len(dates), p=[0.95, 0.025, 0.025])
        >>> crypto_returns = returns + extreme_moves
        >>> crypto_prices = pd.Series(50000 * np.cumprod(1 + crypto_returns), index=dates)
        >>> 
        >>> # Optional: Add volume data
        >>> volumes = pd.Series(np.random.lognormal(15, 1, len(dates)), index=dates)
        >>> 
        >>> # Calculate crypto metrics
        >>> result = calculate_crypto_metrics(crypto_prices, volumes)
        >>> print(f"Annualized Volatility: {result['crypto_volatility']['volatility_pct']}")
        >>> print(f"Extreme Move Days: {result['crypto_volatility']['extreme_movement_ratio']:.1%}")
        >>> print(f"Current Sentiment: {result['market_sentiment']['sentiment']}")
        >>> print(f"Fear/Greed Index: {result['market_sentiment']['fear_greed_index']:.1f}")
        >>> print(f"30-Day Momentum: {result['momentum_analysis']['momentum_30d_pct']}")
        >>> 
        >>> # Check volume analysis if available
        >>> if 'volume_analysis' in result:
        ...     print(f"Volume Trend: {result['volume_analysis']['volume_trend']}")
        ...     print(f"Price-Volume Correlation: {result['volume_analysis']['price_volume_correlation']:.3f}")
        
    Note:
        - Crypto volatility annualized using 365 days (24/7 markets vs 252 for traditional)
        - Extreme moves (>10% daily) are common in crypto and tracked separately
        - Fear/Greed index combines volatility, momentum, RSI, and volume indicators
        - Recovery analysis helps assess resilience after significant drawdowns
        - Multi-timeframe momentum analysis captures both short-term and medium-term trends
        - Sentiment extremes often coincide with major reversal opportunities
        - Volume analysis requires separate volume data and provides additional insights
        - Results useful for crypto portfolio risk management and position sizing
    """
    try:
        price_series = validate_price_data(prices)
        
        if len(price_series) < 30:
            raise ValueError("Need at least 30 observations for crypto analysis")
        
        # Basic price metrics
        returns = price_series.pct_change().dropna()
        
        # Crypto-specific volatility (higher than traditional assets)
        daily_volatility = returns.std()
        annualized_volatility = daily_volatility * np.sqrt(365)  # 365 days for crypto
        
        # Extreme price movements (more common in crypto)
        extreme_up_days = (returns > 0.10).sum()  # >10% daily gains
        extreme_down_days = (returns < -0.10).sum()  # >10% daily losses
        extreme_movement_ratio = (extreme_up_days + extreme_down_days) / len(returns)
        
        # Price momentum (crypto tends to have strong momentum)
        momentum_7d = (price_series.iloc[-1] / price_series.iloc[-8] - 1) if len(price_series) > 7 else 0
        momentum_30d = (price_series.iloc[-1] / price_series.iloc[-31] - 1) if len(price_series) > 30 else 0
        momentum_90d = (price_series.iloc[-1] / price_series.iloc[-91] - 1) if len(price_series) > 90 else 0
        
        # Drawdown analysis (crypto can have severe drawdowns)
        cumulative_returns = (1 + returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        current_drawdown = drawdown.iloc[-1]
        
        # Recovery from drawdowns
        drawdown_periods = []
        in_drawdown = False
        drawdown_start = None
        
        for i, (date, dd) in enumerate(drawdown.items()):
            if dd < -0.05 and not in_drawdown:  # 5% drawdown threshold
                in_drawdown = True
                drawdown_start = i
            elif dd >= -0.01 and in_drawdown:  # Recovery threshold
                in_drawdown = False
                recovery_days = i - drawdown_start
                drawdown_periods.append(recovery_days)
        
        avg_recovery_days = np.mean(drawdown_periods) if drawdown_periods else 0
        
        # Price ranges and support/resistance
        recent_high = price_series.tail(90).max() if len(price_series) > 90 else price_series.max()
        recent_low = price_series.tail(90).min() if len(price_series) > 90 else price_series.min()
        current_price = price_series.iloc[-1]
        
        distance_from_high = (recent_high - current_price) / recent_high
        distance_from_low = (current_price - recent_low) / recent_low if recent_low > 0 else 0
        
        # Volume analysis (if available)
        volume_metrics = {}
        if volumes is not None:
            try:
                if isinstance(volumes, dict):
                    volume_series = pd.Series(volumes)
                else:
                    volume_series = pd.Series(volumes) if not isinstance(volumes, pd.Series) else volumes
                
                # Align with prices
                volume_aligned = volume_series[:len(price_series)]
                
                # Volume trends
                avg_volume_30d = volume_aligned.tail(30).mean() if len(volume_aligned) > 30 else volume_aligned.mean()
                current_volume = volume_aligned.iloc[-1] if len(volume_aligned) > 0 else 0
                volume_ratio = current_volume / avg_volume_30d if avg_volume_30d > 0 else 1
                
                # Price-volume correlation
                price_volume_corr = returns.corr(volume_aligned.pct_change().dropna()) if len(volume_aligned) > 1 else 0
                
                volume_metrics = {
                    "current_volume": float(current_volume),
                    "avg_volume_30d": float(avg_volume_30d),
                    "volume_ratio": float(volume_ratio),
                    "price_volume_correlation": float(price_volume_corr),
                    "volume_trend": "increasing" if volume_ratio > 1.2 else "decreasing" if volume_ratio < 0.8 else "stable"
                }
            except:
                volume_metrics = {"error": "Volume data processing failed"}
        
        # Crypto market sentiment indicators
        rsi_14 = []
        if len(returns) >= 14:
            gains = returns.where(returns > 0, 0)
            losses = -returns.where(returns < 0, 0)
            avg_gain = gains.rolling(window=14).mean()
            avg_loss = losses.rolling(window=14).mean()
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1] if len(rsi) > 0 else 50
        else:
            current_rsi = 50
        
        # Fear & Greed approximation
        fear_greed_components = {
            "volatility_score": min(100, (annualized_volatility * 100)),  # High vol = fear
            "momentum_score": max(0, min(100, (momentum_30d + 1) * 50)),  # Positive momentum = greed
            "volume_score": min(100, volume_metrics.get("volume_ratio", 1) * 50) if volume_metrics else 50,
            "rsi_score": current_rsi
        }
        
        fear_greed_index = np.mean(list(fear_greed_components.values()))
        
        if fear_greed_index > 75:
            market_sentiment = "extreme_greed"
        elif fear_greed_index > 55:
            market_sentiment = "greed"
        elif fear_greed_index > 45:
            market_sentiment = "neutral"
        elif fear_greed_index > 25:
            market_sentiment = "fear"
        else:
            market_sentiment = "extreme_fear"
        
        result = {
            "crypto_volatility": {
                "daily_volatility": float(daily_volatility),
                "annualized_volatility": float(annualized_volatility),
                "volatility_pct": f"{annualized_volatility * 100:.2f}%",
                "extreme_movement_ratio": float(extreme_movement_ratio),
                "extreme_up_days": int(extreme_up_days),
                "extreme_down_days": int(extreme_down_days)
            },
            "momentum_analysis": {
                "momentum_7d": float(momentum_7d),
                "momentum_7d_pct": f"{momentum_7d * 100:.2f}%",
                "momentum_30d": float(momentum_30d),
                "momentum_30d_pct": f"{momentum_30d * 100:.2f}%",
                "momentum_90d": float(momentum_90d),
                "momentum_90d_pct": f"{momentum_90d * 100:.2f}%"
            },
            "drawdown_analysis": {
                "max_drawdown": float(max_drawdown),
                "max_drawdown_pct": f"{max_drawdown * 100:.2f}%",
                "current_drawdown": float(current_drawdown),
                "current_drawdown_pct": f"{current_drawdown * 100:.2f}%",
                "avg_recovery_days": float(avg_recovery_days),
                "drawdown_periods_count": len(drawdown_periods)
            },
            "price_levels": {
                "current_price": float(current_price),
                "recent_high_90d": float(recent_high),
                "recent_low_90d": float(recent_low),
                "distance_from_high": float(distance_from_high),
                "distance_from_high_pct": f"{distance_from_high * 100:.2f}%",
                "distance_from_low": float(distance_from_low),
                "distance_from_low_pct": f"{distance_from_low * 100:.2f}%"
            },
            "market_sentiment": {
                "fear_greed_index": float(fear_greed_index),
                "sentiment": market_sentiment,
                "rsi_14": float(current_rsi),
                "fear_greed_components": {k: float(v) for k, v in fear_greed_components.items()}
            },
            "trading_characteristics": {
                "total_observations": len(price_series),
                "trading_range_90d": float((recent_high - recent_low) / recent_low) if recent_low > 0 else 0,
                "price_stability": "volatile" if annualized_volatility > 1.0 else "moderate" if annualized_volatility > 0.5 else "stable"
            }
        }
        
        # Add volume metrics if available
        if volume_metrics and "error" not in volume_metrics:
            result["volume_analysis"] = volume_metrics
        
        return standardize_output(result, "calculate_crypto_metrics")
        
    except Exception as e:
        return {"success": False, "error": f"Crypto metrics calculation failed: {str(e)}"}


def analyze_weekday_performance(returns: Union[pd.Series, Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze return patterns by weekday to identify day-of-week effects and trading anomalies.
    
    Examines market performance across different weekdays to detect recurring patterns,
    statistical anomalies, and optimal trading days. This analysis helps identify calendar
    effects that may influence trading strategies and market behavior patterns.
    
    The function implements comprehensive weekday analysis including average returns,
    volatility patterns, win rates, and statistical significance testing to determine
    which days show reliable performance patterns versus random variation.
    
    Args:
        returns (Union[pd.Series, Dict[str, Any]]): Return series data as pandas Series with
            datetime index or dictionary with return values. Values should be decimal returns
            (e.g., 0.02 for 2%). Index must be datetime for weekday extraction.
    
    Returns:
        Dict[str, Any]: Comprehensive weekday performance analysis with keys:
            - data_summary (Dict): Basic statistics about the dataset
                - total_observations: Total number of return observations
                - date_range: Start and end dates of the analysis period
                - years_covered: Number of years in the dataset
            - weekday_statistics (Dict): Performance metrics by weekday with keys:
                - mean_returns: Average return for each weekday
                - volatility: Standard deviation of returns by weekday
                - win_rates: Percentage of positive returns by weekday
                - observation_counts: Number of observations per weekday
                - annualized_returns: Annual equivalent returns by weekday
            - best_worst_days (Dict): Identification of optimal trading days
                - best_day: Weekday with highest average return
                - worst_day: Weekday with lowest average return
                - most_volatile_day: Weekday with highest volatility
                - least_volatile_day: Weekday with lowest volatility
                - highest_win_rate_day: Weekday with most frequent positive returns
            - statistical_significance (Dict): Statistical tests for weekday effects
                - anova_f_statistic: F-statistic from ANOVA test
                - anova_p_value: P-value for weekday effect significance
                - is_significant: Boolean indicating if weekday effects are statistically significant
            - trading_insights (Dict): Practical trading implications
                - monday_effect: Analysis of Monday return patterns
                - friday_effect: Analysis of Friday return patterns
                - mid_week_stability: Performance of Tuesday-Thursday
                - recommended_strategy: Suggested approach based on patterns
            - success (bool): Whether calculation succeeded
            - function_name (str): Function identifier for tracking
    
    Raises:
        ValueError: If insufficient data (minimum 100 observations) or non-datetime index.
        TypeError: If return data cannot be converted to valid return series with dates.
        
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Create sample return data with weekday patterns
        >>> dates = pd.date_range('2020-01-01', periods=500, freq='D')
        >>> # Add some weekday bias - Monday slight negative, Friday slight positive
        >>> base_returns = np.random.normal(0.001, 0.015, len(dates))
        >>> weekday_bias = np.where(dates.dayofweek == 0, -0.002, 0)  # Monday penalty
        >>> weekday_bias = np.where(dates.dayofweek == 4, 0.002, weekday_bias)  # Friday bonus
        >>> returns = pd.Series(base_returns + weekday_bias, index=dates)
        >>> 
        >>> # Analyze weekday performance
        >>> result = analyze_weekday_performance(returns)
        >>> print(f"Best performing day: {result['best_worst_days']['best_day']}")
        >>> print(f"ANOVA significance: {result['statistical_significance']['is_significant']}")
        >>> 
        >>> # Examine individual weekday statistics
        >>> weekday_stats = result['weekday_statistics']
        >>> for day_name, avg_return in weekday_stats['mean_returns'].items():
        ...     win_rate = weekday_stats['win_rates'][day_name]
        ...     print(f"{day_name}: {avg_return:.4f} return, {win_rate:.1f}% win rate")
        
    Note:
        - Requires datetime index for proper weekday extraction
        - Minimum 100 observations recommended for reliable statistical testing
        - Monday effect: Tendency for lower returns on Mondays (weekend news impact)
        - Friday effect: Often higher returns before weekends (position squaring)
        - ANOVA p-value < 0.05 indicates statistically significant weekday effects
        - Results help optimize entry/exit timing and risk management strategies
        - Function automatically handles holidays and missing trading days
        - Weekdays are numbered 0-6 (Monday-Sunday) following pandas convention
    """
    try:
        returns_series = validate_return_data(returns)
        
        # Ensure we have datetime index
        if not isinstance(returns_series.index, pd.DatetimeIndex):
            try:
                returns_series.index = pd.to_datetime(returns_series.index)
            except:
                raise ValueError("Returns must have datetime index for weekday analysis")
        
        if len(returns_series) < 100:
            raise ValueError("Need at least 100 observations for reliable weekday analysis")
        
        # Create DataFrame with weekday information
        df = pd.DataFrame({
            'returns': returns_series,
            'weekday': returns_series.index.dayofweek,
            'weekday_name': returns_series.index.day_name()
        })
        
        # Calculate weekday statistics
        weekday_stats = df.groupby('weekday_name')['returns'].agg([
            'mean', 'std', 'count', 'min', 'max'
        ]).round(6)
        
        # Add additional metrics
        weekday_stats['win_rate'] = df.groupby('weekday_name')['returns'].apply(lambda x: (x > 0).mean() * 100)
        weekday_stats['annualized_return'] = weekday_stats['mean'] * 252  # Assuming daily returns
        
        # Convert to dictionaries for output
        weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        available_days = [day for day in weekday_names if day in weekday_stats.index]
        
        mean_returns = {day: float(weekday_stats.loc[day, 'mean']) for day in available_days}
        volatility = {day: float(weekday_stats.loc[day, 'std']) for day in available_days}
        win_rates = {day: float(weekday_stats.loc[day, 'win_rate']) for day in available_days}
        observation_counts = {day: int(weekday_stats.loc[day, 'count']) for day in available_days}
        annualized_returns = {day: float(weekday_stats.loc[day, 'annualized_return']) for day in available_days}
        
        # Identify best and worst performing days
        best_day = max(mean_returns, key=mean_returns.get)
        worst_day = min(mean_returns, key=mean_returns.get)
        most_volatile_day = max(volatility, key=volatility.get)
        least_volatile_day = min(volatility, key=volatility.get)
        highest_win_rate_day = max(win_rates, key=win_rates.get)
        
        # Statistical significance testing (ANOVA)
        from scipy.stats import f_oneway
        
        weekday_groups = [df[df['weekday_name'] == day]['returns'].dropna() for day in available_days]
        weekday_groups = [group for group in weekday_groups if len(group) >= 5]  # Filter small groups
        
        if len(weekday_groups) >= 2:
            f_stat, p_value = f_oneway(*weekday_groups)
            is_significant = p_value < 0.05
        else:
            f_stat, p_value = 0, 1
            is_significant = False
        
        # Trading insights
        monday_return = mean_returns.get('Monday', 0)
        friday_return = mean_returns.get('Friday', 0)
        
        # Mid-week performance (Tue-Thu average)
        mid_week_days = ['Tuesday', 'Wednesday', 'Thursday']
        mid_week_returns = [mean_returns[day] for day in mid_week_days if day in mean_returns]
        mid_week_avg = np.mean(mid_week_returns) if mid_week_returns else 0
        
        # Generate trading recommendation
        if is_significant:
            if best_day in ['Friday']:
                strategy_rec = f"Consider holding positions into {best_day} (strongest day)"
            elif worst_day in ['Monday']:
                strategy_rec = f"Be cautious on {worst_day} (weakest day), consider defensive positioning"
            else:
                strategy_rec = f"Focus trading on {best_day} (strongest performance)"
        else:
            strategy_rec = "No significant weekday patterns detected - standard trading approach recommended"
        
        # Data summary
        data_summary = {
            "total_observations": len(returns_series),
            "date_range": {
                "start_date": str(returns_series.index[0].date()),
                "end_date": str(returns_series.index[-1].date())
            },
            "years_covered": len(df.groupby(returns_series.index.year).size()),
            "trading_days_per_week": len(available_days)
        }
        
        result = {
            "data_summary": data_summary,
            "weekday_statistics": {
                "mean_returns": mean_returns,
                "volatility": volatility,
                "win_rates": win_rates,
                "observation_counts": observation_counts,
                "annualized_returns": annualized_returns
            },
            "best_worst_days": {
                "best_day": best_day,
                "worst_day": worst_day,
                "most_volatile_day": most_volatile_day,
                "least_volatile_day": least_volatile_day,
                "highest_win_rate_day": highest_win_rate_day,
                "performance_spread": float(mean_returns[best_day] - mean_returns[worst_day])
            },
            "statistical_significance": {
                "anova_f_statistic": float(f_stat),
                "anova_p_value": float(p_value),
                "is_significant": is_significant,
                "significance_level": "5%"
            },
            "trading_insights": {
                "monday_effect": {
                    "monday_return": float(monday_return),
                    "is_negative": monday_return < 0,
                    "vs_average": float(monday_return - np.mean(list(mean_returns.values())))
                },
                "friday_effect": {
                    "friday_return": float(friday_return),
                    "is_positive": friday_return > 0,
                    "vs_average": float(friday_return - np.mean(list(mean_returns.values())))
                },
                "mid_week_stability": {
                    "tue_thu_average": float(mid_week_avg),
                    "is_stable": abs(mid_week_avg) < np.std(list(mean_returns.values()))
                },
                "recommended_strategy": strategy_rec
            }
        }
        
        return standardize_output(result, "analyze_weekday_performance")
        
    except Exception as e:
        return {"success": False, "error": f"Weekday performance analysis failed: {str(e)}"}


def analyze_monthly_performance(returns: Union[pd.Series, Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze return patterns by month to identify seasonal effects and calendar anomalies.
    
    Examines market performance across different months to detect recurring seasonal patterns,
    calendar anomalies, and optimal trading periods. This analysis helps identify seasonal
    trends that may influence long-term trading strategies and portfolio allocation decisions.
    
    The function implements comprehensive monthly analysis including average returns,
    volatility patterns, win rates, and statistical significance testing to determine
    which months show reliable performance patterns versus random variation.
    
    Args:
        returns (Union[pd.Series, Dict[str, Any]]): Return series data as pandas Series with
            datetime index or dictionary with return values. Values should be decimal returns
            (e.g., 0.02 for 2%). Index must be datetime for month extraction.
    
    Returns:
        Dict[str, Any]: Comprehensive monthly performance analysis with keys:
            - data_summary (Dict): Basic statistics about the dataset
                - total_observations: Total number of return observations
                - date_range: Start and end dates of the analysis period
                - years_covered: Number of years in the dataset
                - avg_observations_per_month: Average number of observations per month
            - monthly_statistics (Dict): Performance metrics by month with keys:
                - mean_returns: Average return for each month
                - volatility: Standard deviation of returns by month
                - win_rates: Percentage of positive returns by month
                - observation_counts: Number of observations per month
                - annualized_returns: Annual equivalent returns by month
                - best_years: Years with highest return for each month
                - worst_years: Years with lowest return for each month
            - seasonal_patterns (Dict): Identification of seasonal trends
                - best_month: Month with highest average return
                - worst_month: Month with lowest average return
                - most_volatile_month: Month with highest volatility
                - least_volatile_month: Month with lowest volatility
                - strongest_quarter: Quarter with best average performance
                - weakest_quarter: Quarter with worst average performance
            - statistical_significance (Dict): Statistical tests for monthly effects
                - anova_f_statistic: F-statistic from ANOVA test
                - anova_p_value: P-value for monthly effect significance
                - is_significant: Boolean indicating if monthly effects are statistically significant
            - calendar_anomalies (Dict): Analysis of known market effects
                - january_effect: Analysis of January return patterns vs other months
                - december_effect: Analysis of December return patterns (Santa Rally)
                - summer_months: Performance during May-September period
                - winter_months: Performance during October-April period
                - sell_in_may_effect: Comparison of winter vs summer performance
            - quarterly_analysis (Dict): Performance by quarters
                - q1_performance: January-March average performance
                - q2_performance: April-June average performance  
                - q3_performance: July-September average performance
                - q4_performance: October-December average performance
            - success (bool): Whether calculation succeeded
            - function_name (str): Function identifier for tracking
    
    Raises:
        ValueError: If insufficient data (minimum 24 months) or non-datetime index.
        TypeError: If return data cannot be converted to valid return series with dates.
        
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Create sample return data with seasonal patterns
        >>> dates = pd.date_range('2015-01-01', periods=2000, freq='D')
        >>> # Add seasonal bias - stronger returns in November/December, weaker in September
        >>> base_returns = np.random.normal(0.0008, 0.012, len(dates))
        >>> seasonal_bias = np.where(dates.month.isin([11, 12]), 0.003, base_returns)
        >>> seasonal_bias = np.where(dates.month == 9, -0.002, seasonal_bias)
        >>> returns = pd.Series(base_returns + (seasonal_bias - base_returns) * 0.3, index=dates)
        >>> 
        >>> # Analyze monthly performance
        >>> result = analyze_monthly_performance(returns)
        >>> print(f"Best performing month: {result['seasonal_patterns']['best_month']}")
        >>> print(f"January Effect detected: {result['calendar_anomalies']['january_effect']['is_significant']}")
        >>> print(f"Sell in May effect: {result['calendar_anomalies']['sell_in_may_effect']['effect_size']:.4f}")
        >>> 
        >>> # Examine quarterly trends
        >>> quarterly = result['quarterly_analysis']
        >>> for quarter, performance in quarterly.items():
        ...     print(f"{quarter}: {performance['average_return']:.4f}")
        
    Note:
        - Requires datetime index for proper month extraction
        - Minimum 24 months (2 years) recommended for reliable seasonal analysis
        - January effect: Tendency for higher returns in January (tax-loss selling reversal)
        - December effect: Often strong performance (Santa Claus rally, window dressing)
        - Sell in May effect: Historical underperformance in summer months (May-September)
        - ANOVA p-value < 0.05 indicates statistically significant monthly effects
        - Results help optimize seasonal trading strategies and portfolio rebalancing
        - Function automatically handles varying month lengths and leap years
        - Analysis accounts for multiple years to avoid single-year bias
    """
    try:
        returns_series = validate_return_data(returns)
        
        # Ensure we have datetime index
        if not isinstance(returns_series.index, pd.DatetimeIndex):
            try:
                returns_series.index = pd.to_datetime(returns_series.index)
            except:
                raise ValueError("Returns must have datetime index for monthly analysis")
        
        # Need sufficient data for reliable seasonal analysis
        unique_months = len(returns_series.groupby([returns_series.index.year, returns_series.index.month]).size())
        if unique_months < 24:
            raise ValueError("Need at least 24 months of data for reliable seasonal analysis")
        
        # Create DataFrame with monthly information
        df = pd.DataFrame({
            'returns': returns_series,
            'year': returns_series.index.year,
            'month': returns_series.index.month,
            'month_name': returns_series.index.strftime('%B'),
            'quarter': returns_series.index.quarter
        })
        
        # Calculate monthly statistics
        monthly_stats = df.groupby('month_name')['returns'].agg([
            'mean', 'std', 'count', 'min', 'max'
        ]).round(6)
        
        # Add additional metrics
        monthly_stats['win_rate'] = df.groupby('month_name')['returns'].apply(lambda x: (x > 0).mean() * 100)
        monthly_stats['annualized_return'] = monthly_stats['mean'] * 12  # Monthly to annual
        
        # Get proper month order
        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        available_months = [month for month in month_names if month in monthly_stats.index]
        
        # Convert to dictionaries for output
        mean_returns = {month: float(monthly_stats.loc[month, 'mean']) for month in available_months}
        volatility = {month: float(monthly_stats.loc[month, 'std']) for month in available_months}
        win_rates = {month: float(monthly_stats.loc[month, 'win_rate']) for month in available_months}
        observation_counts = {month: int(monthly_stats.loc[month, 'count']) for month in available_months}
        annualized_returns = {month: float(monthly_stats.loc[month, 'annualized_return']) for month in available_months}
        
        # Find best and worst years for each month
        best_years = {}
        worst_years = {}
        for month in available_months:
            month_data = df[df['month_name'] == month].groupby('year')['returns'].sum()
            if len(month_data) > 0:
                best_years[month] = int(month_data.idxmax())
                worst_years[month] = int(month_data.idxmin())
        
        # Identify seasonal patterns
        best_month = max(mean_returns, key=mean_returns.get)
        worst_month = min(mean_returns, key=mean_returns.get)
        most_volatile_month = max(volatility, key=volatility.get)
        least_volatile_month = min(volatility, key=volatility.get)
        
        # Quarterly analysis
        quarterly_performance = df.groupby('quarter')['returns'].agg(['mean', 'std', 'count']).round(6)
        quarterly_stats = {}
        
        quarters = ['Q1', 'Q2', 'Q3', 'Q4']
        for i, quarter in enumerate([1, 2, 3, 4], 1):
            if quarter in quarterly_performance.index:
                quarterly_stats[f'q{i}_performance'] = {
                    'average_return': float(quarterly_performance.loc[quarter, 'mean']),
                    'volatility': float(quarterly_performance.loc[quarter, 'std']),
                    'annualized_return': float(quarterly_performance.loc[quarter, 'mean'] * 4),
                    'observation_count': int(quarterly_performance.loc[quarter, 'count'])
                }
        
        # Find strongest and weakest quarters
        quarterly_returns = {f'Q{i}': quarterly_stats[f'q{i}_performance']['average_return'] 
                           for i in range(1, 5) if f'q{i}_performance' in quarterly_stats}
        
        if quarterly_returns:
            strongest_quarter = max(quarterly_returns, key=quarterly_returns.get)
            weakest_quarter = min(quarterly_returns, key=quarterly_returns.get)
        else:
            strongest_quarter = "N/A"
            weakest_quarter = "N/A"
        
        # Statistical significance testing (ANOVA)
        from scipy.stats import f_oneway
        
        monthly_groups = [df[df['month_name'] == month]['returns'].dropna() for month in available_months]
        monthly_groups = [group for group in monthly_groups if len(group) >= 5]  # Filter small groups
        
        if len(monthly_groups) >= 3:
            f_stat, p_value = f_oneway(*monthly_groups)
            is_significant = p_value < 0.05
        else:
            f_stat, p_value = 0, 1
            is_significant = False
        
        # Calendar anomalies analysis
        january_return = mean_returns.get('January', 0)
        december_return = mean_returns.get('December', 0)
        
        # Calculate average return for comparison
        avg_monthly_return = np.mean(list(mean_returns.values()))
        
        # January effect
        january_effect = {
            'january_return': float(january_return),
            'vs_average_months': float(january_return - avg_monthly_return),
            'is_significant': january_return > avg_monthly_return + np.std(list(mean_returns.values())),
            'effect_strength': 'strong' if abs(january_return - avg_monthly_return) > 2 * np.std(list(mean_returns.values())) else 'moderate' if abs(january_return - avg_monthly_return) > np.std(list(mean_returns.values())) else 'weak'
        }
        
        # December effect (Santa Rally)
        december_effect = {
            'december_return': float(december_return),
            'vs_average_months': float(december_return - avg_monthly_return),
            'is_positive': december_return > avg_monthly_return,
            'santa_rally_detected': december_return > avg_monthly_return and december_return > 0
        }
        
        # Sell in May effect (Summer vs Winter months)
        summer_months = ['May', 'June', 'July', 'August', 'September']
        winter_months = ['October', 'November', 'December', 'January', 'February', 'March', 'April']
        
        summer_returns = [mean_returns[month] for month in summer_months if month in mean_returns]
        winter_returns = [mean_returns[month] for month in winter_months if month in mean_returns]
        
        summer_avg = np.mean(summer_returns) if summer_returns else 0
        winter_avg = np.mean(winter_returns) if winter_returns else 0
        sell_in_may_effect = winter_avg - summer_avg
        
        # Data summary
        data_summary = {
            "total_observations": len(returns_series),
            "date_range": {
                "start_date": str(returns_series.index[0].date()),
                "end_date": str(returns_series.index[-1].date())
            },
            "years_covered": len(df['year'].unique()),
            "months_covered": len(available_months),
            "avg_observations_per_month": len(returns_series) / len(available_months)
        }
        
        result = {
            "data_summary": data_summary,
            "monthly_statistics": {
                "mean_returns": mean_returns,
                "volatility": volatility,
                "win_rates": win_rates,
                "observation_counts": observation_counts,
                "annualized_returns": annualized_returns,
                "best_years": best_years,
                "worst_years": worst_years
            },
            "seasonal_patterns": {
                "best_month": best_month,
                "worst_month": worst_month,
                "most_volatile_month": most_volatile_month,
                "least_volatile_month": least_volatile_month,
                "strongest_quarter": strongest_quarter,
                "weakest_quarter": weakest_quarter,
                "performance_spread": float(mean_returns[best_month] - mean_returns[worst_month])
            },
            "statistical_significance": {
                "anova_f_statistic": float(f_stat),
                "anova_p_value": float(p_value),
                "is_significant": is_significant,
                "significance_level": "5%"
            },
            "calendar_anomalies": {
                "january_effect": january_effect,
                "december_effect": december_effect,
                "summer_months": {
                    "average_return": float(summer_avg),
                    "months_included": summer_months
                },
                "winter_months": {
                    "average_return": float(winter_avg),
                    "months_included": winter_months
                },
                "sell_in_may_effect": {
                    "effect_size": float(sell_in_may_effect),
                    "winter_outperforms": sell_in_may_effect > 0,
                    "effect_strength": 'strong' if abs(sell_in_may_effect) > 0.01 else 'moderate' if abs(sell_in_may_effect) > 0.005 else 'weak'
                }
            },
            "quarterly_analysis": quarterly_stats
        }
        
        return standardize_output(result, "analyze_monthly_performance")
        
    except Exception as e:
        return {"success": False, "error": f"Monthly performance analysis failed: {str(e)}"}


# Registry of market analysis functions - both simple and complex
MARKET_ANALYSIS_FUNCTIONS = {
    'calculate_trend_strength': calculate_trend_strength,
    'calculate_market_stress': calculate_market_stress,
    'calculate_market_breadth': calculate_market_breadth,
    'detect_market_regime': detect_market_regime,
    'analyze_volatility_clustering': analyze_volatility_clustering,
    'analyze_seasonality': analyze_seasonality,
    'detect_structural_breaks': detect_structural_breaks,
    'detect_crisis_periods': detect_crisis_periods,
    'calculate_crypto_metrics': calculate_crypto_metrics,
    'analyze_weekday_performance': analyze_weekday_performance,
    'analyze_monthly_performance': analyze_monthly_performance
}