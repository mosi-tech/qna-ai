"""
Advanced Statistical Indicators

Statistical analysis indicators for technical analysis:
- Linear Regression (slope, intercept, R-squared)
- Standard Error
- Correlation Coefficient
- Z-Score
- Skewness
- Kurtosis
- Percentile Rank
- Beta Coefficient

All functions follow consistent patterns:
- Input: pandas Series or DataFrame with OHLCV data
- Output: pandas Series or DataFrame with calculated indicator values
- Parameters: Standard parameter names with sensible defaults
"""

import pandas as pd
import numpy as np
from typing import Union, Optional
from scipy import stats


def linear_regression(data: Union[pd.Series, pd.DataFrame], period: int = 20,
                     column: str = 'close') -> pd.DataFrame:
    """
    Linear Regression Analysis
    
    Calculates slope, intercept, R-squared, and forecasted value.
    
    Args:
        data: Price data (Series or DataFrame)
        period: Regression period (default: 20)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        DataFrame with columns: slope, intercept, r_squared, forecast, std_error
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    
    def calculate_regression(y):
        if len(y) < 2:
            return pd.Series([np.nan, np.nan, np.nan, np.nan, np.nan])
        
        x = np.arange(len(y))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        # Forecast for next period
        forecast = slope * len(y) + intercept
        
        return pd.Series([slope, intercept, r_value**2, forecast, std_err])
    
    result = prices.rolling(window=period).apply(
        lambda x: calculate_regression(x), raw=False, result_type='expand'
    )
    
    if result.shape[1] >= 5:
        return pd.DataFrame({
            'slope': result.iloc[:, 0],
            'intercept': result.iloc[:, 1], 
            'r_squared': result.iloc[:, 2],
            'forecast': result.iloc[:, 3],
            'std_error': result.iloc[:, 4]
        }, index=prices.index)
    else:
        return pd.DataFrame({
            'slope': np.nan,
            'intercept': np.nan,
            'r_squared': np.nan,
            'forecast': np.nan,
            'std_error': np.nan
        }, index=prices.index)


def correlation_coefficient(data1: Union[pd.Series, pd.DataFrame], 
                           data2: Union[pd.Series, pd.DataFrame],
                           period: int = 20, column1: str = 'close',
                           column2: str = 'close') -> pd.Series:
    """
    Rolling Correlation Coefficient
    
    Calculates rolling correlation between two price series.
    
    Args:
        data1: First price data (Series or DataFrame)
        data2: Second price data (Series or DataFrame)
        period: Correlation period (default: 20)
        column1: Column name for first dataset (default: 'close')
        column2: Column name for second dataset (default: 'close')
        
    Returns:
        pandas Series with correlation coefficients
    """
    prices1 = data1[column1] if isinstance(data1, pd.DataFrame) else data1
    prices2 = data2[column2] if isinstance(data2, pd.DataFrame) else data2
    
    return prices1.rolling(window=period).corr(prices2)


def z_score(data: Union[pd.Series, pd.DataFrame], period: int = 20,
           column: str = 'close') -> pd.Series:
    """
    Z-Score (Standard Score)
    
    Measures how many standard deviations a value is from the mean.
    
    Args:
        data: Price data (Series or DataFrame)
        period: Rolling period (default: 20)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with Z-score values
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    
    rolling_mean = prices.rolling(window=period).mean()
    rolling_std = prices.rolling(window=period).std()
    
    z_score = (prices - rolling_mean) / rolling_std
    return z_score


def skewness(data: Union[pd.Series, pd.DataFrame], period: int = 20,
            column: str = 'close') -> pd.Series:
    """
    Rolling Skewness
    
    Measures asymmetry of the price distribution.
    
    Args:
        data: Price data (Series or DataFrame)
        period: Rolling period (default: 20)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with skewness values
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    returns = prices.pct_change()
    
    return returns.rolling(window=period).skew()


def kurtosis(data: Union[pd.Series, pd.DataFrame], period: int = 20,
            column: str = 'close') -> pd.Series:
    """
    Rolling Kurtosis
    
    Measures tail heaviness of the price distribution.
    
    Args:
        data: Price data (Series or DataFrame)
        period: Rolling period (default: 20)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with kurtosis values
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    returns = prices.pct_change()
    
    return returns.rolling(window=period).kurt()


