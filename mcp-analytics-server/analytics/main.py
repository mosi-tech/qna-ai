"""
Main Analytics Engine Interface

Consolidated interface for all financial analysis functions
From financial-analysis-function-library.json - using libraries from requirements.txt
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Union, Optional, Callable
import warnings
warnings.filterwarnings('ignore')

# Import all function registries - no code duplication
from .utils.data_utils import DATA_UTILS_FUNCTIONS
from .performance.metrics import PERFORMANCE_METRICS_FUNCTIONS
from .indicators.technical import TECHNICAL_INDICATORS_FUNCTIONS
from .portfolio.optimization import PORTFOLIO_OPTIMIZATION_FUNCTIONS
from .portfolio.simulation import PORTFOLIO_SIMULATION_FUNCTIONS
from .risk.metrics import RISK_METRICS_FUNCTIONS


class AnalyticsEngine:
    """
    Main analytics engine that consolidates all financial analysis functions.
    
    From financial-analysis-function-library.json
    Uses library-first approach - empyrical, TA-Lib, PyPortfolioOpt, scipy
    No manual calculations or code duplication
    """
    
    def __init__(self):
        """Initialize the analytics engine with all function registries."""
        self.functions = {}
        
        # Register all function categories - using libraries from requirements.txt
        self._register_functions("data_utils", DATA_UTILS_FUNCTIONS)
        self._register_functions("performance", PERFORMANCE_METRICS_FUNCTIONS)
        self._register_functions("indicators", TECHNICAL_INDICATORS_FUNCTIONS)
        self._register_functions("portfolio_optimization", PORTFOLIO_OPTIMIZATION_FUNCTIONS)
        self._register_functions("portfolio_simulation", PORTFOLIO_SIMULATION_FUNCTIONS)
        self._register_functions("risk", RISK_METRICS_FUNCTIONS)
    
    def _register_functions(self, category: str, function_dict: Dict[str, Callable]):
        """Register functions from a category."""
        for name, func in function_dict.items():
            self.functions[name] = {
                "function": func,
                "category": category,
                "source": "financial-analysis-function-library.json",
                "library_based": True
            }
    
    def list_functions(self, category: Optional[str] = None) -> Dict[str, List[str]]:
        """
        List all available functions, optionally filtered by category.
        
        Args:
            category: Optional category filter
            
        Returns:
            Dict: Functions organized by category
        """
        if category:
            return {
                category: [name for name, info in self.functions.items() 
                          if info["category"] == category]
            }
        
        # Group by category
        by_category = {}
        for name, info in self.functions.items():
            cat = info["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(name)
        
        return by_category
    
    def get_function_info(self, function_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific function.
        
        Args:
            function_name: Name of the function
            
        Returns:
            Dict: Function information
        """
        return self.functions.get(function_name)
    
    def call_function(self, function_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Call a function by name with provided arguments.
        
        Args:
            function_name: Name of the function to call
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Dict: Function result
        """
        if function_name not in self.functions:
            return {
                "success": False,
                "error": f"Function '{function_name}' not found. Available functions: {list(self.functions.keys())}"
            }
        
        try:
            func_info = self.functions[function_name]
            result = func_info["function"](*args, **kwargs)
            
            # Add metadata
            if isinstance(result, dict) and result.get("success", True):
                result["function_info"] = {
                    "name": function_name,
                    "category": func_info["category"],
                    "source": func_info["source"],
                    "library_based": func_info["library_based"]
                }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Function '{function_name}' failed: {str(e)}",
                "function_name": function_name
            }
    
    def get_all_function_names(self) -> List[str]:
        """Get all function names - compatibility with old interface."""
        return list(self.functions.keys())
    
    def get_function_count(self) -> Dict[str, int]:
        """Get function counts by category - compatibility with old interface."""
        counts = {}
        by_category = {}
        
        for name, info in self.functions.items():
            cat = info["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(name)
        
        for category, func_list in by_category.items():
            counts[category] = len(func_list)
        
        counts["total"] = len(self.functions)
        return counts
    
    def execute_function(self, name: str, **kwargs) -> Dict[str, Any]:
        """Execute function - compatibility with old interface."""
        return self.call_function(name, **kwargs)
    
    def analyze_portfolio(self, prices: Union[pd.DataFrame, Dict[str, Any]], 
                         benchmark_prices: Optional[Union[pd.Series, Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Comprehensive portfolio analysis using all available functions.
        
        From financial-analysis-function-library.json
        Combines multiple analysis functions - all using libraries from requirements.txt
        
        Args:
            prices: Portfolio price data
            benchmark_prices: Optional benchmark data
            
        Returns:
            Dict: Comprehensive analysis results
        """
        try:
            results = {
                "analysis_type": "comprehensive_portfolio_analysis",
                "library_based": True,
                "source": "financial-analysis-function-library.json"
            }
            
            # Convert prices to returns for analysis
            if isinstance(prices, dict):
                price_df = pd.DataFrame(prices)
            else:
                price_df = prices.copy()
            
            returns_df = price_df.pct_change().dropna()
            
            if len(price_df.columns) == 1:
                # Single asset analysis
                asset_name = price_df.columns[0]
                price_series = price_df[asset_name]
                return_series = returns_df[asset_name]
                
                # Performance metrics using empyrical
                results["performance"] = self.call_function("calculate_returns_metrics", return_series)
                results["risk"] = self.call_function("calculate_risk_metrics", return_series)
                
                # Technical indicators using TA-Lib
                results["sma_20"] = self.call_function("calculate_sma", price_series, 20)
                results["ema_12"] = self.call_function("calculate_ema", price_series, 12)
                results["rsi"] = self.call_function("calculate_rsi", price_series)
                results["macd"] = self.call_function("calculate_macd", price_series)
                
                # Risk analysis using empyrical/scipy
                results["var_analysis"] = self.call_function("calculate_var", return_series)
                results["cvar_analysis"] = self.call_function("calculate_cvar", return_series)
                
                # Benchmark comparison if provided
                if benchmark_prices is not None:
                    benchmark_returns = self.call_function("prices_to_returns", benchmark_prices)
                    if benchmark_returns.get("success", True):
                        benchmark_return_series = benchmark_returns.get("data", benchmark_returns)
                        results["benchmark_comparison"] = self.call_function(
                            "calculate_benchmark_metrics", return_series, benchmark_return_series
                        )
                        results["beta_analysis"] = self.call_function(
                            "calculate_beta_analysis", return_series, benchmark_return_series
                        )
            
            else:
                # Multi-asset portfolio analysis
                
                # Equal weight portfolio for analysis
                portfolio_returns = returns_df.mean(axis=1)
                
                # Performance metrics using empyrical
                results["performance"] = self.call_function("calculate_returns_metrics", portfolio_returns)
                results["risk"] = self.call_function("calculate_risk_metrics", portfolio_returns)
                
                # Portfolio optimization using PyPortfolioOpt
                results["max_sharpe_optimization"] = self.call_function("optimize_max_sharpe", price_df)
                results["min_vol_optimization"] = self.call_function("optimize_min_volatility", price_df)
                results["efficient_frontier"] = self.call_function("calculate_efficient_frontier", price_df, 10)
                
                # Risk analysis using empyrical/scipy
                results["correlation_analysis"] = self.call_function("calculate_correlation_analysis", returns_df)
                results["var_analysis"] = self.call_function("calculate_var", portfolio_returns)
                results["stress_test"] = self.call_function("stress_test_portfolio", portfolio_returns)
                
                # Strategy simulation using empyrical
                if len(price_df) > 20:  # Enough data for simulation
                    results["dca_simulation"] = self.call_function(
                        "simulate_dca_strategy", price_df.iloc[:, 0], 1000, "M"
                    )
            
            results["analysis_timestamp"] = pd.Timestamp.now().isoformat()
            results["n_assets"] = len(price_df.columns)
            results["n_observations"] = len(price_df)
            
            return results
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Comprehensive portfolio analysis failed: {str(e)}",
                "analysis_type": "comprehensive_portfolio_analysis"
            }


