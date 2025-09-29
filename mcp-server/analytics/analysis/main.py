import pandas as pd

def analyze_returns_symmetry(returns_series: pd.Series):
    """Analyze up vs down day symmetry for a return series.
    
    This function examines the balance between positive and negative return days,
    analyzing count symmetry, magnitude symmetry, and volatility symmetry to
    provide insights into return distribution characteristics. This analysis is
    useful for understanding market behavior patterns and risk characteristics.
    
    Args:
        returns_series (pd.Series): A pandas Series containing daily return values.
            The series should contain numerical values representing percentage
            returns (e.g., 0.02 for 2% return, -0.015 for -1.5% return).
    
    Returns:
        dict or None: Dictionary containing symmetry analysis metrics:
            - up_days_count (int): Number of positive return days
            - down_days_count (int): Number of negative return days  
            - neutral_days_count (int): Number of zero return days
            - up_percentage (float): Percentage of days with positive returns
            - down_percentage (float): Percentage of days with negative returns
            - avg_up_return (float): Average return on positive days
            - avg_down_return (float): Average return on negative days (negative value)
            - up_volatility (float): Standard deviation of positive returns
            - down_volatility (float): Standard deviation of negative returns
            - count_symmetry_ratio (float): Ratio of balanced up/down day counts (0-1)
            - magnitude_symmetry_ratio (float): Ratio of balanced avg magnitudes (0-1)
            - volatility_symmetry_ratio (float): Ratio of balanced volatilities (0-1)
            - overall_symmetry_score (float): Composite symmetry score (0-1)
        Returns None if input is invalid or insufficient data.
    
    Notes:
        - Symmetry ratios range from 0 (completely asymmetric) to 1 (perfectly symmetric)
        - Overall symmetry score is the geometric mean of the three component ratios
        - Requires at least one positive and one negative return day to calculate
        - Perfect symmetry (score = 1.0) indicates equal up/down days with equal
          average magnitudes and volatilities
    
    Examples:
        >>> import pandas as pd
        >>> import numpy as np
        >>> 
        >>> # Create sample return data
        >>> np.random.seed(42)
        >>> returns = pd.Series(np.random.normal(0.001, 0.02, 100))
        >>> 
        >>> # Analyze symmetry
        >>> result = analyze_returns_symmetry(returns)
        >>> print(f"Up days: {result['up_days_count']}")
        >>> print(f"Down days: {result['down_days_count']}")
        >>> print(f"Overall symmetry score: {result['overall_symmetry_score']:.3f}")
        Up days: 54
        Down days: 46
        Overall symmetry score: 0.892
        
        >>> # Example with perfectly symmetric data
        >>> symmetric_returns = pd.Series([0.01, -0.01, 0.02, -0.02, 0.01, -0.01])
        >>> result = analyze_returns_symmetry(symmetric_returns)
        >>> print(f"Symmetry score: {result['overall_symmetry_score']:.3f}")
        Symmetry score: 1.000
        
        >>> # Example with invalid input
        >>> empty_series = pd.Series([])
        >>> result = analyze_returns_symmetry(empty_series)
        >>> print(result)
        None
        
        >>> # Example with only positive returns
        >>> positive_only = pd.Series([0.01, 0.02, 0.015])
        >>> result = analyze_returns_symmetry(positive_only)
        >>> print(result)
        None
    
    Raises:
        No explicit exceptions are raised. Invalid inputs return None.
    """
    if not isinstance(returns_series, pd.Series) or len(returns_series) == 0:
        return None
    
    # Separate up and down days
    up_days = returns_series[returns_series > 0]
    down_days = returns_series[returns_series < 0]
    neutral_days = returns_series[returns_series == 0]
    
    if len(up_days) == 0 or len(down_days) == 0:
        return None
    
    # Calculate symmetry metrics
    up_count = len(up_days)
    down_count = len(down_days)
    total_count = len(returns_series)
    
    # Count symmetry (how balanced up vs down days are)
    count_ratio = min(up_count, down_count) / max(up_count, down_count)
    
    # Magnitude symmetry (how similar average up vs down moves are)
    avg_up_magnitude = up_days.mean()
    avg_down_magnitude = abs(down_days.mean())
    magnitude_ratio = min(avg_up_magnitude, avg_down_magnitude) / max(avg_up_magnitude, avg_down_magnitude)
    
    # Volatility symmetry (how similar up vs down volatilities are)
    up_volatility = up_days.std()
    down_volatility = down_days.std()
    volatility_ratio = min(up_volatility, down_volatility) / max(up_volatility, down_volatility) if up_volatility > 0 and down_volatility > 0 else 0
    
    # Composite symmetry score (geometric mean of ratios)
    symmetry_score = (count_ratio * magnitude_ratio * volatility_ratio) ** (1/3)
    
    return {
        'up_days_count': up_count,
        'down_days_count': down_count,
        'neutral_days_count': len(neutral_days),
        'up_percentage': (up_count / total_count) * 100,
        'down_percentage': (down_count / total_count) * 100,
        'avg_up_return': avg_up_magnitude,
        'avg_down_return': -avg_down_magnitude,  # Keep negative for display
        'up_volatility': up_volatility,
        'down_volatility': down_volatility,
        'count_symmetry_ratio': count_ratio,
        'magnitude_symmetry_ratio': magnitude_ratio,
        'volatility_symmetry_ratio': volatility_ratio,
        'overall_symmetry_score': symmetry_score
    }
