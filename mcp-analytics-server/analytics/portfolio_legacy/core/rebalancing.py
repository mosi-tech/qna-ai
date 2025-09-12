"""
Simple Rebalancing Tools

Retail-friendly rebalancing analysis and recommendations.
Focuses on practical decisions: when, how much, and what to do.

Functions designed for MCP integration with plain English outputs.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta


def rebalancing_frequency_tester(
    initial_amount: float = 10000,
    monthly_contribution: float = 0,
    years_to_test: int = 10,
    portfolio_allocation: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Test different rebalancing frequencies
    
    Compare never rebalancing vs quarterly vs yearly rebalancing.
    Show the dollar difference to help investors decide.
    
    Args:
        initial_amount: Starting investment amount
        monthly_contribution: Additional monthly investment
        years_to_test: Years to simulate
        portfolio_allocation: Dict of asset allocations (default: 60/40 stocks/bonds)
        
    Returns:
        Dictionary comparing rebalancing strategies with dollar impacts
    """
    
    if portfolio_allocation is None:
        portfolio_allocation = {"stocks": 60.0, "bonds": 40.0}
    
    # Simulate market returns (simplified - in production use real MCP data)
    np.random.seed(42)
    monthly_stock_returns = np.random.normal(0.008, 0.046, years_to_test * 12)  # ~10% annual, 16% vol
    monthly_bond_returns = np.random.normal(0.003, 0.014, years_to_test * 12)   # ~4% annual, 5% vol
    
    def simulate_strategy(rebalance_frequency: str):
        """Simulate a rebalancing strategy"""
        months = years_to_test * 12
        stock_value = initial_amount * portfolio_allocation["stocks"] / 100
        bond_value = initial_amount * portfolio_allocation["bonds"] / 100
        
        for month in range(months):
            # Apply returns
            stock_value *= (1 + monthly_stock_returns[month])
            bond_value *= (1 + monthly_bond_returns[month])
            
            # Add monthly contribution
            if monthly_contribution > 0:
                stock_contribution = monthly_contribution * portfolio_allocation["stocks"] / 100
                bond_contribution = monthly_contribution * portfolio_allocation["bonds"] / 100
                stock_value += stock_contribution
                bond_value += bond_contribution
            
            # Rebalance check
            total_value = stock_value + bond_value
            current_stock_pct = (stock_value / total_value) * 100
            target_stock_pct = portfolio_allocation["stocks"]
            
            should_rebalance = False
            if rebalance_frequency == "quarterly" and month % 3 == 0:
                should_rebalance = True
            elif rebalance_frequency == "yearly" and month % 12 == 0:
                should_rebalance = True
            elif rebalance_frequency == "threshold" and abs(current_stock_pct - target_stock_pct) > 5:
                should_rebalance = True
            
            if should_rebalance and month > 0:
                # Rebalance to target allocation
                target_stock_value = total_value * portfolio_allocation["stocks"] / 100
                target_bond_value = total_value * portfolio_allocation["bonds"] / 100
                stock_value = target_stock_value
                bond_value = target_bond_value
        
        return stock_value + bond_value
    
    # Test different strategies
    strategies = {
        "never": simulate_strategy("never"),
        "quarterly": simulate_strategy("quarterly"), 
        "yearly": simulate_strategy("yearly"),
        "threshold_5pct": simulate_strategy("threshold")
    }
    
    # Calculate differences
    best_strategy = max(strategies, key=strategies.get)
    worst_strategy = min(strategies, key=strategies.get)
    
    # Calculate rebalancing benefit
    never_rebalance_value = strategies["never"]
    best_rebalance_value = strategies[best_strategy]
    rebalancing_benefit = best_rebalance_value - never_rebalance_value
    
    return {
        "success": True,
        "test_parameters": {
            "initial_investment": f"${initial_amount:,.0f}",
            "monthly_contribution": f"${monthly_contribution:,.0f}",
            "years_tested": years_to_test,
            "portfolio_mix": f"{portfolio_allocation['stocks']:.0f}% stocks, {portfolio_allocation['bonds']:.0f}% bonds"
        },
        "strategy_results": {
            strategy: {
                "final_value": f"${value:,.0f}",
                "total_return": f"{((value / initial_amount) - 1) * 100:.1f}%",
                "vs_never_rebalancing": f"{value - never_rebalance_value:+,.0f}"
            }
            for strategy, value in strategies.items()
        },
        "recommendation": {
            "best_strategy": best_strategy.replace("_", " ").title(),
            "benefit_vs_never": f"${rebalancing_benefit:+,.0f}",
            "worst_strategy": worst_strategy.replace("_", " ").title()
        },
        "plain_english_summary": (
            f"Over {years_to_test} years, {best_strategy.replace('_', ' ')} rebalancing "
            f"would have made you ${rebalancing_benefit:+,.0f} more than never rebalancing. "
            f"Your ${initial_amount:,.0f} would have grown to ${best_rebalance_value:,.0f}."
        ),
        "practical_advice": (
            "Yearly rebalancing" if best_strategy == "yearly" else
            "Quarterly rebalancing" if best_strategy == "quarterly" else 
            "Rebalance when allocation drifts 5% from target" if best_strategy == "threshold_5pct" else
            "Set-and-forget approach works fine"
        )
    }


