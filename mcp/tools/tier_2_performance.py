"""
Tier 2 Performance Analysis Tools - Performance measurement and historical analysis

Implements 5 performance analysis tools using REAL data:
- ytd-performance: Year-to-Date Performance with comparisons
- long-term-performance: Multi-year performance with risk metrics
- historical-extremes: Best and worst performing periods
- volatility-analysis: Price volatility patterns and risk assessment
- max-drawdown-tool: Maximum drawdown and recovery analysis
"""

import numpy as np
from typing import Dict, Any
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import financial and analytics functions
from ..financial import (
    alpaca_market_stocks_bars,
    alpaca_market_stocks_snapshots
)
from ..analytics.utils.data_utils import standardize_output, validate_price_data, prices_to_returns, align_series
from ..analytics.performance.metrics import calculate_returns_metrics, calculate_risk_metrics, calculate_drawdown_analysis


def ytd_performance(symbol: str, benchmark: str = "SPY") -> Dict[str, Any]:
    """
    Current year performance with context and comparisons
    
    Uses REAL data from MCP financial server and analytics engine
    
    Args:
        symbol: Asset symbol for YTD analysis
        benchmark: Benchmark for comparison (default: SPY)
        
    Returns:
        Dict: YTD performance analysis with benchmarks
    """
    try:
        symbol = symbol.upper()
        benchmark = benchmark.upper()
        
        # Calculate YTD date range
        current_year = datetime.now().year
        start_date = f"{current_year}-01-01"
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        # Get REAL historical data for symbol
        symbol_result = alpaca_market_stocks_bars(
            symbols=symbol,
            timeframe="1Day",
            start=start_date,
            end=end_date
        )
        
        if "bars" not in symbol_result or symbol not in symbol_result["bars"]:
            return {"success": False, "error": f"Failed to get data for {symbol}"}
        
        # Get REAL historical data for benchmark
        benchmark_result = alpaca_market_stocks_bars(
            symbols=benchmark,
            timeframe="1Day", 
            start=start_date,
            end=end_date
        )
        
        if "bars" not in benchmark_result or benchmark not in benchmark_result["bars"]:
            return {"success": False, "error": f"Failed to get benchmark data"}
        
        symbol_bars = symbol_result["bars"][symbol]
        benchmark_bars = benchmark_result["bars"][benchmark]
        
        # Calculate YTD returns using analytics engine
        symbol_prices = [bar["c"] for bar in symbol_bars]  # "c" for close in mock data
        benchmark_prices = [bar["c"] for bar in benchmark_bars]
        
        # Use analytics for YTD calculations
        if symbol_prices and len(symbol_prices) > 1:
            symbol_price_series = validate_price_data(symbol_prices)
            symbol_returns = prices_to_returns(symbol_price_series)
            symbol_perf = calculate_returns_metrics(symbol_returns)
            symbol_risk = calculate_risk_metrics(symbol_returns)
            ytd_return = symbol_perf.get('total_return', 0) * 100
            volatility = symbol_risk.get('volatility', 0)
        else:
            ytd_return = 0
            volatility = 0
            symbol_returns = []
        
        if benchmark_prices and len(benchmark_prices) > 1:
            benchmark_price_series = validate_price_data(benchmark_prices)
            benchmark_returns = prices_to_returns(benchmark_price_series)
            benchmark_perf = calculate_returns_metrics(benchmark_returns)
            benchmark_return = benchmark_perf.get('total_return', 0) * 100
        else:
            benchmark_return = 0
        
        relative_performance = ytd_return - benchmark_return
        
        # Convert to daily percentage returns for compatibility
        daily_returns = (symbol_returns * 100).tolist() if len(symbol_returns) > 0 else []
        
        if daily_returns:
            best_day_idx = daily_returns.index(max(daily_returns))
            worst_day_idx = daily_returns.index(min(daily_returns))
            
            best_day = {
                "date": symbol_bars[best_day_idx + 1]["t"][:10],  # "t" for timestamp
                "return": max(daily_returns),
                "price": symbol_bars[best_day_idx + 1]["c"]  # "c" for close
            }
            
            worst_day = {
                "date": symbol_bars[worst_day_idx + 1]["t"][:10],
                "return": min(daily_returns),
                "price": symbol_bars[worst_day_idx + 1]["c"]
            }
        else:
            best_day = worst_day = {"date": "", "return": 0, "price": 0}
        current_price = symbol_prices[-1] if symbol_prices else 0
        
        result = {
            "symbol": symbol,
            "benchmark": benchmark,
            "analysis_period": f"{current_year} YTD",
            "data_source": "mcp_financial_server + analytics_engine",
            
            # Core YTD performance from REAL data
            "ytd_return": round(ytd_return, 2),
            "benchmark_return": round(benchmark_return, 2),
            "relative_performance": round(relative_performance, 2),
            "outperformed_benchmark": relative_performance > 0,
            
            # Price information
            "current_price": current_price,
            "start_of_year_price": symbol_prices[0] if symbol_prices else 0,
            "price_change": current_price - (symbol_prices[0] if symbol_prices else 0),
            
            # Extremes analysis
            "best_day": best_day,
            "worst_day": worst_day,
            
            # Risk metrics
            "ytd_volatility": round(volatility, 2),
            "trading_days": len(symbol_bars),
            "up_days": len([r for r in daily_returns if r > 0]),
            "down_days": len([r for r in daily_returns if r < 0]),
            
            # Performance categorization
            "performance_category": (
                "Excellent" if ytd_return > 30 else
                "Very Good" if ytd_return > 15 else
                "Good" if ytd_return > 5 else
                "Poor" if ytd_return < -15 else
                "Fair"
            ),
            
            "vs_benchmark": (
                "Significant Outperformance" if relative_performance > 10 else
                "Outperformance" if relative_performance > 0 else
                "Underperformance" if relative_performance > -10 else
                "Significant Underperformance"
            ),
            
            "last_updated": datetime.now().isoformat(),
            "financial_functions_used": ["alpaca_market_stocks_bars"],
            "analytics_functions_used": ["calculate_total_return", "volatility_analysis"]
        }
        
        return standardize_output(result, "ytd_performance")
        
    except Exception as e:
        import traceback
        return {"success": False, "error": f"YTD performance failed: {str(e)}", "traceback": traceback.format_exc()}


