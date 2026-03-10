#!/usr/bin/env python3
"""
Function Signature Pipeline

Uses function signatures as the cacheable unit instead of generic questions.
LLM matches sub-questions to existing function signatures or creates new ones.

This approach naturally increases cache hits because:
1. Similar questions map to the same function signature
2. LLM sees existing signatures and reuses them when appropriate
3. Function signatures are the cacheable unit (like MCP functions)

Usage:
    python function_pipeline.py --use-planner --use-llm --max-iterations 100
"""

import asyncio
import json
import hashlib
import os
import sys
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field
from collections import defaultdict

# Path setup
_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND = os.path.normpath(os.path.join(_DIR, "..", ".."))
_OUTPUT = os.path.join(_DIR, "output")
sys.path.insert(0, _BACKEND)

from dotenv import load_dotenv
load_dotenv(os.path.join(_BACKEND, "apiServer", ".env"))

import logging
logging.basicConfig(level=logging.WARNING, stream=sys.stderr)

logger = logging.getLogger("func-pipeline")
logger.setLevel(logging.INFO)
_handler = logging.StreamHandler(sys.stderr)
_handler.setFormatter(logging.Formatter("[func-pipeline] %(message)s"))
logger.addHandler(_handler)
logger.propagate = False


# =============================================================================
# Initial Function Registry
# =============================================================================

INITIAL_FUNCTIONS = [
    # Price & Market Data
    {"name": "get_price", "signature": "get_price(ticker: str)", "returns": ["price", "change", "change_pct"]},
    {"name": "get_quote", "signature": "get_quote(ticker: str)", "returns": ["price", "bid", "ask", "volume", "market_cap"]},
    {"name": "get_52wk_range", "signature": "get_52wk_range(ticker: str)", "returns": ["high_52w", "low_52w"]},

    # Price Trends
    {"name": "get_price_trend", "signature": "get_price_trend(ticker: str, period: str)", "returns": ["timestamps", "prices"]},
    {"name": "get_price_volume_trend", "signature": "get_price_volume_trend(ticker: str, period: str)", "returns": ["timestamps", "prices", "volumes"]},
    {"name": "get_ohlc", "signature": "get_ohlc(ticker: str, period: str)", "returns": ["open", "high", "low", "close", "volume"]},

    # Performance
    {"name": "get_returns", "signature": "get_returns(ticker: str, period: str)", "returns": ["total_return", "cagr", "volatility"]},
    {"name": "get_performance", "signature": "get_performance(ticker: str, period: str)", "returns": ["return_1d", "return_1w", "return_1m", "return_ytd", "return_1y"]},

    # Risk Metrics
    {"name": "get_risk_metrics", "signature": "get_risk_metrics(ticker: str, period: str)", "returns": ["volatility", "max_drawdown", "sharpe_ratio", "sortino_ratio"]},
    {"name": "get_beta", "signature": "get_beta(ticker: str, benchmark: str)", "returns": ["beta", "correlation", "alpha"]},
    {"name": "get_drawdown", "signature": "get_drawdown(ticker: str, period: str)", "returns": ["max_drawdown", "recovery_days", "current_drawdown"]},

    # Fundamentals
    {"name": "get_fundamentals", "signature": "get_fundamentals(ticker: str)", "returns": ["pe_ratio", "pb_ratio", "ps_ratio", "ev_ebitda", "market_cap"]},
    {"name": "get_valuation", "signature": "get_valuation(ticker: str)", "returns": ["pe_ratio", "forward_pe", "peg_ratio", "price_to_book", "price_to_sales"]},
    {"name": "get_profitability", "signature": "get_profitability(ticker: str)", "returns": ["gross_margin", "operating_margin", "net_margin", "roe", "roa"]},
    {"name": "get_financials", "signature": "get_financials(ticker: str)", "returns": ["revenue", "net_income", "eps", "free_cash_flow", "debt_to_equity"]},

    # Technicals
    {"name": "get_technicals", "signature": "get_technicals(ticker: str)", "returns": ["rsi", "macd", "sma_20", "sma_50", "sma_200"]},
    {"name": "get_moving_averages", "signature": "get_moving_averages(ticker: str)", "returns": ["sma_20", "sma_50", "sma_200", "ema_20"]},
    {"name": "get_bollinger", "signature": "get_bollinger(ticker: str)", "returns": ["upper_band", "middle_band", "lower_band", "band_width"]},
    {"name": "get_support_resistance", "signature": "get_support_resistance(ticker: str)", "returns": ["support_levels", "resistance_levels"]},

    # Comparisons
    {"name": "compare_performance", "signature": "compare_performance(tickers: list, period: str)", "returns": ["returns", "volatility", "sharpe"]},
    {"name": "compare_fundamentals", "signature": "compare_fundamentals(tickers: list)", "returns": ["pe_ratio", "pb_ratio", "market_cap", "dividend_yield"]},
    {"name": "get_correlation", "signature": "get_correlation(ticker1: str, ticker2: str, period: str)", "returns": ["correlation", "beta"]},

    # Portfolio
    {"name": "get_holdings", "signature": "get_holdings(ticker: str)", "returns": ["holdings", "weights", "sectors"]},
    {"name": "get_sector_allocation", "signature": "get_sector_allocation(ticker: str)", "returns": ["sectors", "weights"]},
    {"name": "get_top_holdings", "signature": "get_top_holdings(ticker: str, n: int)", "returns": ["holdings", "weights"]},

    # Dividends
    {"name": "get_dividend", "signature": "get_dividend(ticker: str)", "returns": ["yield", "amount", "payout_ratio", "ex_date"]},
    {"name": "get_dividend_history", "signature": "get_dividend_history(ticker: str, years: int)", "returns": ["dates", "amounts", "yields"]},

    # Options
    {"name": "get_option_chain", "signature": "get_option_chain(ticker: str)", "returns": ["calls", "puts", "implied_volatility"]},
    {"name": "get_iv_rank", "signature": "get_iv_rank(ticker: str)", "returns": ["current_iv", "iv_rank", "iv_percentile"]},

    # Backtest
    {"name": "backtest_investment", "signature": "backtest_investment(ticker: str, amount: float, years: int)", "returns": ["final_value", "total_return", "cagr"]},
]


# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class FunctionSignature:
    """A function signature that can answer questions."""
    name: str
    signature: str
    returns: List[str]
    params: List[str] = field(default_factory=list)
    block_types: List[str] = field(default_factory=list)  # Which blocks can use this
    hit_count: int = 0
    first_seen: str = ""
    last_seen: str = ""
    discovered_from: str = ""  # Original question that led to discovery

    def __post_init__(self):
        if not self.params:
            # Extract params from signature
            import re
            match = re.search(r'\(([^)]*)\)', self.signature)
            if match:
                params_str = match.group(1)
                self.params = [p.strip().split(':')[0].strip() for p in params_str.split(',') if p.strip()]
        if not self.first_seen:
            self.first_seen = datetime.now().isoformat()

    @property
    def function_key(self) -> str:
        """Unique key for this function."""
        return hashlib.sha256(f"{self.name}:{self.signature}".encode()).hexdigest()[:16]


@dataclass
class MatchResult:
    """Result of matching a question to a function."""
    action: str  # "reuse" or "create"
    function_name: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    new_signature: str = ""
    new_returns: List[str] = field(default_factory=list)
    reasoning: str = ""


@dataclass
class CacheStats:
    """Statistics for function cache."""
    total_questions: int = 0
    total_blocks: int = 0
    reuse_count: int = 0
    create_count: int = 0
    total_functions: int = 0

    @property
    def hit_rate(self) -> float:
        total = self.reuse_count + self.create_count
        return self.reuse_count / total if total > 0 else 0.0


# =============================================================================
# Function Matcher (LLM-powered)
# =============================================================================

FUNCTION_MATCHER_PROMPT = """You are a function signature matcher. Match questions to existing functions or create new ones.

RULES:
1. REUSE an existing function if it can answer the question (even partially)
2. CREATE a new function only if no existing function matches
3. Prefer functions with fewer parameters when multiple match
4. The function must return data that fits the block type

OUTPUT FORMAT (JSON only, no explanation):
For reuse: {{"action": "reuse", "function": "function_name", "params": {{"ticker": "QQQ", "period": "1y"}}}}
For create: {{"action": "create", "name": "descriptive_name", "signature": "func_name(ticker: str, param: type)", "returns": ["field1", "field2"]}}

EXAMPLES:

Question: "What is QQQ's current price?"
Block: kpi-cards
Available: get_price(ticker), get_quote(ticker), get_fundamentals(ticker)
Output: {{"action": "reuse", "function": "get_price", "params": {{"ticker": "QQQ"}}}}

Question: "What is QQQ's max drawdown and Sharpe ratio?"
Block: kpi-cards
Available: get_price(ticker), get_risk_metrics(ticker, period)
Output: {{"action": "reuse", "function": "get_risk_metrics", "params": {{"ticker": "QQQ", "period": "1y"}}}}

Question: "What is QQQ's implied volatility rank?"
Block: kpi-cards
Available: get_price(ticker), get_risk_metrics(ticker, period), get_technicals(ticker)
Output: {{"action": "create", "name": "get_iv_rank", "signature": "get_iv_rank(ticker: str)", "returns": ["current_iv", "iv_rank", "iv_percentile"]}}

NOW MATCH THIS QUESTION:

Available Functions:
{function_list}

Question: {question}
Block: {block_type}
"""