def rebalancing_cost_calculator(
    portfolio_value: float,
    trades_needed: List[Dict[str, Any]],
    commission_per_trade: float = 0.0,
    bid_ask_spread_pct: float = 0.05
) -> Dict[str, Any]:
    """
    Calculate the cost of rebalancing
    
    Help investors understand if rebalancing is worth the cost.
    
    Args:
        portfolio_value: Total portfolio value
        trades_needed: List of trades with 'action', 'asset', 'amount'
        commission_per_trade: Commission per trade (many brokers are $0)
        bid_ask_spread_pct: Estimated bid-ask spread percentage
        
    Returns:
        Dictionary with rebalancing costs and cost-benefit analysis
    """
    
    total_commission = len(trades_needed) * commission_per_trade
    
    # Calculate spread costs
    total_trade_amount = sum(abs(trade.get('amount', 0)) for trade in trades_needed)
    spread_cost = total_trade_amount * (bid_ask_spread_pct / 100)
    
    total_cost = total_commission + spread_cost
    cost_as_pct = (total_cost / portfolio_value) * 100
    
    # Cost-benefit analysis
    if cost_as_pct < 0.1:
        recommendation = "Low cost - rebalancing is worthwhile"
        cost_level = "low"
    elif cost_as_pct < 0.5:
        recommendation = "Moderate cost - consider quarterly instead of monthly rebalancing"
        cost_level = "moderate" 
    else:
        recommendation = "High cost - only rebalance when significantly out of alignment"
        cost_level = "high"
    
    return {
        "success": True,
        "cost_breakdown": {
            "commission_costs": f"${total_commission:.2f}",
            "spread_costs": f"${spread_cost:.2f}",
            "total_cost": f"${total_cost:.2f}",
            "cost_percentage": f"{cost_as_pct:.3f}%"
        },
        "trades_analyzed": len(trades_needed),
        "total_trade_amount": f"${total_trade_amount:,.0f}",
        "cost_assessment": {
            "cost_level": cost_level,
            "recommendation": recommendation
        },
        "plain_english_summary": (
            f"Rebalancing will cost ${total_cost:.2f} ({cost_as_pct:.3f}% of portfolio). "
            f"{recommendation}."
        )
    }


def smart_rebalancing_alerts(
    current_allocation: Dict[str, float],
    target_allocation: Dict[str, float], 
    portfolio_value: float,
    last_rebalance_days_ago: int = 0,
    min_rebalance_interval_days: int = 90
) -> Dict[str, Any]:
    """
    Smart rebalancing alert system
    
    Determines when rebalancing is actually needed vs just noise.
    
    Args:
        current_allocation: Current asset percentages
        target_allocation: Target asset percentages
        portfolio_value: Total portfolio value
        last_rebalance_days_ago: Days since last rebalancing
        min_rebalance_interval_days: Minimum days between rebalances
        
    Returns:
        Dictionary with alert level and specific recommendations
    """
    
    # Calculate drift for each asset
    drifts = {}
    max_drift = 0
    total_drift = 0
    
    for asset in target_allocation:
        current = current_allocation.get(asset, 0)
        target = target_allocation[asset]
        drift = abs(current - target)
        drifts[asset] = {
            "current": current,
            "target": target,
            "drift": drift,
            "drift_pct": f"{drift:.1f}%"
        }
        max_drift = max(max_drift, drift)
        total_drift += drift
    
    # Determine alert level
    if max_drift < 3:
        alert_level = "green"
        alert_message = "Portfolio is well-balanced"
        action_needed = False
    elif max_drift < 7:
        alert_level = "yellow"
        alert_message = "Minor drift detected"
        action_needed = last_rebalance_days_ago > min_rebalance_interval_days
    elif max_drift < 15:
        alert_level = "orange"  
        alert_message = "Moderate drift - consider rebalancing"
        action_needed = last_rebalance_days_ago > 30
    else:
        alert_level = "red"
        alert_message = "Significant drift - rebalancing recommended"
        action_needed = True
    
    # Generate specific actions
    actions = []
    if action_needed:
        for asset, data in drifts.items():
            if data["drift"] > 3:
                current_value = portfolio_value * (data["current"] / 100)
                target_value = portfolio_value * (data["target"] / 100)
                difference = current_value - target_value
                
                if difference > 0:
                    actions.append(f"Sell ${abs(difference):,.0f} of {asset}")
                else:
                    actions.append(f"Buy ${abs(difference):,.0f} of {asset}")
    
    # Calculate days until next recommended check
    if alert_level == "green":
        next_check_days = 90
    elif alert_level == "yellow":
        next_check_days = 30
    else:
        next_check_days = 7
    
    return {
        "success": True,
        "alert_status": {
            "level": alert_level,
            "message": alert_message,
            "action_needed": action_needed
        },
        "drift_analysis": drifts,
        "portfolio_health": {
            "max_drift": f"{max_drift:.1f}%",
            "total_drift": f"{total_drift:.1f}%",
            "days_since_rebalance": last_rebalance_days_ago
        },
        "recommendations": {
            "immediate_actions": actions if action_needed else ["No action needed"],
            "next_check_in_days": next_check_days
        },
        "plain_english_summary": (
            f"Portfolio alert: {alert_level.upper()} - {alert_message}. "
            f"Maximum drift is {max_drift:.1f}%. "
            + (f"Action needed: {', '.join(actions[:2])}." if action_needed else "No action needed.")
        )
    }