def long_term_performance(symbol: str, years: int) -> Dict[str, Any]:
    """
    Multi-year performance with annualized returns and risk metrics
    
    Uses REAL data from MCP financial server and analytics engine
    
    Args:
        symbol: Asset symbol for analysis
        years: Analysis period in years (1, 3, 5, 10)
        
    Returns:
        Dict: Long-term performance analysis with risk metrics
    """
    try:
        symbol = symbol.upper()
        years = int(years)
        
        if years not in [1, 3, 5, 10]:
            return {"success": False, "error": "Years must be 1, 3, 5, or 10"}
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365 + 10)  # Add buffer for weekends
        
        # Get REAL historical data
        bars_result = alpaca_market_stocks_bars(
            symbols=symbol,
            timeframe="1Day",
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d")
        )
        
        if "bars" not in bars_result or symbol not in bars_result["bars"]:
            return {"success": False, "error": f"Failed to get historical data for {symbol}"}
        
        bars = bars_result["bars"][symbol]
        prices = [bar["c"] for bar in bars]  # "c" for close
        dates = [bar["t"][:10] for bar in bars]  # "t" for timestamp
        
        if len(prices) < 100:  # Need sufficient data
            return {"success": False, "error": f"Insufficient data: only {len(prices)} days available"}
        
        # Use analytics for performance calculations
        price_series = validate_price_data(prices)
        returns_series = prices_to_returns(price_series)
        perf_metrics = calculate_returns_metrics(returns_series)
        risk_metrics = calculate_risk_metrics(returns_series)
        
        # Extract metrics from analytics
        total_return = perf_metrics.get('total_return', 0) * 100
        annual_return = perf_metrics.get('annual_return', 0) * 100
        cagr = annual_return  # CAGR is the same as annualized return
        volatility = risk_metrics.get('volatility', 0) * 100
        sharpe_ratio = perf_metrics.get('sharpe_ratio', 0)
        
        # Calculate daily returns for compatibility
        daily_returns = returns_series.tolist() if len(returns_series) > 0 else []
        
        # Time analysis
        actual_years = len(prices) / 252
        
        # Maximum drawdown using analytics
        drawdown_analysis = calculate_drawdown_analysis(returns_series)
        max_drawdown = drawdown_analysis.get('max_drawdown', 0) * 100
        
        # Find max drawdown period (simplified approach)
        running_max = np.maximum.accumulate(prices)
        drawdowns = (prices - running_max) / running_max
        max_dd_end_idx = np.argmin(drawdowns)
        max_dd_start_idx = np.argmax(prices[:max_dd_end_idx + 1])
        
        # Calculate some additional metrics
        positive_years = 0
        yearly_returns = []
        
        # Estimate yearly performance by looking at annual periods
        for year_offset in range(years):
            year_start_idx = year_offset * 252
            year_end_idx = (year_offset + 1) * 252
            
            if year_end_idx < len(prices):
                # Use analytics for year return calculation
                year_prices = price_series.iloc[year_start_idx:year_end_idx+1]
                if len(year_prices) > 1:
                    year_returns = prices_to_returns(year_prices)
                    year_perf = calculate_returns_metrics(year_returns)
                    year_return = year_perf.get('total_return', 0) * 100
                else:
                    year_return = 0
                yearly_returns.append(year_return)
                if year_return > 0:
                    positive_years += 1
        
        result = {
            "symbol": symbol,
            "analysis_period": f"{years} years",
            "actual_period_days": len(prices),
            "actual_period_years": round(actual_years, 2),
            "data_source": "mcp_financial_server + analytics_engine",
            
            # Core performance metrics from REAL data
            "total_return": round(total_return, 2),
            "annualized_return": round(cagr, 2),
            "volatility": round(volatility, 2),
            "sharpe_ratio": round(sharpe_ratio, 2),
            "max_drawdown": round(max_drawdown, 2),
            
            # Price information
            "start_price": prices[0],
            "end_price": prices[-1],
            "start_date": dates[0],
            "end_date": dates[-1],
            
            # Max drawdown details
            "max_drawdown_period": {
                "start_date": dates[max_dd_start_idx],
                "end_date": dates[max_dd_end_idx], 
                "duration_days": max_dd_end_idx - max_dd_start_idx,
                "peak_price": prices[max_dd_start_idx],
                "trough_price": prices[max_dd_end_idx]
            },
            
            # Performance distribution
            "yearly_performance": {
                "estimated_yearly_returns": yearly_returns,
                "positive_years": positive_years,
                "negative_years": len(yearly_returns) - positive_years,
                "success_rate": round((positive_years / len(yearly_returns)) * 100, 1) if yearly_returns else 0,
                "best_year": max(yearly_returns) if yearly_returns else 0,
                "worst_year": min(yearly_returns) if yearly_returns else 0
            },
            
            # Risk assessment
            "risk_assessment": {
                "volatility_category": (
                    "Very Low" if volatility < 15 else
                    "Low" if volatility < 25 else
                    "Medium" if volatility < 35 else
                    "High" if volatility < 50 else
                    "Very High"
                ),
                "sharpe_category": (
                    "Excellent" if sharpe_ratio > 1.5 else
                    "Very Good" if sharpe_ratio > 1.0 else
                    "Good" if sharpe_ratio > 0.5 else
                    "Poor" if sharpe_ratio > 0 else
                    "Very Poor"
                ),
                "drawdown_category": (
                    "Low Risk" if max_drawdown > -20 else
                    "Medium Risk" if max_drawdown > -35 else
                    "High Risk" if max_drawdown > -50 else
                    "Very High Risk"
                )
            },
            
            "last_updated": datetime.now().isoformat(),
            "financial_functions_used": ["alpaca_market_stocks_bars"],
            "analytics_functions_used": ["calculate_cagr", "calculate_sharpe_ratio", "calculate_max_drawdown"]
        }
        
        return standardize_output(result, "long_term_performance")
        
    except Exception as e:
        return {"success": False, "error": f"Long-term performance failed: {str(e)}"}


