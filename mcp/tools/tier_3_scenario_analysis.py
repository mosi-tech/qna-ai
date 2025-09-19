"""
Tier 3 Scenario Analysis Tools - What-if scenario and simulation tools

Implements 4 scenario analysis tools using REAL data:
- time-machine-calculator: Calculate returns from any historical investment date
- dca-simulator: Dollar-cost averaging simulation
- crisis-investment-tool: Analyze returns from investing during market crashes
- perfect-timing-tool: Calculate returns from perfect buy low/sell high timing
"""

import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import financial and analytics functions
from ..financial import (
    alpaca_market_stocks_bars,
    eodhd_dividends
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
    calculate_drawdown_analysis
)


def time_machine_calculator(symbol: str, investment_date: str, amount: float, include_dividends: bool = True) -> Dict[str, Any]:
    """
    Calculate returns from any historical investment date
    
    Uses REAL data from MCP financial server
    
    Args:
        symbol: Asset symbol to analyze
        investment_date: Date of hypothetical investment (YYYY-MM-DD)
        amount: Investment amount in dollars
        include_dividends: Include dividend reinvestment
        
    Returns:
        Dict: Time machine investment analysis
    """
    try:
        symbol = symbol.upper()
        
        # Parse investment date
        invest_date = datetime.strptime(investment_date, "%Y-%m-%d")
        current_date = datetime.now()
        
        if invest_date >= current_date:
            return {"success": False, "error": "Investment date must be in the past"}
        
        # Get historical price data
        bars_result = alpaca_market_stocks_bars(
            symbols=symbol,
            timeframe="1Day",
            start=investment_date,
            end=current_date.strftime("%Y-%m-%d")
        )
        
        if "bars" not in bars_result or symbol not in bars_result["bars"]:
            return {"success": False, "error": f"Failed to get historical data for {symbol}"}
        
        bars = bars_result["bars"][symbol]
        if not bars:
            return {"success": False, "error": f"No data available for {symbol} from {investment_date}"}
        
        # Use analytics utilities for price processing
        prices = validate_price_data([bar["c"] for bar in bars])
        returns = prices_to_returns(prices)
        
        # Calculate performance metrics using analytics functions
        perf_metrics = calculate_returns_metrics(returns)
        risk_metrics = calculate_risk_metrics(returns)
        
        # Extract basic investment metrics
        initial_price = prices.iloc[0]
        current_price = prices.iloc[-1]
        initial_shares = amount / initial_price
        
        # Get performance data from analytics
        total_return_no_div = perf_metrics.get("total_return", 0) * 100
        cagr = perf_metrics.get("annual_return", 0) * 100
        
        # Calculate basic values
        current_value_no_div = initial_shares * current_price
        days_invested = len(prices)
        years_invested = days_invested / 365.25
        
        # Initialize dividend variables
        total_dividends = 0
        dividend_shares = 0
        current_value_with_div = current_value_no_div
        
        # Get dividend data if requested
        if include_dividends:
            div_result = eodhd_dividends(
                symbol=f"{symbol}.US",
                from_date=investment_date,
                to_date=current_date.strftime("%Y-%m-%d")
            )
            
            if "data" in div_result and div_result["data"]:
                dividends = div_result["data"]
                
                # Calculate dividend reinvestment
                current_shares = initial_shares
                for dividend in dividends:
                    div_per_share = dividend["amount"]
                    div_date = dividend["date"]
                    
                    # Find price on dividend date for reinvestment
                    div_price = None
                    for bar in bars:
                        if bar["t"][:10] == div_date:
                            div_price = bar["c"]
                            break
                    
                    if div_price:
                        div_payment = current_shares * div_per_share
                        total_dividends += div_payment
                        additional_shares = div_payment / div_price
                        current_shares += additional_shares
                        dividend_shares += additional_shares
                
                current_value_with_div = current_shares * current_price
        
        # Calculate performance metrics
        total_return_with_div = (current_value_with_div / amount - 1) * 100 if include_dividends else total_return_no_div
        cagr_with_div = ((current_value_with_div / amount) ** (1 / years_invested) - 1) * 100 if include_dividends and years_invested > 0 else cagr
        
        # Get volatility from analytics
        volatility = risk_metrics.get("volatility", 0) * 100
        
        # Find best and worst years using analytics data
        yearly_returns = []
        if len(prices) > 252:  # More than 1 year of data
            for year_start in range(0, len(prices) - 252, 252):
                year_end = min(year_start + 252, len(prices) - 1)
                if year_end > year_start:
                    year_return = (prices.iloc[year_end] / prices.iloc[year_start] - 1) * 100
                    yearly_returns.append({
                        "period": f"Year_{len(yearly_returns)+1}",
                        "return": round(year_return, 2)
                    })
        
        result = {
            "symbol": symbol,
            "investment_scenario": "time_machine_calculator",
            "data_source": "mcp_financial_server",
            
            # Investment details
            "investment_date": investment_date,
            "investment_amount": amount,
            "include_dividends": include_dividends,
            "days_invested": days_invested,
            "years_invested": round(years_invested, 2),
            
            # Price information
            "initial_price": round(initial_price, 2),
            "current_price": round(current_price, 2),
            "initial_shares": round(initial_shares, 4),
            "current_shares": round(initial_shares + dividend_shares, 4) if include_dividends else round(initial_shares, 4),
            
            # Performance metrics
            "current_value": round(current_value_with_div, 2),
            "total_return": round(total_return_with_div, 2),
            "annualized_return": round(cagr_with_div, 2),
            "total_dividends": round(total_dividends, 2) if include_dividends else 0,
            "dividend_shares": round(dividend_shares, 4) if include_dividends else 0,
            
            # Risk metrics
            "volatility": round(volatility, 2),
            
            # Performance breakdown
            "performance_breakdown": {
                "capital_appreciation": round(total_return_no_div, 2),
                "dividend_contribution": round(total_return_with_div - total_return_no_div, 2) if include_dividends else 0,
                "total_performance": round(total_return_with_div, 2)
            },
            
            # Historical context
            "yearly_performance": yearly_returns[:10],  # Show up to 10 years
            
            # What-if scenarios
            "alternative_scenarios": {
                "without_dividends": {
                    "value": round(current_value_no_div, 2),
                    "return": round(total_return_no_div, 2),
                    "cagr": round(cagr, 2)
                },
                "lump_sum_today": {
                    "description": f"If you invested ${amount} today instead",
                    "shares": round(amount / current_price, 4),
                    "note": "Future performance unknown"
                }
            },
            
            "last_updated": datetime.now().isoformat(),
            "financial_functions_used": ["alpaca_market_stocks_bars", "eodhd_dividends"],
            "analytics_functions_used": ["calculate_returns_metrics", "calculate_risk_metrics", "validate_price_data", "prices_to_returns"]
        }
        
        return standardize_output(result, "time_machine_calculator")
        
    except Exception as e:
        import traceback
        return {"success": False, "error": f"Time machine calculator failed: {str(e)}", "traceback": traceback.format_exc()}


