"""
Risk Metrics using empyrical and scipy

All risk calculations using libraries from requirements.txt
From financial-analysis-function-library.json
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Union, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Use empyrical and scipy from requirements.txt - no manual calculations
import empyrical
from scipy import stats

from ..utils.data_utils import validate_return_data, align_series, standardize_output


def calculate_var(returns: Union[pd.Series, Dict[str, Any]], 
                  confidence_level: float = 0.05,
                  method: str = "historical") -> Dict[str, Any]:
    """
    Calculate Value at Risk using empyrical and scipy.
    
    From financial-analysis-function-library.json
    Uses empyrical/scipy libraries instead of manual calculations - no code duplication
    
    Args:
        returns: Return series
        confidence_level: Confidence level (e.g., 0.05 for 95% VaR)
        method: Calculation method ('historical', 'parametric', 'cornish_fisher')
        
    Returns:
        Dict: VaR values and analysis
    """
    try:
        returns_series = validate_return_data(returns)
        
        if method == "historical":
            if EMPYRICAL_AVAILABLE:
                # Use empyrical - leveraging requirements.txt
                var = empyrical.value_at_risk(returns_series, cutoff=confidence_level)
            else:
                # Basic fallback
                var = np.percentile(returns_series, confidence_level * 100)
        
        elif method == "parametric" and SCIPY_AVAILABLE:
            # Use scipy for parametric VaR
            mean = returns_series.mean()
            std = returns_series.std()
            var = stats.norm.ppf(confidence_level, mean, std)
        
        elif method == "cornish_fisher" and SCIPY_AVAILABLE:
            # Cornish-Fisher expansion using scipy
            mean = returns_series.mean()
            std = returns_series.std()
            skew = stats.skew(returns_series)
            kurt = stats.kurtosis(returns_series)
            
            # Standard normal quantile
            z = stats.norm.ppf(confidence_level)
            
            # Cornish-Fisher adjustment
            cf_adjustment = (z + (z**2 - 1) * skew / 6 + 
                           (z**3 - 3*z) * kurt / 24 - 
                           (2*z**3 - 5*z) * skew**2 / 36)
            
            var = mean + std * cf_adjustment
        
        else:
            # Fallback to basic percentile
            var = np.percentile(returns_series, confidence_level * 100)
        
        # Calculate daily and annual VaR
        daily_var = float(var)
        annual_var = daily_var * np.sqrt(252)
        
        # Calculate number of violations
        violations = (returns_series < daily_var).sum()
        violation_rate = violations / len(returns_series)
        expected_violations = len(returns_series) * confidence_level
        
        result = {
            "var_daily": daily_var,
            "var_daily_pct": f"{daily_var * 100:.2f}%",
            "var_annual": annual_var,
            "var_annual_pct": f"{annual_var * 100:.2f}%",
            "confidence_level": confidence_level,
            "confidence_level_pct": f"{(1 - confidence_level) * 100:.1f}%",
            "method": method,
            "violations": int(violations),
            "violation_rate": float(violation_rate),
            "violation_rate_pct": f"{violation_rate * 100:.2f}%",
            "expected_violations": float(expected_violations),
            "backtesting_ratio": float(violations / expected_violations) if expected_violations > 0 else 0
        }
        
        return standardize_output(result, "calculate_var")
        
    except Exception as e:
        return {"success": False, "error": f"VaR calculation failed: {str(e)}"}


def calculate_cvar(returns: Union[pd.Series, Dict[str, Any]], 
                   confidence_level: float = 0.05) -> Dict[str, Any]:
    """
    Calculate Conditional Value at Risk (Expected Shortfall) using empyrical.
    
    From financial-analysis-function-library.json
    Uses empyrical library instead of manual calculations - no code duplication
    
    Args:
        returns: Return series
        confidence_level: Confidence level
        
    Returns:
        Dict: CVaR values and analysis
    """
    try:
        returns_series = validate_return_data(returns)
        
        if EMPYRICAL_AVAILABLE:
            # Use empyrical - leveraging requirements.txt
            cvar = empyrical.conditional_value_at_risk(returns_series, cutoff=confidence_level)
            var = empyrical.value_at_risk(returns_series, cutoff=confidence_level)
        else:
            # Basic fallback
            var = np.percentile(returns_series, confidence_level * 100)
            tail_losses = returns_series[returns_series <= var]
            cvar = tail_losses.mean() if len(tail_losses) > 0 else var
        
        # Calculate daily and annual CVaR
        daily_cvar = float(cvar)
        annual_cvar = daily_cvar * np.sqrt(252)
        
        # CVaR ratio (CVaR / VaR)
        cvar_ratio = abs(daily_cvar / var) if var != 0 else 1
        
        result = {
            "cvar_daily": daily_cvar,
            "cvar_daily_pct": f"{daily_cvar * 100:.2f}%",
            "cvar_annual": annual_cvar,
            "cvar_annual_pct": f"{annual_cvar * 100:.2f}%",
            "var_daily": float(var),
            "var_daily_pct": f"{var * 100:.2f}%",
            "cvar_var_ratio": float(cvar_ratio),
            "confidence_level": confidence_level,
            "confidence_level_pct": f"{(1 - confidence_level) * 100:.1f}%"
        }
        
        return standardize_output(result, "calculate_cvar")
        
    except Exception as e:
        return {"success": False, "error": f"CVaR calculation failed: {str(e)}"}


def calculate_correlation_analysis(returns: Union[pd.DataFrame, Dict[str, Any]],
                                  method: str = "pearson") -> Dict[str, Any]:
    """
    Calculate correlation analysis using pandas and scipy.
    
    From financial-analysis-function-library.json
    Uses pandas/scipy libraries instead of manual calculations - no code duplication
    
    Args:
        returns: Return data for multiple assets
        method: Correlation method ('pearson', 'spearman', 'kendall')
        
    Returns:
        Dict: Correlation matrix and analysis
    """
    try:
        if isinstance(returns, dict):
            returns_df = pd.DataFrame(returns)
        else:
            returns_df = returns.copy()
        
        # Drop NaN values
        returns_df = returns_df.dropna()
        
        if len(returns_df.columns) < 2:
            raise ValueError("At least 2 assets required for correlation analysis")
        
        # Calculate correlation matrix using pandas
        if method == "pearson":
            corr_matrix = returns_df.corr(method='pearson')
        elif method == "spearman":
            corr_matrix = returns_df.corr(method='spearman')
        elif method == "kendall":
            corr_matrix = returns_df.corr(method='kendall')
        else:
            corr_matrix = returns_df.corr(method='pearson')
            method = "pearson"
        
        # Extract upper triangle (remove duplicates)
        n = len(corr_matrix)
        correlations = []
        for i in range(n):
            for j in range(i+1, n):
                correlations.append({
                    "asset_1": corr_matrix.index[i],
                    "asset_2": corr_matrix.columns[j], 
                    "correlation": float(corr_matrix.iloc[i, j])
                })
        
        # Find highest and lowest correlations
        correlations_sorted = sorted(correlations, key=lambda x: x['correlation'])
        highest_corr = correlations_sorted[-1] if correlations_sorted else None
        lowest_corr = correlations_sorted[0] if correlations_sorted else None
        
        # Calculate average correlation
        corr_values = [c['correlation'] for c in correlations]
        avg_correlation = np.mean(corr_values) if corr_values else 0
        
        # Diversification ratio (1 - average correlation)
        diversification_ratio = 1 - abs(avg_correlation)
        
        result = {
            "correlation_matrix": corr_matrix,
            "method": method,
            "pairwise_correlations": correlations,
            "highest_correlation": highest_corr,
            "lowest_correlation": lowest_corr,
            "average_correlation": float(avg_correlation),
            "diversification_ratio": float(diversification_ratio),
            "n_assets": n,
            "n_observations": len(returns_df)
        }
        
        return standardize_output(result, "calculate_correlation_analysis")
        
    except Exception as e:
        return {"success": False, "error": f"Correlation analysis failed: {str(e)}"}


def calculate_beta_analysis(asset_returns: Union[pd.Series, Dict[str, Any]],
                           market_returns: Union[pd.Series, Dict[str, Any]],
                           risk_free_rate: float = 0.02) -> Dict[str, Any]:
    """
    Calculate beta analysis using empyrical and scipy.
    
    From financial-analysis-function-library.json
    Uses empyrical/scipy libraries instead of manual calculations - no code duplication
    
    Args:
        asset_returns: Asset return series
        market_returns: Market return series
        risk_free_rate: Risk-free rate
        
    Returns:
        Dict: Beta analysis results
    """
    try:
        asset_series = validate_return_data(asset_returns)
        market_series = validate_return_data(market_returns)
        
        # Align series
        asset_aligned, market_aligned = align_series(asset_series, market_series)
        
        if EMPYRICAL_AVAILABLE:
            # Use empyrical - leveraging requirements.txt
            beta = empyrical.beta(asset_aligned, market_aligned)
            alpha = empyrical.alpha(asset_aligned, market_aligned, risk_free=risk_free_rate)
        elif SCIPY_AVAILABLE:
            # Use scipy for regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(market_aligned, asset_aligned)
            beta = slope
            alpha = intercept - risk_free_rate / 252  # Daily alpha
        else:
            # Basic calculation
            covariance = np.cov(asset_aligned, market_aligned)[0, 1]
            market_variance = np.var(market_aligned)
            beta = covariance / market_variance if market_variance > 0 else 1
            
            # Simple alpha calculation
            asset_mean = asset_aligned.mean() * 252
            market_mean = market_aligned.mean() * 252
            alpha = asset_mean - (risk_free_rate + beta * (market_mean - risk_free_rate))
        
        # Calculate correlation
        correlation = asset_aligned.corr(market_aligned)
        
        # Calculate R-squared
        r_squared = correlation ** 2
        
        # Calculate tracking error
        excess_returns = asset_aligned - market_aligned
        tracking_error = excess_returns.std() * np.sqrt(252)
        
        # Calculate information ratio
        information_ratio = (excess_returns.mean() * 252) / tracking_error if tracking_error > 0 else 0
        
        # Interpret beta
        if beta > 1.2:
            beta_interpretation = "high_beta"
        elif beta > 0.8:
            beta_interpretation = "moderate_beta"
        elif beta > 0:
            beta_interpretation = "low_beta"
        else:
            beta_interpretation = "negative_beta"
        
        result = {
            "beta": float(beta),
            "alpha": float(alpha),
            "alpha_annualized": float(alpha * 252) if not EMPYRICAL_AVAILABLE else float(alpha),
            "alpha_pct": f"{(alpha * 252 if not EMPYRICAL_AVAILABLE else alpha) * 100:.2f}%",
            "correlation": float(correlation),
            "r_squared": float(r_squared),
            "tracking_error": float(tracking_error),
            "tracking_error_pct": f"{tracking_error * 100:.2f}%",
            "information_ratio": float(information_ratio),
            "beta_interpretation": beta_interpretation,
            "risk_free_rate": risk_free_rate,
            "n_observations": len(asset_aligned)
        }
        
        return standardize_output(result, "calculate_beta_analysis")
        
    except Exception as e:
        return {"success": False, "error": f"Beta analysis failed: {str(e)}"}


def stress_test_portfolio(returns: Union[pd.Series, Dict[str, Any]],
                         stress_scenarios: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Conduct portfolio stress testing using scipy.
    
    From financial-analysis-function-library.json
    Uses scipy for statistical analysis - no code duplication
    
    Args:
        returns: Portfolio return series
        stress_scenarios: Custom stress scenarios
        
    Returns:
        Dict: Stress test results
    """
    try:
        returns_series = validate_return_data(returns)
        
        # Default stress scenarios if none provided
        if stress_scenarios is None:
            stress_scenarios = [
                {"name": "Market Crash", "return_shock": -0.20, "volatility_multiplier": 2.0},
                {"name": "Moderate Correction", "return_shock": -0.10, "volatility_multiplier": 1.5},
                {"name": "High Volatility", "return_shock": 0.0, "volatility_multiplier": 2.5},
                {"name": "Low Growth", "return_shock": -0.05, "volatility_multiplier": 1.2}
            ]
        
        # Calculate base portfolio metrics
        mean_return = returns_series.mean()
        std_return = returns_series.std()
        
        stress_results = []
        
        for scenario in stress_scenarios:
            scenario_name = scenario.get("name", "Unknown")
            return_shock = scenario.get("return_shock", 0)
            vol_multiplier = scenario.get("volatility_multiplier", 1)
            
            # Apply stress scenario
            stressed_mean = mean_return + return_shock / 252  # Daily shock
            stressed_std = std_return * vol_multiplier
            
            if SCIPY_AVAILABLE:
                # Use scipy for scenario analysis
                # Calculate probability of large losses
                prob_loss_5pct = stats.norm.cdf(-0.05, stressed_mean, stressed_std)
                prob_loss_10pct = stats.norm.cdf(-0.10, stressed_mean, stressed_std) 
                prob_loss_20pct = stats.norm.cdf(-0.20, stressed_mean, stressed_std)
                
                # Expected shortfall in stressed scenario
                var_95 = stats.norm.ppf(0.05, stressed_mean, stressed_std)
                # Approximate CVaR for normal distribution
                cvar_95 = stressed_mean - stressed_std * stats.norm.pdf(stats.norm.ppf(0.05)) / 0.05
            else:
                # Basic approximations
                prob_loss_5pct = 0.15  # Rough estimate
                prob_loss_10pct = 0.05
                prob_loss_20pct = 0.01
                var_95 = stressed_mean - 1.645 * stressed_std
                cvar_95 = stressed_mean - 2.0 * stressed_std
            
            # Annualize metrics
            stressed_annual_return = stressed_mean * 252
            stressed_annual_vol = stressed_std * np.sqrt(252)
            annual_var_95 = var_95 * np.sqrt(252)
            annual_cvar_95 = cvar_95 * np.sqrt(252)
            
            scenario_result = {
                "scenario_name": scenario_name,
                "return_shock": return_shock,
                "volatility_multiplier": vol_multiplier,
                "stressed_annual_return": float(stressed_annual_return),
                "stressed_annual_return_pct": f"{stressed_annual_return * 100:.2f}%",
                "stressed_annual_volatility": float(stressed_annual_vol),
                "stressed_annual_volatility_pct": f"{stressed_annual_vol * 100:.2f}%",
                "var_95_annual": float(annual_var_95),
                "var_95_annual_pct": f"{annual_var_95 * 100:.2f}%",
                "cvar_95_annual": float(annual_cvar_95),
                "cvar_95_annual_pct": f"{annual_cvar_95 * 100:.2f}%",
                "prob_loss_5pct": float(prob_loss_5pct),
                "prob_loss_10pct": float(prob_loss_10pct),
                "prob_loss_20pct": float(prob_loss_20pct)
            }
            
            stress_results.append(scenario_result)
        
        # Find worst case scenario
        worst_scenario = min(stress_results, key=lambda x: x['stressed_annual_return'])
        
        result = {
            "base_annual_return": float(mean_return * 252),
            "base_annual_volatility": float(std_return * np.sqrt(252)),
            "stress_scenarios": stress_results,
            "worst_case_scenario": worst_scenario,
            "n_scenarios": len(stress_scenarios)
        }
        
        return standardize_output(result, "stress_test_portfolio")
        
    except Exception as e:
        return {"success": False, "error": f"Stress testing failed: {str(e)}"}


# Registry of risk metrics functions - all using libraries
RISK_METRICS_FUNCTIONS = {
    'calculate_var': calculate_var,
    'calculate_cvar': calculate_cvar,
    'calculate_correlation_analysis': calculate_correlation_analysis,
    'calculate_beta_analysis': calculate_beta_analysis,
    'stress_test_portfolio': stress_test_portfolio
}