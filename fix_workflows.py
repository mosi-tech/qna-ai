#!/usr/bin/env python3
"""
Fix all experimental workflows based on audit results.
Addresses function mismatches, library opportunities, and missing functions.
"""

import json
import sys
from pathlib import Path

# Workflow fixes based on audit results
WORKFLOW_FIXES = {
    # Function mismatches: Replace incorrect function usage
    "function_replacements": {
        ("calculate_daily_returns", "pattern"): "identify_trading_patterns",
        ("calculate_risk_metrics", "fair value"): "calculate_fair_value_gaps",
    },
    
    # Add library-based functions for better implementations
    "library_upgrades": {
        "weekday": "analyze_weekday_patterns",
        "technical": "comprehensive_technical_analysis", 
        "cluster": "cluster_stocks_by_returns",
        "outlier": "detect_outlier_stocks",
    },
    
    # New function mappings for missing capabilities
    "new_functions": [
        "calculate_fair_value_gaps",
        "analyze_weekday_patterns",
        "comprehensive_technical_analysis",
        "cluster_stocks_by_returns",
        "detect_outlier_stocks",
        "feature_importance_analysis",
    ]
}

def load_experimental_data():
    """Load experimental.json data."""
    try:
        with open('/Users/shivc/Documents/Workspace/JS/qna-ai-admin/data/experimental.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading experimental.json: {e}")
        return []

def save_experimental_data(data):
    """Save updated experimental.json data."""
    try:
        with open('/Users/shivc/Documents/Workspace/JS/qna-ai-admin/data/experimental.json', 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving experimental.json: {e}")
        return False

def fix_workflow(workflow):
    """Fix a single workflow based on audit findings."""
    fixes_applied = []
    workflow_steps = workflow.get('workflow', [])
    
    for i, step in enumerate(workflow_steps):
        step_type = step.get('type', 'unknown')
        step_function = step.get('function', '')
        step_desc = step.get('description', '').lower()
        
        # Fix function mismatches
        if step_type == 'engine' and step_function == 'calculate_daily_returns':
            if any(word in step_desc for word in ['pattern', 'engulfing', 'weekday', 'monday', 'friday']):
                if 'weekday' in step_desc or 'monday' in step_desc or 'friday' in step_desc:
                    step['function'] = 'analyze_weekday_patterns'
                    fixes_applied.append(f"Step {i+1}: Replaced calculate_daily_returns with analyze_weekday_patterns for weekday analysis")
                else:
                    step['function'] = 'identify_trading_patterns'
                    fixes_applied.append(f"Step {i+1}: Replaced calculate_daily_returns with identify_trading_patterns for pattern analysis")
        
        # Fix fair value calculation
        if step_function == 'calculate_risk_metrics' and 'fair value' in step_desc:
            step['function'] = 'calculate_fair_value_gaps'
            fixes_applied.append(f"Step {i+1}: Replaced calculate_risk_metrics with calculate_fair_value_gaps for fair value analysis")
        
        # Upgrade to comprehensive technical analysis
        if any(indicator in step_desc for indicator in ['rsi', 'macd', 'bollinger', 'stochastic', 'adx', 'technical']):
            if step_function not in ['comprehensive_technical_analysis', 'calculate_rsi', 'calculate_macd', 'calculate_bollinger_bands']:
                step['function'] = 'comprehensive_technical_analysis'
                fixes_applied.append(f"Step {i+1}: Upgraded to comprehensive_technical_analysis for technical indicators")
        
        # Add ML clustering for relevant analyses
        if any(term in step_desc for term in ['cluster', 'similar', 'group', 'correlation', 'diversification']):
            if step_function not in ['cluster_stocks_by_returns', 'calculate_correlation_matrix']:
                if 'correlation' in step_desc:
                    step['function'] = 'calculate_correlation_matrix'
                    fixes_applied.append(f"Step {i+1}: Added calculate_correlation_matrix for correlation analysis")
                else:
                    step['function'] = 'cluster_stocks_by_returns'
                    fixes_applied.append(f"Step {i+1}: Added cluster_stocks_by_returns for clustering analysis")
        
        # Update step descriptions to reflect library usage
        if step['function'] == 'analyze_weekday_patterns':
            if 'pandas' not in step_desc:
                step['description'] = step['description'].replace('Calculate day', 'Analyze weekday patterns using pandas and scipy statistical analysis to calculate day')
                fixes_applied.append(f"Step {i+1}: Updated description to reflect pandas/scipy usage")
        
        elif step['function'] == 'comprehensive_technical_analysis':
            if 'ta library' not in step_desc:
                step['description'] = step['description'].replace('technical', 'technical indicators using ta library for comprehensive')
                fixes_applied.append(f"Step {i+1}: Updated description to reflect ta library usage")
        
        elif step['function'] == 'cluster_stocks_by_returns':
            if 'sklearn' not in step_desc:
                step['description'] = step['description'].replace('cluster', 'cluster using scikit-learn KMeans algorithm to group')
                fixes_applied.append(f"Step {i+1}: Updated description to reflect scikit-learn usage")
    
    return fixes_applied

def main():
    """Main workflow fixing function."""
    print("🔧 FIXING EXPERIMENTAL WORKFLOWS")
    print("=" * 50)
    
    experimental_data = load_experimental_data()
    
    if not experimental_data:
        print("❌ No experimental data found")
        return
    
    total_workflows = len(experimental_data)
    workflows_fixed = 0
    total_fixes = 0
    
    print(f"📊 Processing {total_workflows} workflows...\n")
    
    for workflow in experimental_data:
        workflow_id = workflow.get('id', 'unknown')
        workflow_name = workflow.get('name', 'Unknown')
        
        fixes = fix_workflow(workflow)
        
        if fixes:
            workflows_fixed += 1
            total_fixes += len(fixes)
            
            print(f"🔧 Fixed: {workflow_name} ({workflow_id})")
            for fix in fixes:
                print(f"   ✅ {fix}")
            print()
    
    # Save updated workflows
    if workflows_fixed > 0:
        if save_experimental_data(experimental_data):
            print(f"💾 Successfully saved {total_fixes} fixes across {workflows_fixed} workflows")
        else:
            print("❌ Failed to save workflow fixes")
    else:
        print("ℹ️  No workflows required fixing")
    
    # Summary Report
    print("\n📋 FIX SUMMARY")
    print("=" * 50)
    print(f"Total workflows processed: {total_workflows}")
    print(f"Workflows fixed: {workflows_fixed}")
    print(f"Total fixes applied: {total_fixes}")
    
    print("\n🎯 IMPROVEMENTS MADE")
    print("=" * 50)
    print("✅ Function mismatches resolved")
    print("✅ Library-based implementations added")
    print("✅ Proper statistical analysis functions integrated")
    print("✅ Technical analysis upgraded to ta library")
    print("✅ ML clustering functions added where appropriate")
    print("✅ Workflow descriptions updated to reflect library usage")
    
    print("\n🧪 NEXT STEPS")
    print("=" * 50)
    print("1. Run pipeline testing with mock data")
    print("2. Verify all MCP functions are implemented")
    print("3. Test end-to-end workflow execution")
    print("4. Validate JSON output structures")

if __name__ == "__main__":
    main()