def dca_simulator(symbol: str, monthly_amount: float, start_date: str, frequency: str = "monthly") -> Dict[str, Any]:
    """
    Simulate dollar-cost averaging strategy
    
    Uses REAL data from MCP financial server
    
    Args:
        symbol: Asset for DCA simulation
        monthly_amount: Monthly investment amount
        start_date: Start date for DCA (YYYY-MM-DD)
        frequency: Investment frequency (weekly, monthly, quarterly)
        
    Returns:
        Dict: DCA simulation results
    """
    try:
        symbol = symbol.upper()
        
        # Parse dates
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.now()
        
        if start_dt >= end_dt:
            return {"success": False, "error": "Start date must be in the past"}
        
        # Get historical data
        bars_result = alpaca_market_stocks_bars(
            symbols=symbol,
            timeframe="1Day",
            start=start_date,
            end=end_dt.strftime("%Y-%m-%d")
        )
        
        if "bars" not in bars_result or symbol not in bars_result["bars"]:
            return {"success": False, "error": f"Failed to get historical data for {symbol}"}
        
        bars = bars_result["bars"][symbol]
        if not bars:
            return {"success": False, "error": f"No data available for {symbol} from {start_date}"}
        
        # Create price lookup by date
        price_by_date = {bar["t"][:10]: bar["c"] for bar in bars}
        
        # Determine investment frequency
        freq_days = {"weekly": 7, "monthly": 30, "quarterly": 90}
        if frequency not in freq_days:
            return {"success": False, "error": "Frequency must be weekly, monthly, or quarterly"}
        
        days_between = freq_days[frequency]
        
        # Simulate DCA investments
        investments = []
        total_invested = 0
        total_shares = 0
        current_date = start_dt
        
        while current_date <= end_dt:
            # Find the closest trading day
            date_str = current_date.strftime("%Y-%m-%d")
            investment_price = None
            
            # Look for price within 5 days of investment date
            for offset in range(5):
                check_date = (current_date + timedelta(days=offset)).strftime("%Y-%m-%d")
                if check_date in price_by_date:
                    investment_price = price_by_date[check_date]
                    date_str = check_date
                    break
            
            if investment_price:
                shares_bought = monthly_amount / investment_price
                total_shares += shares_bought
                total_invested += monthly_amount
                
                investments.append({
                    "date": date_str,
                    "amount": monthly_amount,
                    "price": round(investment_price, 2),
                    "shares": round(shares_bought, 4),
                    "cumulative_shares": round(total_shares, 4),
                    "cumulative_invested": round(total_invested, 2)
                })
            
            current_date += timedelta(days=days_between)
        
        if not investments:
            return {"success": False, "error": "No valid investment dates found"}
        
        # Use analytics for performance calculation
        perf_metrics = {}
        risk_metrics = {}
        if investments:
            all_prices = [price_by_date[inv["date"]] for inv in investments if inv["date"] in price_by_date]
            if all_prices:
                prices_series = validate_price_data(all_prices + [bars[-1]["c"]])
                returns_series = prices_to_returns(prices_series)
                perf_metrics = calculate_returns_metrics(returns_series)
                risk_metrics = calculate_risk_metrics(returns_series)
        
        # Calculate current value and performance using analytics
        current_price = bars[-1]["c"]
        current_value = total_shares * current_price
        total_return = (current_value / total_invested - 1) * 100
        
        # Calculate average cost basis
        avg_cost_basis = total_invested / total_shares if total_shares > 0 else 0
        
        # Calculate time period
        days_invested = (end_dt - start_dt).days
        years_invested = days_invested / 365.25
        
        # Use analytics metrics if available, otherwise calculate manually
        cagr = perf_metrics.get("annual_return", ((current_value / total_invested) ** (1 / years_invested) - 1)) * 100 if years_invested > 0 else 0
        
        # Compare to lump sum investment
        lump_sum_amount = total_invested
        if investments:
            first_price = investments[0]["price"]
            lump_sum_shares = lump_sum_amount / first_price
            lump_sum_value = lump_sum_shares * current_price
            lump_sum_return = (lump_sum_value / lump_sum_amount - 1) * 100
            dca_vs_lump_sum = total_return - lump_sum_return
        else:
            lump_sum_return = 0
            dca_vs_lump_sum = 0
        
        # Calculate volatility of cost basis using analytics
        investment_prices = [inv["price"] for inv in investments]
        if investment_prices:
            price_series = validate_price_data(investment_prices)
            price_returns = prices_to_returns(price_series)
            price_risk_metrics = calculate_risk_metrics(price_returns)
            price_volatility = price_risk_metrics.get("volatility", 0) * 100
        else:
            price_volatility = 0
        
        result = {
            "symbol": symbol,
            "strategy": "dollar_cost_averaging",
            "data_source": "mcp_financial_server",
            
            # DCA parameters
            "start_date": start_date,
            "end_date": end_dt.strftime("%Y-%m-%d"),
            "frequency": frequency,
            "amount_per_investment": monthly_amount,
            "total_investments": len(investments),
            "days_invested": days_invested,
            "years_invested": round(years_invested, 2),
            
            # Investment summary
            "total_invested": round(total_invested, 2),
            "current_value": round(current_value, 2),
            "total_shares": round(total_shares, 4),
            "average_cost_basis": round(avg_cost_basis, 2),
            "current_price": round(current_price, 2),
            
            # Performance metrics
            "total_return": round(total_return, 2),
            "annualized_return": round(cagr, 2),
            "profit_loss": round(current_value - total_invested, 2),
            
            # DCA specific metrics
            "cost_basis_volatility": round(price_volatility, 2),
            "highest_purchase_price": round(max(investment_prices), 2) if investment_prices else 0,
            "lowest_purchase_price": round(min(investment_prices), 2) if investment_prices else 0,
            "price_range_captured": round((max(investment_prices) - min(investment_prices)) / min(investment_prices) * 100, 2) if investment_prices else 0,
            
            # Comparison analysis
            "vs_lump_sum": {
                "lump_sum_value": round(lump_sum_value, 2) if investments else 0,
                "lump_sum_return": round(lump_sum_return, 2),
                "dca_advantage": round(dca_vs_lump_sum, 2),
                "better_strategy": "DCA" if dca_vs_lump_sum > 0 else "Lump Sum"
            },
            
            # Investment history (show last 10)
            "recent_investments": investments[-10:],
            
            # Analysis insights
            "dca_effectiveness": {
                "smoothed_volatility": price_volatility < 20,
                "consistent_accumulation": len(investments) >= years_invested * 12 * 0.8,  # 80% of expected investments
                "market_timing_avoided": True,
                "discipline_maintained": True
            },
            
            "last_updated": datetime.now().isoformat(),
            "financial_functions_used": ["alpaca_market_stocks_bars"],
            "analytics_functions_used": ["calculate_returns_metrics", "calculate_risk_metrics", "validate_price_data", "prices_to_returns"]
        }
        
        return standardize_output(result, "dca_simulator")
        
    except Exception as e:
        return {"success": False, "error": f"DCA simulation failed: {str(e)}"}


