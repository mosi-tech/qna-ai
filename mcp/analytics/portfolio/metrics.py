"""
Portfolio Analysis Metrics using libraries

Portfolio analysis functions from financial-analysis-function-library.json portfolio_analysis category.
Uses empyrical, numpy, scipy for proven calculations - no code duplication.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Union, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Use libraries from requirements.txt - no manual calculations
import empyrical
from scipy import stats
import scipy.optimize as sco

from ..utils.data_utils import validate_return_data, validate_price_data, standardize_output
from ..performance.metrics import calculate_returns_metrics, calculate_risk_metrics


def calculate_portfolio_metrics(weights: Union[pd.Series, Dict[str, Any], List[float]], 
                               returns: Union[pd.DataFrame, Dict[str, Any]],
                               benchmark_returns: Optional[Union[pd.Series, Dict[str, Any]]] = None,
                               risk_free_rate: float = 0.02) -> Dict[str, Any]:
    """
    Calculate comprehensive portfolio metrics using empyrical and scipy.
    
    From financial-analysis-function-library.json portfolio_analysis category
    Uses empyrical library for all performance metrics - no code duplication
    
    Args:
        weights: Portfolio weights
        returns: Asset returns matrix
        benchmark_returns: Benchmark returns for comparison
        risk_free_rate: Risk-free rate for calculations
        
    Returns:
        Dict: Comprehensive portfolio metrics
    """
    try:
        # Validate and convert inputs
        if isinstance(weights, dict):
            weights = pd.Series(weights)
        elif isinstance(weights, list):
            weights = pd.Series(weights)
        
        if isinstance(returns, dict):
            returns_df = pd.DataFrame(returns)
        else:
            returns_df = returns.copy()
        
        # Ensure weights are normalized
        weights = weights / weights.sum()
        
        # Calculate portfolio returns
        portfolio_returns = returns_df.dot(weights)
        
        # Basic portfolio metrics using empyrical
        total_return = empyrical.cum_returns_final(portfolio_returns)
        annual_return = empyrical.annual_return(portfolio_returns)
        annual_volatility = empyrical.annual_volatility(portfolio_returns)
        sharpe_ratio = empyrical.sharpe_ratio(portfolio_returns, risk_free=risk_free_rate)
        sortino_ratio = empyrical.sortino_ratio(portfolio_returns, required_return=risk_free_rate)
        max_drawdown = empyrical.max_drawdown(portfolio_returns)
        calmar_ratio = empyrical.calmar_ratio(portfolio_returns)
        
        # VaR and CVaR using empyrical
        var_95 = empyrical.value_at_risk(portfolio_returns, cutoff=0.05)
        cvar_95 = empyrical.conditional_value_at_risk(portfolio_returns, cutoff=0.05)
        
        # Rolling metrics
        rolling_sharpe = empyrical.rolling_sharpe(portfolio_returns, rolling_window=252)
        rolling_volatility = empyrical.rolling_volatility(portfolio_returns, rolling_window=252)
        
        # Portfolio composition analysis
        effective_n_assets = 1 / np.sum(weights ** 2)  # Effective number of assets
        concentration_ratio = np.sum(np.sort(weights)[-5:])  # Top 5 concentration
        
        # Diversification metrics
        portfolio_variance = np.dot(weights, np.dot(returns_df.cov() * 252, weights))
        weighted_avg_variance = np.sum(weights ** 2 * np.diag(returns_df.cov() * 252))
        diversification_ratio = np.sqrt(weighted_avg_variance / portfolio_variance) if portfolio_variance > 0 else 1
        
        result = {
            "portfolio_composition": {
                "number_of_assets": len(weights),
                "effective_number_of_assets": float(effective_n_assets),
                "largest_weight": float(weights.max()),
                "smallest_weight": float(weights.min()),
                "weight_concentration": float(concentration_ratio),
                "diversification_ratio": float(diversification_ratio)
            },
            "return_metrics": {
                "total_return": float(total_return),
                "total_return_pct": f"{total_return * 100:.2f}%",
                "annual_return": float(annual_return),
                "annual_return_pct": f"{annual_return * 100:.2f}%",
                "excess_return": float(annual_return - risk_free_rate),
                "excess_return_pct": f"{(annual_return - risk_free_rate) * 100:.2f}%"
            },
            "risk_metrics": {
                "annual_volatility": float(annual_volatility),
                "annual_volatility_pct": f"{annual_volatility * 100:.2f}%",
                "max_drawdown": float(max_drawdown),
                "max_drawdown_pct": f"{max_drawdown * 100:.2f}%",
                "var_95_daily": float(var_95),
                "var_95_daily_pct": f"{var_95 * 100:.2f}%",
                "cvar_95_daily": float(cvar_95),
                "cvar_95_daily_pct": f"{cvar_95 * 100:.2f}%",
                "var_95_annual": float(var_95 * np.sqrt(252)),
                "cvar_95_annual": float(cvar_95 * np.sqrt(252))
            },
            "risk_adjusted_metrics": {
                "sharpe_ratio": float(sharpe_ratio),
                "sortino_ratio": float(sortino_ratio),
                "calmar_ratio": float(calmar_ratio),
                "return_vol_ratio": float(annual_return / annual_volatility) if annual_volatility > 0 else 0
            },
            "rolling_metrics": {
                "avg_rolling_sharpe": float(rolling_sharpe.mean()),
                "volatility_of_sharpe": float(rolling_sharpe.std()),
                "avg_rolling_volatility": float(rolling_volatility.mean()),
                "volatility_stability": float(1 - rolling_volatility.std() / rolling_volatility.mean()) if rolling_volatility.mean() > 0 else 0
            }
        }
        
        # Add benchmark comparison if provided
        if benchmark_returns is not None:
            benchmark_series = validate_return_data(benchmark_returns)
            
            # Align portfolio and benchmark returns
            aligned_portfolio, aligned_benchmark = portfolio_returns.align(benchmark_series, join='inner')
            
            if len(aligned_portfolio) > 0:
                # Calculate tracking metrics using empyrical
                tracking_error = empyrical.down_stdev(aligned_portfolio - aligned_benchmark)
                information_ratio = (aligned_portfolio.mean() - aligned_benchmark.mean()) / tracking_error if tracking_error > 0 else 0
                
                # Beta and alpha using empyrical
                beta = empyrical.beta(aligned_portfolio, aligned_benchmark)
                alpha = empyrical.alpha(aligned_portfolio, aligned_benchmark, risk_free=risk_free_rate)
                
                # Up/down capture ratios
                up_capture = empyrical.capture_ratio(aligned_portfolio, aligned_benchmark, period='up')
                down_capture = empyrical.capture_ratio(aligned_portfolio, aligned_benchmark, period='down')
                
                result["benchmark_comparison"] = {
                    "beta": float(beta),
                    "alpha": float(alpha),
                    "alpha_pct": f"{alpha * 100:.2f}%",
                    "tracking_error": float(tracking_error),
                    "tracking_error_pct": f"{tracking_error * 100:.2f}%",
                    "information_ratio": float(information_ratio),
                    "up_capture_ratio": float(up_capture),
                    "down_capture_ratio": float(down_capture),
                    "correlation": float(aligned_portfolio.corr(aligned_benchmark))
                }
        
        return standardize_output(result, "calculate_portfolio_metrics")
        
    except Exception as e:
        return {"success": False, "error": f"Portfolio metrics calculation failed: {str(e)}"}


def analyze_portfolio_concentration(weights: Union[pd.Series, Dict[str, Any], List[float]],
                                   asset_names: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Analyze portfolio concentration and diversification using numpy and scipy.
    
    From financial-analysis-function-library.json portfolio_analysis category
    Uses established concentration measures - no code duplication
    
    Args:
        weights: Portfolio weights
        asset_names: Asset names for detailed analysis
        
    Returns:
        Dict: Concentration analysis results
    """
    try:
        # Validate and convert inputs
        if isinstance(weights, dict):
            weights = pd.Series(weights)
            if asset_names is None:
                asset_names = list(weights.index)
        elif isinstance(weights, list):
            weights = pd.Series(weights)
            if asset_names is None:
                asset_names = [f"Asset_{i+1}" for i in range(len(weights))]
        
        # Ensure weights are normalized and positive
        weights = weights / weights.sum()
        weights = weights.abs()  # Handle any negative weights
        
        # Sort weights for analysis
        sorted_weights = weights.sort_values(ascending=False)
        
        # Herfindahl-Hirschman Index (HHI)
        hhi = np.sum(weights ** 2)
        
        # Effective number of assets
        effective_n = 1 / hhi
        
        # Concentration ratios
        cr_1 = sorted_weights.iloc[0] if len(sorted_weights) > 0 else 0
        cr_3 = sorted_weights.iloc[:3].sum() if len(sorted_weights) >= 3 else sorted_weights.sum()
        cr_5 = sorted_weights.iloc[:5].sum() if len(sorted_weights) >= 5 else sorted_weights.sum()
        cr_10 = sorted_weights.iloc[:10].sum() if len(sorted_weights) >= 10 else sorted_weights.sum()
        
        # Diversification measures
        max_weight = weights.max()
        min_weight = weights.min()
        weight_variance = weights.var()
        weight_entropy = -np.sum(weights * np.log(weights + 1e-10))  # Add small value to avoid log(0)
        
        # Gini coefficient for inequality
        sorted_weights_array = np.sort(weights.values)
        n = len(sorted_weights_array)
        gini = (2 * np.sum((np.arange(1, n + 1) * sorted_weights_array))) / (n * np.sum(sorted_weights_array)) - (n + 1) / n
        
        # Risk concentration (if all weights were equal)
        equal_weight = 1 / len(weights)
        concentration_deviation = np.sum(np.abs(weights - equal_weight))
        
        # Identify outliers (weights significantly different from average)
        mean_weight = weights.mean()
        std_weight = weights.std()
        outlier_threshold = mean_weight + 2 * std_weight
        outliers = weights[weights > outlier_threshold]
        
        # Classification based on concentration
        if hhi > 0.25:
            concentration_level = "highly_concentrated"
        elif hhi > 0.15:
            concentration_level = "moderately_concentrated"
        elif hhi > 0.10:
            concentration_level = "somewhat_concentrated"
        else:
            concentration_level = "well_diversified"
        
        result = {
            "concentration_indices": {
                "herfindahl_hirschman_index": float(hhi),
                "effective_number_of_assets": float(effective_n),
                "gini_coefficient": float(gini),
                "concentration_level": concentration_level
            },
            "concentration_ratios": {
                "top_1_holding": float(cr_1),
                "top_1_holding_pct": f"{cr_1 * 100:.2f}%",
                "top_3_holdings": float(cr_3),
                "top_3_holdings_pct": f"{cr_3 * 100:.2f}%",
                "top_5_holdings": float(cr_5),
                "top_5_holdings_pct": f"{cr_5 * 100:.2f}%",
                "top_10_holdings": float(cr_10),
                "top_10_holdings_pct": f"{cr_10 * 100:.2f}%"
            },
            "diversification_metrics": {
                "weight_entropy": float(weight_entropy),
                "weight_variance": float(weight_variance),
                "concentration_deviation": float(concentration_deviation),
                "max_weight": float(max_weight),
                "max_weight_pct": f"{max_weight * 100:.2f}%",
                "min_weight": float(min_weight),
                "min_weight_pct": f"{min_weight * 100:.2f}%"
            },
            "top_holdings": [
                {
                    "asset": asset_names[sorted_weights.index[i]] if i < len(asset_names) else f"Asset_{sorted_weights.index[i]}",
                    "weight": float(sorted_weights.iloc[i]),
                    "weight_pct": f"{sorted_weights.iloc[i] * 100:.2f}%",
                    "rank": i + 1
                }
                for i in range(min(10, len(sorted_weights)))
            ],
            "concentration_outliers": [
                {
                    "asset": asset_names[idx] if idx < len(asset_names) else f"Asset_{idx}",
                    "weight": float(weight),
                    "weight_pct": f"{weight * 100:.2f}%",
                    "deviation_from_mean": float(weight - mean_weight)
                }
                for idx, weight in outliers.items()
            ]
        }
        
        return standardize_output(result, "analyze_portfolio_concentration")
        
    except Exception as e:
        return {"success": False, "error": f"Portfolio concentration analysis failed: {str(e)}"}


