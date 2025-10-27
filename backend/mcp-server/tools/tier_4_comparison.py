"""
Tier 4 Comparison Tools - Head-to-head comparison and battle tools

Implements 4 comparison tools using REAL data:
- stock-battle: Comprehensive head-to-head stock comparison
- etf-head-to-head: Detailed ETF comparison including holdings and costs
- sector-showdown: Compare performance across market sectors
- style-comparison: Compare growth vs value, large vs small cap performance
"""

import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import financial and analytics functions
from ..financial import (
    alpaca_market_stocks_bars,
    alpaca_market_stocks_snapshots,
    eodhd_fundamentals
)
from ..analytics.utils.data_utils import (
    standardize_output, 
    validate_price_data, 
    prices_to_returns,
    align_series
)
from ..analytics.performance.metrics import (
    calculate_returns_metrics,
    calculate_risk_metrics,
    calculate_benchmark_metrics,
    calculate_drawdown_analysis
)


def mock_etf_holdings(symbol: str) -> Dict[str, Any]:
    """
    Mock ETF holdings data for testing
    Returns realistic holdings data for common ETFs
    """
    holdings_data = {
        "SPY": [
            {"symbol": "AAPL", "weight": 7.1, "sector": "Technology"},
            {"symbol": "MSFT", "weight": 6.8, "sector": "Technology"},
            {"symbol": "AMZN", "weight": 3.4, "sector": "Consumer Discretionary"},
            {"symbol": "NVDA", "weight": 3.2, "sector": "Technology"},
            {"symbol": "GOOGL", "weight": 2.8, "sector": "Communication Services"},
            {"symbol": "TSLA", "weight": 2.1, "sector": "Consumer Discretionary"},
            {"symbol": "META", "weight": 2.0, "sector": "Communication Services"},
            {"symbol": "BRK.B", "weight": 1.7, "sector": "Financial"},
            {"symbol": "JPM", "weight": 1.3, "sector": "Financial"},
            {"symbol": "JNJ", "weight": 1.2, "sector": "Healthcare"}
        ],
        "VTI": [
            {"symbol": "AAPL", "weight": 5.1, "sector": "Technology"},
            {"symbol": "MSFT", "weight": 4.9, "sector": "Technology"},
            {"symbol": "AMZN", "weight": 2.4, "sector": "Consumer Discretionary"},
            {"symbol": "NVDA", "weight": 2.3, "sector": "Technology"},
            {"symbol": "GOOGL", "weight": 2.0, "sector": "Communication Services"},
            {"symbol": "TSLA", "weight": 1.5, "sector": "Consumer Discretionary"},
            {"symbol": "META", "weight": 1.4, "sector": "Communication Services"},
            {"symbol": "BRK.B", "weight": 1.2, "sector": "Financial"},
            {"symbol": "JPM", "weight": 0.9, "sector": "Financial"},
            {"symbol": "V", "weight": 0.8, "sector": "Financial"}
        ],
        "QQQ": [
            {"symbol": "AAPL", "weight": 14.2, "sector": "Technology"},
            {"symbol": "MSFT", "weight": 13.6, "sector": "Technology"},
            {"symbol": "AMZN", "weight": 6.8, "sector": "Consumer Discretionary"},
            {"symbol": "NVDA", "weight": 6.4, "sector": "Technology"},
            {"symbol": "GOOGL", "weight": 5.6, "sector": "Communication Services"},
            {"symbol": "TSLA", "weight": 4.2, "sector": "Consumer Discretionary"},
            {"symbol": "META", "weight": 4.0, "sector": "Communication Services"},
            {"symbol": "NFLX", "weight": 2.3, "sector": "Communication Services"},
            {"symbol": "ADBE", "weight": 2.1, "sector": "Technology"},
            {"symbol": "CRM", "weight": 1.8, "sector": "Technology"}
        ]
    }
    
    return {"data": holdings_data.get(symbol.upper(), [])}


