"""
Event-driven performance analysis module for economic announcements and news.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


class EventDrivenAnalyzer:
    """Analyze performance during specific economic events and announcements."""
    
    @staticmethod
    def economic_sensitivity_analysis(price_data: List[Dict], event_dates: List[str], 
                                    event_type: str = "CPI") -> Dict[str, Any]:
        """
        Analyze performance on economic event dates.
        
        Args:
            price_data: List of OHLC dictionaries
            event_dates: List of event dates in YYYY-MM-DD format
            event_type: Type of economic event
            
        Returns:
            Dictionary with economic sensitivity analysis
        """
        if not price_data or not event_dates:
            return {"error": "Missing price data or event dates"}
        
        df = pd.DataFrame(price_data)
        df['t'] = pd.to_datetime(df['t'])
        df = df.sort_values('t').reset_index(drop=True)
        
        # Calculate daily returns
        df['daily_return'] = ((df['c'] - df['o']) / df['o']) * 100
        df['overnight_return'] = ((df['o'] - df['c'].shift(1)) / df['c'].shift(1)) * 100
        df['close_to_close_return'] = df['c'].pct_change() * 100
        df['date'] = df['t'].dt.date
        
        # Convert event dates
        event_dates_parsed = [pd.to_datetime(date).date() for date in event_dates]
        
        # Filter for event days
        event_day_mask = df['date'].isin(event_dates_parsed)
        event_day_data = df[event_day_mask].copy()
        non_event_data = df[~event_day_mask].copy()
        
        if event_day_data.empty:
            return {"error": "No price data found for event dates"}
        
        # Calculate event-day statistics
        event_returns = event_day_data['daily_return'].dropna().tolist()
        non_event_returns = non_event_data['daily_return'].dropna().tolist()
        
        # Volume analysis (if available)
        volume_multiplier = 0
        if 'v' in df.columns and not df['v'].isna().all():
            avg_volume = df['v'].mean()
            event_avg_volume = event_day_data['v'].mean() if not event_day_data['v'].isna().all() else avg_volume
            volume_multiplier = event_avg_volume / avg_volume if avg_volume > 0 else 1
        
        # Pre/post event analysis
        pre_post_analysis = EventDrivenAnalyzer._analyze_pre_post_event(df, event_dates_parsed)
        
        return {
            "event_type": event_type,
            "total_events": len(event_dates_parsed),
            "events_with_data": len(event_returns),
            "event_day_performance": {
                "avg_return": float(np.mean(event_returns)) if event_returns else 0,
                "median_return": float(np.median(event_returns)) if event_returns else 0,
                "std_return": float(np.std(event_returns)) if event_returns else 0,
                "max_return": float(max(event_returns)) if event_returns else 0,
                "min_return": float(min(event_returns)) if event_returns else 0,
                "success_rate": len([r for r in event_returns if r > 0]) / len(event_returns) * 100 if event_returns else 0
            },
            "normal_day_performance": {
                "avg_return": float(np.mean(non_event_returns)) if non_event_returns else 0,
                "std_return": float(np.std(non_event_returns)) if non_event_returns else 0,
                "success_rate": len([r for r in non_event_returns if r > 0]) / len(non_event_returns) * 100 if non_event_returns else 0
            },
            "comparative_metrics": {
                "event_outperformance": float(np.mean(event_returns) - np.mean(non_event_returns)) if event_returns and non_event_returns else 0,
                "volatility_multiplier": float(np.std(event_returns) / np.std(non_event_returns)) if event_returns and non_event_returns and np.std(non_event_returns) > 0 else 1,
                "volume_multiplier": float(volume_multiplier),
                "risk_adjusted_outperformance": float((np.mean(event_returns) - np.mean(non_event_returns)) / np.std(event_returns)) if event_returns and np.std(event_returns) > 0 else 0
            },
            "event_day_returns": event_returns,
            "pre_post_event_analysis": pre_post_analysis,
            "event_dates_analyzed": [d.strftime('%Y-%m-%d') for d in event_dates_parsed if d in df['date'].values],
            "interpretation": EventDrivenAnalyzer._interpret_event_sensitivity(
                np.mean(event_returns) if event_returns else 0,
                np.std(event_returns) / np.std(non_event_returns) if event_returns and non_event_returns and np.std(non_event_returns) > 0 else 1,
                len([r for r in event_returns if r > 0]) / len(event_returns) * 100 if event_returns else 0
            )
        }
    
    @staticmethod
    def news_sensitivity_scoring(price_data: List[Dict], news_data: Optional[List[Dict]] = None,
                               volatility_weight: float = 0.4, correlation_weight: float = 0.3,
                               sentiment_weight: float = 0.2, consistency_weight: float = 0.1) -> Dict[str, Any]:
        """
        Create news sensitivity scoring (0-10 scale).
        
        Args:
            price_data: List of OHLC dictionaries
            news_data: Optional list of news data (simplified for now)
            volatility_weight: Weight for volatility expansion component
            correlation_weight: Weight for news correlation component
            sentiment_weight: Weight for sentiment impact component
            consistency_weight: Weight for consistency metrics component
            
        Returns:
            Dictionary with news sensitivity scoring
        """
        if not price_data:
            return {"error": "No price data provided"}
        
        df = pd.DataFrame(price_data)
        df['t'] = pd.to_datetime(df['t'])
        df = df.sort_values('t').reset_index(drop=True)
        
        # Calculate daily returns and volatility
        df['daily_return'] = ((df['c'] - df['o']) / df['o']) * 100
        df['abs_return'] = df['daily_return'].abs()
        
        # Rolling volatility
        df['rolling_vol'] = df['daily_return'].rolling(window=20).std()
        
        # Identify high-volatility days (proxy for news days)
        vol_threshold = df['rolling_vol'].quantile(0.75)
        df['high_vol_day'] = df['rolling_vol'] > vol_threshold
        
        # Volatility expansion score (0-40 points)
        baseline_vol = df['daily_return'].std()
        high_vol_days_vol = df[df['high_vol_day']]['daily_return'].std()
        volatility_multiplier = high_vol_days_vol / baseline_vol if baseline_vol > 0 else 1
        
        volatility_score = min(40, (volatility_multiplier - 1) * 20)  # Scale to 0-40
        
        # News correlation score (0-30 points) - simplified without actual news data
        # Using volume as proxy for news activity
        if 'v' in df.columns and not df['v'].isna().all():
            df['volume_spike'] = df['v'] > df['v'].rolling(window=20).mean() * 1.5
            correlation_score = min(30, df[df['volume_spike']]['abs_return'].mean() * 3)
        else:
            correlation_score = 15  # Default moderate score
        
        # Sentiment impact score (0-20 points) - simplified
        # Using return asymmetry as proxy
        positive_vol = df[df['daily_return'] > 0]['daily_return'].std()
        negative_vol = df[df['daily_return'] < 0]['daily_return'].std()
        asymmetry = abs(positive_vol - negative_vol) / ((positive_vol + negative_vol) / 2) if (positive_vol + negative_vol) > 0 else 0
        sentiment_score = min(20, asymmetry * 40)
        
        # Consistency score (0-10 points)
        # Measure consistency of high volatility reactions
        high_vol_frequency = df['high_vol_day'].sum() / len(df)
        consistency_score = min(10, high_vol_frequency * 50)
        
        # Calculate final score
        final_score = (
            volatility_score * volatility_weight +
            correlation_score * correlation_weight +
            sentiment_score * sentiment_weight +
            consistency_score * consistency_weight
        )
        
        return {
            "news_sensitivity_score": float(min(10, max(0, final_score / 10))),  # Scale to 0-10
            "component_scores": {
                "volatility_expansion": float(volatility_score),
                "news_correlation": float(correlation_score),
                "sentiment_impact": float(sentiment_score),
                "consistency": float(consistency_score)
            },
            "score_weights": {
                "volatility_weight": volatility_weight,
                "correlation_weight": correlation_weight,
                "sentiment_weight": sentiment_weight,
                "consistency_weight": consistency_weight
            },
            "volatility_metrics": {
                "baseline_volatility": float(baseline_vol),
                "high_vol_day_volatility": float(high_vol_days_vol),
                "volatility_multiplier": float(volatility_multiplier)
            },
            "sensitivity_classification": EventDrivenAnalyzer._classify_news_sensitivity(final_score / 10),
            "high_volatility_days": int(df['high_vol_day'].sum()),
            "total_days": len(df)
        }
    
    @staticmethod
    def earnings_announcement_analysis(price_data: List[Dict], earnings_dates: List[str],
                                     pre_earnings_days: int = 5, post_earnings_days: int = 5) -> Dict[str, Any]:
        """
        Analyze performance around earnings announcements.
        
        Args:
            price_data: List of OHLC dictionaries
            earnings_dates: List of earnings dates
            pre_earnings_days: Days before earnings to analyze
            post_earnings_days: Days after earnings to analyze
            
        Returns:
            Dictionary with earnings performance analysis
        """
        if not price_data or not earnings_dates:
            return {"error": "Missing price data or earnings dates"}
        
        df = pd.DataFrame(price_data)
        df['t'] = pd.to_datetime(df['t'])
        df = df.sort_values('t').reset_index(drop=True)
        df['daily_return'] = df['c'].pct_change() * 100
        
        earnings_analysis = []
        
        for earnings_date in earnings_dates:
            earnings_dt = pd.to_datetime(earnings_date).date()
            earnings_idx = df[df['t'].dt.date == earnings_dt].index
            
            if len(earnings_idx) == 0:
                continue
                
            earnings_idx = earnings_idx[0]
            
            # Pre-earnings analysis
            pre_start_idx = max(0, earnings_idx - pre_earnings_days)
            pre_returns = df.iloc[pre_start_idx:earnings_idx]['daily_return'].dropna().tolist()
            
            # Post-earnings analysis (including earnings day)
            post_end_idx = min(len(df), earnings_idx + post_earnings_days + 1)
            post_returns = df.iloc[earnings_idx:post_end_idx]['daily_return'].dropna().tolist()
            
            # Earnings day specific metrics
            if earnings_idx < len(df):
                earnings_return = df.iloc[earnings_idx]['daily_return']
                earnings_volume = df.iloc[earnings_idx].get('v', 0)
                avg_volume = df['v'].mean() if 'v' in df.columns else 0
                volume_spike = earnings_volume / avg_volume if avg_volume > 0 else 1
            else:
                earnings_return = 0
                volume_spike = 1
            
            earnings_analysis.append({
                "earnings_date": earnings_date,
                "pre_earnings_returns": pre_returns,
                "post_earnings_returns": post_returns,
                "pre_earnings_avg": float(np.mean(pre_returns)) if pre_returns else 0,
                "post_earnings_avg": float(np.mean(post_returns)) if post_returns else 0,
                "earnings_day_return": float(earnings_return),
                "earnings_volume_spike": float(volume_spike),
                "pre_earnings_volatility": float(np.std(pre_returns)) if pre_returns else 0,
                "post_earnings_volatility": float(np.std(post_returns)) if post_returns else 0
            })
        
        if not earnings_analysis:
            return {"error": "No earnings data could be analyzed"}
        
        # Aggregate statistics
        all_pre_returns = [r for ea in earnings_analysis for r in ea["pre_earnings_returns"]]
        all_post_returns = [r for ea in earnings_analysis for r in ea["post_earnings_returns"]]
        earnings_day_returns = [ea["earnings_day_return"] for ea in earnings_analysis]
        
        return {
            "earnings_events": earnings_analysis,
            "total_earnings": len(earnings_analysis),
            "aggregate_performance": {
                "pre_earnings_avg": float(np.mean(all_pre_returns)) if all_pre_returns else 0,
                "post_earnings_avg": float(np.mean(all_post_returns)) if all_post_returns else 0,
                "earnings_day_avg": float(np.mean(earnings_day_returns)) if earnings_day_returns else 0,
                "pre_earnings_success_rate": len([r for r in all_pre_returns if r > 0]) / len(all_pre_returns) * 100 if all_pre_returns else 0,
                "post_earnings_success_rate": len([r for r in all_post_returns if r > 0]) / len(all_post_returns) * 100 if all_post_returns else 0
            },
            "volatility_analysis": {
                "pre_earnings_volatility": float(np.std(all_pre_returns)) if all_pre_returns else 0,
                "post_earnings_volatility": float(np.std(all_post_returns)) if all_post_returns else 0,
                "volatility_ratio": float(np.std(all_post_returns) / np.std(all_pre_returns)) if all_pre_returns and all_post_returns and np.std(all_pre_returns) > 0 else 1
            },
            "earnings_patterns": {
                "positive_earnings_days": len([r for r in earnings_day_returns if r > 0]),
                "negative_earnings_days": len([r for r in earnings_day_returns if r < 0]),
                "avg_volume_spike": float(np.mean([ea["earnings_volume_spike"] for ea in earnings_analysis]))
            }
        }
    
    @staticmethod
    def _analyze_pre_post_event(df: pd.DataFrame, event_dates: List) -> Dict[str, Any]:
        """Analyze performance before and after events."""
        pre_event_returns = []
        post_event_returns = []
        
        for event_date in event_dates:
            event_idx = df[df['date'] == event_date].index
            if len(event_idx) == 0:
                continue
            event_idx = event_idx[0]
            
            # Pre-event (1 day before)
            if event_idx > 0:
                pre_return = df.iloc[event_idx - 1]['daily_return']
                if not pd.isna(pre_return):
                    pre_event_returns.append(pre_return)
            
            # Post-event (1 day after)
            if event_idx < len(df) - 1:
                post_return = df.iloc[event_idx + 1]['daily_return']
                if not pd.isna(post_return):
                    post_event_returns.append(post_return)
        
        return {
            "pre_event_avg_return": float(np.mean(pre_event_returns)) if pre_event_returns else 0,
            "post_event_avg_return": float(np.mean(post_event_returns)) if post_event_returns else 0,
            "pre_event_success_rate": len([r for r in pre_event_returns if r > 0]) / len(pre_event_returns) * 100 if pre_event_returns else 0,
            "post_event_success_rate": len([r for r in post_event_returns if r > 0]) / len(post_event_returns) * 100 if post_event_returns else 0
        }
    
    @staticmethod
    def _interpret_event_sensitivity(avg_return: float, volatility_multiplier: float, success_rate: float) -> str:
        """Interpret event sensitivity results."""
        if avg_return > 0.5 and success_rate > 60:
            return f"Strong positive reaction to {avg_return:.1f}% avg return with {success_rate:.0f}% success rate"
        elif avg_return < -0.5 and success_rate < 40:
            return f"Strong negative reaction to {avg_return:.1f}% avg return with {success_rate:.0f}% success rate"
        elif volatility_multiplier > 2:
            return f"High volatility reaction ({volatility_multiplier:.1f}x normal) but mixed direction"
        else:
            return f"Moderate reaction with {avg_return:.1f}% avg return and {volatility_multiplier:.1f}x volatility"
    
    @staticmethod
    def _classify_news_sensitivity(score: float) -> str:
        """Classify news sensitivity based on score."""
        if score >= 7:
            return "Very High - Extremely sensitive to news and headlines"
        elif score >= 5:
            return "High - Quite sensitive to news events"
        elif score >= 3:
            return "Medium - Moderately sensitive to news"
        elif score >= 1:
            return "Low - Somewhat sensitive to major news"
        else:
            return "Very Low - Relatively insensitive to news events"