class FunctionMatcher:
    """Matches questions to function signatures using LLM."""

    def __init__(self, llm_service=None):
        self.llm_service = llm_service

    def format_function_list(self, functions: List[FunctionSignature], block_type: str = None) -> str:
        """Format function list for prompt. Optionally filter by block type."""
        lines = []
        for func in functions:
            # If block_type filter is set, only include functions that match
            if block_type and func.block_types and block_type not in func.block_types:
                continue
            returns_str = ", ".join(func.returns[:5])  # Limit returns shown
            if len(func.returns) > 5:
                returns_str += "..."
            lines.append(f"{func.signature} -> {{{returns_str}}}")
        return "\n".join(lines)

    async def match(
        self,
        question: str,
        block_type: str,
        available_functions: List[FunctionSignature],
    ) -> MatchResult:
        """Match a question to an existing function or create a new one."""

        # Format function list (just signatures, minimal)
        function_list = self.format_function_list(available_functions, block_type)

        if self.llm_service:
            content = ""
            try:
                prompt = FUNCTION_MATCHER_PROMPT.format(
                    function_list=function_list,
                    question=question,
                    block_type=block_type,
                )

                response = await self.llm_service.make_request(
                    messages=[{"role": "user", "content": prompt}],
                    system_prompt="You are a function signature matcher. Output JSON only.",
                    max_tokens=300,
                    temperature=0.1,
                )

                content = response.get("content", "").strip()
                logger.debug(f"LLM response: {content[:200]}")

                # Parse JSON
                json_start = content.find("{")
                json_end = content.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    data = json.loads(content[json_start:json_end])

                    if data.get("action") == "reuse":
                        return MatchResult(
                            action="reuse",
                            function_name=data.get("function", ""),
                            params=data.get("params", {}),
                            reasoning=data.get("reasoning", ""),
                        )
                    else:
                        return MatchResult(
                            action="create",
                            function_name=data.get("name", ""),
                            new_signature=data.get("signature", ""),
                            new_returns=data.get("returns", []),
                            reasoning=data.get("reasoning", ""),
                        )

            except Exception as e:
                logger.warning(f"LLM matching failed: {e}, response: {content[:200] if content else 'empty'}")

        # Fallback: heuristic matching
        return self._heuristic_match(question, block_type, available_functions)

    def _heuristic_match(
        self,
        question: str,
        block_type: str,
        functions: List[FunctionSignature],
    ) -> MatchResult:
        """Simple keyword-based matching as fallback."""
        question_lower = question.lower()

        # Keywords to function mapping
        keyword_map = {
            "price": ["get_price", "get_quote"],
            "trend": ["get_price_trend", "get_price_volume_trend"],
            "return": ["get_returns", "get_performance"],
            "risk": ["get_risk_metrics"],
            "drawdown": ["get_risk_metrics", "get_drawdown"],
            "sharpe": ["get_risk_metrics"],
            "volatility": ["get_risk_metrics"],
            "fundamental": ["get_fundamentals", "get_valuation"],
            "pe ratio": ["get_valuation", "get_fundamentals"],
            "market cap": ["get_quote", "get_fundamentals"],
            "technical": ["get_technicals"],
            "rsi": ["get_technicals"],
            "moving average": ["get_moving_averages"],
            "bollinger": ["get_bollinger"],
            "support": ["get_support_resistance"],
            "resistance": ["get_support_resistance"],
            "compare": ["compare_performance", "compare_fundamentals"],
            "correlation": ["get_correlation"],
            "holding": ["get_holdings", "get_top_holdings"],
            "sector": ["get_sector_allocation"],
            "dividend": ["get_dividend", "get_dividend_history"],
            "option": ["get_option_chain"],
            "implied volatility": ["get_iv_rank"],
            "iv rank": ["get_iv_rank"],
        }

        # Find matching functions
        matched_funcs = set()
        for keyword, func_names in keyword_map.items():
            if keyword in question_lower:
                matched_funcs.update(func_names)

        # Check if any matched function exists
        for func in functions:
            if func.name in matched_funcs:
                # Extract ticker from question
                import re
                ticker_match = re.search(r'\b([A-Z]{2,5})\b', question)
                params = {}
                if ticker_match:
                    params["ticker"] = ticker_match.group(1)
                if "period" in func.params:
                    params["period"] = "1y"

                return MatchResult(
                    action="reuse",
                    function_name=func.name,
                    params=params,
                    reasoning=f"Heuristic match: keyword '{keyword}' -> {func.name}",
                )

        # No match found, need to create
        return MatchResult(
            action="create",
            function_name="",
            new_signature=f"get_data(ticker: str)",
            new_returns=["data"],
            reasoning="No matching function found",
        )