def percentile_rank(data: Union[pd.Series, pd.DataFrame], period: int = 20,
                   column: str = 'close') -> pd.Series:
    """
    Percentile Rank
    
    Shows where current price ranks within recent price history (0-100).
    
    Args:
        data: Price data (Series or DataFrame)
        period: Rolling period (default: 20)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with percentile rank values
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    
    def calc_percentile_rank(series):
        if len(series) < 2:
            return np.nan
        current_value = series.iloc[-1]
        return (series < current_value).sum() / len(series) * 100
    
    percentile_rank = prices.rolling(window=period).apply(calc_percentile_rank)
    return percentile_rank


def beta_coefficient(data: Union[pd.Series, pd.DataFrame],
                    market_data: Union[pd.Series, pd.DataFrame],
                    period: int = 60, column: str = 'close',
                    market_column: str = 'close') -> pd.Series:
    """
    Beta Coefficient
    
    Measures sensitivity of asset returns to market returns.
    
    Args:
        data: Asset price data (Series or DataFrame)
        market_data: Market benchmark data (Series or DataFrame)
        period: Rolling period (default: 60)
        column: Column name for asset data (default: 'close')
        market_column: Column name for market data (default: 'close')
        
    Returns:
        pandas Series with beta coefficient values
    """
    asset_prices = data[column] if isinstance(data, pd.DataFrame) else data
    market_prices = market_data[market_column] if isinstance(market_data, pd.DataFrame) else market_data
    
    asset_returns = asset_prices.pct_change()
    market_returns = market_prices.pct_change()
    
    # Calculate rolling beta
    covariance = asset_returns.rolling(window=period).cov(market_returns)
    market_variance = market_returns.rolling(window=period).var()
    
    beta = covariance / market_variance
    return beta


def alpha_coefficient(data: Union[pd.Series, pd.DataFrame],
                     market_data: Union[pd.Series, pd.DataFrame],
                     risk_free_rate: float = 0.02, period: int = 60,
                     column: str = 'close', market_column: str = 'close') -> pd.Series:
    """
    Alpha Coefficient (Jensen's Alpha)
    
    Measures risk-adjusted excess return relative to market.
    
    Args:
        data: Asset price data (Series or DataFrame)
        market_data: Market benchmark data (Series or DataFrame)
        risk_free_rate: Annual risk-free rate (default: 0.02 = 2%)
        period: Rolling period (default: 60)
        column: Column name for asset data (default: 'close')
        market_column: Column name for market data (default: 'close')
        
    Returns:
        pandas Series with alpha coefficient values
    """
    asset_prices = data[column] if isinstance(data, pd.DataFrame) else data
    market_prices = market_data[market_column] if isinstance(market_data, pd.DataFrame) else market_data
    
    asset_returns = asset_prices.pct_change()
    market_returns = market_prices.pct_change()
    
    # Annualized daily risk-free rate
    daily_rf_rate = risk_free_rate / 252
    
    # Calculate excess returns
    excess_asset_returns = asset_returns - daily_rf_rate
    excess_market_returns = market_returns - daily_rf_rate
    
    # Calculate rolling beta
    beta = beta_coefficient(data, market_data, period, column, market_column)
    
    # Calculate alpha
    rolling_asset_mean = excess_asset_returns.rolling(window=period).mean()
    rolling_market_mean = excess_market_returns.rolling(window=period).mean()
    
    alpha = rolling_asset_mean - beta * rolling_market_mean
    
    # Annualize alpha
    alpha = alpha * 252
    
    return alpha


def information_ratio(data: Union[pd.Series, pd.DataFrame],
                     benchmark_data: Union[pd.Series, pd.DataFrame],
                     period: int = 60, column: str = 'close',
                     benchmark_column: str = 'close') -> pd.Series:
    """
    Information Ratio
    
    Measures risk-adjusted excess return relative to a benchmark.
    
    Args:
        data: Asset price data (Series or DataFrame)
        benchmark_data: Benchmark data (Series or DataFrame)
        period: Rolling period (default: 60)
        column: Column name for asset data (default: 'close')
        benchmark_column: Column name for benchmark data (default: 'close')
        
    Returns:
        pandas Series with information ratio values
    """
    asset_prices = data[column] if isinstance(data, pd.DataFrame) else data
    benchmark_prices = benchmark_data[benchmark_column] if isinstance(benchmark_data, pd.DataFrame) else benchmark_data
    
    asset_returns = asset_prices.pct_change()
    benchmark_returns = benchmark_prices.pct_change()
    
    # Active returns
    active_returns = asset_returns - benchmark_returns
    
    # Rolling information ratio
    rolling_mean = active_returns.rolling(window=period).mean()
    rolling_std = active_returns.rolling(window=period).std()
    
    info_ratio = rolling_mean / rolling_std
    
    # Annualize
    info_ratio = info_ratio * np.sqrt(252)
    
    return info_ratio


def standard_error_regression(data: Union[pd.Series, pd.DataFrame], period: int = 20,
                              column: str = 'close') -> pd.Series:
    """
    Standard Error of Linear Regression
    
    Measures the accuracy of linear regression predictions.
    
    Args:
        data: Price data (Series or DataFrame)
        period: Regression period (default: 20)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with standard error values
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    
    def calculate_std_error(y):
        if len(y) < 3:
            return np.nan
        
        x = np.arange(len(y))
        slope, intercept = np.polyfit(x, y, 1)
        
        y_pred = slope * x + intercept
        residuals = y - y_pred
        
        # Standard error calculation
        std_error = np.sqrt(np.sum(residuals**2) / (len(y) - 2))
        return std_error
    
    std_error = prices.rolling(window=period).apply(calculate_std_error, raw=False)
    return std_error


def cointegration_test(data1: Union[pd.Series, pd.DataFrame],
                      data2: Union[pd.Series, pd.DataFrame],
                      period: int = 60, column1: str = 'close',
                      column2: str = 'close') -> pd.DataFrame:
    """
    Cointegration Test (Engle-Granger)
    
    Tests for cointegration between two price series using rolling windows.
    
    Args:
        data1: First price series (Series or DataFrame)
        data2: Second price series (Series or DataFrame)
        period: Rolling window period (default: 60)
        column1: Column name for first series (default: 'close')
        column2: Column name for second series (default: 'close')
        
    Returns:
        DataFrame with cointegration_stat, p_value, and is_cointegrated columns
    """
    from statsmodels.tsa.stattools import adfuller
    
    prices1 = data1[column1] if isinstance(data1, pd.DataFrame) else data1
    prices2 = data2[column2] if isinstance(data2, pd.DataFrame) else data2
    
    coint_stat = pd.Series(index=prices1.index, dtype=float)
    p_values = pd.Series(index=prices1.index, dtype=float)
    is_cointegrated = pd.Series(index=prices1.index, dtype=bool)
    
    for i in range(period, len(prices1)):
        try:
            y1 = prices1.iloc[i-period+1:i+1].values
            y2 = prices2.iloc[i-period+1:i+1].values
            
            if len(y1) == len(y2) and len(y1) > 10:
                # Step 1: Run regression y1 = alpha + beta * y2 + residuals
                beta, alpha = np.polyfit(y2, y1, 1)
                residuals = y1 - (alpha + beta * y2)
                
                # Step 2: Test residuals for unit root (ADF test)
                adf_result = adfuller(residuals)
                
                coint_stat.iloc[i] = adf_result[0]
                p_values.iloc[i] = adf_result[1]
                is_cointegrated.iloc[i] = adf_result[1] < 0.05
                
        except Exception:
            coint_stat.iloc[i] = np.nan
            p_values.iloc[i] = np.nan
            is_cointegrated.iloc[i] = False
    
    return pd.DataFrame({
        'cointegration_stat': coint_stat,
        'p_value': p_values,
        'is_cointegrated': is_cointegrated
    }, index=prices1.index)


def hurst_exponent(data: Union[pd.Series, pd.DataFrame], period: int = 100,
                  column: str = 'close') -> pd.Series:
    """
    Hurst Exponent
    
    Measures the long-term memory of time series.
    H > 0.5: persistent/trending, H < 0.5: mean-reverting, H = 0.5: random walk
    
    Args:
        data: Price data (Series or DataFrame)
        period: Analysis period (default: 100)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with Hurst exponent values
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    
    def calculate_hurst(series):
        """Calculate Hurst exponent using R/S analysis"""
        if len(series) < 10:
            return np.nan
        
        try:
            # Convert to log returns
            log_returns = np.log(series).diff().dropna()
            if len(log_returns) < 5:
                return np.nan
            
            # Calculate cumulative sum of deviations from mean
            mean_return = log_returns.mean()
            cumulative_devs = (log_returns - mean_return).cumsum()
            
            # Calculate range
            R = cumulative_devs.max() - cumulative_devs.min()
            
            # Calculate standard deviation
            S = log_returns.std()
            
            # Avoid division by zero
            if S == 0 or R == 0:
                return 0.5
            
            # R/S ratio
            rs_ratio = R / S
            
            # Hurst exponent approximation
            # For more accurate calculation, should use multiple time scales
            hurst = np.log(rs_ratio) / np.log(len(log_returns))
            
            # Clamp to reasonable range
            return max(0, min(1, hurst))
            
        except Exception:
            return np.nan
    
    hurst_values = prices.rolling(window=period).apply(calculate_hurst, raw=False)
    return hurst_values


def t_test_indicator(data1: Union[pd.Series, pd.DataFrame],
                    data2: Optional[Union[pd.Series, pd.DataFrame]] = None,
                    period: int = 30, column1: str = 'close',
                    column2: str = 'close') -> pd.DataFrame:
    """
    T-Test Indicator
    
    Performs rolling t-tests to compare means.
    If data2 is None, tests if mean is significantly different from zero.
    
    Args:
        data1: First dataset (Series or DataFrame)
        data2: Second dataset (Series or DataFrame), optional
        period: Rolling window period (default: 30)
        column1: Column name for first dataset (default: 'close')
        column2: Column name for second dataset (default: 'close')
        
    Returns:
        DataFrame with t_statistic, p_value, and significant columns
    """
    from scipy import stats
    
    series1 = data1[column1] if isinstance(data1, pd.DataFrame) else data1
    
    if data2 is not None:
        series2 = data2[column2] if isinstance(data2, pd.DataFrame) else data2
    else:
        series2 = None
    
    t_stats = pd.Series(index=series1.index, dtype=float)
    p_values = pd.Series(index=series1.index, dtype=float)
    significant = pd.Series(index=series1.index, dtype=bool)
    
    for i in range(period, len(series1)):
        try:
            sample1 = series1.iloc[i-period+1:i+1].values
            
            if series2 is not None:
                sample2 = series2.iloc[i-period+1:i+1].values
                # Two-sample t-test
                t_stat, p_val = stats.ttest_ind(sample1, sample2, equal_var=False)
            else:
                # One-sample t-test (test if mean is different from 0)
                # First convert to returns
                returns = pd.Series(sample1).pct_change().dropna().values
                if len(returns) > 2:
                    t_stat, p_val = stats.ttest_1samp(returns, 0)
                else:
                    t_stat, p_val = np.nan, np.nan
            
            t_stats.iloc[i] = t_stat
            p_values.iloc[i] = p_val
            significant.iloc[i] = p_val < 0.05 if not np.isnan(p_val) else False
            
        except Exception:
            t_stats.iloc[i] = np.nan
            p_values.iloc[i] = np.nan
            significant.iloc[i] = False
    
    return pd.DataFrame({
        't_statistic': t_stats,
        'p_value': p_values,
        'significant': significant
    }, index=series1.index)


def sharpe_ratio(data: Union[pd.Series, pd.DataFrame], risk_free_rate: float = 0.02,
                period: int = 60, column: str = 'close') -> pd.Series:
    """
    Sharpe Ratio
    
    Measures risk-adjusted return.
    
    Args:
        data: Price data (Series or DataFrame)
        risk_free_rate: Annual risk-free rate (default: 0.02 = 2%)
        period: Rolling period (default: 60)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with Sharpe ratio values
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    returns = prices.pct_change()
    
    # Daily risk-free rate
    daily_rf_rate = risk_free_rate / 252
    
    # Excess returns
    excess_returns = returns - daily_rf_rate
    
    # Rolling Sharpe ratio
    rolling_mean = excess_returns.rolling(window=period).mean()
    rolling_std = returns.rolling(window=period).std()
    
    sharpe = rolling_mean / rolling_std
    
    # Annualize
    sharpe = sharpe * np.sqrt(252)
    
    return sharpe


# Registry of all advanced statistical functions
ADVANCED_STATISTICAL_INDICATORS = {
    'linear_regression': linear_regression,
    'correlation_coefficient': correlation_coefficient,
    'z_score': z_score,
    'skewness': skewness,
    'kurtosis': kurtosis,
    'percentile_rank': percentile_rank,
    'beta_coefficient': beta_coefficient,
    'alpha_coefficient': alpha_coefficient,
    'information_ratio': information_ratio,
    'sharpe_ratio': sharpe_ratio,
    'standard_error_regression': standard_error_regression,
    'cointegration_test': cointegration_test,
    'hurst_exponent': hurst_exponent,
    't_test_indicator': t_test_indicator
}


def get_statistical_function_names():
    """Get list of all advanced statistical function names"""
    return list(ADVANCED_STATISTICAL_INDICATORS.keys())