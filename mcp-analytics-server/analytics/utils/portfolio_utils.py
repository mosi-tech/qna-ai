"""
Portfolio calculation utilities for MCP analytics server.
Provides comprehensive portfolio analysis, risk metrics, and performance calculations.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from scipy import stats
from sklearn.covariance import LedoitWolf
import logging

logger = logging.getLogger(__name__)

def calculate_portfolio_returns(df: pd.DataFrame, weights: Dict[str, float]) -> pd.DataFrame:
    """
    Calculate portfolio returns given asset weights.
    
    Args:
        df: DataFrame with asset price columns
        weights: Dictionary mapping asset symbols to weights
        
    Returns:
        DataFrame: Portfolio returns with comprehensive metrics
    """
    try:
        # Ensure weights sum to 1
        total_weight = sum(weights.values())
        if abs(total_weight - 1.0) > 0.001:
            weights = {asset: weight/total_weight for asset, weight in weights.items()}
        
        # Calculate individual asset returns
        returns_df = df.pct_change().dropna()
        
        # Calculate portfolio returns
        portfolio_returns = pd.Series(0.0, index=returns_df.index)
        
        for asset, weight in weights.items():
            if asset in returns_df.columns:
                portfolio_returns += weight * returns_df[asset]
        
        # Calculate cumulative returns
        cumulative_returns = (1 + portfolio_returns).cumprod()
        
        # Create comprehensive return dataframe
        result_df = pd.DataFrame({
            'portfolio_returns': portfolio_returns,
            'cumulative_returns': cumulative_returns,
            'rolling_volatility_30d': portfolio_returns.rolling(30).std() * np.sqrt(252),
            'rolling_sharpe_30d': calculate_rolling_sharpe(portfolio_returns, window=30),
            'drawdown': calculate_drawdown_series(cumulative_returns)
        })
        
        return result_df
        
    except Exception as e:
        logger.error(f"Portfolio return calculation failed: {str(e)}")
        return pd.DataFrame()

def calculate_rolling_sharpe(returns: pd.Series, window: int = 30, risk_free_rate: float = 0.02) -> pd.Series:
    """Calculate rolling Sharpe ratio."""
    try:
        excess_returns = returns - risk_free_rate/252
        rolling_mean = excess_returns.rolling(window).mean()
        rolling_std = excess_returns.rolling(window).std()
        
        return (rolling_mean / rolling_std) * np.sqrt(252)
    except:
        return pd.Series(0.0, index=returns.index)

def calculate_drawdown_series(cumulative_returns: pd.Series) -> pd.Series:
    """Calculate rolling drawdown series."""
    try:
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        return drawdown
    except:
        return pd.Series(0.0, index=cumulative_returns.index)

def calculate_portfolio_risk_metrics(returns: pd.Series, benchmark_returns: pd.Series = None) -> Dict:
    """
    Calculate comprehensive portfolio risk metrics.
    
    Args:
        returns: Portfolio return series
        benchmark_returns: Optional benchmark for relative metrics
        
    Returns:
        dict: Comprehensive risk metrics
    """
    try:
        # Basic return statistics
        total_return = (1 + returns).prod() - 1
        annualized_return = (1 + returns.mean())**252 - 1
        annualized_volatility = returns.std() * np.sqrt(252)
        
        # Risk-adjusted metrics
        sharpe_ratio = calculate_sharpe_ratio(returns)
        sortino_ratio = calculate_sortino_ratio(returns)
        calmar_ratio = calculate_calmar_ratio(returns)
        
        # Drawdown analysis
        cumulative_returns = (1 + returns).cumprod()
        drawdown_metrics = calculate_drawdown_metrics(cumulative_returns)
        
        # Value at Risk metrics
        var_metrics = calculate_var_metrics(returns)
        
        # Tail risk metrics
        tail_metrics = calculate_tail_risk_metrics(returns)
        
        # Beta and correlation (if benchmark provided)
        relative_metrics = {}
        if benchmark_returns is not None:
            relative_metrics = calculate_relative_metrics(returns, benchmark_returns)
        
        return {
            "return_metrics": {
                "total_return": float(total_return),
                "annualized_return": float(annualized_return),
                "annualized_volatility": float(annualized_volatility),
                "best_day": float(returns.max()),
                "worst_day": float(returns.min()),
                "positive_days": int((returns > 0).sum()),
                "negative_days": int((returns < 0).sum()),
                "win_rate": float((returns > 0).mean())
            },
            "risk_adjusted_metrics": {
                "sharpe_ratio": float(sharpe_ratio),
                "sortino_ratio": float(sortino_ratio),
                "calmar_ratio": float(calmar_ratio),
                "information_ratio": relative_metrics.get("information_ratio", 0.0)
            },
            "drawdown_metrics": drawdown_metrics,
            "var_metrics": var_metrics,
            "tail_risk_metrics": tail_metrics,
            **relative_metrics
        }
        
    except Exception as e:
        logger.error(f"Risk metrics calculation failed: {str(e)}")
        return {"error": str(e)}

def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """Calculate Sharpe ratio."""
    try:
        excess_returns = returns - risk_free_rate/252
        return float((excess_returns.mean() / excess_returns.std()) * np.sqrt(252))
    except:
        return 0.0

def calculate_sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """Calculate Sortino ratio (uses downside deviation)."""
    try:
        excess_returns = returns - risk_free_rate/252
        downside_returns = excess_returns[excess_returns < 0]
        downside_deviation = downside_returns.std()
        
        if downside_deviation == 0:
            return 0.0
            
        return float((excess_returns.mean() / downside_deviation) * np.sqrt(252))
    except:
        return 0.0

def calculate_calmar_ratio(returns: pd.Series) -> float:
    """Calculate Calmar ratio (return/max drawdown)."""
    try:
        annual_return = (1 + returns.mean())**252 - 1
        cumulative_returns = (1 + returns).cumprod()
        max_drawdown = calculate_max_drawdown(cumulative_returns)
        
        if max_drawdown == 0:
            return 0.0
            
        return float(annual_return / abs(max_drawdown))
    except:
        return 0.0

def calculate_drawdown_metrics(cumulative_returns: pd.Series) -> Dict:
    """Calculate comprehensive drawdown metrics."""
    try:
        running_max = cumulative_returns.expanding().max()
        drawdowns = (cumulative_returns - running_max) / running_max
        
        # Maximum drawdown
        max_drawdown = drawdowns.min()
        
        # Drawdown duration analysis
        in_drawdown = drawdowns < -0.001  # Consider -0.1% threshold
        drawdown_periods = identify_drawdown_periods(in_drawdown)
        
        # Current drawdown
        current_drawdown = drawdowns.iloc[-1]
        current_duration = calculate_current_drawdown_duration(in_drawdown)
        
        # Recovery analysis
        recovery_metrics = calculate_recovery_metrics(drawdowns, running_max, cumulative_returns)
        
        return {
            "max_drawdown": float(max_drawdown),
            "current_drawdown": float(current_drawdown),
            "current_drawdown_duration_days": int(current_duration),
            "average_drawdown": float(drawdowns[drawdowns < 0].mean()) if len(drawdowns[drawdowns < 0]) > 0 else 0.0,
            "drawdown_frequency": len(drawdown_periods),
            "average_drawdown_duration_days": float(np.mean([p["duration"] for p in drawdown_periods])) if drawdown_periods else 0.0,
            "longest_drawdown_duration_days": max([p["duration"] for p in drawdown_periods]) if drawdown_periods else 0,
            **recovery_metrics
        }
        
    except Exception as e:
        logger.error(f"Drawdown metrics calculation failed: {str(e)}")
        return {"max_drawdown": 0.0, "current_drawdown": 0.0}

def calculate_max_drawdown(cumulative_returns: pd.Series) -> float:
    """Calculate maximum drawdown."""
    try:
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        return float(drawdown.min())
    except:
        return 0.0

def identify_drawdown_periods(in_drawdown: pd.Series) -> List[Dict]:
    """Identify discrete drawdown periods."""
    periods = []
    start_idx = None
    
    for i, is_dd in enumerate(in_drawdown):
        if is_dd and start_idx is None:
            start_idx = i
        elif not is_dd and start_idx is not None:
            periods.append({
                "start_idx": start_idx,
                "end_idx": i-1,
                "duration": i - start_idx,
                "start_date": in_drawdown.index[start_idx],
                "end_date": in_drawdown.index[i-1]
            })
            start_idx = None
    
    # Handle case where drawdown continues to end
    if start_idx is not None:
        periods.append({
            "start_idx": start_idx,
            "end_idx": len(in_drawdown)-1,
            "duration": len(in_drawdown) - start_idx,
            "start_date": in_drawdown.index[start_idx],
            "end_date": in_drawdown.index[-1]
        })
    
    return periods

def calculate_current_drawdown_duration(in_drawdown: pd.Series) -> int:
    """Calculate current drawdown duration in days."""
    if not in_drawdown.iloc[-1]:
        return 0
    
    # Count consecutive True values from the end
    duration = 0
    for i in range(len(in_drawdown)-1, -1, -1):
        if in_drawdown.iloc[i]:
            duration += 1
        else:
            break
    
    return duration

def calculate_recovery_metrics(drawdowns: pd.Series, running_max: pd.Series, cumulative_returns: pd.Series) -> Dict:
    """Calculate recovery time metrics."""
    try:
        # Find recovery times for completed drawdown periods
        recovery_times = []
        
        # Simplified recovery calculation
        in_recovery = (cumulative_returns >= running_max * 0.999)  # Within 0.1% of high water mark
        
        return {
            "average_recovery_time_days": float(np.mean(recovery_times)) if recovery_times else 0.0,
            "longest_recovery_time_days": max(recovery_times) if recovery_times else 0,
            "is_at_high_water_mark": bool(in_recovery.iloc[-1])
        }
        
    except Exception as e:
        logger.warning(f"Recovery metrics calculation failed: {str(e)}")
        return {"average_recovery_time_days": 0.0, "longest_recovery_time_days": 0}

def calculate_var_metrics(returns: pd.Series, confidence_levels: List[float] = [0.95, 0.99]) -> Dict:
    """Calculate Value at Risk metrics."""
    try:
        var_metrics = {}
        
        for confidence in confidence_levels:
            # Historical VaR
            var_historical = returns.quantile(1 - confidence)
            
            # Parametric VaR (assuming normal distribution)
            mean_return = returns.mean()
            std_return = returns.std()
            var_parametric = mean_return + std_return * stats.norm.ppf(1 - confidence)
            
            # Modified VaR (Cornish-Fisher expansion)
            skewness = returns.skew()
            kurtosis = returns.kurtosis()
            z_score = stats.norm.ppf(1 - confidence)
            
            # Cornish-Fisher adjustment
            z_cf = z_score + (z_score**2 - 1) * skewness / 6 + \
                   (z_score**3 - 3*z_score) * kurtosis / 24 - \
                   (2*z_score**3 - 5*z_score) * skewness**2 / 36
            
            var_modified = mean_return + std_return * z_cf
            
            var_metrics[f"var_{int(confidence*100)}"] = {
                "historical": float(var_historical),
                "parametric": float(var_parametric),
                "modified": float(var_modified)
            }
        
        return var_metrics
        
    except Exception as e:
        logger.error(f"VaR calculation failed: {str(e)}")
        return {}

def calculate_tail_risk_metrics(returns: pd.Series) -> Dict:
    """Calculate tail risk metrics including Expected Shortfall."""
    try:
        # Expected Shortfall (Conditional VaR) at 95% and 99%
        var_95 = returns.quantile(0.05)
        var_99 = returns.quantile(0.01)
        
        es_95 = returns[returns <= var_95].mean()
        es_99 = returns[returns <= var_99].mean()
        
        # Tail ratio
        tail_ratio = abs(returns.quantile(0.95)) / abs(returns.quantile(0.05)) if returns.quantile(0.05) != 0 else 0
        
        # Extreme value statistics
        extreme_losses = returns[returns <= returns.quantile(0.01)]
        extreme_gains = returns[returns >= returns.quantile(0.99)]
        
        return {
            "expected_shortfall_95": float(es_95),
            "expected_shortfall_99": float(es_99),
            "tail_ratio": float(tail_ratio),
            "extreme_loss_frequency": len(extreme_losses),
            "extreme_gain_frequency": len(extreme_gains),
            "skewness": float(returns.skew()),
            "kurtosis": float(returns.kurtosis()),
            "jarque_bera_test": calculate_jarque_bera_test(returns)
        }
        
    except Exception as e:
        logger.error(f"Tail risk calculation failed: {str(e)}")
        return {}

def calculate_jarque_bera_test(returns: pd.Series) -> Dict:
    """Perform Jarque-Bera test for normality."""
    try:
        jb_stat, p_value = stats.jarque_bera(returns.dropna())
        
        return {
            "statistic": float(jb_stat),
            "p_value": float(p_value),
            "is_normal": bool(p_value > 0.05)  # 5% significance level
        }
    except:
        return {"statistic": 0.0, "p_value": 1.0, "is_normal": True}

def calculate_relative_metrics(portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> Dict:
    """Calculate portfolio metrics relative to benchmark."""
    try:
        # Align time series
        aligned_data = pd.DataFrame({
            'portfolio': portfolio_returns,
            'benchmark': benchmark_returns
        }).dropna()
        
        if len(aligned_data) < 2:
            return {}
        
        portfolio_aligned = aligned_data['portfolio']
        benchmark_aligned = aligned_data['benchmark']
        
        # Beta calculation
        covariance = np.cov(portfolio_aligned, benchmark_aligned)[0, 1]
        benchmark_variance = np.var(benchmark_aligned)
        beta = covariance / benchmark_variance if benchmark_variance != 0 else 1.0
        
        # Alpha calculation (CAPM)
        portfolio_mean = portfolio_aligned.mean() * 252  # Annualized
        benchmark_mean = benchmark_aligned.mean() * 252  # Annualized
        risk_free_rate = 0.02  # Assume 2%
        
        alpha = portfolio_mean - (risk_free_rate + beta * (benchmark_mean - risk_free_rate))
        
        # Tracking error and Information Ratio
        excess_returns = portfolio_aligned - benchmark_aligned
        tracking_error = excess_returns.std() * np.sqrt(252)
        information_ratio = (excess_returns.mean() * 252) / tracking_error if tracking_error != 0 else 0
        
        # Correlation
        correlation = portfolio_aligned.corr(benchmark_aligned)
        
        # Up/Down capture ratios
        up_capture, down_capture = calculate_capture_ratios(portfolio_aligned, benchmark_aligned)
        
        return {
            "beta": float(beta),
            "alpha_annualized": float(alpha),
            "correlation": float(correlation),
            "tracking_error_annualized": float(tracking_error),
            "information_ratio": float(information_ratio),
            "up_capture_ratio": float(up_capture),
            "down_capture_ratio": float(down_capture)
        }
        
    except Exception as e:
        logger.error(f"Relative metrics calculation failed: {str(e)}")
        return {}

def calculate_capture_ratios(portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> Tuple[float, float]:
    """Calculate up and down capture ratios."""
    try:
        # Separate up and down periods
        up_periods = benchmark_returns > 0
        down_periods = benchmark_returns < 0
        
        # Up capture ratio
        if up_periods.sum() > 0:
            up_portfolio = portfolio_returns[up_periods].mean()
            up_benchmark = benchmark_returns[up_periods].mean()
            up_capture = up_portfolio / up_benchmark if up_benchmark != 0 else 1.0
        else:
            up_capture = 1.0
        
        # Down capture ratio
        if down_periods.sum() > 0:
            down_portfolio = portfolio_returns[down_periods].mean()
            down_benchmark = benchmark_returns[down_periods].mean()
            down_capture = down_portfolio / down_benchmark if down_benchmark != 0 else 1.0
        else:
            down_capture = 1.0
        
        return up_capture, down_capture
        
    except:
        return 1.0, 1.0

def calculate_portfolio_concentration(weights: Dict[str, float], prices_df: pd.DataFrame = None) -> Dict:
    """
    Calculate portfolio concentration metrics.
    
    Args:
        weights: Dictionary of asset weights
        prices_df: Optional price data for value-based concentration
        
    Returns:
        dict: Concentration metrics
    """
    try:
        weight_values = list(weights.values())
        
        # Herfindahl-Hirschman Index
        hhi = sum(w**2 for w in weight_values)
        
        # Effective number of holdings
        effective_holdings = 1 / hhi if hhi > 0 else 0
        
        # Weight-based metrics
        max_weight = max(weight_values) if weight_values else 0
        top_5_weight = sum(sorted(weight_values, reverse=True)[:5])
        top_10_weight = sum(sorted(weight_values, reverse=True)[:10])
        
        # Gini coefficient for weight inequality
        gini_coefficient = calculate_gini_coefficient(weight_values)
        
        concentration_metrics = {
            "herfindahl_index": float(hhi),
            "effective_number_holdings": float(effective_holdings),
            "max_single_weight": float(max_weight),
            "top_5_weight_percent": float(top_5_weight * 100),
            "top_10_weight_percent": float(top_10_weight * 100),
            "gini_coefficient": float(gini_coefficient),
            "concentration_level": classify_concentration_level(hhi, len(weight_values))
        }
        
        return concentration_metrics
        
    except Exception as e:
        logger.error(f"Concentration calculation failed: {str(e)}")
        return {}

def calculate_gini_coefficient(weights: List[float]) -> float:
    """Calculate Gini coefficient for weight distribution."""
    try:
        sorted_weights = sorted(weights)
        n = len(sorted_weights)
        cumsum = np.cumsum(sorted_weights)
        
        return (n + 1 - 2 * sum((n + 1 - i) * y for i, y in enumerate(cumsum))) / (n * sum(sorted_weights))
    except:
        return 0.0

def classify_concentration_level(hhi: float, num_holdings: int) -> str:
    """Classify portfolio concentration level."""
    if hhi > 0.25:
        return "highly_concentrated"
    elif hhi > 0.15:
        return "moderately_concentrated"
    elif hhi > 0.1:
        return "somewhat_concentrated"
    else:
        return "well_diversified"

def calculate_correlation_matrix(returns_df: pd.DataFrame, method: str = "pearson") -> Dict:
    """
    Calculate comprehensive correlation analysis.
    
    Args:
        returns_df: DataFrame with asset returns
        method: Correlation method ("pearson", "spearman", "kendall")
        
    Returns:
        dict: Correlation analysis results
    """
    try:
        # Calculate correlation matrix
        corr_matrix = returns_df.corr(method=method)
        
        # Average correlation (excluding diagonal)
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
        avg_correlation = corr_matrix.values[mask].mean()
        
        # Maximum and minimum correlations
        max_correlation = corr_matrix.values[mask].max()
        min_correlation = corr_matrix.values[mask].min()
        
        # Highly correlated pairs (>0.7)
        high_corr_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    high_corr_pairs.append({
                        "asset_1": corr_matrix.columns[i],
                        "asset_2": corr_matrix.columns[j],
                        "correlation": float(corr_val)
                    })
        
        # Eigenvalue analysis for systemic risk
        eigenvalues = np.linalg.eigvals(corr_matrix.values)
        largest_eigenvalue = eigenvalues.max()
        eigenvalue_ratio = largest_eigenvalue / len(eigenvalues)
        
        return {
            "correlation_matrix": corr_matrix.round(3).to_dict(),
            "average_correlation": float(avg_correlation),
            "max_correlation": float(max_correlation),
            "min_correlation": float(min_correlation),
            "high_correlation_pairs": high_corr_pairs,
            "eigenvalue_analysis": {
                "largest_eigenvalue": float(largest_eigenvalue),
                "eigenvalue_ratio": float(eigenvalue_ratio),
                "systemic_risk_level": classify_systemic_risk(eigenvalue_ratio)
            },
            "diversification_score": calculate_diversification_score(avg_correlation, len(corr_matrix))
        }
        
    except Exception as e:
        logger.error(f"Correlation analysis failed: {str(e)}")
        return {}

def classify_systemic_risk(eigenvalue_ratio: float) -> str:
    """Classify systemic risk based on eigenvalue concentration."""
    if eigenvalue_ratio > 0.4:
        return "high"
    elif eigenvalue_ratio > 0.3:
        return "moderate"
    else:
        return "low"

def calculate_diversification_score(avg_correlation: float, num_assets: int) -> float:
    """Calculate diversification score (0-100)."""
    try:
        # Penalize high correlations and reward more assets
        correlation_penalty = abs(avg_correlation) * 50
        asset_bonus = min(num_assets * 2, 30)  # Cap at 30 points
        
        base_score = 70  # Starting score
        final_score = max(0, min(100, base_score - correlation_penalty + asset_bonus))
        
        return float(final_score)
    except:
        return 50.0

def optimize_portfolio_weights(returns_df: pd.DataFrame, method: str = "equal_weight", **kwargs) -> Dict:
    """
    Calculate optimal portfolio weights using various methods.
    
    Args:
        returns_df: DataFrame with asset returns
        method: Optimization method ("equal_weight", "min_variance", "max_sharpe", "risk_parity")
        **kwargs: Additional parameters for optimization
        
    Returns:
        dict: Optimal weights and portfolio metrics
    """
    try:
        num_assets = len(returns_df.columns)
        
        if method == "equal_weight":
            weights = {col: 1.0/num_assets for col in returns_df.columns}
            
        elif method == "min_variance":
            weights = calculate_min_variance_weights(returns_df)
            
        elif method == "max_sharpe":
            weights = calculate_max_sharpe_weights(returns_df, kwargs.get("risk_free_rate", 0.02))
            
        elif method == "risk_parity":
            weights = calculate_risk_parity_weights(returns_df)
            
        else:
            weights = {col: 1.0/num_assets for col in returns_df.columns}
        
        # Calculate portfolio metrics with optimized weights
        portfolio_returns = calculate_weighted_returns(returns_df, weights)
        portfolio_metrics = calculate_portfolio_risk_metrics(portfolio_returns)
        
        return {
            "optimal_weights": weights,
            "optimization_method": method,
            "portfolio_metrics": portfolio_metrics,
            "weight_constraints_satisfied": validate_weight_constraints(weights, kwargs)
        }
        
    except Exception as e:
        logger.error(f"Portfolio optimization failed: {str(e)}")
        return {"optimal_weights": {}, "error": str(e)}

def calculate_min_variance_weights(returns_df: pd.DataFrame) -> Dict[str, float]:
    """Calculate minimum variance portfolio weights."""
    try:
        # Use Ledoit-Wolf shrinkage estimator for covariance
        lw = LedoitWolf()
        cov_matrix = lw.fit(returns_df.fillna(0)).covariance_
        
        # Calculate minimum variance weights: w = inv(Σ)1 / 1'inv(Σ)1
        inv_cov = np.linalg.pinv(cov_matrix)
        ones = np.ones((len(returns_df.columns), 1))
        
        weights_array = inv_cov @ ones
        weights_array = weights_array / weights_array.sum()
        
        return {col: float(weights_array[i, 0]) for i, col in enumerate(returns_df.columns)}
        
    except Exception as e:
        logger.warning(f"Min variance calculation failed: {str(e)}")
        # Fallback to equal weights
        num_assets = len(returns_df.columns)
        return {col: 1.0/num_assets for col in returns_df.columns}

def calculate_max_sharpe_weights(returns_df: pd.DataFrame, risk_free_rate: float = 0.02) -> Dict[str, float]:
    """Calculate maximum Sharpe ratio portfolio weights (simplified)."""
    try:
        # Simplified approach using mean returns and covariance
        mean_returns = returns_df.mean() * 252  # Annualized
        cov_matrix = returns_df.cov() * 252  # Annualized
        
        # Excess returns
        excess_returns = mean_returns - risk_free_rate
        
        # Simplified optimization (not exact but reasonable approximation)
        inv_cov = np.linalg.pinv(cov_matrix.values)
        weights_array = inv_cov @ excess_returns.values
        weights_array = weights_array / weights_array.sum()
        
        # Ensure no negative weights (long-only constraint)
        weights_array = np.maximum(weights_array, 0)
        weights_array = weights_array / weights_array.sum()
        
        return {col: float(weights_array[i]) for i, col in enumerate(returns_df.columns)}
        
    except Exception as e:
        logger.warning(f"Max Sharpe calculation failed: {str(e)}")
        # Fallback to equal weights
        num_assets = len(returns_df.columns)
        return {col: 1.0/num_assets for col in returns_df.columns}

def calculate_risk_parity_weights(returns_df: pd.DataFrame) -> Dict[str, float]:
    """Calculate risk parity portfolio weights (equal risk contribution)."""
    try:
        # Simplified risk parity: inverse volatility weighting
        volatilities = returns_df.std()
        inv_vol = 1 / volatilities
        weights_array = inv_vol / inv_vol.sum()
        
        return {col: float(weights_array[col]) for col in returns_df.columns}
        
    except Exception as e:
        logger.warning(f"Risk parity calculation failed: {str(e)}")
        # Fallback to equal weights
        num_assets = len(returns_df.columns)
        return {col: 1.0/num_assets for col in returns_df.columns}

def calculate_weighted_returns(returns_df: pd.DataFrame, weights: Dict[str, float]) -> pd.Series:
    """Calculate portfolio returns given weights."""
    try:
        portfolio_returns = pd.Series(0.0, index=returns_df.index)
        
        for asset, weight in weights.items():
            if asset in returns_df.columns:
                portfolio_returns += weight * returns_df[asset]
        
        return portfolio_returns
        
    except Exception as e:
        logger.error(f"Weighted returns calculation failed: {str(e)}")
        return pd.Series(0.0, index=returns_df.index)

def validate_weight_constraints(weights: Dict[str, float], constraints: Dict) -> bool:
    """Validate that weights satisfy constraints."""
    try:
        # Check sum to 1
        total_weight = sum(weights.values())
        if abs(total_weight - 1.0) > 0.001:
            return False
        
        # Check individual weight limits
        max_weight = constraints.get("max_weight", 1.0)
        min_weight = constraints.get("min_weight", 0.0)
        
        for weight in weights.values():
            if weight > max_weight or weight < min_weight:
                return False
        
        return True
        
    except:
        return False

def calculate_rebalancing_metrics(original_weights: Dict[str, float], 
                                current_weights: Dict[str, float],
                                price_changes: Dict[str, float]) -> Dict:
    """
    Calculate portfolio drift and rebalancing metrics.
    
    Args:
        original_weights: Target portfolio weights
        current_weights: Current portfolio weights after price changes
        price_changes: Percentage price changes by asset
        
    Returns:
        dict: Rebalancing analysis
    """
    try:
        # Calculate weight drift
        weight_drifts = {}
        total_drift = 0
        
        for asset in original_weights:
            original = original_weights.get(asset, 0)
            current = current_weights.get(asset, 0)
            drift = current - original
            weight_drifts[asset] = {
                "original_weight": float(original),
                "current_weight": float(current),
                "drift": float(drift),
                "drift_percent": float(drift / original * 100) if original != 0 else 0
            }
            total_drift += abs(drift)
        
        # Rebalancing requirements
        rebalancing_trades = {}
        for asset, drift_data in weight_drifts.items():
            trade_amount = -drift_data["drift"]  # Negative drift means need to buy
            rebalancing_trades[asset] = {
                "trade_weight": float(trade_amount),
                "action": "buy" if trade_amount > 0 else "sell" if trade_amount < 0 else "hold"
            }
        
        # Portfolio concentration change
        original_hhi = sum(w**2 for w in original_weights.values())
        current_hhi = sum(w**2 for w in current_weights.values())
        concentration_change = current_hhi - original_hhi
        
        return {
            "total_weight_drift": float(total_drift),
            "weight_drifts": weight_drifts,
            "rebalancing_trades": rebalancing_trades,
            "concentration_change": float(concentration_change),
            "rebalancing_urgency": classify_rebalancing_urgency(total_drift),
            "largest_drift_asset": max(weight_drifts.items(), key=lambda x: abs(x[1]["drift"]))[0] if weight_drifts else None
        }
        
    except Exception as e:
        logger.error(f"Rebalancing metrics calculation failed: {str(e)}")
        return {}

def classify_rebalancing_urgency(total_drift: float) -> str:
    """Classify urgency of rebalancing based on total drift."""
    if total_drift > 0.1:  # 10% total drift
        return "high"
    elif total_drift > 0.05:  # 5% total drift
        return "medium"
    elif total_drift > 0.02:  # 2% total drift
        return "low"
    else:
        return "none"