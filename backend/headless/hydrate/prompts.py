"""
Prompts for Cache Hydration Pipeline

Contains all LLM prompts used for:
- Question generation (simulating real user queries)
- Generic question generation (converting specific → parametric templates)
"""

# =============================================================================
# Question Generation Prompt
# =============================================================================

QUESTION_GENERATOR_PROMPT = """
You are a financial question generator simulating real users of a financial dashboard.
Generate diverse, realistic financial questions that users would ask.

## CATEGORIES TO COVER

### Basic Market Data
- Price queries: current price, 52-week high/low, open, close, volume
- Basic metrics: market cap, P/E ratio, dividend yield, EPS, beta

### Performance & Returns
- Period returns: 1d, 1w, 1m, 3m, 6m, YTD, 1y, 3y, 5y, 10y
- Total return, CAGR, risk-adjusted returns
- Benchmark comparisons: vs SPY, QQQ, sector indices

### Technical Analysis
- Moving averages: SMA, EMA (20, 50, 100, 200 day)
- Oscillators: RSI, MACD, Stochastic, Williams %R
- Support/resistance levels, trend lines
- Bollinger Bands, ATR, volatility indicators
- Chart patterns: head and shoulders, triangles, flags

### Fundamental Analysis
- Valuation: P/E, P/B, P/S, P/FCF, EV/EBITDA
- Profitability: margins, ROE, ROA, ROI
- Growth: revenue growth, earnings growth, EPS growth
- Financial health: debt/equity, current ratio, quick ratio
- Cash flow: operating cash flow, free cash flow, capex

### Portfolio Analysis
- Holdings breakdown, sector allocation, geographic exposure
- Top 10 holdings, concentration risk
- Portfolio performance, attribution analysis
- Rebalancing suggestions

### Risk Metrics
- Volatility: standard deviation, ATR
- Drawdown: max drawdown, recovery time
- Risk-adjusted: Sharpe ratio, Sortino ratio, Treynor ratio, Calmar ratio
- VaR (Value at Risk), CVaR
- Beta, correlation, covariance with market

### Comparisons
- Ticker vs ticker: QQQ vs SPY, NVDA vs AMD
- Ticker vs benchmark: AAPL vs SPY, QQQ vs Nasdaq
- Ticker vs sector: XLF vs financials sector
- Multiple tickers: compare 3-5 stocks side by side

### Backtesting & Strategy
- "What if I invested $X in YYY Z years ago?"
- Historical performance of a strategy
- Dollar-cost averaging vs lump sum
- Dividend reinvestment impact
- Option strategies: covered call, protective put, straddles

### Options & Derivatives
- Option chain data: calls, puts, strike prices
- Implied volatility, IV rank, IV percentile
- Greeks: delta, gamma, theta, vega
- Options flow, unusual activity
- Put/call ratios

### ETF & Fund Analysis
- Holdings analysis, expense ratios
- Tracking error, premium/discount to NAV
- Sector exposure, factor exposure
- ETF comparison

### Economic Indicators
- Interest rates: Fed funds, 10y Treasury, yield curve
- Inflation: CPI, PPI, PCE
- Employment: unemployment rate, jobless claims
- GDP, consumer sentiment, PMI

### News & Sentiment
- Recent news impact on price
- Analyst ratings, price targets
- Insider trading activity
- Social sentiment

## TICKERS TO USE

Mix these tickers naturally:
- ETFs: QQQ, SPY, VOO, VTI, IWM, DIA, GLD, TLT, EEM, IWM, XLK, XLF, XLV, XLE
- Tech: AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA, AMD, INTC, CRM, ORCL
- Finance: JPM, BAC, WFC, GS, MS, BLK, V, MA, AXp, C
- Healthcare: JNJ, UNH, PFE, ABBV, LLY, MRK, TMO, ABT
- Consumer: WMT, COST, HD, NKE, MCD, SBUX, AMZN, TGT
- Energy: XOM, CVX, COP, SLB, PSX
- Industrial: BA, CAT, HON, UPS, GE
- Crypto-related: COIN, MSTR, MARA, RIOT

## PHRASING GUIDELINES

1. Vary formality: "What's QQQ's price?" vs "What is the current price of QQQ?"
2. Mix specific and vague: "How's NVDA doing?" vs "What's NVDA's 6-month return?"
3. Include follow-up style: "Speaking of tech, how's AAPL performing?"
4. Use natural language: "Is it a good time to buy TSLA?" vs "TSLA valuation"
5. Mix complexity: Simple 1-metric queries to complex multi-part questions

## OUTPUT FORMAT

Output a JSON array of questions. No markdown, no explanation, just the JSON array.

Example output:
["Question 1?", "Question 2?", "Question 3?"]

Generate {count} diverse, realistic financial questions now:
"""


