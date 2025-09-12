# MCP Analytics Server

A Python-based MCP (Model Context Protocol) server that provides advanced financial analytics and computational capabilities for the QnA AI Admin system.

## Features

- **Daily Returns Calculation**: Calculate various types of daily returns (close-to-close, open-to-close, etc.)
- **Rolling Statistics**: Volatility, skewness, and other rolling window calculations
- **Correlation Analysis**: Pairwise correlations and correlation matrices
- **Trend Analysis**: Linear regression-based trend analysis with statistical significance
- **Risk Metrics**: VaR, CVaR, Sharpe ratio, drawdown analysis
- **Pattern Recognition**: Gap fills, failed breakdowns, consecutive trading days
- **Economic Sensitivity**: Performance analysis on specific economic event dates (CPI, FOMC, etc.)

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the MCP server:
```bash
python server.py
```

The server will start and listen for MCP protocol messages via stdio.

## Available Tools

### calculate_daily_returns
Calculate daily percentage returns from OHLC price data.

### calculate_rolling_volatility  
Calculate rolling volatility with optional annualization.

### calculate_rolling_skewness
Calculate rolling skewness to measure return distribution asymmetry.

### calculate_correlation_matrix
Generate correlation matrices between multiple return series.

### calculate_trend_analysis
Perform linear regression trend analysis on price series.

### calculate_drawdown_metrics
Calculate maximum drawdown and related risk metrics.

### calculate_risk_metrics
Comprehensive risk analysis including VaR, Sharpe ratio, etc.

### identify_trading_patterns
Identify specific trading patterns like gap fills and failed breakdowns.

### analyze_economic_sensitivity
Analyze position performance on economic event dates.

## Integration

This server integrates with the QnA AI Admin system to support "engine" and "compute" workflow steps that require advanced analytics beyond basic API data retrieval.

## Dependencies

- pandas: Data manipulation and analysis
- numpy: Numerical computations
- scipy: Statistical functions
- scikit-learn: Machine learning utilities
- ta: Technical analysis indicators
- yfinance: Backup market data (if needed)
- matplotlib: Plotting capabilities (if needed)
- mcp: Model Context Protocol implementation