def calculate_portfolio_beta(weights: Union[pd.Series, Dict[str, Any], List[float]],
                           asset_betas: Union[pd.Series, Dict[str, Any], List[float]]) -> Dict[str, Any]:
    """
    Calculate portfolio beta using weights and individual asset betas.
    
    From financial-analysis-function-library.json portfolio_analysis category
    Simple weighted average calculation - no code duplication
    
    Args:
        weights: Portfolio weights
        asset_betas: Individual asset betas
        
    Returns:
        Dict: Portfolio beta calculation results
    """
    try:
        # Validate and convert inputs
        if isinstance(weights, dict):
            weights = pd.Series(weights)
        elif isinstance(weights, list):
            weights = pd.Series(weights)
        
        if isinstance(asset_betas, dict):
            betas = pd.Series(asset_betas)
        elif isinstance(asset_betas, list):
            betas = pd.Series(asset_betas)
        else:
            betas = asset_betas.copy()
        
        # Ensure same length
        if len(weights) != len(betas):
            raise ValueError(f"Weights length ({len(weights)}) must match betas length ({len(betas)})")
        
        # Normalize weights
        weights = weights / weights.sum()
        
        # Calculate portfolio beta as weighted average
        portfolio_beta = np.sum(weights * betas)
        
        # Beta interpretation
        if portfolio_beta > 1.2:
            beta_interpretation = "high_beta"
            risk_profile = "aggressive"
        elif portfolio_beta > 0.8:
            beta_interpretation = "moderate_beta"
            risk_profile = "balanced"
        elif portfolio_beta > 0:
            beta_interpretation = "low_beta"
            risk_profile = "conservative"
        else:
            beta_interpretation = "negative_beta"
            risk_profile = "hedge"
        
        # Component contributions to portfolio beta
        beta_contributions = weights * betas
        
        # Sort by contribution
        sorted_contributions = beta_contributions.sort_values(ascending=False)
        
        result = {
            "portfolio_beta": float(portfolio_beta),
            "beta_interpretation": beta_interpretation,
            "risk_profile": risk_profile,
            "beta_statistics": {
                "weighted_average_beta": float(portfolio_beta),
                "max_individual_beta": float(betas.max()),
                "min_individual_beta": float(betas.min()),
                "beta_range": float(betas.max() - betas.min()),
                "beta_std_dev": float(betas.std())
            },
            "top_beta_contributors": [
                {
                    "asset_index": int(idx),
                    "weight": float(weights.iloc[idx]),
                    "weight_pct": f"{weights.iloc[idx] * 100:.2f}%",
                    "asset_beta": float(betas.iloc[idx]),
                    "beta_contribution": float(contribution),
                    "contribution_pct": f"{contribution / portfolio_beta * 100:.2f}%" if portfolio_beta != 0 else "0.00%"
                }
                for idx, contribution in enumerate(sorted_contributions.iloc[:5])
            ],
            "portfolio_characteristics": {
                "market_sensitivity": "high" if abs(portfolio_beta) > 1.0 else "low",
                "expected_volatility_vs_market": f"{portfolio_beta:.2f}x",
                "defensive_properties": portfolio_beta < 0.8,
                "aggressive_properties": portfolio_beta > 1.2
            }
        }
        
        return standardize_output(result, "calculate_portfolio_beta")
        
    except Exception as e:
        return {"success": False, "error": f"Portfolio beta calculation failed: {str(e)}"}


