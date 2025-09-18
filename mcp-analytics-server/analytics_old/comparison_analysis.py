"""
Comparison Analysis Functions

Functions for comparing assets, strategies, and portfolios, matching the 
categorical structure from financial-analysis-function-library.json

From financial-analysis-function-library.json category: comparison_analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
import warnings
warnings.filterwarnings('ignore')


def comparePerformanceMetrics(
    returns1: Union[pd.Series, List[float], Dict[str, Any]],
    returns2: Union[pd.Series, List[float], Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Compare key performance metrics between two assets/strategies.
    
    From financial-analysis-function-library.json
    
    Args:
        returns1: First asset/strategy return series
        returns2: Second asset/strategy return series
        
    Returns:
        {
            "asset1_metrics": Dict,
            "asset2_metrics": Dict,
            "comparison": Dict,
            "winner": str,
            "success": bool
        }
    """
    try:
        # Handle input formats
        def extract_series(data):
            if isinstance(data, dict) and "returns" in data:
                return data["returns"]
            elif isinstance(data, dict) and "filtered_data" in data:
                return data["filtered_data"]
            elif isinstance(data, (list, np.ndarray)):
                return pd.Series(data)
            elif isinstance(data, pd.Series):
                return data
            else:
                raise ValueError("Invalid data format")
        
        series1 = extract_series(returns1)
        series2 = extract_series(returns2)
        
        # Align the series
        aligned_data = pd.DataFrame({
            'asset1': series1,
            'asset2': series2
        }).dropna()
        
        if len(aligned_data) < 10:
            return {"success": False, "error": "Need at least 10 aligned observations"}
        
        s1 = aligned_data['asset1']
        s2 = aligned_data['asset2']
        
        # Calculate performance metrics for both assets
        def calc_metrics(series):
            total_return = (1 + series).prod() - 1
            annualized_return = (1 + total_return) ** (252 / len(series)) - 1
            volatility = series.std() * np.sqrt(252)
            sharpe_ratio = (annualized_return - 0.02) / volatility if volatility > 0 else 0
            
            # Max drawdown
            cumulative = (1 + series).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min()
            
            # Win rate
            win_rate = (series > 0).sum() / len(series)
            
            return {
                "total_return": float(total_return),
                "annualized_return": float(annualized_return),
                "volatility": float(volatility),
                "sharpe_ratio": float(sharpe_ratio),
                "max_drawdown": float(max_drawdown),
                "win_rate": float(win_rate),
                "best_day": float(series.max()),
                "worst_day": float(series.min())
            }
        
        asset1_metrics = calc_metrics(s1)
        asset2_metrics = calc_metrics(s2)
        
        # Create comparison
        comparison = {}
        winner_scores = {"asset1": 0, "asset2": 0}
        
        for metric in ["total_return", "annualized_return", "sharpe_ratio", "win_rate"]:
            if asset1_metrics[metric] > asset2_metrics[metric]:
                comparison[f"{metric}_winner"] = "asset1"
                winner_scores["asset1"] += 1
            elif asset2_metrics[metric] > asset1_metrics[metric]:
                comparison[f"{metric}_winner"] = "asset2"
                winner_scores["asset2"] += 1
            else:
                comparison[f"{metric}_winner"] = "tie"
            
            comparison[f"{metric}_difference"] = asset1_metrics[metric] - asset2_metrics[metric]
        
        # For risk metrics (lower is better)
        for metric in ["volatility", "max_drawdown"]:
            if asset1_metrics[metric] < asset2_metrics[metric]:
                comparison[f"{metric}_winner"] = "asset1"
                winner_scores["asset1"] += 1
            elif asset2_metrics[metric] < asset1_metrics[metric]:
                comparison[f"{metric}_winner"] = "asset2"
                winner_scores["asset2"] += 1
            else:
                comparison[f"{metric}_winner"] = "tie"
            
            comparison[f"{metric}_difference"] = asset1_metrics[metric] - asset2_metrics[metric]
        
        # Determine overall winner
        if winner_scores["asset1"] > winner_scores["asset2"]:
            overall_winner = "asset1"
        elif winner_scores["asset2"] > winner_scores["asset1"]:
            overall_winner = "asset2"
        else:
            overall_winner = "tie"
        
        return {
            "success": True,
            "asset1_metrics": asset1_metrics,
            "asset2_metrics": asset2_metrics,
            "comparison": comparison,
            "winner_scores": winner_scores,
            "overall_winner": overall_winner,
            "num_observations": len(aligned_data),
            "correlation": float(s1.corr(s2))
        }
        
    except Exception as e:
        return {"success": False, "error": f"Performance comparison failed: {str(e)}"}


