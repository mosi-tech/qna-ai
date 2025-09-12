"""
Relative strength analysis for comparing asset performance vs benchmarks.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any


class RelativeStrengthAnalyzer:
    """Analyze relative strength performance vs benchmarks."""
    
    @staticmethod
    def calculate_relative_strength(asset_returns: List[float], benchmark_returns: List[float]) -> Dict[str, Any]:
        """
        Calculate relative strength vs benchmark.
        
        Args:
            asset_returns: List of asset returns (as percentages)
            benchmark_returns: List of benchmark returns (as percentages)
            
        Returns:
            Dictionary with relative strength analysis
        """
        if not asset_returns or not benchmark_returns:
            return {"error": "Asset and benchmark returns required"}
        
        if len(asset_returns) != len(benchmark_returns):
            return {"error": "Asset and benchmark return series must be same length"}
        
        if len(asset_returns) < 5:
            return {"error": "Minimum 5 observations required for relative strength analysis"}
        
        asset_array = np.array(asset_returns)
        benchmark_array = np.array(benchmark_returns)
        
        # Calculate relative strength ratios
        relative_ratios = []
        cumulative_asset = 1.0
        cumulative_benchmark = 1.0
        
        for asset_ret, bench_ret in zip(asset_returns, benchmark_returns):
            cumulative_asset *= (1 + asset_ret / 100)
            cumulative_benchmark *= (1 + bench_ret / 100)
            relative_ratios.append(cumulative_asset / cumulative_benchmark)
        
        # Calculate period-over-period relative strength
        period_rs = []
        for i in range(len(asset_returns)):
            if benchmark_returns[i] != 0:
                period_rs.append(asset_returns[i] / benchmark_returns[i])
            else:
                period_rs.append(1.0)  # Neutral if benchmark return is 0
        
        # Identify improvement periods
        rs_improvements = 0
        consecutive_improvements = 0
        max_consecutive = 0
        current_consecutive = 0
        
        for i in range(1, len(relative_ratios)):
            if relative_ratios[i] > relative_ratios[i-1]:
                rs_improvements += 1
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        # Calculate statistics
        total_asset_return = (cumulative_asset - 1) * 100
        total_benchmark_return = (cumulative_benchmark - 1) * 100
        outperformance = total_asset_return - total_benchmark_return
        
        # Beta calculation
        if np.std(benchmark_array) > 0:
            beta = np.cov(asset_array, benchmark_array)[0][1] / np.var(benchmark_array)
        else:
            beta = 1.0
        
        # Alpha calculation (excess return vs beta-adjusted benchmark)
        alpha = np.mean(asset_array) - beta * np.mean(benchmark_array)
        
        return {
            "periods_analyzed": len(asset_returns),
            "total_asset_return": total_asset_return,
            "total_benchmark_return": total_benchmark_return,
            "outperformance": outperformance,
            "relative_strength_ratio": relative_ratios[-1],
            "relative_strength_ratios": relative_ratios,
            "period_relative_strength": period_rs,
            "avg_period_rs": np.mean(period_rs),
            "beta": beta,
            "alpha": alpha,
            "improving_periods": rs_improvements,
            "improvement_rate": rs_improvements / (len(relative_ratios) - 1) * 100,
            "max_consecutive_improvements": max_consecutive,
            "current_trend": "improving" if len(relative_ratios) > 1 and relative_ratios[-1] > relative_ratios[-2] else "weakening",
            "volatility_ratio": np.std(asset_array) / np.std(benchmark_array) if np.std(benchmark_array) > 0 else 1.0,
            "correlation_with_benchmark": np.corrcoef(asset_array, benchmark_array)[0][1] if len(asset_array) > 1 else 0.0
        }
    
    @staticmethod
    def calculate_rolling_relative_strength(asset_returns: List[float], benchmark_returns: List[float],
                                          window: int = 20) -> Dict[str, Any]:
        """
        Calculate rolling relative strength over time.
        
        Args:
            asset_returns: List of asset returns
            benchmark_returns: List of benchmark returns  
            window: Rolling window size
            
        Returns:
            Dictionary with rolling relative strength metrics
        """
        if len(asset_returns) < window:
            return {"error": f"Insufficient data for rolling window of {window}"}
        
        asset_series = pd.Series(asset_returns)
        benchmark_series = pd.Series(benchmark_returns)
        
        # Calculate rolling metrics
        rolling_corr = asset_series.rolling(window).corr(benchmark_series)
        rolling_beta = asset_series.rolling(window).cov(benchmark_series) / benchmark_series.rolling(window).var()
        rolling_alpha = asset_series.rolling(window).mean() - rolling_beta * benchmark_series.rolling(window).mean()
        
        # Calculate rolling relative performance
        asset_cumret = (1 + asset_series / 100).rolling(window).apply(lambda x: x.prod() - 1, raw=True) * 100
        bench_cumret = (1 + benchmark_series / 100).rolling(window).apply(lambda x: x.prod() - 1, raw=True) * 100
        rolling_outperformance = asset_cumret - bench_cumret
        
        return {
            "window_size": window,
            "observations": len(asset_returns),
            "rolling_values": len(rolling_corr.dropna()),
            "rolling_correlation": rolling_corr.dropna().tolist(),
            "rolling_beta": rolling_beta.dropna().tolist(),
            "rolling_alpha": rolling_alpha.dropna().tolist(),
            "rolling_outperformance": rolling_outperformance.dropna().tolist(),
            "current_correlation": rolling_corr.iloc[-1] if not pd.isna(rolling_corr.iloc[-1]) else None,
            "current_beta": rolling_beta.iloc[-1] if not pd.isna(rolling_beta.iloc[-1]) else None,
            "current_alpha": rolling_alpha.iloc[-1] if not pd.isna(rolling_alpha.iloc[-1]) else None,
            "current_outperformance": rolling_outperformance.iloc[-1] if not pd.isna(rolling_outperformance.iloc[-1]) else None,
            "avg_correlation": rolling_corr.mean(),
            "avg_beta": rolling_beta.mean(),
            "avg_alpha": rolling_alpha.mean()
        }