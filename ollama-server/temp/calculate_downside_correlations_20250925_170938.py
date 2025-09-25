def calculate_downside_correlations():
    """Calculate downside correlation between holdings and SPY during market decline periods"""
    import pandas as pd
    import numpy as np
    
    # Get SPY data
    spy_bars = bars_data.get('SPY', [])
    if not spy_bars:
        return {'error': 'SPY data not available'}
    
    spy_df = pd.DataFrame(spy_bars)
    spy_df['spy_return'] = spy_df['c'].pct_change()
    
    # Filter for SPY down days only (> 0.1% decline)
    down_days = spy_df['spy_return'] < -0.001
    
    correlations = []
    for symbol in position_symbols:
        if symbol == 'SPY': continue
        
        bars = bars_data.get(symbol, [])
        if len(bars) < 50: continue
        
        df = pd.DataFrame(bars)
        df['return'] = df['c'].pct_change()
        
        # Align dates with SPY
        spy_dates = spy_df['t'].values
        stock_data = df[df['t'].isin(spy_dates)]
        
        # Get returns on SPY down days only
        aligned_spy = spy_df[spy_df['t'].isin(stock_data['t'])]
        down_mask = aligned_spy['spy_return'] < -0.001
        
        if down_mask.sum() < 20:  # Need minimum observations
            continue
            
        spy_down_returns = aligned_spy[down_mask]['spy_return']
        stock_down_returns = stock_data[down_mask]['return']
        
        if len(spy_down_returns) > 0 and len(stock_down_returns) > 0:
            corr = np.corrcoef(spy_down_returns, stock_down_returns)[0,1]
            if not np.isnan(corr):
                correlations.append({
                    'symbol': symbol,
                    'downside_correlation': round(corr, 4),
                    'observations': len(spy_down_returns),
                    'total_spy_down_days': down_mask.sum()
                })
    
    # Sort by correlation strength (descending)
    correlations.sort(key=lambda x: abs(x['downside_correlation']), reverse=True)
    
    return {
        'highest_downside_correlation': correlations[0] if correlations else None,
        'all_correlations': correlations[:5],  # Top 5
        'spy_down_days': down_days.sum(),
        'analysis_period': '2023-2024',
        'methodology': 'Correlation calculated only during SPY decline days (>0.1% drop)'
    }