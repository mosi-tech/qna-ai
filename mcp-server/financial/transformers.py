"""
Data Transformation Utilities for Vendor Mapping

This module provides utilities to transform data between vendor-specific formats
and the standardized schemas. Each vendor has its own transformer class that
handles mapping to/from the standard format.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from .schemas import (
    StandardBar, StandardQuote, StandardTrade, StandardSnapshot, 
    StandardScreenerResult, StandardNewsArticle, StandardFundamentals,
    StandardDividend, StandardSplit, StandardPosition, StandardAccount,
    StandardOrder, SymbolFormatter
)


class AlpacaTransformer:
    """Transform data between Alpaca format and standard format."""
    
    @staticmethod
    def transform_bars(alpaca_data: Dict[str, Any], symbols: List[str]) -> List[StandardBar]:
        """Transform Alpaca bars response to standard format."""
        if "bars" not in alpaca_data:
            return []
        
        standard_bars = []
        for symbol, bars in alpaca_data["bars"].items():
            std_symbol = SymbolFormatter.to_standard(symbol, "alpaca")
            for bar in bars:
                standard_bars.append(StandardBar(
                    timestamp=bar["t"],
                    symbol=std_symbol,
                    open=float(bar["o"]),
                    high=float(bar["h"]),
                    low=float(bar["l"]),
                    close=float(bar["c"]),
                    volume=int(bar["v"]),
                    vwap=float(bar.get("vw", 0)) if bar.get("vw") else None,
                    trade_count=int(bar.get("n", 0)) if bar.get("n") else None
                ))
        return standard_bars
    
    @staticmethod
    def transform_snapshots(alpaca_data: Dict[str, Any]) -> List[StandardSnapshot]:
        """Transform Alpaca snapshots to standard format."""
        if "snapshots" not in alpaca_data:
            return []
        
        snapshots = []
        for symbol, snapshot in alpaca_data["snapshots"].items():
            std_symbol = SymbolFormatter.to_standard(symbol, "alpaca")
            
            # Transform latest trade
            latest_trade = None
            if "latestTrade" in snapshot:
                trade_data = snapshot["latestTrade"]
                latest_trade = StandardTrade(
                    timestamp=trade_data["t"],
                    symbol=std_symbol,
                    price=float(trade_data["p"]),
                    size=int(trade_data["s"])
                )
            
            # Transform latest quote
            latest_quote = None
            if "latestQuote" in snapshot:
                quote_data = snapshot["latestQuote"]
                latest_quote = StandardQuote(
                    timestamp=quote_data["t"],
                    symbol=std_symbol,
                    bid_price=float(quote_data["bp"]),
                    bid_size=int(quote_data["bs"]),
                    ask_price=float(quote_data["ap"]),
                    ask_size=int(quote_data["as"])
                )
            
            # Transform daily bar
            daily_bar = None
            if "dailyBar" in snapshot:
                bar_data = snapshot["dailyBar"]
                daily_bar = StandardBar(
                    timestamp=bar_data["t"],
                    symbol=std_symbol,
                    open=float(bar_data["o"]),
                    high=float(bar_data["h"]),
                    low=float(bar_data["l"]),
                    close=float(bar_data["c"]),
                    volume=int(bar_data["v"])
                )
            
            # Get previous close
            previous_close = None
            if "prevDailyBar" in snapshot:
                previous_close = float(snapshot["prevDailyBar"]["c"])
            
            snapshots.append(StandardSnapshot(
                symbol=std_symbol,
                timestamp=datetime.now().isoformat(),
                latest_trade=latest_trade,
                latest_quote=latest_quote,
                daily_bar=daily_bar,
                previous_close=previous_close
            ))
        
        return snapshots
    
    @staticmethod
    def transform_quotes(alpaca_data: Dict[str, Any]) -> List[StandardQuote]:
        """Transform Alpaca quotes to standard format."""
        if "quotes" not in alpaca_data:
            return []
        
        quotes = []
        for symbol, quote in alpaca_data["quotes"].items():
            std_symbol = SymbolFormatter.to_standard(symbol, "alpaca")
            quotes.append(StandardQuote(
                timestamp=quote["t"],
                symbol=std_symbol,
                bid_price=float(quote["bp"]),
                bid_size=int(quote["bs"]),
                ask_price=float(quote["ap"]),
                ask_size=int(quote["as"])
            ))
        return quotes
    
    @staticmethod
    def transform_trades(alpaca_data: Dict[str, Any]) -> List[StandardTrade]:
        """Transform Alpaca trades to standard format."""
        if "trades" not in alpaca_data:
            return []
        
        trades = []
        for symbol, trade in alpaca_data["trades"].items():
            std_symbol = SymbolFormatter.to_standard(symbol, "alpaca")
            trades.append(StandardTrade(
                timestamp=trade["t"],
                symbol=std_symbol,
                price=float(trade["p"]),
                size=int(trade["s"]),
                exchange=trade.get("x")
            ))
        return trades
    
    @staticmethod
    def transform_screener(alpaca_data: Dict[str, Any], screener_type: str) -> List[StandardScreenerResult]:
        """Transform Alpaca screener results to standard format."""
        data_key = {
            "most_actives": "most_actives",
            "top_gainers": "top_gainers", 
            "top_losers": "top_losers"
        }.get(screener_type)
        
        if not data_key or data_key not in alpaca_data:
            return []
        
        results = []
        for item in alpaca_data[data_key]:
            std_symbol = SymbolFormatter.to_standard(item["symbol"], "alpaca")
            results.append(StandardScreenerResult(
                symbol=std_symbol,
                name=item.get("name", std_symbol),
                price=float(item["price"]),
                change=float(item["change"]),
                change_percent=float(item["percent_change"]),
                volume=int(item["volume"])
            ))
        return results
    
    @staticmethod
    def transform_news(alpaca_data: Dict[str, Any]) -> List[StandardNewsArticle]:
        """Transform Alpaca news to standard format."""
        if "news" not in alpaca_data:
            return []
        
        articles = []
        for article in alpaca_data["news"]:
            symbols = [SymbolFormatter.to_standard(s, "alpaca") for s in article.get("symbols", [])]
            articles.append(StandardNewsArticle(
                id=article["id"],
                headline=article["headline"],
                summary=article.get("summary"),
                content=article.get("content"),
                symbols=symbols,
                published_at=article["created_at"],
                source=article.get("source", "Alpaca"),
                url=article.get("url")
            ))
        return articles
    
    @staticmethod
    def transform_positions(alpaca_data: List[Dict[str, Any]]) -> List[StandardPosition]:
        """Transform Alpaca positions to standard format."""
        positions = []
        for pos in alpaca_data:
            std_symbol = SymbolFormatter.to_standard(pos["symbol"], "alpaca")
            positions.append(StandardPosition(
                symbol=std_symbol,
                quantity=float(pos["qty"]),
                side=pos["side"],
                avg_entry_price=float(pos["avg_entry_price"]),
                current_price=float(pos["current_price"]),
                market_value=float(pos["market_value"]),
                cost_basis=float(pos["cost_basis"]),
                unrealized_pnl=float(pos["unrealized_pl"]),
                unrealized_pnl_percent=float(pos["unrealized_plpc"])
            ))
        return positions
    
    @staticmethod
    def transform_account(alpaca_data: Dict[str, Any]) -> StandardAccount:
        """Transform Alpaca account to standard format."""
        return StandardAccount(
            account_id=alpaca_data["id"],
            status=alpaca_data["status"],
            currency=alpaca_data["currency"],
            cash=float(alpaca_data["cash"]),
            buying_power=float(alpaca_data["buying_power"]),
            portfolio_value=float(alpaca_data["portfolio_value"]),
            equity=float(alpaca_data["equity"]),
            initial_margin=float(alpaca_data.get("initial_margin", 0)),
            maintenance_margin=float(alpaca_data.get("maintenance_margin", 0)),
            is_pattern_day_trader=alpaca_data.get("pattern_day_trader", False)
        )


class EODHDTransformer:
    """Transform data between EODHD format and standard format."""
    
    @staticmethod
    def transform_eod_data(eodhd_data: List[Dict[str, Any]], symbol: str) -> List[StandardBar]:
        """Transform EODHD EOD data to standard format."""
        if not eodhd_data or isinstance(eodhd_data, dict):
            return []
        
        std_symbol = SymbolFormatter.to_standard(symbol, "eodhd")
        bars = []
        for bar in eodhd_data:
            # Convert date to ISO timestamp
            date_str = bar["date"]
            timestamp = f"{date_str}T00:00:00Z"
            
            bars.append(StandardBar(
                timestamp=timestamp,
                symbol=std_symbol,
                open=float(bar["open"]),
                high=float(bar["high"]),
                low=float(bar["low"]),
                close=float(bar["close"]),
                volume=int(bar["volume"])
            ))
        return bars
    
    @staticmethod
    def transform_real_time(eodhd_data: Dict[str, Any], symbol: str) -> StandardSnapshot:
        """Transform EODHD real-time data to standard format."""
        std_symbol = SymbolFormatter.to_standard(symbol, "eodhd")
        
        # Create a basic snapshot from real-time data
        timestamp = datetime.now().isoformat()
        
        daily_bar = StandardBar(
            timestamp=timestamp,
            symbol=std_symbol,
            open=float(eodhd_data.get("open", 0)),
            high=float(eodhd_data.get("high", 0)),
            low=float(eodhd_data.get("low", 0)),
            close=float(eodhd_data.get("close", 0)),
            volume=int(eodhd_data.get("volume", 0))
        )
        
        return StandardSnapshot(
            symbol=std_symbol,
            timestamp=timestamp,
            daily_bar=daily_bar,
            previous_close=float(eodhd_data.get("previousClose", 0))
        )
    
    @staticmethod
    def transform_fundamentals(eodhd_data: Dict[str, Any], symbol: str) -> StandardFundamentals:
        """Transform EODHD fundamentals to standard format."""
        std_symbol = SymbolFormatter.to_standard(symbol, "eodhd")
        general = eodhd_data.get("General", {})
        highlights = eodhd_data.get("Highlights", {})
        valuation = eodhd_data.get("Valuation", {})
        
        return StandardFundamentals(
            symbol=std_symbol,
            company_name=general.get("Name", ""),
            sector=general.get("Sector"),
            industry=general.get("Industry"),
            market_cap=float(general.get("MarketCapitalization", 0)) if general.get("MarketCapitalization") else None,
            pe_ratio=float(highlights.get("PERatio", 0)) if highlights.get("PERatio") else None,
            pb_ratio=float(highlights.get("PriceBookMRQ", 0)) if highlights.get("PriceBookMRQ") else None,
            dividend_yield=float(highlights.get("DividendYield", 0)) if highlights.get("DividendYield") else None,
            eps=float(highlights.get("EarningsShare", 0)) if highlights.get("EarningsShare") else None,
            revenue=float(highlights.get("RevenueTTM", 0)) if highlights.get("RevenueTTM") else None,
            shares_outstanding=int(general.get("SharesOutstanding", 0)) if general.get("SharesOutstanding") else None
        )
    
    @staticmethod
    def transform_dividends(eodhd_data: List[Dict[str, Any]], symbol: str) -> List[StandardDividend]:
        """Transform EODHD dividends to standard format."""
        if not eodhd_data or isinstance(eodhd_data, dict):
            return []
        
        std_symbol = SymbolFormatter.to_standard(symbol, "eodhd")
        dividends = []
        for div in eodhd_data:
            dividends.append(StandardDividend(
                symbol=std_symbol,
                ex_date=div["date"],
                payment_date=div.get("paymentDate", div["date"]),
                record_date=div.get("recordDate"),
                declaration_date=div.get("declarationDate"),
                amount=float(div["value"]),
                currency=div.get("currency", "USD")
            ))
        return dividends
    
    @staticmethod
    def transform_splits(eodhd_data: List[Dict[str, Any]], symbol: str) -> List[StandardSplit]:
        """Transform EODHD splits to standard format."""
        if not eodhd_data or isinstance(eodhd_data, dict):
            return []
        
        std_symbol = SymbolFormatter.to_standard(symbol, "eodhd")
        splits = []
        for split in eodhd_data:
            splits.append(StandardSplit(
                symbol=std_symbol,
                date=split["date"],
                ratio=split["split"],
                split_factor=float(split.get("splitCoefficient", 1.0))
            ))
        return splits
    
    @staticmethod
    def transform_screener(eodhd_data: List[Dict[str, Any]]) -> List[StandardScreenerResult]:
        """Transform EODHD screener results to standard format."""
        if not eodhd_data or isinstance(eodhd_data, dict):
            return []
        
        results = []
        for item in eodhd_data:
            std_symbol = SymbolFormatter.to_standard(item["code"], "eodhd")
            results.append(StandardScreenerResult(
                symbol=std_symbol,
                name=item.get("name", std_symbol),
                price=float(item.get("price", 0)),
                change=float(item.get("change", 0)),
                change_percent=float(item.get("change_p", 0)),
                volume=int(item.get("volume", 0)),
                market_cap=float(item.get("market_cap", 0)) if item.get("market_cap") else None
            ))
        return results


def handle_vendor_error(vendor_response: Dict[str, Any], vendor_name: str) -> Dict[str, Any]:
    """Handle and standardize vendor error responses."""
    if isinstance(vendor_response, dict) and "error" in vendor_response:
        return {
            "success": False,
            "data": None,
            "error": f"{vendor_name}: {vendor_response['error']}"
        }
    return vendor_response


def ensure_standard_response(data: Any, success: bool = True, error: str = None) -> Dict[str, Any]:
    """Ensure response follows standard format."""
    return {
        "success": success,
        "data": data if success else None,
        "error": error if not success else None
    }