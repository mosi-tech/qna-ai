# Pattern Recognition in Function Gap Analysis

## Common False Positives

These functions EXIST in MCP but are often incorrectly flagged as gaps:

| Incorrect Gap Name | Actual MCP Function | Reason for Confusion |
|-------------------|---------------------|---------------------|
| expected_shortfall | `calculate_expected_shortfall` | Also called CVaR |
| dividend_yield | `calculate_dividend_yield` | Semantic naming difference |
| beta | `calculate_beta` | Basic function name |
| risk_parity | `calculate_risk_parity` | Semantic naming |
| market_regime | `detect_market_regime` | Multiple aliases |
| cvar | `calculate_cvar` | Alias for expected shortfall |

## Question Pattern Analysis

### Questions That Don't Match Any Function (37.05%)

These questions require:
1. **Composite logic** - Combining multiple MCP functions
2. **Human interpretation** - Subjective judgments
3. **Domain knowledge** - Investment advice, tax planning
4. **External data** - Not available via current MCP providers

Examples:
- "Is now a good time to invest in gold?" - Subjective
- "What tax strategies should I use?" - Requires tax expertise
- "Will AAPL stock go up tomorrow?" - Prediction (not analysis)

### High-Frequency Questions

Questions that appear frequently (>20 times) and indicate important user needs:

1. **Risk Analysis** - Risk metrics, drawdowns, volatility
2. **Portfolio Performance** - Returns, comparison to benchmarks
3. **Technical Analysis** - Moving averages, indicators, patterns
4. **Fundamental Analysis** - P/E, ROE, ROA, margins
5. **Options Trading** - Greeks, IV, spreads, strategies

### Domain Distribution

| Domain | Question Count | Percentage |
|--------|----------------|------------|
| Account/Portfolio | 227 | 12.5% |
| Technical Analysis | ~400 | 22.1% |
| Risk Analysis | ~200 | 11.0% |
| Fundamental Analysis | ~150 | 8.3% |
| Options/Derivatives | ~100 | 5.5% |
| Market Analysis | ~80 | 4.4% |
| Unknown/Other | ~656 | 36.2% |

## Function Naming Patterns

### MCP Function Naming Convention
- **Calculation**: `calculate_{metric}` (e.g., `calculate_beta`, `calculate_sharpe_ratio`)
- **Detection**: `detect_{pattern}` (e.g., `detect_sma_crossover`, `detect_market_regime`)
- **Analysis**: `analyze_{topic}` (e.g., `analyze_seasonality`, `analyze_leverage_fund`)
- **Optimization**: `optimize_{objective}` (e.g., `optimize_max_sharpe`, `optimize_portfolio`)

### Missing Function Naming Convention
- Follow MCP convention for consistency
- Use descriptive names
- Avoid abbreviations (e.g., use `calculate_earnings_per_share` not `calculate_eps`)

## Data Availability Matrix

| Data Type | Available via MCP | Gaps Identified |
|-----------|------------------|-----------------|
| Historical prices | Yes (`get_historical_data`) | None |
| Real-time prices | Yes (`get_real_time_data`) | None |
| Fundamentals | Yes (`get_fundamentals`) | Calculation functions needed |
| Dividends | Yes (`get_dividends`) | None |
| Splits | Yes (`get_splits`) | None |
| Market news | Yes (`get_market_news`) | Sentiment scoring needed |
| Options data | Limited | Greeks, IV surface, open interest |
| Futures data | Limited | Futures curve, contango/backwardation |
| Sentiment data | Limited | N/A |
| Economic indicators | Limited | N/A |

## Implementation Complexity

### Easy (1-2 hours)
- Fundamental ratio calculators
- Basic technical indicators (TRIX, Keltner)
- Performance ratios (alpha, tracking error)
- ADV calculation

### Medium (3-5 hours)
- Pattern recognition (candlestick, flag)
- Calendar effects (options expiration, earnings season)
- Market microstructure (bid-ask spread, turnover)
- Statistical tests (ADF, cointegration)

### Hard (1-3 days)
- Options analytics (IV surface, greeks chain)
- Futures analysis (curve, contango/backwardation)
- Sentiment analysis (NLP integration)
- Forecasting models (ARIMA, exponential smoothing)
- Advanced patterns (head & shoulders, wedge)

### Very Hard (1+ weeks)
- Machine learning models (HMM, neural networks)
- Real-time market regime detection
- Multi-factor attribution
- Complex optimization (Black-Litterman)

## Question Complexity Levels