def compareRiskMetrics(
    returns1: Union[pd.Series, List[float], Dict[str, Any]],
    returns2: Union[pd.Series, List[float], Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Compare risk metrics between two assets/strategies.
    
    From financial-analysis-function-library.json
    
    Args:
        returns1: First asset/strategy return series
        returns2: Second asset/strategy return series
        
    Returns:
        {
            "asset1_risk": Dict,
            "asset2_risk": Dict,
            "risk_comparison": Dict,
            "safer_asset": str,
            "success": bool
        }
    """
    try:
        # Handle input formats
        def extract_series(data):
            if isinstance(data, dict) and "returns" in data:
                return data["returns"]
            elif isinstance(data, dict) and "filtered_data" in data:
                return data["filtered_data"]
            elif isinstance(data, (list, np.ndarray)):
                return pd.Series(data)
            elif isinstance(data, pd.Series):
                return data
            else:
                raise ValueError("Invalid data format")
        
        series1 = extract_series(returns1)
        series2 = extract_series(returns2)
        
        # Align the series
        aligned_data = pd.DataFrame({
            'asset1': series1,
            'asset2': series2
        }).dropna()
        
        if len(aligned_data) < 10:
            return {"success": False, "error": "Need at least 10 aligned observations"}
        
        s1 = aligned_data['asset1']
        s2 = aligned_data['asset2']
        
        # Calculate risk metrics for both assets
        def calc_risk_metrics(series):
            # Basic volatility
            volatility = series.std() * np.sqrt(252)
            
            # VaR (5% worst case)
            var_95 = np.percentile(series, 5)
            var_99 = np.percentile(series, 1)
            
            # CVaR (Expected Shortfall)
            cvar_95 = series[series <= var_95].mean() if len(series[series <= var_95]) > 0 else var_95
            
            # Max drawdown
            cumulative = (1 + series).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min()
            
            # Downside deviation
            downside_returns = series[series < 0]
            downside_deviation = np.sqrt((downside_returns ** 2).mean()) * np.sqrt(252) if len(downside_returns) > 0 else 0
            
            # Skewness and Kurtosis
            skewness = series.skew()
            kurtosis = series.kurtosis()
            
            # Tail ratio (95th percentile / 5th percentile)
            p95 = np.percentile(series, 95)
            p5 = np.percentile(series, 5)
            tail_ratio = abs(p95 / p5) if p5 != 0 else float('inf')
            
            return {
                "volatility": float(volatility),
                "var_95": float(var_95),
                "var_99": float(var_99),
                "cvar_95": float(cvar_95),
                "max_drawdown": float(max_drawdown),
                "downside_deviation": float(downside_deviation),
                "skewness": float(skewness),
                "kurtosis": float(kurtosis),
                "tail_ratio": float(tail_ratio) if tail_ratio != float('inf') else "infinite"
            }
        
        asset1_risk = calc_risk_metrics(s1)
        asset2_risk = calc_risk_metrics(s2)
        
        # Create risk comparison (lower is better for most risk metrics)
        risk_comparison = {}
        safety_scores = {"asset1": 0, "asset2": 0}
        
        # Lower is better for these metrics
        lower_better_metrics = ["volatility", "var_95", "var_99", "cvar_95", "max_drawdown", "downside_deviation", "kurtosis"]
        
        for metric in lower_better_metrics:
            val1 = asset1_risk[metric]
            val2 = asset2_risk[metric]
            
            if isinstance(val1, str) or isinstance(val2, str):
                continue  # Skip infinite values
                
            if abs(val1) < abs(val2):
                risk_comparison[f"{metric}_safer"] = "asset1"
                safety_scores["asset1"] += 1
            elif abs(val2) < abs(val1):
                risk_comparison[f"{metric}_safer"] = "asset2"
                safety_scores["asset2"] += 1
            else:
                risk_comparison[f"{metric}_safer"] = "tie"
            
            risk_comparison[f"{metric}_difference"] = val1 - val2
        
        # For skewness, positive is generally better (right-skewed returns)
        if asset1_risk["skewness"] > asset2_risk["skewness"]:
            risk_comparison["skewness_better"] = "asset1"
            safety_scores["asset1"] += 1
        elif asset2_risk["skewness"] > asset1_risk["skewness"]:
            risk_comparison["skewness_better"] = "asset2"
            safety_scores["asset2"] += 1
        else:
            risk_comparison["skewness_better"] = "tie"
        
        # Determine safer asset
        if safety_scores["asset1"] > safety_scores["asset2"]:
            safer_asset = "asset1"
        elif safety_scores["asset2"] > safety_scores["asset1"]:
            safer_asset = "asset2"
        else:
            safer_asset = "tie"
        
        return {
            "success": True,
            "asset1_risk": asset1_risk,
            "asset2_risk": asset2_risk,
            "risk_comparison": risk_comparison,
            "safety_scores": safety_scores,
            "safer_asset": safer_asset,
            "num_observations": len(aligned_data),
            "correlation": float(s1.corr(s2))
        }
        
    except Exception as e:
        return {"success": False, "error": f"Risk comparison failed: {str(e)}"}


def compareDrawdowns(
    prices1: Union[pd.Series, List[float], Dict[str, Any]],
    prices2: Union[pd.Series, List[float], Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Compare drawdown characteristics.
    
    From financial-analysis-function-library.json
    
    Args:
        prices1: First asset price series
        prices2: Second asset price series
        
    Returns:
        {
            "asset1_drawdown": Dict,
            "asset2_drawdown": Dict,
            "drawdown_comparison": Dict,
            "success": bool
        }
    """
    try:
        # Handle input formats
        def extract_series(data):
            if isinstance(data, dict) and "prices" in data:
                return data["prices"]
            elif isinstance(data, dict) and "returns" in data:
                # Convert returns to price series
                return (1 + data["returns"]).cumprod() * 100
            elif isinstance(data, (list, np.ndarray)):
                return pd.Series(data)
            elif isinstance(data, pd.Series):
                return data
            else:
                raise ValueError("Invalid data format")
        
        series1 = extract_series(prices1)
        series2 = extract_series(prices2)
        
        # Align the series
        aligned_data = pd.DataFrame({
            'asset1': series1,
            'asset2': series2
        }).dropna()
        
        if len(aligned_data) < 10:
            return {"success": False, "error": "Need at least 10 aligned observations"}
        
        # Calculate drawdown analysis for both assets
        def calc_drawdown_analysis(prices):
            # Calculate cumulative returns if not already prices
            if prices.min() < 0:  # Likely returns, convert to prices
                cumulative = (1 + prices).cumprod() * 100
            else:
                cumulative = prices
            
            # Calculate running maximum
            running_max = cumulative.expanding().max()
            
            # Calculate drawdown series
            drawdown = (cumulative - running_max) / running_max
            
            # Find drawdown periods
            in_drawdown = drawdown < 0
            drawdown_changes = in_drawdown.diff()
            
            # Identify drawdown start and end points
            starts = drawdown_changes[drawdown_changes == True].index
            ends = drawdown_changes[drawdown_changes == False].index
            
            # Calculate drawdown statistics
            max_drawdown = drawdown.min()
            max_dd_date = drawdown.idxmin()
            
            # Calculate recovery times
            recovery_times = []
            drawdown_depths = []
            
            for i, start in enumerate(starts):
                # Find corresponding end
                end_candidates = ends[ends > start]
                if len(end_candidates) > 0:
                    end = end_candidates.iloc[0]
                    recovery_time = (end - start).days if hasattr(start, 'date') else (ends.get_loc(end) - starts.get_loc(start))
                    recovery_times.append(recovery_time)
                    
                    # Get the depth of this drawdown
                    period_drawdown = drawdown[start:end]
                    if len(period_drawdown) > 0:
                        drawdown_depths.append(period_drawdown.min())
            
            avg_recovery_time = np.mean(recovery_times) if recovery_times else 0
            max_recovery_time = max(recovery_times) if recovery_times else 0
            num_drawdowns = len(starts)
            
            return {
                "max_drawdown": float(max_drawdown),
                "max_drawdown_pct": f"{max_drawdown * 100:.2f}%",
                "max_dd_date": str(max_dd_date) if hasattr(max_dd_date, 'strftime') else str(max_dd_date),
                "num_drawdowns": int(num_drawdowns),
                "avg_recovery_time": float(avg_recovery_time),
                "max_recovery_time": float(max_recovery_time),
                "avg_drawdown_depth": float(np.mean(drawdown_depths)) if drawdown_depths else 0,
                "drawdown_series": drawdown,
                "time_underwater_pct": float((drawdown < 0).sum() / len(drawdown) * 100)
            }
        
        asset1_drawdown = calc_drawdown_analysis(aligned_data['asset1'])
        asset2_drawdown = calc_drawdown_analysis(aligned_data['asset2'])
        
        # Create comparison
        drawdown_comparison = {
            "max_drawdown_better": "asset1" if asset1_drawdown["max_drawdown"] > asset2_drawdown["max_drawdown"] else "asset2",
            "recovery_speed_better": "asset1" if asset1_drawdown["avg_recovery_time"] < asset2_drawdown["avg_recovery_time"] else "asset2",
            "frequency_better": "asset1" if asset1_drawdown["num_drawdowns"] < asset2_drawdown["num_drawdowns"] else "asset2",
            "time_underwater_better": "asset1" if asset1_drawdown["time_underwater_pct"] < asset2_drawdown["time_underwater_pct"] else "asset2"
        }
        
        return {
            "success": True,
            "asset1_drawdown": asset1_drawdown,
            "asset2_drawdown": asset2_drawdown,
            "drawdown_comparison": drawdown_comparison,
            "num_observations": len(aligned_data)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Drawdown comparison failed: {str(e)}"}


def compareVolatilityProfiles(
    returns1: Union[pd.Series, List[float], Dict[str, Any]],
    returns2: Union[pd.Series, List[float], Dict[str, Any]],
    window: int = 30
) -> Dict[str, Any]:
    """
    Compare rolling volatility profiles.
    
    From financial-analysis-function-library.json
    
    Args:
        returns1: First asset return series
        returns2: Second asset return series
        window: Rolling window for volatility calculation
        
    Returns:
        {
            "asset1_volatility": Dict,
            "asset2_volatility": Dict,
            "volatility_comparison": Dict,
            "success": bool
        }
    """
    try:
        # Handle input formats
        def extract_series(data):
            if isinstance(data, dict) and "returns" in data:
                return data["returns"]
            elif isinstance(data, dict) and "filtered_data" in data:
                return data["filtered_data"]
            elif isinstance(data, (list, np.ndarray)):
                return pd.Series(data)
            elif isinstance(data, pd.Series):
                return data
            else:
                raise ValueError("Invalid data format")
        
        series1 = extract_series(returns1)
        series2 = extract_series(returns2)
        
        # Align the series
        aligned_data = pd.DataFrame({
            'asset1': series1,
            'asset2': series2
        }).dropna()
        
        if len(aligned_data) < window + 10:
            return {"success": False, "error": f"Need at least {window + 10} aligned observations"}
        
        s1 = aligned_data['asset1']
        s2 = aligned_data['asset2']
        
        # Calculate rolling volatility
        vol1 = s1.rolling(window=window).std() * np.sqrt(252)
        vol2 = s2.rolling(window=window).std() * np.sqrt(252)
        
        vol1 = vol1.dropna()
        vol2 = vol2.dropna()
        
        # Calculate volatility statistics
        def calc_vol_stats(vol_series):
            return {
                "mean_volatility": float(vol_series.mean()),
                "volatility_volatility": float(vol_series.std()),  # Volatility of volatility
                "min_volatility": float(vol_series.min()),
                "max_volatility": float(vol_series.max()),
                "current_volatility": float(vol_series.iloc[-1]),
                "volatility_percentile_95": float(np.percentile(vol_series, 95)),
                "volatility_percentile_5": float(np.percentile(vol_series, 5))
            }
        
        asset1_vol_stats = calc_vol_stats(vol1)
        asset2_vol_stats = calc_vol_stats(vol2)
        
        # Calculate correlation between volatilities
        vol_correlation = vol1.corr(vol2)
        
        # Volatility regime analysis
        # High vol = above 75th percentile, Low vol = below 25th percentile
        def calc_regime_stats(vol_series, returns_series):
            p75 = np.percentile(vol_series, 75)
            p25 = np.percentile(vol_series, 25)
            
            high_vol_periods = vol_series > p75
            low_vol_periods = vol_series < p25
            
            # Align with returns (accounting for rolling window lag)
            aligned_returns = returns_series[vol_series.index]
            
            high_vol_returns = aligned_returns[high_vol_periods].mean() if high_vol_periods.sum() > 0 else 0
            low_vol_returns = aligned_returns[low_vol_periods].mean() if low_vol_periods.sum() > 0 else 0
            
            return {
                "high_vol_threshold": float(p75),
                "low_vol_threshold": float(p25),
                "high_vol_periods": int(high_vol_periods.sum()),
                "low_vol_periods": int(low_vol_periods.sum()),
                "high_vol_avg_return": float(high_vol_returns),
                "low_vol_avg_return": float(low_vol_returns)
            }
        
        # Calculate regime stats (need to align returns with volatility indices)
        asset1_regime = calc_regime_stats(vol1, s1)
        asset2_regime = calc_regime_stats(vol2, s2)
        
        # Create comparison
        volatility_comparison = {
            "lower_avg_volatility": "asset1" if asset1_vol_stats["mean_volatility"] < asset2_vol_stats["mean_volatility"] else "asset2",
            "more_stable_volatility": "asset1" if asset1_vol_stats["volatility_volatility"] < asset2_vol_stats["volatility_volatility"] else "asset2",
            "volatility_correlation": float(vol_correlation),
            "volatility_difference": asset1_vol_stats["mean_volatility"] - asset2_vol_stats["mean_volatility"]
        }
        
        return {
            "success": True,
            "asset1_volatility": {
                "statistics": asset1_vol_stats,
                "regime_analysis": asset1_regime,
                "rolling_volatility": vol1
            },
            "asset2_volatility": {
                "statistics": asset2_vol_stats,
                "regime_analysis": asset2_regime,
                "rolling_volatility": vol2
            },
            "volatility_comparison": volatility_comparison,
            "window_size": window,
            "num_observations": len(vol1)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Volatility comparison failed: {str(e)}"}


def compareExpenseRatios(
    funds: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Compare expense ratios and fees.
    
    From financial-analysis-function-library.json
    
    Args:
        funds: List of fund data with expense ratios
        
    Returns:
        {
            "expense_analysis": List[Dict],
            "cheapest_fund": str,
            "most_expensive_fund": str,
            "cost_impact": Dict,
            "success": bool
        }
    """
    try:
        if not funds or len(funds) < 2:
            return {"success": False, "error": "Need at least 2 funds for comparison"}
        
        expense_analysis = []
        investment_amount = 10000  # Standard amount for comparison
        time_horizon = 10  # 10 years
        
        for fund in funds:
            if "expense_ratio" not in fund:
                return {"success": False, "error": "All funds must have expense_ratio field"}
            
            expense_ratio = fund["expense_ratio"]
            fund_name = fund.get("name", "Unknown Fund")
            
            # Calculate cost impact over time
            annual_cost = investment_amount * expense_ratio
            total_cost_10yr = annual_cost * time_horizon
            
            # With compounding effect (assuming 7% annual return)
            annual_return = 0.07
            future_value_gross = investment_amount * (1 + annual_return) ** time_horizon
            future_value_net = investment_amount * (1 + annual_return - expense_ratio) ** time_horizon
            cost_impact_compounded = future_value_gross - future_value_net
            
            analysis = {
                "fund_name": fund_name,
                "expense_ratio": float(expense_ratio),
                "expense_ratio_pct": f"{expense_ratio * 100:.2f}%",
                "annual_cost": float(annual_cost),
                "total_cost_10yr": float(total_cost_10yr),
                "cost_impact_compounded": float(cost_impact_compounded),
                "net_return_10yr": float((future_value_net / investment_amount) - 1),
                "gross_return_10yr": float((future_value_gross / investment_amount) - 1)
            }
            
            expense_analysis.append(analysis)
        
        # Sort by expense ratio
        expense_analysis.sort(key=lambda x: x["expense_ratio"])
        
        cheapest_fund = expense_analysis[0]["fund_name"]
        most_expensive_fund = expense_analysis[-1]["fund_name"]
        
        # Calculate cost differences
        cheapest_expense = expense_analysis[0]["expense_ratio"]
        most_expensive_expense = expense_analysis[-1]["expense_ratio"]
        
        cost_difference = most_expensive_expense - cheapest_expense
        annual_cost_difference = investment_amount * cost_difference
        
        cost_impact = {
            "expense_ratio_spread": float(cost_difference),
            "expense_ratio_spread_pct": f"{cost_difference * 100:.2f}%",
            "annual_cost_difference": float(annual_cost_difference),
            "cost_difference_10yr": float(annual_cost_difference * time_horizon),
            "cheapest_expense_ratio": float(cheapest_expense),
            "most_expensive_expense_ratio": float(most_expensive_expense)
        }
        
        return {
            "success": True,
            "expense_analysis": expense_analysis,
            "cheapest_fund": cheapest_fund,
            "most_expensive_fund": most_expensive_fund,
            "cost_impact": cost_impact,
            "num_funds": len(funds),
            "investment_amount": investment_amount,
            "time_horizon": time_horizon
        }
        
    except Exception as e:
        return {"success": False, "error": f"Expense ratio comparison failed: {str(e)}"}


# Registry for MCP server
COMPARISON_ANALYSIS_FUNCTIONS = {
    'comparePerformanceMetrics': comparePerformanceMetrics,
    'compareRiskMetrics': compareRiskMetrics,
    'compareDrawdowns': compareDrawdowns,
    'compareVolatilityProfiles': compareVolatilityProfiles,
    'compareExpenseRatios': compareExpenseRatios
}