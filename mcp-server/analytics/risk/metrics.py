"""Risk metrics and analysis using industry-standard libraries.

This module provides comprehensive risk measurement and analysis functionality including
Value at Risk (VaR), Conditional Value at Risk (CVaR), correlation analysis, beta analysis,
stress testing, and various risk decomposition techniques. All calculations leverage
established libraries from requirements.txt (empyrical, scipy, numpy) to ensure accuracy
and avoid code duplication.

The module supports multiple risk measurement approaches including:
- Historical, parametric, and Cornish-Fisher VaR calculation
- Component and marginal VaR for risk attribution
- Correlation and concentration analysis
- Tail risk and stress testing
- Portfolio risk decomposition and budgeting

Functions are designed to integrate with the financial-analysis-function-library.json
specification and provide standardized outputs for the MCP analytics server.

Example:
    Basic risk analysis workflow:
    
    >>> from mcp.analytics.risk.metrics import calculate_var, calculate_beta_analysis
    >>> import pandas as pd
    >>> returns = pd.Series(...)  # Historical returns data
    >>> var_result = calculate_var(returns, confidence_level=0.05, method="historical")
    >>> print(f"95% VaR: {var_result['var_daily_pct']}")
    
Note:
    All functions return standardized output dictionaries compatible with the
    MCP analytics server architecture and use proven financial risk metrics.
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
    """Calculate Value at Risk (VaR) using multiple methodologies.
    
    Value at Risk estimates the maximum potential loss for a portfolio over a
    specified time horizon at a given confidence level. This function supports
    three different calculation methods: historical simulation, parametric
    (normal distribution), and Cornish-Fisher expansion for non-normal distributions.
    
    Args:
        returns: Historical returns data. Can be provided as pandas Series with
            dates as index, or dictionary with dates as keys and returns as values.
        confidence_level: Confidence level for VaR calculation. Defaults to 0.05
            for 95% VaR (5% tail probability). Common values: 0.01, 0.05, 0.10.
        method: VaR calculation method. Options:
            - "historical": Uses empirical distribution of returns (non-parametric)
            - "parametric": Assumes normal distribution of returns
            - "cornish_fisher": Adjusts for skewness and kurtosis using Cornish-Fisher expansion
            Defaults to "historical".
            
    Returns:
        Dict[str, Any]: VaR analysis results including:
            - var_daily/var_annual: Daily and annualized VaR values
            - confidence_level: Confidence level used in calculations
            - method: VaR calculation method applied
            - violations: Number of actual returns below VaR threshold
            - violation_rate: Percentage of violations vs expected
            - backtesting_ratio: Ratio of actual vs expected violations (for model validation)
            
    Raises:
        Exception: If VaR calculation fails due to invalid inputs or computation errors.
        
    Example:
        >>> import pandas as pd
        >>> returns = pd.Series([-0.02, 0.01, -0.015, 0.005, -0.03, ...])  # Daily returns
        >>> var_result = calculate_var(returns, confidence_level=0.05, method="historical")
        >>> print(f"95% Daily VaR: {var_result['var_daily_pct']}")
        >>> print(f"Violations: {var_result['violations']} out of {len(returns)} observations")
        >>> print(f"Backtesting ratio: {var_result['backtesting_ratio']:.2f}")
        
    Note:
        - Historical method uses actual return percentiles (most conservative)
        - Parametric method assumes returns are normally distributed
        - Cornish-Fisher adjusts normal distribution for higher moments
        - Backtesting ratio should be close to 1.0 for well-calibrated models
        - Annual VaR calculated using √252 scaling factor
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
    """Calculate Conditional Value at Risk (Expected Shortfall).
    
    Conditional Value at Risk (CVaR), also known as Expected Shortfall, measures
    the average loss in the worst-case scenarios beyond the VaR threshold. It provides
    a more comprehensive risk measure than VaR by considering the severity of tail losses,
    not just their probability.
    
    Args:
        returns: Historical returns data. Can be provided as pandas Series with
            dates as index, or dictionary with dates as keys and returns as values.
        confidence_level: Confidence level for CVaR calculation. Defaults to 0.05
            for 95% CVaR (average loss in worst 5% of scenarios). Should match
            VaR confidence level for meaningful comparison.
            
    Returns:
        Dict[str, Any]: CVaR analysis results including:
            - cvar_daily/cvar_annual: Daily and annualized CVaR values
            - var_daily: Corresponding VaR value for comparison
            - cvar_var_ratio: Ratio of CVaR to VaR (measures tail risk severity)
            - confidence_level: Confidence level used in calculations
            
    Raises:
        Exception: If CVaR calculation fails due to invalid inputs.
        
    Example:
        >>> import pandas as pd
        >>> returns = pd.Series([-0.02, 0.01, -0.015, 0.005, -0.03, ...])  # Daily returns
        >>> cvar_result = calculate_cvar(returns, confidence_level=0.05)
        >>> print(f"95% CVaR: {cvar_result['cvar_daily_pct']}")
        >>> print(f"95% VaR: {cvar_result['var_daily_pct']}")
        >>> print(f"CVaR/VaR ratio: {cvar_result['cvar_var_ratio']:.2f}")
        
    Note:
        - CVaR is always more conservative (higher loss) than VaR
        - CVaR/VaR ratio > 1.2 suggests significant tail risk
        - CVaR is a coherent risk measure (satisfies all coherence axioms)
        - Uses empyrical library for consistent calculation with industry standards
        - Annual CVaR calculated using √252 scaling factor
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


def calculate_correlation_analysis(returns: Union[pd.DataFrame, Dict[str, Any], List[List[float]]],
                                  method: str = "pearson") -> Dict[str, Any]:
    """Calculate comprehensive correlation analysis for multiple assets.
    
    This function computes correlation matrices and provides detailed analysis
    of relationships between assets including highest/lowest correlations,
    average correlation levels, and diversification implications. Supports
    multiple correlation methods to handle different data characteristics.
    
    Args:
        returns: Multi-asset return data. Can be provided as:
            - pandas DataFrame: Assets as columns, dates as index
            - Dictionary: Asset names as keys, return series as values
            - List of lists: Each inner list contains returns for one asset
        method: Correlation calculation method. Options:
            - "pearson": Linear correlation (assumes normal distributions)
            - "spearman": Rank correlation (non-parametric, handles outliers)
            - "kendall": Rank correlation (robust to outliers, smaller samples)
            Defaults to "pearson".
            
    Returns:
        Dict[str, Any]: Correlation analysis results including:
            - correlation_matrix: Full correlation matrix between all assets
            - pairwise_correlations: List of all unique asset pair correlations
            - highest_correlation: Asset pair with strongest positive correlation
            - lowest_correlation: Asset pair with strongest negative correlation
            - average_correlation: Mean correlation across all asset pairs
            - diversification_ratio: 1 - |average_correlation| (higher = better diversification)
            - n_assets: Number of assets analyzed
            - n_observations: Number of time periods used
            
    Raises:
        ValueError: If fewer than 2 assets provided.
        Exception: If correlation analysis fails due to data issues.
        
    Example:
        >>> import pandas as pd
        >>> returns_df = pd.DataFrame({
        ...     'STOCKS': [0.01, -0.02, 0.015, ...],
        ...     'BONDS': [-0.005, 0.008, -0.002, ...],
        ...     'GOLD': [0.002, 0.012, -0.008, ...]
        ... })
        >>> corr_analysis = calculate_correlation_analysis(returns_df, method="pearson")
        >>> print(f"Average correlation: {corr_analysis['average_correlation']:.3f}")
        >>> print(f"Diversification ratio: {corr_analysis['diversification_ratio']:.3f}")
        >>> print(f"Highest correlation: {corr_analysis['highest_correlation']}")
        
    Note:
        - Pearson correlation measures linear relationships
        - Spearman correlation captures monotonic relationships
        - Kendall correlation is more robust but computationally intensive
        - Diversification benefits decrease as average correlation increases
        - NaN values are automatically removed before calculation
    """
    try:
        if isinstance(returns, dict):
            returns_df = pd.DataFrame(returns)
        elif isinstance(returns, list):
            # Handle list of lists (each list is an asset's returns)
            if len(returns) > 0 and isinstance(returns[0], list):
                returns_df = pd.DataFrame(returns).T  # Transpose so each column is an asset
                returns_df.columns = [f"Asset_{i}" for i in range(len(returns))]
            else:
                # Single list of returns - convert to single column
                returns_df = pd.DataFrame({"Asset_0": returns})
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
    """Calculate comprehensive beta analysis relative to market benchmark.
    
    Beta measures the sensitivity of an asset's returns to market movements.
    This function calculates beta along with alpha, correlation, tracking error,
    and other measures that help assess systematic risk and relative performance
    characteristics using the empyrical library for proven calculations.
    
    Args:
        asset_returns: Asset return series. Can be provided as pandas Series
            with dates as index, or dictionary with dates as keys and returns as values.
        market_returns: Market benchmark return series. Must have overlapping
            periods with asset_returns. Can be provided as pandas Series or dictionary.
        risk_free_rate: Annual risk-free rate used for alpha and excess return
            calculations. Defaults to 0.02 (2%).
            
    Returns:
        Dict[str, Any]: Beta analysis results including:
            - beta: Systematic risk coefficient (market sensitivity)
            - alpha: Risk-adjusted excess return (Jensen's alpha)
            - correlation: Linear correlation with market
            - r_squared: Proportion of variance explained by market (beta²×correlation²)
            - tracking_error: Standard deviation of excess returns (annualized)
            - information_ratio: Excess return divided by tracking error
            - beta_interpretation: Classification (high/moderate/low/negative beta)
            - n_observations: Number of overlapping return periods
            
    Raises:
        Exception: If beta analysis fails due to insufficient data or calculation errors.
        
    Example:
        >>> import pandas as pd
        >>> asset_rets = pd.Series([0.02, -0.01, 0.015, -0.008, ...])  # Stock returns
        >>> market_rets = pd.Series([0.015, -0.005, 0.01, -0.002, ...])  # Market returns
        >>> beta_analysis = calculate_beta_analysis(asset_rets, market_rets, risk_free_rate=0.03)
        >>> print(f"Beta: {beta_analysis['beta']:.2f}")
        >>> print(f"Alpha: {beta_analysis['alpha_pct']}")
        >>> print(f"R-squared: {beta_analysis['r_squared']:.3f}")
        >>> print(f"Risk profile: {beta_analysis['beta_interpretation']}")
        
    Note:
        - Beta > 1.2: High beta (aggressive, more volatile than market)
        - Beta 0.8-1.2: Moderate beta (similar volatility to market)
        - Beta < 0.8: Low beta (defensive, less volatile than market)
        - Beta < 0: Negative beta (tends to move opposite to market)
        - Alpha > 0 indicates outperformance after adjusting for systematic risk
        - R-squared shows how much of asset's movement is explained by market
        - Uses empyrical library for consistent industry-standard calculations
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
    """Conduct comprehensive portfolio stress testing under adverse scenarios.
    
    Stress testing evaluates portfolio performance under extreme market conditions
    by applying various shock scenarios to historical return characteristics.
    This function calculates expected returns, volatility, VaR, and loss probabilities
    under each stress scenario using scipy for statistical analysis.
    
    Args:
        returns: Portfolio return series. Can be provided as pandas Series with
            dates as index, or dictionary with dates as keys and returns as values.
        stress_scenarios: Optional list of custom stress scenarios. If not provided,
            uses default scenarios (market crash, moderate correction, high volatility,
            low growth). Each scenario should be a dictionary with:
            - "name": Scenario description
            - "return_shock": Additional return impact (e.g., -0.20 for 20% loss)
            - "volatility_multiplier": Volatility scaling factor (e.g., 2.0 for double volatility)
            
    Returns:
        Dict[str, Any]: Stress test results including:
            - base_annual_return/volatility: Original portfolio characteristics
            - stress_scenarios: Detailed results for each scenario
            - worst_case_scenario: Scenario with lowest expected return
            - n_scenarios: Number of scenarios tested
            
        Each scenario result includes:
            - stressed_annual_return/volatility: Adjusted performance metrics
            - var_95_annual/cvar_95_annual: Risk measures under stress
            - prob_loss_X%: Probability of various loss thresholds
            
    Raises:
        Exception: If stress testing fails due to invalid inputs or calculation errors.
        
    Example:
        >>> import pandas as pd
        >>> portfolio_returns = pd.Series([0.001, -0.015, 0.008, ...])  # Daily returns
        >>> # Custom stress scenario
        >>> custom_scenarios = [
        ...     {"name": "Financial Crisis", "return_shock": -0.30, "volatility_multiplier": 3.0},
        ...     {"name": "Inflation Spike", "return_shock": -0.15, "volatility_multiplier": 1.8}
        ... ]
        >>> stress_results = stress_test_portfolio(portfolio_returns, custom_scenarios)
        >>> worst_case = stress_results['worst_case_scenario']
        >>> print(f"Worst scenario: {worst_case['scenario_name']}")
        >>> print(f"Expected return under stress: {worst_case['stressed_annual_return_pct']}")
        
    Note:
        - Default scenarios cover major market stress types
        - Uses normal distribution assumptions for probability calculations
        - Return shocks are applied as additive adjustments to daily returns
        - Volatility multipliers scale the historical standard deviation
        - Probability calculations assume stressed returns follow normal distribution
        - Results help assess portfolio resilience and potential tail losses
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
    """Calculate rolling volatility with specified window for time-series volatility analysis.
    
    Rolling volatility measures how the volatility of returns changes over time by
    calculating the standard deviation within a moving window. This function provides
    annualized volatility estimates that help identify periods of market stress,
    volatility clustering, and regime changes in financial time series.
    
    The rolling volatility calculation uses a backward-looking window to compute
    the standard deviation of returns at each point in time, then annualizes the
    result using the square root of time scaling (√252 for daily data).
    
    Args:
        returns (Union[pd.Series, Dict[str, Any]]): Return series for volatility analysis.
            Can be provided as pandas Series with datetime index, or dictionary with
            dates as keys and returns as values. Should contain decimal returns
            (e.g., 0.01 for 1%, -0.02 for -2%).
        window (int, optional): Rolling window size in periods for volatility calculation.
            Defaults to 30. Common values: 30 (monthly), 252 (annual), 21 (business month).
            Larger windows provide smoother estimates but less sensitivity to recent changes.
            
    Returns:
        pd.Series: Rolling volatility series with annualized volatility values.
            Index matches input returns (excluding first window-1 observations).
            Values represent annualized standard deviation of returns within each window.
            NaN values are automatically dropped from the beginning of the series.
            
    Raises:
        ValueError: If rolling volatility calculation fails due to invalid data or parameters.
        
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Create sample return data with volatility clustering
        >>> dates = pd.date_range('2023-01-01', periods=252, freq='D')
        >>> np.random.seed(42)
        >>> # First half: low volatility period
        >>> low_vol_returns = np.random.normal(0.0008, 0.01, 126)
        >>> # Second half: high volatility period  
        >>> high_vol_returns = np.random.normal(0.0005, 0.025, 126)
        >>> returns = pd.Series(np.concatenate([low_vol_returns, high_vol_returns]), index=dates)
        >>> 
        >>> # Calculate 30-day rolling volatility
        >>> rolling_vol = calculate_rolling_volatility(returns, window=30)
        >>> print(f"Average early-period volatility: {rolling_vol.iloc[:50].mean():.3f}")
        >>> print(f"Average late-period volatility: {rolling_vol.iloc[-50:].mean():.3f}")
        >>> 
        >>> # Plot volatility over time
        >>> import matplotlib.pyplot as plt
        >>> rolling_vol.plot(title='30-Day Rolling Volatility (Annualized)')
        >>> plt.ylabel('Annualized Volatility')
        >>> plt.show()
        
    Note:
        - Annualization assumes 252 trading days per year (standard for daily data)
        - For other frequencies, adjust annualization factor accordingly
        - Early observations (first window-1 periods) will be NaN
        - Volatility clustering often appears in financial time series
        - Higher rolling volatility indicates periods of market stress or uncertainty
        - Can be used for dynamic risk management and volatility-based position sizing
        - Results are compatible with GARCH models and volatility forecasting
        - Uses pandas rolling() function for computational efficiency
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
    """Calculate beta coefficient measuring systematic risk relative to market movements.
    
    Beta (β) is a fundamental measure of systematic risk that quantifies how much
    a security's returns tend to move relative to market returns. A beta of 1.0 means
    the security moves in line with the market, while beta > 1.0 indicates higher
    volatility than the market, and beta < 1.0 suggests lower volatility.
    
    Beta is calculated as the covariance between stock and market returns divided
    by the variance of market returns: β = Cov(stock, market) / Var(market).
    This provides a standardized measure of systematic risk exposure.
    
    Args:
        stock_returns (Union[pd.Series, Dict[str, Any]]): Individual stock or asset
            return series. Can be provided as pandas Series with datetime index,
            or dictionary with dates as keys and returns as values. Returns should
            be in decimal format (e.g., 0.02 for 2%).
        market_returns (Union[pd.Series, Dict[str, Any]]): Market benchmark return
            series (e.g., S&P 500, market index). Must have overlapping periods
            with stock_returns for meaningful calculation. Same format as stock_returns.
            
    Returns:
        float: Beta coefficient representing systematic risk:
            - β = 1.0: Moves exactly with market (systematic risk = market risk)
            - β > 1.0: More volatile than market (amplifies market movements)
            - β < 1.0: Less volatile than market (dampens market movements) 
            - β = 0.0: No correlation with market (no systematic risk)
            - β < 0.0: Moves opposite to market (rare, often temporary)
            
    Raises:
        ValueError: If beta calculation fails due to data alignment issues,
            insufficient data, or zero market variance.
        
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Create sample market and stock return data
        >>> dates = pd.date_range('2023-01-01', periods=252, freq='D')
        >>> np.random.seed(42)
        >>> market_rets = pd.Series(np.random.normal(0.0008, 0.015, 252), index=dates)
        >>> 
        >>> # High-beta stock (amplifies market moves)
        >>> high_beta_stock = pd.Series([
        ...     market_ret * 1.5 + np.random.normal(0, 0.005) 
        ...     for market_ret in market_rets
        ... ], index=dates)
        >>> 
        >>> # Low-beta stock (dampens market moves)
        >>> low_beta_stock = pd.Series([
        ...     market_ret * 0.6 + np.random.normal(0, 0.003) 
        ...     for market_ret in market_rets
        ... ], index=dates)
        >>> 
        >>> # Calculate betas
        >>> high_beta = calculate_beta(high_beta_stock, market_rets)
        >>> low_beta = calculate_beta(low_beta_stock, market_rets)
        >>> 
        >>> print(f"High-beta stock β: {high_beta:.2f}")  # Should be around 1.5
        >>> print(f"Low-beta stock β: {low_beta:.2f}")    # Should be around 0.6
        >>> 
        >>> # Interpretation
        >>> if high_beta > 1.2:
        ...     print("High-beta stock is aggressive (high systematic risk)")
        >>> if low_beta < 0.8:
        ...     print("Low-beta stock is defensive (low systematic risk)")
        
    Note:
        - Beta measures only systematic (market-related) risk, not total risk
        - Calculated using historical data; future beta may differ
        - Beta = 0 doesn't mean risk-free; idiosyncratic risk may still exist
        - Market benchmark choice affects beta calculation significantly
        - Rolling beta calculations can reveal changing risk characteristics
        - Beta is a key input for CAPM (Capital Asset Pricing Model)
        - High-beta stocks tend to outperform in bull markets, underperform in bear markets
        - Defensive sectors typically have lower betas than growth/cyclical sectors
        - Uses covariance/variance calculation for numerical stability
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
    """Calculate Pearson correlation coefficient between two financial time series.
    
    Correlation measures the linear relationship between two variables, ranging from
    -1 to +1. In finance, correlation analysis helps understand how different assets
    move relative to each other, which is critical for portfolio diversification,
    risk management, and asset allocation decisions.
    
    A correlation of +1 indicates perfect positive linear relationship (assets move
    together), -1 indicates perfect negative relationship (assets move opposite),
    and 0 indicates no linear relationship (assets are uncorrelated).
    
    Args:
        series1 (Union[pd.Series, Dict[str, Any]]): First time series for correlation
            analysis. Can be provided as pandas Series with datetime index, or
            dictionary with dates as keys and values. Typically represents returns,
            prices, or other financial metrics.
        series2 (Union[pd.Series, Dict[str, Any]]): Second time series for correlation
            analysis. Must have overlapping time periods with series1 for meaningful
            calculation. Same format as series1.
            
    Returns:
        float: Pearson correlation coefficient between the two series:
            - +1.0: Perfect positive correlation (move together exactly)
            - +0.7 to +0.99: Strong positive correlation 
            - +0.3 to +0.69: Moderate positive correlation
            - -0.3 to +0.29: Weak correlation (relatively independent)
            - -0.69 to -0.31: Moderate negative correlation
            - -0.99 to -0.7: Strong negative correlation
            - -1.0: Perfect negative correlation (move opposite exactly)
            
    Raises:
        ValueError: If correlation calculation fails due to data alignment issues,
            insufficient overlapping data, or invalid input formats.
        
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Create sample time series data
        >>> dates = pd.date_range('2023-01-01', periods=100, freq='D')
        >>> 
        >>> # Positively correlated series (tech stocks)
        >>> stock_a = pd.Series(np.random.normal(0.001, 0.02, 100), index=dates)
        >>> stock_b = pd.Series([
        ...     ret_a * 0.8 + np.random.normal(0, 0.01) 
        ...     for ret_a in stock_a
        ... ], index=dates)
        >>> 
        >>> # Negatively correlated series (stocks vs bonds)
        >>> bonds = pd.Series([
        ...     -ret_a * 0.3 + np.random.normal(0.0002, 0.005) 
        ...     for ret_a in stock_a
        ... ], index=dates)
        >>> 
        >>> # Calculate correlations
        >>> tech_correlation = calculate_correlation(stock_a, stock_b)
        >>> stock_bond_correlation = calculate_correlation(stock_a, bonds)
        >>> 
        >>> print(f"Tech stocks correlation: {tech_correlation:.3f}")  # Should be ~0.8
        >>> print(f"Stock-bond correlation: {stock_bond_correlation:.3f}")  # Should be ~-0.3
        >>> 
        >>> # Interpretation for portfolio construction
        >>> if abs(tech_correlation) > 0.7:
        ...     print("High correlation - limited diversification benefit")
        >>> if stock_bond_correlation < -0.2:
        ...     print("Negative correlation - good for diversification")
        
    Note:
        - Only measures linear relationships; non-linear relationships may exist
        - Correlation doesn't imply causation between the variables
        - Financial correlations can change over time (correlation instability)
        - Extreme market events often increase correlations temporarily
        - Low correlation (near 0) is generally preferred for diversification
        - Uses Pearson correlation (assumes normal distributions)
        - For non-normal data, consider Spearman or Kendall correlations
        - Missing values are automatically excluded from calculation
        - Essential for modern portfolio theory and risk parity strategies
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
    """Calculate pairwise correlation matrix for multiple financial time series.
    
    A correlation matrix provides a comprehensive view of linear relationships between
    multiple assets or variables simultaneously. Each cell (i,j) contains the correlation
    coefficient between series i and series j. This matrix is essential for portfolio
    construction, risk analysis, and understanding diversification benefits across assets.
    
    The resulting matrix is symmetric (correlations are the same both ways) with 1.0s
    along the diagonal (perfect self-correlation) and correlation coefficients ranging
    from -1 to +1 in off-diagonal elements.
    
    Args:
        series_array (List[Union[pd.Series, Dict[str, Any]]]): List of time series
            for correlation analysis. Each element can be a pandas Series with datetime
            index or dictionary with dates as keys. All series should represent similar
            metrics (e.g., all returns, all prices) for meaningful comparison.
            Series will be automatically aligned to common time periods.
            
    Returns:
        pd.DataFrame: Square correlation matrix where:
            - Rows and columns represent the input series (indexed as series_0, series_1, etc.)
            - Diagonal elements = 1.0 (perfect self-correlation)
            - Off-diagonal elements = correlation coefficients between pairs
            - Matrix is symmetric (correlation(A,B) = correlation(B,A))
            - Index and columns labeled with series names if available, otherwise numbered
            
    Raises:
        ValueError: If correlation matrix calculation fails due to insufficient data,
            incompatible series formats, or fewer than 2 series provided.
            
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Create sample asset return series
        >>> dates = pd.date_range('2023-01-01', periods=252, freq='D')
        >>> np.random.seed(42)
        >>> 
        >>> # Tech stocks (high correlation with each other)
        >>> tech_base = np.random.normal(0.001, 0.02, 252)
        >>> aapl_returns = pd.Series(tech_base + np.random.normal(0, 0.005, 252), index=dates, name='AAPL')
        >>> msft_returns = pd.Series(tech_base * 0.9 + np.random.normal(0, 0.008, 252), index=dates, name='MSFT')
        >>> 
        >>> # Bonds (low/negative correlation with stocks)
        >>> bond_returns = pd.Series([-r * 0.2 + np.random.normal(0.0001, 0.003, 252) 
        ...                          for r in tech_base], index=dates, name='Bonds')
        >>> 
        >>> # Gold (moderate correlation, flight-to-safety asset)
        >>> gold_returns = pd.Series([np.random.normal(0.0002, 0.015, 252)[i] + 
        ...                          (0.5 if tech_base[i] < -0.02 else 0) 
        ...                          for i in range(252)], index=dates, name='Gold')
        >>> 
        >>> # Calculate correlation matrix
        >>> series_list = [aapl_returns, msft_returns, bond_returns, gold_returns]
        >>> corr_matrix = calculate_correlation_matrix(series_list)
        >>> 
        >>> print("Correlation Matrix:")
        >>> print(corr_matrix.round(3))
        >>> print(f"\\nTech stocks correlation: {corr_matrix.loc['AAPL', 'MSFT']:.3f}")
        >>> print(f"Stock-bond correlation: {corr_matrix.loc['AAPL', 'Bonds']:.3f}")
        >>> 
        >>> # Identify diversification opportunities
        >>> import numpy as np
        >>> off_diagonal = corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)]
        >>> avg_correlation = np.mean(off_diagonal)
        >>> print(f"Average pairwise correlation: {avg_correlation:.3f}")
        >>> 
        >>> if avg_correlation < 0.3:
        ...     print("Good diversification potential (low average correlation)")
        >>> elif avg_correlation > 0.7:
        ...     print("Limited diversification (high correlation)")
        
    Note:
        - Uses Pearson correlation coefficients (measures linear relationships)
        - Missing values are automatically handled via pairwise deletion
        - All input series are aligned to common time periods before calculation
        - Matrix can be used directly in portfolio optimization algorithms
        - High correlations (>0.7) indicate limited diversification benefits
        - Negative correlations (<-0.3) provide natural hedging opportunities
        - Correlation matrices are used in risk parity and mean-variance optimization
        - Consider using robust correlation measures for non-normal return distributions
        - Large matrices (>50 assets) may have numerical stability issues
        - Essential input for Modern Portfolio Theory and CAPM calculations
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
    """Calculate skewness measuring asymmetry of return distribution.
    
    Skewness quantifies the asymmetry of a probability distribution around its mean.
    In finance, skewness helps assess tail risk and return distribution characteristics.
    Positive skewness indicates more frequent small losses and occasional large gains,
    while negative skewness suggests more frequent small gains and occasional large losses.
    
    Args:
        returns (Union[pd.Series, Dict[str, Any]]): Return series for skewness analysis.
            Can be pandas Series with datetime index or dictionary format.
            
    Returns:
        float: Skewness coefficient:
            - = 0: Symmetric distribution (normal distribution)
            - > 0: Positive skew (right tail longer, occasional large gains)
            - < 0: Negative skew (left tail longer, occasional large losses)
            - |skew| > 1: Highly skewed distribution
            
    Note:
        - Negative skewness often observed in equity returns (crash risk)
        - Positive skewness may indicate momentum or bubble patterns
        - Uses scipy.stats.skew for robust calculation
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
    """Calculate excess kurtosis measuring tail thickness of return distribution.
    
    Kurtosis measures the "tailedness" of a probability distribution. Excess kurtosis
    compares to normal distribution (kurtosis=3). High kurtosis indicates fat tails
    and higher probability of extreme events, crucial for risk management.
    
    Args:
        returns (Union[pd.Series, Dict[str, Any]]): Return series for kurtosis analysis.
            
    Returns:
        float: Excess kurtosis coefficient:
            - = 0: Normal distribution tail thickness
            - > 0: Fat tails (higher extreme event probability)
            - < 0: Thin tails (lower extreme event probability)
            - > 3: Significantly fat tails (high tail risk)
            
    Note:
        - Financial returns typically exhibit positive excess kurtosis
        - High kurtosis suggests higher crash/boom probability than normal distribution
        - Uses scipy.stats.kurtosis with Fisher=True (excess kurtosis)
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
    """Calculate specified percentile for risk and performance analysis.
    
    Percentiles are essential for risk measurement, showing the value below which
    a certain percentage of observations fall. Commonly used for VaR calculation,
    performance benchmarking, and outlier identification.
    
    Args:
        data (Union[pd.Series, Dict[str, Any], List[float]]): Data for percentile calculation.
        percentile (float): Percentile to calculate (0-100). Common values:
            - 5th percentile: Bottom 5% threshold (VaR calculation)
            - 25th percentile: First quartile
            - 50th percentile: Median
            - 95th percentile: Top 5% threshold
            
    Returns:
        float: Percentile value representing the threshold.
        
    Note:
        - Used extensively in VaR and stress testing
        - 5th percentile often represents worst-case scenarios
        - 95th percentile represents best-case scenarios
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
    """Calculate Herfindahl-Hirschman Index measuring portfolio concentration.
    
    HHI measures market concentration by summing squared market shares (weights).
    In portfolio context, it quantifies how concentrated holdings are. Lower values
    indicate better diversification, higher values suggest concentration risk.
    
    Args:
        weights (Union[pd.Series, Dict[str, Any], List[float]]): Portfolio weights.
            Automatically normalized to sum to 1.0.
            
    Returns:
        float: Herfindahl index:
            - 1/N (equal weights): Well diversified portfolio
            - Approaching 1.0: Highly concentrated portfolio
            - = 1.0: Single asset portfolio (maximum concentration)
            
    Note:
        - HHI = Σ(wi²) where wi are normalized weights
        - Lower HHI generally indicates better diversification
        - Regulatory agencies use HHI for market concentration analysis
        - Effective number of assets ≈ 1/HHI
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
    """Calculate Treynor ratio measuring risk-adjusted return per unit of systematic risk.
    
    The Treynor ratio evaluates portfolio performance by comparing excess return
    to systematic risk (beta). Unlike Sharpe ratio which uses total risk, Treynor
    ratio focuses on market-related risk, making it ideal for comparing diversified
    portfolios where unsystematic risk is minimized.
    
    Formula: Treynor Ratio = (Portfolio Return - Risk-free Rate) / Beta
    
    Args:
        returns (Union[pd.Series, Dict[str, Any]]): Portfolio return series.
        market_returns (Union[pd.Series, Dict[str, Any]]): Market benchmark returns.
        risk_free_rate (float, optional): Annual risk-free rate. Defaults to 0.02 (2%).
            
    Returns:
        float: Treynor ratio - higher values indicate better risk-adjusted performance.
            Positive values suggest outperformance after adjusting for market risk.
            
    Note:
        - Higher Treynor ratio indicates better systematic risk-adjusted performance
        - More appropriate than Sharpe ratio for well-diversified portfolios
        - Assumes portfolio is well-diversified (unsystematic risk eliminated)
        - Cannot be calculated if beta is zero
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
    """Calculate portfolio volatility using correlation matrix and individual asset volatilities.
    
    Portfolio volatility calculation incorporates both individual asset volatilities and
    their correlations. The formula accounts for diversification benefits: when assets
    are not perfectly correlated, portfolio risk is less than the weighted average of
    individual risks. This is fundamental to modern portfolio theory.
    
    Formula: σp = √(w'Σw) where w is weights vector and Σ is covariance matrix
    Σ = correlation_matrix * (volatilities ⊗ volatilities)
    
    Args:
        weights (Union[pd.Series, Dict[str, Any], List[float]]): Portfolio allocation weights.
            Should sum to 1.0 (automatically normalized if needed). Order must match
            correlation matrix and volatilities.
        correlation_matrix (Union[pd.DataFrame, Dict[str, Any]]): Asset correlation matrix.
            Must be square matrix with dimensions matching number of assets.
            Diagonal should be 1.0, off-diagonal elements between -1 and 1.
        volatilities (Union[pd.Series, Dict[str, Any], List[float]]): Individual asset
            volatilities (standard deviations). Should be annualized and match the
            time period of desired portfolio volatility.
            
    Returns:
        float: Portfolio volatility (annualized standard deviation). Always non-negative.
            Represents the portfolio's total risk including diversification effects.
            
    Raises:
        ValueError: If dimensions don't match between inputs, or correlation matrix
            is not properly formatted.
            
    Example:
        >>> import numpy as np
        >>> import pandas as pd
        >>> 
        >>> # 3-asset portfolio example
        >>> weights = [0.5, 0.3, 0.2]  # 50% stocks, 30% bonds, 20% commodities
        >>> volatilities = [0.20, 0.08, 0.25]  # 20%, 8%, 25% annual volatility
        >>> 
        >>> # Correlation matrix
        >>> correlation_matrix = pd.DataFrame([
        ...     [1.0, -0.2, 0.3],   # Stocks vs others
        ...     [-0.2, 1.0, 0.1],   # Bonds vs others  
        ...     [0.3, 0.1, 1.0]     # Commodities vs others
        ... ])
        >>> 
        >>> portfolio_vol = calculate_portfolio_volatility(weights, correlation_matrix, volatilities)
        >>> print(f"Portfolio volatility: {portfolio_vol:.3f}")
        >>> 
        >>> # Compare to weighted average (no diversification)
        >>> weighted_avg_vol = sum(w * v for w, v in zip(weights, volatilities))
        >>> print(f"Weighted average volatility: {weighted_avg_vol:.3f}")
        >>> print(f"Diversification benefit: {weighted_avg_vol - portfolio_vol:.3f}")
        >>> 
        >>> # Diversification ratio
        >>> div_ratio = weighted_avg_vol / portfolio_vol
        >>> print(f"Diversification ratio: {div_ratio:.2f}")
        
    Note:
        - Portfolio volatility is always ≤ weighted average volatility (diversification benefit)
        - Perfect positive correlation (ρ=1) gives portfolio volatility = weighted average
        - Perfect negative correlation can theoretically reduce portfolio volatility to zero
        - Negative correlations provide the greatest diversification benefits
        - Essential for mean-variance optimization and efficient frontier construction
        - Assumes returns are normally distributed and correlations are stable
        - Used in risk budgeting and portfolio risk management
        - Formula is exact for linear portfolios (no options or derivatives)
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
    """Calculate Value at Risk contribution by portfolio component.
    
    Component VaR decomposes total portfolio VaR into contributions from each asset,
    helping identify which positions contribute most to tail risk. This is essential
    for risk budgeting and position sizing decisions.
    
    Formula: Component VaRi = weightᵢ × Marginal VaRᵢ
    where Marginal VaRᵢ = ∂(Portfolio VaR)/∂weightᵢ
    
    Args:
        weights (Union[pd.Series, Dict[str, Any], List[float]]): Portfolio weights.
        returns (Union[pd.DataFrame, Dict[str, Any]]): Multi-asset return matrix.
        confidence (float): Confidence level (0.05 for 95% VaR).
            
    Returns:
        List[float]: Component VaR contributions for each asset.
            Sum of components equals total portfolio VaR.
            
    Note:
        - Sum of component VaRs equals total portfolio VaR
        - Larger absolute values indicate higher risk contribution
        - Used for risk budgeting and capital allocation
        - Helps identify concentration risks in portfolios
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
    """Calculate marginal Value at Risk for each portfolio position.
    
    Marginal VaR measures how much portfolio VaR would change if a position's
    weight increased by a small amount. This helps optimize portfolio risk
    allocation and identify positions with highest risk impact per unit weight.
    
    Formula: Marginal VaRᵢ = ∂(Portfolio VaR)/∂weightᵢ
    Calculated using numerical differentiation with small weight perturbations.
    
    Args:
        weights (Union[pd.Series, Dict[str, Any], List[float]]): Portfolio weights.
        returns (Union[pd.DataFrame, Dict[str, Any]]): Multi-asset return matrix.
        confidence (float): Confidence level for VaR calculation.
            
    Returns:
        List[float]: Marginal VaR for each position.
            Positive values indicate VaR increases with position size.
            
    Note:
        - Higher marginal VaR indicates position adds more risk per unit weight
        - Used in risk-adjusted position sizing and portfolio optimization
        - Essential for risk parity and risk budgeting strategies
        - Calculated via numerical differentiation (finite differences)
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
    """Calculate risk budget allocation showing each asset's risk contribution percentage.
    
    Risk budgeting allocates portfolio risk rather than capital across assets.
    This approach ensures each position contributes a target percentage to total
    portfolio risk, leading to more balanced risk exposure than traditional
    market-cap weighted approaches.
    
    Formula: Risk Budgetᵢ = |Risk Contributionᵢ| / Σ|Risk Contributionⱼ|
    
    Args:
        weights (Union[pd.Series, Dict[str, Any], List[float]]): Portfolio weights.
        risk_contributions (Union[pd.Series, Dict[str, Any], List[float]]): 
            Risk contributions for each asset (e.g., component VaR values).
            
    Returns:
        List[float]: Risk budget percentages for each asset.
            Values sum to 1.0 and show relative risk contribution.
            
    Note:
        - Risk budget percentages sum to 100% of total portfolio risk
        - Equal risk budgets (1/N) indicate risk parity portfolio
        - Unequal budgets show concentration of risk in certain positions
        - Used in risk parity and equal risk contribution strategies
        - Helps rebalance portfolios based on risk rather than dollar amounts
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
    """Calculate comprehensive tail risk statistics for extreme events.
    
    Tail risk analysis focuses on the statistical properties of extreme negative
    returns (tail events) that exceed a specified threshold. This function provides
    detailed analysis of tail frequency, severity, and distributional characteristics
    to help assess the risk of extreme losses.
    
    Args:
        returns: Historical returns data. Can be provided as pandas Series with
            dates as index, or dictionary with dates as keys and returns as values.
        threshold: Threshold defining tail events (e.g., -0.05 for returns
            worse than -5%). All returns at or below this level are considered
            tail events for analysis.
            
    Returns:
        Dict[str, Any]: Tail risk analysis including:
            - threshold: Threshold value used to define tail events
            - tail_frequency: Proportion of observations in the tail
            - tail_mean: Average return among tail events (expected tail loss)
            - tail_volatility: Standard deviation of tail event returns
            - tail_events_count: Number of tail events observed
            - expected_tail_loss: Mean loss given a tail event occurs
            - tail_skewness/kurtosis: Higher moments of tail distribution
            - total_observations: Total number of return observations
            
    Raises:
        ValueError: If tail risk calculation fails due to data issues.
        
    Example:
        >>> import pandas as pd
        >>> returns = pd.Series([0.01, -0.02, 0.005, -0.08, -0.12, ...])  # Daily returns
        >>> tail_analysis = calculate_tail_risk(returns, threshold=-0.05)
        >>> print(f"Tail frequency: {tail_analysis['tail_frequency_pct']}")
        >>> print(f"Expected tail loss: {tail_analysis['expected_tail_loss_pct']}")
        >>> print(f"Tail events: {tail_analysis['tail_events_count']} out of {tail_analysis['total_observations']}")
        
    Note:
        - Tail frequency shows how often extreme losses occur
        - Expected tail loss provides conditional expectation given tail event
        - Tail volatility measures dispersion of extreme losses
        - Higher tail skewness indicates more extreme outliers in tail
        - Tail kurtosis measures thickness of extreme tail distribution
        - Returns empty statistics if no tail events found in data
        - Useful for stress testing and extreme risk scenario planning
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
    """Calculate Expected Shortfall (Conditional VaR) measuring tail risk severity.
    
    Expected Shortfall (ES) measures the average loss in the worst-case scenarios
    beyond the VaR threshold. Unlike VaR which only gives the threshold, ES quantifies
    the severity of tail losses, providing a more complete picture of tail risk.
    
    Args:
        returns (Union[pd.Series, Dict[str, Any]]): Historical return series.
        confidence (float): Confidence level (e.g., 0.05 for 95% confidence).
            
    Returns:
        float: Expected Shortfall - average loss in worst-case scenarios.
            More negative values indicate higher tail risk.
            
    Note:
        - ES is always more conservative (worse) than VaR
        - Provides expected loss given that VaR threshold is exceeded
        - Also known as Conditional Value at Risk (CVaR)
        - Coherent risk measure (satisfies all mathematical risk axioms)
        - Essential for comprehensive tail risk assessment
    """
    try:
        returns_series = validate_return_data(returns)
        
        # Use empyrical for Expected Shortfall (same as CVaR)
        expected_shortfall = empyrical.conditional_value_at_risk(returns_series, cutoff=confidence)
        
        return float(expected_shortfall)
        
    except Exception as e:
        raise ValueError(f"Expected Shortfall calculation failed: {str(e)}")


def calculate_diversification_ratio(portfolio_vol: float, weighted_avg_vol: float) -> float:
    """Calculate diversification ratio measuring portfolio diversification benefits.
    
    The diversification ratio compares the weighted average volatility of individual
    assets to the actual portfolio volatility. Higher ratios indicate greater
    diversification benefits from correlation effects between assets.
    
    Formula: Diversification Ratio = (Weighted Average Volatility) / (Portfolio Volatility)
    
    Args:
        portfolio_vol (float): Actual portfolio volatility (standard deviation).
        weighted_avg_vol (float): Weighted average of individual asset volatilities.
            
    Returns:
        float: Diversification ratio:
            - = 1.0: No diversification benefit (perfect correlation)
            - > 1.0: Diversification benefit from correlation < 1
            - Higher values indicate better diversification
            - Theoretical maximum depends on correlation structure
            
    Note:
        - Ratio > 1.0 indicates diversification reduces portfolio risk
        - Higher ratios suggest lower average correlations between assets
        - Essential for evaluating portfolio construction effectiveness
        - Used in risk parity and diversification-focused strategies
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


def calculate_downside_correlation(portfolio_returns: Union[pd.Series, Dict[str, Any]], 
                                  benchmark_returns: Union[pd.Series, Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate portfolio correlation with benchmark returns specifically on negative benchmark days.
    
    Downside correlation measures how closely a portfolio moves with its benchmark during
    periods when the benchmark experiences negative returns. This metric is crucial for
    understanding portfolio behavior during market stress and downturns, providing insight
    into downside protection and systematic risk exposure when markets decline.
    
    Unlike traditional correlation which considers all market conditions equally, downside
    correlation focuses specifically on adverse market conditions, making it more relevant
    for risk management and portfolio construction decisions.
    
    Args:
        portfolio_returns (Union[pd.Series, Dict[str, Any]]): Portfolio return series as
            pandas Series with datetime index or dictionary with return values. Values
            should be decimal returns (e.g., 0.02 for 2%, -0.01 for -1%).
        benchmark_returns (Union[pd.Series, Dict[str, Any]]): Benchmark return series with
            same format as portfolio returns. Will be automatically aligned with portfolio
            returns for fair comparison.
    
    Returns:
        Dict[str, Any]: Downside correlation analysis with keys:
            - downside_correlation (float): Correlation coefficient during negative benchmark days
            - total_observations (int): Total number of overlapping return observations
            - negative_benchmark_days (int): Number of days when benchmark was negative
            - negative_days_percentage (str): Percentage of days with negative benchmark returns
            - portfolio_avg_on_negative_days (float): Average portfolio return on negative benchmark days
            - benchmark_avg_on_negative_days (float): Average benchmark return on negative benchmark days
            - portfolio_volatility_downside (float): Portfolio volatility during negative benchmark days
            - benchmark_volatility_downside (float): Benchmark volatility during negative benchmark days
            - beta_downside (float): Portfolio beta calculated only on negative benchmark days
            - success (bool): Whether calculation succeeded
            - function_name (str): Function identifier for tracking
    
    Raises:
        ValueError: If return data cannot be converted to valid return series or alignment fails.
        TypeError: If input data format is invalid or incompatible.
        
    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Create sample portfolio and benchmark return data
        >>> dates = pd.date_range('2023-01-01', periods=252, freq='D')
        >>> benchmark_rets = pd.Series(np.random.normal(0.0005, 0.015, 252), index=dates)
        >>> # Portfolio with higher downside correlation (more risk in downturns)
        >>> portfolio_rets = []
        >>> for bench_ret in benchmark_rets:
        ...     if bench_ret < 0:
        ...         port_ret = bench_ret * 1.3 + np.random.normal(0, 0.005)  # Amplifies losses
        ...     else:
        ...         port_ret = bench_ret * 0.8 + np.random.normal(0, 0.003)  # Moderate gains
        ...     portfolio_rets.append(port_ret)
        >>> portfolio_rets = pd.Series(portfolio_rets, index=dates)
        >>> 
        >>> # Calculate downside correlation
        >>> result = calculate_downside_correlation(portfolio_rets, benchmark_rets)
        >>> print(f"Downside Correlation: {result['downside_correlation']:.3f}")
        >>> print(f"Negative Days: {result['negative_days_percentage']}")
        >>> print(f"Downside Beta: {result['beta_downside']:.3f}")
        >>> print(f"Portfolio avg on bad days: {result['portfolio_avg_on_negative_days_pct']}")
        
    Note:
        - Values closer to 1.0 indicate portfolio closely follows benchmark during downturns
        - Values closer to 0.0 indicate portfolio is less correlated during market stress
        - Negative values indicate portfolio tends to rise when benchmark falls (rare)
        - Downside beta > 1.0 suggests portfolio amplifies benchmark losses
        - Lower downside correlation may indicate better downside protection
        - Only considers periods when benchmark returns are negative
        - Useful for evaluating defensive characteristics and tail risk management
        - Complements traditional correlation analysis by focusing on stress periods
    """
    try:
        portfolio_series = validate_return_data(portfolio_returns)
        benchmark_series = validate_return_data(benchmark_returns)
        
        # Align series to ensure same dates
        portfolio_aligned, benchmark_aligned = align_series(portfolio_series, benchmark_series)
        
        # Filter for negative benchmark days only
        negative_days_mask = benchmark_aligned < 0
        negative_benchmark_days = benchmark_aligned[negative_days_mask]
        negative_portfolio_days = portfolio_aligned[negative_days_mask]
        
        # Check if we have sufficient negative days for analysis
        if len(negative_benchmark_days) < 2:
            return {
                "success": False, 
                "error": "Insufficient negative benchmark days for correlation calculation"
            }
        
        # Calculate downside correlation
        downside_correlation = negative_portfolio_days.corr(negative_benchmark_days)
        
        # Calculate additional downside metrics
        portfolio_avg_negative = negative_portfolio_days.mean()
        benchmark_avg_negative = negative_benchmark_days.mean()
        portfolio_vol_downside = negative_portfolio_days.std()
        benchmark_vol_downside = negative_benchmark_days.std()
        
        # Calculate downside beta (portfolio sensitivity during negative benchmark days)
        covariance_downside = negative_portfolio_days.cov(negative_benchmark_days)
        benchmark_variance_downside = negative_benchmark_days.var()
        beta_downside = covariance_downside / benchmark_variance_downside if benchmark_variance_downside > 0 else 0
        
        result = {
            "downside_correlation": float(downside_correlation) if not pd.isna(downside_correlation) else 0.0,
            "total_observations": len(portfolio_aligned),
            "negative_benchmark_days": len(negative_benchmark_days),
            "negative_days_percentage": f"{len(negative_benchmark_days) / len(portfolio_aligned) * 100:.2f}%",
            "portfolio_avg_on_negative_days": float(portfolio_avg_negative),
            "portfolio_avg_on_negative_days_pct": f"{portfolio_avg_negative * 100:.2f}%",
            "benchmark_avg_on_negative_days": float(benchmark_avg_negative),
            "benchmark_avg_on_negative_days_pct": f"{benchmark_avg_negative * 100:.2f}%",
            "portfolio_volatility_downside": float(portfolio_vol_downside),
            "portfolio_volatility_downside_pct": f"{portfolio_vol_downside * 100:.2f}%",
            "benchmark_volatility_downside": float(benchmark_vol_downside),
            "benchmark_volatility_downside_pct": f"{benchmark_vol_downside * 100:.2f}%",
            "beta_downside": float(beta_downside)
        }
        
        return standardize_output(result, "calculate_downside_correlation")
        
    except Exception as e:
        return {"success": False, "error": f"Downside correlation calculation failed: {str(e)}"}


def calculate_concentration_metrics(weights: Union[pd.Series, Dict[str, Any], List[float]]) -> Dict[str, Any]:
    """Calculate comprehensive portfolio concentration and diversification metrics.
    
    Portfolio concentration analysis measures how equally assets are weighted
    within a portfolio. High concentration increases specific risk, while better
    diversification (lower concentration) can reduce portfolio volatility through
    the benefits of diversification. This function calculates multiple established
    concentration measures.
    
    Args:
        weights: Portfolio allocation weights. Can be provided as pandas Series
            with asset names as index, dictionary mapping asset names to weights,
            or list of weights. Weights will be normalized to sum to 1.
            
    Returns:
        Dict[str, Any]: Concentration analysis including:
            - herfindahl_index: Sum of squared weights (0=perfectly diversified, 1=concentrated)
            - effective_assets: 1/HHI - equivalent number of equally weighted assets
            - concentration_ratio_N: Percentage held in top N positions (1,3,5,10)
            - gini_coefficient: Inequality measure (0=equal weights, 1=maximum inequality)
            - max_weight: Largest individual position size
            - shannon_entropy: Information-theoretic diversity measure
            - total_assets: Number of assets in portfolio
            
    Raises:
        ValueError: If concentration calculation fails due to invalid weights.
        
    Example:
        >>> weights = {'AAPL': 0.30, 'GOOGL': 0.25, 'MSFT': 0.20, 'AMZN': 0.15, 'Others': 0.10}
        >>> concentration = calculate_concentration_metrics(weights)
        >>> print(f"Herfindahl Index: {concentration['herfindahl_index']:.3f}")
        >>> print(f"Effective assets: {concentration['effective_assets']:.1f}")
        >>> print(f"Top 3 concentration: {concentration['concentration_ratio_3_pct']}")
        >>> print(f"Max position: {concentration['max_weight_pct']}")
        
    Note:
        - HHI = 1/N for equally weighted portfolio with N assets
        - HHI approaches 1.0 as portfolio becomes more concentrated
        - Effective assets shows diversification equivalent in equal-weight terms
        - Concentration ratios show cumulative weight in largest positions
        - Gini coefficient borrowed from income inequality measurement
        - Shannon entropy higher when weights are more equally distributed
        - All weights converted to absolute values and normalized
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


# Registry of risk metrics functions - all using proven libraries
RISK_METRICS_FUNCTIONS = {
    'calculate_var': calculate_var,
    'calculate_cvar': calculate_cvar,
    'calculate_correlation_analysis': calculate_correlation_analysis,
    'calculate_beta_analysis': calculate_beta_analysis,
    'calculate_downside_correlation': calculate_downside_correlation,
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