### Level 1: Single Function (Atomic)
- "Calculate the 20-day SMA for AAPL"
- → `calculate_sma(data, period=20)`

### Level 2: 2-3 Functions (Simple Composite)
- "Find all stocks with RSI < 30"
- → `get_exchange_symbols()` + `calculate_rsi()` + filter

### Level 3: 3-5 Functions (Complex)
- "Backtest a golden cross strategy with transaction costs"
- → Multiple functions chained together

### Level 4: 5+ Functions + Logic (Advanced)
- "Compare my portfolio's performance across bull and bear market regimes"
- → Complex workflow with conditional logic

### Level 5: Non-Deterministic (Subjective)
- "Is now a good time to buy tech stocks?"
- → Requires human judgment, not just calculation

## Semantic Matching Heuristics

When checking if a function exists:

1. **Exact match first** - e.g., `calculate_beta`
2. **Alias check** - e.g., `beta` → `calculate_beta`
3. **Semantic match** - e.g., "risk adjusted return" → `calculate_sharpe_ratio`
4. **Composition check** - Can it be built from existing functions?
5. **External data check** - Is data available but function missing?

## Priority Assignment Rules

- **HIGH**: Frequency > 20 OR appears in multiple domains
- **MEDIUM**: Frequency 5-20 OR single domain
- **LOW**: Frequency < 5 OR rare use case
- **DEFER**: Requires new data source OR non-deterministic

## Recurring Themes

### Theme 1: Risk Management
- Users care deeply about downside risk
- Want to understand drawdowns, tail risk, stress scenarios
- Questions appear across all market conditions

### Theme 2: Benchmark Comparison
- Users want to know "am I beating the market?"
- Alpha, beta, tracking error are high-priority gaps
- Comparison to SPY, QQQ are common

### Theme 3: Technical Pattern Recognition
- Users want to identify actionable patterns
- Candlestick, continuation patterns, reversal patterns
- Pattern frequency analysis is common

### Theme 4: Fundamental Valuation
- Users want to know "is this stock cheap?"
- P/E, PEG, EV/EBITDA are standard metrics
- Valuation relative to sector/industry is important

### Theme 5: Options Trading
- Advanced users need options analytics
- Greeks, IV surface, skew are essential
- Options flow and positioning are emerging themes

## User Expertise Levels

### Beginner
- Basic questions: "What is my account balance?"
- Simple indicators: SMA, basic patterns
- Needs guidance and education

### Intermediate
- Risk management questions
- Portfolio optimization
- Multiple indicators combined

### Advanced
- Complex options strategies
- Statistical analysis
- Machine learning models
- Quantitative strategies

### Institutional
- Transaction cost analysis
- Large-scale backtesting
- Risk parity, factor models
- Attribution analysis

## Data Frequency Requirements

| Analysis | Required Data Frequency | Available? |
|----------|------------------------|------------|
| Intraday (VWAP) | Minute-level | No (currently) |
| Daily analysis | Daily | Yes |
| Weekly analysis | Weekly | Yes (via resample) |
| Monthly analysis | Monthly | Yes (via resample) |
| Quarterly analysis | Quarterly | Yes (via resample) |
| Annual analysis | Annual | Yes (via resample) |
| Real-time | Streaming | Partial (get_real_time_data) |

## Integration Patterns

### Sequential Function Calls
```python
# Get data → Calculate indicator → Detect signal → Backtest
prices = get_historical_data(symbols=['AAPL'])
sma = calculate_sma(prices, period=20)
crossovers = detect_sma_crossover(prices)
performance = backtest_strategy(prices, signals=crossovers)
```

### Parallel Function Calls
```python
# Calculate multiple indicators in parallel
sma = calculate_sma(prices, period=20)
ema = calculate_ema(prices, period=20)
rsi = calculate_rsi(prices, period=14)
# All independent, can be called in parallel
```

### Conditional Function Calls
```python
# Based on regime detection
regime = detect_market_regime(prices)
if regime == 'bull':
    strategy = optimize_max_sharpe(prices)
else:
    strategy = optimize_min_volatility(prices)
```

## Error Handling Patterns

### Missing Data
- Handle NaN/infinite values gracefully
- Provide clear error messages
- Suggest alternative functions

### Invalid Parameters
- Validate input ranges (e.g., period > 0)
- Check data sufficiency (e.g., period <= len(data))
- Provide helpful error messages

### Calculation Failures
- Fallback to alternative methods
- Log warnings for borderline cases
- Return None or NaN on failure