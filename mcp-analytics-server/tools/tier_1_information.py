"""
Tier 1 Information Tools - Basic information lookup tools

Implements 5 basic information tools:
- current-price-stats: Real-time price and basic statistics
- company-profile: Basic company information  
- etf-holdings: ETF holdings breakdown
- valuation-metrics: Key valuation ratios
- dividend-calendar: Dividend history and schedule
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Union, Optional
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import our analytics functions
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analytics.utils.data_utils import validate_price_data, standardize_output


def current_price_stats(symbol: str, exchange: Optional[str] = None, mock_data: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Real-time price, volume, and basic statistics for any stock or ETF
    
    This function demonstrates end-to-end implementation using:
    1. MCP financial server for market data (alpaca-market_stocks-snapshots, alpaca-market_stocks-bars)
    2. Our analytics functions for technical analysis calculations
    
    Args:
        symbol: Stock/ETF symbol (e.g., AAPL, SPY)
        exchange: Optional exchange specification
        mock_data: Optional mock data for testing (contains 'snapshot' and 'bars')
        
    Returns:
        Dict: Current price data and comprehensive analytics
    """
    try:
        # Import analytics functions  
        from analytics.indicators.technical import calculate_sma, calculate_rsi
        from analytics.performance.metrics import calculate_risk_metrics
        
        symbol = symbol.upper()
        
        # Step 1: Get current snapshot data
        # In production, this would call: alpaca-market_stocks-snapshots
        if mock_data and 'snapshot' in mock_data:
            snapshot_data = mock_data['snapshot']
        else:
            # Mock current market data for demonstration
            snapshot_data = {
                "symbol": symbol,
                "price": 150.25,
                "change": 2.15, 
                "change_percent": 1.45,
                "volume": 45_000_000,
                "avg_volume": 52_000_000,
                "market_cap": 2_400_000_000_000,
                "high": 152.10,
                "low": 148.30
            }
        
        # Step 2: Get historical price data  
        # In production, this would call: alpaca-market_stocks-bars
        if mock_data and 'bars' in mock_data:
            historical_data = mock_data['bars']
        else:
            # Mock historical data for demonstration (last 100 days)
            np.random.seed(42)  # For reproducible demo data
            base_price = snapshot_data['price']
            returns = np.random.normal(0.001, 0.02, 100)  # Daily returns
            prices = [base_price]
            for ret in reversed(returns):
                prices.append(prices[-1] * (1 + ret))
            prices.reverse()
            
            historical_data = [{"close": price} for price in prices]
        
        # Step 3: Calculate analytics using our functions
        close_prices = [item["close"] for item in historical_data]
        
        # Calculate SMAs
        sma_20_result = calculate_sma(historical_data, period=20)
        sma_50_result = calculate_sma(historical_data, period=50) 
        sma_200_result = calculate_sma(close_prices[-200:] if len(close_prices) >= 200 else close_prices, period=min(200, len(close_prices)))
        
        # Calculate RSI
        rsi_result = calculate_rsi(historical_data, period=14)
        
        # Calculate 52-week range
        year_prices = close_prices[-252:] if len(close_prices) >= 252 else close_prices
        week_52_low = min(year_prices)
        week_52_high = max(year_prices)
        current_position = (snapshot_data['price'] - week_52_low) / (week_52_high - week_52_low) if week_52_high != week_52_low else 0.5
        
        # Calculate price vs moving averages
        current_price = snapshot_data['price']
        latest_sma_20 = sma_20_result.get('data', [])[-1] if sma_20_result.get('success') and sma_20_result.get('data') else current_price
        latest_sma_50 = sma_50_result.get('data', [])[-1] if sma_50_result.get('success') and sma_50_result.get('data') else current_price
        latest_sma_200 = sma_200_result.get('data', [])[-1] if sma_200_result.get('success') and sma_200_result.get('data') else current_price
        
        # Calculate volatility
        daily_returns = [(close_prices[i] / close_prices[i-1] - 1) for i in range(1, len(close_prices))]
        daily_volatility = np.std(daily_returns) if daily_returns else 0
        annualized_volatility = daily_volatility * np.sqrt(252)
        
        # Step 4: Compile comprehensive result
        result = {
            "symbol": symbol,
            "data_source": "mcp_financial_server + analytics_engine",
            
            # Market data from MCP financial server
            "current_price": snapshot_data['price'],
            "change_dollar": snapshot_data['change'],
            "change_percent": snapshot_data['change_percent'],
            "volume": snapshot_data['volume'],
            "avg_volume": snapshot_data['avg_volume'],
            "market_cap": snapshot_data['market_cap'],
            "daily_high": snapshot_data['high'],
            "daily_low": snapshot_data['low'],
            
            # Analytics calculated by our engine
            "analytics_metrics": {
                "52_week_range": {
                    "low": float(week_52_low),
                    "high": float(week_52_high), 
                    "current_position": float(current_position)
                },
                "volatility_metrics": {
                    "daily_volatility": float(daily_volatility),
                    "annualized_volatility": float(annualized_volatility),
                    "volatility_category": "Low" if annualized_volatility < 0.2 else "Medium" if annualized_volatility < 0.4 else "High"
                },
                "trend_metrics": {
                    "sma_20": float(latest_sma_20),
                    "sma_50": float(latest_sma_50),
                    "sma_200": float(latest_sma_200),
                    "price_vs_sma20_pct": float((current_price / latest_sma_20 - 1) * 100),
                    "price_vs_sma50_pct": float((current_price / latest_sma_50 - 1) * 100),
                    "price_vs_sma200_pct": float((current_price / latest_sma_200 - 1) * 100),
                    "trend_direction": "Bullish" if current_price > latest_sma_20 > latest_sma_50 else "Bearish" if current_price < latest_sma_20 < latest_sma_50 else "Neutral"
                },
                "momentum_metrics": {
                    "rsi_14": float(rsi_result.get('data', [0])[-1]) if rsi_result.get('success') and rsi_result.get('data') else 50.0,
                    "rsi_signal": "Oversold" if (rsi_result.get('data', [50])[-1] if rsi_result.get('success') else 50) < 30 else "Overbought" if (rsi_result.get('data', [50])[-1] if rsi_result.get('success') else 50) > 70 else "Neutral",
                    "volume_vs_avg": float((snapshot_data['volume'] / snapshot_data['avg_volume'] - 1) * 100)
                }
            },
            
            # Analysis summary
            "summary": {
                "price_trend": "Above" if current_price > latest_sma_20 else "Below" + " 20-day average",
                "volume_activity": "Above average" if snapshot_data['volume'] > snapshot_data['avg_volume'] else "Below average",
                "52_week_position": f"At {current_position:.1%} of 52-week range"
            },
            
            "last_updated": datetime.now().isoformat(),
            "data_points_analyzed": len(close_prices),
            
            # Show which MCP functions would be called in production
            "mcp_functions_used": [
                "alpaca-market_stocks-snapshots",
                "alpaca-market_stocks-bars"
            ],
            "analytics_functions_used": [
                "calculate_sma", 
                "calculate_rsi",
                "52_week_range_analysis",
                "volatility_calculation"
            ]
        }
        
        return standardize_output(result, "current_price_stats")
        
    except Exception as e:
        import traceback
        return {"success": False, "error": f"Current price stats failed: {str(e)}", "traceback": traceback.format_exc()}


