#!/usr/bin/env python3
"""
Fix incorrect function names in experimental.json workflows.
Map non-existent functions to correct MCP function names.
"""

import json
import sys
import os

# Available MCP functions from both servers
ANALYTICS_FUNCTIONS = [
    # Returns calculations
    'calculate_daily_returns', 'calculate_weekly_returns', 'calculate_monthly_returns',
    'calculate_annualized_return', 'calculate_cumulative_returns', 'return_distribution_stats',
    
    # Volatility calculations
    'calculate_rolling_volatility', 'calculate_realized_volatility', 'analyze_volatility_clustering',
    'calculate_downside_volatility', 'volatility_regime_analysis',
    
    # Correlation analysis
    'calculate_correlation_matrix', 'calculate_rolling_correlation', 'calculate_downside_correlation',
    'correlation_significance_test', 'portfolio_correlation_analysis',
    
    # Rolling metrics
    'calculate_rolling_skewness', 'calculate_rolling_kurtosis', 'calculate_rolling_sharpe',
    'calculate_rolling_beta', 'calculate_rolling_information_ratio', 'calculate_rolling_max_drawdown',
    
    # Trend analysis
    'linear_trend_analysis', 'trend_breakout_analysis', 'trend_momentum_analysis', 'trend_reversal_signals',
    
    # Moving averages
    'calculate_sma', 'calculate_ema', 'moving_average_crossovers',
    'moving_average_envelope', 'adaptive_moving_average',
    
    # Gap analysis
    'identify_gaps', 'gap_fill_analysis', 'gap_continuation_analysis', 'island_reversal_detection',
    
    # Event-driven analysis
    'analyze_economic_sensitivity', 'news_sensitivity_scoring', 'earnings_announcement_analysis',
    
    # Relative strength analysis
    'calculate_relative_strength', 'calculate_rolling_relative_strength',
    
    # Pattern analysis
    'identify_consecutive_patterns', 'analyze_rebound_after_down_days',
    
    # Range analysis
    'calculate_weekly_range_tightness', 'calculate_daily_range_metrics',
    
    # New consolidated functions
    'calculate_risk_metrics', 'identify_trading_patterns', 'calculate_statistical_significance',
    'analyze_volume_patterns', 'calculate_performance_metrics'
]

FINANCIAL_FUNCTIONS = [
    # Alpaca Trading
    'alpaca-trading_account', 'alpaca-trading_positions', 'alpaca-trading_orders',
    'alpaca-trading_portfolio-history', 'alpaca-trading_watchlists', 'alpaca-trading_account-activities',
    'alpaca-trading_assets', 'alpaca-trading_calendar', 'alpaca-trading_clock',
    'alpaca-trading_options-contracts', 'alpaca-trading_corporate-actions', 'alpaca-trading_wallets',
    
    # Alpaca Market Data
    'alpaca-market_stocks-bars', 'alpaca-market_stocks-quotes-latest', 'alpaca-market_stocks-trades-latest',
    'alpaca-market_stocks-snapshots', 'alpaca-market_options-quotes-latest', 'alpaca-market_options-trades-latest',
    'alpaca-market_options-snapshots', 'alpaca-market_crypto-bars', 'alpaca-market_forex-rates',
    'alpaca-market_screener-most-actives', 'alpaca-market_screener-top-gainers', 'alpaca-market_screener-top-losers',
    'alpaca-market_news', 'alpaca-market_corporate-actions', 'alpaca-market_stocks-auctions',
    
    # EODHD
    'eodhd_eod-data', 'eodhd_real-time', 'eodhd_fundamentals', 'eodhd_dividends', 'eodhd_splits',
    'eodhd_technical-indicators', 'eodhd_screener', 'eodhd_search', 'eodhd_exchanges',
    'eodhd_etf-holdings', 'eodhd_insider-transactions', 'eodhd_short-interest',
    'eodhd_macro-indicators', 'eodhd_earnings-calendar'
]

ALL_FUNCTIONS = ANALYTICS_FUNCTIONS + FINANCIAL_FUNCTIONS

