def analyze_watchlist_momentum():
    import json
    
    # Access execution context
    step_data = context_data
    
    # Get position data to identify watchlist symbols
    positions_data = step_data.get('positions_data')
    historical_bars = step_data.get('historical_bars')
    
    if not positions_data:
        return {"error": "No positions data found to identify watchlist symbols"}
    
    if not historical_bars:
        return {"error": "No historical bars data found"}
    
    # Parse positions data if string
    if isinstance(positions_data, str):
        try:
            positions_data = json.loads(positions_data)
        except json.JSONDecodeError:
            return {"error": "Invalid positions data format"}
    
    # Parse historical bars data if string
    if isinstance(historical_bars, str):
        try:
            historical_bars = json.loads(historical_bars)
        except json.JSONDecodeError:
            return {"error": "Invalid historical bars data format"}
    
    # Extract symbols from positions
    watchlist_symbols = []
    if isinstance(positions_data, list):
        watchlist_symbols = [pos.get('symbol') for pos in positions_data if pos.get('symbol')]
    elif isinstance(positions_data, dict) and 'positions' in positions_data:
        watchlist_symbols = [pos.get('symbol') for pos in positions_data['positions'] if pos.get('symbol')]
    
    if not watchlist_symbols:
        return {"error": "No symbols found in positions data"}
    
    # Calculate 6-month momentum for each symbol
    momentum_results = []
    
    # Access bars data
    bars_data = historical_bars.get('bars', {}) if isinstance(historical_bars, dict) else {}
    
    for symbol in watchlist_symbols:
        if symbol not in bars_data:
            continue
            
        bars = bars_data[symbol]
        if not bars or len(bars) < 2:
            continue
            
        # Calculate 6-month return (first close to last close)
        start_price = float(bars[0]['c'])  # First close price
        end_price = float(bars[-1]['c'])   # Last close price
        
        six_month_return = ((end_price - start_price) / start_price) * 100
        
        momentum_results.append({
            'symbol': symbol,
            'start_price': round(start_price, 2),
            'end_price': round(end_price, 2),
            'six_month_momentum': round(six_month_return, 2),
            'total_bars': len(bars)
        })
    
    # Sort by strongest momentum (highest returns first)
    momentum_results.sort(key=lambda x: x['six_month_momentum'], reverse=True)
    
    # Prepare summary statistics
    if momentum_results:
        avg_momentum = sum(r['six_month_momentum'] for r in momentum_results) / len(momentum_results)
        max_momentum = max(r['six_month_momentum'] for r in momentum_results)
        min_momentum = min(r['six_month_momentum'] for r in momentum_results)
        
        return {
            'watchlist_momentum_ranking': momentum_results,
            'summary': {
                'total_symbols_analyzed': len(momentum_results),
                'average_momentum': round(avg_momentum, 2),
                'highest_momentum': round(max_momentum, 2),
                'lowest_momentum': round(min_momentum, 2),
                'analysis_period': '6 months (180 days)'
            },
            'strongest_performers': momentum_results[:5]  # Top 5
        }
    else:
        return {"error": "No momentum data could be calculated for watchlist symbols"}