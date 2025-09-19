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
            # Use empyrical - leveraging requirements.txt
            var = empyrical.value_at_risk(returns_series, cutoff=confidence_level)
        
        elif method == "parametric":
            # Use scipy for parametric VaR
            mean = returns_series.mean()
            std = returns_series.std()
            var = stats.norm.ppf(confidence_level, mean, std)
        
        elif method == "cornish_fisher":
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
            # Default to historical method
            var = empyrical.value_at_risk(returns_series, cutoff=confidence_level)
        
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
        
        # Use empyrical - leveraging requirements.txt
        cvar = empyrical.conditional_value_at_risk(returns_series, cutoff=confidence_level)
        var = empyrical.value_at_risk(returns_series, cutoff=confidence_level)
        
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
        
        # Use empyrical - leveraging requirements.txt
        beta = empyrical.beta(asset_aligned, market_aligned)
        alpha = empyrical.alpha(asset_aligned, market_aligned, risk_free=risk_free_rate)
        
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
            "alpha_annualized": float(alpha),
            "alpha_pct": f"{alpha * 100:.2f}%",
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
            
            # Use scipy for scenario analysis
            # Calculate probability of large losses
            prob_loss_5pct = stats.norm.cdf(-0.05, stressed_mean, stressed_std)
            prob_loss_10pct = stats.norm.cdf(-0.10, stressed_mean, stressed_std) 
            prob_loss_20pct = stats.norm.cdf(-0.20, stressed_mean, stressed_std)
            
            # Expected shortfall in stressed scenario
            var_95 = stats.norm.ppf(0.05, stressed_mean, stressed_std)
            # Approximate CVaR for normal distribution
            cvar_95 = stressed_mean - stressed_std * stats.norm.pdf(stats.norm.ppf(0.05)) / 0.05
            
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


def calculate_rolling_volatility(returns: Union[pd.Series, Dict[str, Any]], window: int = 30) -> pd.Series:
    """
    Calculate rolling volatility with specified window.
    
    From financial-analysis-function-library.json time_series_processing category
    Uses pandas rolling calculations for efficiency
    
    Args:
        returns: Return series
        window: Rolling window size
        
    Returns:
        pd.Series: Rolling volatility series (annualized)
    """
    try:
        from ..utils.data_utils import validate_return_data
        
        returns_series = validate_return_data(returns)
        
        # Calculate rolling volatility and annualize
        rolling_vol = returns_series.rolling(window=window).std() * np.sqrt(252)
        
        return rolling_vol.dropna()
        
    except Exception as e:
        raise ValueError(f"Rolling volatility calculation failed: {str(e)}")


def calculate_beta(stock_returns: Union[pd.Series, Dict[str, Any]], 
                   market_returns: Union[pd.Series, Dict[str, Any]]) -> float:
    """
    Calculate beta coefficient vs market.
    
    From financial-analysis-function-library.json time_series_processing category
    Simple beta calculation wrapper around scipy
    
    Args:
        stock_returns: Stock return series
        market_returns: Market return series
        
    Returns:
        float: Beta coefficient
    """
    try:
        from ..utils.data_utils import validate_return_data, align_series
        
        stock_series = validate_return_data(stock_returns)
        market_series = validate_return_data(market_returns)
        
        # Align series
        stock_aligned, market_aligned = align_series(stock_series, market_series)
        
        # Calculate beta using covariance and variance
        covariance = stock_aligned.cov(market_aligned)
        market_variance = market_aligned.var()
        
        beta = covariance / market_variance if market_variance > 0 else 0
        
        return float(beta)
        
    except Exception as e:
        raise ValueError(f"Beta calculation failed: {str(e)}")


