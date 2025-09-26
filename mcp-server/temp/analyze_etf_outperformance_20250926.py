def analyze_etf_outperformance():
    import json
    
    # Access execution context
    step_data = context_data
    
    # Use named output variables from workflow steps
    benchmark_data = step_data.get('benchmark_bars')
    etf_universe = step_data.get('active_symbols')  
    etf_data = step_data.get('etf_bars')
    
    if not benchmark_data:
        return {"error": "No benchmark data (SPY/QQQ) found"}
    
    if not etf_data:
        return {"error": "No ETF historical data found"}
    
    # Calculate 30-day returns for benchmarks
    def calculate_30_day_return(bars):
        if len(bars) < 2:
            return None
        start_price = bars[0]['c']  # First close
        end_price = bars[-1]['c']   # Last close
        return ((end_price - start_price) / start_price) * 100
    
    # Access benchmark bars data
    if "bars" in benchmark_data:
        benchmark_bars = benchmark_data["bars"]
    else:
        benchmark_bars = benchmark_data
        
    spy_return = calculate_30_day_return(benchmark_bars.get("SPY", []))
    qqq_return = calculate_30_day_return(benchmark_bars.get("QQQ", []))
    
    if spy_return is None or qqq_return is None:
        return {"error": "Could not calculate benchmark returns"}
    
    # Analyze ETF performance
    outperformers = []
    
    # Access ETF bars data
    if "bars" in etf_data:
        etf_bars = etf_data["bars"]
    else:
        etf_bars = etf_data
    
    for symbol, bars in etf_bars.items():
        if len(bars) < 2:
            continue
            
        etf_return = calculate_30_day_return(bars)
        if etf_return is None:
            continue
            
        # Check if outperformed both SPY and QQQ
        if etf_return > spy_return and etf_return > qqq_return:
            outperformers.append({
                'symbol': symbol,
                'return_30d': round(etf_return, 2),
                'outperformance_vs_spy': round(etf_return - spy_return, 2),
                'outperformance_vs_qqq': round(etf_return - qqq_return, 2),
                'start_price': bars[0]['c'],
                'end_price': bars[-1]['c']
            })
    
    # Sort by total return (highest first)
    outperformers.sort(key=lambda x: x['return_30d'], reverse=True)
    
    return {
        'benchmark_returns': {
            'SPY': round(spy_return, 2),
            'QQQ': round(qqq_return, 2)
        },
        'outperforming_etfs': outperformers[:15],  # Top 15
        'total_analyzed': len(etf_bars),
        'outperformers_count': len(outperformers)
    }