def dollar_cost_averaging_vs_rebalancing(
    monthly_investment: float = 1000,
    years_to_simulate: int = 10,
    target_allocation: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Compare dollar cost averaging vs rebalancing strategies
    
    Help investors understand the impact of different investment approaches.
    
    Args:
        monthly_investment: Monthly investment amount
        years_to_simulate: Years to run simulation
        target_allocation: Target portfolio allocation
        
    Returns:
        Dictionary comparing DCA strategies
    """
    
    if target_allocation is None:
        target_allocation = {"stocks": 70.0, "bonds": 30.0}
    
    # Simulate returns
    np.random.seed(42)
    months = years_to_simulate * 12
    monthly_stock_returns = np.random.normal(0.008, 0.046, months)
    monthly_bond_returns = np.random.normal(0.003, 0.014, months)
    
    def simulate_dca_strategy(rebalance: bool):
        """Simulate DCA with or without rebalancing"""
        stock_shares = 0
        bond_shares = 0
        stock_price = 100  # Starting price
        bond_price = 100
        
        for month in range(months):
            # Update prices
            stock_price *= (1 + monthly_stock_returns[month])
            bond_price *= (1 + monthly_bond_returns[month])
            
            # Invest new money
            stock_investment = monthly_investment * target_allocation["stocks"] / 100
            bond_investment = monthly_investment * target_allocation["bonds"] / 100
            
            stock_shares += stock_investment / stock_price
            bond_shares += bond_investment / bond_price
            
            # Rebalance quarterly if strategy calls for it
            if rebalance and month % 3 == 0 and month > 0:
                total_value = stock_shares * stock_price + bond_shares * bond_price
                target_stock_value = total_value * target_allocation["stocks"] / 100
                target_bond_value = total_value * target_allocation["bonds"] / 100
                
                stock_shares = target_stock_value / stock_price
                bond_shares = target_bond_value / bond_price
        
        final_value = stock_shares * stock_price + bond_shares * bond_price
        return final_value, stock_shares, bond_shares
    
    # Run both strategies
    dca_only_value, _, _ = simulate_dca_strategy(rebalance=False)
    dca_rebalance_value, _, _ = simulate_dca_strategy(rebalance=True)
    
    total_invested = monthly_investment * months
    
    return {
        "success": True,
        "simulation_parameters": {
            "monthly_investment": f"${monthly_investment:,.0f}",
            "years_simulated": years_to_simulate,
            "total_invested": f"${total_invested:,.0f}",
            "target_allocation": f"{target_allocation['stocks']:.0f}% stocks, {target_allocation['bonds']:.0f}% bonds"
        },
        "strategy_comparison": {
            "dca_only": {
                "final_value": f"${dca_only_value:,.0f}",
                "total_return": f"{((dca_only_value / total_invested) - 1) * 100:.1f}%"
            },
            "dca_with_rebalancing": {
                "final_value": f"${dca_rebalance_value:,.0f}",
                "total_return": f"{((dca_rebalance_value / total_invested) - 1) * 100:.1f}%"
            }
        },
        "rebalancing_benefit": {
            "additional_value": f"${dca_rebalance_value - dca_only_value:+,.0f}",
            "percentage_improvement": f"{((dca_rebalance_value / dca_only_value) - 1) * 100:+.2f}%"
        },
        "plain_english_summary": (
            f"Investing ${monthly_investment:,.0f} monthly for {years_to_simulate} years: "
            f"DCA with quarterly rebalancing would give you ${dca_rebalance_value:,.0f} "
            f"vs ${dca_only_value:,.0f} without rebalancing. "
            f"That's ${dca_rebalance_value - dca_only_value:+,.0f} more."
        )
    }


# Registry of rebalancing functions
REBALANCING_FUNCTIONS = {
    'rebalancing_frequency_tester': rebalancing_frequency_tester,
    'rebalancing_cost_calculator': rebalancing_cost_calculator,
    'smart_rebalancing_alerts': smart_rebalancing_alerts,
    'dollar_cost_averaging_vs_rebalancing': dollar_cost_averaging_vs_rebalancing
}


def get_rebalancing_function_names():
    """Get list of all rebalancing function names"""
    return list(REBALANCING_FUNCTIONS.keys())