def calculate_correlation(series1: Union[pd.Series, Dict[str, Any]], 
                         series2: Union[pd.Series, Dict[str, Any]]) -> float:
    """
    Calculate correlation between two series.
    
    From financial-analysis-function-library.json time_series_processing category
    Simple correlation calculation using pandas
    
    Args:
        series1: First series
        series2: Second series
        
    Returns:
        float: Correlation coefficient
    """
    try:
        from ..utils.data_utils import validate_return_data, align_series
        
        s1 = validate_return_data(series1)
        s2 = validate_return_data(series2)
        
        # Align series
        s1_aligned, s2_aligned = align_series(s1, s2)
        
        # Calculate correlation
        correlation = s1_aligned.corr(s2_aligned)
        
        return float(correlation)
        
    except Exception as e:
        raise ValueError(f"Correlation calculation failed: {str(e)}")


def calculate_correlation_matrix(series_array: List[Union[pd.Series, Dict[str, Any]]]) -> pd.DataFrame:
    """
    Calculate correlation matrix for multiple series.
    
    From financial-analysis-function-library.json time_series_processing category
    Uses pandas correlation matrix calculation
    
    Args:
        series_array: Array of series to calculate correlations
        
    Returns:
        pd.DataFrame: Correlation matrix
    """
    try:
        from ..utils.data_utils import validate_return_data
        
        # Validate and prepare all series
        validated_series = []
        for i, series in enumerate(series_array):
            validated = validate_return_data(series)
            validated.name = f"series_{i}" if validated.name is None else validated.name
            validated_series.append(validated)
        
        # Create DataFrame and calculate correlation matrix
        df = pd.concat(validated_series, axis=1)
        correlation_matrix = df.corr()
        
        return correlation_matrix
        
    except Exception as e:
        raise ValueError(f"Correlation matrix calculation failed: {str(e)}")


def calculate_skewness(returns: Union[pd.Series, Dict[str, Any]]) -> float:
    """
    Calculate skewness of return distribution.
    
    From financial-analysis-function-library.json statistical_analysis category
    Uses scipy for statistical calculations - no code duplication
    
    Args:
        returns: Return series
        
    Returns:
        float: Skewness coefficient
    """
    try:
        from ..utils.data_utils import validate_return_data
        
        returns_series = validate_return_data(returns)
        
        # Use scipy for skewness calculation
        skewness = stats.skew(returns_series.dropna())
        
        return float(skewness)
        
    except Exception as e:
        raise ValueError(f"Skewness calculation failed: {str(e)}")


def calculate_kurtosis(returns: Union[pd.Series, Dict[str, Any]]) -> float:
    """
    Calculate kurtosis of return distribution.
    
    From financial-analysis-function-library.json statistical_analysis category
    Uses scipy for statistical calculations - no code duplication
    
    Args:
        returns: Return series
        
    Returns:
        float: Kurtosis coefficient (excess kurtosis)
    """
    try:
        from ..utils.data_utils import validate_return_data
        
        returns_series = validate_return_data(returns)
        
        # Use scipy for kurtosis calculation (excess kurtosis)
        kurtosis = stats.kurtosis(returns_series.dropna())
        
        return float(kurtosis)
        
    except Exception as e:
        raise ValueError(f"Kurtosis calculation failed: {str(e)}")


def calculate_percentile(data: Union[pd.Series, Dict[str, Any], List[float]], percentile: float) -> float:
    """
    Calculate specified percentile of data.
    
    From financial-analysis-function-library.json statistical_analysis category
    Uses numpy for percentile calculation - no code duplication
    
    Args:
        data: Data series or array
        percentile: Percentile to calculate (0-100)
        
    Returns:
        float: Percentile value
    """
    try:
        if isinstance(data, (list, np.ndarray)):
            data_array = np.array(data)
        elif isinstance(data, dict):
            data_array = np.array(list(data.values()))
        else:
            data_array = data.values if hasattr(data, 'values') else np.array(data)
        
        # Remove NaN values
        data_clean = data_array[~np.isnan(data_array)]
        
        if len(data_clean) == 0:
            raise ValueError("No valid data points for percentile calculation")
        
        # Use numpy percentile
        result = np.percentile(data_clean, percentile)
        
        return float(result)
        
    except Exception as e:
        raise ValueError(f"Percentile calculation failed: {str(e)}")


