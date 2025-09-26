def calculate_downside_gap_fills():
    """
    Calculate downside gap fills from OHLC bar data.
    Uses context_data from the execution engine to access step data.
        
    Returns:
        List of dictionaries with gap fill analysis results
    """
    gap_fills = []
    
    import json
    
    # Get data from context_data (set by execution engine)
    step_data = context_data
    
    # Look for bars data in tool results
    bars_dict = None
    
    # Check tool results for bars data
    for key, value in step_data.items():
        if "tool_result" in key and isinstance(value, dict):
            result = value.get("result", {})
            # Parse the JSON content from MCP response
            if "content" in result and len(result["content"]) > 0:
                try:
                    content_text = result["content"][0].get("text", "")
                    parsed_data = json.loads(content_text)
                    if "bars" in parsed_data:
                        bars_dict = parsed_data["bars"]
                        break
                except (json.JSONDecodeError, KeyError, IndexError) as e:
                    continue
    
    if not bars_dict:
        return {"error": "No bars data found in context"}
    
    if not isinstance(bars_dict, dict):
        return {"error": f"Invalid bars data format: {type(bars_dict)}"}
    
    for symbol, bars in bars_dict.items():
        if len(bars) < 2:
            continue
            
        # Get yesterday and today data
        yesterday = bars[-2]  # Second to last bar
        today = bars[-1]     # Last bar
        
        yesterday_close = yesterday['c']
        today_open = today['o'] 
        today_high = today['h']
        today_low = today['l']
        today_close = today['c']
        
        # Check for downside gap (today open < yesterday close)
        if today_open >= yesterday_close:
            continue
            
        gap_size = yesterday_close - today_open
        if gap_size <= 0:
            continue
            
        # Calculate gap fill metrics
        recovery_amount = today_high - today_open
        gap_fill_percentage = (recovery_amount / gap_size) * 100 if gap_size > 0 else 0
        
        # Only include if there was meaningful recovery (>5%)
        if gap_fill_percentage > 5:
            gap_fills.append({
                'symbol': symbol,
                'yesterday_close': yesterday_close,
                'today_open': today_open,
                'today_high': today_high,
                'today_close': today_close,
                'gap_size': gap_size,
                'recovery_amount': recovery_amount,
                'gap_fill_percentage': round(gap_fill_percentage, 2),
                'gap_percentage': round((gap_size / yesterday_close) * 100, 2)
            })
    
    # Sort by gap fill percentage (largest first)
    gap_fills.sort(key=lambda x: x['gap_fill_percentage'], reverse=True)
    
    return gap_fills[:20]  # Return top 20 results