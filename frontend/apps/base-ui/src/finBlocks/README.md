# finBlocks - Financial UI Components Library

A comprehensive collection of **110 financial UI blocks** for retail investor dashboards, organized into **11 categories**. Each finBlock is a React component that wraps a Tremor UI block and specializes in displaying specific financial data patterns.

## Overview

### Categories

1. **Portfolio** (12 blocks) - Portfolio management and overview
   - KPI summaries, holdings tables, sector allocation, performance tracking
   
2. **Stock Research** (12 blocks) - Stock analysis and research
   - Price data, fundamentals, earnings, technical indicators, valuation
   
3. **ETF Analysis** (10 blocks) - ETF comparison and analysis
   - Performance comparison, sector composition, expense ratios, tax efficiency
   
4. **Risk Management** (12 blocks) - Risk analysis and monitoring
   - Volatility, VaR, drawdowns, concentration, correlation matrices
   
5. **Performance** (12 blocks) - Performance tracking and attribution
   - Returns analysis, risk-adjusted metrics, attribution, capture ratios
   
6. **Income** (10 blocks) - Dividend and income analysis
   - Dividend tracking, yield analysis, distribution calendars
   
7. **Sector** (10 blocks) - Sector and asset class analysis
   - Sector performance, allocation, rotation signals, correlation
   
8. **Technical** (8 blocks) - Technical analysis signals
   - RSI, MACD, moving averages, Bollinger Bands, support/resistance
   
9. **Fundamental** (8 blocks) - Fundamental analysis
   - Earnings quality, margins, debt, cash flow, competitive advantage
   
10. **Tax** (8 blocks) - Tax planning and optimization
    - Tax-loss harvesting, capital gains, estimated liability
    
11. **Monitoring** (10 blocks) - Alerts and monitoring
    - Price alerts, earnings calendar, news sentiment, volatility spikes

## Usage

### Basic Import

```tsx
import { PortfolioKpiSummary, HoldingsTable } from '@/finBlocks';

export function MyDashboard() {
  return (
    <>
      <PortfolioKpiSummary data={kpiData} />
      <HoldingsTable data={holdingsData} />
    </>
  );
}
```

### Using the Registry

```tsx
import { getFinBlock, getFinBlocksByCategory, getAllFinBlocks } from '@/finBlocks';

// Get a specific finBlock by ID
const block = getFinBlock('portfolio-kpi-summary');

// Get all finBlocks in a category
const portfolioBlocks = getFinBlocksByCategory('portfolio');

// Get all finBlocks
const allBlocks = getAllFinBlocks();

// Get finBlocks by financial concept
const riskBlocks = getFinBlocksByFinancialConcept('volatility');
```

## Component Structure

Each finBlock component:

- **Imports** the underlying Tremor block component
- **Defines** a TypeScript data interface matching the data contract
- **Includes** sample data for preview/testing
- **Exports** a React component accepting optional data prop
- **Falls back** to sample data if no data provided

### Example Component

```tsx
/**
 * Portfolio KPI Summary finBlock
 * Wraps: KpiCard01
 * Description: Total value, total P&L, YTD return, and Sharpe ratio
 */

import React from 'react';
import { KpiCard01 } from '../../../blocks/kpi-cards/kpi-card-01';

export interface PortfolioKpiSummaryData {
  metrics?: Array<{ 
    name: string; 
    stat: number | string; 
    change: string; 
    changeType: 'positive' | 'negative' | 'neutral' 
  }>;
  cols?: number;
}

const SAMPLE_DATA: PortfolioKpiSummaryData = {
  metrics: [
    { name: 'Portfolio Value', stat: 120505, change: '+2.3%', changeType: 'positive' },
    { name: 'Total P&L', stat: 8505, change: '+7.6%', changeType: 'positive' },
  ],
  cols: 2,
};

export const PortfolioKpiSummary: React.FC<{ data?: PortfolioKpiSummaryData }> = ({ 
  data = SAMPLE_DATA 
}) => {
  return <KpiCard01 {...data} />;
};
```

