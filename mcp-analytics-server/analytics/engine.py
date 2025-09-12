"""
Clean Analytics Engine

This is a completely new, well-organized analytics engine that exposes sophisticated
technical analysis functions through a clean MCP interface.

Architecture:
- Core technical indicators (36 functions)
- Crossover detection systems (10 functions) 
- Advanced pattern recognition (4 functions)
- Clean error handling and validation
- Consistent input/output formats
- Professional-grade implementations

Total: 50 high-quality technical analysis functions
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Union, Optional
import json
from datetime import datetime

# Import our clean technical analysis modules
from .technical import (
    # Core Indicators
    sma, ema, rsi, macd, bollinger_bands, stochastic, atr, adx,
    williams_r, cci, obv, vwap, keltner_channels, donchian_channels,
    
    # Crossovers
    moving_average_crossover, macd_crossover, rsi_level_cross,
    stochastic_crossover, price_channel_breakout,
    
    # Patterns
    bullish_confluence, bearish_confluence, squeeze_pattern,
    trend_continuation_pattern,
    
    # Utilities
    get_function_categories, get_all_functions, get_function_count
)


class CleanAnalyticsEngine:
    """
    Clean, professional-grade analytics engine for technical analysis
    """
    
    def __init__(self):
        """Initialize the analytics engine"""
        self.function_registry = self._build_function_registry()
        self.categories = get_function_categories()
        
    def _build_function_registry(self) -> Dict[str, callable]:
        """Build the complete function registry with all 50 technical analysis functions"""
        from .technical import ALL_TECHNICAL_FUNCTIONS
        return ALL_TECHNICAL_FUNCTIONS
    
    def list_all_functions(self) -> Dict[str, Any]:
        """
        List all available functions organized by category
        
        Returns:
            Dictionary with categorized function information
        """
        counts = get_function_count()
        
        return {
            'total_functions': counts['total'],
            'categories': {
                'core_indicators': {
                    'count': counts['core_indicators'],
                    'subcategories': self.categories['core_indicators']
                },
                'crossover_detection': {
                    'count': counts['crossovers'],
                    'functions': self.categories['crossovers']
                },
                'pattern_recognition': {
                    'count': counts['patterns'],
                    'functions': self.categories['patterns']
                }
            },
            'all_function_names': sorted(list(self.function_registry.keys()))
        }
    
    def execute_function(self, function_name: str, data: Any, **kwargs) -> Dict[str, Any]:
        """
        Execute a technical analysis function
        
        Args:
            function_name: Name of the function to execute
            data: Input data (dict, list, or pandas DataFrame/Series)
            **kwargs: Additional function parameters
            
        Returns:
            Dictionary with function results and metadata
        """
        try:
            # Validate function exists
            if function_name not in self.function_registry:
                return self._error_response(
                    function_name,
                    f"Function '{function_name}' not found",
                    available_functions=list(self.function_registry.keys())
                )
            
            # Convert data to appropriate format
            processed_data = self._process_input_data(data, function_name)
            if isinstance(processed_data, dict) and 'error' in processed_data:
                return processed_data
            
            # Execute the function
            func = self.function_registry[function_name]
            result = func(processed_data, **kwargs)
            
            # Format response
            return self._success_response(function_name, result, kwargs)
            
        except Exception as e:
            return self._error_response(function_name, str(e), kwargs)
    
    def _process_input_data(self, data: Any, function_name: str) -> Union[pd.DataFrame, pd.Series, Dict[str, Any]]:
        """
        Process and validate input data
        
        Args:
            data: Raw input data
            function_name: Name of the function (for context)
            
        Returns:
            Processed pandas DataFrame/Series or error dict
        """
        try:
            if isinstance(data, (pd.DataFrame, pd.Series)):
                return data
            
            if isinstance(data, list):
                if len(data) == 0:
                    return self._error_response(function_name, "Empty data list provided")
                
                # Handle list of dictionaries (OHLCV data)
                if isinstance(data[0], dict):
                    df = pd.DataFrame(data)
                    # Standardize column names
                    column_mapping = {
                        'c': 'close', 'o': 'open', 'h': 'high', 'l': 'low', 'v': 'volume',
                        'Close': 'close', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Volume': 'volume'
                    }
                    df = df.rename(columns=column_mapping)
                    return df
                
                # Handle list of numbers (price series)
                else:
                    return pd.Series(data, name='close')
            
            if isinstance(data, dict):
                # Handle single OHLCV record
                if any(key in data for key in ['c', 'close', 'o', 'open']):
                    df = pd.DataFrame([data])
                    column_mapping = {
                        'c': 'close', 'o': 'open', 'h': 'high', 'l': 'low', 'v': 'volume'
                    }
                    df = df.rename(columns=column_mapping)
                    return df
                else:
                    return self._error_response(function_name, "Invalid dictionary format")
            
            return self._error_response(function_name, f"Unsupported data type: {type(data)}")
            
        except Exception as e:
            return self._error_response(function_name, f"Data processing error: {str(e)}")
    
    def _success_response(self, function_name: str, result: Any, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Format successful function response"""
        return {
            'success': True,
            'function': function_name,
            'result': self._serialize_result(result),
            'parameters': parameters,
            'timestamp': datetime.now().isoformat(),
            'engine': 'CleanAnalyticsEngine'
        }
    
    def _error_response(self, function_name: str, error_message: str, 
                       parameters: Optional[Dict[str, Any]] = None,
                       **context) -> Dict[str, Any]:
        """Format error response"""
        return {
            'success': False,
            'function': function_name,
            'error': error_message,
            'parameters': parameters or {},
            'context': context,
            'timestamp': datetime.now().isoformat(),
            'engine': 'CleanAnalyticsEngine'
        }
    
    def _serialize_result(self, result: Any) -> Any:
        """Convert pandas objects and numpy types to JSON-serializable formats"""
        if isinstance(result, pd.DataFrame):
            return {
                'type': 'DataFrame',
                'data': result.to_dict('records'),
                'columns': list(result.columns),
                'index': list(result.index) if hasattr(result.index, 'tolist') else list(range(len(result)))
            }
        elif isinstance(result, pd.Series):
            return {
                'type': 'Series',
                'data': result.to_list(),
                'index': list(result.index) if hasattr(result.index, 'tolist') else list(range(len(result))),
                'name': result.name
            }
        elif isinstance(result, np.ndarray):
            return result.tolist()
        elif isinstance(result, (np.integer, np.floating)):
            return float(result)
        elif isinstance(result, dict):
            # Recursively serialize dictionary values
            return {k: self._serialize_result(v) for k, v in result.items()}
        elif isinstance(result, list):
            return [self._serialize_result(item) for item in result]
        else:
            return result
    
    def get_function_info(self, function_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific function
        
        Args:
            function_name: Name of the function
            
        Returns:
            Dictionary with function information and documentation
        """
        if function_name not in self.function_registry:
            return self._error_response(function_name, "Function not found")
        
        func = self.function_registry[function_name]
        
        # Determine category
        category = 'unknown'
        for cat, subcats in self.categories.items():
            if cat == 'core_indicators':
                for subcat, funcs in subcats.items():
                    if function_name in funcs:
                        category = f"core_indicators.{subcat}"
                        break
            elif isinstance(subcats, list) and function_name in subcats:
                category = cat
                break
        
        return {
            'function_name': function_name,
            'category': category,
            'docstring': func.__doc__,
            'available': True,
            'module': func.__module__,
            'signature': str(func.__annotations__) if hasattr(func, '__annotations__') else 'No type hints available'
        }


# Create a global instance for easy access
clean_analytics = CleanAnalyticsEngine()


# Export the main engine class and instance
__all__ = ['CleanAnalyticsEngine', 'clean_analytics']