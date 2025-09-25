def calculate_downside_correlations():
    """Calculate downside correlation between holdings and SPY during market decline periods"""
    # Get SPY data
    spy_bars = bars_data.get('SPY', [])
    if not spy_bars:
        return {'error': 'SPY data not available'}
    
    spy_df = pd.DataFrame(spy_bars)
    spy_df['spy_return'] = spy_df['c'].pct_change()
    
    # Filter for SPY down days only
    down_days = spy_df['spy_return'] < -0.001  # SPY down > 0.1%
    
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
        
        if down_mask.sum() < 10: continue  # Need at least 10 down days
        
        stock_down_returns = stock_data[down_mask]['return']
        spy_subset = aligned_spy[down_mask]['spy_return']
        
        if len(stock_down_returns) > 0 and len(spy_subset) > 0:
            downside_corr = np.corrcoef(stock_down_returns, spy_subset)[0,1]
            if not np.isnan(downside_corr):
                correlations.append({
                    'symbol': symbol,
                    'downside_correlation': round(downside_corr, 3),
                    'down_days_analyzed': len(stock_down_returns),
                    'avg_return_on_spy_down': round(stock_down_returns.mean() * 100, 2)
                })
    
    correlations.sort(key=lambda x: x['downside_correlation'], reverse=True)
    return correlations