"""
Data validation and conversion utilities for MCP analytics server.
Provides comprehensive data validation, standardization, and conversion functions.
"""

import pandas as pd
import numpy as np
from typing import Union, List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

def validate_and_convert_data(data: Union[List[Dict], pd.DataFrame, Dict], 
                             required_columns: List[str] = None) -> pd.DataFrame:
    """
    Validate and convert input data to standardized DataFrame format.
    
    Args:
        data: Input data in various formats (list of dicts, DataFrame, single dict)
        required_columns: List of required column names
        
    Returns:
        pd.DataFrame: Validated and standardized DataFrame
        
    Raises:
        ValueError: If data format is invalid or required columns are missing
    """
    try:
        # Convert input to DataFrame
        if isinstance(data, pd.DataFrame):
            df = data.copy()
        elif isinstance(data, list):
            if not data:
                raise ValueError("Input data list is empty")
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            # Single record - convert to DataFrame
            df = pd.DataFrame([data])
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")
        
        # Standardize column names
        df = standardize_column_names(df)
        
        # Validate required columns
        if required_columns:
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Validate numeric columns
        numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'o', 'h', 'l', 'c', 'v']
        available_numeric = [col for col in numeric_columns if col in df.columns]
        if available_numeric:
            df = validate_numeric_columns(df, available_numeric)
        
        # Ensure minimum data requirements
        if len(df) == 0:
            raise ValueError("DataFrame has no rows after validation")
            
        return df
        
    except Exception as e:
        logger.error(f"Data validation failed: {str(e)}")
        raise

def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert various column naming conventions to standard format.
    
    Handles Alpaca API format (o,h,l,c,v,t) and standard format (open,high,low,close,volume,date)
    
    Args:
        df: Input DataFrame with various column formats
        
    Returns:
        pd.DataFrame: DataFrame with standardized column names
    """
    df = df.copy()
    
    # Column mapping for different formats
    column_mappings = {
        # Alpaca API format
        'o': 'open',
        'h': 'high', 
        'l': 'low',
        'c': 'close',
        'v': 'volume',
        't': 'timestamp',
        
        # Alternative naming conventions
        'Open': 'open',
        'High': 'high',
        'Low': 'low', 
        'Close': 'close',
        'Volume': 'volume',
        'Date': 'date',
        'Timestamp': 'timestamp',
        'datetime': 'timestamp',
        
        # Trading related
        'qty': 'quantity',
        'market_value': 'market_value',
        'unrealized_pl': 'unrealized_pnl',
        'unrealized_plpc': 'unrealized_pnl_percent'
    }
    
    # Apply column mappings
    df = df.rename(columns=column_mappings)
    
    # Handle timestamp/date columns
    if 'timestamp' in df.columns and 'date' not in df.columns:
        df['date'] = df['timestamp']
    
    return df

def validate_numeric_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """
    Ensure specified columns are numeric and handle missing values.
    
    Args:
        df: Input DataFrame
        columns: List of column names to validate as numeric
        
    Returns:
        pd.DataFrame: DataFrame with validated numeric columns
    """
    df = df.copy()
    
    for col in columns:
        if col in df.columns:
            # Convert to numeric, coercing errors to NaN
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Handle missing values
            if df[col].isna().all():
                logger.warning(f"Column {col} has all NaN values")
            elif df[col].isna().any():
                # Forward fill for price data
                if col in ['open', 'high', 'low', 'close', 'o', 'h', 'l', 'c']:
                    df[col] = df[col].fillna(method='ffill')
                # Set volume to 0 if missing
                elif col in ['volume', 'v']:
                    df[col] = df[col].fillna(0)
    
    return df

def validate_price_data_integrity(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate OHLC price data integrity and fix common issues.
    
    Args:
        df: DataFrame with OHLC data
        
    Returns:
        pd.DataFrame: DataFrame with validated price data
    """
    df = df.copy()
    
    # Identify OHLC columns
    ohlc_map = {}
    for std, alts in [('open', ['o', 'Open']), ('high', ['h', 'High']), 
                      ('low', ['l', 'Low']), ('close', ['c', 'Close'])]:
        for col in [std] + alts:
            if col in df.columns:
                ohlc_map[std] = col
                break
    
    required_ohlc = ['open', 'high', 'low', 'close']
    available_ohlc = [k for k in required_ohlc if k in ohlc_map]
    
    if len(available_ohlc) >= 2:  # Need at least 2 price points
        # Validate price relationships
        for i, row in df.iterrows():
            try:
                prices = {k: row[ohlc_map[k]] for k in available_ohlc if not pd.isna(row[ohlc_map[k]])}
                
                if len(prices) >= 4:  # Full OHLC available
                    # High should be >= max(open, close) and low should be <= min(open, close)
                    max_oc = max(prices['open'], prices['close'])
                    min_oc = min(prices['open'], prices['close'])
                    
                    # Fix impossible price relationships
                    if prices['high'] < max_oc:
                        df.loc[i, ohlc_map['high']] = max_oc
                    if prices['low'] > min_oc:
                        df.loc[i, ohlc_map['low']] = min_oc
                        
            except (KeyError, TypeError, ValueError):
                continue  # Skip rows with invalid data
    
    return df