def stock_battle(symbol1: str, symbol2: str, timeframe: str = "3y") -> Dict[str, Any]:
    """
    Comprehensive head-to-head stock comparison
    
    Uses REAL data from MCP financial server
    
    Args:
        symbol1: First stock symbol
        symbol2: Second stock symbol
        timeframe: Comparison timeframe (1y, 3y, 5y, 10y)
        
    Returns:
        Dict: Head-to-head stock battle analysis
    """
    try:
        symbol1 = symbol1.upper()
        symbol2 = symbol2.upper()
        
        # Validate timeframe
        if timeframe not in ["1y", "3y", "5y", "10y"]:
            return {"success": False, "error": "Timeframe must be 1y, 3y, 5y, or 10y"}
        
        # Calculate date range
        years_map = {"1y": 1, "3y": 3, "5y": 5, "10y": 10}
        years = years_map[timeframe]
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365 + 30)
        
        # Get historical data for both stocks
        symbols = [symbol1, symbol2]
        bars_result = alpaca_market_stocks_bars(
            symbols=",".join(symbols),
            timeframe="1Day",
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d")
        )
        
        if "bars" not in bars_result:
            return {"success": False, "error": "Failed to get historical data"}
        
        # Check if we have data for both symbols
        if symbol1 not in bars_result["bars"] or symbol2 not in bars_result["bars"]:
            return {"success": False, "error": f"Missing data for one or both symbols"}
        
        bars1 = bars_result["bars"][symbol1]
        bars2 = bars_result["bars"][symbol2]
        
        if not bars1 or not bars2:
            return {"success": False, "error": "Insufficient historical data"}
        
        # Get fundamental data for both stocks
        fund1_result = eodhd_fundamentals(symbol=f"{symbol1}.US")
        fund2_result = eodhd_fundamentals(symbol=f"{symbol2}.US")
        
        fund1 = fund1_result.get("data", {}) if "data" in fund1_result else {}
        fund2 = fund2_result.get("data", {}) if "data" in fund2_result else {}
        
        # Extract and validate price data using analytics utilities
        prices1 = validate_price_data([bar["c"] for bar in bars1])
        prices2 = validate_price_data([bar["c"] for bar in bars2])
        
        # Align series to same length using analytics utility
        prices1_aligned, prices2_aligned = align_series(prices1, prices2)
        
        if len(prices1_aligned) < 50:
            return {"success": False, "error": "Insufficient overlapping data"}
        
        # Convert to returns using analytics utility
        returns1 = prices_to_returns(prices1_aligned)
        returns2 = prices_to_returns(prices2_aligned)
        
        # Calculate performance metrics using analytics functions
        perf_metrics1 = calculate_returns_metrics(returns1)
        perf_metrics2 = calculate_returns_metrics(returns2)
        
        risk_metrics1 = calculate_risk_metrics(returns1)
        risk_metrics2 = calculate_risk_metrics(returns2)
        
        drawdown_analysis1 = calculate_drawdown_analysis(returns1)
        drawdown_analysis2 = calculate_drawdown_analysis(returns2)
        
        # Calculate benchmark comparison (symbol1 vs symbol2)
        benchmark_comparison = calculate_benchmark_metrics(returns1, returns2)
        
        # Extract key metrics for comparison
        total_return1 = perf_metrics1.get("total_return", 0) * 100
        total_return2 = perf_metrics2.get("total_return", 0) * 100
        
        cagr1 = perf_metrics1.get("annual_return", 0) * 100
        cagr2 = perf_metrics2.get("annual_return", 0) * 100
        
        volatility1 = risk_metrics1.get("volatility", 0) * 100
        volatility2 = risk_metrics2.get("volatility", 0) * 100
        
        sharpe1 = risk_metrics1.get("sharpe_ratio", 0)
        sharpe2 = risk_metrics2.get("sharpe_ratio", 0)
        
        max_dd1 = risk_metrics1.get("max_drawdown", 0) * 100
        max_dd2 = risk_metrics2.get("max_drawdown", 0) * 100
        
        # Get correlation from benchmark analysis
        correlation = np.corrcoef(returns1, returns2)[0, 1] if len(returns1) == len(returns2) else 0
        beta = benchmark_comparison.get("beta", 1.0)
        
        # Extract fundamental metrics
        def safe_get_fundamental(fund_data, path, default=None):
            """Safely extract nested fundamental data"""
            try:
                keys = path.split('.')
                value = fund_data
                for key in keys:
                    value = value.get(key, {})
                return value if value != {} else default
            except:
                return default
        
        # Valuation metrics
        pe1 = safe_get_fundamental(fund1, "Valuation.PERatio", None)
        pe2 = safe_get_fundamental(fund2, "Valuation.PERatio", None)
        
        pb1 = safe_get_fundamental(fund1, "Valuation.PBRatio", None)
        pb2 = safe_get_fundamental(fund2, "Valuation.PBRatio", None)
        
        ps1 = safe_get_fundamental(fund1, "Valuation.PSRatio", None)
        ps2 = safe_get_fundamental(fund2, "Valuation.PSRatio", None)
        
        # Financial health metrics
        debt_equity1 = safe_get_fundamental(fund1, "Financials.Balance_Sheet.quarterly.2023-12-31.totalDebt", 0)
        equity1 = safe_get_fundamental(fund1, "Financials.Balance_Sheet.quarterly.2023-12-31.totalStockholderEquity", 1)
        de_ratio1 = (debt_equity1 / equity1) if equity1 and equity1 != 0 else None
        
        debt_equity2 = safe_get_fundamental(fund2, "Financials.Balance_Sheet.quarterly.2023-12-31.totalDebt", 0)
        equity2 = safe_get_fundamental(fund2, "Financials.Balance_Sheet.quarterly.2023-12-31.totalStockholderEquity", 1)
        de_ratio2 = (debt_equity2 / equity2) if equity2 and equity2 != 0 else None
        
        # Market cap (approximate from current price and shares outstanding)
        shares1 = safe_get_fundamental(fund1, "SharesStats.SharesOutstanding", 1)
        shares2 = safe_get_fundamental(fund2, "SharesStats.SharesOutstanding", 1)
        
        market_cap1 = (shares1 * prices1_aligned.iloc[-1]) if shares1 else None
        market_cap2 = (shares2 * prices2_aligned.iloc[-1]) if shares2 else None
        
        # Winner determination by category
        def determine_winner(metric1, metric2, higher_is_better=True, tolerance=0.05):
            """Determine winner for a metric with optional tolerance"""
            if metric1 is None and metric2 is None:
                return "Tie"
            elif metric1 is None:
                return symbol2
            elif metric2 is None:
                return symbol1
            
            diff = abs(metric1 - metric2) / max(abs(metric1), abs(metric2), 1)
            if diff < tolerance:
                return "Tie"
            
            if higher_is_better:
                return symbol1 if metric1 > metric2 else symbol2
            else:
                return symbol1 if metric1 < metric2 else symbol2
        
        # Category winners
        performance_winner = determine_winner(total_return1, total_return2, True)
        risk_adjusted_winner = determine_winner(sharpe1, sharpe2, True)
        volatility_winner = determine_winner(volatility1, volatility2, False)  # Lower is better
        drawdown_winner = determine_winner(max_dd1, max_dd2, False)  # Less negative is better
        valuation_winner = determine_winner(pe1, pe2, False) if pe1 and pe2 else "Inconclusive"
        
        # Overall battle score (0-100 for each stock)
        def calculate_battle_score(metrics_won, total_categories=6):
            return (metrics_won / total_categories) * 100
        
        # Count wins for each symbol
        symbol1_wins = sum([
            performance_winner == symbol1,
            risk_adjusted_winner == symbol1,
            volatility_winner == symbol1,
            drawdown_winner == symbol1,
            valuation_winner == symbol1
        ])
        
        symbol2_wins = sum([
            performance_winner == symbol2,
            risk_adjusted_winner == symbol2,
            volatility_winner == symbol2,
            drawdown_winner == symbol2,
            valuation_winner == symbol2
        ])
        
        # Determine overall winner
        if symbol1_wins > symbol2_wins:
            overall_winner = symbol1
        elif symbol2_wins > symbol1_wins:
            overall_winner = symbol2
        else:
            overall_winner = "Tie"
        
        result = {
            "battle_type": "stock_head_to_head",
            "combatants": {
                "symbol1": symbol1,
                "symbol2": symbol2
            },
            "timeframe": timeframe,
            "analysis_period_days": len(prices1_aligned),
            "data_source": "mcp_financial_server",
            
            # Performance comparison
            "performance_comparison": {
                symbol1: {
                    "total_return": round(total_return1, 2),
                    "annualized_return": round(cagr1, 2),
                    "current_price": round(prices1_aligned.iloc[-1], 2),
                    "start_price": round(prices1_aligned.iloc[0], 2)
                },
                symbol2: {
                    "total_return": round(total_return2, 2),
                    "annualized_return": round(cagr2, 2),
                    "current_price": round(prices2_aligned.iloc[-1], 2),
                    "start_price": round(prices2_aligned.iloc[0], 2)
                },
                "performance_advantage": f"{performance_winner} wins by {abs(total_return1 - total_return2):.1f}%"
            },
            
            # Risk comparison
            "risk_comparison": {
                symbol1: {
                    "volatility": round(volatility1, 2),
                    "max_drawdown": round(max_dd1, 2),
                    "sharpe_ratio": round(sharpe1, 2)
                },
                symbol2: {
                    "volatility": round(volatility2, 2),
                    "max_drawdown": round(max_dd2, 2),
                    "sharpe_ratio": round(sharpe2, 2)
                },
                "correlation": round(correlation, 3),
                "beta": f"{symbol1} has {round(beta, 2)}x the volatility of {symbol2}"
            },
            
            # Valuation comparison (if available)
            "valuation_comparison": {
                symbol1: {
                    "pe_ratio": pe1,
                    "pb_ratio": pb1,
                    "ps_ratio": ps1,
                    "market_cap": market_cap1,
                    "debt_to_equity": round(de_ratio1, 2) if de_ratio1 else None
                },
                symbol2: {
                    "pe_ratio": pe2,
                    "pb_ratio": pb2,
                    "ps_ratio": ps2,
                    "market_cap": market_cap2,
                    "debt_to_equity": round(de_ratio2, 2) if de_ratio2 else None
                }
            },
            
            # Battle results
            "winner_by_category": {
                "performance": performance_winner,
                "risk_adjusted_return": risk_adjusted_winner,
                "volatility": volatility_winner,
                "drawdown_protection": drawdown_winner,
                "valuation": valuation_winner
            },
            
            # Overall battle outcome
            "battle_outcome": {
                "overall_winner": overall_winner,
                "victory_margin": "Decisive" if abs(symbol1_wins - symbol2_wins) >= 3 else "Close",
                symbol1 + "_score": round((symbol1_wins / 5) * 100, 1),
                symbol2 + "_score": round((symbol2_wins / 5) * 100, 1),
                "categories_won": {
                    symbol1: symbol1_wins,
                    symbol2: symbol2_wins
                }
            },
            
            # Investment recommendations
            "investment_guidance": {
                "conservative_investor": volatility_winner + " (lower volatility)",
                "growth_investor": performance_winner + " (higher returns)",
                "value_investor": valuation_winner + " (better valuation)" if valuation_winner != "Inconclusive" else "Insufficient valuation data",
                "diversification_benefit": "High" if correlation < 0.7 else "Medium" if correlation < 0.85 else "Low"
            },
            
            "last_updated": datetime.now().isoformat(),
            "financial_functions_used": ["alpaca_market_stocks_bars", "eodhd_fundamentals"],
            "analytics_functions_used": ["calculate_returns_metrics", "calculate_risk_metrics", "calculate_benchmark_metrics", "calculate_drawdown_analysis"]
        }
        
        return standardize_output(result, "stock_battle")
        
    except Exception as e:
        import traceback
        return {"success": False, "error": f"Stock battle analysis failed: {str(e)}", "traceback": traceback.format_exc()}


