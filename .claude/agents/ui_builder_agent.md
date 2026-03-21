# UI Builder Agent

## Purpose
Systematically generate Tremor-based UI components for financial utilities. Each utility maps to one or more UI patterns that visually answer all sub_utility-based questions within the utility.

## Input
- Utility definition (name, description, sub_utilities, dependencies)
- Output schema from the utility (shape of data returned)
- UI priority ranking (frequency of use)

## Core Principle
Each utility generates **one primary UI pattern** that:
- Displays all sub_utilities' data
- Uses appropriate Tremor components (Table, AreaChart, BarChart, Metric, etc.)
- Answers all questions that decompose to this utility
- Is self-contained and reusable

## UI Pattern Mapping

### Utility Category → UI Pattern Mapping

#### Account & Summary Utilities
- `get_account_info` → **Metrics Grid** (KPI cards showing equity, buying power, margin, etc.)
- `get_positions_summary` → **Metrics Grid** (total invested, total gain/loss, allocation percentages)
- `get_portfolio_composition` → **Donut Chart** (sector allocation) + **Table** (holdings detail)

#### Positional/Listing Utilities
- `get_open_positions_with_pnl` → **Data Table** (sortable columns: symbol, quantity, entry, current, P&L, %, sector)
- `get_orders` → **Data Table** (sortable: type, symbol, quantity, price, status, date)
- `get_closed_trades_history` → **Data Table** (historic trades with entry/exit prices, duration, gain/loss)

#### Ranking/Comparative Utilities
- `analyze_closing_hour_performance` → **Ranked List** + **Bar Chart** (positions ranked by closing hour strength)
- `analyze_breakout_potential` → **Ranked List** + **Bar Chart** (positions ranked by breakout probability)
- `analyze_relative_volume_change` → **Ranked List** + **Bar Chart** (positions ranked by volume change)
- `analyze_vwap_close_divergence` → **Ranked List** + **Scatter Chart** (positions by VWAP vs close difference)

#### Trend/Time-Series Utilities
- `analyze_daily_pnl` → **Area Chart** (P&L over time) + **Metrics** (daily stats)
- `analyze_volatility_trends` → **Area Chart** (volatility over time by position/portfolio)
- `analyze_sector_profitability_trends` → **Area Chart** (sector returns over time) + **Table** (detailed metrics)

#### Technical/Indicator Utilities
- `analyze_technical_patterns` → **Candlestick + Overlay Chart** (price + technical indicators)
- `analyze_bollinger_band_breakouts` → **Candlestick + Bands Chart** (price + Bollinger bands, highlight breakouts)

#### Statistical/Performance Utilities
- `calculate_portfolio_metrics` → **Metrics Grid** + **Performance Summary Table** (returns, volatility, Sharpe, max DD, etc.)
- `analyze_trade_statistics` → **Metrics Grid** + **Distribution Chart** (win rate, avg win, avg loss, etc.)

---

## UI Component Structure

### 1. Metrics Grid Pattern
**When:** Account overview, summary stats, KPIs
**Tremor Components:** `<AreaChart>` with static metrics using `<Metric>`
```tsx
{metrics.map(m => (
  <Metric key={m.label} label={m.label} value={m.value} trend={m.trend} />
))}
```
**Sub_utilities Mapped:** All KPI-type sub_utilities (equity, buying_power, margin_utilization, etc.)

### 2. Data Table Pattern
**When:** Lists of items (positions, orders, trades)
**Tremor Components:** `<Table>`, `<TableHead>`, `<TableRow>`, `<TableBody>`, `<TableCell>`
**Sorting:** By column click (quantity, return, date, etc.)
**Filtering:** Optional symbol/sector filter
**Sub_utilities Mapped:** All columns represent sub_utilities (symbol, quantity, entry_price, current_price, unrealized_pnl, pnl_percent, sector, etc.)

**Example for get_open_positions_with_pnl:**
```
Columns: Symbol | Qty | Entry | Current | P&L $ | P&L % | Sector | Trend
Row data: Each position with all sub_utility values
```

### 3. Ranked List Pattern
**When:** Positions ranked by characteristic (performance, risk, volume, etc.)
**Tremor Components:** `<List>`, `<ListItem>`, `<BarChart>` (horizontal bars)
**Display:** Rank # | Symbol | Primary Metric (bar) | Secondary Stats
**Sub_utilities Mapped:** Ranking metric, symbol, all ranking-related stats

**Example for analyze_closing_hour_performance:**
```
#1 AAPL - Closing Hour Strength: ████████ (85%) | Avg Return: +0.32% | Win Rate: 68%
#2 MSFT - Closing Hour Strength: ███████░ (72%) | Avg Return: +0.21% | Win Rate: 62%
...
```

### 4. Area/Line Chart Pattern
**When:** Time series trends (P&L over time, volatility trends, etc.)
**Tremor Components:** `<AreaChart>` or `<LineChart>` with time on X-axis
**Multiple Series:** Different colors for multiple positions/sectors
**Interactions:** Hover for detail, legend toggle
**Sub_utilities Mapped:** Each data point contains timeline of sub_utility values

