"""
Comparison Analysis Metrics using empyrical and pandas

Atomic comparison functions for assets, strategies, and portfolios
From financial-analysis-function-library.json comparison_analysis category
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Union, Optional
import warnings
warnings.filterwarnings('ignore')

# Use empyrical library from requirements.txt - no wheel reinvention
import empyrical
from scipy import stats

from ..utils.data_utils import validate_return_data, validate_price_data, align_series, standardize_output
from ..performance.metrics import (
    calculate_returns_metrics, 
    calculate_risk_metrics,
    calculate_drawdown_analysis,
    calculate_annualized_return,
    calculate_annualized_volatility,
    calculate_win_rate
)
from ..risk.metrics import (
    calculate_var,
    calculate_cvar,
    calculate_beta,
    calculate_correlation,
    calculate_skewness,
    calculate_kurtosis
)


def compare_performance_metrics(returns1: Union[pd.Series, Dict[str, Any]], 
                               returns2: Union[pd.Series, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compare key performance metrics between two assets/strategies.
    
    From financial-analysis-function-library.json comparison_analysis category
    Uses existing performance functions - no code duplication
    
    Args:
        returns1: First asset/strategy returns
        returns2: Second asset/strategy returns
        
    Returns:
        Dict: Performance comparison data
    """
    try:
        returns_series1 = validate_return_data(returns1)
        returns_series2 = validate_return_data(returns2)
        
        # Align series for fair comparison
        ret1_aligned, ret2_aligned = align_series(returns_series1, returns_series2)
        
        # Calculate performance metrics for both
        perf1 = calculate_returns_metrics(ret1_aligned)
        perf2 = calculate_returns_metrics(ret2_aligned)
        risk1 = calculate_risk_metrics(ret1_aligned)
        risk2 = calculate_risk_metrics(ret2_aligned)
        
        # Extract key metrics for comparison
        metrics_comparison = {
            "annual_return": {
                "asset_1": perf1.get("annual_return", 0),
                "asset_2": perf2.get("annual_return", 0),
                "difference": perf2.get("annual_return", 0) - perf1.get("annual_return", 0),
                "winner": "asset_2" if perf2.get("annual_return", 0) > perf1.get("annual_return", 0) else "asset_1"
            },
            "total_return": {
                "asset_1": perf1.get("total_return", 0),
                "asset_2": perf2.get("total_return", 0),
                "difference": perf2.get("total_return", 0) - perf1.get("total_return", 0),
                "winner": "asset_2" if perf2.get("total_return", 0) > perf1.get("total_return", 0) else "asset_1"
            },
            "volatility": {
                "asset_1": risk1.get("volatility", 0),
                "asset_2": risk2.get("volatility", 0),
                "difference": risk2.get("volatility", 0) - risk1.get("volatility", 0),
                "winner": "asset_1" if risk1.get("volatility", 0) < risk2.get("volatility", 0) else "asset_2"
            },
            "sharpe_ratio": {
                "asset_1": risk1.get("sharpe_ratio", 0),
                "asset_2": risk2.get("sharpe_ratio", 0),
                "difference": risk2.get("sharpe_ratio", 0) - risk1.get("sharpe_ratio", 0),
                "winner": "asset_2" if risk2.get("sharpe_ratio", 0) > risk1.get("sharpe_ratio", 0) else "asset_1"
            },
            "max_drawdown": {
                "asset_1": risk1.get("max_drawdown", 0),
                "asset_2": risk2.get("max_drawdown", 0),
                "difference": risk2.get("max_drawdown", 0) - risk1.get("max_drawdown", 0),
                "winner": "asset_1" if abs(risk1.get("max_drawdown", 0)) < abs(risk2.get("max_drawdown", 0)) else "asset_2"
            }
        }
        
        # Calculate win rates
        win_rate1 = calculate_win_rate(ret1_aligned)
        win_rate2 = calculate_win_rate(ret2_aligned)
        
        metrics_comparison["win_rate"] = {
            "asset_1": win_rate1,
            "asset_2": win_rate2,
            "difference": win_rate2 - win_rate1,
            "winner": "asset_2" if win_rate2 > win_rate1 else "asset_1"
        }
        
        # Calculate overall winner
        wins_asset1 = sum(1 for metric in metrics_comparison.values() if metric.get("winner") == "asset_1")
        wins_asset2 = sum(1 for metric in metrics_comparison.values() if metric.get("winner") == "asset_2")
        
        result = {
            "comparison_period": f"{len(ret1_aligned)} observations",
            "metrics_comparison": metrics_comparison,
            "summary": {
                "asset_1_wins": wins_asset1,
                "asset_2_wins": wins_asset2,
                "overall_winner": "asset_1" if wins_asset1 > wins_asset2 else "asset_2",
                "total_metrics": len(metrics_comparison)
            },
            "correlation": calculate_correlation(ret1_aligned, ret2_aligned)
        }
        
        return standardize_output(result, "compare_performance_metrics")
        
    except Exception as e:
        return {"success": False, "error": f"Performance comparison failed: {str(e)}"}