## Registry Types

```tsx
export interface FinBlockMetadata {
  id: string;                              // Unique identifier
  name: string;                            // Display name
  description: string;                     // What it shows
  category: string;                        // Category key
  blockType: string;                       // kpi-card, table, bar-chart, etc.
  blockCatalogRef: string;                 // Underlying block reference
  component: React.ComponentType<any>;     // React component
  financialConcepts: string[];             // Financial concepts it covers
  dataContract: Record<string, any>;       // Expected data shape
  parameters?: Array<...>;                 // Configuration parameters
  mcpRequired: string[];                   // MCP tools needed
  useCases: string[];                      // Typical use cases
  estimatedDataFetch: string;              // Data fetch time estimate
}
```

## Data Contracts

Each finBlock documents its expected data structure in the FINBLOCK_CATALOG.json. The data contract defines:

- Required and optional fields
- Field types (string, number, array, etc.)
- Expected object shapes for complex types

Always consult the specific component's TypeScript interface for exact requirements.

## Performance Considerations

- Sample data is baked into components for instant preview
- Components accept optional data props to override samples
- Use lazy loading for dashboard grids with many finBlocks
- Consider pagination for large tables and lists

## Integration with MCP

Each finBlock documents which MCP (Model Context Protocol) tools are required:

```tsx
mcpRequired: ['get_account', 'get_positions', 'get_portfolio_history']
```

Use this metadata to:
- Understand data dependencies
- Batch API calls efficiently
- Handle missing data gracefully

## Directory Structure

```
finBlocks/
├── components/
│   ├── portfolio/
│   │   ├── portfolio-kpi-summary.tsx
│   │   ├── holdings-table.tsx
│   │   ├── ...
│   │   └── index.ts
│   ├── stock_research/
│   ├── etf_analysis/
│   ├── risk_management/
│   ├── performance/
│   ├── income/
│   ├── sector/
│   ├── technical/
│   ├── fundamental/
│   ├── tax/
│   └── monitoring/
├── FINBLOCK_CATALOG.json
├── finBlockRegistry.ts
├── index.ts
└── README.md
```

## Building Dashboards

Typical dashboard patterns using finBlocks:

### 1. Portfolio Overview
```tsx
<PortfolioKpiSummary />
<HoldingsTable />
<SectorAllocationDonut />
```

### 2. Stock Analysis
```tsx
<StockPriceKpi />
<PriceHistoryWithMa />
<FundamentalMetricsList />
<EarningsHistoryTable />
```

### 3. Risk Dashboard
```tsx
<RiskMetricsKpi />
<VolatilityByHolding />
<DrawdownHistory />
<CorrelationMatrix />
```

### 4. Income Portfolio
```tsx
<DividendIncomeKpi />
<DividendPayersTable />
<MonthlyDividendTrend />
<TopDividendYielders />
```

## Customization

To customize a finBlock:

1. Import the component
2. Prepare data matching the TypeScript interface
3. Pass data via the `data` prop
4. Styles follow Tremor theming (light/dark mode)

```tsx
<PortfolioKpiSummary 
  data={{
    metrics: myMetrics,
    cols: 4,
  }}
/>
```

## Generated Files Summary

- **110 component files** - One per finBlock
- **11 index.ts files** - One per category
- **1 finBlockRegistry.ts** - Runtime metadata and helpers
- **1 FINBLOCK_CATALOG.json** - Complete specification

Total: **123 files** organized for scalability and maintainability.

## Future Enhancements

- Add more block types (heatmaps, treemaps, waterfall charts)
- Implement real-time data updates via WebSocket
- Add export capabilities (PDF, CSV)
- Create dashboard builder UI
- Add finBlock composition patterns
- Implement caching layer for MCP calls

---

**Generated:** 2024
**Total Components:** 110
**Categories:** 11
**Underlying Block Types:** 12
