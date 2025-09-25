def calculate_downside_correlations():
    """Calculate downside correlation between holdings and SPY using only built-in Python libraries"""
    try:
        # Get SPY data from context
        spy_bars = bars_data.get('SPY', [])
        if not spy_bars:
            return {'error': 'SPY data not available', 'context_keys': list(context_data.keys())}
        
        # Calculate SPY returns manually
        spy_returns = []
        spy_dates = []
        
        for i in range(1, len(spy_bars)):
            if spy_bars[i-1].get('c') and spy_bars[i].get('c'):
                prev_close = float(spy_bars[i-1]['c'])
                curr_close = float(spy_bars[i]['c'])
                return_val = (curr_close - prev_close) / prev_close
                spy_returns.append(return_val)
                spy_dates.append(spy_bars[i].get('t', ''))
        
        # Filter for SPY down days (> 0.1% decline)
        down_day_indices = []
        for i, ret in enumerate(spy_returns):
            if ret < -0.001:  # > 0.1% decline
                down_day_indices.append(i)
        
        if len(down_day_indices) < 20:
            return {'error': f'Insufficient SPY down days: {len(down_day_indices)}'}
        
        # Analyze each position
        correlations = []
        
        for symbol in position_symbols:
            if symbol == 'SPY':
                continue
                
            # Get stock data
            stock_bars = bars_data.get(symbol, [])
            if len(stock_bars) < 50:
                continue
                
            # Calculate stock returns
            stock_returns = []
            for i in range(1, len(stock_bars)):
                if stock_bars[i-1].get('c') and stock_bars[i].get('c'):
                    prev_close = float(stock_bars[i-1]['c'])
                    curr_close = float(stock_bars[i]['c'])
                    return_val = (curr_close - prev_close) / prev_close
                    stock_returns.append(return_val)
            
            # Align with SPY returns (simplified - assume same length)
            min_len = min(len(spy_returns), len(stock_returns))
            if min_len < 100:
                continue
                
            # Get returns on SPY down days only
            spy_down_returns = []
            stock_down_returns = []
            
            for idx in down_day_indices:
                if idx < min_len:
                    spy_down_returns.append(spy_returns[idx])
                    stock_down_returns.append(stock_returns[idx])
            
            if len(spy_down_returns) < 10:
                continue
                
            # Calculate correlation manually (Pearson correlation)
            n = len(spy_down_returns)
            if n < 2:
                continue
                
            # Calculate means
            spy_mean = sum(spy_down_returns) / n
            stock_mean = sum(stock_down_returns) / n
            
            # Calculate correlation components
            numerator = sum((spy_down_returns[i] - spy_mean) * (stock_down_returns[i] - stock_mean) for i in range(n))
            spy_var = sum((spy_down_returns[i] - spy_mean) ** 2 for i in range(n))
            stock_var = sum((stock_down_returns[i] - stock_mean) ** 2 for i in range(n))
            
            if spy_var == 0 or stock_var == 0:
                continue
                
            correlation = numerator / (spy_var * stock_var) ** 0.5
            
            correlations.append({
                'symbol': symbol,
                'downside_correlation': round(correlation, 4),
                'observations': n,
                'spy_down_days_used': len(spy_down_returns)
            })
        
        # Sort by absolute correlation strength
        correlations.sort(key=lambda x: abs(x['downside_correlation']), reverse=True)
        
        return {
            'highest_downside_correlation': correlations[0] if correlations else None,
            'all_correlations': correlations[:5],  # Top 5
            'total_spy_down_days': len(down_day_indices),
            'analysis_period': '2023-2024',
            'methodology': 'Manual correlation calculation using only Python built-ins',
            'positions_analyzed': len(correlations)
        }
        
    except Exception as e:
        return {
            'error': f'Analysis failed: {str(e)}',
            'context_available': 'context_data' in globals(),
            'position_symbols_available': 'position_symbols' in globals(),
            'bars_data_available': 'bars_data' in globals()
        }