# =============================================================================
# Generic Question Generation Prompt
# =============================================================================

GENERIC_QUESTION_PROMPT = """
You are a financial question abstraction engine. Your job is to understand the UNDERLYING INTENT
of a question and create a GENERIC template that captures that intent, not just replace values.

## THE PROBLEM WE'RE SOLVING

These questions all ask for the SAME THING (risk metrics):
- "What's TSLA's max drawdown and Sharpe ratio?"
- "What are AAPL's volatility and beta?"
- "Show me NVDA's risk metrics"
- "What's MSFT's downside risk?"

They should ALL map to the SAME generic template:
"What are {{ticker}}'s risk metrics?"

## INTENT CATEGORIES

Before creating a generic template, FIRST identify the INTENT:

1. **PRICE_QUERY**: Single price value (current, 52wk high/low, etc.)
   - Intent: Get current market price
   - Generic: "What is {{ticker}}'s current price?"

2. **PERFORMANCE_QUERY**: Returns over a period
   - Intent: Get returns/performance metrics
   - Generic: "What is {{ticker}}'s performance over {{period}}?"

3. **RISK_METRICS**: Volatility, drawdown, Sharpe, Sortino, beta
   - Intent: Get risk/uncertainty measures
   - Generic: "What are {{ticker}}'s risk metrics over {{period}}?"

4. **FUNDAMENTALS**: P/E, market cap, revenue, earnings
   - Intent: Get fundamental valuation metrics
   - Generic: "What are {{ticker}}'s fundamental metrics?"

5. **TECHNICALS**: RSI, MACD, moving averages, support/resistance
   - Intent: Get technical indicator values
   - Generic: "What are {{ticker}}'s technical indicators?"

6. **COMPARISON**: Compare multiple tickers on metrics
   - Intent: Compare performance/risk/fundamentals
   - Generic: "Compare {{ticker1}} and {{ticker2}} on {{metric}} over {{period}}?"

7. **PORTFOLIO_ANALYSIS**: Holdings, allocation, exposure
   - Intent: Get portfolio composition
   - Generic: "What is {{ticker}}'s portfolio composition?"

8. **BACKTEST**: What-if investment scenarios
   - Intent: Simulate historical investment
   - Generic: "What would {{amount}} invested in {{ticker}} {{period}} ago be worth?"

9. **TREND_ANALYSIS**: Price trends, patterns over time
   - Intent: Visualize price movement
   - Generic: "What is {{ticker}}'s price trend over {{period}}?"

## BLOCK CONTEXT

Block Type: {block_type}
Block Definition:
{block_definition}

## RULES

1. **INTENT FIRST**: Identify the intent category before creating the template
2. **ABSTRACT, DON'T TRANSLITERATE**: "max drawdown and Sharpe ratio" → "risk metrics", NOT "max_drawdown and sharpe_ratio"
3. **METRICS ARE PARAMETERS**: If asking for specific metrics, use {{metrics}} parameter
4. **BLOCK-AWARE**: The generic template must fit the block's dataShape

## EXAMPLES

Input: "What's TSLA's max drawdown this year and how does its Sharpe ratio compare to QQQ?"
Block: kpi-card (expects multiple KPI values)
Intent Analysis:
  - Part 1: "TSLA's max drawdown and Sharpe ratio" → RISK_METRICS intent
  - Part 2: "compare to QQQ" → COMPARISON intent
Output:
{{
    "intent": "RISK_METRICS",
    "template": "What are {{ticker}}'s risk metrics over {{period}}?",
    "params": ["ticker", "period"],
    "metrics_included": ["max_drawdown", "sharpe_ratio"],
    "note": "User wants risk metrics; block should render max_drawdown and sharpe_ratio as KPIs"
}}

Input: "How has NVDA performed compared to SPY over 6 months?"
Block: comparison-chart (expects 2+ series for comparison)
Intent Analysis:
  - Intent: COMPARISON of performance
  - Metrics: returns/performance
Output:
{{
    "intent": "COMPARISON",
    "template": "Compare {{ticker1}} and {{ticker2}} performance over {{period}}",
    "params": ["ticker1", "ticker2", "period"],
    "metrics_included": ["total_return", "cagr"],
    "note": "User wants to compare performance; block should show both tickers' returns"
}}

Input: "What's AAPL's P/E ratio and market cap?"
Block: kpi-card (expects KPI values)
Intent Analysis:
  - Intent: FUNDAMENTALS - valuation metrics
  - Specific metrics: P/E, market cap
Output:
{{
    "intent": "FUNDAMENTALS",
    "template": "What are {{ticker}}'s valuation metrics?",
    "params": ["ticker"],
    "metrics_included": ["pe_ratio", "market_cap"],
    "note": "User wants valuation metrics; block should render P/E and market cap as KPIs"
}}

Input: "What's the current price of MSFT?"
Block: kpi-card (expects single value)
Intent Analysis:
  - Intent: PRICE_QUERY - current price
Output:
{{
    "intent": "PRICE_QUERY",
    "template": "What is {{ticker}}'s current price?",
    "params": ["ticker"],
    "metrics_included": ["price"],
    "note": "Simple price query"
}}

Input: "Show me QQQ's volatility, beta, and max drawdown over the past year"
Block: kpi-card (expects multiple KPIs)
Intent Analysis:
  - Intent: RISK_METRICS
  - All three are risk metrics
Output:
{{
    "intent": "RISK_METRICS",
    "template": "What are {{ticker}}'s risk metrics over {{period}}?",
    "params": ["ticker", "period"],
    "metrics_included": ["volatility", "beta", "max_drawdown"],
    "note": "User wants comprehensive risk metrics"
}}

## YOUR TASK

Specific Question: {sub_question}
Block Type: {block_type}
Block Contract: {data_contract}

First, analyze the INTENT. Then create a GENERIC template that captures that intent.
Output JSON format:
{{
    "intent": "INTENT_CATEGORY",
    "template": "the generic question capturing the intent",
    "params": ["list", "of", "parameter", "names"],
    "metrics_included": ["specific", "metrics", "mentioned"],
    "output_shape": "description matching the block's dataShape",
    "note": "brief explanation of intent analysis"
}}
"""