def calculate_herfindahl_index(weights: Union[pd.Series, Dict[str, Any], List[float]]) -> float:
    """
    Calculate concentration index for portfolio weights.
    
    From financial-analysis-function-library.json statistical_analysis category
    Simple concentration measure using numpy - no code duplication
    
    Args:
        weights: Portfolio weights
        
    Returns:
        float: Herfindahl index (0 = perfectly diversified, 1 = concentrated)
    """
    try:
        if isinstance(weights, (list, np.ndarray)):
            weights_array = np.array(weights)
        elif isinstance(weights, dict):
            weights_array = np.array(list(weights.values()))
        else:
            weights_array = weights.values if hasattr(weights, 'values') else np.array(weights)
        
        # Remove NaN values and ensure positive weights
        weights_clean = weights_array[~np.isnan(weights_array)]
        weights_clean = weights_clean[weights_clean >= 0]
        
        if len(weights_clean) == 0:
            raise ValueError("No valid weights for Herfindahl index calculation")
        
        # Normalize weights to sum to 1
        weights_normalized = weights_clean / weights_clean.sum()
        
        # Calculate Herfindahl index: sum of squared weights
        herfindahl_index = np.sum(weights_normalized ** 2)
        
        return float(herfindahl_index)
        
    except Exception as e:
        raise ValueError(f"Herfindahl index calculation failed: {str(e)}")


def calculate_treynor_ratio(returns: Union[pd.Series, Dict[str, Any]], 
                           market_returns: Union[pd.Series, Dict[str, Any]], 
                           risk_free_rate: float = 0.02) -> float:
    """
    Calculate Treynor ratio.
    
    From financial-analysis-function-library.json statistical_analysis category
    Uses existing beta calculation and empyrical functions - no code duplication
    
    Args:
        returns: Portfolio returns
        market_returns: Market returns
        risk_free_rate: Risk-free rate
        
    Returns:
        float: Treynor ratio
    """
    try:
        from ..utils.data_utils import validate_return_data, align_series
        
        portfolio_returns = validate_return_data(returns)
        market_series = validate_return_data(market_returns)
        
        # Align series
        portfolio_aligned, market_aligned = align_series(portfolio_returns, market_series)
        
        # Calculate beta
        beta = calculate_beta(portfolio_aligned, market_aligned)
        
        if beta == 0:
            raise ValueError("Beta is zero, cannot calculate Treynor ratio")
        
        # Calculate excess return
        portfolio_annual_return = empyrical.annual_return(portfolio_aligned)
        
        excess_return = portfolio_annual_return - risk_free_rate
        
        # Calculate Treynor ratio
        treynor_ratio = excess_return / beta
        
        return float(treynor_ratio)
        
    except Exception as e:
        raise ValueError(f"Treynor ratio calculation failed: {str(e)}")


