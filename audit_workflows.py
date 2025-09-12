#!/usr/bin/env python3
"""
Audit all experimental workflows for MCP compatibility.
Identifies missing functions, data flow issues, and library usage opportunities.
"""

import json
import sys
from pathlib import Path

# Available MCP Functions (based on our current implementation)
AVAILABLE_MCP_FUNCTIONS = {
    # Financial Server (fetch)
    "alpaca-trading_positions",
    "alpaca-trading_account", 
    "alpaca-trading_orders",
    "alpaca-trading_watchlists",
    "alpaca-market_stocks-bars",
    "alpaca-market_stocks-snapshots", 
    "alpaca-market_stocks-quotes-latest",
    "alpaca-market_screener-most-actives",
    "alpaca-market_screener-top-gainers",
    "alpaca-market_screener-top-losers",
    
    # Analytics Server (engine) 
    "calculate_daily_returns",
    "calculate_rolling_volatility",
    "calculate_rolling_skewness",
    "linear_trend_analysis",
    "analyze_economic_sensitivity",
    "identify_gaps",
    "calculate_correlation_matrix",
    "calculate_drawdown_metrics",
    "calculate_sma",
    "identify_consecutive_patterns",
    "calculate_weekly_range_tightness",
    "calculate_relative_strength",
    "calculate_risk_metrics",
    "identify_trading_patterns",
    "calculate_statistical_significance",
    "analyze_volume_patterns",
    "calculate_performance_metrics",
    "calculate_rsi",
    "calculate_macd",
    "calculate_bollinger_bands",
    
    # New Advanced Functions
    "cluster_stocks_by_returns",
    "detect_outlier_stocks", 
    "feature_importance_analysis",
    "comprehensive_technical_analysis",
    "predict_returns_xgboost",
    
    # Client compute
    "client_compute"
}