def get_all_functions() -> Dict[str, Dict[str, Any]]:
    """
    Get all available functions with their metadata.
    
    Returns:
        Dict: All functions with metadata
    """
    engine = AnalyticsEngine()
    
    function_list = {}
    for name, info in engine.functions.items():
        function_list[name] = {
            "category": info["category"],
            "source": info["source"],
            "library_based": info["library_based"],
            "description": f"Function from {info['source']} - uses libraries from requirements.txt"
        }
    
    return function_list


# Create global engine instance
analytics_engine = AnalyticsEngine()

# Export main functions for direct access
def calculate_sma(data, period=20):
    """Calculate SMA using TA-Lib - from financial-analysis-function-library.json"""
    return analytics_engine.call_function("calculate_sma", data, period)

def calculate_rsi(data, period=14):
    """Calculate RSI using TA-Lib - from financial-analysis-function-library.json"""
    return analytics_engine.call_function("calculate_rsi", data, period)

def optimize_portfolio(prices, method="max_sharpe"):
    """Optimize portfolio using PyPortfolioOpt - from financial-analysis-function-library.json"""
    return analytics_engine.call_function("optimize_portfolio", prices, method)

def calculate_risk_metrics(returns):
    """Calculate risk metrics using empyrical - from financial-analysis-function-library.json"""
    return analytics_engine.call_function("calculate_risk_metrics", returns)

def simulate_dca_strategy(prices, amount=1000, frequency="M"):
    """Simulate DCA using empyrical - from financial-analysis-function-library.json"""
    return analytics_engine.call_function("simulate_dca_strategy", prices, amount, frequency)


# Registry of all available functions - consolidated and library-based
ALL_ANALYTICS_FUNCTIONS = get_all_functions()

if __name__ == "__main__":
    # Example usage
    engine = AnalyticsEngine()
    
    print("Analytics Engine - Library-Based Financial Analysis")
    print("=================================================")
    print(f"Total functions available: {len(engine.functions)}")
    print()
    
    # List functions by category
    functions_by_category = engine.list_functions()
    for category, function_names in functions_by_category.items():
        print(f"{category.upper()}:")
        for func_name in function_names:
            print(f"  - {func_name}")
        print()
    
    print("All functions use libraries from requirements.txt")
    print("Source: financial-analysis-function-library.json")
    print("No code duplication - library-first approach")