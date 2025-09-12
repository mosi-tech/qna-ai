#!/usr/bin/env python3
"""
Main analytics server entry point with comprehensive technical analysis.

This module provides a clean interface to our comprehensive technical analysis system
with 50 professional-grade functions organized into:
- 36 Core Technical Indicators
- 10 Crossover Detection Functions  
- 4 Advanced Pattern Recognition Functions

All functions follow consistent patterns with clean input/output interfaces.
"""

import sys
import json
import argparse
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

# Import our new clean analytics engine
from .engine import CleanAnalyticsEngine, clean_analytics

# Import all technical analysis functions for direct access
from .technical import (
    # Core Indicators - Moving Averages
    sma, ema,
    
    # Core Indicators - Momentum Oscillators
    rsi, stochastic, stochastic_rsi, williams_r, cci, money_flow_index,
    ultimate_oscillator, awesome_oscillator, rate_of_change,
    
    # Core Indicators - Trend
    macd, adx, trix, parabolic_sar, aroon, mass_index,
    dpo, kst, ichimoku, supertrend,
    
    # Core Indicators - Volatility
    bollinger_bands, atr, keltner_channels, donchian_channels,
    
    # Core Indicators - Volume
    obv, vwap, chaikin_money_flow, accumulation_distribution, chaikin_oscillator,
    volume_sma, volume_weighted_moving_average, ease_of_movement, force_index,
    negative_volume_index, positive_volume_index,
    
    # Crossover Detection
    moving_average_crossover, macd_crossover, rsi_level_cross,
    stochastic_crossover, price_channel_breakout,
    
    # Pattern Recognition
    bullish_confluence, bearish_confluence, squeeze_pattern,
    trend_continuation_pattern,
    
    # Utilities
    ALL_TECHNICAL_FUNCTIONS, get_function_categories, get_all_functions,
    get_function_count
)


class AnalyticsEngine:
    """
    Main Analytics Engine - Updated to use our comprehensive technical analysis system
    
    This class provides backward compatibility with the old interface while 
    using our new clean technical analysis system under the hood.
    """
    
    def __init__(self):
        """Initialize with our new clean analytics engine"""
        self.clean_engine = clean_analytics
        self.function_registry = self.clean_engine.function_registry
        
    def execute_function(self, function_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a technical analysis function
        
        Args:
            function_name: Name of the function to execute
            **kwargs: Function arguments
            
        Returns:
            Dictionary with function results
        """
        # Handle legacy function name mappings if needed
        legacy_mappings = {
            'calculate_bollinger_bands': 'bollinger_bands',
            'calculate_rsi': 'rsi',
            'calculate_macd': 'macd',
            'calculate_sma': 'sma',
            'calculate_ema': 'ema',
            'calculate_adx': 'adx',
            'calculate_atr': 'atr',
            'calculate_stochastic': 'stochastic',
            'calculate_williams_r': 'williams_r',
            'calculate_cci': 'cci',
            'calculate_obv': 'obv',
            'calculate_mfi': 'money_flow_index',
            'calculate_parabolic_sar': 'parabolic_sar'
        }
        
        # Map legacy function names to new names
        mapped_name = legacy_mappings.get(function_name, function_name)
        
        # Extract data from kwargs
        data = kwargs.pop('data', kwargs.pop('price_data', None))
        
        if data is None:
            return {
                'success': False,
                'error': f"No data provided for function {function_name}",
                'function': function_name
            }
        
        # Use our clean analytics engine
        return self.clean_engine.execute_function(mapped_name, data, **kwargs)
    
    def list_functions(self) -> Dict[str, List[str]]:
        """
        List all available functions by category
        
        Returns:
            Dictionary with categorized function lists
        """
        categories = get_function_categories()
        result = {}
        
        # Flatten core indicators subcategories
        for subcat, funcs in categories['core_indicators'].items():
            result[subcat] = funcs
            
        # Add other categories
        result['crossovers'] = categories['crossovers']
        result['patterns'] = categories['patterns']
        
        return result
    
    def get_function_info(self, function_name: str) -> Dict[str, Any]:
        """Get information about a specific function"""
        return self.clean_engine.get_function_info(function_name)
    
    def get_all_function_names(self) -> List[str]:
        """Get list of all function names"""
        return get_all_functions()
    
    def get_function_count(self) -> Dict[str, int]:
        """Get count of functions by category"""
        return get_function_count()


# Create global analytics engine instance
analytics_engine = AnalyticsEngine()


def main():
    """Main entry point for command-line usage"""
    parser = argparse.ArgumentParser(description='Financial Analytics Engine')
    parser.add_argument('--list-functions', action='store_true', 
                       help='List all available functions')
    parser.add_argument('--function', type=str, 
                       help='Execute specific function')
    parser.add_argument('--data', type=str, 
                       help='JSON data file path')
    
    args = parser.parse_args()
    
    if args.list_functions:
        functions = analytics_engine.list_functions()
        counts = analytics_engine.get_function_count()
        
        print("📊 Comprehensive Technical Analysis System")
        print("=" * 50)
        print(f"Total Functions: {counts['total']}")
        print()
        
        for category, function_list in functions.items():
            print(f"{category.replace('_', ' ').title()} ({len(function_list)}):")
            for func in function_list:
                print(f"  - {func}")
            print()
                
    elif args.function and args.data:
        try:
            with open(args.data, 'r') as f:
                data = json.load(f)
            
            result = analytics_engine.execute_function(args.function, data=data)
            print(json.dumps(result, indent=2, default=str))
            
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()