"""
Portfolio Analysis Functions

Portfolio-level analysis and optimization functions, matching the 
categorical structure from financial-analysis-function-library.json

From financial-analysis-function-library.json category: portfolio_analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
import warnings
warnings.filterwarnings('ignore')


def calculatePortfolioMetrics(
    weights: Union[List[float], Dict[str, float]],
    returns: Union[pd.DataFrame, Dict[str, pd.Series]]
) -> Dict[str, Any]:
    """
    Calculate comprehensive portfolio metrics.
    
    From financial-analysis-function-library.json
    
    Args:
        weights: Portfolio weights as list or dict {asset: weight}
        returns: Return series for each asset as DataFrame or dict
        
    Returns:
        {
            "portfolio_return": float,
            "portfolio_volatility": float,
            "sharpe_ratio": float,
            "diversification_ratio": float,
            "success": bool
        }
    """
    try:
        # Handle input formats
        if isinstance(weights, dict) and isinstance(returns, dict):
            # Ensure same assets
            common_assets = set(weights.keys()) & set(returns.keys())
            if len(common_assets) == 0:
                return {"success": False, "error": "No common assets found"}
            
            # Create aligned DataFrame
            weight_series = pd.Series({asset: weights[asset] for asset in common_assets})
            return_df = pd.DataFrame({asset: returns[asset] for asset in common_assets})
            
        elif isinstance(weights, list) and isinstance(returns, pd.DataFrame):
            if len(weights) != returns.shape[1]:
                return {"success": False, "error": "Number of weights must match number of assets"}
            
            weight_series = pd.Series(weights, index=returns.columns)
            return_df = returns
            
        elif isinstance(weights, list) and isinstance(returns, dict):
            assets = list(returns.keys())
            if len(weights) != len(assets):
                return {"success": False, "error": "Number of weights must match number of assets"}
            
            weight_series = pd.Series(weights, index=assets)
            return_df = pd.DataFrame(returns)
            
        else:
            return {"success": False, "error": "Invalid input format"}
        
        # Normalize weights
        weight_series = weight_series / weight_series.sum()
        
        # Align data and remove NaN
        return_df = return_df.dropna()
        
        if len(return_df) < 10:
            return {"success": False, "error": "Need at least 10 observations"}
        
        # Calculate portfolio returns
        portfolio_returns = (return_df * weight_series).sum(axis=1)
        
        # Portfolio metrics
        portfolio_return = portfolio_returns.mean() * 252  # Annualized
        portfolio_volatility = portfolio_returns.std() * np.sqrt(252)  # Annualized
        
        # Sharpe ratio
        risk_free_rate = 0.02
        sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0
        
        # Individual asset metrics
        asset_returns = return_df.mean() * 252
        asset_volatilities = return_df.std() * np.sqrt(252)
        
        # Diversification ratio = Weighted average volatility / Portfolio volatility
        weighted_avg_volatility = (weight_series * asset_volatilities).sum()
        diversification_ratio = weighted_avg_volatility / portfolio_volatility if portfolio_volatility > 0 else 1
        
        # Correlation matrix
        correlation_matrix = return_df.corr()
        avg_correlation = correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].mean()
        
        # Maximum drawdown
        cumulative = (1 + portfolio_returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        return {
            "success": True,
            "portfolio_return": float(portfolio_return),
            "portfolio_return_pct": f"{portfolio_return * 100:.2f}%",
            "portfolio_volatility": float(portfolio_volatility),
            "portfolio_volatility_pct": f"{portfolio_volatility * 100:.2f}%",
            "sharpe_ratio": float(sharpe_ratio),
            "diversification_ratio": float(diversification_ratio),
            "max_drawdown": float(max_drawdown),
            "max_drawdown_pct": f"{max_drawdown * 100:.2f}%",
            "avg_correlation": float(avg_correlation),
            "num_assets": len(weight_series),
            "num_observations": len(return_df),
            "weights": weight_series.to_dict(),
            "asset_returns": asset_returns.to_dict(),
            "asset_volatilities": asset_volatilities.to_dict()
        }
        
    except Exception as e:
        return {"success": False, "error": f"Portfolio metrics calculation failed: {str(e)}"}


def analyzePortfolioConcentration(
    weights: Union[List[float], Dict[str, float], pd.Series]
) -> Dict[str, Any]:
    """
    Analyze portfolio concentration and diversification.
    
    From financial-analysis-function-library.json
    
    Args:
        weights: Portfolio weights
        
    Returns:
        {
            "herfindahl_index": float,
            "effective_number_assets": float,
            "concentration_level": str,
            "top_holdings": Dict,
            "success": bool
        }
    """
    try:
        # Handle input formats
        if isinstance(weights, dict):
            weight_series = pd.Series(weights)
        elif isinstance(weights, list):
            weight_series = pd.Series(weights, index=[f"Asset_{i+1}" for i in range(len(weights))])
        elif isinstance(weights, pd.Series):
            weight_series = weights
        else:
            return {"success": False, "error": "Invalid weights format"}
        
        # Remove zero weights and normalize
        weight_series = weight_series[weight_series > 0]
        weight_series = weight_series / weight_series.sum()
        
        if len(weight_series) == 0:
            return {"success": False, "error": "No positive weights found"}
        
        # Calculate Herfindahl Index (sum of squared weights)
        herfindahl_index = (weight_series ** 2).sum()
        
        # Effective number of assets (1/HHI)
        effective_number = 1 / herfindahl_index
        
        # Concentration level classification
        if herfindahl_index > 0.25:
            concentration_level = "Highly Concentrated"
        elif herfindahl_index > 0.15:
            concentration_level = "Moderately Concentrated"
        elif herfindahl_index > 0.10:
            concentration_level = "Somewhat Concentrated"
        else:
            concentration_level = "Well Diversified"
        
        # Top holdings analysis
        sorted_weights = weight_series.sort_values(ascending=False)
        
        top_holdings = {
            "largest_holding": {
                "asset": sorted_weights.index[0],
                "weight": float(sorted_weights.iloc[0]),
                "weight_pct": f"{sorted_weights.iloc[0] * 100:.2f}%"
            },
            "top_3_concentration": float(sorted_weights.head(3).sum()),
            "top_5_concentration": float(sorted_weights.head(5).sum()),
            "top_10_concentration": float(sorted_weights.head(min(10, len(sorted_weights))).sum())
        }
        
        # Gini coefficient (inequality measure)
        n = len(weight_series)
        sorted_weights_array = sorted_weights.values
        index = np.arange(1, n + 1)
        gini = ((2 * index - n - 1) * sorted_weights_array).sum() / (n * sorted_weights_array.sum())
        
        return {
            "success": True,
            "herfindahl_index": float(herfindahl_index),
            "effective_number_assets": float(effective_number),
            "concentration_level": concentration_level,
            "gini_coefficient": float(gini),
            "top_holdings": top_holdings,
            "num_assets": len(weight_series),
            "all_weights": sorted_weights.to_dict()
        }
        
    except Exception as e:
        return {"success": False, "error": f"Portfolio concentration analysis failed: {str(e)}"}


def calculatePortfolioBeta(
    weights: Union[List[float], Dict[str, float]],
    betas: Union[List[float], Dict[str, float]]
) -> Dict[str, Any]:
    """
    Calculate portfolio beta.
    
    From financial-analysis-function-library.json
    
    Args:
        weights: Portfolio weights
        betas: Individual asset betas
        
    Returns:
        {
            "portfolio_beta": float,
            "weighted_betas": Dict,
            "beta_contribution": Dict,
            "success": bool
        }
    """
    try:
        # Handle input formats
        if isinstance(weights, dict) and isinstance(betas, dict):
            # Ensure same assets
            common_assets = set(weights.keys()) & set(betas.keys())
            if len(common_assets) == 0:
                return {"success": False, "error": "No common assets found"}
            
            weight_series = pd.Series({asset: weights[asset] for asset in common_assets})
            beta_series = pd.Series({asset: betas[asset] for asset in common_assets})
            
        elif isinstance(weights, list) and isinstance(betas, list):
            if len(weights) != len(betas):
                return {"success": False, "error": "Number of weights must match number of betas"}
            
            assets = [f"Asset_{i+1}" for i in range(len(weights))]
            weight_series = pd.Series(weights, index=assets)
            beta_series = pd.Series(betas, index=assets)
            
        else:
            return {"success": False, "error": "Invalid input format"}
        
        # Normalize weights
        weight_series = weight_series / weight_series.sum()
        
        # Calculate portfolio beta (weighted average of individual betas)
        portfolio_beta = (weight_series * beta_series).sum()
        
        # Calculate beta contributions
        beta_contributions = weight_series * beta_series
        
        # Beta risk decomposition
        total_beta_risk = abs(beta_contributions).sum()
        relative_contributions = (abs(beta_contributions) / total_beta_risk) * 100
        
        return {
            "success": True,
            "portfolio_beta": float(portfolio_beta),
            "weighted_betas": beta_contributions.to_dict(),
            "beta_contribution_pct": relative_contributions.to_dict(),
            "market_sensitivity": "High" if abs(portfolio_beta) > 1.2 else "Medium" if abs(portfolio_beta) > 0.8 else "Low",
            "beta_direction": "Positive" if portfolio_beta > 0 else "Negative",
            "num_assets": len(weight_series)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Portfolio beta calculation failed: {str(e)}"}


def calculateActiveShare(
    portfolio_weights: Union[List[float], Dict[str, float]],
    benchmark_weights: Union[List[float], Dict[str, float]]
) -> Dict[str, Any]:
    """
    Calculate active share vs benchmark.
    
    From financial-analysis-function-library.json
    
    Args:
        portfolio_weights: Portfolio weights
        benchmark_weights: Benchmark weights
        
    Returns:
        {
            "active_share": float,
            "active_positions": Dict,
            "tracking_difference": Dict,
            "success": bool
        }
    """
    try:
        # Handle input formats
        if isinstance(portfolio_weights, dict) and isinstance(benchmark_weights, dict):
            # Get all assets (union of both)
            all_assets = set(portfolio_weights.keys()) | set(benchmark_weights.keys())
            
            port_series = pd.Series({asset: portfolio_weights.get(asset, 0) for asset in all_assets})
            bench_series = pd.Series({asset: benchmark_weights.get(asset, 0) for asset in all_assets})
            
        elif isinstance(portfolio_weights, list) and isinstance(benchmark_weights, list):
            max_len = max(len(portfolio_weights), len(benchmark_weights))
            
            # Pad shorter list with zeros
            port_weights = portfolio_weights + [0] * (max_len - len(portfolio_weights))
            bench_weights = benchmark_weights + [0] * (max_len - len(benchmark_weights))
            
            assets = [f"Asset_{i+1}" for i in range(max_len)]
            port_series = pd.Series(port_weights, index=assets)
            bench_series = pd.Series(bench_weights, index=assets)
            
        else:
            return {"success": False, "error": "Invalid input format"}
        
        # Normalize weights
        if port_series.sum() > 0:
            port_series = port_series / port_series.sum()
        if bench_series.sum() > 0:
            bench_series = bench_series / bench_series.sum()
        
        # Calculate active weights (portfolio - benchmark)
        active_weights = port_series - bench_series
        
        # Active Share = 0.5 * sum(|active weights|)
        active_share = 0.5 * abs(active_weights).sum()
        
        # Identify overweight and underweight positions
        overweight = active_weights[active_weights > 0.001]  # Threshold for meaningful differences
        underweight = active_weights[active_weights < -0.001]
        
        active_positions = {
            "overweight_positions": overweight.to_dict(),
            "underweight_positions": underweight.to_dict(),
            "num_overweight": len(overweight),
            "num_underweight": len(underweight),
            "largest_overweight": {
                "asset": overweight.idxmax() if len(overweight) > 0 else None,
                "weight_diff": float(overweight.max()) if len(overweight) > 0 else 0
            },
            "largest_underweight": {
                "asset": underweight.idxmin() if len(underweight) > 0 else None,
                "weight_diff": float(underweight.min()) if len(underweight) > 0 else 0
            }
        }
        
        # Active share interpretation
        if active_share > 0.80:
            interpretation = "Very High Active Share - Significantly different from benchmark"
        elif active_share > 0.60:
            interpretation = "High Active Share - Notably different from benchmark"
        elif active_share > 0.40:
            interpretation = "Moderate Active Share - Some differences from benchmark"
        elif active_share > 0.20:
            interpretation = "Low Active Share - Similar to benchmark"
        else:
            interpretation = "Very Low Active Share - Close to index tracking"
        
        return {
            "success": True,
            "active_share": float(active_share),
            "active_share_pct": f"{active_share * 100:.2f}%",
            "interpretation": interpretation,
            "active_positions": active_positions,
            "all_active_weights": active_weights.to_dict(),
            "num_assets": len(port_series)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Active share calculation failed: {str(e)}"}


# Registry for MCP server
PORTFOLIO_ANALYSIS_FUNCTIONS = {
    'calculatePortfolioMetrics': calculatePortfolioMetrics,
    'analyzePortfolioConcentration': analyzePortfolioConcentration,
    'calculatePortfolioBeta': calculatePortfolioBeta,
    'calculateActiveShare': calculateActiveShare
}