def crisis_investment_tool(symbol: str, crisis_period: str, investment_timing: str = "bottom") -> Dict[str, Any]:
    """
    Analyze returns from investing during market crashes
    
    Uses REAL data from MCP financial server
    
    Args:
        symbol: Asset to analyze
        crisis_period: Crisis period (2008_financial_crisis, 2020_covid_crash, 2022_tech_selloff, custom)
        investment_timing: When to invest (bottom, during_decline, early_recovery)
        
    Returns:
        Dict: Crisis investment analysis
    """
    try:
        symbol = symbol.upper()
        
        # Define crisis periods
        crisis_periods = {
            "2008_financial_crisis": {
                "start": "2008-01-01",
                "end": "2009-03-31",
                "peak_date": "2007-10-09",
                "bottom_date": "2009-03-09",
                "description": "Global Financial Crisis and Great Recession"
            },
            "2020_covid_crash": {
                "start": "2020-02-01", 
                "end": "2020-04-30",
                "peak_date": "2020-02-19",
                "bottom_date": "2020-03-23",
                "description": "COVID-19 Pandemic Market Crash"
            },
            "2022_tech_selloff": {
                "start": "2022-01-01",
                "end": "2022-10-31", 
                "peak_date": "2021-11-22",
                "bottom_date": "2022-10-13",
                "description": "2022 Technology Selloff"
            }
        }
        
        if crisis_period not in crisis_periods:
            return {"success": False, "error": f"Crisis period must be one of: {list(crisis_periods.keys())}"}
        
        crisis_info = crisis_periods[crisis_period]
        
        # Get extended historical data (2 years before and after)
        start_date = datetime.strptime(crisis_info["peak_date"], "%Y-%m-%d") - timedelta(days=730)
        end_date = datetime.now()
        
        bars_result = alpaca_market_stocks_bars(
            symbols=symbol,
            timeframe="1Day", 
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d")
        )
        
        if "bars" not in bars_result or symbol not in bars_result["bars"]:
            return {"success": False, "error": f"Failed to get historical data for {symbol}"}
        
        bars = bars_result["bars"][symbol]
        
        # Use analytics for price processing
        prices_list = [bar["c"] for bar in bars]
        prices = validate_price_data(prices_list)
        dates = [bar["t"][:10] for bar in bars]
        
        # Find crisis period indices
        peak_idx = None
        bottom_idx = None
        
        for i, date in enumerate(dates):
            if date == crisis_info["peak_date"]:
                peak_idx = i
            if date == crisis_info["bottom_date"]:
                bottom_idx = i
        
        # If exact dates not found, find closest dates
        if peak_idx is None:
            peak_date_dt = datetime.strptime(crisis_info["peak_date"], "%Y-%m-%d")
            peak_idx = min(range(len(dates)), 
                          key=lambda i: abs((datetime.strptime(dates[i], "%Y-%m-%d") - peak_date_dt).days))
        
        if bottom_idx is None:
            bottom_date_dt = datetime.strptime(crisis_info["bottom_date"], "%Y-%m-%d")
            bottom_idx = min(range(len(dates)),
                            key=lambda i: abs((datetime.strptime(dates[i], "%Y-%m-%d") - bottom_date_dt).days))
        
        # Determine investment timing
        if investment_timing == "bottom":
            investment_idx = bottom_idx
        elif investment_timing == "during_decline":
            investment_idx = (peak_idx + bottom_idx) // 2
        elif investment_timing == "early_recovery":
            investment_idx = min(bottom_idx + 30, len(prices) - 1)  # 30 days after bottom
        else:
            return {"success": False, "error": "investment_timing must be: bottom, during_decline, or early_recovery"}
        
        investment_price = prices.iloc[investment_idx]
        investment_date = dates[investment_idx]
        current_price = prices.iloc[-1]
        
        # Use analytics for performance metrics
        peak_price = prices.iloc[peak_idx]
        bottom_price = prices.iloc[bottom_idx]
        
        crisis_decline = (bottom_price / peak_price - 1) * 100
        investment_to_current = (current_price / investment_price - 1) * 100
        
        # Calculate analytics metrics for post-investment period
        post_investment_prices = prices.iloc[investment_idx:]
        if len(post_investment_prices) > 1:
            post_investment_returns = prices_to_returns(post_investment_prices)
            post_perf_metrics = calculate_returns_metrics(post_investment_returns)
            post_risk_metrics = calculate_risk_metrics(post_investment_returns)
            cagr = post_perf_metrics.get("annual_return", 0) * 100
        else:
            cagr = 0
            post_risk_metrics = {}
        
        # Calculate time periods
        crisis_duration = bottom_idx - peak_idx
        recovery_to_peak = None
        for i in range(bottom_idx, len(prices)):
            if prices.iloc[i] >= peak_price:
                recovery_to_peak = i - bottom_idx
                break
        
        days_since_investment = len(prices) - 1 - investment_idx
        years_since_investment = days_since_investment / 365.25
        
        # Calculate maximum subsequent drawdown using analytics
        if len(post_investment_prices) > 1:
            drawdown_analysis = calculate_drawdown_analysis(post_investment_returns)
            subsequent_drawdown = drawdown_analysis.get("max_drawdown", 0) * 100
            volatility_after = post_risk_metrics.get("volatility", 0) * 100
        else:
            subsequent_drawdown = 0
            volatility_after = 0
        
        result = {
            "symbol": symbol,
            "analysis_type": "crisis_investment_analyzer",
            "data_source": "mcp_financial_server",
            
            # Crisis information
            "crisis_period": crisis_period,
            "crisis_description": crisis_info["description"],
            "investment_timing": investment_timing,
            
            # Key dates and prices
            "peak_date": crisis_info["peak_date"],
            "peak_price": round(peak_price, 2),
            "bottom_date": crisis_info["bottom_date"], 
            "bottom_price": round(bottom_price, 2),
            "investment_date": investment_date,
            "investment_price": round(investment_price, 2),
            "current_price": round(current_price, 2),
            
            # Crisis metrics
            "crisis_decline": round(crisis_decline, 2),
            "crisis_duration_days": crisis_duration,
            "recovery_to_peak_days": recovery_to_peak,
            
            # Investment performance
            "total_return": round(investment_to_current, 2),
            "annualized_return": round(cagr, 2),
            "days_since_investment": days_since_investment,
            "years_since_investment": round(years_since_investment, 2),
            
            # Risk analysis using analytics
            "max_subsequent_drawdown": round(subsequent_drawdown, 2),
            "volatility_after_investment": round(volatility_after, 2),
            
            # Timing analysis
            "timing_quality": {
                "distance_from_bottom": investment_idx - bottom_idx,
                "price_vs_bottom": round((investment_price / bottom_price - 1) * 100, 2),
                "price_vs_peak": round((investment_price / peak_price - 1) * 100, 2),
                "timing_score": "Excellent" if abs(investment_idx - bottom_idx) <= 5 else
                              "Good" if abs(investment_idx - bottom_idx) <= 15 else
                              "Fair" if abs(investment_idx - bottom_idx) <= 30 else
                              "Poor"
            },
            
            # Comparison scenarios
            "alternative_scenarios": {
                "if_bought_at_peak": {
                    "return": round((current_price / peak_price - 1) * 100, 2),
                    "description": "Return if invested at market peak"
                },
                "if_bought_at_bottom": {
                    "return": round((current_price / bottom_price - 1) * 100, 2),
                    "description": "Return if invested at exact bottom"
                }
            },
            
            # Lessons learned
            "lessons_learned": [
                f"Crisis declined {abs(crisis_decline):.1f}% over {crisis_duration} days",
                f"Recovery to previous peak took {recovery_to_peak} days" if recovery_to_peak else "Still below previous peak",
                f"Investing during crisis generated {investment_to_current:.1f}% return" if investment_to_current > 0 else f"Investment is down {abs(investment_to_current):.1f}%",
                "Crisis periods often present excellent long-term opportunities",
                "Patience and conviction required for crisis investing"
            ],
            
            "last_updated": datetime.now().isoformat(),
            "financial_functions_used": ["alpaca_market_stocks_bars"],
            "analytics_functions_used": ["calculate_returns_metrics", "calculate_risk_metrics", "calculate_drawdown_analysis", "validate_price_data", "prices_to_returns"]
        }
        
        return standardize_output(result, "crisis_investment_tool")
        
    except Exception as e:
        return {"success": False, "error": f"Crisis investment analysis failed: {str(e)}"}


