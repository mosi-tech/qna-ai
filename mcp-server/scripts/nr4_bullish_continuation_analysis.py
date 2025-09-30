#!/usr/bin/env python3
"""
Financial Analysis: Which symbols most often printed bullish continuation after NR4 days?
Generated with fast-track MCP validation - Parameterized Version
"""

import json
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# NOTE: call_mcp_function is PROVIDED by execution environment

def safe_mcp_call(function_name, params):
    """Call MCP function with fail-fast error handling and production debugging"""
    try:
        result = call_mcp_function(function_name, params)
        if result is None:
            raise Exception(f"MCP call {function_name} returned None - function may not be implemented in production environment")
        if isinstance(result, dict) and not result:
            raise Exception(f"MCP call {function_name} returned empty dict - check function parameters: {params}")
        return result
    except Exception as e:
        raise Exception(f"MCP call failed for {function_name} with params {params}: {e}")

def analyze_nr4_bullish_continuation(
    symbols: Optional[List[str]] = None,
    top_symbols: int = 50,
    analysis_period_days: int = 180,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    nr4_atr_multiplier: float = 0.5,
    bullish_continuation_threshold: float = 0.02,
    lookback_days: int = 4,
    atr_period: int = 14,
    min_occurrences: int = 3,
    max_results: int = 10,
    sort_by: str = "success_rate",
    timeframe: str = "1Day",
    exclude_symbols: Optional[List[str]] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    mock: bool = False
) -> Dict[str, Any]:
    """
    Analyze which symbols most often show bullish continuation after NR4 (Narrow Range 4) days
    
    Args:
        symbols: Explicit list of symbols to analyze (takes precedence over top_symbols)
        top_symbols: Number of most active symbols to fetch if symbols not provided
        analysis_period_days: Number of days of historical data (ignored if start_date/end_date provided)
        start_date: Explicit start date in YYYY-MM-DD format (overrides analysis_period_days)
        end_date: Explicit end date in YYYY-MM-DD format (defaults to current date)
        nr4_atr_multiplier: ATR multiplier to define narrow range (lower = more restrictive)
        bullish_continuation_threshold: Minimum price increase % to qualify as bullish continuation
        lookback_days: Number of days to look back for NR4 pattern (typically 4)
        atr_period: Period for ATR calculation (typically 14)
        min_occurrences: Minimum number of NR4 occurrences required for ranking
        max_results: Maximum number of top performers to return
        sort_by: Sort criteria ("success_rate", "occurrences", or "avg_continuation")
        timeframe: Data timeframe ("1Day", "1Hour", etc.)
        exclude_symbols: List of symbols to exclude from analysis
        min_price: Minimum stock price filter
        max_price: Maximum stock price filter
        mock: Whether running in mock/validation mode
        
    Returns:
        Dict containing analysis results with metadata
    """
    try:
        logging.info("🚀 Starting NR4 bullish continuation analysis")
        
        # Step 1: Determine symbols to analyze (comprehensive parameter handling)
        if symbols:
            # Use explicit symbols list (takes precedence)
            final_symbols = symbols.copy()
            logging.info(f"Using explicit symbols list: {final_symbols}")
        else:
            # Fetch most active symbols
            logging.info(f"Fetching top {top_symbols} most active symbols")
            actives_data = safe_mcp_call("alpaca_market_screener_most_actives", {"top": top_symbols})
            
            if not actives_data.get('most_actives'):
                raise Exception("No active symbols data received")
            
            final_symbols = [stock['symbol'] for stock in actives_data['most_actives']]
            logging.info(f"Using most active symbols: {final_symbols}")
        
        # Apply exclusions if provided
        if exclude_symbols:
            final_symbols = [s for s in final_symbols if s not in exclude_symbols]
            logging.info(f"After exclusions: {final_symbols}")
        
        if not final_symbols:
            raise Exception("No symbols to analyze after filtering")
        
        # Step 2: Calculate date range (comprehensive date parameter handling)
        if end_date is None:
            final_end_date = datetime.now().strftime('%Y-%m-%d')
        else:
            final_end_date = end_date
            
        if start_date is None:
            # Use analysis_period_days to calculate start date
            final_start_date = (datetime.now() - timedelta(days=analysis_period_days)).strftime('%Y-%m-%d')
        else:
            # Use explicit start date (takes precedence)
            final_start_date = start_date
        
        # Step 3: Get historical data for all symbols
        logging.info(f"Fetching historical data from {final_start_date} to {final_end_date}")
        bars_data = safe_mcp_call("alpaca_market_stocks_bars", {
            "symbols": final_symbols,
            "timeframe": timeframe,
            "start": final_start_date,
            "end": final_end_date
        })
        
        if not bars_data.get('bars'):
            raise Exception("No historical bars data received")
        
        symbol_results = []
        
        # Step 4: Analyze each symbol for NR4 patterns and bullish continuations
        for symbol in final_symbols:
            symbol_bars = bars_data['bars'].get(symbol, [])
            if len(symbol_bars) < lookback_days + 20:  # Need enough data for ATR and pattern analysis
                logging.warning(f"Insufficient data for {symbol}: {len(symbol_bars)} bars")
                continue
            
            # Convert to DataFrame for easier analysis
            df = pd.DataFrame(symbol_bars)
            df['date'] = pd.to_datetime(df['t'])
            df = df.sort_values('date').reset_index(drop=True)
            
            # Calculate ATR for volatility context
            ohlc_data = {
                'high': df['h'].values,
                'low': df['l'].values,
                'close': df['c'].values
            }
            
            atr_result = safe_mcp_call("calculate_atr", {"data": ohlc_data, "period": atr_period})
            if not atr_result.get('success') or atr_result.get('atr') is None:
                logging.warning(f"ATR calculation failed for {symbol}")
                continue
            
            atr_series = pd.Series(atr_result['atr'])
            
            # Calculate daily ranges
            df['range'] = df['h'] - df['l']
            
            # Identify NR4 days (Narrow Range 4)
            nr4_days = []
            bullish_continuations = 0
            total_nr4_occurrences = 0
            
            for i in range(lookback_days, len(df) - 1):  # -1 to check next day for continuation
                # Check if current day has narrowest range in last 4 days
                current_range = df.iloc[i]['range']
                lookback_ranges = df.iloc[i-lookback_days+1:i+1]['range']
                
                # Also check against ATR context
                current_atr = atr_series.iloc[i] if i < len(atr_series) else None
                if current_atr is None:
                    continue
                
                # NR4 condition: narrowest range in last 4 days AND below ATR threshold
                is_nr4 = (current_range == lookback_ranges.min() and 
                         current_range < current_atr * nr4_atr_multiplier)
                
                if is_nr4:
                    total_nr4_occurrences += 1
                    nr4_date = df.iloc[i]['date']
                    
                    # Check for bullish continuation next day
                    next_day_close = df.iloc[i+1]['c']
                    nr4_close = df.iloc[i]['c']
                    
                    price_change_pct = (next_day_close - nr4_close) / nr4_close
                    
                    if price_change_pct >= bullish_continuation_threshold:
                        bullish_continuations += 1
                        nr4_days.append({
                            'date': nr4_date.strftime('%Y-%m-%d'),
                            'nr4_range': current_range,
                            'atr': current_atr,
                            'continuation_pct': price_change_pct * 100
                        })
            
            # Calculate success rate and apply price filters
            latest_price = df.iloc[-1]['c']
            
            # Apply price filters if specified
            if min_price is not None and latest_price < min_price:
                continue
            if max_price is not None and latest_price > max_price:
                continue
            
            if total_nr4_occurrences >= min_occurrences:
                success_rate = (bullish_continuations / total_nr4_occurrences) * 100
                avg_continuation = np.mean([day['continuation_pct'] for day in nr4_days]) if nr4_days else 0
                
                symbol_results.append({
                    'symbol': symbol,
                    'total_nr4_occurrences': total_nr4_occurrences,
                    'bullish_continuations': bullish_continuations,
                    'success_rate_pct': success_rate,
                    'latest_price': latest_price,
                    'avg_continuation_pct': avg_continuation,
                    'nr4_examples': nr4_days[:3]  # Show up to 3 examples
                })
        
        # Sort by specified criteria
        if sort_by == "success_rate":
            symbol_results.sort(key=lambda x: (x['success_rate_pct'], x['total_nr4_occurrences']), reverse=True)
        elif sort_by == "occurrences":
            symbol_results.sort(key=lambda x: (x['total_nr4_occurrences'], x['success_rate_pct']), reverse=True)
        elif sort_by == "avg_continuation":
            symbol_results.sort(key=lambda x: (x['avg_continuation_pct'], x['success_rate_pct']), reverse=True)
        else:
            # Default to success_rate
            symbol_results.sort(key=lambda x: (x['success_rate_pct'], x['total_nr4_occurrences']), reverse=True)
        
        # Calculate summary statistics
        total_symbols_analyzed = len([r for r in symbol_results if r['total_nr4_occurrences'] > 0])
        avg_success_rate = np.mean([r['success_rate_pct'] for r in symbol_results]) if symbol_results else 0
        top_performers = symbol_results[:max_results]
        
        results = {
            "question": "Which symbols most often printed bullish continuation after NR4 days?",
            "analysis_completed": True,
            "parameters_used": {
                "symbols": symbols,
                "top_symbols": top_symbols,
                "analysis_period_days": analysis_period_days,
                "start_date": final_start_date,
                "end_date": final_end_date,
                "nr4_atr_multiplier": nr4_atr_multiplier,
                "bullish_continuation_threshold": bullish_continuation_threshold,
                "lookback_days": lookback_days,
                "atr_period": atr_period,
                "min_occurrences": min_occurrences,
                "max_results": max_results,
                "sort_by": sort_by,
                "timeframe": timeframe,
                "exclude_symbols": exclude_symbols,
                "min_price": min_price,
                "max_price": max_price
            },
            "results": {
                "summary": {
                    "total_symbols_analyzed": total_symbols_analyzed,
                    "average_success_rate_pct": round(avg_success_rate, 2),
                    "analysis_period": f"{final_start_date} to {final_end_date}",
                    "nr4_definition": f"Narrowest range in {lookback_days} days AND < {nr4_atr_multiplier}x ATR"
                },
                "top_performers": top_performers,
                "methodology": {
                    "nr4_identification": "Daily range is minimum of last 4 days AND below ATR threshold",
                    "bullish_continuation": f"Next day close > {bullish_continuation_threshold*100}% above NR4 close",
                    "success_rate_calculation": "Bullish continuations / Total NR4 occurrences",
                    "ranking_criteria": "Success rate and occurrence frequency"
                }
            },
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "data_source": "MCP Financial + Analytics Servers",
                "pattern_type": "NR4 (Narrow Range 4) Bullish Continuation"
            }
        }
        
        logging.info("✅ NR4 bullish continuation analysis completed")
        return results
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logging.error(f"❌ Analysis failed: {e}")
        logging.error(f"Full traceback: {error_details}")
        return {
            "question": "Which symbols most often printed bullish continuation after NR4 days?",
            "analysis_completed": False,
            "error": str(e),
            "error_traceback": error_details
        }

def main(mock=False):
    """Main analysis function with comprehensive default parameters"""
    return analyze_nr4_bullish_continuation(
        symbols=None,  # Use most active symbols by default
        top_symbols=50,
        analysis_period_days=180,
        start_date=None,
        end_date=None,
        nr4_atr_multiplier=0.5,
        bullish_continuation_threshold=0.02,
        lookback_days=4,
        atr_period=14,
        min_occurrences=3,
        max_results=10,
        sort_by="success_rate",
        timeframe="1Day",
        exclude_symbols=None,
        min_price=None,
        max_price=None,
        mock=mock
    )

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true")
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    results = main(mock=args.mock)
    print(json.dumps(results, indent=2, default=str))