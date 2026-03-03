# Context Awareness for QnA AI Admin Financial Analysis System

## Project Overview
This is a Next.js prototype application that creates a QnA-driven JSON output workflow for financial data. The app features a two-panel interface where users can ask investment/trading questions and preview corresponding well-formatted JSON outputs with descriptive field explanations.

## Current Development Focus
We are building a comprehensive analysis categorization system for retail investors, ranging from simple information lookup to sophisticated financial analysis. The system uses natural language processing to match user questions to appropriate analysis types and complexity levels.

## Key Architectural Principles

### 1. Complexity Hierarchy (Simple → Expert)
Every analysis category follows a 4-tier complexity structure:
- **Simple**: Basic retail investor needs (beginners)
- **Intermediate**: Active retail traders/investors
- **Advanced**: Sophisticated investors, financial advisors
- **Expert**: Institutional-grade analysis

### 2. Objective Analysis Only
- ❌ NO buy/sell/hold recommendations
- ❌ NO "good" vs "bad" judgments
- ✅ Objective metrics and calculations only
- ✅ Educational explanations with context
- ✅ "Here's what the data shows" approach

### 3. JSON Schema Structure
All analyses follow this standardized format:
```json
{
  "analysis_id": "unique_identifier",
  "name": "Human Readable Name",
  "complexity": "simple|intermediate|advanced|expert",
  "category": "category_name",
  "keywords": ["trigger", "words", "for", "matching"],
  "description": "What this analysis does",
  "typical_questions": ["Sample user questions"],
  "parameters": {
    "required": { "symbol": "AAPL" },
    "optional": { "timeframe": "1Y" }
  },
  "output_format": { "detailed output structure" },
  "api_requirements": ["mcp server functions needed"],
  "computational_complexity": "low|medium|high|very_high"
}
```

### 4. Output Filtering & Intent Recognition
The system supports smart output filtering based on user intent:
- Parse user input for specific keywords
- Match to intent (holdings, sectors, performance, etc.)
- Return only relevant data sections
- Avoid information overload

## Developed Categories (Priority Order)

### 0. Stock/ETF Info (FOUNDATION) 🏃
**Status: COMPLETE**
- Basic company/fund information lookup
- Current price and historical performance
- Holdings and sector breakdowns
- Output filtering for specific requests
- Foundation before any analysis

### 1. Portfolio Visualizer (COMPLETE) 📈
**Status: COMPLETE**
- Simple: Basic 60/40, Three-Fund portfolios
- Intermediate: Multi-asset strategies
- Advanced: Risk-optimized portfolios
- Expert: Dynamic multi-strategy systems
- Enhanced with dollar-cost averaging, rebalancing analysis

### 2. Stock Analysis (IN PLANNING) 📊
**Status: PLANNED**
- Objective fundamental and technical analysis
- No recommendations, pure data analysis
- Complexity from basic metrics to quantitative research

### 3. Technical Indicators Trading 📈
**Status: PLANNED**
- Chart-based analysis and signal detection
- Visual indicators and pattern recognition

### 4. Stock/ETF Comparison ⚖️
**Status: PLANNED**
- Head-to-head comparisons
- Multi-factor analysis

## Available APIs & Data Sources

### MCP Financial Server
- Alpaca Market Data: Stock pricing, options, crypto, forex
- Alpaca Trading: Account management, positions, orders
- EODHD: Additional financial data endpoints

### MCP Analytics Server
- Technical indicators (RSI, MACD, Bollinger Bands, etc.)
- Statistical analysis functions
- Portfolio analysis tools
- Risk metrics calculations

## File Structure & Naming Convention
- `{category}-{type}.json` for analysis schemas
- `retail-analysis-categories-priority.txt` for roadmap
- `CLAUDE.md` for project instructions
- `experimental/` for JSON output examples

## Design Philosophy

### Retail-First Approach
- Start with what retail investors actually want to know
- Use natural language keywords they would type
- Provide educational context, not just numbers
- Bridge the gap between beginner and sophisticated analysis

### Extensible Architecture
- Each category can be developed independently
- Consistent JSON schema allows easy integration
- Keyword mapping enables natural language processing
- Output filtering provides surgical precision

### Real-World Implementation
- Consider practical constraints (minimum investments, fees)
- Include brokerage-specific guidance
- Provide step-by-step implementation help
- Account for tax implications and account types

## Current Conversation Context
We are systematically building analysis categories one by one, focusing on:

1. **JSON Schema Design**: Creating comprehensive, filterable output structures
2. **Keyword Mapping**: Natural language triggers for analysis matching
3. **Output Filtering**: Intent-based data filtering for precise responses
4. **Complexity Scaling**: From beginner-friendly to institutional-grade

The immediate goal is to complete the foundational "Stock/ETF Info" category and then move systematically through the priority list, ensuring each category is complete before advancing.

## Key Success Metrics
- Natural language question matching accuracy
- Appropriate complexity level assignment
- Educational value for retail investors
- Actionable insights without recommendations
- API integration completeness