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

# Import portfolio analysis functions using new categorical structure from financial-analysis-function-library.json
from .time_series_processing import (
    calculateReturns, calculateLogReturns, calculateCumulativeReturns,
    calculateRollingVolatility, calculateBeta, calculateCorrelation, calculateCorrelationMatrix,
    calculateSMA, calculateEMA, detectSMACrossover, detectEMACrossover,
    TIME_SERIES_PROCESSING_FUNCTIONS
)

from .performance_analysis import (
    calculateSharpeRatio, calculateSortinoRatio, calculateCAGR,
    calculateInformationRatio, calculateTreynorRatio, calculateCalmarRatio, calculateAlpha,
    calculateAnnualizedReturn, calculateAnnualizedVolatility, calculateTotalReturn, calculateWinRate,
    PERFORMANCE_ANALYSIS_FUNCTIONS
)

from .risk_analysis import (
    calculateMaxDrawdown, calculateVaR, calculateCVaR, calculateDownsideDeviation,
    calculateUpsideCapture, calculateDownsideCapture, calculateSkewness, calculateKurtosis,
    RISK_ANALYSIS_FUNCTIONS
)

from .strategy_simulation import (
    backtestTechnicalStrategy, monteCarloSimulation, backtestBuyAndHold, compareStrategies,
    STRATEGY_SIMULATION_FUNCTIONS
)

# Import new analytics categories from financial-analysis-function-library.json
from .statistical_analysis import (
    calculatePercentile, calculateHerfindahlIndex, calculateTrackingError,
    calculateOmegaRatio, calculateBestWorstPeriods, calculateZScore,
    STATISTICAL_ANALYSIS_FUNCTIONS
)

from .comparison_analysis import (
    comparePerformanceMetrics, compareRiskMetrics, compareDrawdowns,
    compareVolatilityProfiles, compareExpenseRatios,
    COMPARISON_ANALYSIS_FUNCTIONS
)

from .portfolio_analysis import (
    calculatePortfolioMetrics, analyzePortfolioConcentration, 
    calculatePortfolioBeta, calculateActiveShare,
    PORTFOLIO_ANALYSIS_FUNCTIONS
)

# Import legacy portfolio functions for backward compatibility
from .portfolio.data_processing import (
    calculate_portfolio_returns, filter_date_range, resample_frequency,
    align_data_series, fill_missing_data,
    DATA_PROCESSING_FUNCTIONS
)