def calculate_portfolio_volatility(weights: Union[pd.Series, Dict[str, Any], List[float]], 
                                  correlation_matrix: Union[pd.DataFrame, Dict[str, Any]], 
                                  volatilities: Union[pd.Series, Dict[str, Any], List[float]]) -> float:
    """
    Calculate portfolio volatility using correlation matrix.
    
    From financial-analysis-function-library.json risk_analysis category
    Uses numpy for portfolio volatility calculation - no code duplication
    
    Args:
        weights: Portfolio weights
        correlation_matrix: Asset correlation matrix
        volatilities: Individual asset volatilities
        
    Returns:
        float: Portfolio volatility
    """
    try:
        # Convert inputs to numpy arrays
        if isinstance(weights, (list, pd.Series)):
            w = np.array(weights)
        elif isinstance(weights, dict):
            w = np.array(list(weights.values()))
        else:
            w = np.array(weights)
        
        if isinstance(volatilities, (list, pd.Series)):
            vol = np.array(volatilities)
        elif isinstance(volatilities, dict):
            vol = np.array(list(volatilities.values()))
        else:
            vol = np.array(volatilities)
        
        if isinstance(correlation_matrix, dict):
            corr = np.array(list(correlation_matrix.values()))
        elif isinstance(correlation_matrix, pd.DataFrame):
            corr = correlation_matrix.values
        else:
            corr = np.array(correlation_matrix)
        
        # Validate dimensions
        n_assets = len(w)
        if len(vol) != n_assets:
            raise ValueError("Weights and volatilities must have same length")
        if corr.shape != (n_assets, n_assets):
            raise ValueError("Correlation matrix must be square with same dimension as weights")
        
        # Create covariance matrix
        vol_matrix = np.outer(vol, vol)
        cov_matrix = corr * vol_matrix
        
        # Calculate portfolio volatility: sqrt(w' * Cov * w)
        portfolio_variance = np.dot(w, np.dot(cov_matrix, w))
        portfolio_vol = np.sqrt(portfolio_variance)
        
        return float(portfolio_vol)
        
    except Exception as e:
        raise ValueError(f"Portfolio volatility calculation failed: {str(e)}")


def calculate_component_var(weights: Union[pd.Series, Dict[str, Any], List[float]], 
                           returns: Union[pd.DataFrame, Dict[str, Any]], 
                           confidence: float) -> List[float]:
    """
    Calculate VaR contribution by component.
    
    From financial-analysis-function-library.json risk_analysis category
    Uses scipy and numpy for component VaR calculation - no code duplication
    
    Args:
        weights: Portfolio weights
        returns: Multi-asset return matrix
        confidence: Confidence level (e.g., 0.05 for 95% VaR)
        
    Returns:
        List[float]: Component VaR contributions
    """
    try:
        # Convert inputs to appropriate formats
        if isinstance(weights, (list, pd.Series)):
            w = np.array(weights)
        elif isinstance(weights, dict):
            w = np.array(list(weights.values()))
        else:
            w = np.array(weights)
        
        if isinstance(returns, dict):
            returns_df = pd.DataFrame(returns)
        elif isinstance(returns, list):
            returns_df = pd.DataFrame(returns).T
        else:
            returns_df = returns.copy()
        
        # Calculate portfolio returns
        portfolio_returns = (returns_df * w).sum(axis=1)
        
        # Calculate portfolio VaR
        portfolio_var = np.percentile(portfolio_returns, confidence * 100)
        
        # Calculate marginal VaR for each component
        n_assets = len(w)
        marginal_vars = []
        
        epsilon = 0.01  # Small perturbation for numerical derivative
        
        for i in range(n_assets):
            # Create perturbed weights
            w_plus = w.copy()
            w_plus[i] += epsilon
            w_plus = w_plus / w_plus.sum()  # Renormalize
            
            # Calculate perturbed portfolio returns and VaR
            portfolio_returns_plus = (returns_df * w_plus).sum(axis=1)
            var_plus = np.percentile(portfolio_returns_plus, confidence * 100)
            
            # Marginal VaR = (VaR_perturbed - VaR_original) / epsilon
            marginal_var = (var_plus - portfolio_var) / epsilon
            marginal_vars.append(marginal_var)
        
        # Component VaR = weight * marginal VaR
        component_vars = [float(w[i] * marginal_vars[i]) for i in range(n_assets)]
        
        return component_vars
        
    except Exception as e:
        raise ValueError(f"Component VaR calculation failed: {str(e)}")