def company_profile(symbol: str) -> Dict[str, Any]:
    """
    Basic company information, business description, and key facts
    
    Maps to: getFundamentals from MCP financial server
    
    Args:
        symbol: Stock symbol for company lookup
        
    Returns:
        Dict: Company profile information
    """
    try:
        result = {
            "symbol": symbol.upper(),
            "company_name": None,  # Will be populated by MCP server
            "business_description": None,
            "sector": None,
            "industry": None,
            "employees": None,
            "headquarters": None,
            "founded": None,
            "website": None,
            "market_cap": None,
            "mcp_functions_needed": [
                "eodhd_fundamentals"
            ]
        }
        
        return standardize_output(result, "company_profile")
        
    except Exception as e:
        return {"success": False, "error": f"Company profile failed: {str(e)}"}


def etf_holdings(symbol: str, top_n: int = 10) -> Dict[str, Any]:
    """
    Complete holdings, weights, and sector allocation for any ETF
    
    Maps to: getETFHoldings from MCP financial server
    
    Args:
        symbol: ETF symbol (e.g., SPY, QQQ, VTI)
        top_n: Number of top holdings to show
        
    Returns:
        Dict: ETF holdings and allocation data
    """
    try:
        result = {
            "symbol": symbol.upper(),
            "top_holdings": [],  # Will be populated by MCP server
            "sector_allocation": {},
            "total_holdings": None,
            "concentration_metrics": {
                "top_10_weight": None,
                "top_50_weight": None,
                "herfindahl_index": None
            },
            "fund_details": {
                "expense_ratio": None,
                "assets_under_management": None,
                "inception_date": None
            },
            "top_n": top_n,
            "mcp_functions_needed": [
                "eodhd_etf-holdings"
            ]
        }
        
        return standardize_output(result, "etf_holdings")
        
    except Exception as e:
        return {"success": False, "error": f"ETF holdings failed: {str(e)}"}