# Mapping of incorrect function names to correct ones
FUNCTION_CORRECTIONS = {
    # Non-existent functions that were used incorrectly
    'calculate_trend_analysis': 'linear_trend_analysis',
    'client_compute': None,  # Remove this as it's not a real function
    'calculate_volume_analysis': 'analyze_volume_patterns',
    'calculate_pattern_analysis': 'identify_trading_patterns',
    'calculate_technical_indicators': 'eodhd_technical-indicators',
    'calculate_portfolio_analysis': 'alpaca-trading_portfolio-history',
    'calculate_market_analysis': 'alpaca-market_stocks-snapshots',
    'analyze_earnings_impact': 'earnings_announcement_analysis',
    'calculate_options_analysis': 'alpaca-market_options-snapshots',
    'analyze_sector_performance': 'calculate_relative_strength',
    'calculate_insider_analysis': 'eodhd_insider-transactions',
    'analyze_short_interest': 'eodhd_short-interest',
    'calculate_fundamental_analysis': 'eodhd_fundamentals',
    'analyze_dividend_yield': 'eodhd_dividends',
    'calculate_split_analysis': 'eodhd_splits',
    'analyze_macro_impact': 'eodhd_macro-indicators'
}

def fix_experimental_json():
    """Fix function names in experimental.json"""
    
    # Load experimental.json
    exp_file = '../data/experimental.json'
    if not os.path.exists(exp_file):
        print(f"Error: {exp_file} not found")
        return
    
    with open(exp_file, 'r') as f:
        data = json.load(f)
    
    corrections_made = 0
    total_steps = 0
    removed_steps = 0
    
    print("Fixing function names in experimental.json...")
    
    for item in data:
        if 'workflow' in item:
            new_workflow = []
            for step in item['workflow']:
                total_steps += 1
                
                if isinstance(step, dict) and 'function' in step:
                    func_name = step['function']
                    
                    # Check if function exists
                    if func_name in ALL_FUNCTIONS:
                        # Function is correct
                        new_workflow.append(step)
                    elif func_name in FUNCTION_CORRECTIONS:
                        # Apply correction
                        corrected_func = FUNCTION_CORRECTIONS[func_name]
                        if corrected_func is not None:
                            step['function'] = corrected_func
                            new_workflow.append(step)
                            corrections_made += 1
                            print(f"  Corrected: {func_name} -> {corrected_func}")
                        else:
                            # Remove step with invalid function
                            removed_steps += 1
                            print(f"  Removed step with invalid function: {func_name}")
                    else:
                        # Unknown function - try to map to a reasonable alternative
                        if 'risk' in func_name.lower():
                            step['function'] = 'calculate_risk_metrics'
                            corrections_made += 1
                            print(f"  Mapped risk function: {func_name} -> calculate_risk_metrics")
                        elif 'pattern' in func_name.lower():
                            step['function'] = 'identify_trading_patterns'
                            corrections_made += 1
                            print(f"  Mapped pattern function: {func_name} -> identify_trading_patterns")
                        elif 'volume' in func_name.lower():
                            step['function'] = 'analyze_volume_patterns'
                            corrections_made += 1
                            print(f"  Mapped volume function: {func_name} -> analyze_volume_patterns")
                        elif 'performance' in func_name.lower():
                            step['function'] = 'calculate_performance_metrics'
                            corrections_made += 1
                            print(f"  Mapped performance function: {func_name} -> calculate_performance_metrics")
                        else:
                            # Keep the step but flag it
                            new_workflow.append(step)
                            print(f"  Warning: Unknown function kept: {func_name}")
                else:
                    # Step without function field - keep as is
                    new_workflow.append(step)
            
            item['workflow'] = new_workflow
    
    # Save the corrected file
    with open(exp_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\nSummary:")
    print(f"  Total workflow steps: {total_steps}")
    print(f"  Corrections made: {corrections_made}")
    print(f"  Steps removed: {removed_steps}")
    print(f"  File updated: {exp_file}")

def validate_functions():
    """Validate that all functions in experimental.json exist"""
    
    exp_file = '../data/experimental.json'
    with open(exp_file, 'r') as f:
        data = json.load(f)
    
    used_functions = set()
    missing_functions = set()
    
    for item in data:
        if 'workflow' in item:
            for step in item['workflow']:
                if isinstance(step, dict) and 'function' in step:
                    func_name = step['function']
                    used_functions.add(func_name)
                    
                    if func_name not in ALL_FUNCTIONS:
                        missing_functions.add(func_name)
    
    print(f"\nValidation Results:")
    print(f"  Total unique functions used: {len(used_functions)}")
    print(f"  Missing functions: {len(missing_functions)}")
    
    if missing_functions:
        print("\nMissing functions:")
        for func in sorted(missing_functions):
            print(f"  - {func}")
    else:
        print("\nAll functions are valid!")

if __name__ == "__main__":
    fix_experimental_json()
    validate_functions()