def perfect_timing_tool(symbol: str, years: int, timing_frequency: str = "annual") -> Dict[str, Any]:
    """
    Calculate returns from perfect buy low/sell high timing
    
    Uses REAL data from MCP financial server
    
    Args:
        symbol: Asset for timing analysis
        years: Years to analyze
        timing_frequency: How often to time entries/exits (annual, quarterly, monthly)
        
    Returns:
        Dict: Perfect timing analysis
    """
    try:
        symbol = symbol.upper()
        
        if timing_frequency not in ["annual", "quarterly", "monthly"]:
            return {"success": False, "error": "timing_frequency must be: annual, quarterly, or monthly"}
        
        # Get historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365 + 30)
        
        bars_result = alpaca_market_stocks_bars(
            symbols=symbol,
            timeframe="1Day",
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d")
        )
        
        if "bars" not in bars_result or symbol not in bars_result["bars"]:
            return {"success": False, "error": f"Failed to get historical data for {symbol}"}
        
        bars = bars_result["bars"][symbol]
        
        # Use analytics for price processing
        prices_list = [bar["c"] for bar in bars]
        prices = validate_price_data(prices_list)
        dates = [bar["t"][:10] for bar in bars]
        
        if len(prices) < 100:
            return {"success": False, "error": "Insufficient data for analysis"}
        
        # Define period lengths
        period_days = {"annual": 252, "quarterly": 63, "monthly": 21}
        period_length = period_days[timing_frequency]
        
        # Calculate perfect timing returns
        perfect_timing_value = 10000  # Starting value
        buy_hold_value = 10000
        timing_trades = []
        
        # Buy and hold baseline using analytics
        buy_hold_prices = prices.copy()
        buy_hold_returns = prices_to_returns(buy_hold_prices)
        buy_hold_perf = calculate_returns_metrics(buy_hold_returns)
        buy_hold_return = buy_hold_perf.get("total_return", 0) * 100
        
        # Also calculate manually for comparison
        buy_hold_shares = buy_hold_value / prices.iloc[0]
        buy_hold_final = buy_hold_shares * prices.iloc[-1]
        buy_hold_return_manual = (buy_hold_final / buy_hold_value - 1) * 100
        
        # Perfect timing simulation
        current_position = "cash"  # Start in cash
        shares_held = 0
        cash = perfect_timing_value
        
        i = 0
        while i < len(prices) - period_length:
            period_prices = prices.iloc[i:i + period_length]
            period_dates = dates[i:i + period_length]
            
            if len(period_prices) == 0:
                break
                
            period_low = period_prices.min()
            period_high = period_prices.max()
            
            # Find indices of min and max values
            period_prices_list = period_prices.tolist()
            low_idx = period_prices_list.index(period_low)
            high_idx = period_prices_list.index(period_high)
            
            # Perfect timing: buy at low, sell at high
            if current_position == "cash":
                # Buy at period low
                buy_price = period_low
                buy_date = period_dates[low_idx]
                shares_held = cash / buy_price
                cash = 0
                current_position = "invested"
                
                timing_trades.append({
                    "action": "BUY",
                    "date": buy_date,
                    "price": round(buy_price, 2),
                    "shares": round(shares_held, 4),
                    "value": round(shares_held * buy_price, 2)
                })
            
            if current_position == "invested" and high_idx > low_idx:
                # Sell at period high (if high comes after low)
                sell_price = period_high
                sell_date = period_dates[high_idx]
                cash = shares_held * sell_price
                shares_held = 0
                current_position = "cash"
                
                timing_trades.append({
                    "action": "SELL", 
                    "date": sell_date,
                    "price": round(sell_price, 2),
                    "value": round(cash, 2),
                    "period_return": round((sell_price / buy_price - 1) * 100, 2)
                })
            
            i += period_length
        
        # Final position value
        if current_position == "invested":
            final_value = shares_held * prices.iloc[-1]
        else:
            final_value = cash
        
        perfect_timing_return = (final_value / perfect_timing_value - 1) * 100
        timing_premium = perfect_timing_return - buy_hold_return
        
        # Calculate required accuracy
        total_trades = len([t for t in timing_trades if t["action"] == "BUY"])
        successful_trades = len([t for t in timing_trades if t["action"] == "SELL" and t.get("period_return", 0) > 0])
        success_rate = (successful_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Calculate realistic scenario (80% timing accuracy)
        realistic_return = buy_hold_return + (timing_premium * 0.2)  # Assume only 20% of perfect timing captured
        
        result = {
            "symbol": symbol,
            "analysis_type": "perfect_timing_analyzer",
            "data_source": "mcp_financial_server",
            
            # Analysis parameters
            "analysis_period_years": years,
            "timing_frequency": timing_frequency,
            "total_periods": len(prices) // period_length,
            
            # Performance comparison
            "perfect_timing_return": round(perfect_timing_return, 2),
            "buy_hold_return": round(buy_hold_return, 2),
            "timing_premium": round(timing_premium, 2),
            "timing_advantage": f"{timing_premium:.1f} percentage points",
            
            # Timing analysis
            "total_trades": total_trades,
            "successful_periods": successful_trades,
            "required_accuracy": round(success_rate, 1),
            "trades_per_year": round(total_trades / years, 1),
            
            # Realistic scenarios
            "realistic_scenarios": {
                "80_percent_accuracy": {
                    "return": round(buy_hold_return + (timing_premium * 0.8), 2),
                    "description": "If you could time 80% of decisions perfectly"
                },
                "50_percent_accuracy": {
                    "return": round(buy_hold_return + (timing_premium * 0.5), 2),
                    "description": "If you could time 50% of decisions perfectly"
                },
                "20_percent_accuracy": {
                    "return": round(realistic_return, 2),
                    "description": "More realistic scenario with occasional good timing"
                }
            },
            
            # Market timing difficulty
            "timing_difficulty_analysis": {
                "timing_window": f"{period_length} days per decision",
                "decisions_required": total_trades * 2,  # Buy and sell decisions
                "perfect_decisions_needed": "100%",
                "margin_for_error": "0%",
                "realistic_achievement": "Nearly impossible"
            },
            
            # Key insights
            "key_insights": [
                f"Perfect timing would generate {timing_premium:.1f}% extra return",
                f"Requires {total_trades * 2} perfect decisions over {years} years",
                f"Buy-and-hold achieved {buy_hold_return:.1f}% return with zero timing decisions",
                "Perfect timing is theoretically possible but practically impossible",
                "Time in market typically beats timing the market"
            ],
            
            # Sample timing trades (last 5)
            "sample_trades": timing_trades[-10:] if timing_trades else [],
            
            "last_updated": datetime.now().isoformat(),
            "financial_functions_used": ["alpaca_market_stocks_bars"],
            "analytics_functions_used": ["calculate_returns_metrics", "validate_price_data", "prices_to_returns"]
        }
        
        return standardize_output(result, "perfect_timing_tool")
        
    except Exception as e:
        return {"success": False, "error": f"Perfect timing analysis failed: {str(e)}"}


# Registry of Tier 3 tools using REAL data
TIER_3_TOOLS = {
    'time_machine_calculator': time_machine_calculator,
    'dca_simulator': dca_simulator,
    'crisis_investment_tool': crisis_investment_tool,
    'perfect_timing_tool': perfect_timing_tool
}