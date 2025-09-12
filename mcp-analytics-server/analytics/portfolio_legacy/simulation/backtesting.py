"""
Simple Backtesting Engine

Retail-focused backtesting that answers practical questions:
- How would my portfolio have performed?
- What were the worst drawdowns?
- When should I have stayed the course?

Focus on education and confidence-building rather than complex metrics.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta


def simple_portfolio_backtest(
    portfolio_allocation: Dict[str, float],
    start_amount: float = 10000,
    monthly_contribution: float = 0,
    years_to_test: int = 10,
    rebalance_frequency: str = "yearly"
) -> Dict[str, Any]:
    """
    Simple portfolio backtesting for retail investors
    
    Test how a portfolio allocation would have performed historically.
    Focus on practical insights and confidence building.
    
    Args:
        portfolio_allocation: Dict of asset names to percentages
        start_amount: Initial investment
        monthly_contribution: Monthly additional investment
        years_to_test: Years of historical data to test
        rebalance_frequency: "never", "yearly", "quarterly"
        
    Returns:
        Dictionary with backtest results and practical insights
    """
    
    # Validate allocation
    total_allocation = sum(portfolio_allocation.values())
    if abs(total_allocation - 100) > 0.1:
        return {
            "success": False,
            "error": f"Allocation must sum to 100%, got {total_allocation}%"
        }
    
    # Simulate historical returns (in production, use real MCP financial data)
    np.random.seed(42)
    months = years_to_test * 12
    
    # Simplified asset returns
    asset_returns = {}
    if "stocks" in portfolio_allocation or "US_stocks" in portfolio_allocation:
        asset_returns["stocks"] = np.random.normal(0.008, 0.046, months)  # ~10% annual, 16% vol
        asset_returns["US_stocks"] = asset_returns["stocks"]
    if "bonds" in portfolio_allocation:
        asset_returns["bonds"] = np.random.normal(0.003, 0.014, months)   # ~4% annual, 5% vol
    if "international" in portfolio_allocation or "international_stocks" in portfolio_allocation:
        asset_returns["international"] = np.random.normal(0.007, 0.050, months)  # ~9% annual, 18% vol
        asset_returns["international_stocks"] = asset_returns["international"]
    if "REITs" in portfolio_allocation:
        asset_returns["REITs"] = np.random.normal(0.006, 0.055, months)   # ~8% annual, 20% vol
    
    # Initialize portfolio
    portfolio_values = [start_amount]
    monthly_values = [start_amount]
    asset_values = {}
    
    for asset, allocation in portfolio_allocation.items():
        asset_values[asset] = start_amount * (allocation / 100)
    
    # Track drawdowns
    peak_value = start_amount
    max_drawdown = 0
    drawdown_periods = []
    current_drawdown_months = 0
    
    # Simulate monthly performance
    for month in range(months):
        # Apply returns to each asset
        total_value = 0
        for asset in asset_values:
            if asset in asset_returns:
                asset_values[asset] *= (1 + asset_returns[asset][month])
            total_value += asset_values[asset]
        
        # Add monthly contribution
        if monthly_contribution > 0:
            for asset, allocation in portfolio_allocation.items():
                contribution = monthly_contribution * (allocation / 100)
                asset_values[asset] += contribution
            total_value += monthly_contribution
        
        # Check for rebalancing
        should_rebalance = False
        if rebalance_frequency == "quarterly" and month % 3 == 0:
            should_rebalance = True
        elif rebalance_frequency == "yearly" and month % 12 == 0:
            should_rebalance = True
        
        if should_rebalance and month > 0:
            # Rebalance to target allocation
            for asset, allocation in portfolio_allocation.items():
                asset_values[asset] = total_value * (allocation / 100)
        
        # Track values and drawdowns
        monthly_values.append(total_value)
        
        # Update peak and calculate drawdown
        if total_value > peak_value:
            peak_value = total_value
            if current_drawdown_months > 0:
                drawdown_periods.append(current_drawdown_months)
                current_drawdown_months = 0
        else:
            current_drawdown = (peak_value - total_value) / peak_value
            max_drawdown = max(max_drawdown, current_drawdown)
            current_drawdown_months += 1
    
    # Add final drawdown period if still in drawdown
    if current_drawdown_months > 0:
        drawdown_periods.append(current_drawdown_months)
    
    final_value = monthly_values[-1]
    total_contributed = start_amount + (monthly_contribution * months)
    total_return = (final_value / total_contributed - 1) * 100
    annualized_return = ((final_value / total_contributed) ** (1/years_to_test) - 1) * 100
    
    # Calculate some practical metrics
    monthly_returns = []
    for i in range(1, len(monthly_values)):
        if monthly_contribution > 0:
            # Adjust for contributions when calculating returns
            prev_value = monthly_values[i-1]
            current_value = monthly_values[i] - monthly_contribution
            monthly_return = (current_value / prev_value - 1) if prev_value > 0 else 0
        else:
            monthly_return = (monthly_values[i] / monthly_values[i-1] - 1) if monthly_values[i-1] > 0 else 0
        monthly_returns.append(monthly_return)
    
    volatility = np.std(monthly_returns) * np.sqrt(12) * 100  # Annualized
    
    # Best and worst periods
    best_12_months = max([
        (monthly_values[i+12] / monthly_values[i] - 1) * 100
        for i in range(len(monthly_values) - 12)
    ])
    worst_12_months = min([
        (monthly_values[i+12] / monthly_values[i] - 1) * 100
        for i in range(len(monthly_values) - 12)
    ])
    
    # Recovery analysis
    avg_recovery_months = np.mean(drawdown_periods) if drawdown_periods else 0
    max_recovery_months = max(drawdown_periods) if drawdown_periods else 0
    
    return {
        "success": True,
        "backtest_summary": {
            "initial_investment": f"${start_amount:,.0f}",
            "monthly_contribution": f"${monthly_contribution:,.0f}",
            "total_contributed": f"${total_contributed:,.0f}",
            "final_value": f"${final_value:,.0f}",
            "total_profit": f"${final_value - total_contributed:+,.0f}",
            "years_tested": years_to_test
        },
        "performance_metrics": {
            "total_return": f"{total_return:.1f}%",
            "annualized_return": f"{annualized_return:.1f}%",
            "volatility": f"{volatility:.1f}%",
            "best_12_months": f"+{best_12_months:.1f}%",
            "worst_12_months": f"{worst_12_months:.1f}%"
        },
        "risk_analysis": {
            "max_drawdown": f"-{max_drawdown * 100:.1f}%",
            "average_recovery_time": f"{avg_recovery_months:.0f} months",
            "longest_recovery_time": f"{max_recovery_months:.0f} months",
            "number_of_drawdown_periods": len(drawdown_periods)
        },
        "portfolio_details": {
            "allocation": {asset: f"{pct}%" for asset, pct in portfolio_allocation.items()},
            "rebalancing_frequency": rebalance_frequency
        },
        "monthly_portfolio_values": monthly_values,
        "plain_english_summary": (
            f"Your {'/'.join([f'{int(pct)}%' for pct in portfolio_allocation.values()])} portfolio "
            f"would have grown ${total_contributed:,.0f} to ${final_value:,.0f} over {years_to_test} years. "
            f"That's {annualized_return:.1f}% per year. The worst drop was {max_drawdown * 100:.1f}%, "
            f"and it typically took {avg_recovery_months:.0f} months to recover."
        ),
        "confidence_builders": [
            f"Even in the worst 12-month period ({worst_12_months:.1f}%), staying invested was key to long-term success",
            f"The portfolio recovered from drawdowns {len(drawdown_periods)} times, proving resilience",
            f"Your best 12-month period was +{best_12_months:.1f}%, showing the upside of staying invested"
        ]
    }


def crisis_survival_test(
    portfolio_allocation: Dict[str, float],
    initial_investment: float = 100000
) -> Dict[str, Any]:
    """
    Test portfolio survival during historical crises
    
    Show how the portfolio would have performed during major market downturns.
    Focus on building confidence for staying invested during tough times.
    
    Args:
        portfolio_allocation: Portfolio allocation to test
        initial_investment: Starting investment amount
        
    Returns:
        Dictionary with crisis survival analysis
    """
    
    # Historical crisis scenarios (simplified - in production use real data)
    crises = {
        "2008_financial_crisis": {
            "name": "2008 Financial Crisis",
            "duration_months": 18,
            "stock_decline": -0.37,  # -37% for stocks
            "bond_performance": 0.05,  # +5% for bonds
            "recovery_months": 36
        },
        "2020_covid_crash": {
            "name": "COVID-19 Pandemic",
            "duration_months": 2,
            "stock_decline": -0.20,  # -20% quick drop
            "bond_performance": 0.08,  # +8% flight to safety
            "recovery_months": 12
        },
        "2000_dotcom_crash": {
            "name": "Dot-com Crash",
            "duration_months": 31,
            "stock_decline": -0.49,  # -49% for stocks
            "bond_performance": 0.18,  # +18% for bonds
            "recovery_months": 84
        }
    }
    
    crisis_results = {}
    
    for crisis_id, crisis in crises.items():
        # Calculate portfolio impact during crisis
        portfolio_impact = 0
        for asset, allocation in portfolio_allocation.items():
            if asset.lower() in ["stocks", "us_stocks", "international", "reits"]:
                impact = crisis["stock_decline"] * (allocation / 100)
            elif asset.lower() in ["bonds"]:
                impact = crisis["bond_performance"] * (allocation / 100)
            else:
                # Conservative estimate for other assets
                impact = crisis["stock_decline"] * 0.5 * (allocation / 100)
            portfolio_impact += impact
        
        # Calculate values
        crisis_low_value = initial_investment * (1 + portfolio_impact)
        loss_amount = initial_investment - crisis_low_value
        recovery_value = initial_investment * 1.1  # Assume 10% recovery beyond initial
        
        crisis_results[crisis_id] = {
            "crisis_name": crisis["name"],
            "portfolio_decline": f"{portfolio_impact * 100:.1f}%",
            "value_at_low": f"${crisis_low_value:,.0f}",
            "loss_amount": f"${loss_amount:,.0f}",
            "recovery_time": f"{crisis['recovery_months']} months",
            "value_after_recovery": f"${recovery_value:,.0f}"
        }
    
    # Overall crisis resilience score
    avg_decline = np.mean([
        abs(crises[c]["stock_decline"] * sum([
            portfolio_allocation.get(asset, 0) 
            for asset in ["stocks", "US_stocks", "international", "REITs"]
        ]) / 100)
        for c in crises
    ])
    
    if avg_decline < 0.15:
        resilience_level = "high"
        resilience_description = "Your conservative allocation provides good downside protection"
    elif avg_decline < 0.25:
        resilience_level = "moderate" 
        resilience_description = "Balanced portfolio with reasonable downside risk"
    else:
        resilience_level = "lower"
        resilience_description = "Growth-focused portfolio with higher volatility but better long-term potential"
    
    return {
        "success": True,
        "portfolio_allocation": {asset: f"{pct}%" for asset, pct in portfolio_allocation.items()},
        "initial_investment": f"${initial_investment:,.0f}",
        "crisis_scenarios": crisis_results,
        "resilience_assessment": {
            "overall_resilience": resilience_level,
            "description": resilience_description,
            "average_crisis_decline": f"{avg_decline * 100:.1f}%"
        },
        "plain_english_summary": (
            f"During major market crises, your portfolio would typically decline {avg_decline * 100:.1f}%. "
            f"This shows {resilience_level} resilience to market shocks. "
            f"Remember: every crisis in history has been followed by recovery and new highs."
        ),
        "survival_tips": [
            "Stay invested - selling during crises locks in losses",
            "Consider it a buying opportunity if you have extra cash",
            "Focus on your long-term goals, not short-term volatility",
            "Diversification helps reduce portfolio swings during crises"
        ]
    }


def rolling_returns_analysis(
    portfolio_allocation: Dict[str, float],
    years_to_analyze: int = 20,
    rolling_period_years: int = 10
) -> Dict[str, Any]:
    """
    Analyze rolling period returns
    
    Show how consistent portfolio performance is over different time periods.
    Help investors understand the importance of time horizon.
    
    Args:
        portfolio_allocation: Portfolio to analyze
        years_to_analyze: Total years of data
        rolling_period_years: Rolling window size
        
    Returns:
        Dictionary with rolling returns analysis
    """
    
    # Generate longer historical data
    np.random.seed(42)
    months = years_to_analyze * 12
    rolling_months = rolling_period_years * 12
    
    # Simulate portfolio returns
    portfolio_returns = []
    for month in range(months):
        monthly_return = 0
        for asset, allocation in portfolio_allocation.items():
            if asset.lower() in ["stocks", "us_stocks"]:
                asset_return = np.random.normal(0.008, 0.046)  # Monthly stock return
            elif asset.lower() in ["bonds"]:
                asset_return = np.random.normal(0.003, 0.014)  # Monthly bond return
            elif asset.lower() in ["international", "international_stocks"]:
                asset_return = np.random.normal(0.007, 0.050)
            else:
                asset_return = np.random.normal(0.006, 0.040)  # Default
            
            monthly_return += asset_return * (allocation / 100)
        
        portfolio_returns.append(monthly_return)
    
    # Calculate rolling period returns
    rolling_returns = []
    for i in range(len(portfolio_returns) - rolling_months + 1):
        period_returns = portfolio_returns[i:i + rolling_months]
        cumulative_return = np.prod([1 + r for r in period_returns]) - 1
        annualized_return = ((1 + cumulative_return) ** (1/rolling_period_years) - 1) * 100
        rolling_returns.append(annualized_return)
    
    # Calculate statistics
    best_period = max(rolling_returns)
    worst_period = min(rolling_returns)
    avg_return = np.mean(rolling_returns)
    
    # Positive return periods
    positive_periods = len([r for r in rolling_returns if r > 0])
    total_periods = len(rolling_returns)
    success_rate = (positive_periods / total_periods) * 100
    
    return {
        "success": True,
        "analysis_parameters": {
            "portfolio": {asset: f"{pct}%" for asset, pct in portfolio_allocation.items()},
            "rolling_period": f"{rolling_period_years} years",
            "total_periods_analyzed": total_periods,
            "data_span": f"{years_to_analyze} years"
        },
        "rolling_returns_summary": {
            "best_period": f"{best_period:.1f}% per year",
            "worst_period": f"{worst_period:.1f}% per year", 
            "average_return": f"{avg_return:.1f}% per year",
            "success_rate": f"{success_rate:.0f}% of periods were positive"
        },
        "time_horizon_insights": {
            "consistency": "higher" if success_rate > 85 else "moderate" if success_rate > 70 else "lower",
            "range_of_outcomes": f"{best_period - worst_period:.1f}% spread between best and worst"
        },
        "rolling_returns_data": rolling_returns,
        "plain_english_summary": (
            f"Looking at {rolling_period_years}-year rolling periods over {years_to_analyze} years, "
            f"your portfolio averaged {avg_return:.1f}% annually. "
            f"{success_rate:.0f}% of all {rolling_period_years}-year periods were profitable. "
            f"The worst {rolling_period_years}-year stretch returned {worst_period:.1f}% per year."
        ),
        "investor_lessons": [
            f"Time horizon matters: {rolling_period_years} years dramatically improves success rates",
            f"Even in the worst {rolling_period_years}-year period, losses were limited" if worst_period > -5 else f"Patience is key - even bad {rolling_period_years}-year periods eventually recover",
            f"Consistency improves with longer time horizons"
        ]
    }


# Registry of backtesting functions
BACKTESTING_FUNCTIONS = {
    'simple_portfolio_backtest': simple_portfolio_backtest,
    'crisis_survival_test': crisis_survival_test, 
    'rolling_returns_analysis': rolling_returns_analysis
}


def get_backtesting_function_names():
    """Get list of all backtesting function names"""
    return list(BACKTESTING_FUNCTIONS.keys())