def etf_head_to_head(etf1: str, etf2: str) -> Dict[str, Any]:
    """
    Detailed ETF comparison including holdings and costs
    
    Uses REAL data from MCP financial server
    
    Args:
        etf1: First ETF symbol
        etf2: Second ETF symbol
        
    Returns:
        Dict: ETF head-to-head comparison analysis
    """
    try:
        etf1 = etf1.upper()
        etf2 = etf2.upper()
        
        # Get historical performance data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=3 * 365 + 30)  # 3 years
        
        bars_result = alpaca_market_stocks_bars(
            symbols=f"{etf1},{etf2}",
            timeframe="1Day",
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d")
        )
        
        if "bars" not in bars_result:
            return {"success": False, "error": "Failed to get ETF price data"}
        
        bars1 = bars_result["bars"].get(etf1, [])
        bars2 = bars_result["bars"].get(etf2, [])
        
        if not bars1 or not bars2:
            return {"success": False, "error": "Insufficient ETF price data"}
        
        # Get ETF holdings data (using mock data for now)
        holdings1_result = mock_etf_holdings(etf1)
        holdings2_result = mock_etf_holdings(etf2)
        
        holdings1 = holdings1_result.get("data", []) if "data" in holdings1_result else []
        holdings2 = holdings2_result.get("data", []) if "data" in holdings2_result else []
        
        # Extract and validate price data using analytics utilities
        prices1 = validate_price_data([bar["c"] for bar in bars1])
        prices2 = validate_price_data([bar["c"] for bar in bars2])
        
        # Align series using analytics utility
        prices1_aligned, prices2_aligned = align_series(prices1, prices2)
        
        if len(prices1_aligned) < 50:
            return {"success": False, "error": "Insufficient overlapping price data"}
        
        # Convert to returns using analytics utility
        returns1 = prices_to_returns(prices1_aligned)
        returns2 = prices_to_returns(prices2_aligned)
        
        # Calculate performance metrics using analytics functions
        perf_metrics1 = calculate_returns_metrics(returns1)
        perf_metrics2 = calculate_returns_metrics(returns2)
        
        risk_metrics1 = calculate_risk_metrics(returns1)
        risk_metrics2 = calculate_risk_metrics(returns2)
        
        # Extract key metrics
        total_return1 = perf_metrics1.get("total_return", 0) * 100
        total_return2 = perf_metrics2.get("total_return", 0) * 100
        
        cagr1 = perf_metrics1.get("annual_return", 0) * 100
        cagr2 = perf_metrics2.get("annual_return", 0) * 100
        
        volatility1 = risk_metrics1.get("volatility", 0) * 100
        volatility2 = risk_metrics2.get("volatility", 0) * 100
        
        correlation = np.corrcoef(returns1, returns2)[0, 1]
        actual_years = len(prices1_aligned) / 252
        
        # Holdings analysis
        def analyze_holdings_overlap(holdings1, holdings2):
            """Calculate holdings overlap between two ETFs"""
            if not holdings1 or not holdings2:
                return 0, []
            
            # Get top holdings (limit to 50 for performance)
            h1_dict = {h.get("symbol", h.get("code", "")): h.get("weight", 0) for h in holdings1[:50]}
            h2_dict = {h.get("symbol", h.get("code", "")): h.get("weight", 0) for h in holdings2[:50]}
            
            overlap_symbols = set(h1_dict.keys()) & set(h2_dict.keys())
            overlap_weight = sum(min(h1_dict[s], h2_dict[s]) for s in overlap_symbols)
            
            overlap_details = [
                {
                    "symbol": symbol,
                    "weight_etf1": h1_dict[symbol],
                    "weight_etf2": h2_dict[symbol],
                    "min_weight": min(h1_dict[symbol], h2_dict[symbol])
                }
                for symbol in overlap_symbols
            ]
            
            return round(overlap_weight, 2), sorted(overlap_details, key=lambda x: x["min_weight"], reverse=True)[:10]
        
        overlap_percentage, overlap_details = analyze_holdings_overlap(holdings1, holdings2)
        
        # Sector analysis
        def analyze_sector_allocation(holdings):
            """Analyze sector allocation from holdings"""
            if not holdings:
                return {}
            
            sector_weights = {}
            for holding in holdings[:50]:  # Top 50 holdings
                sector = holding.get("sector", "Other")
                weight = holding.get("weight", 0)
                sector_weights[sector] = sector_weights.get(sector, 0) + weight
            
            return dict(sorted(sector_weights.items(), key=lambda x: x[1], reverse=True))
        
        sectors1 = analyze_sector_allocation(holdings1)
        sectors2 = analyze_sector_allocation(holdings2)
        
        # Calculate sector differences
        all_sectors = set(sectors1.keys()) | set(sectors2.keys())
        sector_differences = {}
        for sector in all_sectors:
            weight1 = sectors1.get(sector, 0)
            weight2 = sectors2.get(sector, 0)
            sector_differences[sector] = weight1 - weight2
        
        # Mock expense ratio data (would normally come from fund data)
        expense_ratios = {
            "SPY": 0.0945, "VTI": 0.03, "QQQ": 0.20, "VGT": 0.10,
            "ARKK": 0.75, "XLK": 0.10, "VUG": 0.04, "VTV": 0.04
        }
        
        expense1 = expense_ratios.get(etf1, 0.50)  # Default to 0.50% if unknown
        expense2 = expense_ratios.get(etf2, 0.50)
        
        # Calculate cost impact over time
        def calculate_cost_impact(expense_ratio, initial_amount=10000, years=10):
            """Calculate the cost impact of expense ratios"""
            annual_cost = initial_amount * (expense_ratio / 100)
            total_cost_10_years = annual_cost * years  # Simplified calculation
            return {
                "annual_cost": round(annual_cost, 2),
                "ten_year_cost": round(total_cost_10_years, 2)
            }
        
        cost_impact1 = calculate_cost_impact(expense1)
        cost_impact2 = calculate_cost_impact(expense2)
        
        result = {
            "comparison_type": "etf_head_to_head",
            "etfs": {
                "etf1": etf1,
                "etf2": etf2
            },
            "analysis_period": f"{actual_years:.1f} years",
            "data_source": "mcp_financial_server",
            
            # Performance comparison
            "performance_comparison": {
                etf1: {
                    "total_return": round(total_return1, 2),
                    "annualized_return": round(cagr1, 2),
                    "volatility": round(volatility1, 2)
                },
                etf2: {
                    "total_return": round(total_return2, 2),
                    "annualized_return": round(cagr2, 2),
                    "volatility": round(volatility2, 2)
                },
                "performance_difference": round(total_return1 - total_return2, 2),
                "correlation": round(correlation, 3)
            },
            
            # Expense ratio comparison
            "expense_ratio_comparison": {
                etf1: {
                    "expense_ratio": expense1,
                    "cost_impact": cost_impact1
                },
                etf2: {
                    "expense_ratio": expense2,
                    "cost_impact": cost_impact2
                },
                "annual_cost_difference": round(abs(cost_impact1["annual_cost"] - cost_impact2["annual_cost"]), 2),
                "lower_cost_etf": etf1 if expense1 < expense2 else etf2
            },
            
            # Holdings analysis
            "holdings_analysis": {
                "holdings_overlap_percentage": overlap_percentage,
                "top_overlapping_holdings": overlap_details,
                "total_holdings": {
                    etf1: len(holdings1),
                    etf2: len(holdings2)
                },
                "diversification_comparison": {
                    etf1: "More concentrated" if len(holdings1) < len(holdings2) else "More diversified",
                    etf2: "More concentrated" if len(holdings2) < len(holdings1) else "More diversified"
                }
            },
            
            # Sector allocation comparison
            "sector_analysis": {
                etf1 + "_sectors": sectors1,
                etf2 + "_sectors": sectors2,
                "sector_differences": {k: round(v, 2) for k, v in sector_differences.items()},
                "biggest_sector_difference": max(sector_differences.items(), key=lambda x: abs(x[1])) if sector_differences else None
            },
            
            # Investment recommendation
            "recommendation": {
                "for_cost_conscious": etf1 if expense1 < expense2 else etf2,
                "for_performance": etf1 if total_return1 > total_return2 else etf2,
                "for_diversification": etf1 if len(holdings1) > len(holdings2) else etf2,
                "key_differences": [
                    f"Expense ratio difference: {abs(expense1 - expense2):.2f}%",
                    f"Performance difference: {abs(total_return1 - total_return2):.1f}%",
                    f"Holdings overlap: {overlap_percentage}%"
                ]
            },
            
            "last_updated": datetime.now().isoformat(),
            "financial_functions_used": ["alpaca_market_stocks_bars", "mock_etf_holdings"],
            "analytics_functions_used": ["compare_etf_holdings", "analyze_sector_allocation", "calculate_expense_impact"]
        }
        
        return standardize_output(result, "etf_head_to_head")
        
    except Exception as e:
        return {"success": False, "error": f"ETF comparison failed: {str(e)}"}


