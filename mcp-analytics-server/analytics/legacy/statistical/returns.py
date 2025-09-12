"""
Returns calculation module for various types of financial returns.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional


class ReturnsCalculator:
    """Calculate various types of financial returns from price data."""
    
    @staticmethod
    def daily_returns(price_data: List[Dict], return_type: str = "close_to_close") -> Dict[str, Any]:
        """
        Calculate daily returns from OHLC price data.
        
        Args:
            price_data: List of OHLC dictionaries with 't', 'o', 'h', 'l', 'c' keys
            return_type: Type of return - 'close_to_close', 'open_to_close', 'close_to_open'
        
        Returns:
            Dictionary with returns and statistics
        """
        if not price_data or len(price_data) < 2:
            return {"error": "Insufficient price data"}
        
        df = pd.DataFrame(price_data)
        df['t'] = pd.to_datetime(df['t'])
        df = df.sort_values('t').reset_index(drop=True)
        
        if return_type == "close_to_close":
            df['return'] = df['c'].pct_change() * 100
        elif return_type == "open_to_close":
            df['return'] = ((df['c'] - df['o']) / df['o']) * 100
        elif return_type == "close_to_open":
            df['return'] = ((df['o'] - df['c'].shift(1)) / df['c'].shift(1)) * 100
        else:
            return {"error": f"Unknown return type: {return_type}"}
        
        returns = df['return'].dropna().tolist()
        
        if not returns:
            return {"error": "No valid returns calculated"}
        
        return {
            "returns": returns,
            "dates": df.loc[df['return'].notna(), 't'].dt.strftime('%Y-%m-%d').tolist(),
            "mean_return": np.mean(returns),
            "std_return": np.std(returns),
            "positive_days": sum(1 for r in returns if r > 0),
            "negative_days": sum(1 for r in returns if r < 0),
            "zero_days": sum(1 for r in returns if r == 0),
            "success_rate": sum(1 for r in returns if r > 0) / len(returns) * 100,
            "max_return": max(returns),
            "min_return": min(returns),
            "total_observations": len(returns)
        }
    
    @staticmethod
    def weekly_returns(price_data: List[Dict]) -> Dict[str, Any]:
        """
        Calculate weekly returns (Friday to Friday).
        
        Args:
            price_data: List of daily OHLC dictionaries
            
        Returns:
            Dictionary with weekly returns and statistics
        """
        if not price_data or len(price_data) < 7:
            return {"error": "Insufficient data for weekly returns"}
        
        df = pd.DataFrame(price_data)
        df['t'] = pd.to_datetime(df['t'])
        df = df.sort_values('t').reset_index(drop=True)
        
        # Resample to weekly (Friday close)
        df.set_index('t', inplace=True)
        weekly = df['c'].resample('W-FRI').last().dropna()
        
        if len(weekly) < 2:
            return {"error": "Insufficient weeks for calculation"}
        
        weekly_returns = weekly.pct_change().dropna() * 100
        
        return {
            "weekly_returns": weekly_returns.tolist(),
            "dates": weekly_returns.index.strftime('%Y-%m-%d').tolist(),
            "mean_weekly_return": weekly_returns.mean(),
            "std_weekly_return": weekly_returns.std(),
            "positive_weeks": sum(1 for r in weekly_returns if r > 0),
            "negative_weeks": sum(1 for r in weekly_returns if r < 0),
            "weekly_success_rate": sum(1 for r in weekly_returns if r > 0) / len(weekly_returns) * 100,
            "total_weeks": len(weekly_returns)
        }
    
    @staticmethod
    def monthly_returns(price_data: List[Dict]) -> Dict[str, Any]:
        """
        Calculate monthly returns (end-of-month).
        
        Args:
            price_data: List of daily OHLC dictionaries
            
        Returns:
            Dictionary with monthly returns and statistics
        """
        if not price_data or len(price_data) < 30:
            return {"error": "Insufficient data for monthly returns"}
        
        df = pd.DataFrame(price_data)
        df['t'] = pd.to_datetime(df['t'])
        df = df.sort_values('t').reset_index(drop=True)
        
        # Resample to monthly (end of month)
        df.set_index('t', inplace=True)
        monthly = df['c'].resample('M').last().dropna()
        
        if len(monthly) < 2:
            return {"error": "Insufficient months for calculation"}
        
        monthly_returns = monthly.pct_change().dropna() * 100
        
        return {
            "monthly_returns": monthly_returns.tolist(),
            "dates": monthly_returns.index.strftime('%Y-%m').tolist(),
            "mean_monthly_return": monthly_returns.mean(),
            "std_monthly_return": monthly_returns.std(),
            "positive_months": sum(1 for r in monthly_returns if r > 0),
            "negative_months": sum(1 for r in monthly_returns if r < 0),
            "monthly_success_rate": sum(1 for r in monthly_returns if r > 0) / len(monthly_returns) * 100,
            "total_months": len(monthly_returns)
        }
    
    @staticmethod
    def annualized_return(returns: List[float], frequency: str = "daily") -> float:
        """
        Calculate annualized return from a series of returns.
        
        Args:
            returns: List of periodic returns (as percentages)
            frequency: Frequency of returns - 'daily', 'weekly', 'monthly'
            
        Returns:
            Annualized return as percentage
        """
        if not returns:
            return 0.0
        
        # Convert to decimal returns
        decimal_returns = [r / 100 for r in returns]
        
        # Calculate compound return
        compound_return = 1.0
        for r in decimal_returns:
            compound_return *= (1 + r)
        
        # Determine periods per year
        periods_per_year = {"daily": 252, "weekly": 52, "monthly": 12}
        periods = periods_per_year.get(frequency, 252)
        
        # Annualize
        n_periods = len(returns)
        if n_periods == 0:
            return 0.0
        
        annualized = ((compound_return ** (periods / n_periods)) - 1) * 100
        return annualized
    
    @staticmethod
    def cumulative_returns(returns: List[float]) -> List[float]:
        """
        Calculate cumulative returns from a series of periodic returns.
        
        Args:
            returns: List of periodic returns (as percentages)
            
        Returns:
            List of cumulative returns
        """
        if not returns:
            return []
        
        # Convert to decimal returns
        decimal_returns = [r / 100 for r in returns]
        
        # Calculate cumulative returns
        cumulative = [0.0]  # Start at 0%
        compound = 1.0
        
        for r in decimal_returns:
            compound *= (1 + r)
            cumulative.append((compound - 1) * 100)
        
        return cumulative[1:]  # Remove the initial 0
    
    @staticmethod
    def return_distribution_stats(returns: List[float]) -> Dict[str, float]:
        """
        Calculate distribution statistics for returns.
        
        Args:
            returns: List of returns (as percentages)
            
        Returns:
            Dictionary with distribution statistics
        """
        if not returns:
            return {"error": "No returns provided"}
        
        returns_array = np.array(returns)
        
        return {
            "mean": np.mean(returns_array),
            "median": np.median(returns_array),
            "std": np.std(returns_array),
            "var": np.var(returns_array),
            "min": np.min(returns_array),
            "max": np.max(returns_array),
            "q25": np.percentile(returns_array, 25),
            "q75": np.percentile(returns_array, 75),
            "skewness": float(pd.Series(returns).skew()),
            "kurtosis": float(pd.Series(returns).kurtosis()),
            "count": len(returns)
        }