def calculate_marginal_var(weights: Union[pd.Series, Dict[str, Any], List[float]], 
                          returns: Union[pd.DataFrame, Dict[str, Any]], 
                          confidence: float) -> List[float]:
    """
    Calculate marginal VaR for each position.
    
    From financial-analysis-function-library.json risk_analysis category
    Uses numerical differentiation for marginal VaR - no code duplication
    
    Args:
        weights: Portfolio weights
        returns: Multi-asset return matrix
        confidence: Confidence level
        
    Returns:
        List[float]: Marginal VaR for each position
    """
    try:
        # Convert inputs
        if isinstance(weights, (list, pd.Series)):
            w = np.array(weights)
        elif isinstance(weights, dict):
            w = np.array(list(weights.values()))
        else:
            w = np.array(weights)
        
        if isinstance(returns, dict):
            returns_df = pd.DataFrame(returns)
        elif isinstance(returns, list):
            returns_df = pd.DataFrame(returns).T
        else:
            returns_df = returns.copy()
        
        # Calculate current portfolio VaR
        portfolio_returns = (returns_df * w).sum(axis=1)
        current_var = np.percentile(portfolio_returns, confidence * 100)
        
        # Calculate marginal VaR using numerical differentiation
        epsilon = 0.01
        marginal_vars = []
        
        for i in range(len(w)):
            # Increase weight of asset i by epsilon
            w_perturbed = w.copy()
            w_perturbed[i] += epsilon
            w_perturbed = w_perturbed / w_perturbed.sum()  # Renormalize
            
            # Calculate new portfolio VaR
            perturbed_returns = (returns_df * w_perturbed).sum(axis=1)
            perturbed_var = np.percentile(perturbed_returns, confidence * 100)
            
            # Marginal VaR = derivative of portfolio VaR w.r.t. weight
            marginal_var = (perturbed_var - current_var) / epsilon
            marginal_vars.append(float(marginal_var))
        
        return marginal_vars
        
    except Exception as e:
        raise ValueError(f"Marginal VaR calculation failed: {str(e)}")


def calculate_risk_budget(weights: Union[pd.Series, Dict[str, Any], List[float]], 
                         risk_contributions: Union[pd.Series, Dict[str, Any], List[float]]) -> List[float]:
    """
    Calculate risk budget allocation.
    
    From financial-analysis-function-library.json risk_analysis category
    Simple risk budget calculation using numpy - no code duplication
    
    Args:
        weights: Portfolio weights
        risk_contributions: Risk contributions for each asset
        
    Returns:
        List[float]: Risk budget percentages
    """
    try:
        # Convert to numpy arrays
        if isinstance(weights, (list, pd.Series)):
            w = np.array(weights)
        elif isinstance(weights, dict):
            w = np.array(list(weights.values()))
        else:
            w = np.array(weights)
        
        if isinstance(risk_contributions, (list, pd.Series)):
            rc = np.array(risk_contributions)
        elif isinstance(risk_contributions, dict):
            rc = np.array(list(risk_contributions.values()))
        else:
            rc = np.array(risk_contributions)
        
        if len(w) != len(rc):
            raise ValueError("Weights and risk contributions must have same length")
        
        # Calculate risk budget: risk_contribution / total_risk
        total_risk = np.sum(np.abs(rc))
        
        if total_risk == 0:
            # Equal budget if no risk
            risk_budget = np.ones(len(w)) / len(w)
        else:
            risk_budget = np.abs(rc) / total_risk
        
        return [float(rb) for rb in risk_budget]
        
    except Exception as e:
        raise ValueError(f"Risk budget calculation failed: {str(e)}")


