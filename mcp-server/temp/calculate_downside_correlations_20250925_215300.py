def calculate_downside_correlations():
    """Calculate downside correlation between portfolio holdings and SPY during SPY decline periods only."""
    import pandas as pd
    import numpy as np
    
    # Get positions data
    positions = context_data.get('positions_data', [])
    if not positions:
        return {"error": "No positions data available"}
    
    # Extract symbols from positions
    symbols = [pos.get('symbol') for pos in positions if pos.get('symbol')]
    if not symbols:
        return {"error": "No symbols found in positions"}
    
    # Get price data
    price_data = context_data.get('price_data', {})
    if not price_data or 'bars' not in price_data:
        return {"error": "No price data available"}
    
    bars = price_data['bars']
    
    # Extract SPY data
    if 'SPY' not in bars:
        return {"error": "SPY data not found in price data"}
    
    spy_bars = bars['SPY']
    spy_df = pd.DataFrame(spy_bars)
    spy_df['date'] = pd.to_datetime(spy_df['t'])
    spy_df = spy_df.sort_values('date').reset_index(drop=True)
    spy_df['spy_return'] = spy_df['c'].pct_change()
    
    # Identify SPY down periods (negative returns)
    down_periods = spy_df['spy_return'] < 0
    
    results = {}
    correlations = {}
    
    for symbol in symbols:
        if symbol == 'SPY':
            continue
            
        if symbol not in bars:
            results[symbol] = {"error": f"No price data found for {symbol}"}
            continue
        
        # Process symbol data
        symbol_bars = bars[symbol]
        symbol_df = pd.DataFrame(symbol_bars)
        symbol_df['date'] = pd.to_datetime(symbol_df['t'])
        symbol_df = symbol_df.sort_values('date').reset_index(drop=True)
        symbol_df['return'] = symbol_df['c'].pct_change()
        
        # Merge with SPY data on date
        merged = pd.merge(spy_df[['date', 'spy_return']], 
                         symbol_df[['date', 'return']], 
                         on='date', how='inner')
        
        # Calculate downside correlation (only during SPY down periods)
        down_data = merged[merged['spy_return'] < 0]
        
        if len(down_data) < 5:  # Need at least 5 observations
            results[symbol] = {
                "downside_correlation": None,
                "error": "Insufficient downside periods for correlation calculation",
                "down_periods": len(down_data)
            }
            continue
        
        # Calculate correlation during down periods
        downside_corr = down_data['spy_return'].corr(down_data['return'])
        correlations[symbol] = downside_corr
        
        results[symbol] = {
            "downside_correlation": float(downside_corr) if not pd.isna(downside_corr) else None,
            "down_periods_analyzed": len(down_data),
            "total_periods": len(merged)
        }
    
    # Find highest correlation
    valid_corrs = {k: v for k, v in correlations.items() if not pd.isna(v)}
    highest_symbol = max(valid_corrs.items(), key=lambda x: x[1]) if valid_corrs else None
    
    return {
        "question": "Which of my holdings has the highest downside correlation with SPY?",
        "answer": {
            "highest_correlation_holding": highest_symbol[0] if highest_symbol else "None",
            "highest_correlation_value": float(highest_symbol[1]) if highest_symbol else None
        },
        "portfolio_symbols": symbols,
        "detailed_correlations": results,
        "analysis_summary": {
            "symbols_analyzed": len([s for s in results.keys() if "error" not in results[s]]),
            "symbols_with_errors": len([s for s in results.keys() if "error" in results[s]]),
            "total_spy_periods": len(spy_df) - 1,
            "total_spy_down_periods": sum(down_periods)
        }
    }