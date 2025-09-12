#!/usr/bin/env python3
"""
Verification script to check if all workflow compute/engine requirements are supported.
"""

import json
from analytics.main import AnalyticsEngine


def check_workflow_support():
    """Check if analytics engine supports all workflow requirements."""
    
    # Load experimental workflows
    with open('../data/experimental.json', 'r') as f:
        workflows = json.load(f)
    
    engine = AnalyticsEngine()
    available_functions = engine.list_functions()
    all_functions = []
    for category, funcs in available_functions.items():
        all_functions.extend(funcs)
    
    print("=" * 80)
    print("WORKFLOW ANALYTICS SUPPORT VERIFICATION")
    print("=" * 80)
    
    # Required functions based on workflow analysis
    required_functions = {
        "calculate_daily_returns": "Daily return calculations for all price-based analysis",
        "analyze_economic_sensitivity": "CPI/economic event performance analysis",
        "calculate_rolling_skewness": "Position rolling skew analysis",
        "linear_trend_analysis": "200-day trend steepness analysis",
        "calculate_rolling_volatility": "ETF volatility ranking and analysis",
        "identify_gaps": "Gap analysis and gap fill detection",
        "calculate_correlation_matrix": "Holdings correlation analysis",
        "calculate_rolling_max_drawdown": "Risk metrics and drawdown analysis",
        "identify_consecutive_patterns": "Consecutive up/down day patterns",
        "calculate_weekly_range_tightness": "Weekly range tightness analysis",
        "calculate_relative_strength": "Relative strength vs benchmarks",
        "calculate_sma": "Moving average calculations for technical analysis"
    }
    
    print(f"📊 AVAILABLE FUNCTION CATEGORIES: {len(available_functions)}")
    for category, funcs in available_functions.items():
        print(f"   • {category.upper()}: {len(funcs)} functions")
    
    print(f"\n🔍 TOTAL AVAILABLE FUNCTIONS: {len(all_functions)}")
    
    print(f"\n✅ WORKFLOW REQUIREMENT VERIFICATION:")
    supported = 0
    for func, description in required_functions.items():
        if func in all_functions:
            print(f"   ✓ {func} - {description}")
            supported += 1
        else:
            print(f"   ✗ {func} - {description} [MISSING]")
    
    print(f"\n📈 SUPPORT COVERAGE: {supported}/{len(required_functions)} ({supported/len(required_functions)*100:.1f}%)")
    
    # Workflow analysis
    print(f"\n📋 WORKFLOW ANALYSIS:")
    engine_steps = 0
    compute_steps = 0
    
    for workflow in workflows:
        if 'workflow' in workflow:
            for step in workflow['workflow']:
                if step.get('type') == 'engine':
                    engine_steps += 1
                elif step.get('type') == 'compute':
                    compute_steps += 1
    
    print(f"   • Total workflows analyzed: {len(workflows)}")
    print(f"   • Engine steps requiring analytics: {engine_steps}")
    print(f"   • Compute steps for formatting: {compute_steps}")
    print(f"   • Total analytical operations: {engine_steps + compute_steps}")
    
    # Test a few key functions
    print(f"\n🧪 FUNCTION TESTING:")
    
    # Test 1: Daily returns
    try:
        test_data = [
            {"t": "2024-01-01", "o": 100, "h": 102, "l": 98, "c": 101},
            {"t": "2024-01-02", "o": 101, "h": 103, "l": 99, "c": 102}
        ]
        result = engine.execute_function("calculate_daily_returns", price_data=test_data)
        if 'error' not in result:
            print(f"   ✓ Daily returns calculation: Working")
        else:
            print(f"   ✗ Daily returns calculation: {result['error']}")
    except Exception as e:
        print(f"   ✗ Daily returns calculation: {str(e)}")
    
    # Test 2: Trend analysis
    try:
        test_prices = [100, 101, 102, 103, 104, 105]
        result = engine.execute_function("linear_trend_analysis", prices=test_prices)
        if 'error' not in result:
            print(f"   ✓ Linear trend analysis: Working")
        else:
            print(f"   ✗ Linear trend analysis: {result['error']}")
    except Exception as e:
        print(f"   ✗ Linear trend analysis: {str(e)}")
    
    # Test 3: Economic sensitivity
    try:
        result = engine.execute_function("analyze_economic_sensitivity", 
                                       price_data=test_data, 
                                       event_dates=["2024-01-01"])
        if 'error' not in result:
            print(f"   ✓ Economic sensitivity analysis: Working")
        else:
            print(f"   ✗ Economic sensitivity analysis: {result['error']}")
    except Exception as e:
        print(f"   ✗ Economic sensitivity analysis: {str(e)}")
    
    print(f"\n" + "=" * 80)
    if supported == len(required_functions):
        print("🎉 ALL WORKFLOW REQUIREMENTS ARE FULLY SUPPORTED!")
        print("The MCP analytics server is ready to handle all experimental workflows.")
    else:
        print(f"⚠️  {len(required_functions) - supported} FUNCTIONS NEED IMPLEMENTATION")
        print("Some workflow steps may require additional analytics functions.")
    print("=" * 80)
    
    return supported == len(required_functions)


if __name__ == "__main__":
    check_workflow_support()