class AnalyticsEngine:
    """
    Main Analytics Engine - Updated to use our comprehensive technical analysis system
    
    This class provides backward compatibility with the old interface while 
    using our new clean technical analysis system under the hood.
    """
    
    def __init__(self):
        """Initialize with our new clean analytics engine and portfolio functions"""
        self.clean_engine = clean_analytics
        self.function_registry = self.clean_engine.function_registry.copy()
        
        # Add portfolio analysis functions from library.json using new categorical structure
        self.function_registry.update(TIME_SERIES_PROCESSING_FUNCTIONS)
        self.function_registry.update(PERFORMANCE_ANALYSIS_FUNCTIONS)
        self.function_registry.update(RISK_ANALYSIS_FUNCTIONS)
        self.function_registry.update(STRATEGY_SIMULATION_FUNCTIONS)
        
        # Add new analytics categories from financial-analysis-function-library.json
        self.function_registry.update(STATISTICAL_ANALYSIS_FUNCTIONS)
        self.function_registry.update(COMPARISON_ANALYSIS_FUNCTIONS)
        self.function_registry.update(PORTFOLIO_ANALYSIS_FUNCTIONS)
        
        # Add legacy portfolio functions for backward compatibility
        self.function_registry.update(DATA_PROCESSING_FUNCTIONS)
        
    def execute_function(self, function_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a technical analysis or portfolio function
        
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
        
        # Check if function exists in our registry
        if mapped_name not in self.function_registry:
            return {
                'success': False,
                'error': f"Function '{function_name}' not found",
                'function': function_name,
                'available_functions': list(self.function_registry.keys())
            }
        
        # Get the actual function
        func = self.function_registry[mapped_name]
        
        # Check if this is a portfolio function (from library.json)
        portfolio_functions = (set(TIME_SERIES_PROCESSING_FUNCTIONS.keys()) | 
                               set(PERFORMANCE_ANALYSIS_FUNCTIONS.keys()) | 
                               set(RISK_ANALYSIS_FUNCTIONS.keys()) | 
                               set(STRATEGY_SIMULATION_FUNCTIONS.keys()) |
                               set(STATISTICAL_ANALYSIS_FUNCTIONS.keys()) |
                               set(COMPARISON_ANALYSIS_FUNCTIONS.keys()) |
                               set(PORTFOLIO_ANALYSIS_FUNCTIONS.keys()) |
                               set(DATA_PROCESSING_FUNCTIONS.keys()))
        
        if mapped_name in portfolio_functions:
            # Portfolio functions handle their own argument parsing
            try:
                # Handle different argument formats for portfolio functions
                if 'data' in kwargs and mapped_name in ['calculateReturns', 'calculateLogReturns', 'calculateCumulativeReturns', 'calculateRollingVolatility', 'calculateSMA', 'calculateEMA', 'detectSMACrossover', 'detectEMACrossover', 'calculatePercentile', 'calculateHerfindahlIndex', 'calculateOmegaRatio', 'calculateBestWorstPeriods', 'calculateZScore', 'calculateAnnualizedReturn', 'calculateAnnualizedVolatility', 'calculateTotalReturn', 'calculateWinRate', 'calculateSharpeRatio', 'calculateSortinoRatio', 'calculateCalmarRatio']:
                    # These functions expect prices/returns as first argument
                    prices_or_returns = kwargs.pop('data')
                    return func(prices_or_returns, **kwargs)
                elif 'returns' in kwargs and mapped_name in ['calculateBeta', 'calculateCorrelation', 'calculateInformationRatio', 'calculateTreynorRatio', 'calculateTrackingError', 'calculateAlpha']:
                    # These functions expect returns as first argument  
                    returns = kwargs.pop('returns')
                    return func(returns, **kwargs)
                elif 'returns1' in kwargs and mapped_name in ['comparePerformanceMetrics', 'compareRiskMetrics', 'compareVolatilityProfiles']:
                    # Comparison functions expect two return series
                    returns1 = kwargs.pop('returns1')
                    returns2 = kwargs.pop('returns2', kwargs.pop('data', None))
                    return func(returns1, returns2, **kwargs)
                elif 'prices1' in kwargs and mapped_name in ['compareDrawdowns']:
                    # Drawdown comparison expects two price series
                    prices1 = kwargs.pop('prices1')
                    prices2 = kwargs.pop('prices2', kwargs.pop('data', None))
                    return func(prices1, prices2, **kwargs)
                else:
                    # Default behavior
                    return func(**kwargs)
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Portfolio function execution failed: {str(e)}",
                    'function': function_name
                }
        else:
            # Technical analysis functions use the clean analytics engine
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
            
        # Add other technical categories
        result['crossovers'] = categories['crossovers']
        result['patterns'] = categories['patterns']
        
        # Add portfolio analysis categories from library.json using new categorical structure
        result['time_series_processing'] = list(TIME_SERIES_PROCESSING_FUNCTIONS.keys())
        result['performance_analysis'] = list(PERFORMANCE_ANALYSIS_FUNCTIONS.keys())
        result['risk_analysis'] = list(RISK_ANALYSIS_FUNCTIONS.keys())
        result['strategy_simulation'] = list(STRATEGY_SIMULATION_FUNCTIONS.keys())
        
        # Add new analytics categories from financial-analysis-function-library.json
        result['statistical_analysis'] = list(STATISTICAL_ANALYSIS_FUNCTIONS.keys())
        result['comparison_analysis'] = list(COMPARISON_ANALYSIS_FUNCTIONS.keys())
        result['portfolio_analysis'] = list(PORTFOLIO_ANALYSIS_FUNCTIONS.keys())
        
        # Add legacy categories for backward compatibility
        result['data_processing'] = list(DATA_PROCESSING_FUNCTIONS.keys())
        
        return result
    
    def get_function_info(self, function_name: str) -> Dict[str, Any]:
        """Get information about a specific function"""
        return self.clean_engine.get_function_info(function_name)
    
    def get_all_function_names(self) -> List[str]:
        """Get list of all function names"""
        technical_functions = get_all_functions()
        portfolio_functions = list(self.function_registry.keys())
        # Remove duplicates while preserving order
        all_functions = list(dict.fromkeys(technical_functions + portfolio_functions))
        return all_functions
    
    def get_function_count(self) -> Dict[str, int]:
        """Get count of functions by category"""
        technical_counts = get_function_count()
        
        # Add portfolio function counts using new categorical structure
        portfolio_counts = {
            'time_series_processing': len(TIME_SERIES_PROCESSING_FUNCTIONS),
            'performance_analysis': len(PERFORMANCE_ANALYSIS_FUNCTIONS),
            'risk_analysis': len(RISK_ANALYSIS_FUNCTIONS),
            'strategy_simulation': len(STRATEGY_SIMULATION_FUNCTIONS),
            'statistical_analysis': len(STATISTICAL_ANALYSIS_FUNCTIONS),
            'comparison_analysis': len(COMPARISON_ANALYSIS_FUNCTIONS),
            'portfolio_analysis': len(PORTFOLIO_ANALYSIS_FUNCTIONS),
            'data_processing': len(DATA_PROCESSING_FUNCTIONS)  # Legacy compatibility
        }
        
        # Calculate total including portfolio functions
        portfolio_total = sum(portfolio_counts.values())
        total_count = technical_counts.get('total', 0) + portfolio_total
        
        # Merge the counts
        result = technical_counts.copy()
        result.update(portfolio_counts)
        result['total'] = total_count
        result['portfolio_functions'] = portfolio_total
        
        return result


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