def load_experimental_data():
    """Load experimental.json data."""
    try:
        with open('/Users/shivc/Documents/Workspace/JS/qna-ai-admin/data/experimental.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading experimental.json: {e}")
        return []

def analyze_workflow(workflow_data):
    """Analyze a single workflow for issues."""
    issues = []
    workflow_steps = workflow_data.get('workflow', [])
    
    for i, step in enumerate(workflow_steps):
        step_num = i + 1
        step_type = step.get('type', 'unknown')
        step_function = step.get('function', 'missing')
        step_desc = step.get('description', '')
        
        # Check if function exists
        if step_function not in AVAILABLE_MCP_FUNCTIONS and step_function != 'missing':
            issues.append({
                'type': 'missing_function',
                'step': step_num,
                'function': step_function,
                'step_type': step_type,
                'description': step_desc
            })
        
        # Check for mismatched function usage
        if step_type == 'engine':
            if 'calculate_daily_returns' in step_function and 'pattern' in step_desc.lower():
                issues.append({
                    'type': 'function_mismatch',
                    'step': step_num,
                    'function': step_function,
                    'issue': 'Using calculate_daily_returns for pattern analysis - should use identify_trading_patterns'
                })
            
            if 'calculate_risk_metrics' in step_function and 'fair value' in step_desc.lower():
                issues.append({
                    'type': 'function_mismatch', 
                    'step': step_num,
                    'function': step_function,
                    'issue': 'Using calculate_risk_metrics for fair value - need custom fair value function'
                })
        
        # Check for opportunities to use ta library
        if any(indicator in step_desc.lower() for indicator in ['rsi', 'macd', 'bollinger', 'stochastic', 'adx']):
            if step_function not in ['calculate_rsi', 'calculate_macd', 'calculate_bollinger_bands', 'comprehensive_technical_analysis']:
                issues.append({
                    'type': 'library_opportunity',
                    'step': step_num,
                    'function': step_function,
                    'opportunity': f'Should use ta library functions for technical indicators mentioned in: {step_desc[:100]}...'
                })
        
        # Check for clustering/ML opportunities
        if any(term in step_desc.lower() for term in ['cluster', 'similar', 'group', 'classify']):
            if step_function not in ['cluster_stocks_by_returns', 'detect_outlier_stocks']:
                issues.append({
                    'type': 'ml_opportunity',
                    'step': step_num,
                    'function': step_function,
                    'opportunity': f'Should use ML clustering functions for: {step_desc[:100]}...'
                })
    
    return issues

def generate_mock_data_test(workflow_data):
    """Generate mock data flow test for a workflow."""
    workflow_steps = workflow_data.get('workflow', [])
    mock_tests = []
    
    for i, step in enumerate(workflow_steps):
        step_num = i + 1
        step_type = step.get('type')
        step_function = step.get('function')
        
        if step_type == 'fetch':
            if 'positions' in step_function:
                mock_output = '[{"symbol": "AAPL", "qty": "100", "market_value": "15000", "unrealized_pl": "500"}]'
            elif 'bars' in step_function:
                mock_output = '[{"t": "2024-01-01", "o": 150, "h": 155, "l": 148, "c": 152, "v": 1000000}]'
            elif 'snapshots' in step_function:
                mock_output = '[{"symbol": "AAPL", "lastTrade": {"p": 152.50, "t": "2024-01-01T16:00:00Z"}}]'
            elif 'screener' in step_function:
                mock_output = '[{"symbol": "AAPL", "volume": 50000000}, {"symbol": "MSFT", "volume": 45000000}]'
            else:
                mock_output = '[{"data": "sample"}]'
        
        elif step_type == 'engine':
            if 'returns' in step_function:
                mock_output = '{"returns": [0.02, -0.01, 0.015], "stats": {"mean": 0.008, "std": 0.012}}'
            elif 'volatility' in step_function:
                mock_output = '{"rolling_volatility": [0.15, 0.18, 0.16], "annualized": 0.25}'
            elif 'correlation' in step_function:
                mock_output = '{"correlation_matrix": [[1.0, 0.65], [0.65, 1.0]], "symbols": ["AAPL", "MSFT"]}'
            elif 'patterns' in step_function or 'gaps' in step_function:
                mock_output = '{"patterns": [{"type": "bullish_engulfing", "date": "2024-01-01", "strength": "strong"}]}'
            else:
                mock_output = '{"analysis_result": "computed"}'
        
        else:  # compute
            mock_output = '{"ranked_results": [{"symbol": "AAPL", "rank": 1, "score": 95.2}]}'
        
        mock_tests.append({
            'step': step_num,
            'function': step_function,
            'mock_input': 'Output from previous step' if i > 0 else 'Initial parameters',
            'expected_output': mock_output,
            'compatibility_check': 'needs_validation'
        })
    
    return mock_tests

def main():
    """Main audit function."""
    print("🔍 EXPERIMENTAL WORKFLOW AUDIT")
    print("=" * 50)
    
    experimental_data = load_experimental_data()
    
    if not experimental_data:
        print("❌ No experimental data found")
        return
    
    total_workflows = len(experimental_data)
    total_issues = 0
    workflows_with_issues = 0
    
    print(f"📊 Analyzing {total_workflows} workflows...\n")
    
    # Summary counters
    missing_functions = set()
    function_mismatches = []
    library_opportunities = []
    ml_opportunities = []
    
    for workflow in experimental_data:
        workflow_id = workflow.get('id', 'unknown')
        workflow_name = workflow.get('name', 'Unknown')
        issues = analyze_workflow(workflow)
        
        if issues:
            workflows_with_issues += 1
            total_issues += len(issues)
            
            print(f"⚠️  {workflow_name} ({workflow_id})")
            for issue in issues:
                if issue['type'] == 'missing_function':
                    missing_functions.add(issue['function'])
                    print(f"   ❌ Step {issue['step']}: Missing function '{issue['function']}'")
                elif issue['type'] == 'function_mismatch':
                    function_mismatches.append(issue)
                    print(f"   🔄 Step {issue['step']}: {issue['issue']}")
                elif issue['type'] == 'library_opportunity':
                    library_opportunities.append(issue)
                    print(f"   📚 Step {issue['step']}: {issue['opportunity']}")
                elif issue['type'] == 'ml_opportunity':
                    ml_opportunities.append(issue)
                    print(f"   🤖 Step {issue['step']}: {issue['opportunity']}")
            print()
    
    # Summary Report
    print("📋 AUDIT SUMMARY")
    print("=" * 50)
    print(f"Total workflows analyzed: {total_workflows}")
    print(f"Workflows with issues: {workflows_with_issues}")
    print(f"Total issues found: {total_issues}")
    print()
    
    if missing_functions:
        print(f"🚨 MISSING FUNCTIONS ({len(missing_functions)}):")
        for func in sorted(missing_functions):
            print(f"   - {func}")
        print()
    
    if function_mismatches:
        print(f"🔄 FUNCTION MISMATCHES ({len(function_mismatches)}):")
        for mismatch in function_mismatches:
            print(f"   - {mismatch['issue']}")
        print()
    
    if library_opportunities:
        print(f"📚 LIBRARY OPPORTUNITIES ({len(library_opportunities)}):")
        print("   Should use ta library, sklearn, scipy instead of custom implementations")
        print()
    
    if ml_opportunities:
        print(f"🤖 ML OPPORTUNITIES ({len(ml_opportunities)}):")
        print("   Should use scikit-learn clustering/classification functions")
        print()
    
    # Recommendations
    print("💡 RECOMMENDATIONS")
    print("=" * 50)
    print("1. Implement missing MCP functions using proper libraries")
    print("2. Fix function mismatches in workflow steps")
    print("3. Replace custom implementations with ta/sklearn/scipy libraries")
    print("4. Run end-to-end pipeline testing with mock data")
    print("5. Update workflow descriptions to match actual function capabilities")

if __name__ == "__main__":
    main()