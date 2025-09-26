"""
ETF Performance Comparison vs SPY and QQQ
Extract prices and calculate 30-day returns for performance comparison
"""

def extract_prices_and_calculate_returns(price_data):
    """
    Extract closing prices and calculate 30-day returns for ETF vs SPY/QQQ comparison
    
    Args:
        price_data: Raw price data from alpaca_market_stocks_bars
        
    Returns:
        dict: ETF performance comparison results
    """
    
    # Extract bars data
    bars_data = price_data.get('bars', {})
    
    # Initialize results
    results = {
        'etfs_outperforming_both': [],
        'all_returns': {},
        'benchmark_returns': {},
        'analysis_period': '30_days'
    }
    
    # Calculate returns for each symbol
    for symbol, bars in bars_data.items():
        if not bars or len(bars) < 2:
            continue
            
        # Get first and last closing prices
        first_price = bars[0]['c']
        last_price = bars[-1]['c']
        
        # Calculate 30-day return
        total_return = ((last_price - first_price) / first_price) * 100
        
        results['all_returns'][symbol] = {
            'total_return_pct': round(total_return, 2),
            'start_price': first_price,
            'end_price': last_price,
            'days': len(bars)
        }
    
    # Extract benchmark returns
    spy_return = results['all_returns'].get('SPY', {}).get('total_return_pct', 0)
    qqq_return = results['all_returns'].get('QQQ', {}).get('total_return_pct', 0)
    
    results['benchmark_returns'] = {
        'SPY': spy_return,
        'QQQ': qqq_return
    }
    
    # Find ETFs that outperformed both SPY and QQQ
    etf_symbols = ['VTI', 'VOO', 'ARKK', 'GLD', 'VEA', 'VWO', 'IWM', 'EFA', 'XLK', 'XLF', 'XLE', 'XLV', 'XLI']
    
    for symbol in etf_symbols:
        if symbol in results['all_returns']:
            etf_return = results['all_returns'][symbol]['total_return_pct']
            
            if etf_return > spy_return and etf_return > qqq_return:
                results['etfs_outperforming_both'].append({
                    'symbol': symbol,
                    'return_pct': etf_return,
                    'vs_spy': round(etf_return - spy_return, 2),
                    'vs_qqq': round(etf_return - qqq_return, 2)
                })
    
    # Sort by performance
    results['etfs_outperforming_both'].sort(key=lambda x: x['return_pct'], reverse=True)
    
    # Add summary statistics
    results['summary'] = {
        'total_etfs_analyzed': len(etf_symbols),
        'etfs_outperforming_both_count': len(results['etfs_outperforming_both']),
        'best_performer': results['etfs_outperforming_both'][0] if results['etfs_outperforming_both'] else None
    }
    
    return results