def calculate_tail_risk(returns: Union[pd.Series, Dict[str, Any]], threshold: float) -> Dict[str, Any]:
    """
    Calculate tail risk statistics.
    
    From financial-analysis-function-library.json risk_analysis category
    Uses scipy and numpy for tail risk analysis - no code duplication
    
    Args:
        returns: Return series
        threshold: Threshold for tail definition (e.g., -0.05 for 5% loss)
        
    Returns:
        Dict: Tail risk statistics
    """
    try:
        returns_series = validate_return_data(returns)
        
        # Identify tail events
        tail_events = returns_series[returns_series <= threshold]
        
        if len(tail_events) == 0:
            return {
                "threshold": threshold,
                "tail_frequency": 0.0,
                "tail_mean": 0.0,
                "tail_volatility": 0.0,
                "tail_events_count": 0,
                "expected_tail_loss": 0.0
            }
        
        # Calculate tail statistics
        tail_frequency = len(tail_events) / len(returns_series)
        tail_mean = tail_events.mean()
        tail_volatility = tail_events.std()
        expected_tail_loss = tail_events.mean()  # Expected loss given tail event
        
        # Additional tail risk measures
        tail_skewness = stats.skew(tail_events) if len(tail_events) > 2 else 0.0
        tail_kurtosis = stats.kurtosis(tail_events) if len(tail_events) > 3 else 0.0
        
        result = {
            "threshold": float(threshold),
            "threshold_pct": f"{threshold * 100:.2f}%",
            "tail_frequency": float(tail_frequency),
            "tail_frequency_pct": f"{tail_frequency * 100:.2f}%",
            "tail_mean": float(tail_mean),
            "tail_mean_pct": f"{tail_mean * 100:.2f}%",
            "tail_volatility": float(tail_volatility),
            "tail_volatility_pct": f"{tail_volatility * 100:.2f}%",
            "tail_events_count": len(tail_events),
            "expected_tail_loss": float(expected_tail_loss),
            "expected_tail_loss_pct": f"{expected_tail_loss * 100:.2f}%",
            "tail_skewness": float(tail_skewness),
            "tail_kurtosis": float(tail_kurtosis),
            "total_observations": len(returns_series)
        }
        
        return standardize_output(result, "calculate_tail_risk")
        
    except Exception as e:
        raise ValueError(f"Tail risk calculation failed: {str(e)}")


def calculate_expected_shortfall(returns: Union[pd.Series, Dict[str, Any]], confidence: float) -> float:
    """
    Calculate Expected Shortfall (Conditional VaR).
    
    From financial-analysis-function-library.json risk_analysis category
    Simple wrapper around empyrical CVaR - no code duplication
    
    Args:
        returns: Return series
        confidence: Confidence level
        
    Returns:
        float: Expected Shortfall
    """
    try:
        returns_series = validate_return_data(returns)
        
        # Use empyrical for Expected Shortfall (same as CVaR)
        expected_shortfall = empyrical.conditional_value_at_risk(returns_series, cutoff=confidence)
        
        return float(expected_shortfall)
        
    except Exception as e:
        raise ValueError(f"Expected Shortfall calculation failed: {str(e)}")


def calculate_diversification_ratio(portfolio_vol: float, weighted_avg_vol: float) -> float:
    """
    Calculate diversification ratio.
    
    From financial-analysis-function-library.json risk_analysis category
    Simple diversification ratio calculation - no code duplication
    
    Args:
        portfolio_vol: Portfolio volatility
        weighted_avg_vol: Weighted average of individual asset volatilities
        
    Returns:
        float: Diversification ratio
    """
    try:
        if portfolio_vol <= 0:
            raise ValueError("Portfolio volatility must be positive")
        if weighted_avg_vol <= 0:
            raise ValueError("Weighted average volatility must be positive")
        
        # Diversification ratio = weighted_avg_vol / portfolio_vol
        # Higher ratio = better diversification
        diversification_ratio = weighted_avg_vol / portfolio_vol
        
        return float(diversification_ratio)
        
    except Exception as e:
        raise ValueError(f"Diversification ratio calculation failed: {str(e)}")