def compare_risk_metrics(returns1: Union[pd.Series, Dict[str, Any]], 
                        returns2: Union[pd.Series, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compare risk metrics between two assets/strategies.
    
    From financial-analysis-function-library.json comparison_analysis category
    Uses existing risk functions - no code duplication
    
    Args:
        returns1: First asset/strategy returns
        returns2: Second asset/strategy returns
        
    Returns:
        Dict: Risk comparison data
    """
    try:
        returns_series1 = validate_return_data(returns1)
        returns_series2 = validate_return_data(returns2)
        
        # Align series
        ret1_aligned, ret2_aligned = align_series(returns_series1, returns_series2)
        
        # Calculate risk metrics
        risk1 = calculate_risk_metrics(ret1_aligned)
        risk2 = calculate_risk_metrics(ret2_aligned)
        
        # VaR and CVaR calculations
        var1 = calculate_var(ret1_aligned, confidence_level=0.05)
        var2 = calculate_var(ret2_aligned, confidence_level=0.05)
        cvar1 = calculate_cvar(ret1_aligned, confidence_level=0.05)
        cvar2 = calculate_cvar(ret2_aligned, confidence_level=0.05)
        
        # Distribution metrics
        skew1 = calculate_skewness(ret1_aligned)
        skew2 = calculate_skewness(ret2_aligned)
        kurt1 = calculate_kurtosis(ret1_aligned)
        kurt2 = calculate_kurtosis(ret2_aligned)
        
        risk_comparison = {
            "volatility": {
                "asset_1": risk1.get("volatility", 0),
                "asset_2": risk2.get("volatility", 0),
                "difference": risk2.get("volatility", 0) - risk1.get("volatility", 0),
                "winner": "asset_1" if risk1.get("volatility", 0) < risk2.get("volatility", 0) else "asset_2"
            },
            "var_95": {
                "asset_1": var1.get("var_daily", 0),
                "asset_2": var2.get("var_daily", 0),
                "difference": var2.get("var_daily", 0) - var1.get("var_daily", 0),
                "winner": "asset_1" if abs(var1.get("var_daily", 0)) < abs(var2.get("var_daily", 0)) else "asset_2"
            },
            "cvar_95": {
                "asset_1": cvar1.get("cvar_daily", 0),
                "asset_2": cvar2.get("cvar_daily", 0),
                "difference": cvar2.get("cvar_daily", 0) - cvar1.get("cvar_daily", 0),
                "winner": "asset_1" if abs(cvar1.get("cvar_daily", 0)) < abs(cvar2.get("cvar_daily", 0)) else "asset_2"
            },
            "max_drawdown": {
                "asset_1": risk1.get("max_drawdown", 0),
                "asset_2": risk2.get("max_drawdown", 0),
                "difference": risk2.get("max_drawdown", 0) - risk1.get("max_drawdown", 0),
                "winner": "asset_1" if abs(risk1.get("max_drawdown", 0)) < abs(risk2.get("max_drawdown", 0)) else "asset_2"
            },
            "skewness": {
                "asset_1": skew1,
                "asset_2": skew2,
                "difference": skew2 - skew1,
                "winner": "asset_2" if skew2 > skew1 else "asset_1"  # Higher skewness is better
            },
            "kurtosis": {
                "asset_1": kurt1,
                "asset_2": kurt2,
                "difference": kurt2 - kurt1,
                "winner": "asset_1" if abs(kurt1) < abs(kurt2) else "asset_2"  # Lower excess kurtosis is better
            }
        }
        
        # Calculate overall risk winner (lower risk wins most categories)
        wins_asset1 = sum(1 for metric in risk_comparison.values() if metric.get("winner") == "asset_1")
        wins_asset2 = sum(1 for metric in risk_comparison.values() if metric.get("winner") == "asset_2")
        
        result = {
            "comparison_period": f"{len(ret1_aligned)} observations",
            "risk_comparison": risk_comparison,
            "summary": {
                "asset_1_wins": wins_asset1,
                "asset_2_wins": wins_asset2,
                "lower_risk_asset": "asset_1" if wins_asset1 > wins_asset2 else "asset_2",
                "total_metrics": len(risk_comparison)
            },
            "correlation": calculate_correlation(ret1_aligned, ret2_aligned)
        }
        
        return standardize_output(result, "compare_risk_metrics")
        
    except Exception as e:
        return {"success": False, "error": f"Risk comparison failed: {str(e)}"}


def compare_drawdowns(prices1: Union[pd.Series, Dict[str, Any]], 
                     prices2: Union[pd.Series, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compare drawdown characteristics.
    
    From financial-analysis-function-library.json comparison_analysis category
    Uses existing drawdown functions - no code duplication
    
    Args:
        prices1: First asset price series
        prices2: Second asset price series
        
    Returns:
        Dict: Drawdown comparison data
    """
    try:
        price_series1 = validate_price_data(prices1)
        price_series2 = validate_price_data(prices2)
        
        # Convert to returns for drawdown analysis
        returns1 = price_series1.pct_change().dropna()
        returns2 = price_series2.pct_change().dropna()
        
        # Align series
        ret1_aligned, ret2_aligned = align_series(returns1, returns2)
        
        # Calculate drawdown analysis
        dd1 = calculate_drawdown_analysis(ret1_aligned)
        dd2 = calculate_drawdown_analysis(ret2_aligned)
        
        # Extract drawdown details using empyrical
        dd_details1 = empyrical.drawdown_details(empyrical.cum_returns(ret1_aligned))
        dd_details2 = empyrical.drawdown_details(empyrical.cum_returns(ret2_aligned))
        
        # Calculate additional drawdown metrics
        drawdown_series1 = empyrical.drawdown_details(empyrical.cum_returns(ret1_aligned))
        drawdown_series2 = empyrical.drawdown_details(empyrical.cum_returns(ret2_aligned))
        
        # Count significant drawdowns (>5%)
        significant_dd1 = (drawdown_series1 < -0.05).sum() if hasattr(drawdown_series1, 'sum') else 0
        significant_dd2 = (drawdown_series2 < -0.05).sum() if hasattr(drawdown_series2, 'sum') else 0
        
        # Average time in drawdown
        in_drawdown1 = (drawdown_series1 < 0).sum() if hasattr(drawdown_series1, 'sum') else 0
        in_drawdown2 = (drawdown_series2 < 0).sum() if hasattr(drawdown_series2, 'sum') else 0
        
        pct_time_dd1 = (in_drawdown1 / len(ret1_aligned)) * 100 if len(ret1_aligned) > 0 else 0
        pct_time_dd2 = (in_drawdown2 / len(ret2_aligned)) * 100 if len(ret2_aligned) > 0 else 0
        
        drawdown_comparison = {
            "max_drawdown": {
                "asset_1": dd1.get("max_drawdown", 0),
                "asset_2": dd2.get("max_drawdown", 0),
                "difference": dd2.get("max_drawdown", 0) - dd1.get("max_drawdown", 0),
                "winner": "asset_1" if abs(dd1.get("max_drawdown", 0)) < abs(dd2.get("max_drawdown", 0)) else "asset_2"
            },
            "significant_drawdowns": {
                "asset_1": significant_dd1,
                "asset_2": significant_dd2,
                "difference": significant_dd2 - significant_dd1,
                "winner": "asset_1" if significant_dd1 < significant_dd2 else "asset_2"
            },
            "time_in_drawdown": {
                "asset_1": pct_time_dd1,
                "asset_2": pct_time_dd2,
                "difference": pct_time_dd2 - pct_time_dd1,
                "winner": "asset_1" if pct_time_dd1 < pct_time_dd2 else "asset_2"
            }
        }
        
        # Overall drawdown winner
        wins_asset1 = sum(1 for metric in drawdown_comparison.values() if metric.get("winner") == "asset_1")
        wins_asset2 = sum(1 for metric in drawdown_comparison.values() if metric.get("winner") == "asset_2")
        
        result = {
            "comparison_period": f"{len(ret1_aligned)} observations",
            "drawdown_comparison": drawdown_comparison,
            "summary": {
                "asset_1_wins": wins_asset1,
                "asset_2_wins": wins_asset2,
                "better_drawdown_profile": "asset_1" if wins_asset1 > wins_asset2 else "asset_2",
                "total_metrics": len(drawdown_comparison)
            }
        }
        
        return standardize_output(result, "compare_drawdowns")
        
    except Exception as e:
        return {"success": False, "error": f"Drawdown comparison failed: {str(e)}"}


def compare_volatility_profiles(returns1: Union[pd.Series, Dict[str, Any]], 
                               returns2: Union[pd.Series, Dict[str, Any]], 
                               window: int = 30) -> Dict[str, Any]:
    """
    Compare rolling volatility profiles.
    
    From financial-analysis-function-library.json comparison_analysis category
    Uses pandas rolling calculations - no code duplication
    
    Args:
        returns1: First asset returns
        returns2: Second asset returns
        window: Rolling window size
        
    Returns:
        Dict: Volatility profile comparison
    """
    try:
        returns_series1 = validate_return_data(returns1)
        returns_series2 = validate_return_data(returns2)
        
        # Align series
        ret1_aligned, ret2_aligned = align_series(returns_series1, returns_series2)
        
        # Calculate rolling volatility (annualized)
        rolling_vol1 = ret1_aligned.rolling(window=window).std() * np.sqrt(252)
        rolling_vol2 = ret2_aligned.rolling(window=window).std() * np.sqrt(252)
        
        # Remove NaN values
        rolling_vol1 = rolling_vol1.dropna()
        rolling_vol2 = rolling_vol2.dropna()
        
        # Align rolling series
        vol1_aligned, vol2_aligned = align_series(rolling_vol1, rolling_vol2)
        
        # Calculate volatility statistics
        vol_stats = {
            "average_volatility": {
                "asset_1": float(vol1_aligned.mean()),
                "asset_2": float(vol2_aligned.mean()),
                "difference": float(vol2_aligned.mean() - vol1_aligned.mean()),
                "winner": "asset_1" if vol1_aligned.mean() < vol2_aligned.mean() else "asset_2"
            },
            "volatility_volatility": {  # Volatility of volatility
                "asset_1": float(vol1_aligned.std()),
                "asset_2": float(vol2_aligned.std()),
                "difference": float(vol2_aligned.std() - vol1_aligned.std()),
                "winner": "asset_1" if vol1_aligned.std() < vol2_aligned.std() else "asset_2"
            },
            "max_volatility": {
                "asset_1": float(vol1_aligned.max()),
                "asset_2": float(vol2_aligned.max()),
                "difference": float(vol2_aligned.max() - vol1_aligned.max()),
                "winner": "asset_1" if vol1_aligned.max() < vol2_aligned.max() else "asset_2"
            },
            "min_volatility": {
                "asset_1": float(vol1_aligned.min()),
                "asset_2": float(vol2_aligned.min()),
                "difference": float(vol2_aligned.min() - vol1_aligned.min()),
                "winner": "asset_1" if vol1_aligned.min() < vol2_aligned.min() else "asset_2"
            }
        }
        
        # Volatility correlation
        vol_correlation = vol1_aligned.corr(vol2_aligned)
        
        # Periods of high volatility (>90th percentile)
        high_vol_threshold1 = vol1_aligned.quantile(0.9)
        high_vol_threshold2 = vol2_aligned.quantile(0.9)
        
        high_vol_periods1 = (vol1_aligned > high_vol_threshold1).sum()
        high_vol_periods2 = (vol2_aligned > high_vol_threshold2).sum()
        
        vol_stats["high_volatility_periods"] = {
            "asset_1": int(high_vol_periods1),
            "asset_2": int(high_vol_periods2),
            "difference": int(high_vol_periods2 - high_vol_periods1),
            "winner": "asset_1" if high_vol_periods1 < high_vol_periods2 else "asset_2"
        }
        
        # Overall volatility profile winner
        wins_asset1 = sum(1 for metric in vol_stats.values() if metric.get("winner") == "asset_1")
        wins_asset2 = sum(1 for metric in vol_stats.values() if metric.get("winner") == "asset_2")
        
        result = {
            "window_size": window,
            "comparison_period": f"{len(vol1_aligned)} rolling periods",
            "volatility_comparison": vol_stats,
            "volatility_correlation": float(vol_correlation),
            "summary": {
                "asset_1_wins": wins_asset1,
                "asset_2_wins": wins_asset2,
                "more_stable_volatility": "asset_1" if wins_asset1 > wins_asset2 else "asset_2",
                "total_metrics": len(vol_stats)
            }
        }
        
        return standardize_output(result, "compare_volatility_profiles")
        
    except Exception as e:
        return {"success": False, "error": f"Volatility profile comparison failed: {str(e)}"}


def compare_correlation_stability(returns1: Union[pd.Series, Dict[str, Any]], 
                                 returns2: Union[pd.Series, Dict[str, Any]], 
                                 window: int = 60) -> Dict[str, Any]:
    """
    Analyze correlation stability over time.
    
    From financial-analysis-function-library.json comparison_analysis category
    Uses pandas rolling correlation - no code duplication
    
    Args:
        returns1: First asset returns
        returns2: Second asset returns
        window: Rolling window for correlation calculation
        
    Returns:
        Dict: Correlation stability analysis
    """
    try:
        returns_series1 = validate_return_data(returns1)
        returns_series2 = validate_return_data(returns2)
        
        # Align series
        ret1_aligned, ret2_aligned = align_series(returns_series1, returns_series2)
        
        # Calculate rolling correlation
        rolling_corr = ret1_aligned.rolling(window=window).corr(ret2_aligned)
        rolling_corr = rolling_corr.dropna()
        
        if len(rolling_corr) == 0:
            raise ValueError("Insufficient data for rolling correlation calculation")
        
        # Calculate correlation statistics
        corr_stats = {
            "average_correlation": float(rolling_corr.mean()),
            "correlation_volatility": float(rolling_corr.std()),
            "max_correlation": float(rolling_corr.max()),
            "min_correlation": float(rolling_corr.min()),
            "correlation_range": float(rolling_corr.max() - rolling_corr.min())
        }
        
        # Correlation regime analysis
        high_corr_threshold = 0.7
        low_corr_threshold = 0.3
        
        high_corr_periods = (rolling_corr > high_corr_threshold).sum()
        low_corr_periods = (rolling_corr < low_corr_threshold).sum()
        moderate_corr_periods = len(rolling_corr) - high_corr_periods - low_corr_periods
        
        # Calculate percentage in each regime
        total_periods = len(rolling_corr)
        
        correlation_regimes = {
            "high_correlation_periods": {
                "count": int(high_corr_periods),
                "percentage": float((high_corr_periods / total_periods) * 100)
            },
            "moderate_correlation_periods": {
                "count": int(moderate_corr_periods),
                "percentage": float((moderate_corr_periods / total_periods) * 100)
            },
            "low_correlation_periods": {
                "count": int(low_corr_periods),
                "percentage": float((low_corr_periods / total_periods) * 100)
            }
        }
        
        # Stability assessment
        stability_score = 1 - (corr_stats["correlation_volatility"] / 1.0)  # Normalize by max possible std (1.0)
        stability_rating = "high" if stability_score > 0.8 else "moderate" if stability_score > 0.6 else "low"
        
        # Trend analysis - is correlation increasing or decreasing?
        recent_corr = rolling_corr.tail(window // 2).mean()
        early_corr = rolling_corr.head(window // 2).mean()
        correlation_trend = "increasing" if recent_corr > early_corr else "decreasing"
        trend_magnitude = abs(recent_corr - early_corr)
        
        result = {
            "window_size": window,
            "total_rolling_periods": total_periods,
            "correlation_statistics": corr_stats,
            "correlation_regimes": correlation_regimes,
            "stability_analysis": {
                "stability_score": float(stability_score),
                "stability_rating": stability_rating,
                "correlation_trend": correlation_trend,
                "trend_magnitude": float(trend_magnitude)
            },
            "overall_correlation": float(ret1_aligned.corr(ret2_aligned))
        }
        
        return standardize_output(result, "compare_correlation_stability")
        
    except Exception as e:
        return {"success": False, "error": f"Correlation stability analysis failed: {str(e)}"}


def compare_sector_exposure(holdings1: List[Dict[str, Any]], 
                           holdings2: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compare sector allocation between portfolios/ETFs.
    
    From financial-analysis-function-library.json comparison_analysis category
    Uses pandas for sector analysis - no code duplication
    
    Args:
        holdings1: First portfolio/ETF holdings
        holdings2: Second portfolio/ETF holdings
        
    Returns:
        Dict: Sector comparison data
    """
    try:
        # Convert holdings to DataFrames
        df1 = pd.DataFrame(holdings1)
        df2 = pd.DataFrame(holdings2)
        
        # Validate required columns
        required_cols = ['sector', 'weight']
        for col in required_cols:
            if col not in df1.columns or col not in df2.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Aggregate by sector
        sector_weights1 = df1.groupby('sector')['weight'].sum().sort_values(ascending=False)
        sector_weights2 = df2.groupby('sector')['weight'].sum().sort_values(ascending=False)
        
        # Get all unique sectors
        all_sectors = set(sector_weights1.index) | set(sector_weights2.index)
        
        # Create sector comparison
        sector_comparison = {}
        for sector in all_sectors:
            weight1 = sector_weights1.get(sector, 0)
            weight2 = sector_weights2.get(sector, 0)
            
            sector_comparison[sector] = {
                "portfolio_1_weight": float(weight1),
                "portfolio_2_weight": float(weight2),
                "difference": float(weight2 - weight1),
                "relative_difference": float((weight2 - weight1) / max(weight1, 0.01)) if weight1 > 0 else float('inf') if weight2 > 0 else 0
            }
        
        # Calculate concentration metrics
        def calculate_sector_concentration(weights):
            weights_array = np.array(list(weights.values()))
            weights_normalized = weights_array / weights_array.sum()
            hhi = np.sum(weights_normalized ** 2)
            return hhi
        
        concentration1 = calculate_sector_concentration(sector_weights1)
        concentration2 = calculate_sector_concentration(sector_weights2)
        
        # Find largest differences
        sorted_sectors = sorted(
            sector_comparison.items(), 
            key=lambda x: abs(x[1]['difference']), 
            reverse=True
        )
        
        largest_differences = [
            {
                "sector": sector,
                "difference": data["difference"],
                "portfolio_1_weight": data["portfolio_1_weight"],
                "portfolio_2_weight": data["portfolio_2_weight"]
            }
            for sector, data in sorted_sectors[:5]
        ]
        
        # Calculate sector overlap
        common_sectors = set(sector_weights1.index) & set(sector_weights2.index)
        overlap_percentage = (len(common_sectors) / len(all_sectors)) * 100
        
        result = {
            "total_sectors": len(all_sectors),
            "common_sectors": len(common_sectors),
            "overlap_percentage": float(overlap_percentage),
            "sector_comparison": sector_comparison,
            "concentration_analysis": {
                "portfolio_1_hhi": float(concentration1),
                "portfolio_2_hhi": float(concentration2),
                "more_concentrated": "portfolio_1" if concentration1 > concentration2 else "portfolio_2"
            },
            "largest_differences": largest_differences,
            "top_sectors": {
                "portfolio_1": [
                    {"sector": sector, "weight": float(weight)} 
                    for sector, weight in sector_weights1.head(5).items()
                ],
                "portfolio_2": [
                    {"sector": sector, "weight": float(weight)} 
                    for sector, weight in sector_weights2.head(5).items()
                ]
            }
        }
        
        return standardize_output(result, "compare_sector_exposure")
        
    except Exception as e:
        return {"success": False, "error": f"Sector exposure comparison failed: {str(e)}"}


def compare_expense_ratios(funds: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compare expense ratios and fees.
    
    From financial-analysis-function-library.json comparison_analysis category
    Simple expense ratio comparison - no code duplication
    
    Args:
        funds: List of fund data with expense ratios
        
    Returns:
        Dict: Expense comparison data
    """
    try:
        if len(funds) < 2:
            raise ValueError("At least 2 funds required for comparison")
        
        # Extract expense ratios
        expense_data = []
        for i, fund in enumerate(funds):
            if 'expense_ratio' not in fund:
                raise ValueError(f"Fund {i} missing expense_ratio")
            
            expense_data.append({
                "fund_name": fund.get("name", f"Fund_{i+1}"),
                "symbol": fund.get("symbol", f"FUND{i+1}"),
                "expense_ratio": float(fund["expense_ratio"]),
                "expense_ratio_pct": f"{float(fund['expense_ratio']) * 100:.2f}%"
            })
        
        # Sort by expense ratio
        expense_data_sorted = sorted(expense_data, key=lambda x: x["expense_ratio"])
        
        # Calculate cost impact over time
        def calculate_cost_impact(expense_ratio, initial_amount=10000, years=10, annual_return=0.07):
            """Calculate the cost impact of expense ratios over time"""
            # Final value with costs
            net_return = annual_return - expense_ratio
            final_with_costs = initial_amount * ((1 + net_return) ** years)
            
            # Final value without costs
            final_without_costs = initial_amount * ((1 + annual_return) ** years)
            
            # Cost impact
            cost_impact = final_without_costs - final_with_costs
            
            return {
                "final_value_with_costs": final_with_costs,
                "final_value_without_costs": final_without_costs,
                "total_cost_impact": cost_impact,
                "cost_impact_percentage": (cost_impact / final_without_costs) * 100
            }
        
        # Calculate cost impacts
        for fund in expense_data:
            fund["cost_impact_10_years"] = calculate_cost_impact(fund["expense_ratio"])
        
        # Find differences
        cheapest = expense_data_sorted[0]
        most_expensive = expense_data_sorted[-1]
        
        # Calculate difference in costs
        cost_difference = most_expensive["expense_ratio"] - cheapest["expense_ratio"]
        impact_difference = (
            most_expensive["cost_impact_10_years"]["total_cost_impact"] - 
            cheapest["cost_impact_10_years"]["total_cost_impact"]
        )
        
        result = {
            "funds_compared": len(funds),
            "expense_comparison": expense_data_sorted,
            "summary": {
                "cheapest_fund": {
                    "name": cheapest["fund_name"],
                    "expense_ratio": cheapest["expense_ratio"],
                    "expense_ratio_pct": cheapest["expense_ratio_pct"]
                },
                "most_expensive_fund": {
                    "name": most_expensive["fund_name"],
                    "expense_ratio": most_expensive["expense_ratio"],
                    "expense_ratio_pct": most_expensive["expense_ratio_pct"]
                },
                "cost_difference": {
                    "expense_ratio_difference": float(cost_difference),
                    "expense_ratio_difference_pct": f"{cost_difference * 100:.2f}%",
                    "10_year_impact_difference": float(impact_difference),
                    "percentage_savings": f"{(impact_difference / 10000) * 100:.2f}%"
                }
            }
        }
        
        return standardize_output(result, "compare_expense_ratios")
        
    except Exception as e:
        return {"success": False, "error": f"Expense ratio comparison failed: {str(e)}"}


def compare_liquidity(volumes1: Union[pd.Series, Dict[str, Any], List[float]], 
                     volumes2: Union[pd.Series, Dict[str, Any], List[float]]) -> Dict[str, Any]:
    """
    Compare liquidity metrics.
    
    From financial-analysis-function-library.json comparison_analysis category
    Uses pandas for volume analysis - no code duplication
    
    Args:
        volumes1: First asset volume data
        volumes2: Second asset volume data
        
    Returns:
        Dict: Liquidity comparison data
    """
    try:
        # Convert to pandas Series
        if isinstance(volumes1, (list, np.ndarray)):
            vol1 = pd.Series(volumes1)
        elif isinstance(volumes1, dict):
            vol1 = pd.Series(list(volumes1.values()))
        else:
            vol1 = volumes1.copy()
        
        if isinstance(volumes2, (list, np.ndarray)):
            vol2 = pd.Series(volumes2)
        elif isinstance(volumes2, dict):
            vol2 = pd.Series(list(volumes2.values()))
        else:
            vol2 = volumes2.copy()
        
        # Align series
        vol1_aligned, vol2_aligned = align_series(vol1, vol2)
        
        # Calculate liquidity metrics
        liquidity_metrics = {
            "average_volume": {
                "asset_1": float(vol1_aligned.mean()),
                "asset_2": float(vol2_aligned.mean()),
                "difference": float(vol2_aligned.mean() - vol1_aligned.mean()),
                "winner": "asset_2" if vol2_aligned.mean() > vol1_aligned.mean() else "asset_1"
            },
            "median_volume": {
                "asset_1": float(vol1_aligned.median()),
                "asset_2": float(vol2_aligned.median()),
                "difference": float(vol2_aligned.median() - vol1_aligned.median()),
                "winner": "asset_2" if vol2_aligned.median() > vol1_aligned.median() else "asset_1"
            },
            "volume_volatility": {  # Consistency of volume
                "asset_1": float(vol1_aligned.std()),
                "asset_2": float(vol2_aligned.std()),
                "difference": float(vol2_aligned.std() - vol1_aligned.std()),
                "winner": "asset_1" if vol1_aligned.std() < vol2_aligned.std() else "asset_2"  # Lower volatility is better
            },
            "max_volume": {
                "asset_1": float(vol1_aligned.max()),
                "asset_2": float(vol2_aligned.max()),
                "difference": float(vol2_aligned.max() - vol1_aligned.max()),
                "winner": "asset_2" if vol2_aligned.max() > vol1_aligned.max() else "asset_1"
            },
            "min_volume": {
                "asset_1": float(vol1_aligned.min()),
                "asset_2": float(vol2_aligned.min()),
                "difference": float(vol2_aligned.min() - vol1_aligned.min()),
                "winner": "asset_2" if vol2_aligned.min() > vol1_aligned.min() else "asset_1"
            }
        }
        
        # Calculate zero/low volume days
        low_volume_threshold_1 = vol1_aligned.quantile(0.1)  # Bottom 10%
        low_volume_threshold_2 = vol2_aligned.quantile(0.1)
        
        low_volume_days_1 = (vol1_aligned <= low_volume_threshold_1).sum()
        low_volume_days_2 = (vol2_aligned <= low_volume_threshold_2).sum()
        
        liquidity_metrics["low_volume_days"] = {
            "asset_1": int(low_volume_days_1),
            "asset_2": int(low_volume_days_2),
            "difference": int(low_volume_days_2 - low_volume_days_1),
            "winner": "asset_1" if low_volume_days_1 < low_volume_days_2 else "asset_2"
        }
        
        # Volume correlation
        volume_correlation = vol1_aligned.corr(vol2_aligned)
        
        # Overall liquidity winner
        wins_asset1 = sum(1 for metric in liquidity_metrics.values() if metric.get("winner") == "asset_1")
        wins_asset2 = sum(1 for metric in liquidity_metrics.values() if metric.get("winner") == "asset_2")
        
        # Liquidity score (normalized)
        def calculate_liquidity_score(volumes):
            # Higher average volume, lower volatility = better score
            avg_vol = volumes.mean()
            vol_consistency = 1 / (volumes.std() / avg_vol + 0.01)  # Coefficient of variation
            return avg_vol * vol_consistency
        
        score1 = calculate_liquidity_score(vol1_aligned)
        score2 = calculate_liquidity_score(vol2_aligned)
        
        result = {
            "comparison_period": f"{len(vol1_aligned)} observations",
            "liquidity_comparison": liquidity_metrics,
            "volume_correlation": float(volume_correlation),
            "liquidity_scores": {
                "asset_1_score": float(score1),
                "asset_2_score": float(score2),
                "score_ratio": float(score2 / score1) if score1 > 0 else float('inf')
            },
            "summary": {
                "asset_1_wins": wins_asset1,
                "asset_2_wins": wins_asset2,
                "more_liquid_asset": "asset_1" if score1 > score2 else "asset_2",
                "total_metrics": len(liquidity_metrics)
            }
        }
        
        return standardize_output(result, "compare_liquidity")
        
    except Exception as e:
        return {"success": False, "error": f"Liquidity comparison failed: {str(e)}"}


def compare_fundamental(fundamentals1: Dict[str, Any], 
                       fundamentals2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare fundamental metrics between companies.
    
    From financial-analysis-function-library.json comparison_analysis category
    Simple fundamental comparison - no code duplication
    
    Args:
        fundamentals1: First company fundamental data
        fundamentals2: Second company fundamental data
        
    Returns:
        Dict: Fundamental comparison data
    """
    try:
        # Define key fundamental metrics to compare
        key_metrics = [
            'pe_ratio', 'price_to_book', 'price_to_sales', 'price_to_cash_flow',
            'debt_to_equity', 'current_ratio', 'quick_ratio', 'return_on_equity',
            'return_on_assets', 'profit_margin', 'operating_margin', 'revenue_growth',
            'earnings_growth', 'dividend_yield', 'market_cap'
        ]
        
        fundamental_comparison = {}
        
        for metric in key_metrics:
            value1 = fundamentals1.get(metric)
            value2 = fundamentals2.get(metric)
            
            if value1 is not None and value2 is not None:
                try:
                    val1 = float(value1)
                    val2 = float(value2)
                    
                    # Determine winner based on metric type
                    if metric in ['pe_ratio', 'price_to_book', 'price_to_sales', 'price_to_cash_flow', 'debt_to_equity']:
                        # Lower is better
                        winner = "company_1" if val1 < val2 else "company_2"
                    else:
                        # Higher is better
                        winner = "company_1" if val1 > val2 else "company_2"
                    
                    fundamental_comparison[metric] = {
                        "company_1": val1,
                        "company_2": val2,
                        "difference": val2 - val1,
                        "relative_difference": ((val2 - val1) / abs(val1)) * 100 if val1 != 0 else float('inf'),
                        "winner": winner
                    }
                except (ValueError, TypeError):
                    # Skip metrics that can't be converted to float
                    continue
        
        # Calculate category winners
        valuation_metrics = ['pe_ratio', 'price_to_book', 'price_to_sales', 'price_to_cash_flow']
        financial_health_metrics = ['debt_to_equity', 'current_ratio', 'quick_ratio']
        profitability_metrics = ['return_on_equity', 'return_on_assets', 'profit_margin', 'operating_margin']
        growth_metrics = ['revenue_growth', 'earnings_growth']
        
        def count_category_wins(metrics_list):
            wins_c1 = sum(1 for metric in metrics_list 
                         if metric in fundamental_comparison and 
                         fundamental_comparison[metric]['winner'] == 'company_1')
            wins_c2 = sum(1 for metric in metrics_list 
                         if metric in fundamental_comparison and 
                         fundamental_comparison[metric]['winner'] == 'company_2')
            return wins_c1, wins_c2
        
        valuation_wins = count_category_wins(valuation_metrics)
        health_wins = count_category_wins(financial_health_metrics)
        profitability_wins = count_category_wins(profitability_metrics)
        growth_wins = count_category_wins(growth_metrics)
        
        # Overall fundamental winner
        total_wins_c1 = sum(1 for comp in fundamental_comparison.values() if comp['winner'] == 'company_1')
        total_wins_c2 = sum(1 for comp in fundamental_comparison.values() if comp['winner'] == 'company_2')
        
        result = {
            "metrics_compared": len(fundamental_comparison),
            "fundamental_comparison": fundamental_comparison,
            "category_analysis": {
                "valuation": {
                    "company_1_wins": valuation_wins[0],
                    "company_2_wins": valuation_wins[1],
                    "winner": "company_1" if valuation_wins[0] > valuation_wins[1] else "company_2"
                },
                "financial_health": {
                    "company_1_wins": health_wins[0],
                    "company_2_wins": health_wins[1],
                    "winner": "company_1" if health_wins[0] > health_wins[1] else "company_2"
                },
                "profitability": {
                    "company_1_wins": profitability_wins[0],
                    "company_2_wins": profitability_wins[1],
                    "winner": "company_1" if profitability_wins[0] > profitability_wins[1] else "company_2"
                },
                "growth": {
                    "company_1_wins": growth_wins[0],
                    "company_2_wins": growth_wins[1],
                    "winner": "company_1" if growth_wins[0] > growth_wins[1] else "company_2"
                }
            },
            "summary": {
                "company_1_total_wins": total_wins_c1,
                "company_2_total_wins": total_wins_c2,
                "overall_fundamental_winner": "company_1" if total_wins_c1 > total_wins_c2 else "company_2",
                "company_1_info": {
                    "name": fundamentals1.get("name", "Company 1"),
                    "symbol": fundamentals1.get("symbol", "N/A"),
                    "sector": fundamentals1.get("sector", "N/A")
                },
                "company_2_info": {
                    "name": fundamentals2.get("name", "Company 2"),
                    "symbol": fundamentals2.get("symbol", "N/A"),
                    "sector": fundamentals2.get("sector", "N/A")
                }
            }
        }
        
        return standardize_output(result, "compare_fundamental")
        
    except Exception as e:
        return {"success": False, "error": f"Fundamental comparison failed: {str(e)}"}


# Registry of comparison metrics functions - all using libraries and existing functions
COMPARISON_METRICS_FUNCTIONS = {
    'compare_performance_metrics': compare_performance_metrics,
    'compare_risk_metrics': compare_risk_metrics,
    'compare_drawdowns': compare_drawdowns,
    'compare_volatility_profiles': compare_volatility_profiles,
    'compare_correlation_stability': compare_correlation_stability,
    'compare_sector_exposure': compare_sector_exposure,
    'compare_expense_ratios': compare_expense_ratios,
    'compare_liquidity': compare_liquidity,
    'compare_fundamental': compare_fundamental
}