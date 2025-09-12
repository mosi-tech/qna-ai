"""
Correlation analysis module for portfolio and market relationships.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from scipy import stats


class CorrelationAnalyzer:
    """Analyze correlations between securities and market factors."""
    
    @staticmethod
    def pairwise_correlation(returns_data: Dict[str, List[float]], method: str = "pearson") -> Dict[str, Any]:
        """
        Calculate pairwise correlations between return series.
        
        Args:
            returns_data: Dictionary with symbol as key and returns list as value
            method: Correlation method - 'pearson', 'spearman', 'kendall'
            
        Returns:
            Dictionary with correlation matrix and analysis
        """
        if len(returns_data) < 2:
            return {"error": "Need at least 2 securities for correlation analysis"}
        
        # Convert to DataFrame
        df = pd.DataFrame(returns_data)
        
        # Check for sufficient data
        min_observations = df.count().min()
        if min_observations < 10:
            return {"error": "Insufficient overlapping observations"}
        
        # Calculate correlation matrix
        correlation_matrix = df.corr(method=method)
        
        # Find pairwise correlations
        correlations = []
        symbols = list(returns_data.keys())
        
        for i, symbol1 in enumerate(symbols):
            for j, symbol2 in enumerate(symbols):
                if i < j:  # Avoid duplicates and self-correlation
                    corr_value = correlation_matrix.loc[symbol1, symbol2]
                    if not np.isnan(corr_value):
                        correlations.append({
                            "pair": [symbol1, symbol2],
                            "correlation": float(corr_value),
                            "strength": CorrelationAnalyzer._classify_correlation_strength(corr_value)
                        })
        
        # Sort by correlation strength
        correlations.sort(key=lambda x: abs(x["correlation"]))
        
        return {
            "correlation_matrix": correlation_matrix.to_dict(),
            "pairwise_correlations": correlations,
            "least_correlated_pairs": correlations[:3],
            "most_correlated_pairs": sorted(correlations, key=lambda x: abs(x["correlation"]), reverse=True)[:3],
            "method": method,
            "total_pairs": len(correlations),
            "avg_correlation": np.mean([c["correlation"] for c in correlations]),
            "correlation_range": {
                "min": min([c["correlation"] for c in correlations]) if correlations else 0,
                "max": max([c["correlation"] for c in correlations]) if correlations else 0
            }
        }
    
    @staticmethod
    def rolling_correlation(returns1: List[float], returns2: List[float], window: int = 30) -> Dict[str, Any]:
        """
        Calculate rolling correlation between two return series.
        
        Args:
            returns1: First return series
            returns2: Second return series
            window: Rolling window size
            
        Returns:
            Dictionary with rolling correlation analysis
        """
        if len(returns1) != len(returns2):
            return {"error": "Return series must have same length"}
        
        if len(returns1) < window:
            return {"error": f"Insufficient data: need at least {window} observations"}
        
        df = pd.DataFrame({"series1": returns1, "series2": returns2})
        rolling_corr = df['series1'].rolling(window=window).corr(df['series2'])
        rolling_corr_clean = rolling_corr.dropna()
        
        if rolling_corr_clean.empty:
            return {"error": "No valid rolling correlations calculated"}
        
        return {
            "rolling_correlations": rolling_corr_clean.tolist(),
            "current_correlation": rolling_corr_clean.iloc[-1],
            "avg_correlation": rolling_corr_clean.mean(),
            "max_correlation": rolling_corr_clean.max(),
            "min_correlation": rolling_corr_clean.min(),
            "correlation_volatility": rolling_corr_clean.std(),
            "correlation_trend": "Increasing" if rolling_corr_clean.iloc[-5:].mean() > rolling_corr_clean.iloc[-10:-5].mean() else "Decreasing",
            "window_size": window,
            "observations": len(rolling_corr_clean)
        }
    
    @staticmethod
    def downside_correlation(returns1: List[float], returns2: List[float], threshold: float = 0.0) -> Dict[str, Any]:
        """
        Calculate correlation only during downside periods.
        
        Args:
            returns1: First return series (typically the market)
            returns2: Second return series (security)
            threshold: Threshold below which periods are considered downside
            
        Returns:
            Dictionary with downside correlation analysis
        """
        if len(returns1) != len(returns2):
            return {"error": "Return series must have same length"}
        
        # Identify downside periods for the first series (market)
        downside_mask = [r < threshold for r in returns1]
        
        if not any(downside_mask):
            return {"error": "No downside periods found"}
        
        # Filter returns for downside periods only
        downside_returns1 = [r1 for r1, is_down in zip(returns1, downside_mask) if is_down]
        downside_returns2 = [r2 for r2, is_down in zip(returns2, downside_mask) if is_down]
        
        if len(downside_returns1) < 3:
            return {"error": "Insufficient downside observations"}
        
        # Calculate correlations
        downside_corr = np.corrcoef(downside_returns1, downside_returns2)[0, 1]
        overall_corr = np.corrcoef(returns1, returns2)[0, 1]
        
        # Calculate upside correlation for comparison
        upside_mask = [r >= threshold for r in returns1]
        upside_returns1 = [r1 for r1, is_up in zip(returns1, upside_mask) if is_up]
        upside_returns2 = [r2 for r2, is_up in zip(returns2, upside_mask) if is_up]
        
        upside_corr = np.corrcoef(upside_returns1, upside_returns2)[0, 1] if len(upside_returns1) > 2 else np.nan
        
        return {
            "downside_correlation": float(downside_corr) if not np.isnan(downside_corr) else None,
            "upside_correlation": float(upside_corr) if not np.isnan(upside_corr) else None,
            "overall_correlation": float(overall_corr) if not np.isnan(overall_corr) else None,
            "downside_periods": len(downside_returns1),
            "upside_periods": len(upside_returns1),
            "total_periods": len(returns1),
            "downside_percentage": len(downside_returns1) / len(returns1) * 100,
            "correlation_asymmetry": float(downside_corr - upside_corr) if not (np.isnan(downside_corr) or np.isnan(upside_corr)) else None,
            "diversification_benefit": "Low" if abs(downside_corr) > 0.7 else "Medium" if abs(downside_corr) > 0.4 else "High"
        }
    
    @staticmethod
    def correlation_significance_test(returns1: List[float], returns2: List[float]) -> Dict[str, Any]:
        """
        Test statistical significance of correlation.
        
        Args:
            returns1: First return series
            returns2: Second return series
            
        Returns:
            Dictionary with significance test results
        """
        if len(returns1) != len(returns2) or len(returns1) < 3:
            return {"error": "Invalid or insufficient data"}
        
        # Calculate correlation and significance
        corr_coef, p_value = stats.pearsonr(returns1, returns2)
        
        # Calculate confidence intervals
        n = len(returns1)
        z_score = 0.5 * np.log((1 + corr_coef) / (1 - corr_coef))
        se = 1 / np.sqrt(n - 3)
        
        # 95% confidence interval
        z_lower = z_score - 1.96 * se
        z_upper = z_score + 1.96 * se
        
        corr_lower = (np.exp(2 * z_lower) - 1) / (np.exp(2 * z_lower) + 1)
        corr_upper = (np.exp(2 * z_upper) - 1) / (np.exp(2 * z_upper) + 1)
        
        return {
            "correlation": float(corr_coef),
            "p_value": float(p_value),
            "is_significant": p_value < 0.05,
            "confidence_95_lower": float(corr_lower),
            "confidence_95_upper": float(corr_upper),
            "sample_size": n,
            "interpretation": CorrelationAnalyzer._interpret_correlation(corr_coef, p_value)
        }
    
    @staticmethod
    def portfolio_correlation_analysis(portfolio_returns: Dict[str, List[float]], 
                                       weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Analyze correlation structure of a portfolio.
        
        Args:
            portfolio_returns: Dictionary of symbol -> returns
            weights: Optional portfolio weights
            
        Returns:
            Dictionary with portfolio correlation analysis
        """
        if len(portfolio_returns) < 2:
            return {"error": "Need at least 2 positions for portfolio analysis"}
        
        # Equal weights if not provided
        if weights is None:
            weights = {symbol: 1.0/len(portfolio_returns) for symbol in portfolio_returns.keys()}
        
        # Calculate correlation matrix
        corr_result = CorrelationAnalyzer.pairwise_correlation(portfolio_returns)
        if "error" in corr_result:
            return corr_result
        
        correlations = [c["correlation"] for c in corr_result["pairwise_correlations"]]
        
        # Calculate weighted average correlation
        weighted_corr = 0.0
        total_weight = 0.0
        
        for pair_data in corr_result["pairwise_correlations"]:
            symbol1, symbol2 = pair_data["pair"]
            weight1 = weights.get(symbol1, 0)
            weight2 = weights.get(symbol2, 0)
            pair_weight = weight1 * weight2
            weighted_corr += pair_data["correlation"] * pair_weight
            total_weight += pair_weight
        
        if total_weight > 0:
            weighted_corr /= total_weight
        
        return {
            "correlation_matrix": corr_result["correlation_matrix"],
            "average_correlation": np.mean(correlations),
            "weighted_average_correlation": weighted_corr,
            "correlation_range": {
                "min": min(correlations),
                "max": max(correlations)
            },
            "diversification_score": 1 - abs(np.mean(correlations)),  # Higher is better
            "concentration_risk": "High" if abs(np.mean(correlations)) > 0.7 else "Medium" if abs(np.mean(correlations)) > 0.4 else "Low",
            "least_correlated_pairs": corr_result["least_correlated_pairs"][:3],
            "most_correlated_pairs": corr_result["most_correlated_pairs"][:3],
            "total_positions": len(portfolio_returns),
            "correlation_distribution": {
                "high_correlation": sum(1 for c in correlations if abs(c) > 0.7),
                "medium_correlation": sum(1 for c in correlations if 0.3 < abs(c) <= 0.7),
                "low_correlation": sum(1 for c in correlations if abs(c) <= 0.3)
            }
        }
    
    @staticmethod
    def _classify_correlation_strength(correlation: float) -> str:
        """Classify correlation strength."""
        abs_corr = abs(correlation)
        if abs_corr >= 0.8:
            return "Very Strong"
        elif abs_corr >= 0.6:
            return "Strong"
        elif abs_corr >= 0.4:
            return "Moderate"
        elif abs_corr >= 0.2:
            return "Weak"
        else:
            return "Very Weak"
    
    @staticmethod
    def _interpret_correlation(correlation: float, p_value: float) -> str:
        """Interpret correlation result."""
        strength = CorrelationAnalyzer._classify_correlation_strength(correlation)
        direction = "positive" if correlation > 0 else "negative"
        significance = "statistically significant" if p_value < 0.05 else "not statistically significant"
        
        return f"{strength} {direction} correlation that is {significance} (p={p_value:.4f})"