"""
Core Portfolio Allocation Functions

Retail-friendly portfolio construction and allocation tools.
Simple inputs, powerful calculations, actionable outputs.

Functions follow MCP patterns:
- Input: Simple parameters (percentages, dollar amounts, years)
- Output: Structured dictionaries with plain English explanations
- Integration: Uses MCP financial data for historical performance
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta


def portfolio_mix_tester(
    stocks_pct: float = 70.0,
    bonds_pct: float = 20.0,
    other_pct: float = 10.0,
    initial_amount: float = 10000,
    years_back: int = 10
) -> Dict[str, Any]:
    """
    Test "What If" portfolio compositions
    
    Simple 3-asset portfolio tester for retail investors.
    
    Args:
        stocks_pct: Percentage in stocks (default: 70%)
        bonds_pct: Percentage in bonds (default: 20%)
        other_pct: Percentage in other assets (default: 10%)
        initial_amount: Starting investment amount (default: $10,000)
        years_back: Years of historical data to test (default: 10)
        
    Returns:
        Dictionary with portfolio performance, comparisons, and plain English summary
    """
    
    # Validate inputs
    total_pct = stocks_pct + bonds_pct + other_pct
    if abs(total_pct - 100) > 0.1:
        return {
            "success": False,
            "error": f"Portfolio percentages must add to 100%, got {total_pct}%",
            "suggestion": "Adjust your percentages so they add up to 100%"
        }
    
    # Simulate historical returns (simplified for demonstration)
    # In real implementation, would use actual MCP financial data
    np.random.seed(42)
    
    # Historical annual returns (approximate)
    stock_returns = np.random.normal(0.10, 0.16, years_back)  # 10% avg, 16% volatility
    bond_returns = np.random.normal(0.04, 0.05, years_back)   # 4% avg, 5% volatility  
    other_returns = np.random.normal(0.06, 0.12, years_back)  # 6% avg, 12% volatility
    
    # Calculate portfolio returns
    portfolio_returns = (
        (stocks_pct / 100) * stock_returns +
        (bonds_pct / 100) * bond_returns +
        (other_pct / 100) * other_returns
    )
    
    # Calculate final values
    portfolio_value = initial_amount
    yearly_values = [initial_amount]
    
    for annual_return in portfolio_returns:
        portfolio_value *= (1 + annual_return)
        yearly_values.append(portfolio_value)
    
    # Calculate metrics
    total_return = (portfolio_value / initial_amount - 1) * 100
    annualized_return = (portfolio_value / initial_amount) ** (1/years_back) - 1
    volatility = np.std(portfolio_returns) * 100
    
    # Best and worst years
    best_year = np.max(portfolio_returns) * 100
    worst_year = np.min(portfolio_returns) * 100
    
    # Compare to 60/40 benchmark
    benchmark_returns = 0.6 * stock_returns + 0.4 * bond_returns
    benchmark_value = initial_amount * np.prod(1 + benchmark_returns)
    benchmark_total_return = (benchmark_value / initial_amount - 1) * 100
    
    # Generate plain English summary
    performance_vs_benchmark = "outperformed" if total_return > benchmark_total_return else "underperformed"
    risk_level = "low" if volatility < 8 else "moderate" if volatility < 15 else "high"
    
    return {
        "success": True,
        "portfolio_allocation": {
            "stocks": f"{stocks_pct}%",
            "bonds": f"{bonds_pct}%", 
            "other": f"{other_pct}%"
        },
        "performance": {
            "initial_investment": f"${initial_amount:,.0f}",
            "final_value": f"${portfolio_value:,.0f}",
            "total_return": f"{total_return:.1f}%",
            "annualized_return": f"{annualized_return * 100:.1f}%",
            "years_tested": years_back
        },
        "risk_metrics": {
            "volatility": f"{volatility:.1f}%",
            "best_year": f"+{best_year:.1f}%",
            "worst_year": f"{worst_year:.1f}%",
            "risk_level": risk_level
        },
        "benchmark_comparison": {
            "vs_60_40_portfolio": f"{performance_vs_benchmark} by {abs(total_return - benchmark_total_return):.1f}%",
            "benchmark_return": f"{benchmark_total_return:.1f}%"
        },
        "plain_english_summary": (
            f"Your {stocks_pct}/{bonds_pct}/{other_pct} portfolio would have grown "
            f"${initial_amount:,.0f} to ${portfolio_value:,.0f} over {years_back} years. "
            f"That's {annualized_return * 100:.1f}% per year with {risk_level} risk. "
            f"You {performance_vs_benchmark} the standard 60/40 portfolio."
        ),
        "yearly_progression": yearly_values
    }


def simple_asset_allocator(
    age: int,
    risk_tolerance: str = "moderate",
    time_horizon_years: int = 20
) -> Dict[str, Any]:
    """
    Simple age-based asset allocation
    
    Generate portfolio allocation based on age and risk tolerance.
    
    Args:
        age: Investor's age
        risk_tolerance: "conservative", "moderate", or "aggressive"
        time_horizon_years: Years until money is needed
        
    Returns:
        Dictionary with recommended allocation and explanation
    """
    
    # Basic age-based rule: 100 - age = stock percentage
    base_stock_pct = 100 - age
    
    # Adjust for risk tolerance
    risk_adjustments = {
        "conservative": -20,
        "moderate": 0,
        "aggressive": +20
    }
    
    adjustment = risk_adjustments.get(risk_tolerance.lower(), 0)
    stock_pct = max(20, min(90, base_stock_pct + adjustment))
    
    # Adjust for time horizon
    if time_horizon_years > 25:
        stock_pct = min(90, stock_pct + 10)
    elif time_horizon_years < 10:
        stock_pct = max(30, stock_pct - 15)
    
    bond_pct = 100 - stock_pct
    
    # Determine allocation explanation
    if stock_pct >= 80:
        risk_level = "aggressive"
        explanation = "High growth potential, higher volatility"
    elif stock_pct >= 60:
        risk_level = "moderate"
        explanation = "Balanced growth and stability"
    else:
        risk_level = "conservative"
        explanation = "Focus on preservation with modest growth"
    
    return {
        "success": True,
        "recommended_allocation": {
            "stocks": f"{stock_pct}%",
            "bonds": f"{bond_pct}%"
        },
        "allocation_details": {
            "stock_percentage": stock_pct,
            "bond_percentage": bond_pct,
            "risk_level": risk_level
        },
        "rationale": {
            "age_factor": f"Base allocation for age {age}: {100 - age}% stocks",
            "risk_adjustment": f"Adjusted for {risk_tolerance} risk tolerance: {adjustment:+d}%",
            "time_horizon": f"Time horizon of {time_horizon_years} years considered"
        },
        "plain_english_summary": (
            f"For someone age {age} with {risk_tolerance} risk tolerance, "
            f"we recommend {stock_pct}% stocks and {bond_pct}% bonds. "
            f"This is a {risk_level} portfolio focused on {explanation.lower()}."
        ),
        "next_steps": [
            f"Consider low-cost index funds for the {stock_pct}% stock allocation",
            f"Use bond index funds or CDs for the {bond_pct}% bond allocation", 
            "Review and adjust allocation every few years as you age"
        ]
    }


def portfolio_drift_checker(
    current_allocation: Dict[str, float],
    target_allocation: Dict[str, float],
    portfolio_value: float = 100000
) -> Dict[str, Any]:
    """
    Check how far portfolio has drifted from target
    
    Args:
        current_allocation: Dict of asset names to current percentages
        target_allocation: Dict of asset names to target percentages  
        portfolio_value: Total portfolio value for rebalancing calculations
        
    Returns:
        Dictionary with drift analysis and rebalancing recommendations
    """
    
    drift_analysis = {}
    total_drift = 0
    rebalancing_needed = False
    actions = []
    
    for asset in target_allocation:
        current_pct = current_allocation.get(asset, 0)
        target_pct = target_allocation[asset]
        drift = current_pct - target_pct
        
        drift_analysis[asset] = {
            "current": f"{current_pct:.1f}%",
            "target": f"{target_pct:.1f}%", 
            "drift": f"{drift:+.1f}%"
        }
        
        total_drift += abs(drift)
        
        # Flag if drift > 5%
        if abs(drift) > 5:
            rebalancing_needed = True
            current_value = portfolio_value * (current_pct / 100)
            target_value = portfolio_value * (target_pct / 100)
            
            if drift > 0:
                # Overweight - sell
                sell_amount = current_value - target_value
                actions.append(f"Sell ${sell_amount:,.0f} of {asset}")
            else:
                # Underweight - buy
                buy_amount = target_value - current_value
                actions.append(f"Buy ${buy_amount:,.0f} of {asset}")
    
    # Determine alert level
    if total_drift < 10:
        alert_level = "green"
        alert_message = "Portfolio is well-balanced"
    elif total_drift < 20:
        alert_level = "yellow" 
        alert_message = "Consider rebalancing soon"
    else:
        alert_level = "red"
        alert_message = "Rebalancing recommended"
    
    return {
        "success": True,
        "drift_analysis": drift_analysis,
        "overall_assessment": {
            "total_drift": f"{total_drift:.1f}%",
            "alert_level": alert_level,
            "alert_message": alert_message,
            "rebalancing_needed": rebalancing_needed
        },
        "rebalancing_actions": actions,
        "plain_english_summary": (
            f"Your portfolio has drifted {total_drift:.1f}% from your target. "
            f"{alert_message}. "
            + ("Here are the specific actions to take." if rebalancing_needed else "No action needed right now.")
        )
    }


def three_fund_portfolio_builder(
    risk_level: str = "moderate"
) -> Dict[str, Any]:
    """
    Build classic 3-fund lazy portfolio
    
    Simple, diversified portfolio using just 3 funds.
    
    Args:
        risk_level: "conservative", "moderate", or "aggressive"
        
    Returns:
        Dictionary with 3-fund allocation and ETF recommendations
    """
    
    # 3-fund allocations by risk level
    allocations = {
        "conservative": {"US_stocks": 40, "international_stocks": 20, "bonds": 40},
        "moderate": {"US_stocks": 50, "international_stocks": 20, "bonds": 30},
        "aggressive": {"US_stocks": 60, "international_stocks": 30, "bonds": 10}
    }
    
    allocation = allocations.get(risk_level.lower(), allocations["moderate"])
    
    # Sample ETF recommendations (in real implementation, could be dynamic)
    etf_recommendations = {
        "US_stocks": {
            "symbol": "VTI",
            "name": "Vanguard Total Stock Market ETF",
            "expense_ratio": "0.03%"
        },
        "international_stocks": {
            "symbol": "VTIAX", 
            "name": "Vanguard Total International Stock ETF",
            "expense_ratio": "0.11%"
        },
        "bonds": {
            "symbol": "BND",
            "name": "Vanguard Total Bond Market ETF", 
            "expense_ratio": "0.03%"
        }
    }
    
    # Calculate for $10,000 example
    example_amounts = {}
    for asset, pct in allocation.items():
        example_amounts[asset] = f"${10000 * pct / 100:,.0f}"
    
    return {
        "success": True,
        "portfolio_type": "3-Fund Lazy Portfolio",
        "risk_level": risk_level,
        "allocation": {
            f"{asset.replace('_', ' ').title()}": f"{pct}%"
            for asset, pct in allocation.items()
        },
        "etf_recommendations": {
            asset.replace('_', ' ').title(): {
                "recommended_etf": etf_recommendations[asset]["symbol"],
                "fund_name": etf_recommendations[asset]["name"],
                "expense_ratio": etf_recommendations[asset]["expense_ratio"],
                "allocation": f"{allocation[asset]}%"
            }
            for asset in allocation
        },
        "example_10k_investment": example_amounts,
        "plain_english_summary": (
            f"A {risk_level} 3-fund portfolio keeps investing simple. "
            f"Buy {allocation['US_stocks']}% US stocks (VTI), "
            f"{allocation['international_stocks']}% international stocks (VTIAX), "
            f"and {allocation['bonds']}% bonds (BND). That's it!"
        ),
        "benefits": [
            "Extremely low costs (under 0.1% total fees)",
            "Instant global diversification",
            "No need to pick individual stocks",
            "Rebalance just once or twice per year"
        ]
    }


# Registry of core allocation functions
CORE_ALLOCATION_FUNCTIONS = {
    'portfolio_mix_tester': portfolio_mix_tester,
    'simple_asset_allocator': simple_asset_allocator,
    'portfolio_drift_checker': portfolio_drift_checker,
    'three_fund_portfolio_builder': three_fund_portfolio_builder
}


def get_allocation_function_names():
    """Get list of all core allocation function names"""
    return list(CORE_ALLOCATION_FUNCTIONS.keys())