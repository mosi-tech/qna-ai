def analyze_momentum_rankings():
    import json
    from datetime import datetime, timedelta
    
    # Access execution context
    step_data = context_data
    
    # Get positions data
    positions_data = step_data.get('positions_data')
    
    # Extract symbols from positions
    if positions_data:
        try:
            if isinstance(positions_data, str):
                positions = json.loads(positions_data)
            else:
                positions = positions_data
            
            symbols = []
            if isinstance(positions, list):
                symbols = [pos.get('symbol') for pos in positions if pos.get('symbol')]
            elif isinstance(positions, dict) and 'positions' in positions:
                symbols = [pos.get('symbol') for pos in positions['positions'] if pos.get('symbol')]
            
            symbols_str = ','.join(symbols) if symbols else 'AAPL,MSFT,GOOGL'
        except:
            symbols_str = 'AAPL,MSFT,GOOGL'
    else:
        symbols_str = 'AAPL,MSFT,GOOGL'
    
    # Calculate dates
    current_date = datetime.now().strftime('%Y-%m-%d')
    six_months_ago = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
    
    # Get historical data
    historical_data = step_data.get('historical_data')
    
    momentum_results = []
    
    if historical_data:
        try:
            if isinstance(historical_data, str):
                data = json.loads(historical_data)
            else:
                data = historical_data
            
            # Process each symbol's data
            for symbol, bars in data.get('bars', {}).items():
                if bars and len(bars) > 0:
                    # Calculate momentum (6-month return)
                    start_price = float(bars[0]['c'])  # First close price
                    end_price = float(bars[-1]['c'])   # Last close price
                    
                    momentum = ((end_price - start_price) / start_price) * 100
                    
                    momentum_results.append({
                        'symbol': symbol,
                        'momentum_pct': round(momentum, 2),
                        'start_price': start_price,
                        'end_price': end_price,
                        'period_days': len(bars)
                    })
        except Exception as e:
            print(f"Error processing historical data: {e}")
    
    # Sort by momentum (highest first)
    momentum_results.sort(key=lambda x: x['momentum_pct'], reverse=True)
    
    return {
        'symbols_analyzed': symbols_str,
        'analysis_period': f"{six_months_ago} to {current_date}",
        'momentum_rankings': momentum_results[:10],  # Top 10
        'total_symbols': len(momentum_results)
    }