def calculate_concentration_metrics(weights: Union[pd.Series, Dict[str, Any], List[float]]) -> Dict[str, Any]:
    """
    Calculate various concentration measures.
    
    From financial-analysis-function-library.json risk_analysis category
    Uses numpy and scipy for concentration analysis - no code duplication
    
    Args:
        weights: Portfolio weights
        
    Returns:
        Dict: Concentration metrics
    """
    try:
        # Convert to numpy array
        if isinstance(weights, (list, pd.Series)):
            w = np.array(weights)
        elif isinstance(weights, dict):
            w = np.array(list(weights.values()))
        else:
            w = np.array(weights)
        
        # Normalize weights to sum to 1
        w = w / w.sum()
        w = np.abs(w)  # Use absolute values
        
        # Sort weights in descending order
        w_sorted = np.sort(w)[::-1]
        n_assets = len(w)
        
        # Herfindahl-Hirschman Index (sum of squared weights)
        hhi = np.sum(w ** 2)
        
        # Effective number of assets
        effective_assets = 1 / hhi if hhi > 0 else n_assets
        
        # Concentration ratios (top N holdings)
        cr_1 = w_sorted[0] if n_assets >= 1 else 0
        cr_3 = np.sum(w_sorted[:3]) if n_assets >= 3 else np.sum(w_sorted)
        cr_5 = np.sum(w_sorted[:5]) if n_assets >= 5 else np.sum(w_sorted)
        cr_10 = np.sum(w_sorted[:10]) if n_assets >= 10 else np.sum(w_sorted)
        
        # Gini coefficient (measure of inequality)
        if n_assets > 1:
            # Sort weights for Gini calculation
            w_gini = np.sort(w)
            index = np.arange(1, n_assets + 1)
            gini = (2 * np.sum(index * w_gini)) / (n_assets * np.sum(w_gini)) - (n_assets + 1) / n_assets
        else:
            gini = 0.0
        
        # Maximum weight
        max_weight = np.max(w)
        
        # Shannon entropy (information-theoretic measure)
        # Higher entropy = lower concentration
        w_nonzero = w[w > 0]
        shannon_entropy = -np.sum(w_nonzero * np.log(w_nonzero)) if len(w_nonzero) > 0 else 0
        
        result = {
            "herfindahl_index": float(hhi),
            "effective_assets": float(effective_assets),
            "concentration_ratio_1": float(cr_1),
            "concentration_ratio_1_pct": f"{cr_1 * 100:.2f}%",
            "concentration_ratio_3": float(cr_3),
            "concentration_ratio_3_pct": f"{cr_3 * 100:.2f}%",
            "concentration_ratio_5": float(cr_5),
            "concentration_ratio_5_pct": f"{cr_5 * 100:.2f}%",
            "concentration_ratio_10": float(cr_10),
            "concentration_ratio_10_pct": f"{cr_10 * 100:.2f}%",
            "gini_coefficient": float(gini),
            "max_weight": float(max_weight),
            "max_weight_pct": f"{max_weight * 100:.2f}%",
            "shannon_entropy": float(shannon_entropy),
            "total_assets": n_assets
        }
        
        return standardize_output(result, "calculate_concentration_metrics")
        
    except Exception as e:
        raise ValueError(f"Concentration metrics calculation failed: {str(e)}")


# Registry of risk metrics functions - all using libraries
RISK_METRICS_FUNCTIONS = {
    'calculate_var': calculate_var,
    'calculate_cvar': calculate_cvar,
    'calculate_correlation_analysis': calculate_correlation_analysis,
    'calculate_beta_analysis': calculate_beta_analysis,
    'stress_test_portfolio': stress_test_portfolio,
    'calculate_rolling_volatility': calculate_rolling_volatility,
    'calculate_beta': calculate_beta,
    'calculate_correlation': calculate_correlation,
    'calculate_correlation_matrix': calculate_correlation_matrix,
    'calculate_skewness': calculate_skewness,
    'calculate_kurtosis': calculate_kurtosis,
    'calculate_percentile': calculate_percentile,
    'calculate_herfindahl_index': calculate_herfindahl_index,
    'calculate_treynor_ratio': calculate_treynor_ratio,
    'calculate_portfolio_volatility': calculate_portfolio_volatility,
    'calculate_component_var': calculate_component_var,
    'calculate_marginal_var': calculate_marginal_var,
    'calculate_risk_budget': calculate_risk_budget,
    'calculate_tail_risk': calculate_tail_risk,
    'calculate_expected_shortfall': calculate_expected_shortfall,
    'calculate_diversification_ratio': calculate_diversification_ratio,
    'calculate_concentration_metrics': calculate_concentration_metrics
}