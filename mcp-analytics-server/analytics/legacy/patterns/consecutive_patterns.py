"""
Consecutive pattern analysis for identifying consecutive up/down days and rebounds.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any


class ConsecutivePatternAnalyzer:
    """Analyze consecutive up/down patterns in price data."""
    
    @staticmethod
    def identify_consecutive_patterns(price_data: List[Dict], min_sequence_length: int = 3) -> Dict[str, Any]:
        """
        Identify consecutive up/down day patterns.
        
        Args:
            price_data: List of OHLC dictionaries with 't', 'o', 'h', 'l', 'c' keys
            min_sequence_length: Minimum consecutive days to identify
            
        Returns:
            Dictionary with consecutive patterns analysis
        """
        if not price_data or len(price_data) < min_sequence_length:
            return {"error": "Insufficient data for pattern analysis"}
        
        df = pd.DataFrame(price_data)
        df['t'] = pd.to_datetime(df['t'])
        df = df.sort_values('t').reset_index(drop=True)
        
        # Calculate daily returns (open to close)
        df['daily_return'] = ((df['c'] - df['o']) / df['o']) * 100
        df['direction'] = np.where(df['daily_return'] > 0, 1, -1)  # 1 for up, -1 for down
        
        # Find sequences of consecutive days
        df['direction_change'] = df['direction'] != df['direction'].shift(1)
        df['sequence_id'] = df['direction_change'].cumsum()
        
        # Group by sequences
        sequences = df.groupby('sequence_id').agg({
            'direction': 'first',
            'daily_return': ['count', 'mean', 'sum'],
            't': ['first', 'last'],
            'o': 'first',
            'c': 'last'
        }).reset_index()
        
        # Flatten column names
        sequences.columns = ['sequence_id', 'direction', 'length', 'avg_return', 'total_return', 'start_date', 'end_date', 'start_price', 'end_price']
        
        # Filter for sequences meeting minimum length
        long_sequences = sequences[sequences['length'] >= min_sequence_length]
        
        # Separate up and down sequences
        up_sequences = long_sequences[long_sequences['direction'] == 1].copy()
        down_sequences = long_sequences[long_sequences['direction'] == -1].copy()
        
        # Calculate sequence statistics
        up_patterns = []
        for _, row in up_sequences.iterrows():
            up_patterns.append({
                "sequence_length": int(row['length']),
                "direction": "up",
                "avg_daily_return": row['avg_return'],
                "total_sequence_return": row['total_return'],
                "start_date": row['start_date'].strftime('%Y-%m-%d'),
                "end_date": row['end_date'].strftime('%Y-%m-%d'),
                "price_change_percent": ((row['end_price'] - row['start_price']) / row['start_price']) * 100
            })
        
        down_patterns = []
        for _, row in down_sequences.iterrows():
            down_patterns.append({
                "sequence_length": int(row['length']),
                "direction": "down",
                "avg_daily_return": row['avg_return'],
                "total_sequence_return": row['total_return'],
                "start_date": row['start_date'].strftime('%Y-%m-%d'),
                "end_date": row['end_date'].strftime('%Y-%m-%d'),
                "price_change_percent": ((row['end_price'] - row['start_price']) / row['start_price']) * 100
            })
        
        return {
            "min_sequence_length": min_sequence_length,
            "total_patterns_found": len(long_sequences),
            "up_patterns": up_patterns,
            "down_patterns": down_patterns,
            "up_pattern_count": len(up_patterns),
            "down_pattern_count": len(down_patterns),
            "avg_up_sequence_length": up_sequences['length'].mean() if len(up_sequences) > 0 else 0,
            "avg_down_sequence_length": down_sequences['length'].mean() if len(down_sequences) > 0 else 0,
            "longest_up_sequence": int(up_sequences['length'].max()) if len(up_sequences) > 0 else 0,
            "longest_down_sequence": int(down_sequences['length'].max()) if len(down_sequences) > 0 else 0
        }
    
    @staticmethod
    def analyze_rebound_after_down_days(price_data: List[Dict], down_day_threshold: int = 3, 
                                       rebound_days: int = 5) -> Dict[str, Any]:
        """
        Analyze rebounds after consecutive down days.
        
        Args:
            price_data: List of OHLC dictionaries
            down_day_threshold: Number of consecutive down days to trigger analysis
            rebound_days: Number of days to analyze for rebound
            
        Returns:
            Dictionary with rebound analysis
        """
        if not price_data or len(price_data) < down_day_threshold + rebound_days:
            return {"error": "Insufficient data for rebound analysis"}
        
        df = pd.DataFrame(price_data)
        df['t'] = pd.to_datetime(df['t'])
        df = df.sort_values('t').reset_index(drop=True)
        
        # Calculate daily returns
        df['daily_return'] = df['c'].pct_change() * 100
        df['is_down_day'] = df['daily_return'] < -0.5  # At least 0.5% decline
        
        # Find consecutive down periods
        rebounds = []
        for i in range(len(df) - down_day_threshold - rebound_days):
            # Check if we have enough consecutive down days
            consecutive_down = True
            for j in range(down_day_threshold):
                if not df.iloc[i + j]['is_down_day']:
                    consecutive_down = False
                    break
            
            if consecutive_down:
                # Calculate rebound performance
                start_price = df.iloc[i + down_day_threshold - 1]['c']  # Price at end of down period
                rebound_returns = []
                
                for k in range(1, min(rebound_days + 1, len(df) - (i + down_day_threshold - 1))):
                    if i + down_day_threshold - 1 + k < len(df):
                        future_price = df.iloc[i + down_day_threshold - 1 + k]['c']
                        rebound_return = ((future_price - start_price) / start_price) * 100
                        rebound_returns.append(rebound_return)
                
                if rebound_returns:
                    rebounds.append({
                        "down_period_start": df.iloc[i]['t'].strftime('%Y-%m-%d'),
                        "down_period_end": df.iloc[i + down_day_threshold - 1]['t'].strftime('%Y-%m-%d'),
                        "down_period_return": ((df.iloc[i + down_day_threshold - 1]['c'] - df.iloc[i]['c']) / df.iloc[i]['c']) * 100,
                        "rebound_returns": rebound_returns,
                        "max_rebound": max(rebound_returns),
                        "final_rebound": rebound_returns[-1] if rebound_returns else 0
                    })
        
        if not rebounds:
            return {
                "down_day_threshold": down_day_threshold,
                "rebound_days": rebound_days,
                "patterns_found": 0,
                "message": "No qualifying down periods found"
            }
        
        # Calculate statistics
        all_max_rebounds = [r['max_rebound'] for r in rebounds]
        all_final_rebounds = [r['final_rebound'] for r in rebounds]
        successful_rebounds = [r for r in all_final_rebounds if r > 0]
        
        return {
            "down_day_threshold": down_day_threshold,
            "rebound_days": rebound_days,
            "patterns_found": len(rebounds),
            "rebounds": rebounds[:10],  # Limit to first 10
            "avg_max_rebound": np.mean(all_max_rebounds),
            "avg_final_rebound": np.mean(all_final_rebounds),
            "success_rate": len(successful_rebounds) / len(rebounds) * 100,
            "best_rebound": max(all_max_rebounds),
            "worst_rebound": min(all_final_rebounds)
        }