# =============================================================================
# Block Context Prompt (for determining block type from question)
# =============================================================================

BLOCK_CONTEXT_PROMPT = """
Given a financial question, determine the best block type to display the answer.

## AVAILABLE BLOCKS

{block_catalog}

## RULES

1. Choose the block whose `bestFor` description matches the question's intent
2. Consider the data type: single value → kpi-card, time series → line-chart, comparison → comparison-chart
3. Check `avoidWhen` to make sure the block is appropriate

## OUTPUT

Output JSON with:
{{
    "block_type": "the block id (e.g., 'kpi-card-01', 'line-chart')",
    "data_contract": {{appropriate data contract for the block}},
    "reasoning": "brief explanation referencing bestFor"
}}

Question: {question}
"""


# =============================================================================
# System Prompts by Use Case
# =============================================================================

SYSTEM_PROMPTS = {
    "question_generator": {
        "role": "You are a financial question generator that simulates real user queries.",
        "task": "Generate diverse, realistic financial questions that users would ask a financial dashboard.",
        "context": "Cover all categories: basic data, technicals, fundamentals, portfolio, risk, comparisons, backtesting, options, ETFs, economics, and sentiment.",
    },
    "generic_question": {
        "role": "You are a financial question parameterizer.",
        "task": "Convert specific financial questions into generic, reusable templates.",
        "context": "The template must produce output that fits the block's dataShape.",
    },
    "block_selector": {
        "role": "You are a dashboard block selector.",
        "task": "Choose the best block type to display the answer to a financial question.",
        "context": "Match the question's intent to the block's bestFor description.",
    },
}