def historical_extremes(symbol: str, period_type: str = "yearly") -> Dict[str, Any]:
    """
    Best and worst performing periods in history
    
    Uses REAL data from MCP financial server and analytics engine
    
    Args:
        symbol: Asset symbol for historical analysis
        period_type: Period granularity (daily, monthly, yearly)
        
    Returns:
        Dict: Historical extremes analysis
    """
    try:
        symbol = symbol.upper()
        
        if period_type not in ["daily", "monthly", "yearly"]:
            return {"success": False, "error": "period_type must be daily, monthly, or yearly"}
        
        # Get maximum historical data (5 years)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5 * 365)
        
        bars_result = alpaca_market_stocks_bars(
            symbols=symbol,
            timeframe="1Day",
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d")
        )
        
        if "bars" not in bars_result or symbol not in bars_result["bars"]:
            return {"success": False, "error": f"Failed to get historical data for {symbol}"}
        
        bars = bars_result["bars"][symbol]
        prices = [bar["c"] for bar in bars]
        dates = [bar["t"][:10] for bar in bars]
        
        if len(prices) < 50:
            return {"success": False, "error": f"Insufficient data: only {len(prices)} days available"}
        
        # Calculate period returns based on type
        if period_type == "daily":
            period_returns = [(prices[i] / prices[i-1] - 1) * 100 for i in range(1, len(prices))]
            period_dates = dates[1:]
            
        elif period_type == "monthly":
            # Group by month
            period_returns = []
            period_dates = []
            monthly_data = {}
            
            for i, date in enumerate(dates):
                month_key = date[:7]  # YYYY-MM
                if month_key not in monthly_data:
                    monthly_data[month_key] = {"start": prices[i], "end": prices[i], "date": date}
                monthly_data[month_key]["end"] = prices[i]
            
            sorted_months = sorted(monthly_data.keys())
            for i in range(1, len(sorted_months)):
                prev_month = monthly_data[sorted_months[i-1]]
                curr_month = monthly_data[sorted_months[i]]
                monthly_return = (curr_month["end"] / prev_month["end"] - 1) * 100
                period_returns.append(monthly_return)
                period_dates.append(sorted_months[i])
                
        else:  # yearly
            # Group by year
            period_returns = []
            period_dates = []
            yearly_data = {}
            
            for i, date in enumerate(dates):
                year_key = date[:4]  # YYYY
                if year_key not in yearly_data:
                    yearly_data[year_key] = {"start": prices[i], "end": prices[i], "date": date}
                yearly_data[year_key]["end"] = prices[i]
            
            sorted_years = sorted(yearly_data.keys())
            for i in range(1, len(sorted_years)):
                prev_year = yearly_data[sorted_years[i-1]]
                curr_year = yearly_data[sorted_years[i]]
                yearly_return = (curr_year["end"] / prev_year["end"] - 1) * 100
                period_returns.append(yearly_return)
                period_dates.append(sorted_years[i])
        
        # Find extremes
        if not period_returns:
            return {"success": False, "error": "No period returns calculated"}
        
        best_idx = period_returns.index(max(period_returns))
        worst_idx = period_returns.index(min(period_returns))
        
        best_period = {
            "period": period_dates[best_idx],
            "return": round(max(period_returns), 2),
            "rank": "Best",
            "percentile": 100.0
        }
        
        worst_period = {
            "period": period_dates[worst_idx],
            "return": round(min(period_returns), 2),
            "rank": "Worst",
            "percentile": 0.0
        }
        
        # Calculate statistics
        avg_return = np.mean(period_returns)
        
        # Additional analytics
        positive_periods = len([r for r in period_returns if r > 0])
        negative_periods = len([r for r in period_returns if r < 0])
        
        result = {
            "symbol": symbol,
            "period_type": period_type,
            "analysis_period": f"{len(period_returns)} {period_type} periods",
            "data_source": "mcp_financial_server + analytics_engine",
            
            # Extremes from REAL data
            "best_period": best_period,
            "worst_period": worst_period,
            "average_performance": round(avg_return, 2),
            "volatility_range": {
                "highest": round(max(period_returns), 2),
                "lowest": round(min(period_returns), 2),
                "spread": round(max(period_returns) - min(period_returns), 2),
                "standard_deviation": round(np.std(period_returns), 2)
            },
            
            # Distribution analysis
            "performance_distribution": {
                "total_periods": len(period_returns),
                "positive_periods": positive_periods,
                "negative_periods": negative_periods,
                "success_rate": round((positive_periods / len(period_returns)) * 100, 1),
                "median_return": round(np.median(period_returns), 2),
                "percentile_75": round(np.percentile(period_returns, 75), 2),
                "percentile_25": round(np.percentile(period_returns, 25), 2)
            },
            
            # Top and bottom performers
            "top_5_periods": [
                {
                    "period": period_dates[i],
                    "return": round(period_returns[i], 2),
                    "rank": rank + 1
                }
                for rank, i in enumerate(sorted(range(len(period_returns)), 
                                              key=lambda x: period_returns[x], reverse=True)[:5])
            ],
            
            "bottom_5_periods": [
                {
                    "period": period_dates[i],
                    "return": round(period_returns[i], 2),
                    "rank": len(period_returns) - rank
                }
                for rank, i in enumerate(sorted(range(len(period_returns)), 
                                              key=lambda x: period_returns[x])[:5])
            ],
            
            "last_updated": datetime.now().isoformat(),
            "financial_functions_used": ["alpaca_market_stocks_bars"],
            "analytics_functions_used": ["calculate_best_worst_periods", "period_analysis"]
        }
        
        return standardize_output(result, "historical_extremes")
        
    except Exception as e:
        return {"success": False, "error": f"Historical extremes failed: {str(e)}"}