# =============================================================================
# Question Bank Storage
# =============================================================================

QUESTION_BANK_FILE = os.path.join(_DIR, "question_bank.json")


class QuestionBank:
    """Persistent storage for generated questions."""

    def __init__(self, filepath: str = QUESTION_BANK_FILE):
        self.filepath = filepath
        self.questions: List[Dict[str, Any]] = []
        self.load()

    def load(self) -> None:
        """Load questions from file."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    self.questions = json.load(f)
                logger.info(f"Loaded {len(self.questions)} questions from bank")
            except Exception as e:
                logger.warning(f"Failed to load question bank: {e}")
                self.questions = []

    def save(self) -> None:
        """Save questions to file."""
        with open(self.filepath, 'w') as f:
            json.dump(self.questions, f, indent=2)
        logger.info(f"Saved {len(self.questions)} questions to bank")

    def add(self, question: str, metadata: Dict[str, Any] = None) -> None:
        """Add a question to the bank."""
        entry = {
            "question": question,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        self.questions.append(entry)

    def get_questions(self) -> List[str]:
        """Get all question strings."""
        return [q["question"] for q in self.questions]


# =============================================================================
# Question Generator (Role-based)
# =============================================================================

QUESTION_GENERATOR_PROMPT = """You are an inquisitive quantitative analyst and retail investor. You ask sophisticated, realistic questions about financial markets, portfolio management, and trading strategies.

Your questions should be:
1. Complex and multi-faceted - not just "What is X?" but exploring relationships, comparisons, and deeper insights
2. Realistic - questions a real trader/investor would ask when making decisions
3. Varied - covering different aspects: risk, performance, valuation, technicals, fundamentals, portfolio construction

PERSONAS (pick one randomly each time):
- Quantitative analyst: Focus on metrics, risk-adjusted returns, statistical analysis, factor models
- Retail trader: Focus on price action, technicals, entry/exit points, market sentiment
- Portfolio manager: Focus on allocation, diversification, rebalancing, risk management
- Options trader: Focus on implied volatility, Greeks, options strategies, hedging
- Fundamental investor: Focus on valuation, earnings quality, competitive positioning, growth

QUESTION TYPES (mix these):
1. **Performance Analysis**: "How has X performed vs benchmark Y over period Z, and what drove the outperformance/underperformance?"
2. **Risk Assessment**: "What's X's risk profile? Drawdown, volatility, Sharpe, Sortino, VaR? How does it behave in stressed markets?"
3. **Relative Value**: "X vs Y - which offers better risk-adjusted returns? Factor exposures? Valuation metrics?"
4. **Technical Setup**: "What's X's technical picture? Support/resistance, trend strength, momentum indicators, key levels?"
5. **Portfolio Construction**: "How would adding X affect my portfolio's risk/return profile? Correlation with existing holdings?"
6. **Thematic/Strategic**: "Given [market condition], how should I position? What are the implications for X?"

