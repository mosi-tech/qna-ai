# Composable Portfolio Analytics Design

## Problem with Previous Approach
- Created monolithic functions that "do everything"
- Not composable for Q&A workflows where questions break down into steps
- Each step in a workflow should map to ONE atomic function
- LLM needs to chain atomic functions together, not call one big function

## MCP Q&A Workflow Pattern

**User Question:** "How would a 60/40 portfolio have performed during the 2008 crisis?"

**LLM Breakdown:**
```
Step 1: Calculate portfolio returns from historical data
Step 2: Filter to crisis period (2008-2009)  
Step 3: Calculate performance metrics for that period
Step 4: Analyze maximum drawdown and recovery
```

**Function Mapping:**
```python
# Step 1
returns = calculate_portfolio_returns(
    data={"SPY": spy_data, "BND": bnd_data}, 
    weights={"SPY": 0.6, "BND": 0.4}
)

# Step 2  
crisis_returns = filter_date_range(
    returns, start="2008-01-01", end="2009-12-31"
)

# Step 3
metrics = calculate_performance_metrics(crisis_returns)

# Step 4
drawdown = calculate_drawdown_analysis(crisis_returns)
```

## Atomic Function Categories

### 1. **Data Processing Functions**
- `calculate_portfolio_returns(data, weights)` - Convert price data + weights → portfolio returns
- `filter_date_range(data, start, end)` - Extract specific time periods
- `resample_frequency(data, frequency)` - Daily → monthly/quarterly/yearly
- `align_data_series(*series)` - Align multiple time series
- `fill_missing_data(data, method)` - Handle gaps in data

### 2. **Performance Calculation Functions**
- `calculate_total_return(returns)` - Total return over period
- `calculate_annualized_return(returns, days)` - Annualized return
- `calculate_volatility(returns, annualized=True)` - Standard deviation
- `calculate_sharpe_ratio(returns, risk_free_rate)` - Risk-adjusted return
- `calculate_sortino_ratio(returns, risk_free_rate)` - Downside-focused ratio

### 3. **Risk Analysis Functions**
- `calculate_drawdown_series(returns)` - Running drawdown series
- `calculate_max_drawdown(returns)` - Maximum drawdown and duration
- `calculate_var(returns, confidence_level)` - Value at Risk
- `calculate_cvar(returns, confidence_level)` - Conditional VaR
- `calculate_beta(portfolio_returns, market_returns)` - Market beta

### 4. **Portfolio Construction Functions**
- `optimize_weights_sharpe(expected_returns, cov_matrix)` - Max Sharpe optimization
- `optimize_weights_risk_parity(cov_matrix)` - Equal risk contribution
- `calculate_efficient_frontier(expected_returns, cov_matrix)` - Efficient frontier points
- `rebalance_portfolio(returns, weights, frequency)` - Simulate rebalancing

### 5. **Comparison Functions**
- `calculate_tracking_error(portfolio_returns, benchmark_returns)` - Tracking error
- `calculate_information_ratio(portfolio_returns, benchmark_returns)` - IR
- `calculate_alpha(portfolio_returns, benchmark_returns, beta)` - Jensen's alpha
- `compare_performance_metrics(*return_series)` - Side-by-side comparison

### 6. **Scenario Analysis Functions**
- `stress_test_portfolio(returns, scenario_shocks)` - Apply stress scenarios
- `monte_carlo_simulation(returns, num_simulations, periods)` - Monte Carlo
- `calculate_rolling_metrics(returns, window, metric)` - Rolling calculations
- `identify_bear_markets(returns, threshold)` - Bear market periods

## Example Q&A Workflows

### Q: "What was the Sharpe ratio of a 70/30 stock/bond portfolio in 2020?"

**Steps:**
1. `calculate_portfolio_returns(data, {"stocks": 0.7, "bonds": 0.3})`
2. `filter_date_range(returns, "2020-01-01", "2020-12-31")`
3. `calculate_sharpe_ratio(filtered_returns, risk_free_rate=0.02)`

### Q: "How often should I rebalance a three-fund portfolio?"

**Steps:**
1. `calculate_portfolio_returns(data, three_fund_weights)`
2. `rebalance_portfolio(returns, weights, "monthly")` → monthly_result
3. `rebalance_portfolio(returns, weights, "quarterly")` → quarterly_result  
4. `rebalance_portfolio(returns, weights, "yearly")` → yearly_result
5. `compare_performance_metrics(monthly_result, quarterly_result, yearly_result)`

### Q: "What's the maximum drawdown during bear markets for my portfolio?"

**Steps:**
1. `calculate_portfolio_returns(data, my_weights)`
2. `identify_bear_markets(market_returns, threshold=-0.20)`
3. `filter_date_range(portfolio_returns, bear_market_periods)`
4. `calculate_max_drawdown(bear_market_returns)`

## Function Design Principles

### ✅ Good Atomic Function
```python
def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """Calculate Sharpe ratio for a return series."""
    excess_returns = returns - risk_free_rate/252
    return excess_returns.mean() / excess_returns.std() * np.sqrt(252)
```

### ❌ Bad Monolithic Function  
```python
def comprehensive_portfolio_analyzer(data, weights, mode, rebalancing, stress_test, ...):
    # Does everything - not composable!
```

### Key Characteristics:
- **Single Responsibility:** Does ONE thing well
- **Pure Function:** Same inputs → same outputs
- **Composable:** Output can be input to other functions
- **Clear Interface:** Obvious what goes in and comes out
- **Descriptive Name:** Function name maps to Q&A workflow step

## Implementation Priority

1. **Core Data Functions** (calculate returns, filter dates)
2. **Basic Performance Metrics** (return, volatility, Sharpe)
3. **Risk Metrics** (drawdown, VaR)
4. **Comparison Functions** (vs benchmark)
5. **Advanced Functions** (optimization, Monte Carlo)