def validate_portfolio_data(positions_data: Union[List[Dict], pd.DataFrame]) -> pd.DataFrame:
    """
    Validate and standardize portfolio position data.
    
    Args:
        positions_data: Portfolio positions in various formats
        
    Returns:
        pd.DataFrame: Validated portfolio DataFrame
    """
    df = validate_and_convert_data(positions_data, required_columns=['symbol'])
    
    # Ensure essential portfolio columns exist
    if 'quantity' not in df.columns and 'qty' in df.columns:
        df['quantity'] = df['qty']
    
    if 'market_value' not in df.columns:
        if 'quantity' in df.columns and 'current_price' in df.columns:
            df['market_value'] = df['quantity'] * df['current_price']
        elif 'qty' in df.columns and 'market_value' not in df.columns:
            logger.warning("Cannot calculate market_value: missing price information")
    
    # Validate numeric portfolio columns
    portfolio_numeric_cols = ['quantity', 'qty', 'market_value', 'cost_basis', 
                             'unrealized_pnl', 'unrealized_pnl_percent']
    available_portfolio_cols = [col for col in portfolio_numeric_cols if col in df.columns]
    
    if available_portfolio_cols:
        df = validate_numeric_columns(df, available_portfolio_cols)
    
    return df

def ensure_minimum_data_length(df: pd.DataFrame, min_length: int = 20, 
                               function_name: str = "") -> pd.DataFrame:
    """
    Ensure DataFrame has minimum required length for calculations.
    
    Args:
        df: Input DataFrame
        min_length: Minimum required number of rows
        function_name: Name of calling function for error messages
        
    Returns:
        pd.DataFrame: Validated DataFrame
        
    Raises:
        ValueError: If DataFrame doesn't meet minimum length requirement
    """
    if len(df) < min_length:
        raise ValueError(
            f"Insufficient data for {function_name}: need at least {min_length} rows, got {len(df)}"
        )
    
    return df

def validate_date_column(df: pd.DataFrame, date_column: str = 'date') -> pd.DataFrame:
    """
    Validate and standardize date/timestamp column.
    
    Args:
        df: Input DataFrame
        date_column: Name of the date column
        
    Returns:
        pd.DataFrame: DataFrame with validated date column
    """
    df = df.copy()
    
    if date_column in df.columns:
        try:
            df[date_column] = pd.to_datetime(df[date_column])
            # Sort by date to ensure chronological order
            df = df.sort_values(date_column).reset_index(drop=True)
        except Exception as e:
            logger.warning(f"Could not parse date column {date_column}: {str(e)}")
    
    return df

def clean_and_validate_data(data: Any, required_columns: List[str] = None, 
                           min_length: int = 1, function_name: str = "") -> pd.DataFrame:
    """
    Comprehensive data cleaning and validation pipeline.
    
    Args:
        data: Input data in any supported format
        required_columns: List of required columns
        min_length: Minimum required number of rows
        function_name: Name of calling function for error messages
        
    Returns:
        pd.DataFrame: Fully validated and cleaned DataFrame
    """
    # Step 1: Basic validation and conversion
    df = validate_and_convert_data(data, required_columns)
    
    # Step 2: Ensure minimum length
    df = ensure_minimum_data_length(df, min_length, function_name)
    
    # Step 3: Validate price data integrity if OHLC columns present
    price_cols = ['open', 'high', 'low', 'close', 'o', 'h', 'l', 'c']
    if any(col in df.columns for col in price_cols):
        df = validate_price_data_integrity(df)
    
    # Step 4: Validate date column if present
    if 'date' in df.columns or 'timestamp' in df.columns:
        date_col = 'date' if 'date' in df.columns else 'timestamp'
        df = validate_date_column(df, date_col)
    
    return df