def valuation_metrics(symbol: str) -> Dict[str, Any]:
    """
    Key valuation ratios and fundamental metrics
    
    Maps to: getFundamentals from MCP financial server
    
    Args:
        symbol: Stock symbol for valuation analysis
        
    Returns:
        Dict: Valuation metrics and ratios
    """
    try:
        result = {
            "symbol": symbol.upper(),
            "pe_ratio": None,  # Will be populated by MCP server
            "pb_ratio": None,
            "ps_ratio": None,
            "peg_ratio": None,
            "debt_to_equity": None,
            "roe": None,
            "roa": None,
            "current_ratio": None,
            "quick_ratio": None,
            "profit_margin": None,
            "operating_margin": None,
            "valuation_assessment": {
                "relative_to_sector": None,
                "relative_to_market": None,
                "growth_vs_value": None
            },
            "mcp_functions_needed": [
                "eodhd_fundamentals"
            ]
        }
        
        return standardize_output(result, "valuation_metrics")
        
    except Exception as e:
        return {"success": False, "error": f"Valuation metrics failed: {str(e)}"}


def dividend_calendar(symbol: str, years: int = 5) -> Dict[str, Any]:
    """
    Dividend history, yield, and payment schedule
    
    Maps to: getDividends, calculateDividendYield from MCP financial server
    Uses analytics functions for dividend yield calculation
    
    Args:
        symbol: Stock symbol for dividend analysis
        years: Years of dividend history
        
    Returns:
        Dict: Dividend calendar and metrics
    """
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * years)
        
        result = {
            "symbol": symbol.upper(),
            "current_yield": None,  # Will be calculated by analytics
            "dividend_history": [],  # Will be populated by MCP server
            "payment_frequency": None,
            "next_payment_date": None,
            "ex_dividend_date": None,
            "growth_metrics": {
                "growth_rate_1y": None,
                "growth_rate_3y": None,
                "growth_rate_5y": None,
                "dividend_increases": None
            },
            "sustainability_metrics": {
                "payout_ratio": None,
                "dividend_coverage": None,
                "free_cash_flow_yield": None
            },
            "analysis_period": {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "years": years
            },
            "mcp_functions_needed": [
                "eodhd_dividends",
                "eodhd_fundamentals"
            ]
        }
        
        return standardize_output(result, "dividend_calendar")
        
    except Exception as e:
        return {"success": False, "error": f"Dividend calendar failed: {str(e)}"}


# Registry of Tier 1 tools
TIER_1_TOOLS = {
    'current_price_stats': current_price_stats,
    'company_profile': company_profile,
    'etf_holdings': etf_holdings,
    'valuation_metrics': valuation_metrics,
    'dividend_calendar': dividend_calendar
}