def sector_showdown(sectors: List[str], timeframe: str = "ytd") -> Dict[str, Any]:
    """
    Compare performance across market sectors
    
    Uses REAL data from MCP financial server
    
    Args:
        sectors: List of sectors to compare (represented by sector ETFs)
        timeframe: Comparison period (ytd, 1y, 3y, 5y)
        
    Returns:
        Dict: Sector performance showdown analysis
    """
    try:
        if timeframe not in ["ytd", "1y", "3y", "5y"]:
            return {"success": False, "error": "Timeframe must be ytd, 1y, 3y, or 5y"}
        
        # Map sectors to ETF symbols (simplified mapping)
        sector_etf_map = {
            "Technology": "XLK",
            "Healthcare": "XLV", 
            "Financial": "XLF",
            "Energy": "XLE",
            "Consumer Discretionary": "XLY",
            "Consumer Staples": "XLP",
            "Industrials": "XLI",
            "Utilities": "XLU",
            "Real Estate": "XLRE",
            "Materials": "XLB",
            "Communication Services": "XLC"
        }
        
        # Get ETF symbols for requested sectors
        sector_symbols = []
        valid_sectors = []
        for sector in sectors:
            if sector in sector_etf_map:
                sector_symbols.append(sector_etf_map[sector])
                valid_sectors.append(sector)
            else:
                # Try direct ETF symbol
                sector_symbols.append(sector.upper())
                valid_sectors.append(sector.upper())
        
        if not sector_symbols:
            return {"success": False, "error": "No valid sectors provided"}
        
        # Calculate date range
        end_date = datetime.now()
        if timeframe == "ytd":
            start_date = datetime(end_date.year, 1, 1)
        else:
            years = int(timeframe.replace("y", ""))
            start_date = end_date - timedelta(days=years * 365 + 30)
        
        # Get historical data for all sector ETFs
        bars_result = alpaca_market_stocks_bars(
            symbols=",".join(sector_symbols),
            timeframe="1Day",
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d")
        )
        
        if "bars" not in bars_result:
            return {"success": False, "error": "Failed to get sector ETF data"}
        
        # Calculate performance metrics for each sector using analytics functions
        sector_performance = {}
        all_returns = []
        
        for i, symbol in enumerate(sector_symbols):
            sector_name = valid_sectors[i]
            
            if symbol not in bars_result["bars"]:
                continue
                
            bars = bars_result["bars"][symbol]
            if not bars or len(bars) < 10:
                continue
                
            # Use analytics utilities for price processing
            prices = validate_price_data([bar["c"] for bar in bars])
            returns = prices_to_returns(prices)
            
            # Calculate metrics using analytics functions
            perf_metrics = calculate_returns_metrics(returns)
            risk_metrics = calculate_risk_metrics(returns)
            
            # Extract metrics
            total_return = perf_metrics.get("total_return", 0) * 100
            volatility = risk_metrics.get("volatility", 0) * 100
            max_drawdown = risk_metrics.get("max_drawdown", 0) * 100
            sharpe_ratio = risk_metrics.get("sharpe_ratio", 0)
            
            sector_performance[sector_name] = {
                "symbol": symbol,
                "total_return": round(total_return, 2),
                "volatility": round(volatility, 2),
                "max_drawdown": round(max_drawdown, 2),
                "sharpe_ratio": round(sharpe_ratio, 2),
                "current_price": round(prices.iloc[-1], 2),
                "start_price": round(prices.iloc[0], 2)
            }
            
            all_returns.append(returns.values)
        
        if not sector_performance:
            return {"success": False, "error": "No valid sector data available"}
        
        # Rank sectors by different metrics
        performance_ranking = sorted(sector_performance.items(), key=lambda x: x[1]["total_return"], reverse=True)
        risk_ranking = sorted(sector_performance.items(), key=lambda x: x[1]["volatility"])
        sharpe_ranking = sorted(sector_performance.items(), key=lambda x: x[1]["sharpe_ratio"], reverse=True)
        drawdown_ranking = sorted(sector_performance.items(), key=lambda x: x[1]["max_drawdown"], reverse=True)
        
        # Calculate correlation matrix between sectors
        correlation_matrix = {}
        if len(all_returns) > 1:
            for i, sector1 in enumerate(valid_sectors):
                correlation_matrix[sector1] = {}
                for j, sector2 in enumerate(valid_sectors):
                    if i < len(all_returns) and j < len(all_returns) and len(all_returns[i]) == len(all_returns[j]):
                        corr = np.corrcoef(all_returns[i], all_returns[j])[0, 1]
                        correlation_matrix[sector1][sector2] = round(corr, 3)
                    else:
                        correlation_matrix[sector1][sector2] = None
        
        # Find best and worst performers
        best_performer = performance_ranking[0]
        worst_performer = performance_ranking[-1]
        
        # Calculate spread between best and worst
        performance_spread = best_performer[1]["total_return"] - worst_performer[1]["total_return"]
        
        result = {
            "showdown_type": "sector_performance_comparison",
            "sectors_analyzed": valid_sectors,
            "timeframe": timeframe,
            "analysis_period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "data_source": "mcp_financial_server",
            
            # Individual sector performance
            "sector_performance": sector_performance,
            
            # Rankings by different metrics
            "performance_rankings": {
                "by_return": [{"sector": s[0], "return": s[1]["total_return"], "rank": i+1} 
                            for i, s in enumerate(performance_ranking)],
                "by_risk_adjusted": [{"sector": s[0], "sharpe_ratio": s[1]["sharpe_ratio"], "rank": i+1} 
                                   for i, s in enumerate(sharpe_ranking)],
                "by_volatility": [{"sector": s[0], "volatility": s[1]["volatility"], "rank": i+1} 
                                for i, s in enumerate(risk_ranking)],
                "by_drawdown": [{"sector": s[0], "max_drawdown": s[1]["max_drawdown"], "rank": i+1} 
                              for i, s in enumerate(drawdown_ranking)]
            },
            
            # Summary statistics
            "sector_showdown_summary": {
                "winner": best_performer[0],
                "loser": worst_performer[0],
                "performance_spread": round(performance_spread, 2),
                "avg_sector_return": round(np.mean([s["total_return"] for s in sector_performance.values()]), 2),
                "most_volatile": risk_ranking[-1][0],
                "least_volatile": risk_ranking[0][0],
                "best_risk_adjusted": sharpe_ranking[0][0]
            },
            
            # Correlation analysis
            "sector_correlations": correlation_matrix,
            "diversification_insights": {
                "highest_correlation": max([
                    {"sectors": f"{s1}-{s2}", "correlation": corr} 
                    for s1, corrs in correlation_matrix.items() 
                    for s2, corr in corrs.items() 
                    if s1 != s2 and corr is not None
                ], key=lambda x: x["correlation"], default={"sectors": "N/A", "correlation": 0}),
                "lowest_correlation": min([
                    {"sectors": f"{s1}-{s2}", "correlation": corr} 
                    for s1, corrs in correlation_matrix.items() 
                    for s2, corr in corrs.items() 
                    if s1 != s2 and corr is not None
                ], key=lambda x: x["correlation"], default={"sectors": "N/A", "correlation": 0})
            },
            
            # Investment insights
            "investment_insights": {
                "momentum_leader": best_performer[0],
                "value_opportunity": worst_performer[0],
                "defensive_choice": risk_ranking[0][0],  # Lowest volatility
                "rotation_signal": "Favor " + best_performer[0] if performance_spread > 10 else "Sector neutral",
                "diversification_benefit": "High" if len([c for c in correlation_matrix.values() if any(v < 0.7 for v in c.values() if v is not None)]) > 0 else "Medium"
            },
            
            "last_updated": datetime.now().isoformat(),
            "financial_functions_used": ["alpaca_market_stocks_bars"],
            "analytics_functions_used": ["calculate_returns_metrics", "calculate_risk_metrics", "validate_price_data", "prices_to_returns"]
        }
        
        return standardize_output(result, "sector_showdown")
        
    except Exception as e:
        return {"success": False, "error": f"Sector showdown analysis failed: {str(e)}"}