def analyze_portfolio_turnover(weights_history: Union[pd.DataFrame, Dict[str, Any]],
                              timeframes: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Analyze portfolio turnover metrics using pandas and numpy.
    
    From financial-analysis-function-library.json portfolio_analysis category
    Uses pandas for time series analysis - no code duplication
    
    Args:
        weights_history: Historical portfolio weights over time
        timeframes: Specific timeframes to analyze
        
    Returns:
        Dict: Portfolio turnover analysis
    """
    try:
        # Validate and convert inputs
        if isinstance(weights_history, dict):
            weights_df = pd.DataFrame(weights_history)
        else:
            weights_df = weights_history.copy()
        
        # Ensure datetime index
        if not isinstance(weights_df.index, pd.DatetimeIndex):
            weights_df.index = pd.to_datetime(weights_df.index)
        
        # Sort by date
        weights_df = weights_df.sort_index()
        
        # Calculate period-over-period changes
        weight_changes = weights_df.diff().fillna(0)
        
        # Calculate turnover for each period (sum of absolute changes / 2)
        period_turnover = weight_changes.abs().sum(axis=1) / 2
        
        # Remove first period (no previous period to compare)
        period_turnover = period_turnover.iloc[1:]
        
        if len(period_turnover) == 0:
            raise ValueError("Need at least 2 time periods to calculate turnover")
        
        # Calculate various turnover metrics
        avg_turnover = period_turnover.mean()
        median_turnover = period_turnover.median()
        max_turnover = period_turnover.max()
        min_turnover = period_turnover.min()
        turnover_volatility = period_turnover.std()
        
        # Annualized turnover (assuming periods are reasonably frequent)
        # Estimate periods per year based on frequency
        time_diffs = weights_df.index.to_series().diff().dropna()
        avg_period_days = time_diffs.dt.days.mean()
        
        if avg_period_days > 0:
            periods_per_year = 365 / avg_period_days
            annualized_turnover = avg_turnover * periods_per_year
        else:
            annualized_turnover = avg_turnover * 12  # Assume monthly if can't determine
        
        # Identify high turnover periods
        high_turnover_threshold = avg_turnover + turnover_volatility
        high_turnover_periods = period_turnover[period_turnover > high_turnover_threshold]
        
        # Calculate cumulative turnover
        cumulative_turnover = period_turnover.cumsum()
        
        # Asset-level turnover analysis
        asset_turnover = weight_changes.abs().mean()
        most_volatile_assets = asset_turnover.sort_values(ascending=False)
        
        # Stability metrics
        weight_stability = 1 - weight_changes.abs().mean().mean()  # Average stability across assets
        portfolio_drift = weights_df.std(axis=0).mean()  # Average weight volatility
        
        result = {
            "turnover_summary": {
                "average_turnover": float(avg_turnover),
                "average_turnover_pct": f"{avg_turnover * 100:.2f}%",
                "median_turnover": float(median_turnover),
                "median_turnover_pct": f"{median_turnover * 100:.2f}%",
                "annualized_turnover": float(annualized_turnover),
                "annualized_turnover_pct": f"{annualized_turnover * 100:.2f}%",
                "turnover_volatility": float(turnover_volatility),
                "turnover_volatility_pct": f"{turnover_volatility * 100:.2f}%"
            },
            "turnover_distribution": {
                "max_turnover": float(max_turnover),
                "max_turnover_pct": f"{max_turnover * 100:.2f}%",
                "min_turnover": float(min_turnover),
                "min_turnover_pct": f"{min_turnover * 100:.2f}%",
                "75th_percentile": float(period_turnover.quantile(0.75)),
                "25th_percentile": float(period_turnover.quantile(0.25)),
                "high_turnover_periods": len(high_turnover_periods),
                "stability_score": float(weight_stability)
            },
            "asset_level_analysis": {
                "most_volatile_assets": [
                    {
                        "asset": str(asset),
                        "avg_weight_change": float(turnover),
                        "avg_weight_change_pct": f"{turnover * 100:.2f}%"
                    }
                    for asset, turnover in most_volatile_assets.head(5).items()
                ],
                "portfolio_drift": float(portfolio_drift),
                "overall_stability": float(1 - portfolio_drift)
            },
            "time_series_analysis": {
                "analysis_period": {
                    "start_date": str(weights_df.index.min().date()),
                    "end_date": str(weights_df.index.max().date()),
                    "total_periods": len(weights_df),
                    "avg_period_days": float(avg_period_days) if avg_period_days > 0 else None
                },
                "cumulative_turnover": float(cumulative_turnover.iloc[-1]),
                "cumulative_turnover_pct": f"{cumulative_turnover.iloc[-1] * 100:.2f}%",
                "turnover_trend": "increasing" if period_turnover.iloc[-1] > period_turnover.iloc[0] else "decreasing"
            }
        }
        
        return standardize_output(result, "analyze_portfolio_turnover")
        
    except Exception as e:
        return {"success": False, "error": f"Portfolio turnover analysis failed: {str(e)}"}


def calculate_active_share(portfolio_weights: Union[pd.Series, Dict[str, Any], List[float]],
                          benchmark_weights: Union[pd.Series, Dict[str, Any], List[float]],
                          asset_names: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Calculate active share vs benchmark using numpy.
    
    From financial-analysis-function-library.json portfolio_analysis category
    Simple mathematical calculation - no code duplication
    
    Args:
        portfolio_weights: Portfolio weights
        benchmark_weights: Benchmark weights
        asset_names: Asset names for detailed analysis
        
    Returns:
        Dict: Active share analysis results
    """
    try:
        # Validate and convert inputs
        if isinstance(portfolio_weights, dict):
            port_weights = pd.Series(portfolio_weights)
        elif isinstance(portfolio_weights, list):
            port_weights = pd.Series(portfolio_weights)
        else:
            port_weights = portfolio_weights.copy()
        
        if isinstance(benchmark_weights, dict):
            bench_weights = pd.Series(benchmark_weights)
        elif isinstance(benchmark_weights, list):
            bench_weights = pd.Series(benchmark_weights)
        else:
            bench_weights = benchmark_weights.copy()
        
        # Align the two series (handle different assets)
        port_weights, bench_weights = port_weights.align(bench_weights, fill_value=0)
        
        # Normalize weights
        port_weights = port_weights / port_weights.sum()
        bench_weights = bench_weights / bench_weights.sum()
        
        # Calculate active share
        weight_differences = port_weights - bench_weights
        active_share = np.sum(np.abs(weight_differences)) / 2
        
        # Calculate tracking error (standard deviation of weight differences)
        tracking_error = weight_differences.std()
        
        # Identify overweight and underweight positions
        overweight_positions = weight_differences[weight_differences > 0].sort_values(ascending=False)
        underweight_positions = weight_differences[weight_differences < 0].sort_values(ascending=True)
        
        # Portfolio vs benchmark composition
        assets_only_in_portfolio = port_weights[(port_weights > 0) & (bench_weights == 0)]
        assets_only_in_benchmark = bench_weights[(bench_weights > 0) & (port_weights == 0)]
        
        # Active share interpretation
        if active_share > 0.8:
            activity_level = "very_active"
        elif active_share > 0.6:
            activity_level = "active"
        elif active_share > 0.4:
            activity_level = "moderately_active"
        elif active_share > 0.2:
            activity_level = "somewhat_active"
        else:
            activity_level = "closet_indexer"
        
        # Calculate concentration of active bets
        active_bet_concentration = np.sum(np.sort(np.abs(weight_differences))[-5:])
        
        result = {
            "active_share_metrics": {
                "active_share": float(active_share),
                "active_share_pct": f"{active_share * 100:.2f}%",
                "activity_level": activity_level,
                "tracking_error": float(tracking_error),
                "tracking_error_pct": f"{tracking_error * 100:.2f}%",
                "active_bet_concentration": float(active_bet_concentration),
                "active_bet_concentration_pct": f"{active_bet_concentration * 100:.2f}%"
            },
            "position_analysis": {
                "total_positions": len(port_weights[port_weights > 0]),
                "benchmark_positions": len(bench_weights[bench_weights > 0]),
                "overweight_positions": len(overweight_positions),
                "underweight_positions": len(abs(underweight_positions)),
                "unique_portfolio_positions": len(assets_only_in_portfolio),
                "missed_benchmark_positions": len(assets_only_in_benchmark)
            },
            "largest_overweights": [
                {
                    "asset": asset_names[i] if asset_names and i < len(asset_names) else f"Asset_{overweight_positions.index[i]}",
                    "portfolio_weight": float(port_weights.iloc[overweight_positions.index[i]]),
                    "portfolio_weight_pct": f"{port_weights.iloc[overweight_positions.index[i]] * 100:.2f}%",
                    "benchmark_weight": float(bench_weights.iloc[overweight_positions.index[i]]),
                    "benchmark_weight_pct": f"{bench_weights.iloc[overweight_positions.index[i]] * 100:.2f}%",
                    "active_weight": float(overweight_positions.iloc[i]),
                    "active_weight_pct": f"{overweight_positions.iloc[i] * 100:.2f}%"
                }
                for i in range(min(5, len(overweight_positions)))
            ],
            "largest_underweights": [
                {
                    "asset": asset_names[i] if asset_names and i < len(asset_names) else f"Asset_{underweight_positions.index[i]}",
                    "portfolio_weight": float(port_weights.iloc[underweight_positions.index[i]]),
                    "portfolio_weight_pct": f"{port_weights.iloc[underweight_positions.index[i]] * 100:.2f}%",
                    "benchmark_weight": float(bench_weights.iloc[underweight_positions.index[i]]),
                    "benchmark_weight_pct": f"{bench_weights.iloc[underweight_positions.index[i]] * 100:.2f}%",
                    "active_weight": float(underweight_positions.iloc[i]),
                    "active_weight_pct": f"{underweight_positions.iloc[i] * 100:.2f}%"
                }
                for i in range(min(5, len(underweight_positions)))
            ]
        }
        
        return standardize_output(result, "calculate_active_share")
        
    except Exception as e:
        return {"success": False, "error": f"Active share calculation failed: {str(e)}"}


def perform_attribution(portfolio_returns: Union[pd.Series, Dict[str, Any]],
                       benchmark_returns: Union[pd.Series, Dict[str, Any]],
                       weights_history: Union[pd.DataFrame, Dict[str, Any]],
                       asset_returns: Optional[Union[pd.DataFrame, Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Perform return attribution analysis using pandas and numpy.
    
    From financial-analysis-function-library.json portfolio_analysis category
    Uses standard attribution methodology - no code duplication
    
    Args:
        portfolio_returns: Portfolio returns time series
        benchmark_returns: Benchmark returns time series
        weights_history: Historical portfolio weights
        asset_returns: Individual asset returns for detailed attribution
        
    Returns:
        Dict: Return attribution analysis results
    """
    try:
        # Validate and convert inputs
        port_returns = validate_return_data(portfolio_returns)
        bench_returns = validate_return_data(benchmark_returns)
        
        if isinstance(weights_history, dict):
            weights_df = pd.DataFrame(weights_history)
        else:
            weights_df = weights_history.copy()
        
        # Align time series
        port_returns, bench_returns = port_returns.align(bench_returns, join='inner')
        
        if len(port_returns) == 0:
            raise ValueError("No overlapping periods between portfolio and benchmark returns")
        
        # Calculate excess returns
        excess_returns = port_returns - bench_returns
        
        # Basic attribution metrics
        total_excess_return = excess_returns.sum()
        avg_excess_return = excess_returns.mean()
        excess_volatility = excess_returns.std()
        information_ratio = avg_excess_return / excess_volatility if excess_volatility > 0 else 0
        
        # Annualized metrics
        annualized_excess = avg_excess_return * 252
        annualized_excess_vol = excess_volatility * np.sqrt(252)
        annualized_ir = annualized_excess / annualized_excess_vol if annualized_excess_vol > 0 else 0
        
        # Hit rate (percentage of periods with positive excess returns)
        hit_rate = (excess_returns > 0).mean()
        
        # Win/loss analysis
        positive_excess = excess_returns[excess_returns > 0]
        negative_excess = excess_returns[excess_returns < 0]
        
        avg_win = positive_excess.mean() if len(positive_excess) > 0 else 0
        avg_loss = negative_excess.mean() if len(negative_excess) > 0 else 0
        win_loss_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
        
        # Tracking error and correlation
        tracking_error = excess_returns.std() * np.sqrt(252)
        correlation = port_returns.corr(bench_returns)
        
        result = {
            "attribution_summary": {
                "total_excess_return": float(total_excess_return),
                "total_excess_return_pct": f"{total_excess_return * 100:.2f}%",
                "average_excess_return": float(avg_excess_return),
                "average_excess_return_pct": f"{avg_excess_return * 100:.2f}%",
                "annualized_excess_return": float(annualized_excess),
                "annualized_excess_return_pct": f"{annualized_excess * 100:.2f}%"
            },
            "risk_metrics": {
                "tracking_error": float(tracking_error),
                "tracking_error_pct": f"{tracking_error * 100:.2f}%",
                "excess_volatility": float(excess_volatility),
                "excess_volatility_pct": f"{excess_volatility * 100:.2f}%",
                "information_ratio": float(information_ratio),
                "annualized_information_ratio": float(annualized_ir)
            },
            "performance_consistency": {
                "hit_rate": float(hit_rate),
                "hit_rate_pct": f"{hit_rate * 100:.2f}%",
                "correlation_with_benchmark": float(correlation),
                "periods_analyzed": len(excess_returns),
                "positive_periods": int((excess_returns > 0).sum()),
                "negative_periods": int((excess_returns < 0).sum())
            },
            "win_loss_analysis": {
                "average_win": float(avg_win),
                "average_win_pct": f"{avg_win * 100:.2f}%",
                "average_loss": float(avg_loss),
                "average_loss_pct": f"{avg_loss * 100:.2f}%",
                "win_loss_ratio": float(win_loss_ratio),
                "best_period": float(excess_returns.max()),
                "best_period_pct": f"{excess_returns.max() * 100:.2f}%",
                "worst_period": float(excess_returns.min()),
                "worst_period_pct": f"{excess_returns.min() * 100:.2f}%"
            },
            "time_series_analysis": {
                "analysis_period": {
                    "start_date": str(excess_returns.index.min().date()),
                    "end_date": str(excess_returns.index.max().date()),
                    "total_periods": len(excess_returns)
                },
                "recent_performance": {
                    "last_month_excess": float(excess_returns.iloc[-21:].sum()) if len(excess_returns) >= 21 else float(excess_returns.iloc[-len(excess_returns):].sum()),
                    "last_quarter_excess": float(excess_returns.iloc[-63:].sum()) if len(excess_returns) >= 63 else float(excess_returns.iloc[-len(excess_returns):].sum()),
                    "last_year_excess": float(excess_returns.iloc[-252:].sum()) if len(excess_returns) >= 252 else float(excess_returns.iloc[-len(excess_returns):].sum())
                }
            }
        }
        
        # Add asset-level attribution if asset returns provided
        if asset_returns is not None:
            if isinstance(asset_returns, dict):
                asset_returns_df = pd.DataFrame(asset_returns)
            else:
                asset_returns_df = asset_returns.copy()
            
            # Align with weights and return period
            common_period = weights_df.index.intersection(asset_returns_df.index)
            if len(common_period) > 0:
                period_weights = weights_df.loc[common_period]
                period_asset_returns = asset_returns_df.loc[common_period]
                
                # Calculate asset contributions to portfolio return
                asset_contributions = period_weights.multiply(period_asset_returns, axis=0)
                avg_contributions = asset_contributions.mean()
                
                # Sort by contribution
                sorted_contributions = avg_contributions.sort_values(ascending=False)
                
                result["asset_level_attribution"] = {
                    "top_contributors": [
                        {
                            "asset": str(asset),
                            "avg_contribution": float(contrib),
                            "avg_contribution_pct": f"{contrib * 100:.2f}%",
                            "contribution_to_total": f"{contrib / avg_contributions.sum() * 100:.2f}%" if avg_contributions.sum() != 0 else "0.00%"
                        }
                        for asset, contrib in sorted_contributions.head(5).items()
                    ],
                    "bottom_contributors": [
                        {
                            "asset": str(asset),
                            "avg_contribution": float(contrib),
                            "avg_contribution_pct": f"{contrib * 100:.2f}%",
                            "contribution_to_total": f"{contrib / avg_contributions.sum() * 100:.2f}%" if avg_contributions.sum() != 0 else "0.00%"
                        }
                        for asset, contrib in sorted_contributions.tail(5).items()
                    ]
                }
        
        return standardize_output(result, "perform_attribution")
        
    except Exception as e:
        return {"success": False, "error": f"Return attribution analysis failed: {str(e)}"}


def calculate_portfolio_var(weights: Union[pd.Series, Dict[str, Any], List[float]],
                           covariance_matrix: Union[pd.DataFrame, Dict[str, Any], np.ndarray],
                           confidence: float = 0.05,
                           time_horizon: int = 1) -> Dict[str, Any]:
    """
    Calculate portfolio Value at Risk using covariance matrix approach.
    
    From financial-analysis-function-library.json portfolio_analysis category
    Uses scipy and numpy for VaR calculation - no code duplication
    
    Args:
        weights: Portfolio weights
        covariance_matrix: Asset covariance matrix
        confidence: Confidence level (e.g., 0.05 for 95% VaR)
        time_horizon: Time horizon in days
        
    Returns:
        Dict: Portfolio VaR analysis results
    """
    try:
        # Validate and convert inputs
        if isinstance(weights, dict):
            weights = pd.Series(weights)
        elif isinstance(weights, list):
            weights = pd.Series(weights)
        
        if isinstance(covariance_matrix, dict):
            cov_matrix = pd.DataFrame(covariance_matrix)
        elif isinstance(covariance_matrix, np.ndarray):
            cov_matrix = pd.DataFrame(covariance_matrix)
        else:
            cov_matrix = covariance_matrix.copy()
        
        # Ensure weights are normalized
        weights = weights / weights.sum()
        
        # Convert to numpy arrays for calculations
        w = weights.values
        cov = cov_matrix.values
        
        # Calculate portfolio variance
        portfolio_variance = np.dot(w, np.dot(cov, w))
        portfolio_volatility = np.sqrt(portfolio_variance)
        
        # Adjust for time horizon
        horizon_volatility = portfolio_volatility * np.sqrt(time_horizon)
        
        # Calculate VaR using normal distribution assumption
        z_score = stats.norm.ppf(confidence)
        parametric_var = abs(z_score * horizon_volatility)
        
        # Calculate component VaR (marginal contribution of each asset)
        marginal_var = np.dot(cov, w) / portfolio_volatility * abs(z_score) * np.sqrt(time_horizon)
        component_var = weights * marginal_var
        
        # Calculate diversification benefit
        individual_vars = np.sqrt(np.diag(cov)) * abs(z_score) * np.sqrt(time_horizon)
        undiversified_var = np.sum(weights * individual_vars)
        diversification_benefit = undiversified_var - parametric_var
        diversification_ratio = diversification_benefit / undiversified_var if undiversified_var > 0 else 0
        
        # Risk decomposition
        sorted_component_var = component_var.sort_values(ascending=False)
        
        # Calculate incremental VaR (impact of removing each asset)
        incremental_vars = []
        for i in range(len(weights)):
            # Create weights without asset i
            reduced_weights = weights.copy()
            reduced_weights.iloc[i] = 0
            reduced_weights = reduced_weights / reduced_weights.sum() if reduced_weights.sum() > 0 else reduced_weights
            
            if reduced_weights.sum() > 0:
                reduced_var = np.sqrt(np.dot(reduced_weights, np.dot(cov, reduced_weights))) * abs(z_score) * np.sqrt(time_horizon)
                incremental_var = parametric_var - reduced_var
            else:
                incremental_var = parametric_var
            
            incremental_vars.append(incremental_var)
        
        incremental_var_series = pd.Series(incremental_vars, index=weights.index)
        
        result = {
            "var_metrics": {
                "portfolio_var": float(parametric_var),
                "portfolio_var_pct": f"{parametric_var * 100:.2f}%",
                "confidence_level": confidence,
                "confidence_level_pct": f"{(1 - confidence) * 100:.1f}%",
                "time_horizon_days": time_horizon,
                "portfolio_volatility": float(portfolio_volatility),
                "portfolio_volatility_pct": f"{portfolio_volatility * 100:.2f}%",
                "horizon_adjusted_volatility": float(horizon_volatility),
                "horizon_adjusted_volatility_pct": f"{horizon_volatility * 100:.2f}%"
            },
            "diversification_analysis": {
                "undiversified_var": float(undiversified_var),
                "undiversified_var_pct": f"{undiversified_var * 100:.2f}%",
                "diversification_benefit": float(diversification_benefit),
                "diversification_benefit_pct": f"{diversification_benefit * 100:.2f}%",
                "diversification_ratio": float(diversification_ratio),
                "risk_reduction": f"{diversification_ratio * 100:.2f}%"
            },
            "component_analysis": {
                "top_risk_contributors": [
                    {
                        "asset_index": int(idx),
                        "weight": float(weights.iloc[idx]),
                        "weight_pct": f"{weights.iloc[idx] * 100:.2f}%",
                        "component_var": float(contribution),
                        "component_var_pct": f"{contribution * 100:.2f}%",
                        "var_contribution_ratio": f"{contribution / parametric_var * 100:.2f}%" if parametric_var > 0 else "0.00%"
                    }
                    for idx, contribution in enumerate(sorted_component_var.iloc[:5])
                ],
                "total_component_var": float(component_var.sum()),
                "component_var_check": float(abs(component_var.sum() - parametric_var))  # Should be close to 0
            },
            "incremental_analysis": {
                "largest_incremental_vars": [
                    {
                        "asset_index": int(idx),
                        "weight": float(weights.iloc[idx]),
                        "weight_pct": f"{weights.iloc[idx] * 100:.2f}%",
                        "incremental_var": float(inc_var),
                        "incremental_var_pct": f"{inc_var * 100:.2f}%",
                        "var_impact_if_removed": f"{inc_var / parametric_var * 100:.2f}%" if parametric_var > 0 else "0.00%"
                    }
                    for idx, inc_var in incremental_var_series.sort_values(ascending=False).head(5).items()
                ]
            }
        }
        
        return standardize_output(result, "calculate_portfolio_var")
        
    except Exception as e:
        return {"success": False, "error": f"Portfolio VaR calculation failed: {str(e)}"}


def stress_test_portfolio(weights: Union[pd.Series, Dict[str, Any], List[float]],
                         returns: Union[pd.DataFrame, Dict[str, Any]],
                         scenarios: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Perform portfolio stress testing using scipy and numpy.
    
    From financial-analysis-function-library.json portfolio_analysis category
    Uses statistical methods for stress testing - no code duplication
    
    Args:
        weights: Portfolio weights
        returns: Historical asset returns
        scenarios: Custom stress scenarios
        
    Returns:
        Dict: Stress test results
    """
    try:
        # Validate and convert inputs
        if isinstance(weights, dict):
            weights = pd.Series(weights)
        elif isinstance(weights, list):
            weights = pd.Series(weights)
        
        if isinstance(returns, dict):
            returns_df = pd.DataFrame(returns)
        else:
            returns_df = returns.copy()
        
        # Ensure weights are normalized
        weights = weights / weights.sum()
        
        # Calculate portfolio returns
        portfolio_returns = returns_df.dot(weights)
        
        # Base portfolio statistics
        portfolio_mean = portfolio_returns.mean()
        portfolio_std = portfolio_returns.std()
        portfolio_var_95 = portfolio_returns.quantile(0.05)
        portfolio_var_99 = portfolio_returns.quantile(0.01)
        
        # Define default stress scenarios if none provided
        if scenarios is None:
            scenarios = [
                {"name": "Market_Crash", "description": "2008-style market crash", "factor": -0.20},
                {"name": "Moderate_Stress", "description": "Moderate market stress", "factor": -0.10},
                {"name": "Severe_Stress", "description": "Severe market stress", "factor": -0.30},
                {"name": "Extreme_Stress", "description": "Extreme market stress", "factor": -0.40},
                {"name": "Volatility_Spike", "description": "Volatility spike scenario", "factor": "vol_spike"}
            ]
        
        stress_results = []
        
        for scenario in scenarios:
            scenario_name = scenario.get("name", "Unknown")
            scenario_description = scenario.get("description", "")
            stress_factor = scenario.get("factor", -0.10)
            
            if stress_factor == "vol_spike":
                # Volatility spike scenario - increase volatility by 2x
                stressed_returns = portfolio_returns + np.random.normal(0, portfolio_std * 2, len(portfolio_returns))
                stressed_mean = portfolio_mean
                stressed_std = portfolio_std * 2
            else:
                # Simple shock scenario
                stressed_returns = portfolio_returns + stress_factor
                stressed_mean = portfolio_mean + stress_factor
                stressed_std = portfolio_std
            
            # Calculate stressed metrics
            stressed_var_95 = np.percentile(stressed_returns, 5)
            stressed_var_99 = np.percentile(stressed_returns, 1)
            
            # Expected shortfall (CVaR)
            stressed_cvar_95 = stressed_returns[stressed_returns <= stressed_var_95].mean()
            stressed_cvar_99 = stressed_returns[stressed_returns <= stressed_var_99].mean()
            
            # Loss relative to current value (assuming current portfolio value = 1)
            loss_95 = abs(stressed_var_95) if stressed_var_95 < 0 else 0
            loss_99 = abs(stressed_var_99) if stressed_var_99 < 0 else 0
            
            # Probability of significant losses
            prob_loss_10 = (stressed_returns < -0.10).mean()
            prob_loss_20 = (stressed_returns < -0.20).mean()
            
            stress_result = {
                "scenario_name": scenario_name,
                "scenario_description": scenario_description,
                "stress_factor": stress_factor,
                "expected_return": float(stressed_mean),
                "expected_return_pct": f"{stressed_mean * 100:.2f}%",
                "volatility": float(stressed_std),
                "volatility_pct": f"{stressed_std * 100:.2f}%",
                "var_95": float(stressed_var_95),
                "var_95_pct": f"{stressed_var_95 * 100:.2f}%",
                "var_99": float(stressed_var_99),
                "var_99_pct": f"{stressed_var_99 * 100:.2f}%",
                "cvar_95": float(stressed_cvar_95),
                "cvar_95_pct": f"{stressed_cvar_95 * 100:.2f}%",
                "cvar_99": float(stressed_cvar_99),
                "cvar_99_pct": f"{stressed_cvar_99 * 100:.2f}%",
                "max_loss_95": float(loss_95),
                "max_loss_95_pct": f"{loss_95 * 100:.2f}%",
                "max_loss_99": float(loss_99),
                "max_loss_99_pct": f"{loss_99 * 100:.2f}%",
                "prob_loss_10pct": float(prob_loss_10),
                "prob_loss_20pct": float(prob_loss_20)
            }
            
            stress_results.append(stress_result)
        
        # Find worst-case scenario
        worst_scenario = min(stress_results, key=lambda x: x["var_99"])
        best_scenario = max(stress_results, key=lambda x: x["var_99"])
        
        # Portfolio resilience metrics
        base_var_95 = float(portfolio_var_95)
        worst_var_95 = worst_scenario["var_95"]
        stress_amplification = abs(worst_var_95 / base_var_95) if base_var_95 != 0 else 1
        
        result = {
            "stress_test_summary": {
                "scenarios_tested": len(scenarios),
                "base_portfolio_var_95": base_var_95,
                "base_portfolio_var_95_pct": f"{base_var_95 * 100:.2f}%",
                "worst_case_var_95": worst_var_95,
                "worst_case_var_95_pct": f"{worst_var_95 * 100:.2f}%",
                "stress_amplification_factor": float(stress_amplification),
                "worst_scenario_name": worst_scenario["scenario_name"],
                "best_scenario_name": best_scenario["scenario_name"]
            },
            "portfolio_resilience": {
                "base_volatility": float(portfolio_std),
                "base_volatility_pct": f"{portfolio_std * 100:.2f}%",
                "resilience_score": max(0, 1 - stress_amplification / 2),  # Simple resilience metric
                "vulnerability_assessment": "high" if stress_amplification > 2 else "moderate" if stress_amplification > 1.5 else "low"
            },
            "detailed_scenarios": stress_results,
            "risk_assessment": {
                "maximum_potential_loss_95": max([s["max_loss_95"] for s in stress_results]),
                "maximum_potential_loss_95_pct": f"{max([s['max_loss_95'] for s in stress_results]) * 100:.2f}%",
                "maximum_potential_loss_99": max([s["max_loss_99"] for s in stress_results]),
                "maximum_potential_loss_99_pct": f"{max([s['max_loss_99'] for s in stress_results]) * 100:.2f}%",
                "avg_prob_significant_loss": np.mean([s["prob_loss_10pct"] for s in stress_results]),
                "recommendations": [
                    "Consider reducing concentration in high-risk assets" if stress_amplification > 2 else "Portfolio shows reasonable resilience",
                    "Monitor correlation during stress periods" if any(s["var_95"] < -0.15 for s in stress_results) else "Stress losses appear manageable",
                    "Consider hedge instruments" if worst_scenario["max_loss_95"] > 0.25 else "Current risk levels appear acceptable"
                ]
            }
        }
        
        return standardize_output(result, "stress_test_portfolio")
        
    except Exception as e:
        return {"success": False, "error": f"Portfolio stress testing failed: {str(e)}"}


# Registry of portfolio analysis functions
PORTFOLIO_ANALYSIS_FUNCTIONS = {
    'calculate_portfolio_metrics': calculate_portfolio_metrics,
    'analyze_portfolio_concentration': analyze_portfolio_concentration,
    'calculate_portfolio_beta': calculate_portfolio_beta,
    'analyze_portfolio_turnover': analyze_portfolio_turnover,
    'calculate_active_share': calculate_active_share,
    'perform_attribution': perform_attribution,
    'calculate_portfolio_var': calculate_portfolio_var,
    'stress_test_portfolio': stress_test_portfolio
}