"""
Lazy Portfolio Builders

Pre-built, time-tested portfolio strategies for retail investors.
Focus on simplicity, low costs, and broad diversification.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any


def three_fund_portfolio_builder(
    risk_level: str = "moderate",
    age: Optional[int] = None
) -> Dict[str, Any]:
    """
    Build the classic 3-fund lazy portfolio
    
    Perfect for: "Give me 3 ETFs that make a good portfolio"
    
    Args:
        risk_level: "conservative", "moderate", or "aggressive"  
        age: Age for age-based adjustment (optional)
        
    Returns:
        Dict with 3-fund allocation and specific ETF recommendations
    """
    
    # Base allocations by risk level
    base_allocations = {
        "conservative": {"us_stocks": 40, "international_stocks": 20, "bonds": 40},
        "moderate": {"us_stocks": 50, "international_stocks": 20, "bonds": 30}, 
        "aggressive": {"us_stocks": 60, "international_stocks": 30, "bonds": 10}
    }
    
    allocation = base_allocations.get(risk_level.lower(), base_allocations["moderate"])
    
    # Age-based adjustment if provided
    if age:
        # Rule of thumb: bond allocation = age - 10, but keep within reasonable bounds
        target_bond_pct = max(20, min(50, age - 10))
        current_bond_pct = allocation["bonds"]
        
        if abs(target_bond_pct - current_bond_pct) > 10:
            # Adjust allocation
            bond_adjustment = target_bond_pct - current_bond_pct
            allocation["bonds"] = target_bond_pct
            
            # Take adjustment from stocks proportionally
            us_ratio = allocation["us_stocks"] / (allocation["us_stocks"] + allocation["international_stocks"])
            allocation["us_stocks"] = max(20, allocation["us_stocks"] - (bond_adjustment * us_ratio))
            allocation["international_stocks"] = max(10, allocation["international_stocks"] - (bond_adjustment * (1 - us_ratio)))
            
            # Ensure it adds to 100
            total = sum(allocation.values())
            for asset in allocation:
                allocation[asset] = allocation[asset] * 100 / total
    
    # Specific ETF recommendations (low-cost leaders)
    etf_recommendations = {
        "us_stocks": {
            "symbol": "VTI", 
            "name": "Vanguard Total Stock Market ETF",
            "expense_ratio": 0.03,
            "description": "Entire US stock market in one fund"
        },
        "international_stocks": {
            "symbol": "VTIAX",
            "name": "Vanguard Total International Stock Index Fund", 
            "expense_ratio": 0.11,
            "description": "Developed and emerging international markets"
        },
        "bonds": {
            "symbol": "BND",
            "name": "Vanguard Total Bond Market ETF",
            "expense_ratio": 0.03, 
            "description": "Broad US bond market exposure"
        }
    }
    
    # Calculate dollar amounts for $10,000 example
    example_investment = 10000
    dollar_allocations = {
        asset: round(example_investment * pct / 100)
        for asset, pct in allocation.items()
    }
    
    # Calculate total expense ratio
    total_expense_ratio = sum([
        etf_recommendations[asset]["expense_ratio"] * (allocation[asset] / 100)
        for asset in allocation
    ])
    
    return {
        "success": True,
        "portfolio_type": "3-Fund Lazy Portfolio",
        "risk_level": risk_level,
        "age_adjusted": age is not None,
        "allocation": {
            "US Stocks": f"{allocation['us_stocks']:.0f}%",
            "International Stocks": f"{allocation['international_stocks']:.0f}%", 
            "Bonds": f"{allocation['bonds']:.0f}%"
        },
        "etf_recommendations": [
            {
                "asset_class": "US Stocks",
                "symbol": etf_recommendations["us_stocks"]["symbol"],
                "fund_name": etf_recommendations["us_stocks"]["name"],
                "allocation": f"{allocation['us_stocks']:.0f}%",
                "expense_ratio": f"{etf_recommendations['us_stocks']['expense_ratio']:.2f}%",
                "description": etf_recommendations["us_stocks"]["description"],
                "example_amount": f"${dollar_allocations['us_stocks']:,}"
            },
            {
                "asset_class": "International Stocks", 
                "symbol": etf_recommendations["international_stocks"]["symbol"],
                "fund_name": etf_recommendations["international_stocks"]["name"],
                "allocation": f"{allocation['international_stocks']:.0f}%",
                "expense_ratio": f"{etf_recommendations['international_stocks']['expense_ratio']:.2f}%",
                "description": etf_recommendations["international_stocks"]["description"],
                "example_amount": f"${dollar_allocations['international_stocks']:,}"
            },
            {
                "asset_class": "Bonds",
                "symbol": etf_recommendations["bonds"]["symbol"], 
                "fund_name": etf_recommendations["bonds"]["name"],
                "allocation": f"{allocation['bonds']:.0f}%",
                "expense_ratio": f"{etf_recommendations['bonds']['expense_ratio']:.2f}%",
                "description": etf_recommendations["bonds"]["description"],
                "example_amount": f"${dollar_allocations['bonds']:,}"
            }
        ],
        "portfolio_cost": {
            "total_expense_ratio": f"{total_expense_ratio:.2f}%",
            "annual_cost_on_10k": f"${total_expense_ratio * 100:.0f}"
        },
        "plain_english_summary": (
            f"A {risk_level} 3-fund portfolio: {allocation['us_stocks']:.0f}% VTI (US stocks), "
            f"{allocation['international_stocks']:.0f}% VTIAX (international), "
            f"{allocation['bonds']:.0f}% BND (bonds). Total cost: {total_expense_ratio:.2f}% per year. "
            f"Rebalance once or twice yearly. That's it!"
        ),
        "benefits": [
            "Ultra-low costs (under 0.1% total)",
            "Instant global diversification",
            "No need to pick individual stocks",
            "Minimal maintenance required",
            "Time-tested approach used by millions"
        ],
        "next_steps": [
            "Open account with discount broker (Vanguard, Fidelity, Schwab)",
            "Buy funds in target percentages",
            "Set up automatic investing",
            "Rebalance when drift exceeds 5-10%"
        ]
    }


def four_fund_portfolio_builder(
    risk_level: str = "moderate", 
    include_reits: bool = True
) -> Dict[str, Any]:
    """
    Build 4-fund lazy portfolio (3-fund + REITs or small-cap value)
    
    Perfect for: "I want a bit more diversification than 3 funds"
    
    Args:
        risk_level: "conservative", "moderate", or "aggressive"
        include_reits: If True, add REITs; if False, add small-cap value
        
    Returns:
        Dict with 4-fund allocation and recommendations
    """
    
    # Start with 3-fund base
    three_fund = three_fund_portfolio_builder(risk_level)["allocation"]
    
    # Convert back to numbers for calculation
    us_stocks = float(three_fund["US Stocks"].replace("%", ""))
    international = float(three_fund["International Stocks"].replace("%", ""))
    bonds = float(three_fund["Bonds"].replace("%", ""))
    
    # Allocate 5-10% to fourth asset class
    fourth_asset_pct = 8 if risk_level == "moderate" else 5 if risk_level == "conservative" else 10
    
    # Reduce other allocations proportionally 
    reduction_factor = (100 - fourth_asset_pct) / 100
    us_stocks *= reduction_factor
    international *= reduction_factor
    bonds *= reduction_factor
    
    if include_reits:
        fourth_asset_name = "REITs"
        fourth_etf = {
            "symbol": "VNQ",
            "name": "Vanguard Real Estate Index Fund ETF",
            "expense_ratio": 0.12,
            "description": "US real estate investment trusts"
        }
    else:
        fourth_asset_name = "Small-Cap Value"
        fourth_etf = {
            "symbol": "VBR", 
            "name": "Vanguard Small-Cap Value ETF",
            "expense_ratio": 0.07,
            "description": "Small-cap value stocks for enhanced returns"
        }
    
    allocation = {
        "us_stocks": us_stocks,
        "international_stocks": international,
        "bonds": bonds,
        fourth_asset_name.lower().replace("-", "_"): fourth_asset_pct
    }
    
    # ETF recommendations
    etfs = [
        {
            "asset_class": "US Stocks",
            "symbol": "VTI",
            "fund_name": "Vanguard Total Stock Market ETF", 
            "allocation": f"{us_stocks:.0f}%",
            "expense_ratio": "0.03%",
            "description": "Entire US stock market"
        },
        {
            "asset_class": "International Stocks",
            "symbol": "VTIAX", 
            "fund_name": "Vanguard Total International Stock Index Fund",
            "allocation": f"{international:.0f}%",
            "expense_ratio": "0.11%",
            "description": "International developed and emerging markets"
        },
        {
            "asset_class": "Bonds",
            "symbol": "BND",
            "fund_name": "Vanguard Total Bond Market ETF",
            "allocation": f"{bonds:.0f}%", 
            "expense_ratio": "0.03%",
            "description": "Broad US bond market"
        },
        {
            "asset_class": fourth_asset_name,
            "symbol": fourth_etf["symbol"],
            "fund_name": fourth_etf["name"],
            "allocation": f"{fourth_asset_pct:.0f}%",
            "expense_ratio": f"{fourth_etf['expense_ratio']:.2f}%",
            "description": fourth_etf["description"]
        }
    ]
    
    # Calculate costs
    total_expense_ratio = (0.03 * us_stocks/100 + 0.11 * international/100 + 
                          0.03 * bonds/100 + fourth_etf["expense_ratio"] * fourth_asset_pct/100)
    
    return {
        "success": True,
        "portfolio_type": f"4-Fund Lazy Portfolio (with {fourth_asset_name})",
        "risk_level": risk_level,
        "allocation": {etf["asset_class"]: etf["allocation"] for etf in etfs},
        "etf_recommendations": etfs,
        "portfolio_cost": {
            "total_expense_ratio": f"{total_expense_ratio:.2f}%",
            "annual_cost_on_10k": f"${total_expense_ratio * 100:.0f}"
        },
        "plain_english_summary": (
            f"A {risk_level} 4-fund portfolio adds {fourth_asset_name.lower()} for extra diversification. "
            f"Buy {us_stocks:.0f}% VTI, {international:.0f}% VTIAX, {bonds:.0f}% BND, "
            f"and {fourth_asset_pct}% {fourth_etf['symbol']}. Total cost: {total_expense_ratio:.2f}% per year."
        ),
        "vs_three_fund": {
            "additional_diversification": f"{fourth_asset_name} exposure for broader diversification",
            "slightly_higher_cost": f"About {(total_expense_ratio - 0.05) * 100:.0f}% more in fees annually",
            "more_complexity": "One additional fund to track and rebalance"
        }
    }


def target_date_portfolio_analyzer(
    target_retirement_year: int,
    current_year: int = 2024
) -> Dict[str, Any]:
    """
    Analyze target-date fund allocation strategy
    
    Perfect for: "Should I just use a target-date fund?"
    
    Args:
        target_retirement_year: Year you plan to retire
        current_year: Current year
        
    Returns:
        Dict with target-date analysis and comparison to lazy portfolios
    """
    
    years_to_retirement = target_retirement_year - current_year
    
    # Typical target-date glide path  
    if years_to_retirement > 40:
        stocks_pct = 90
    elif years_to_retirement > 30:
        stocks_pct = 85
    elif years_to_retirement > 20:
        stocks_pct = 80
    elif years_to_retirement > 10:
        stocks_pct = 70 - (20 - years_to_retirement) * 2
    else:
        stocks_pct = max(40, 70 - (20 - years_to_retirement) * 2)
    
    bonds_pct = 100 - stocks_pct
    
    # Typical target-date fund expense ratios
    expense_ratios = {
        "vanguard": 0.15,
        "fidelity": 0.12, 
        "schwab": 0.08
    }
    
    # Compare to 3-fund portfolio
    three_fund_cost = 0.05  # Approximate
    cost_difference = expense_ratios["vanguard"] - three_fund_cost
    cost_on_100k = cost_difference * 1000  # Annual cost difference on $100k
    
    return {
        "success": True,
        "target_date_analysis": {
            "target_retirement_year": target_retirement_year,
            "years_to_retirement": years_to_retirement,
            "current_allocation": {
                "stocks": f"{stocks_pct}%",
                "bonds": f"{bonds_pct}%"
            },
            "glide_path": "Automatically becomes more conservative as you age"
        },
        "fund_options": [
            {
                "provider": "Vanguard",
                "fund_name": f"Target Retirement {target_retirement_year} Fund",
                "symbol": f"VTTSX",  # Approximation
                "expense_ratio": f"{expense_ratios['vanguard']:.2f}%"
            },
            {
                "provider": "Fidelity", 
                "fund_name": f"Freedom {target_retirement_year} Fund",
                "symbol": f"FFTTX",  # Approximation
                "expense_ratio": f"{expense_ratios['fidelity']:.2f}%"
            },
            {
                "provider": "Schwab",
                "fund_name": f"Target {target_retirement_year} Fund", 
                "symbol": f"SWTTX",  # Approximation
                "expense_ratio": f"{expense_ratios['schwab']:.2f}%"
            }
        ],
        "pros_and_cons": {
            "pros": [
                "Ultimate simplicity - one fund does everything",
                "Automatic rebalancing",
                "Age-appropriate allocation that adjusts over time", 
                "Professional management of glide path",
                "Great for 401(k) accounts"
            ],
            "cons": [
                f"Higher costs - about ${cost_on_100k:.0f}/year more on $100k vs 3-fund portfolio",
                "Less control over allocation",
                "May be too conservative near retirement",
                "All eggs in one fund family basket"
            ]
        },
        "vs_lazy_portfolio": {
            "cost_comparison": f"Target-date costs ~{expense_ratios['vanguard']:.2f}% vs {three_fund_cost:.2f}% for 3-fund",
            "complexity": "Target-date: 1 fund vs 3-fund: 3 funds to manage",
            "control": "3-fund gives you more control over allocation",
            "recommendation": (
                "Target-date if you want maximum simplicity" if years_to_retirement > 10 
                else "Consider 3-fund for more control as you near retirement"
            )
        },
        "plain_english_summary": (
            f"A target {target_retirement_year} fund would currently be {stocks_pct}% stocks, {bonds_pct}% bonds. "
            f"It costs about ${cost_on_100k:.0f} more per year on $100k than a 3-fund portfolio, "
            f"but handles everything automatically. Great choice if you value simplicity over cost savings."
        )
    }


def lazy_portfolio_comparison(
    investment_amount: float = 100000
) -> Dict[str, Any]:
    """
    Compare different lazy portfolio strategies
    
    Perfect for: "Which lazy portfolio is best for me?"
    
    Args:
        investment_amount: Investment amount for cost calculations
        
    Returns:
        Dict comparing different lazy portfolio approaches
    """
    
    portfolios = {
        "2_fund_simple": {
            "name": "2-Fund (Stocks + Bonds)",
            "allocation": {"US Stocks": 70, "Bonds": 30},
            "etfs": ["VTI", "BND"],
            "expense_ratio": 0.03,
            "complexity": "Minimal",
            "description": "Simplest possible - just US stocks and bonds"
        },
        "3_fund_classic": {
            "name": "3-Fund Classic",
            "allocation": {"US Stocks": 60, "International": 20, "Bonds": 20}, 
            "etfs": ["VTI", "VTIAX", "BND"],
            "expense_ratio": 0.05,
            "complexity": "Low",
            "description": "The gold standard - global stock diversification"
        },
        "4_fund_reits": {
            "name": "4-Fund (with REITs)",
            "allocation": {"US Stocks": 50, "International": 20, "Bonds": 20, "REITs": 10},
            "etfs": ["VTI", "VTIAX", "BND", "VNQ"],
            "expense_ratio": 0.06,
            "complexity": "Moderate",
            "description": "Adds real estate for diversification"
        },
        "target_date": {
            "name": "Target-Date Fund",
            "allocation": {"Target Fund": 100},
            "etfs": ["VTTSX"],
            "expense_ratio": 0.15,
            "complexity": "Minimal",
            "description": "One fund handles everything automatically"
        }
    }
    
    # Calculate annual costs
    for portfolio in portfolios.values():
        annual_cost = investment_amount * (portfolio["expense_ratio"] / 100)
        portfolio["annual_cost"] = f"${annual_cost:.0f}"
        portfolio["expense_ratio_display"] = f"{portfolio['expense_ratio']:.2f}%"
    
    # Create comparison matrix
    comparison_matrix = []
    for key, portfolio in portfolios.items():
        comparison_matrix.append({
            "strategy": portfolio["name"],
            "funds_needed": len(portfolio["etfs"]),
            "annual_cost": portfolio["annual_cost"],
            "complexity": portfolio["complexity"],
            "best_for": _best_for_description(key)
        })
    
    return {
        "success": True,
        "investment_amount": f"${investment_amount:,.0f}",
        "portfolio_options": portfolios,
        "comparison_matrix": comparison_matrix,
        "cost_ranking": sorted(
            [(name, data["annual_cost"]) for name, data in portfolios.items()],
            key=lambda x: float(x[1].replace("$", "").replace(",", ""))
        ),
        "recommendations": {
            "beginners": "Start with 3-Fund Classic - proven, simple, effective",
            "hands_off_investors": "Target-Date Fund - ultimate simplicity",
            "cost_conscious": "2-Fund Simple - lowest costs possible", 
            "diversification_seekers": "4-Fund with REITs - maximum diversification"
        },
        "plain_english_summary": (
            f"For ${investment_amount:,.0f}, annual costs range from "
            f"{min([data['annual_cost'] for data in portfolios.values()])} (2-Fund) to "
            f"{max([data['annual_cost'] for data in portfolios.values()])} (Target-Date). "
            f"The 3-Fund Classic offers the best balance of simplicity, diversification, and cost."
        )
    }


def _best_for_description(portfolio_key: str) -> str:
    """Get description of who each portfolio is best for"""
    descriptions = {
        "2_fund_simple": "Ultra-minimalists and cost-conscious investors",
        "3_fund_classic": "Most investors - great balance of simplicity and diversification",
        "4_fund_reits": "Investors wanting maximum diversification",
        "target_date": "Set-and-forget investors who value convenience over cost"
    }
    return descriptions.get(portfolio_key, "Various investor types")


# Registry of lazy portfolio functions
LAZY_PORTFOLIO_FUNCTIONS = {
    'three_fund_portfolio_builder': three_fund_portfolio_builder,
    'four_fund_portfolio_builder': four_fund_portfolio_builder,
    'target_date_portfolio_analyzer': target_date_portfolio_analyzer,
    'lazy_portfolio_comparison': lazy_portfolio_comparison
}


def get_lazy_portfolio_function_names():
    """Get list of all lazy portfolio function names"""
    return list(LAZY_PORTFOLIO_FUNCTIONS.keys())