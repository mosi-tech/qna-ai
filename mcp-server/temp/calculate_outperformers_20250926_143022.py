#!/usr/bin/env python3
"""
Calculate which ETFs outperformed both SPY and QQQ over 30 days.
"""

import json
import logging
from datetime import datetime, timedelta

def calculate_outperformers(historical_bars):
    """
    Calculate ETFs that outperformed both SPY and QQQ over 30 days.
    
    Args:
        historical_bars: Response from alpaca_market_stocks_bars
        
    Returns:
        dict: Analysis results with outperforming ETFs and performance metrics
    """
    logging.info("📊 Calculating ETF outperformers vs SPY and QQQ")
    
    try:
        # Parse historical bars data
        if isinstance(historical_bars, str):
            bars_data = json.loads(historical_bars)
        else:
            bars_data = historical_bars
            
        # Extract bars for each symbol
        bars = bars_data.get('bars', {})
        
        # Calculate 30-day returns for each symbol
        returns = {}
        
        for symbol, symbol_bars in bars.items():
            if not symbol_bars or len(symbol_bars) < 2:
                continue
                
            # Sort bars by timestamp
            sorted_bars = sorted(symbol_bars, key=lambda x: x['timestamp'])
            
            # Get first and last prices
            start_price = float(sorted_bars[0]['close'])
            end_price = float(sorted_bars[-1]['close'])
            
            # Calculate return
            total_return = (end_price - start_price) / start_price
            returns[symbol] = {
                'total_return': total_return,
                'start_price': start_price,
                'end_price': end_price,
                'days': len(sorted_bars)
            }
        
        # Get benchmark returns
        spy_return = returns.get('SPY', {}).get('total_return', 0)
        qqq_return = returns.get('QQQ', {}).get('total_return', 0)
        
        logging.info(f"📈 SPY 30-day return: {spy_return:.2%}")
        logging.info(f"📈 QQQ 30-day return: {qqq_return:.2%}")
        
        # Find ETFs that outperformed both benchmarks
        outperformers = []
        
        for symbol, metrics in returns.items():
            if symbol in ['SPY', 'QQQ']:  # Skip benchmarks
                continue
                
            etf_return = metrics['total_return']
            
            if etf_return > spy_return and etf_return > qqq_return:
                outperformers.append({
                    'symbol': symbol,
                    'total_return': etf_return,
                    'vs_spy': etf_return - spy_return,
                    'vs_qqq': etf_return - qqq_return,
                    'start_price': metrics['start_price'],
                    'end_price': metrics['end_price'],
                    'days_analyzed': metrics['days']
                })
        
        # Sort by total return (descending)
        outperformers.sort(key=lambda x: x['total_return'], reverse=True)
        
        result = {
            'question': 'Which ETFs outperformed both SPY and QQQ over the last 30 days?',
            'analysis_period': '30 days',
            'benchmarks': {
                'SPY': {
                    'return': spy_return,
                    'return_pct': f"{spy_return:.2%}"
                },
                'QQQ': {
                    'return': qqq_return,
                    'return_pct': f"{qqq_return:.2%}"
                }
            },
            'outperforming_etfs': outperformers[:10],  # Top 10
            'total_etfs_analyzed': len(returns) - 2,  # Exclude SPY, QQQ
            'outperformers_count': len(outperformers),
            'methodology': 'Simple total return calculation over 30-day period'
        }
        
        logging.info(f"✅ Found {len(outperformers)} ETFs outperforming both benchmarks")
        
        return result
        
    except Exception as e:
        logging.error(f"❌ Error calculating outperformers: {e}")
        return {
            'error': f'Analysis failed: {str(e)}',
            'question': 'Which ETFs outperformed both SPY and QQQ over the last 30 days?',
            'outperforming_etfs': [],
            'outperformers_count': 0
        }

if __name__ == "__main__":
    # Test with sample data
    sample_bars = {
        'bars': {
            'SPY': [{'close': 400, 'timestamp': '2025-08-27'}, {'close': 410, 'timestamp': '2025-09-26'}],
            'QQQ': [{'close': 350, 'timestamp': '2025-08-27'}, {'close': 360, 'timestamp': '2025-09-26'}],
            'ARKK': [{'close': 50, 'timestamp': '2025-08-27'}, {'close': 60, 'timestamp': '2025-09-26'}]
        }
    }
    result = calculate_outperformers(sample_bars)
    print(json.dumps(result, indent=2))