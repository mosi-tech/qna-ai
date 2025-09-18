"""
Time Utilities for Portfolio Analytics

Atomic functions for handling time-based calculations and date operations.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Union, Optional
from datetime import datetime, timedelta


def calculate_relative_date_range(
    reference_date: str = "today",
    years_back: int = 10,
    months_back: int = None,
    days_back: int = None
) -> Dict[str, Any]:
    """
    Calculate date range relative to reference date.
    
    Args:
        reference_date: "today" or specific date "YYYY-MM-DD"
        years_back: Number of years to go back
        months_back: Number of months to go back (overrides years_back)
        days_back: Number of days to go back (overrides others)
        
    Returns:
        {
            "start_date": str,  # "YYYY-MM-DD"
            "end_date": str,    # "YYYY-MM-DD"  
            "period_description": str,
            "total_days": int,
            "success": bool
        }
    """
    try:
        # Parse reference date
        if reference_date.lower() == "today":
            end_dt = datetime.now()
        else:
            end_dt = pd.to_datetime(reference_date)
        
        # Calculate start date based on priority: days > months > years
        if days_back:
            start_dt = end_dt - timedelta(days=days_back)
            period_desc = f"last {days_back} days"
        elif months_back:
            # Approximate months as 30 days each
            start_dt = end_dt - timedelta(days=months_back * 30)
            period_desc = f"last {months_back} months"
        else:
            # Default to years
            start_dt = end_dt - timedelta(days=years_back * 365)
            period_desc = f"last {years_back} years"
        
        # Calculate total days
        total_days = (end_dt - start_dt).days
        
        return {
            "success": True,
            "start_date": start_dt.strftime("%Y-%m-%d"),
            "end_date": end_dt.strftime("%Y-%m-%d"),
            "period_description": period_desc,
            "total_days": total_days,
            "reference_date": reference_date
        }
        
    except Exception as e:
        return {"success": False, "error": f"Date calculation failed: {str(e)}"}


def get_market_trading_days(
    start_date: str,
    end_date: str,
    market: str = "US"
) -> Dict[str, Any]:
    """
    Calculate number of trading days between dates.
    
    Args:
        start_date: Start date "YYYY-MM-DD"
        end_date: End date "YYYY-MM-DD"
        market: Market to use ("US", "UK", "EU")
        
    Returns:
        {
            "trading_days": int,
            "calendar_days": int,
            "weekends": int,
            "estimated_holidays": int,
            "success": bool
        }
    """
    try:
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        
        if start_dt >= end_dt:
            return {"success": False, "error": "Start date must be before end date"}
        
        # Calculate calendar days
        calendar_days = (end_dt - start_dt).days
        
        # Create date range
        date_range = pd.date_range(start=start_dt, end=end_dt, freq='D')
        
        # Count weekdays (exclude Saturday=5, Sunday=6)
        weekdays = sum(1 for d in date_range if d.weekday() < 5)
        weekends = len(date_range) - weekdays
        
        # Estimate holidays (rough approximation)
        years_span = (end_dt.year - start_dt.year) + 1
        if market.upper() == "US":
            estimated_holidays = years_span * 10  # ~10 US market holidays per year
        else:
            estimated_holidays = years_span * 8   # Rough estimate for other markets
        
        # Trading days = weekdays - estimated holidays
        trading_days = max(weekdays - estimated_holidays, 0)
        
        return {
            "success": True,
            "trading_days": trading_days,
            "calendar_days": calendar_days,
            "weekdays": weekdays,
            "weekends": weekends,
            "estimated_holidays": estimated_holidays,
            "market": market
        }
        
    except Exception as e:
        return {"success": False, "error": f"Trading days calculation failed: {str(e)}"}


def calculate_rolling_metrics(
    data: Union[pd.Series, Dict[str, Any]],
    window_days: int,
    metric: str = "volatility"
) -> Dict[str, Any]:
    """
    Calculate rolling metrics over specified window.
    
    Args:
        data: Return series or result from other functions
        window_days: Rolling window size in days
        metric: "volatility", "return", "sharpe", "max_drawdown"
        
    Returns:
        {
            "rolling_values": pd.Series,
            "current_value": float,
            "average_value": float, 
            "min_value": float,
            "max_value": float,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(data, dict) and "returns" in data:
            series = data["returns"]
        elif isinstance(data, dict) and "filtered_data" in data:
            series = data["filtered_data"]
        elif isinstance(data, pd.Series):
            series = data
        else:
            return {"success": False, "error": "Invalid data format"}
        
        if len(series) < window_days:
            return {"success": False, "error": f"Need at least {window_days} observations"}
        
        # Calculate rolling metric based on type
        if metric == "volatility":
            rolling_values = series.rolling(window=window_days).std() * np.sqrt(252)
        elif metric == "return":
            rolling_values = series.rolling(window=window_days).apply(
                lambda x: (1 + x).prod() - 1, raw=False
            )
        elif metric == "sharpe":
            rolling_values = series.rolling(window=window_days).apply(
                lambda x: (x.mean() - 0.02/252) / x.std() * np.sqrt(252) if x.std() > 0 else 0,
                raw=False
            )
        elif metric == "max_drawdown":
            def rolling_max_dd(window_returns):
                cumulative = (1 + window_returns).cumprod()
                running_max = cumulative.expanding().max()
                drawdown = (cumulative - running_max) / running_max
                return drawdown.min()
            
            rolling_values = series.rolling(window=window_days).apply(
                rolling_max_dd, raw=False
            )
        else:
            return {"success": False, "error": f"Unknown metric: {metric}"}
        
        # Drop NaN values
        rolling_values = rolling_values.dropna()
        
        if len(rolling_values) == 0:
            return {"success": False, "error": "No valid rolling calculations"}
        
        return {
            "success": True,
            "rolling_values": rolling_values,
            "current_value": float(rolling_values.iloc[-1]),
            "average_value": float(rolling_values.mean()),
            "min_value": float(rolling_values.min()),
            "max_value": float(rolling_values.max()),
            "metric": metric,
            "window_days": window_days,
            "num_windows": len(rolling_values)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Rolling metric calculation failed: {str(e)}"}


def identify_time_periods(
    data: Union[pd.Series, Dict[str, Any]],
    period_type: str = "yearly"
) -> Dict[str, Any]:
    """
    Break down time series into periods for analysis.
    
    Args:
        data: Return series or result from other functions
        period_type: "yearly", "quarterly", "monthly"
        
    Returns:
        {
            "periods": List[Dict],  # [{"start": date, "end": date, "returns": series}]
            "period_type": str,
            "num_periods": int,
            "success": bool
        }
    """
    try:
        # Handle input format
        if isinstance(data, dict) and "returns" in data:
            series = data["returns"]
        elif isinstance(data, dict) and "filtered_data" in data:
            series = data["filtered_data"]
        elif isinstance(data, pd.Series):
            series = data
        else:
            return {"success": False, "error": "Invalid data format"}
        
        if len(series) < 10:
            return {"success": False, "error": "Insufficient data for period analysis"}
        
        periods = []
        
        if period_type == "yearly":
            # Group by year
            yearly_groups = series.groupby(series.index.year)
            for year, year_data in yearly_groups:
                periods.append({
                    "period_name": str(year),
                    "start_date": year_data.index[0].strftime("%Y-%m-%d"),
                    "end_date": year_data.index[-1].strftime("%Y-%m-%d"),
                    "num_days": len(year_data),
                    "returns": year_data,
                    "total_return": (1 + year_data).prod() - 1
                })
                
        elif period_type == "quarterly":
            # Group by quarter
            quarterly_groups = series.groupby([series.index.year, series.index.quarter])
            for (year, quarter), quarter_data in quarterly_groups:
                periods.append({
                    "period_name": f"{year} Q{quarter}",
                    "start_date": quarter_data.index[0].strftime("%Y-%m-%d"),
                    "end_date": quarter_data.index[-1].strftime("%Y-%m-%d"),
                    "num_days": len(quarter_data),
                    "returns": quarter_data,
                    "total_return": (1 + quarter_data).prod() - 1
                })
                
        elif period_type == "monthly":
            # Group by month
            monthly_groups = series.groupby([series.index.year, series.index.month])
            for (year, month), month_data in monthly_groups:
                month_name = pd.Timestamp(year=year, month=month, day=1).strftime("%Y-%m")
                periods.append({
                    "period_name": month_name,
                    "start_date": month_data.index[0].strftime("%Y-%m-%d"),
                    "end_date": month_data.index[-1].strftime("%Y-%m-%d"),
                    "num_days": len(month_data),
                    "returns": month_data,
                    "total_return": (1 + month_data).prod() - 1
                })
        else:
            return {"success": False, "error": f"Unknown period type: {period_type}"}
        
        return {
            "success": True,
            "periods": periods,
            "period_type": period_type,
            "num_periods": len(periods),
            "total_data_points": len(series)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Period identification failed: {str(e)}"}


# Registry for MCP server
TIME_UTILITIES_FUNCTIONS = {
    'calculate_relative_date_range': calculate_relative_date_range,
    'get_market_trading_days': get_market_trading_days,
    'calculate_rolling_metrics': calculate_rolling_metrics,
    'identify_time_periods': identify_time_periods
}