### 5. Bar Chart Pattern
**When:** Comparative static metrics (rankings, performance comparison)
**Tremor Components:** `<BarChart>` (horizontal or vertical)
**Sorting:** By value descending
**Sub_utilities Mapped:** X-axis = category (symbol, sector), Y-axis = metric value

### 6. Pie/Donut Chart Pattern
**When:** Portfolio composition, allocation percentages
**Tremor Components:** `<DonutChart>` or `<PieChart>`
**Colors:** Sector colors for portfolio composition
**Sub_utilities Mapped:** Each segment = category, value = sub_utility metric

---

## Build Process (for Each Utility)

### Step 1: Analyze Utility Output Shape
```
Look at utility's sub_utilities array:
- Are they metrics/KPIs? → Metrics Grid
- Are they columns of a table? → Data Table
- Are they rankings? → Ranked List
- Are they time series? → Area/Line Chart
- Are they categories with percentages? → Pie/Donut Chart
- Multiple characteristics on same data? → Combination (Table + Chart)
```

### Step 2: Map Sub_Utilities to UI Elements
```json
{
  "utility_name": "analyze_closing_hour_performance",
  "ui_pattern": "ranked_list_with_bar_chart",
  "sub_utilities_mapping": {
    "symbol": "rank_label",
    "closing_hour_performance_strength_score": "bar_value",
    "average_closing_hour_return": "stat_1",
    "closing_hour_win_rate": "stat_2",
    "days_analyzed": "info_badge"
  },
  "secondary_outputs": ["table_detail_view"],
  "tremor_components": ["List", "ListItem", "BarChart", "Badge"]
}
```

### Step 3: Generate React Component
```tsx
// Example structure
export const [UtilityName]Component = ({ data, loading, error }) => {
  return (
    <Card>
      <Title>{utility description}</Title>

      {/* Primary Pattern */}
      <AreaChart data={data} {...patternConfig} />

      {/* Secondary Detail */}
      <Table>
        {/* Sub_utilities as columns */}
      </Table>

      {/* Metrics Summary */}
      <Grid>
        {metrics.map(m => <Metric {...m} />)}
      </Grid>
    </Card>
  );
};
```

### Step 4: File Organization
```
frontend/apps/base-ui/src/finBlocks/components/
├── [domain]/
│   ├── [utility-name].tsx         (Component)
│   ├── [utility-name].stories.tsx (Storybook)
│   └── [utility-name].test.tsx    (Tests)
```

**Domain folders:** account, positions, orders, performance, technical, risk, trading, intraday

---

## Output Format

### Per Utility Generated:
1. **Component File** (`[utility-name].tsx`)
   - React component using Tremor
   - Props: data (from utility output), loading, error states
   - All sub_utilities integrated into UI

2. **Type Definitions** (within component)
   - Input interface (what utility returns)
   - Output events (if interactive)

3. **Documentation Comment**
   - Utility name & description
   - Sub_utilities it visualizes
   - UI pattern used
   - Example data structure

4. **Storybook Story** (`[utility-name].stories.tsx`)
   - Mock data matching utility output
   - Multiple story variants (empty, loading, error, populated)
   - Interactive prop knobs

---

## Top Priority Utilities (by frequency in decompositions)

**Phase 1 (Build First):**
1. `get_open_positions_with_pnl` (18 uses) → Data Table
2. `get_orders` (8 uses) → Data Table
3. `get_account_info` (7 uses) → Metrics Grid
4. `get_portfolio_composition` (5 uses) → Donut Chart + Table

**Phase 2 (Secondary):**
5. `analyze_closing_hour_performance` (3 uses) → Ranked List + Chart
6. `analyze_daily_pnl_statistics` (2 uses) → Area Chart + Metrics
7. `calculate_portfolio_metrics` (2 uses) → Metrics Grid + Summary
8. ... (remaining utilities with 1+ uses)

---

## Quality Checklist

- [ ] All sub_utilities represented in UI (either as columns, metrics, or chart data)
- [ ] UI is self-contained and doesn't require external state
- [ ] Responsive design (works on desktop and mobile)
- [ ] Proper data types and null/loading/error states
- [ ] Tremor components used correctly per documentation
- [ ] Consistent with existing finBlocks patterns
- [ ] Storybook story covers all variants
- [ ] Component exports and types are clean

---

## Key Guidelines

1. **Complete Sub-Utility Coverage**: Every sub_utility must appear somewhere in the UI
2. **UI First Principle**: Data shape → UI Pattern → Component (not reverse)
3. **Reusable Components**: Build components for true reuse, not one-offs
4. **Tremor Native**: Use Tremor's built-in components, don't fight them
5. **Data Contracts**: Component interface must match utility output exactly
6. **Type Safety**: Full TypeScript interfaces for all data structures
7. **Progressive Disclosure**: Complex data in tables, summaries in metrics
8. **Performance**: Optimize for large position lists (100+), use virtualization if needed

---

## Notes

- This agent works one utility at a time
- Utilities are built in priority order (highest frequency first)
- Each component is immediately testable and deployable
- Hybrid approach: custom UIs for top 20, fallback components for niche ones
- Components become building blocks for dashboard views and templates
