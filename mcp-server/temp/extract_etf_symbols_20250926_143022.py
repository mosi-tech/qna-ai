#!/usr/bin/env python3
"""
Extract ETF symbols from active securities data for analysis.
"""

import json
import logging

def extract_etf_symbols(active_securities):
    """
    Extract ETF symbols from active securities response.
    
    Args:
        active_securities: Response from alpaca_market_screener_most_actives
        
    Returns:
        str: Comma-separated string of ETF symbols
    """
    logging.info("🔍 Extracting ETF symbols from active securities")
    
    try:
        # Parse the active securities data
        if isinstance(active_securities, str):
            securities_data = json.loads(active_securities)
        else:
            securities_data = active_securities
            
        # Filter for ETF symbols (typically contain ETF patterns)
        etf_keywords = ['ETF', 'Fund', 'Trust', 'Index']
        etf_symbols = []
        
        # Common ETF symbols to prioritize
        known_etfs = ['SPY', 'QQQ', 'IWM', 'VTI', 'VOO', 'ARKK', 'ARKQ', 'ARKG', 
                     'XLF', 'XLE', 'XLK', 'XLV', 'XLI', 'XLU', 'XLP', 'XLY', 
                     'GLD', 'SLV', 'TLT', 'IEF', 'HYG', 'LQD', 'EEM', 'EFA']
        
        for security in securities_data[:50]:  # Check top 50 active securities
            symbol = security.get('symbol', '')
            
            # Add known ETFs first
            if symbol in known_etfs and symbol not in etf_symbols:
                etf_symbols.append(symbol)
            # Add symbols that look like ETFs
            elif len(symbol) <= 5 and symbol.isalpha() and symbol not in etf_symbols:
                etf_symbols.append(symbol)
                
        # Limit to top 20 ETFs for analysis
        etf_symbols = etf_symbols[:20]
        
        result = ','.join(etf_symbols)
        logging.info(f"✅ Extracted {len(etf_symbols)} ETF symbols: {result}")
        
        return result
        
    except Exception as e:
        logging.error(f"❌ Error extracting ETF symbols: {e}")
        # Fallback to common ETFs
        fallback_etfs = "ARKK,ARKQ,ARKG,XLF,XLE,XLK,XLV,XLI,XLU,XLP,XLY,GLD,SLV,TLT,IEF,HYG,LQD,EEM,EFA,VTI"
        logging.info(f"🔄 Using fallback ETFs: {fallback_etfs}")
        return fallback_etfs

if __name__ == "__main__":
    # Test with sample data
    sample_data = [{"symbol": "ARKK"}, {"symbol": "XLF"}, {"symbol": "GLD"}]
    result = extract_etf_symbols(sample_data)
    print(f"Test result: {result}")