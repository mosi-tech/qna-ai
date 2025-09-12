"""
Cycle Analysis Indicators

Cycle analysis indicators for identifying market cycles and phases:
- Dominant Cycle (MESA Adaptive Moving Average concepts)
- Cycle Period detection
- Phase indicators  
- Instantaneous Trendline

All functions follow consistent patterns:
- Input: pandas Series or DataFrame with OHLCV data
- Output: pandas Series or DataFrame with calculated indicator values
- Parameters: Standard parameter names with sensible defaults
"""

import pandas as pd
import numpy as np
from typing import Union, Optional
from scipy import signal
from scipy.fft import fft, fftfreq


def dominant_cycle(data: Union[pd.Series, pd.DataFrame], min_period: int = 8,
                  max_period: int = 50, column: str = 'close') -> pd.DataFrame:
    """
    Dominant Cycle Detection
    
    Uses spectral analysis to identify the dominant cycle period in price data.
    Based on MESA (Maximum Entropy Spectral Analysis) concepts.
    
    Args:
        data: Price data (Series or DataFrame)
        min_period: Minimum cycle period to detect (default: 8)
        max_period: Maximum cycle period to detect (default: 50)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        DataFrame with cycle_period, cycle_phase, and dominant_cycle columns
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    
    # Remove trend using high-pass filter
    detrended = prices - prices.rolling(window=max_period).mean()
    detrended = detrended.fillna(0)
    
    cycle_period = pd.Series(index=prices.index, dtype=float)
    cycle_phase = pd.Series(index=prices.index, dtype=float)
    dominant_cycle_values = pd.Series(index=prices.index, dtype=float)
    
    # Use sliding window FFT to detect dominant frequencies
    window_size = max_period * 2
    
    for i in range(window_size, len(detrended)):
        window_data = detrended.iloc[i-window_size:i].values
        
        # Apply FFT
        fft_vals = fft(window_data)
        freqs = fftfreq(window_size)
        
        # Get power spectrum
        power_spectrum = np.abs(fft_vals)**2
        
        # Find dominant frequency within our period range
        valid_freqs = freqs[(freqs > 1/max_period) & (freqs < 1/min_period) & (freqs > 0)]
        if len(valid_freqs) > 0:
            valid_indices = np.where((freqs > 1/max_period) & (freqs < 1/min_period) & (freqs > 0))[0]
            dominant_idx = valid_indices[np.argmax(power_spectrum[valid_indices])]
            dominant_freq = freqs[dominant_idx]
            
            if dominant_freq > 0:
                period = 1 / dominant_freq
                cycle_period.iloc[i] = period
                
                # Calculate phase
                phase = np.angle(fft_vals[dominant_idx])
                cycle_phase.iloc[i] = phase
                
                # Generate dominant cycle wave
                dominant_cycle_values.iloc[i] = np.cos(2 * np.pi * i / period + phase)
    
    return pd.DataFrame({
        'cycle_period': cycle_period,
        'cycle_phase': cycle_phase,
        'dominant_cycle': dominant_cycle_values
    }, index=prices.index)


def cycle_period_detector(data: Union[pd.Series, pd.DataFrame], 
                         window_size: int = 100, column: str = 'close') -> pd.Series:
    """
    Cycle Period Detection using Autocorrelation
    
    Detects the most significant cycle period using autocorrelation analysis.
    
    Args:
        data: Price data (Series or DataFrame)
        window_size: Window size for analysis (default: 100)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with detected cycle periods
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    
    # Detrend the data
    detrended = prices - prices.rolling(window=50).mean()
    detrended = detrended.fillna(0)
    
    cycle_periods = pd.Series(index=prices.index, dtype=float)
    
    for i in range(window_size, len(detrended)):
        window_data = detrended.iloc[i-window_size:i].values
        
        # Calculate autocorrelation
        autocorr = np.correlate(window_data, window_data, mode='full')
        autocorr = autocorr[autocorr.size // 2:]
        
        # Find peaks in autocorrelation (indicating cycle periods)
        peaks, _ = signal.find_peaks(autocorr[1:], height=np.max(autocorr) * 0.3)
        
        if len(peaks) > 0:
            # Most significant peak indicates dominant cycle period
            strongest_peak_idx = peaks[np.argmax(autocorr[peaks + 1])]
            cycle_periods.iloc[i] = strongest_peak_idx + 1
    
    return cycle_periods


def phase_indicator(data: Union[pd.Series, pd.DataFrame], period: int = 20,
                   column: str = 'close') -> pd.DataFrame:
    """
    Phase Indicator using Hilbert Transform
    
    Calculates the phase of the price cycle using Hilbert Transform.
    
    Args:
        data: Price data (Series or DataFrame)
        period: Cycle period for phase calculation (default: 20)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        DataFrame with phase, inphase, and quadrature components
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    
    # Smooth the data
    smoothed = prices.rolling(window=4).mean().fillna(prices)
    
    # Calculate Hilbert Transform components
    inphase = pd.Series(index=prices.index, dtype=float)
    quadrature = pd.Series(index=prices.index, dtype=float)
    phase = pd.Series(index=prices.index, dtype=float)
    
    # Simple approximation of Hilbert Transform
    for i in range(period, len(smoothed)):
        # Inphase component (price)
        inphase.iloc[i] = smoothed.iloc[i]
        
        # Quadrature component (90-degree phase shift approximation)
        if i >= period:
            weights = np.array([0.0962, 0.5769, 0.5769, 0.0962])  # Hilbert coefficients
            if len(smoothed.iloc[i-3:i+1]) == 4:
                quadrature.iloc[i] = np.dot(weights, smoothed.iloc[i-3:i+1].values)
        
        # Calculate phase angle
        if abs(inphase.iloc[i]) > 1e-10:
            phase.iloc[i] = np.arctan2(quadrature.iloc[i], inphase.iloc[i])
        else:
            phase.iloc[i] = np.pi / 2 if quadrature.iloc[i] > 0 else -np.pi / 2
    
    # Convert phase to degrees
    phase_degrees = phase * 180 / np.pi
    
    return pd.DataFrame({
        'phase': phase_degrees,
        'inphase': inphase,
        'quadrature': quadrature
    }, index=prices.index)


def instantaneous_trendline(data: Union[pd.Series, pd.DataFrame], 
                           alpha: float = 0.07, column: str = 'close') -> pd.Series:
    """
    Instantaneous Trendline (MESA)
    
    Adaptive trendline that adjusts based on the dominant cycle period.
    
    Args:
        data: Price data (Series or DataFrame)
        alpha: Smoothing constant (default: 0.07)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with instantaneous trendline values
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    
    # Initialize arrays
    it = pd.Series(index=prices.index, dtype=float)
    it.iloc[0] = prices.iloc[0]
    
    # Calculate instantaneous trendline
    for i in range(1, len(prices)):
        if i < 7:
            # Use simple moving average for initial values
            it.iloc[i] = prices.iloc[:i+1].mean()
        else:
            # MESA Instantaneous Trendline formula
            it.iloc[i] = (alpha - alpha**2/4) * prices.iloc[i] + \
                        (alpha**2/2) * prices.iloc[i-1] - \
                        (alpha - 3*alpha**2/4) * prices.iloc[i-2] + \
                        2 * (1 - alpha) * it.iloc[i-1] - \
                        (1 - alpha)**2 * it.iloc[i-2]
    
    return it


def cycle_strength_indicator(data: Union[pd.Series, pd.DataFrame], 
                           period: int = 20, column: str = 'close') -> pd.Series:
    """
    Cycle Strength Indicator
    
    Measures the strength of the cyclic component in price data.
    
    Args:
        data: Price data (Series or DataFrame)
        period: Analysis period (default: 20)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with cycle strength values (0-100)
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    
    # Get phase components
    phase_data = phase_indicator(data, period, column)
    
    strength = pd.Series(index=prices.index, dtype=float)
    
    # Calculate cycle strength based on phase consistency
    for i in range(period, len(prices)):
        # Get recent phase values
        recent_phases = phase_data['phase'].iloc[i-period+1:i+1]
        
        # Calculate phase consistency (strength)
        if len(recent_phases) > 1:
            phase_diff = recent_phases.diff().abs()
            phase_consistency = 1 - (phase_diff.mean() / 180)  # Normalize to 0-1
            strength.iloc[i] = max(0, min(100, phase_consistency * 100))
    
    return strength


def market_mode_indicator(data: Union[pd.Series, pd.DataFrame], 
                         period: int = 20, column: str = 'close') -> pd.Series:
    """
    Market Mode Indicator
    
    Determines if market is in trending or cycling mode.
    Values > 0.5 indicate trending, < 0.5 indicate cycling.
    
    Args:
        data: Price data (Series or DataFrame)
        period: Analysis period (default: 20)
        column: Column name if DataFrame (default: 'close')
        
    Returns:
        pandas Series with market mode values (0-1)
    """
    prices = data[column] if isinstance(data, pd.DataFrame) else data
    
    # Calculate trend strength using linear regression slope
    trend_strength = pd.Series(index=prices.index, dtype=float)
    
    for i in range(period, len(prices)):
        y = prices.iloc[i-period+1:i+1].values
        x = np.arange(len(y))
        
        # Calculate linear regression
        if len(y) > 1:
            slope, intercept = np.polyfit(x, y, 1)
            
            # Calculate R-squared
            y_pred = slope * x + intercept
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = 1 - (ss_res / (ss_tot + 1e-10))
            
            # Market mode based on R-squared and slope significance
            slope_significance = abs(slope) / (prices.iloc[i] + 1e-10)
            mode_value = r_squared * slope_significance * 10  # Scale factor
            
            trend_strength.iloc[i] = min(1.0, max(0.0, mode_value))
    
    return trend_strength


# Registry of all cycle analysis functions
CYCLE_ANALYSIS_INDICATORS = {
    'dominant_cycle': dominant_cycle,
    'cycle_period_detector': cycle_period_detector,
    'phase_indicator': phase_indicator,
    'instantaneous_trendline': instantaneous_trendline,
    'cycle_strength_indicator': cycle_strength_indicator,
    'market_mode_indicator': market_mode_indicator
}


def get_cycle_analysis_function_names():
    """Get list of all cycle analysis function names"""
    return list(CYCLE_ANALYSIS_INDICATORS.keys())