TICKERS TO USE NATURALLY:
- ETFs: QQQ, SPY, VOO, VTI, IWM, DIA, GLD, TLT, EEM, XLK, XLF, XLV, XLE, XLY
- Tech: AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA, AMD, INTC, CRM, ORCL
- Finance: JPM, BAC, WFC, GS, MS, BLK, V, MA, AXp, C
- Healthcare: JNJ, UNH, PFE, ABBV, LLY, MRK, TMO, ABT
- Consumer: WMT, COST, HD, NKE, MCD, SBUX
- Energy: XOM, CVX, COP
- Crypto-related: COIN, MSTR

OUTPUT FORMAT (JSON only, no explanation):
{"question": "Your complex question here?", "persona": "quant|trader|pm|options|investor", "category": "performance|risk|relative|technical|portfolio|thematic"}

Generate ONE question now."""


class QuestionGenerator:
    """Generates realistic, complex financial questions using LLM with role-playing."""

    def __init__(self, llm_service=None):
        self.llm_service = llm_service
        self.question_bank = QuestionBank()

    async def generate_one(self) -> Dict[str, Any]:
        """Generate a single complex question."""
        if self.llm_service:
            try:
                response = await self.llm_service.make_request(
                    messages=[{"role": "user", "content": QUESTION_GENERATOR_PROMPT}],
                    system_prompt="You are a sophisticated financial market participant generating realistic questions.",
                    max_tokens=500,
                    temperature=0.9,  # Higher temperature for variety
                )

                content = response.get("content", "").strip()

                # Parse JSON
                json_start = content.find("{")
                json_end = content.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    data = json.loads(content[json_start:json_end])
                    question = data.get("question", "")
                    if question:
                        self.question_bank.add(question, {
                            "persona": data.get("persona"),
                            "category": data.get("category"),
                        })
                        logger.info(f"Generated: {question[:80]}...")
                        return data

            except Exception as e:
                logger.warning(f"Question generation failed: {e}")

        # Fallback: use predefined complex questions
        fallback = self._get_fallback_question()
        self.question_bank.add(fallback["question"], {
            "persona": fallback.get("persona"),
            "category": fallback.get("category"),
        })
        return fallback

    def _get_fallback_question(self) -> Dict[str, Any]:
        """Get a random fallback question from a curated list."""
        import random

        fallback_questions = [
            # Performance Analysis
            {"question": "How has QQQ performed relative to SPY over the past 3 years on a risk-adjusted basis, and what sector exposures drove any outperformance?", "persona": "quant", "category": "performance"},
            {"question": "Compare NVDA and AMD's total return, volatility, and maximum drawdown over the past year - which offered better risk-adjusted returns?", "persona": "trader", "category": "relative"},
            {"question": "What's the correlation between QQQ and SPY over different time periods, and how has that correlation changed during market stress events?", "persona": "pm", "category": "portfolio"},

            # Risk Assessment
            {"question": "What is QQQ's Value at Risk (VaR) at 95% confidence for a 1-day horizon, and how does that compare to its 10-day VaR?", "persona": "quant", "category": "risk"},
            {"question": "Analyze TSLA's maximum drawdown characteristics over the past 5 years - what's the typical recovery time and what factors drove the worst drawdowns?", "persona": "trader", "category": "risk"},
            {"question": "What's NVDA's current volatility regime compared to its historical average, and what does its 30-day implied volatility suggest about market expectations?", "persona": "options", "category": "risk"},

            # Relative Value
            {"question": "Compare AAPL and MSFT on valuation (P/E, P/S, EV/EBITDA), growth (revenue, EPS), and profitability (margins, ROE) - which is the better value today?", "persona": "investor", "category": "relative"},
            {"question": "How do QQQ's sector weights compare to SPY, and what's the impact of those differences on performance during tech bull vs bear markets?", "persona": "pm", "category": "relative"},
            {"question": "Compare GLD and TLT on their inflation hedging properties - which has been more effective during different inflation regimes?", "persona": "investor", "category": "relative"},

            # Technical Analysis
            {"question": "What are QQQ's key support and resistance levels on the daily chart, and how does the RSI and MACD suggest momentum is evolving?", "persona": "trader", "category": "technical"},
            {"question": "Show NVDA's price relative to its 50-day and 200-day moving averages, along with Bollinger Band width - is it in a trending or mean-reverting regime?", "persona": "trader", "category": "technical"},
            {"question": "What's SPY's current advance/decline line and volume profile suggesting about market breadth and potential directional moves?", "persona": "trader", "category": "technical"},

            # Portfolio Construction
            {"question": "If I'm 60/40 stocks/bonds, how would adding a 10% allocation to QQQ affect my portfolio's expected return, volatility, and Sharpe ratio?", "persona": "pm", "category": "portfolio"},
            {"question": "What's the optimal hedge ratio for QQQ using SPY put options given current correlation and volatility levels?", "persona": "options", "category": "portfolio"},
            {"question": "How would a portfolio of QQQ, GLD, and TLT have performed during the 2022 rate hike cycle vs the 2020 COVID crash?", "persona": "pm", "category": "portfolio"},

            # Fundamental Analysis
            {"question": "What's NVDA's revenue growth trend over the past 8 quarters, and how does operating margin expansion compare to peers?", "persona": "investor", "category": "fundamental"},
            {"question": "Analyze AAPL's cash flow quality - how much of net income converts to free cash flow and what's the capital allocation strategy?", "persona": "investor", "category": "fundamental"},
            {"question": "Compare META and GOOGL on ROIC, revenue growth, and earnings quality metrics - which company is generating better returns on capital?", "persona": "investor", "category": "fundamental"},

            # Options & Volatility
            {"question": "What's QQQ's current implied volatility term structure, and where does the 30-day IV rank sit relative to its 1-year history?", "persona": "options", "category": "volatility"},
            {"question": "Analyze the risk/reward of a covered call strategy on NVDA given current implied volatility levels vs historical realized volatility", "persona": "options", "category": "volatility"},
            {"question": "What's the put/call ratio for SPY, and how has that ratio historically predicted short-term market moves?", "persona": "trader", "category": "volatility"},

            # Market Regime
            {"question": "What does the yield curve (2y-10y spread) suggest about recession risk, and how have cyclical vs defensive sectors performed historically in similar regimes?", "persona": "pm", "category": "thematic"},
            {"question": "How has market volatility (VIX) evolved over the past year, and what does the current VIX term structure suggest about near-term uncertainty?", "persona": "trader", "category": "thematic"},
        ]

        return random.choice(fallback_questions)

    async def generate_batch(self, count: int = 100) -> List[str]:
        """Generate a batch of questions one at a time."""
        questions = []

        # First, use existing questions from bank
        existing = self.question_bank.get_questions()
        if len(existing) >= count:
            logger.info(f"Using {count} questions from bank")
            return existing[:count]

        # Generate new questions
        needed = count - len(existing)
        logger.info(f"Generating {needed} new questions...")

        for _ in range(needed):
            data = await self.generate_one()
            if data.get("question"):
                questions.append(data["question"])
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.1)

        # Save to bank
        self.question_bank.save()

        # Return all questions (existing + new)
        all_questions = self.question_bank.get_questions()
        return all_questions[:count]


# =============================================================================
# Function Registry
# =============================================================================

class FunctionRegistry:
    """Manages the registry of function signatures."""

    def __init__(self, initial_functions: List[Dict] = None):
        self.functions: Dict[str, FunctionSignature] = {}
        self.stats = CacheStats()

        # Load initial functions
        if initial_functions:
            for func_data in initial_functions:
                func = FunctionSignature(
                    name=func_data["name"],
                    signature=func_data["signature"],
                    returns=func_data["returns"],
                )
                self.functions[func.name] = func

        self.stats.total_functions = len(self.functions)

    def lookup(self, function_name: str) -> Optional[FunctionSignature]:
        """Look up a function by name."""
        return self.functions.get(function_name)

    def add(self, func: FunctionSignature) -> None:
        """Add a new function to the registry."""
        if func.name not in self.functions:
            self.functions[func.name] = func
            self.stats.total_functions = len(self.functions)
            logger.info(f"Created new function: {func.signature}")

    def record_hit(self, function_name: str) -> None:
        """Record a cache hit for a function."""
        if function_name in self.functions:
            self.functions[function_name].hit_count += 1
            self.functions[function_name].last_seen = datetime.now().isoformat()
            self.stats.reuse_count += 1

    def record_miss(self) -> None:
        """Record a cache miss (new function created)."""
        self.stats.create_count += 1

    def get_all_signatures(self) -> List[FunctionSignature]:
        """Get all function signatures."""
        return list(self.functions.values())

    def get_top_functions(self, n: int = 20) -> List[FunctionSignature]:
        """Get top N functions by hit count."""
        return sorted(self.functions.values(), key=lambda f: f.hit_count, reverse=True)[:n]

    def get_report(self) -> Dict[str, Any]:
        """Generate a coverage report."""
        return {
            "stats": asdict(self.stats),
            "hit_rate": f"{self.stats.hit_rate:.1%}",
            "total_functions": len(self.functions),
            "top_functions": [
                {
                    "name": f.name,
                    "signature": f.signature,
                    "hit_count": f.hit_count,
                }
                for f in self.get_top_functions(20)
            ],
            "all_functions": [
                {
                    "name": f.name,
                    "signature": f.signature,
                    "returns": f.returns,
                    "hit_count": f.hit_count,
                    "discovered_from": f.discovered_from,
                }
                for f in self.functions.values()
            ],
        }


# =============================================================================
# Block Catalog Loader
# =============================================================================

def load_block_catalog() -> Dict[str, Any]:
    """Load the block catalog."""
    catalog_path = os.path.normpath(os.path.join(
        _DIR, "..", "..", "..",
        "frontend", "apps", "base-ui", "src", "blocks", "BLOCK_CATALOG.json"
    ))

    try:
        with open(catalog_path) as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Block catalog not found at {catalog_path}")
        return {"categories": {}}


# =============================================================================
# Main Pipeline
# =============================================================================

class FunctionPipeline:
    """Main pipeline using function signatures as cacheable units."""

    def __init__(
        self,
        ui_planner=None,
        llm_service=None,
        max_iterations: int = 1000,
    ):
        self.ui_planner = ui_planner
        self.llm_service = llm_service
        self.question_generator = QuestionGenerator(llm_service=llm_service)
        self.function_matcher = FunctionMatcher(llm_service=llm_service)
        self.registry = FunctionRegistry(initial_functions=INITIAL_FUNCTIONS)
        self.max_iterations = max_iterations
        self._question_cache: List[str] = []
        self.block_catalog = load_block_catalog()

    async def warm_question_cache(self, count: int = 100) -> None:
        """Pre-generate questions."""
        logger.info(f"Warming question cache with {count} questions...")
        self._question_cache = await self.question_generator.generate_batch(count)
        logger.info(f"Cached {len(self._question_cache)} questions")

    async def run_iteration(self, question: str) -> Dict[str, Any]:
        """Run one iteration of the pipeline."""
        result = {
            "question": question,
            "blocks": [],
            "matches": [],
        }

        # Step 1: Get UIPlanner response
        if self.ui_planner:
            try:
                plan = await self.ui_planner.plan(question)
                blocks = plan.get("blocks", [])
            except Exception as e:
                logger.warning(f"UIPlanner failed: {e}")
                blocks = self._mock_blocks(question)
        else:
            blocks = self._mock_blocks(question)

        result["blocks"] = [b.get("blockId") for b in blocks]
        self.registry.stats.total_questions += 1
        self.registry.stats.total_blocks += len(blocks)

        # Step 2: Match each block's sub-question to a function
        for block in blocks:
            sub_question = block.get("sub_question", "")
            block_type = block.get("category", "unknown")

            match_result = await self.function_matcher.match(
                question=sub_question,
                block_type=block_type,
                available_functions=self.registry.get_all_signatures(),
            )

            if match_result.action == "reuse":
                # Cache hit
                self.registry.record_hit(match_result.function_name)
                result["matches"].append({
                    "block": block.get("blockId"),
                    "action": "reuse",
                    "function": match_result.function_name,
                    "params": match_result.params,
                })
                logger.info(f"REUSE: {match_result.function_name}({match_result.params})")

            else:
                # Cache miss - create new function
                new_func = FunctionSignature(
                    name=match_result.function_name,
                    signature=match_result.new_signature,
                    returns=match_result.new_returns,
                    discovered_from=sub_question,
                )
                self.registry.add(new_func)
                self.registry.record_miss()
                result["matches"].append({
                    "block": block.get("blockId"),
                    "action": "create",
                    "function": match_result.function_name,
                    "signature": match_result.new_signature,
                    "returns": match_result.new_returns,
                })
                logger.info(f"CREATE: {match_result.new_signature}")

        return result

    def _mock_blocks(self, question: str) -> List[Dict]:
        """Generate mock blocks for testing."""
        import re

        known_tickers = {
            "QQQ", "SPY", "VOO", "VTI", "IWM", "DIA", "GLD", "TLT",
            "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA",
        }

        ticker_pattern = r'\b([A-Z]{2,5})\b'
        tickers = re.findall(ticker_pattern, question)
        tickers = [t for t in tickers if t in known_tickers]

        blocks = []

        if "compare" in question.lower():
            blocks.append({
                "blockId": "comparison-chart-01",
                "category": "comparison-chart",
                "sub_question": question,
                "dataContract": {"type": "comparison", "series": 2},
            })
        elif "trend" in question.lower() or "over" in question.lower():
            blocks.append({
                "blockId": "line-chart-01",
                "category": "line-chart",
                "sub_question": question,
                "dataContract": {"type": "timeseries"},
            })
        else:
            blocks.append({
                "blockId": "kpi-cards-01",
                "category": "kpi-cards",
                "sub_question": question,
                "dataContract": {"type": "kpi", "points": 4},
            })

        return blocks

    async def run(self, warm_cache_size: int = 100, verbose: bool = True) -> Dict[str, Any]:
        """Run the pipeline."""
        logger.info("=" * 60)
        logger.info("FUNCTION SIGNATURE PIPELINE")
        logger.info("=" * 60)
        logger.info(f"Initial functions: {len(self.registry.functions)}")
        logger.info(f"Max iterations: {self.max_iterations}")

        # Warm question cache
        if warm_cache_size > 0:
            await self.warm_question_cache(warm_cache_size)

        iteration = 0
        results = []

        while iteration < self.max_iterations and self._question_cache:
            iteration += 1
            question = self._question_cache.pop(0)

            result = await self.run_iteration(question)
            results.append(result)

            if verbose and iteration % 20 == 0:
                logger.info(
                    f"Iteration {iteration}: "
                    f"hit_rate={self.registry.stats.hit_rate:.1%}, "
                    f"functions={len(self.registry.functions)}, "
                    f"remaining={len(self._question_cache)}"
                )

        # Generate report
        report = self.registry.get_report()
        report["total_iterations"] = iteration

        return report


# =============================================================================
# CLI Entry Point
# =============================================================================

async def main():
    parser = argparse.ArgumentParser(
        description="Function Signature Pipeline - Match questions to function signatures",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--max-iterations", type=int, default=100,
                        help="Maximum iterations (default: 100)")
    parser.add_argument("--warm-cache", type=int, default=100,
                        help="Number of questions to pre-generate (default: 100)")
    parser.add_argument("--use-planner", action="store_true",
                        help="Use real UIPlanner")
    parser.add_argument("--use-llm", action="store_true",
                        help="Use LLM for matching")
    parser.add_argument("--output", type=str, default=None,
                        help="Output file for report")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose output")
    args = parser.parse_args()

    # Initialize services
    ui_planner = None
    llm_service = None

    if args.use_llm:
        from shared.llm import create_llm_service
        llm_service = create_llm_service(task="generic")
        logger.info("LLM service initialized")

    if args.use_planner:
        from shared.services.ui_planner import create_ui_planner
        ui_planner = create_ui_planner(llm_service=llm_service)
        logger.info("UIPlanner initialized")

    # Create pipeline
    pipeline = FunctionPipeline(
        ui_planner=ui_planner,
        llm_service=llm_service,
        max_iterations=args.max_iterations,
    )

    # Run
    report = await pipeline.run(
        warm_cache_size=args.warm_cache,
        verbose=args.verbose,
    )

    # Save report
    os.makedirs(_OUTPUT, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = args.output or os.path.join(_OUTPUT, f"function_pipeline_{timestamp}.json")

    with open(output_file, "w") as f:
        json.dump(report, f, indent=2, default=str)

    # Print summary
    print("\n" + "=" * 60)
    print("FINAL REPORT")
    print("=" * 60)
    print(f"Total Questions: {report['stats']['total_questions']}")
    print(f"Total Blocks: {report['stats']['total_blocks']}")
    print(f"Function Reuse: {report['stats']['reuse_count']}")
    print(f"Function Creates: {report['stats']['create_count']}")
    print(f"Hit Rate: {report['hit_rate']}")
    print(f"Total Functions: {report['total_functions']}")
    print(f"\nReport saved to: {output_file}")

    print("\n" + "-" * 60)
    print("TOP FUNCTIONS BY HIT COUNT")
    print("-" * 60)
    for i, func in enumerate(report['top_functions'][:10], 1):
        print(f"{i}. {func['signature']}")
        print(f"   Hits: {func['hit_count']}")


if __name__ == "__main__":
    asyncio.run(main())