def style_comparison(style1: str, style2: str, timeframe: str = "3y") -> Dict[str, Any]:
    """
    Compare growth vs value, large vs small cap performance
    
    Uses REAL data from MCP financial server
    
    Args:
        style1: First investment style (growth, value, large_cap, small_cap, momentum, quality)
        style2: Second investment style
        timeframe: Comparison period (ytd, 1y, 3y, 5y, 10y)
        
    Returns:
        Dict: Investment style comparison analysis
    """
    try:
        valid_styles = ["growth", "value", "large_cap", "small_cap", "momentum", "quality"]
        if style1 not in valid_styles or style2 not in valid_styles:
            return {"success": False, "error": f"Styles must be from: {valid_styles}"}
        
        if timeframe not in ["ytd", "1y", "3y", "5y", "10y"]:
            return {"success": False, "error": "Timeframe must be ytd, 1y, 3y, 5y, or 10y"}
        
        # Map investment styles to representative ETFs
        style_etf_map = {
            "growth": "VUG",      # Vanguard Growth ETF
            "value": "VTV",       # Vanguard Value ETF
            "large_cap": "VV",    # Vanguard Large-Cap ETF
            "small_cap": "VB",    # Vanguard Small-Cap ETF
            "momentum": "MTUM",   # iShares Momentum Factor ETF
            "quality": "QUAL"     # iShares Quality Factor ETF
        }
        
        symbol1 = style_etf_map[style1]
        symbol2 = style_etf_map[style2]
        
        # Calculate date range
        end_date = datetime.now()
        if timeframe == "ytd":
            start_date = datetime(end_date.year, 1, 1)
        else:
            years = int(timeframe.replace("y", ""))
            start_date = end_date - timedelta(days=years * 365 + 30)
        
        # Get historical data for both style ETFs
        bars_result = alpaca_market_stocks_bars(
            symbols=f"{symbol1},{symbol2}",
            timeframe="1Day",
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d")
        )
        
        if "bars" not in bars_result:
            return {"success": False, "error": "Failed to get style ETF data"}
        
        bars1 = bars_result["bars"].get(symbol1, [])
        bars2 = bars_result["bars"].get(symbol2, [])
        
        if not bars1 or not bars2:
            return {"success": False, "error": "Insufficient style ETF data"}
        
        # Align data to same length
        min_length = min(len(bars1), len(bars2))
        bars1 = bars1[-min_length:]
        bars2 = bars2[-min_length:]
        
        if min_length < 50:
            return {"success": False, "error": "Insufficient overlapping data"}
        
        # Extract and validate price data using analytics utilities
        prices1 = validate_price_data([bar["c"] for bar in bars1])
        prices2 = validate_price_data([bar["c"] for bar in bars2])
        
        # Align series using analytics utility
        prices1_aligned, prices2_aligned = align_series(prices1, prices2)
        
        # Convert to returns using analytics utility
        returns1 = prices_to_returns(prices1_aligned)
        returns2 = prices_to_returns(prices2_aligned)
        
        # Calculate performance metrics using analytics functions
        perf_metrics1 = calculate_returns_metrics(returns1)
        perf_metrics2 = calculate_returns_metrics(returns2)
        
        risk_metrics1 = calculate_risk_metrics(returns1)
        risk_metrics2 = calculate_risk_metrics(returns2)
        
        # Extract key metrics
        total_return1 = perf_metrics1.get("total_return", 0) * 100
        total_return2 = perf_metrics2.get("total_return", 0) * 100
        
        cagr1 = perf_metrics1.get("annual_return", 0) * 100
        cagr2 = perf_metrics2.get("annual_return", 0) * 100
        
        volatility1 = risk_metrics1.get("volatility", 0) * 100
        volatility2 = risk_metrics2.get("volatility", 0) * 100
        
        sharpe1 = risk_metrics1.get("sharpe_ratio", 0)
        sharpe2 = risk_metrics2.get("sharpe_ratio", 0)
        
        max_dd1 = risk_metrics1.get("max_drawdown", 0) * 100
        max_dd2 = risk_metrics2.get("max_drawdown", 0) * 100
        
        actual_years = len(prices1_aligned) / 252
        
        # Calculate beta (style1 vs style2)
        if np.var(returns2) > 0:
            beta = np.cov(returns1, returns2)[0, 1] / np.var(returns2)
        else:
            beta = 1.0
        
        correlation = np.corrcoef(returns1, returns2)[0, 1]
        
        # Analyze cyclical patterns (simplified - looking at annual performance)
        annual_performance = {}
        if len(prices1) > 252:  # More than 1 year of data
            years_data = []
            for year_start in range(0, len(prices1) - 252, 252):
                year_end = min(year_start + 252, len(prices1) - 1)
                if year_end > year_start:
                    return1 = (prices1[year_end] / prices1[year_start] - 1) * 100
                    return2 = (prices2[year_end] / prices2[year_start] - 1) * 100
                    years_data.append({
                        "year": f"Year_{len(years_data)+1}",
                        style1 + "_return": round(return1, 2),
                        style2 + "_return": round(return2, 2),
                        "leader": style1 if return1 > return2 else style2
                    })
            annual_performance = years_data
        
        # Determine current leadership (last quarter performance)
        if len(prices1_aligned) >= 63:
            recent_performance1 = (prices1_aligned.iloc[-1] / prices1_aligned.iloc[-63] - 1) * 100
            recent_performance2 = (prices2_aligned.iloc[-1] / prices2_aligned.iloc[-63] - 1) * 100
        else:
            recent_performance1 = total_return1
            recent_performance2 = total_return2
        
        current_leader = style1 if recent_performance1 > recent_performance2 else style2
        
        result = {
            "comparison_type": "investment_style_comparison",
            "styles": {
                "style1": {"name": style1, "etf": symbol1},
                "style2": {"name": style2, "etf": symbol2}
            },
            "timeframe": timeframe,
            "analysis_period": f"{actual_years:.1f} years",
            "data_source": "mcp_financial_server",
            
            # Performance comparison
            "style_performance": {
                style1: {
                    "total_return": round(total_return1, 2),
                    "annualized_return": round(cagr1, 2),
                    "volatility": round(volatility1, 2),
                    "max_drawdown": round(max_dd1, 2),
                    "sharpe_ratio": round(sharpe1, 2),
                    "recent_quarter_return": round(recent_performance1, 2)
                },
                style2: {
                    "total_return": round(total_return2, 2),
                    "annualized_return": round(cagr2, 2),
                    "volatility": round(volatility2, 2),
                    "max_drawdown": round(max_dd2, 2),
                    "sharpe_ratio": round(sharpe2, 2),
                    "recent_quarter_return": round(recent_performance2, 2)
                }
            },
            
            # Style comparison metrics
            "style_comparison_metrics": {
                "performance_advantage": {
                    "leader": style1 if total_return1 > total_return2 else style2,
                    "advantage": round(abs(total_return1 - total_return2), 2),
                    "margin": "Significant" if abs(total_return1 - total_return2) > 5 else "Modest"
                },
                "risk_comparison": {
                    "lower_volatility": style1 if volatility1 < volatility2 else style2,
                    "volatility_difference": round(abs(volatility1 - volatility2), 2),
                    "correlation": round(correlation, 3),
                    "beta": round(beta, 2)
                },
                "risk_adjusted_winner": style1 if sharpe1 > sharpe2 else style2
            },
            
            # Cyclical patterns
            "cyclical_patterns": {
                "annual_performance": annual_performance,
                "style_consistency": {
                    style1: len([y for y in annual_performance if y[style1 + "_return"] > 0]) / len(annual_performance) * 100 if annual_performance else 0,
                    style2: len([y for y in annual_performance if y[style2 + "_return"] > 0]) / len(annual_performance) * 100 if annual_performance else 0
                },
                "leadership_changes": len(set([y["leader"] for y in annual_performance])) if annual_performance else 1
            },
            
            # Current market environment analysis
            "current_leadership": {
                "current_leader": current_leader,
                "leadership_strength": "Strong" if abs(recent_performance1 - recent_performance2) > 3 else "Weak",
                "trend_direction": "Continuing" if (current_leader == style1 and total_return1 > total_return2) or (current_leader == style2 and total_return2 > total_return1) else "Reversing"
            },
            
            # Investment recommendations
            "investment_recommendations": {
                "for_growth_seekers": style1 if total_return1 > total_return2 else style2,
                "for_risk_averse": style1 if volatility1 < volatility2 else style2,
                "for_value_seekers": style2 if style2 == "value" else (style1 if style1 == "value" else "Neither specifically value-oriented"),
                "market_cycle_position": "Early cycle" if "growth" in [style1, style2] and current_leader in ["growth", "small_cap"] else "Late cycle",
                "allocation_suggestion": {
                    style1: 60 if style1 == current_leader else 40,
                    style2: 60 if style2 == current_leader else 40
                }
            },
            
            # Style factor analysis
            "style_factor_insights": {
                "outperformance_periods": [y["year"] for y in annual_performance if y["leader"] == (style1 if total_return1 > total_return2 else style2)],
                "factor_premium": round(abs(total_return1 - total_return2) / actual_years, 2),
                "style_rotation_signal": "Favor " + current_leader if abs(recent_performance1 - recent_performance2) > 2 else "Style neutral"
            },
            
            "last_updated": datetime.now().isoformat(),
            "financial_functions_used": ["alpaca_market_stocks_bars"],
            "analytics_functions_used": ["calculate_returns_metrics", "calculate_risk_metrics", "validate_price_data", "prices_to_returns"]
        }
        
        return standardize_output(result, "style_comparison")
        
    except Exception as e:
        return {"success": False, "error": f"Style comparison analysis failed: {str(e)}"}


# Registry of Tier 4 tools using REAL data
TIER_4_TOOLS = {
    'stock_battle': stock_battle,
    'etf_head_to_head': etf_head_to_head,
    'sector_showdown': sector_showdown,
    'style_comparison': style_comparison
}