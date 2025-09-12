"""
Gap analysis module for identifying and analyzing price gaps.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional


class GapAnalyzer:
    """Analyze various types of price gaps in financial data."""
    
    @staticmethod
    def identify_gaps(price_data: List[Dict], gap_threshold: float = 0.5) -> Dict[str, Any]:
        """
        Identify different types of price gaps.
        
        Args:
            price_data: List of OHLC dictionaries with 't', 'o', 'h', 'l', 'c' keys
            gap_threshold: Minimum gap percentage to consider significant
            
        Returns:
            Dictionary with gap analysis
        """
        if len(price_data) < 2:
            return {"error": "Need at least 2 periods for gap analysis"}
        
        df = pd.DataFrame(price_data)
        df['t'] = pd.to_datetime(df['t'])
        df = df.sort_values('t').reset_index(drop=True)
        
        # Calculate gaps
        df['prev_close'] = df['c'].shift(1)
        df['gap_amount'] = df['o'] - df['prev_close']
        df['gap_percent'] = (df['gap_amount'] / df['prev_close']) * 100
        
        # Classify gaps
        gaps = []
        for i in range(1, len(df)):
            row = df.iloc[i]
            gap_pct = row['gap_percent']
            
            if abs(gap_pct) >= gap_threshold:
                gap_type = GapAnalyzer._classify_gap_type(row, gap_pct)
                
                gap_info = {
                    "date": row['t'].strftime('%Y-%m-%d'),
                    "index": i,
                    "gap_percent": float(gap_pct),
                    "gap_amount": float(row['gap_amount']),
                    "gap_direction": "up" if gap_pct > 0 else "down",
                    "gap_type": gap_type,
                    "open_price": float(row['o']),
                    "prev_close": float(row['prev_close']),
                    "high": float(row['h']),
                    "low": float(row['l']),
                    "close": float(row['c'])
                }
                gaps.append(gap_info)
        
        # Analyze gap statistics
        up_gaps = [g for g in gaps if g["gap_direction"] == "up"]
        down_gaps = [g for g in gaps if g["gap_direction"] == "down"]
        
        return {
            "total_gaps": len(gaps),
            "up_gaps": len(up_gaps),
            "down_gaps": len(down_gaps),
            "gap_frequency": len(gaps) / len(df) * 100,
            "avg_gap_size": float(np.mean([abs(g["gap_percent"]) for g in gaps])) if gaps else 0,
            "largest_up_gap": max([g["gap_percent"] for g in up_gaps]) if up_gaps else 0,
            "largest_down_gap": min([g["gap_percent"] for g in down_gaps]) if down_gaps else 0,
            "gaps": gaps,
            "gap_threshold": gap_threshold,
            "analysis_period": f"{df['t'].iloc[0].strftime('%Y-%m-%d')} to {df['t'].iloc[-1].strftime('%Y-%m-%d')}"
        }
    
    @staticmethod
    def gap_fill_analysis(price_data: List[Dict], gap_threshold: float = 0.5, 
                         fill_window: int = 5) -> Dict[str, Any]:
        """
        Analyze gap fill patterns and success rates.
        
        Args:
            price_data: List of OHLC dictionaries
            gap_threshold: Minimum gap percentage to analyze
            fill_window: Number of days to look ahead for gap fills
            
        Returns:
            Dictionary with gap fill analysis
        """
        gap_result = GapAnalyzer.identify_gaps(price_data, gap_threshold)
        if "error" in gap_result:
            return gap_result
        
        gaps = gap_result["gaps"]
        if not gaps:
            return {"error": "No significant gaps found"}
        
        df = pd.DataFrame(price_data)
        df['t'] = pd.to_datetime(df['t'])
        df = df.sort_values('t').reset_index(drop=True)
        
        gap_fills = []
        
        for gap in gaps:
            gap_index = gap["index"]
            gap_direction = gap["gap_direction"]
            fill_target = gap["prev_close"]
            
            # Look ahead for gap fill
            fill_found = False
            fill_days = 0
            partial_fill = 0
            
            for j in range(gap_index + 1, min(gap_index + fill_window + 1, len(df))):
                current_high = df.iloc[j]['h']
                current_low = df.iloc[j]['l']
                current_close = df.iloc[j]['c']
                
                if gap_direction == "up":
                    # For up gaps, check if price falls back to previous close
                    if current_low <= fill_target:
                        fill_found = True
                        fill_days = j - gap_index
                        break
                    # Calculate partial fill
                    partial_fill = max(partial_fill, (gap["open_price"] - current_low) / gap["gap_amount"])
                else:
                    # For down gaps, check if price rises back to previous close
                    if current_high >= fill_target:
                        fill_found = True
                        fill_days = j - gap_index
                        break
                    # Calculate partial fill
                    partial_fill = max(partial_fill, (current_high - gap["open_price"]) / abs(gap["gap_amount"]))
            
            partial_fill = min(1.0, max(0.0, partial_fill))  # Clamp between 0 and 1
            
            gap_fill_info = {
                **gap,
                "fill_found": fill_found,
                "fill_days": fill_days if fill_found else None,
                "partial_fill_percent": float(partial_fill * 100),
                "fill_target": float(fill_target)
            }
            gap_fills.append(gap_fill_info)
        
        # Calculate fill statistics
        filled_gaps = [g for g in gap_fills if g["fill_found"]]
        up_gap_fills = [g for g in filled_gaps if g["gap_direction"] == "up"]
        down_gap_fills = [g for g in filled_gaps if g["gap_direction"] == "down"]
        
        return {
            "gap_fills": gap_fills,
            "total_gaps": len(gap_fills),
            "filled_gaps": len(filled_gaps),
            "fill_rate": (len(filled_gaps) / len(gap_fills)) * 100 if gap_fills else 0,
            "up_gap_fill_rate": (len(up_gap_fills) / len([g for g in gap_fills if g["gap_direction"] == "up"])) * 100 if [g for g in gap_fills if g["gap_direction"] == "up"] else 0,
            "down_gap_fill_rate": (len(down_gap_fills) / len([g for g in gap_fills if g["gap_direction"] == "down"])) * 100 if [g for g in gap_fills if g["gap_direction"] == "down"] else 0,
            "avg_fill_days": float(np.mean([g["fill_days"] for g in filled_gaps])) if filled_gaps else 0,
            "avg_partial_fill": float(np.mean([g["partial_fill_percent"] for g in gap_fills])),
            "fill_window": fill_window,
            "recent_unfilled_gaps": [g for g in gap_fills[-10:] if not g["fill_found"]]
        }
    
    @staticmethod
    def gap_continuation_analysis(price_data: List[Dict], gap_threshold: float = 0.5,
                                continuation_window: int = 3) -> Dict[str, Any]:
        """
        Analyze gap continuation patterns (runaway gaps).
        
        Args:
            price_data: List of OHLC dictionaries
            gap_threshold: Minimum gap percentage to analyze
            continuation_window: Number of days to check for continuation
            
        Returns:
            Dictionary with gap continuation analysis
        """
        gap_result = GapAnalyzer.identify_gaps(price_data, gap_threshold)
        if "error" in gap_result:
            return gap_result
        
        gaps = gap_result["gaps"]
        if not gaps:
            return {"error": "No significant gaps found"}
        
        df = pd.DataFrame(price_data)
        df['t'] = pd.to_datetime(df['t'])
        df = df.sort_values('t').reset_index(drop=True)
        
        gap_continuations = []
        
        for gap in gaps:
            gap_index = gap["index"]
            gap_direction = gap["gap_direction"]
            
            # Check for continuation in the following days
            continuation_strength = 0
            continuation_days = 0
            max_favorable_move = 0
            
            for j in range(gap_index + 1, min(gap_index + continuation_window + 1, len(df))):
                if j >= len(df):
                    break
                    
                day_return = ((df.iloc[j]['c'] - df.iloc[j-1]['c']) / df.iloc[j-1]['c']) * 100
                
                if gap_direction == "up":
                    if day_return > 0:
                        continuation_strength += day_return
                        continuation_days += 1
                    max_favorable_move = max(max_favorable_move, 
                                           ((df.iloc[j]['h'] - gap["open_price"]) / gap["open_price"]) * 100)
                else:
                    if day_return < 0:
                        continuation_strength += abs(day_return)
                        continuation_days += 1
                    max_favorable_move = max(max_favorable_move, 
                                           ((gap["open_price"] - df.iloc[j]['l']) / gap["open_price"]) * 100)
            
            # Determine if gap continued
            continued = continuation_days >= continuation_window * 0.6  # 60% of days
            
            continuation_info = {
                **gap,
                "continued": continued,
                "continuation_days": continuation_days,
                "continuation_strength": float(continuation_strength),
                "max_favorable_move_percent": float(max_favorable_move),
                "continuation_quality": "Strong" if continuation_strength > abs(gap["gap_percent"]) else "Weak"
            }
            gap_continuations.append(continuation_info)
        
        # Calculate continuation statistics
        continued_gaps = [g for g in gap_continuations if g["continued"]]
        up_continuations = [g for g in continued_gaps if g["gap_direction"] == "up"]
        down_continuations = [g for g in continued_gaps if g["gap_direction"] == "down"]
        
        return {
            "gap_continuations": gap_continuations,
            "total_gaps": len(gap_continuations),
            "continued_gaps": len(continued_gaps),
            "continuation_rate": (len(continued_gaps) / len(gap_continuations)) * 100 if gap_continuations else 0,
            "up_gap_continuation_rate": (len(up_continuations) / len([g for g in gap_continuations if g["gap_direction"] == "up"])) * 100 if [g for g in gap_continuations if g["gap_direction"] == "up"] else 0,
            "down_gap_continuation_rate": (len(down_continuations) / len([g for g in gap_continuations if g["gap_direction"] == "down"])) * 100 if [g for g in gap_continuations if g["gap_direction"] == "down"] else 0,
            "avg_continuation_strength": float(np.mean([g["continuation_strength"] for g in continued_gaps])) if continued_gaps else 0,
            "continuation_window": continuation_window,
            "strong_continuations": len([g for g in continued_gaps if g["continuation_quality"] == "Strong"])
        }
    
    @staticmethod
    def island_reversal_detection(price_data: List[Dict], gap_threshold: float = 1.0) -> Dict[str, Any]:
        """
        Detect island reversal patterns (gaps in opposite directions).
        
        Args:
            price_data: List of OHLC dictionaries
            gap_threshold: Minimum gap percentage for island detection
            
        Returns:
            Dictionary with island reversal analysis
        """
        gap_result = GapAnalyzer.identify_gaps(price_data, gap_threshold)
        if "error" in gap_result:
            return gap_result
        
        gaps = gap_result["gaps"]
        if len(gaps) < 2:
            return {"error": "Need at least 2 gaps for island detection"}
        
        islands = []
        
        # Look for gaps in opposite directions within a reasonable timeframe
        for i in range(len(gaps) - 1):
            current_gap = gaps[i]
            
            # Look for opposite gap within next 10 gaps or 20 days
            for j in range(i + 1, min(i + 11, len(gaps))):
                next_gap = gaps[j]
                
                # Check if gaps are in opposite directions
                if (current_gap["gap_direction"] == "up" and next_gap["gap_direction"] == "down") or \
                   (current_gap["gap_direction"] == "down" and next_gap["gap_direction"] == "up"):
                    
                    # Check if gaps are significant and form an island
                    days_between = next_gap["index"] - current_gap["index"]
                    if days_between <= 20:  # Within reasonable timeframe
                        
                        island_info = {
                            "first_gap": current_gap,
                            "second_gap": next_gap,
                            "island_direction": "bullish" if current_gap["gap_direction"] == "up" else "bearish",
                            "days_between_gaps": days_between,
                            "island_size": abs(current_gap["gap_percent"]) + abs(next_gap["gap_percent"]),
                            "reversal_strength": "Strong" if abs(current_gap["gap_percent"]) > 2 and abs(next_gap["gap_percent"]) > 2 else "Moderate"
                        }
                        islands.append(island_info)
                        break  # Found island for this gap
        
        # Analyze island effectiveness (simplified)
        effective_islands = []
        if islands:
            df = pd.DataFrame(price_data)
            df['t'] = pd.to_datetime(df['t'])
            df = df.sort_values('t').reset_index(drop=True)
            
            for island in islands:
                second_gap_index = island["second_gap"]["index"]
                
                # Check if trend actually reversed after the island
                if second_gap_index + 5 < len(df):
                    price_before_island = island["first_gap"]["prev_close"]
                    price_after_island = df.iloc[second_gap_index + 5]['c']
                    
                    if island["island_direction"] == "bullish":
                        # For bullish island, expect price to be higher after reversal
                        effective = price_after_island < price_before_island
                    else:
                        # For bearish island, expect price to be lower after reversal
                        effective = price_after_island > price_before_island
                    
                    if effective:
                        effective_islands.append(island)
        
        return {
            "islands": islands,
            "total_islands": len(islands),
            "bullish_islands": len([i for i in islands if i["island_direction"] == "bullish"]),
            "bearish_islands": len([i for i in islands if i["island_direction"] == "bearish"]),
            "effective_islands": len(effective_islands),
            "island_effectiveness_rate": (len(effective_islands) / len(islands)) * 100 if islands else 0,
            "avg_island_size": float(np.mean([i["island_size"] for i in islands])) if islands else 0,
            "avg_days_between_gaps": float(np.mean([i["days_between_gaps"] for i in islands])) if islands else 0,
            "strong_islands": len([i for i in islands if i["reversal_strength"] == "Strong"])
        }
    
    @staticmethod
    def _classify_gap_type(row: pd.Series, gap_percent: float) -> str:
        """
        Classify gap type based on price action and gap size.
        
        Args:
            row: DataFrame row with OHLC data
            gap_percent: Gap percentage
            
        Returns:
            Gap type classification
        """
        abs_gap = abs(gap_percent)
        
        # Size-based classification
        if abs_gap >= 5:
            size_class = "large"
        elif abs_gap >= 2:
            size_class = "medium"
        else:
            size_class = "small"
        
        # Direction
        direction = "up" if gap_percent > 0 else "down"
        
        # Intraday behavior (simplified)
        daily_range = ((row['h'] - row['l']) / row['o']) * 100
        if daily_range > abs_gap * 1.5:
            behavior = "wide_range"
        else:
            behavior = "narrow_range"
        
        return f"{size_class}_{direction}_{behavior}"