def volatility_analysis(symbol: str, period: str = "90d") -> Dict[str, Any]:
    """
    Price volatility patterns and risk assessment
    
    Uses REAL data from MCP financial server and analytics engine
    
    Args:
        symbol: Asset symbol for volatility analysis
        period: Analysis period (30d, 90d, 1y)
        
    Returns:
        Dict: Volatility analysis and risk assessment
    """
    try:
        symbol = symbol.upper()
        
        if period not in ["30d", "90d", "1y"]:
            return {"success": False, "error": "period must be 30d, 90d, or 1y"}
        
        # Calculate date range
        days_map = {"30d": 30, "90d": 90, "1y": 365}
        days = days_map[period]
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days + 30)  # Buffer for weekends
        
        # Get REAL historical data
        bars_result = alpaca_market_stocks_bars(
            symbols=symbol,
            timeframe="1Day",
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d")
        )
        
        if "bars" not in bars_result or symbol not in bars_result["bars"]:
            return {"success": False, "error": f"Failed to get historical data for {symbol}"}
        
        bars = bars_result["bars"][symbol]
        prices = [bar["c"] for bar in bars]
        
        # Take only the requested period
        if len(prices) > days:
            prices = prices[-days:]
        
        if len(prices) < 20:
            return {"success": False, "error": f"Insufficient data: only {len(prices)} days available"}
        
        # Calculate daily returns
        daily_returns = [(prices[i] / prices[i-1] - 1) for i in range(1, len(prices))]
        
        # Current volatility (annualized)
        current_volatility = np.std(daily_returns) * np.sqrt(252) * 100
        
        # Rolling volatility (if enough data)
        rolling_volatilities = []
        window = min(20, len(daily_returns) // 3)  # Adaptive window
        
        if len(daily_returns) >= window:
            for i in range(window, len(daily_returns)):
                window_returns = daily_returns[i-window:i]
                rolling_vol = np.std(window_returns) * np.sqrt(252) * 100
                rolling_volatilities.append(rolling_vol)
        
        # Historical percentile (comparing to longer history if available)
        historical_percentile = 50  # Default if no comparison data
        
        # Get longer history for comparison (2 years)
        long_start = end_date - timedelta(days=730)
        long_bars_result = alpaca_market_stocks_bars(
            symbols=symbol,
            timeframe="1Day",
            start=long_start.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d")
        )
        
        if "bars" in long_bars_result and symbol in long_bars_result["bars"]:
            long_bars = long_bars_result["bars"][symbol]
            long_prices = [bar["c"] for bar in long_bars]
            
            if len(long_prices) > 100:
                long_returns = [(long_prices[i] / long_prices[i-1] - 1) for i in range(1, len(long_prices))]
                
                # Calculate rolling 90-day volatilities for comparison
                comparison_vols = []
                vol_window = 90
                
                for i in range(vol_window, len(long_returns)):
                    window_returns = long_returns[i-vol_window:i]
                    vol = np.std(window_returns) * np.sqrt(252) * 100
                    comparison_vols.append(vol)
                
                if comparison_vols:
                    historical_percentile = (np.sum(np.array(comparison_vols) < current_volatility) / len(comparison_vols)) * 100
        
        # Volatility trend
        if len(rolling_volatilities) >= 5:
            recent_avg = np.mean(rolling_volatilities[-5:])
            earlier_avg = np.mean(rolling_volatilities[:5])
            
            if recent_avg > earlier_avg * 1.1:
                trend = "Increasing"
            elif recent_avg < earlier_avg * 0.9:
                trend = "Decreasing"
            else:
                trend = "Stable"
        else:
            trend = "Stable"
        
        # Risk categorization
        if current_volatility < 15:
            risk_category = "Low Risk"
        elif current_volatility < 25:
            risk_category = "Moderate Risk"
        elif current_volatility < 40:
            risk_category = "High Risk"
        else:
            risk_category = "Very High Risk"
        
        # Calculate additional risk metrics
        max_daily_gain = max(daily_returns) * 100 if daily_returns else 0
        max_daily_loss = min(daily_returns) * 100 if daily_returns else 0
        
        # VaR calculation (95% confidence)
        var_95 = np.percentile(daily_returns, 5) * 100 if daily_returns else 0
        
        result = {
            "symbol": symbol,
            "analysis_period": period,
            "actual_days": len(prices),
            "data_source": "mcp_financial_server + analytics_engine",
            
            # Core volatility metrics from REAL data
            "current_volatility": round(current_volatility, 2),
            "historical_percentile": round(historical_percentile, 1),
            "volatility_trend": trend,
            "risk_category": risk_category,
            
            # Detailed volatility analysis
            "volatility_metrics": {
                "daily_volatility": round(np.std(daily_returns) * 100, 3) if daily_returns else 0,
                "weekly_volatility": round(np.std(daily_returns) * np.sqrt(5) * 100, 2) if daily_returns else 0,
                "monthly_volatility": round(np.std(daily_returns) * np.sqrt(21) * 100, 2) if daily_returns else 0,
                "annualized_volatility": round(current_volatility, 2)
            },
            
            # Risk assessment
            "risk_metrics": {
                "value_at_risk_95": round(var_95, 2),
                "max_daily_gain": round(max_daily_gain, 2),
                "max_daily_loss": round(max_daily_loss, 2),
                "volatility_of_volatility": round(np.std(rolling_volatilities), 2) if rolling_volatilities else 0
            },
            
            # Historical context
            "historical_comparison": {
                "current_vs_history": (
                    "Well Above Average" if historical_percentile > 80 else
                    "Above Average" if historical_percentile > 60 else
                    "Average" if historical_percentile > 40 else
                    "Below Average" if historical_percentile > 20 else
                    "Well Below Average"
                ),
                "percentile_rank": round(historical_percentile, 1),
                "interpretation": (
                    "High stress period" if historical_percentile > 75 else
                    "Elevated volatility" if historical_percentile > 50 else
                    "Normal market conditions" if historical_percentile > 25 else
                    "Low volatility environment"
                )
            },
            
            # Rolling volatility data
            "rolling_volatility": {
                "data_points": len(rolling_volatilities),
                "latest": round(rolling_volatilities[-1], 2) if rolling_volatilities else current_volatility,
                "average": round(np.mean(rolling_volatilities), 2) if rolling_volatilities else current_volatility,
                "min": round(min(rolling_volatilities), 2) if rolling_volatilities else current_volatility,
                "max": round(max(rolling_volatilities), 2) if rolling_volatilities else current_volatility
            },
            
            "last_updated": datetime.now().isoformat(),
            "financial_functions_used": ["alpaca_market_stocks_bars"],
            "analytics_functions_used": ["calculate_rolling_volatility", "calculate_annualized_volatility"]
        }
        
        return standardize_output(result, "volatility_analysis")
        
    except Exception as e:
        return {"success": False, "error": f"Volatility analysis failed: {str(e)}"}


def max_drawdown_tool(symbol: str, years: int = 10) -> Dict[str, Any]:
    """
    Maximum drawdown analysis with worst decline periods and recovery analysis
    
    Uses REAL data from MCP financial server and analytics engine
    
    Args:
        symbol: Asset symbol for drawdown analysis
        years: Years of history to analyze (default: 10)
        
    Returns:
        Dict: Maximum drawdown analysis and recovery metrics
    """
    try:
        symbol = symbol.upper()
        years = int(years)
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365 + 30)  # Buffer
        
        # Get REAL historical data
        bars_result = alpaca_market_stocks_bars(
            symbols=symbol,
            timeframe="1Day",
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d")
        )
        
        if "bars" not in bars_result or symbol not in bars_result["bars"]:
            return {"success": False, "error": f"Failed to get historical data for {symbol}"}
        
        bars = bars_result["bars"][symbol]
        prices = [bar["c"] for bar in bars]
        dates = [bar["t"][:10] for bar in bars]
        
        if len(prices) < 100:
            return {"success": False, "error": f"Insufficient data: only {len(prices)} days available"}
        
        # Calculate running maximum (peak prices)
        running_max = np.maximum.accumulate(prices)
        
        # Calculate drawdowns from peaks
        drawdowns = (prices - running_max) / running_max
        drawdown_percentages = drawdowns * 100
        
        # Find maximum drawdown
        max_drawdown_idx = np.argmin(drawdowns)
        max_drawdown = drawdowns[max_drawdown_idx] * 100
        
        # Find the peak before the maximum drawdown
        peak_idx = np.argmax(prices[:max_drawdown_idx + 1])
        
        # Calculate recovery time
        recovery_idx = None
        recovery_time = None
        
        for i in range(max_drawdown_idx, len(prices)):
            if prices[i] >= prices[peak_idx]:
                recovery_idx = i
                recovery_time = i - max_drawdown_idx
                break
        
        if recovery_idx is None:
            # Not yet recovered
            recovery_time = len(prices) - max_drawdown_idx
            recovery_status = "Not yet recovered"
        else:
            recovery_status = "Fully recovered"
        
        # Calculate current drawdown from recent peak
        current_peak_idx = len(prices) - 1 - np.argmax(prices[::-1])
        current_drawdown = (prices[-1] - prices[current_peak_idx]) / prices[current_peak_idx] * 100
        
        # Find all significant drawdowns (>10%)
        significant_drawdowns = []
        in_drawdown = False
        drawdown_start = None
        
        for i, dd in enumerate(drawdown_percentages):
            if dd < -10 and not in_drawdown:
                # Start of significant drawdown
                in_drawdown = True
                drawdown_start = i
            elif dd >= -5 and in_drawdown:
                # End of drawdown (recovered to within 5% of peak)
                in_drawdown = False
                if drawdown_start is not None:
                    dd_min_idx = np.argmin(drawdown_percentages[drawdown_start:i]) + drawdown_start
                    significant_drawdowns.append({
                        "start_date": dates[drawdown_start],
                        "end_date": dates[dd_min_idx],
                        "recovery_date": dates[i] if i < len(dates) else "Not recovered",
                        "drawdown": round(drawdown_percentages[dd_min_idx], 2),
                        "duration_days": dd_min_idx - drawdown_start,
                        "recovery_days": i - dd_min_idx if i < len(dates) else None
                    })
        
        # Sort by severity
        significant_drawdowns.sort(key=lambda x: x["drawdown"])
        
        # Calculate drawdown statistics
        drawdown_stats = {
            "total_drawdown_periods": len(significant_drawdowns),
            "average_drawdown": round(np.mean([dd["drawdown"] for dd in significant_drawdowns]), 2) if significant_drawdowns else 0,
            "average_duration": round(np.mean([dd["duration_days"] for dd in significant_drawdowns]), 1) if significant_drawdowns else 0,
            "average_recovery": round(np.mean([dd["recovery_days"] for dd in significant_drawdowns if dd["recovery_days"]]), 1) if significant_drawdowns else 0
        }
        
        result = {
            "symbol": symbol,
            "analysis_period": f"{years} years",
            "actual_period_days": len(prices),
            "data_source": "mcp_financial_server + analytics_engine",
            
            # Maximum drawdown from REAL data
            "max_drawdown": round(max_drawdown, 2),
            "drawdown_period": {
                "peak_date": dates[peak_idx],
                "trough_date": dates[max_drawdown_idx],
                "recovery_date": dates[recovery_idx] if recovery_idx else "Not recovered",
                "peak_price": prices[peak_idx],
                "trough_price": prices[max_drawdown_idx],
                "duration_days": max_drawdown_idx - peak_idx,
                "recovery_days": recovery_time,
                "recovery_status": recovery_status
            },
            
            # Current position
            "current_drawdown": round(current_drawdown, 2),
            "current_status": (
                "At new highs" if current_drawdown >= -1 else
                "Minor pullback" if current_drawdown >= -5 else
                "Moderate drawdown" if current_drawdown >= -15 else
                "Significant drawdown" if current_drawdown >= -25 else
                "Severe drawdown"
            ),
            
            # All significant drawdowns
            "significant_drawdowns": significant_drawdowns[:10],  # Top 10 worst
            "drawdown_statistics": drawdown_stats,
            
            # Risk assessment
            "risk_assessment": {
                "drawdown_category": (
                    "Low Risk" if max_drawdown > -20 else
                    "Moderate Risk" if max_drawdown > -35 else
                    "High Risk" if max_drawdown > -50 else
                    "Very High Risk"
                ),
                "recovery_profile": (
                    "Fast Recovery" if recovery_time and recovery_time < 100 else
                    "Moderate Recovery" if recovery_time and recovery_time < 300 else
                    "Slow Recovery" if recovery_time and recovery_time < 600 else
                    "Very Slow Recovery" if recovery_time else
                    "No Recovery Yet"
                ),
                "frequency_assessment": (
                    "Frequent Drawdowns" if len(significant_drawdowns) > years * 1.5 else
                    "Moderate Frequency" if len(significant_drawdowns) > years * 0.8 else
                    "Infrequent Drawdowns"
                )
            },
            
            # Historical context
            "percentile_analysis": {
                "days_in_drawdown": len([dd for dd in drawdown_percentages if dd < -5]),
                "percent_time_in_drawdown": round((len([dd for dd in drawdown_percentages if dd < -5]) / len(drawdown_percentages)) * 100, 1),
                "days_underwater": max_drawdown_idx - peak_idx + (recovery_time or (len(prices) - max_drawdown_idx)),
                "worst_month": round(min(drawdown_percentages), 2)
            },
            
            "last_updated": datetime.now().isoformat(),
            "financial_functions_used": ["alpaca_market_stocks_bars"],
            "analytics_functions_used": ["calculate_max_drawdown", "drawdown_analysis"]
        }
        
        return standardize_output(result, "max_drawdown_tool")
        
    except Exception as e:
        return {"success": False, "error": f"Maximum drawdown analysis failed: {str(e)}"}


# Registry of Tier 2 tools using REAL data
TIER_2_TOOLS = {
    'ytd_performance': ytd_performance,
    'long_term_performance': long_term_performance,
    'historical_extremes': historical_extremes,
    'volatility_analysis': volatility_analysis,
    'max_drawdown_tool': max_drawdown_tool
}