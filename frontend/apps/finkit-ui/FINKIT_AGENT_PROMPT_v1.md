# FINKIT Primitives — Coding Agent Prompt

## Your role

You are building **FINKIT**, a generic React visualization primitive library for financial analytics dashboards. You are a senior frontend engineer. You write clean, production-quality React. You do not improvise — you follow the spec below exactly.

---

## What you are building

A library of **12 React components** that are the visual foundation for any financial dashboard. These components know nothing about finance. They know about data shapes and visual encodings. Finance-specific meaning lives in how the props are configured and how data is prepared before it reaches the component.

The principle: **a drawdown chart is not a component. It is `FKAreaChart` with `fillMode="below"` and `fillReference={0}`. An earnings chart is not a component. It is `FKBarChart` with a `colorRule` that fires on beat/miss.** Every investment visualization maps to one of these 12 primitives via props configuration alone.

---

## Constraints — read these before writing a single line

1. **React 18 functional components + hooks only.** No class components.
2. **Recharts** for all chart rendering except `FKRangeChart` and `FKScatterChart` which use raw Canvas.
3. **Tailwind CSS for all styling** Use utility classes directly on JSX elements. No inline style objects except where Tailwind cannot express the value (e.g. exact pixel chart dimensions passed as props). No CSS modules. No styled-components.
4. **CSS variables for all surfaces and text colors.** Semantic finance colors (`gain`, `loss`) are hardcoded hex — never use CSS variables for those.
5. **No dependencies beyond React and Recharts.** If you think you need another library, find a way to do it without.
6. **Every component must run with sample data when no props are passed.** This is non-negotiable — components must be self-demonstrating.
7. **Do not invent props** not listed in the spec. If something is unclear, implement the simpler interpretation.

---

## How to work through this

Work file by file in this exact order. Do not skip ahead.

```
1. src/tokens.js            ← shared design tokens, import this everywhere
2. src/FKCard.jsx           ← shared card wrapper, used by every component
3. src/FKSparkline.jsx      ← inline mini chart, used inside other components
4. src/FKMetricGrid.jsx     ← KPI headline block
5. src/FKLineChart.jsx      ← continuous x-axis, one or more series
6. src/FKAreaChart.jsx      ← filled regions: above / below / between / stacked
7. src/FKBarChart.jsx       ← categorical bars: grouped / stacked / waterfall
8. src/FKScatterChart.jsx   ← two-axis, size + color encoding (Canvas)
9. src/FKHeatGrid.jsx       ← two categorical dims, value → cell color
10. src/FKPartChart.jsx     ← part-of-whole: donut / treemap / stacked-bar
11. src/FKRangeChart.jsx    ← value within min-max range (Canvas)
12. src/FKCandleChart.jsx   ← OHLCV candlestick + volume
13. src/FKTable.jsx         ← sortable table with format + color rules
14. src/FKRankedList.jsx    ← ordered rows with metrics + sparklines
15. src/index.js            ← export everything
```

After all 15 files are complete, create a `src/showcase/Showcase.jsx` that renders every component with sample data so everything can be visually verified in one place.

---

## File structure

```
finkit-uikit/
├── package.json
├── src/
│   ├── tokens.js
│   ├── FKCard.jsx
│   ├── FKSparkline.jsx
│   ├── FKMetricGrid.jsx
│   ├── FKLineChart.jsx
│   ├── FKAreaChart.jsx
│   ├── FKBarChart.jsx
│   ├── FKScatterChart.jsx
│   ├── FKHeatGrid.jsx
│   ├── FKPartChart.jsx
│   ├── FKRangeChart.jsx
│   ├── FKCandleChart.jsx
│   ├── FKTable.jsx
│   ├── FKRankedList.jsx
│   ├── index.js
│   └── showcase/
│       └── Showcase.jsx
```

---

## Definition of done

- [ ] All 15 source files created
- [ ] Every component renders without errors when no props are passed (uses built-in sample data)
- [ ] `FKAreaChart` correctly handles all four `fillMode` values: `above`, `below`, `between`, `stacked`
- [ ] `FKBarChart` correctly handles `grouped`, `stacked`, and `waterfall` modes
- [ ] `FKPartChart` correctly handles `donut`, `treemap`, and `stacked-bar` modes
- [ ] `FKRangeChart` and `FKScatterChart` use Canvas with ResizeObserver
- [ ] All colors come from `tokens.js` — no inline color literals except where tokens.js defines them
- [ ] `Showcase.jsx` renders all 12 components visually

---

## The spec

Everything below this line is the full component specification. Follow it exactly.

---

# FINKIT UI Kit — Primitives Build Brief

## Philosophy

This is a **generic visualization primitive library** for financial analytics.
Components know nothing about finance. They know about data shapes and visual encodings.
Finance-specific behavior lives in the data pipeline and in how props are configured —
not in the components themselves.

The goal: 11 primitives that can express any investment question by varying props,
data shape, and a `colorRule` function. No more components should ever need to be added.

---

## Tech stack

- React 18 (functional components + hooks only)
- Recharts for chart primitives (AreaChart, LineChart, BarChart, ComposedChart, PieChart,
  ScatterChart, ResponsiveContainer, XAxis, YAxis, Tooltip, ReferenceLine, Cell)
- Raw Canvas (via useRef + useEffect) for FKRangeChart and FKScatterChart
- CSS variables for all colors and surfaces (dark mode automatic)
- Inline styles only — no Tailwind, no CSS modules, no styled-components
- No other dependencies

---

## Shared design tokens (put in `src/tokens.js`, import everywhere)

```js
export const color = {
  gain:      '#16a34a',
  loss:      '#dc2626',
  warn:      '#d97706',
  gainBg:    'rgba(22,163,74,0.09)',
  lossBg:    'rgba(220,38,38,0.09)',
  series:    ['#6366f1','#06b6d4','#f59e0b','#ec4899','#10b981','#94a3b8'],
  seriesBg:  ['rgba(99,102,241,0.12)','rgba(6,182,212,0.08)','rgba(245,158,11,0.08)',
              'rgba(236,72,153,0.08)','rgba(16,185,129,0.08)','rgba(148,163,184,0.06)'],
}

export const surface = {
  card:    'var(--color-background-primary)',
  raised:  'var(--color-background-secondary)',
  page:    'var(--color-background-tertiary)',
  border:  'var(--color-border-tertiary)',
  border2: 'var(--color-border-secondary)',
}

export const font = {
  sans: 'var(--font-sans)',
  mono: 'var(--font-mono)',
}

// Single source of truth for Recharts — import these into every chart component
export const axisProps = {
  tick:     { fontSize: 10, fill: 'var(--color-text-tertiary)', fontFamily: 'var(--font-mono)' },
  axisLine: false,
  tickLine: false,
}

export const gridProps = {
  stroke:   'var(--color-border-tertiary)',
  vertical: false,
}

export const tooltipStyle = {
  background:   'var(--color-background-primary)',
  border:       '0.5px solid var(--color-border-secondary)',
  borderRadius: 8,
  padding:      '10px 12px',
  fontSize:     12,
  fontFamily:   'var(--font-mono)',
}
```

---

## Shared card wrapper (put in `src/FKCard.jsx`)

Every chart component wraps itself in this card. Export it so compositions can use it too.

```jsx
export function FKCard({ children, style }) {
  return (
    <div style={{
      background:   'var(--color-background-primary)',
      border:       '0.5px solid var(--color-border-tertiary)',
      borderRadius: 12,
      overflow:     'hidden',
      ...style,
    }}>
      {children}
    </div>
  )
}

export function FKCardHeader({ title, subtitle, actions }) {
  return (
    <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start',
                  padding:'18px 20px 0' }}>
      <div>
        {title    && <div style={{ fontSize:14, fontWeight:500,
                                   color:'var(--color-text-primary)', marginBottom:2 }}>{title}</div>}
        {subtitle && <div style={{ fontSize:12, color:'var(--color-text-secondary)' }}>{subtitle}</div>}
      </div>
      {actions && <div style={{ display:'flex', gap:6, alignItems:'center' }}>{actions}</div>}
    </div>
  )
}
```

---

## Shared sub-primitives

### FKBadge
```jsx
// variant: 'gain' | 'loss' | 'warn' | 'neutral' | 'info'
// Pill label. Auto-colors from variant.
export function FKBadge({ children, variant = 'neutral', style })
```

### FKDelta
```jsx
// Renders ▲/▼ + value with gain/loss color. value is a number.
export function FKDelta({ value, decimals = 2, suffix = '%' })
```

### FKSparkline
```jsx
// Pure SVG inline sparkline. data is number[]. No recharts.
// Auto-detects direction from first/last value for color.
export function FKSparkline({ data, width = 72, height = 28, positive, showArea })
```

### FKRangeSelector
```jsx
// Period tab bar: ["1M","3M","6M","1Y"] style selector
// Active tab: border + background. Inactive: transparent.
export function FKRangeSelector({ options, value, onChange })
```

### FKStatStrip
```jsx
// Horizontal key-value bar that docks below charts.
// stats = [{ label, value, color? }]
// Separated from chart by borderTop. Background: var(--color-background-secondary).
export function FKStatStrip({ stats })
```

---

## The 11 Primitives

---

### P1 — FKLineChart

**What it is**: A line or multi-line chart over time or over an ordered category axis.

**Covers**: price history, rolling metrics (Sharpe, beta, vol), yield curve,
multi-asset comparison, implied vs realized vol, any time series.

```jsx
FKLineChart({
  // Data
  data,           // Array<Record<string, any>> — one object per x-axis point
  series,         // Array<{ key: string, label: string, color?: string, dashed?: boolean }>
  xKey,           // string — default 'date'
  yKey,           // string — only needed if single series without series[]

  // Axis
  xType,          // 'time' | 'category' — default 'time'
                  // 'category' = tenors (1M,3M,6M...), qualitative x labels
  yFormat,        // (value) => string — y-axis tick formatter
  xFormat,        // (value) => string — x-axis tick formatter

  // Reference lines
  referenceLines, // Array<{ x?, y?, label?, color?, dashed? }>
                  // x draws a vertical line, y draws a horizontal line

  // Chart controls
  height,         // number — default 240
  rangeSelector,  // boolean | string[] — show period tabs. true = ['1M','3M','6M','1Y','3Y','5Y']
  defaultRange,   // string — default selected range
  onRangeChange,  // (range) => void — called when user switches range

  // Extras
  smooth,         // boolean — curved lines. default false (straight is more precise for financial data)
  connectNulls,   // boolean — connect across null values. default false
  dot,            // boolean — show dots on data points. default false

  // Card
  title,
  subtitle,
  badge,          // string — shown as pill in top-right (e.g. 'Sample data')
  stats,          // FKStatStrip stats array — rendered below chart
})
```

**Key rendering rules**:
- Gradient fill under each series: top opacity 0.15, bottom 0. Use series color.
- When `referenceLines` has `y: 0`, draw it as a solid line in `rgba(0,0,0,0.15)`.
- Tooltip: custom component using `tooltipStyle` from tokens. Show date as header,
  then each series value in its series color, monospace.
- XAxis: `minTickGap: 40`, `maxRotation: 0`. For `xType: 'category'` show all labels.
- YAxis: right-side, width 52. Apply `yFormat`.
- Range selector sits in card header right side.

**Finance examples**:
```jsx
// QQQ 10-year price
<FKLineChart data={monthly} series={[{key:'QQQ'}]} xType="time"
  rangeSelector={['1Y','3Y','5Y','10Y']} yFormat={v=>`$${v.toFixed(0)}`} />

// Rolling Sharpe
<FKLineChart data={rolling} series={[{key:'sharpe_12m',label:'12M Sharpe'}]}
  referenceLines={[{y:1,label:'Good',color:'#16a34a',dashed:true},
                   {y:0,label:'',color:'rgba(0,0,0,0.15)'}]} />

// Yield curve (category x-axis)
<FKLineChart data={yieldData} xType="category" xKey="tenor"
  series={[{key:'today',label:'Today'},{key:'1y_ago',label:'1Y ago',dashed:true}]} />
```

---

### P2 — FKBandChart

**What it is**: An area chart pinned to a baseline, with fill above and/or below the baseline.
Different from FKLineChart because the zero line is semantically meaningful — it separates
gain from loss territory.

**Covers**: drawdown chart, underwater equity curve, confidence bands/cones,
spread between two series, above/below benchmark.

```jsx
FKBandChart({
  data,           // Array<Record<string, any>>
  series,         // Array<{ key: string, label?: string, color?: string }>
                  // If two series: fills the band between them
                  // If one series: fills between series and baseline

  xKey,           // string — default 'date'
  baseline,       // number — default 0. The reference line.

  // Fill colors
  fillAbove,      // string | null — color when value > baseline. null = no fill.
  fillBelow,      // string | null — color when value < baseline. null = no fill.
  fillAboveOpacity, // number — default 0.15
  fillBelowOpacity, // number — default 0.3 (below is usually the warning zone)

  // Axis
  yFormat,
  referenceLines,  // same as FKLineChart

  // Chart
  height,          // default 200
  rangeSelector,
  defaultRange,
  onRangeChange,

  // Card
  title,
  subtitle,
  badge,
  stats,
})
```

**Key rendering rules**:
- Baseline drawn as a solid line `rgba(0,0,0,0.2)`.
- Fill below baseline in `fillBelow` color — this is the "bad zone".
- For drawdown: `fillAbove=null`, `fillBelow='#dc2626'`, `fillBelowOpacity=0.3`.
- For confidence band (two series): fill between the two series in a neutral color.
- The line itself: 1.5px, series color. Below baseline segments: loss color.

**Finance examples**:
```jsx
// Drawdown chart
<FKBandChart data={dd} series={[{key:'drawdown'}]}
  baseline={0} fillAbove={null} fillBelow="#dc2626"
  yFormat={v=>`${v.toFixed(1)}%`} title="Drawdown from Peak" />

// Portfolio vs benchmark band
<FKBandChart data={perf} series={[{key:'portfolio'},{key:'benchmark'}]}
  baseline={0} fillAbove="#16a34a" fillBelow="#dc2626" />
```

---

### P3 — FKBarChart

**What it is**: Vertical or horizontal bars. Single series, grouped, stacked, or waterfall.

**Covers**: monthly P&L, annual returns, sector ranking, grouped comparison (earnings estimate vs actual),
stacked breakdown, P&L attribution waterfall, dividend history, PE comparison.

```jsx
FKBarChart({
  data,            // Array<Record<string, any>>
  series,          // Array<{ key: string, label?: string, color?: string }>
                   // If omitted: single-series using valueKey
  valueKey,        // string — default 'value'. Used when series is omitted.
  labelKey,        // string — default 'label'. X-axis labels.

  // Layout
  orientation,     // 'vertical' | 'horizontal' — default 'vertical'
  mode,            // 'single' | 'grouped' | 'stacked' | 'waterfall' — default 'single'

  // Coloring
  colorRule,       // (row, seriesKey?) => 'gain' | 'loss' | 'warn' | 'neutral' | string
                   // default: positive values → gain, negative → loss
                   // Examples:
                   //   (_,k) => k === 'actual' ? 'gain' : 'neutral'  (earnings chart)
                   //   (row) => row.actual > row.estimate ? 'gain' : 'loss'

  referenceValue,  // number — draws a horizontal reference line (e.g. market PE median)

  // Chart
  height,          // default 200
  maxBarSize,      // number — default 40 (single), 24 (grouped)

  // Waterfall specific
  showRunningTotal, // boolean — default true for waterfall mode
  totalLabel,       // string — label for the final total bar

  // Card
  title,
  subtitle,
  badge,
  stats,
})
```

**Key rendering rules**:
- Default `colorRule`: positive → `rgba(22,163,74,0.72)` fill + `#16a34a` stroke,
  negative → `rgba(220,38,38,0.72)` + `#dc2626` stroke, strokeWidth 1.
- Bar border radius: `[4,4,0,0]` vertical, `[0,4,4,0]` horizontal.
- Waterfall mode: bars start from the running total of previous bars, not from zero.
  Each bar has a thin connector line to the next. Total bar is full-height in neutral color.
- Horizontal mode: sort descending by value so highest is at top.
- Grouped: gap between groups larger than gap within group.

**Finance examples**:
```jsx
// Monthly P&L (auto green/red)
<FKBarChart data={monthly} valueKey="pnl" labelKey="month"
  yFormat={v=>`${v>=0?'+$':'-$'}${Math.abs(v/1000).toFixed(0)}k`} />

// Earnings beat/miss
<FKBarChart data={quarters} mode="grouped"
  series={[{key:'estimate',label:'Est.'},{key:'actual',label:'Actual'}]}
  colorRule={(row,k) => k==='actual' ? (row.actual>row.estimate?'gain':'loss') : 'neutral'} />

// P&L attribution waterfall
<FKBarChart data={attribution} mode="waterfall"
  colorRule={(row) => row.value >= 0 ? 'gain' : 'loss'} />

// Sector ranking (horizontal)
<FKBarChart data={sectors} orientation="horizontal" valueKey="return_pct" labelKey="name" />
```

---

### P4 — FKAreaChart

**What it is**: Stacked area chart where segments sum to 100% (normalized) or to a total.
Different from FKLineChart because the visual purpose is showing composition over time,
not individual values.

**Covers**: sector rotation, portfolio style drift, asset class weight over time,
revenue mix over time.

```jsx
FKAreaChart({
  data,     // Array<Record<string, any>>
  series,   // Array<{ key: string, label: string, color?: string }>
  xKey,     // string — default 'date'

  mode,     // 'stacked'     — absolute values stacked
            // 'normalized'  — each point sums to 100% (shows composition shift)
            // default: 'normalized' (most useful for finance)

  yFormat,
  height,   // default 260
  rangeSelector,
  defaultRange,
  onRangeChange,
  title,
  subtitle,
  badge,
})
```

**Key rendering rules**:
- Fill each band with `series[i].color` at opacity 0.75 (higher than FKLineChart — readability).
- Stroke between bands: 1px white-ish line `rgba(255,255,255,0.4)` for separation.
- Legend: horizontal row below chart, colored square + label.
- Tooltip: stacked — shows all series values at hovered x point.
- Normalized mode: y-axis from 0% to 100%.

**Finance examples**:
```jsx
// Sector rotation
<FKAreaChart data={monthly} mode="normalized"
  series={[{key:'tech'},{key:'finance'},{key:'health'},{key:'energy'},{key:'other'}]}
  title="Sector Weight Over Time" />
```

---

### P5 — FKScatterChart

**What it is**: Two-axis scatter / bubble chart. Optional size dimension (bubble).
Canvas-rendered for performance with many points.

**Covers**: risk vs return, hold-time vs P&L, PE vs revenue growth, momentum vs volatility screener.

```jsx
FKScatterChart({
  data,           // Array<Record<string, any>>
  xKey,           // string — x-axis metric
  yKey,           // string — y-axis metric
  sizeKey,        // string? — bubble radius proportional to this value
  colorKey,       // string? — key whose value maps to color. OR pass color on each row.
  colorMap,       // Record<string, string>? — maps colorKey values to colors
  labelKey,       // string? — label inside bubble (shown when bubble is large enough)

  // Axis
  xLabel,         // string — x-axis title
  yLabel,         // string — y-axis title
  xFormat,        // (v) => string
  yFormat,        // (v) => string

  // Reference lines
  referenceLines, // Array<{ x?, y?, label?, color?, dashed? }>

  // Options
  trendLine,      // boolean — draw OLS regression line. default false
  quadrants,      // boolean — draw crosshair at median x and y. default false

  height,         // default 280
  title,
  subtitle,
  stats,
})
```

**Key rendering rules**:
- Canvas rendering. useRef + useEffect + ResizeObserver for responsive sizing.
- Default bubble color: series[0] at 70% opacity for positive yKey, loss color for negative.
- Bubble stroke: same color at 100% opacity, 1.5px.
- Label inside bubble: only when radius >= 10px. 10px monospace, weight 500.
- Reference lines: drawn before bubbles. x-line = vertical, y-line = horizontal.
  Both dashed `[4,3]`, `rgba(0,0,0,0.15)`.
- Trend line: OLS. `rgba(0,0,0,0.2)`, dashed `[4,3]`, 1.5px.
- Quadrant crosshair: `rgba(0,0,0,0.06)`, solid 0.5px.

**Finance examples**:
```jsx
// Risk vs return
<FKScatterChart data={holdings} xKey="volatility" yKey="return_pct"
  sizeKey="portfolio_weight" labelKey="ticker"
  xLabel="Annualised Volatility (%)" yLabel="Annualised Return (%)"
  referenceLines={[{x: benchmarkVol}, {y: benchmarkReturn}]} quadrants />

// Screener: momentum vs vol
<FKScatterChart data={stocks} xKey="volatility_30d" yKey="momentum_3m"
  sizeKey="market_cap" labelKey="ticker" colorKey="sector"
  colorMap={{Technology:'#6366f1', Healthcare:'#10b981', Energy:'#f59e0b'}}
  trendLine title="Momentum vs Volatility" />
```

---

### P6 — FKHistogram

**What it is**: Distribution chart. Takes raw values, computes bins internally.

**Covers**: return distribution, trade P&L distribution, holding period distribution, VaR visualisation.

```jsx
FKHistogram({
  data,           // number[] — raw values. Bins computed from this.
  binCount,       // number — number of bins. default: auto (Sturges rule)
  binWidth,       // number — fixed bin width. overrides binCount if provided.

  // Overlays
  overlayNormal,  // boolean — draw fitted normal distribution curve. default false
  referenceLines, // Array<{ x, label?, color?, dashed? }>
                  // Common: { x: 0, label: 'Breakeven' }, { x: var95, label: '95% VaR' }

  // Coloring
  colorRule,      // (binMidpoint) => 'gain' | 'loss' | 'warn' | 'neutral' | string
                  // default: bin midpoint >= 0 → gain, < 0 → loss

  // Axis
  xFormat,        // (v) => string — default: v => `${v.toFixed(1)}%`
  yFormat,        // (v) => string — default: count

  height,         // default 220
  title,
  subtitle,
  stats,          // if not provided, auto-generates: mean, std, best, worst, % positive
})
```

**Key rendering rules**:
- Compute bins in the component from raw `data[]` — caller doesn't pre-bin.
- Positive bins: `rgba(22,163,74,0.72)` fill, `#16a34a` stroke.
- Negative bins: `rgba(220,38,38,0.72)` fill, `#dc2626` stroke.
- Normal curve: `#6366f1`, 2px, smooth, no dots. ComposedChart with Line overlay.
- Auto stats strip if `stats` not provided: mean (colored by sign), std dev, best, worst, % positive, N.

**Finance examples**:
```jsx
// Trade return distribution
<FKHistogram data={tradeReturns} overlayNormal
  referenceLines={[{x:0,label:'Breakeven',dashed:true}]}
  title="Trade Return Distribution" />

// VaR histogram
<FKHistogram data={dailyReturns}
  referenceLines={[{x:var95,label:'95% VaR',color:'#dc2626'}]}
  colorRule={(x) => x < var95 ? 'loss' : x < 0 ? 'warn' : 'gain'} />
```

---

### P7 — FKGridChart

**What it is**: A 2D grid where each cell is colored by a value. Rows and columns are
both categorical. This is the single component for all heatmap use cases.

**Covers**: correlation matrix, calendar returns (month × year), sector × period heatmap,
time-of-day × weekday P&L, any value at intersection of two categories.

```jsx
FKGridChart({
  data,           // Array<{ [rowKey]: string, [colKey]: string, [valueKey]: number, label?: string }>
  rowKey,         // string — e.g. 'asset_a', 'month', 'sector', 'hour'
  colKey,         // string — e.g. 'asset_b', 'year', 'period', 'weekday'
  valueKey,       // string — e.g. 'correlation', 'return_pct', 'avg_pnl'

  // Color scale
  colorScale,     // 'diverging'  — negative=red, zero=neutral, positive=green (returns, correlation)
                  // 'sequential' — low=light, high=dark (single direction: volume, AUM)
                  // 'gain-only'  — all positive, intensity = magnitude
                  // default: 'diverging'
  colorDomain,    // [min, max] — override auto-computed domain

  // Display
  showValues,     // boolean — show value text inside cells. default true if cells are large enough
  valueFormat,    // (v) => string — default: v => `${v.toFixed(1)}%`
  shape,          // 'square' | 'circle' — default 'square'
  cellSize,       // number — fixed cell size in px. default: auto-fit
  cellRadius,     // number — border radius. default 6

  // Period selector (for multi-period heatmaps)
  periodKey,      // string — if provided, adds a period selector tab bar
  periods,        // string[] — available period options
  defaultPeriod,  // string

  title,
  subtitle,
  badge,
  stats,
})
```

**Key rendering rules**:
- Diverging color scale (most common):
  ```
  >= +4%:   rgba(22,163,74,0.55)    <= -4%:  rgba(220,38,38,0.55)
  +2–4%:    rgba(22,163,74,0.35)    -2–4%:   rgba(220,38,38,0.35)
  +0.5–2%:  rgba(22,163,74,0.18)    -0.5–2%: rgba(220,38,38,0.18)
  0–0.5%:   rgba(22,163,74,0.08)    0–0.5%:  rgba(220,38,38,0.08)
  ```
- Text color matches cell color family (dark shade of same ramp).
- Cell hover: `opacity: 0.75`, `cursor: default`, smooth transition.
- Color legend: gradient bar at bottom. 5px tall, border-radius 3px.
- Auto-sort rows and columns: for calendar (month order), for correlation (alphabetical).

**Finance examples**:
```jsx
// Correlation matrix
<FKGridChart data={correlations} rowKey="asset_a" colKey="asset_b"
  valueKey="correlation" colorScale="diverging" showValues
  colorDomain={[-1,1]} valueFormat={v=>v.toFixed(2)} title="Correlation Matrix" />

// Monthly returns calendar
<FKGridChart data={calReturns} rowKey="month" colKey="year"
  valueKey="return_pct" colorScale="diverging" showValues
  valueFormat={v=>`${v.toFixed(1)}%`} title="Monthly Returns" />

// Sector × period heatmap
<FKGridChart data={sectorPerf} rowKey="sector" colKey="period"
  valueKey="return_pct" colorScale="diverging"
  periodKey="period" periods={['1D','1W','1M','YTD']} title="Sector Performance" />

// Time-of-day P&L
<FKGridChart data={tradeTiming} rowKey="hour" colKey="weekday"
  valueKey="avg_pnl" colorScale="diverging" title="P&L by Time of Day" />
```

---

### P8 — FKPartChart

**What it is**: Part-of-whole visualization. One component, three rendering modes.

**Covers**: portfolio allocation, sector weights, P&L by ticker, asset class breakdown,
any "how does X break down?" question.

```jsx
FKPartChart({
  data,           // Array<{ [labelKey]: string, [valueKey]: number, [colorKey]?: string }>
  valueKey,       // string — default 'value'
  labelKey,       // string — default 'label'
  colorKey,       // string? — if provided, uses data[colorKey] as color. else auto from palette.

  mode,           // 'donut'   — donut chart + legend with bar breakdown
                  // 'treemap' — squarified treemap, tile size = value
                  // 'bars'    — horizontal bar list, sorted by value
                  // default: 'donut'

  // Donut options
  innerLabel,     // string — center label (e.g. '$94k', 'Total')
  innerSub,       // string — center sub-label (e.g. 'AUM', 'portfolio')
  size,           // number — donut diameter px. default 160

  // Treemap options (mode='treemap')
  colorBy,        // 'value' | 'colorKey' | 'index' — how to color tiles. default 'index'
  // When colorBy='colorKey', each tile is colored by data[colorKey] value
  // (e.g. return_pct — uses diverging scale like FKGridChart)

  // Bars options (mode='bars')
  showTotal,      // boolean — show aggregate total above bars. default true

  height,         // number — default 200 (donut), 260 (treemap), auto (bars)
  title,
  subtitle,
  badge,
})
```

**Key rendering rules**:
- **Donut mode**: Recharts PieChart. `paddingAngle=2`, `strokeWidth=0`.
  Right side: legend with colored square, label, value%, bar proportional to max slice.
  Hover: dim all other slices to 0.4 opacity.
- **Treemap mode**: Squarified algorithm (compute in component, render as absolute-position divs).
  Tile: `border-radius 6px`, `border: 1px solid {color}28`.
  Show label when width > 48px, value when width > 72px.
  Mode switcher tabs: value | return | sector (configurable via `colorBy`).
- **Bars mode**: Sorted descending. Each row: label left, value right, proportional bar.
  Bar height 4px, border-radius 99px. Optional total header.

**Finance examples**:
```jsx
// Portfolio allocation donut
<FKPartChart data={holdings} valueKey="weight" labelKey="ticker"
  mode="donut" innerLabel="$94k" innerSub="total" title="Portfolio Allocation" />

// Portfolio treemap (size=value, color=return)
<FKPartChart data={holdings} valueKey="market_value" labelKey="ticker"
  colorKey="return_pct" mode="treemap" title="Portfolio Map" />

// Sector breakdown bars
<FKPartChart data={sectors} valueKey="weight" labelKey="name"
  mode="bars" showTotal title="Sector Weights" />
```

---

### P9 — FKRangeChart

**What it is**: Shows where a value sits within a min-max range. Multiple rows.
Canvas-rendered.

**Covers**: 52W high/low with current price, price vs analyst target, VaR bands,
mandate limit utilization, options strike range.

```jsx
FKRangeChart({
  data,           // Array<Record<string, any>>
  labelKey,       // string — row label. default 'label'
  minKey,         // string — range minimum. default 'min'
  maxKey,         // string — range maximum. default 'max'
  valueKey,       // string — current value. default 'value'
  targetKey,      // string? — optional target/reference marker (analyst price target)
  value2Key,      // string? — optional second value marker

  // Formatting
  format,         // (v) => string — format all values. default: v => `$${v.toFixed(2)}`
  showValues,     // boolean — show numeric labels. default true

  // Colors
  colorRule,      // (row) => 'gain' | 'loss' | 'warn' | 'neutral'
                  // default: value closer to max → gain, closer to min → loss

  rowHeight,      // number — height per row in px. default 44
  title,
  subtitle,
  badge,
})
```

**Key rendering rules**:
- Canvas rendering. Each row: label left, range bar, value marker, numeric labels.
- Range bar: `rgba(0,0,0,0.08)` background, 6px tall, border-radius 99px.
- Value marker: filled circle on the bar, colored by `colorRule`.
- Target marker: unfilled diamond or triangle in `#6366f1`.
- Position: `(value - min) / (max - min) * barWidth`.
- Value label: shown to the right of the bar.

**Finance examples**:
```jsx
// 52-week range
<FKRangeChart
  data={holdings.map(h => ({
    label: h.ticker, min: h.low52w, max: h.high52w,
    value: h.price, target: h.analystTarget
  }))}
  format={v=>`$${v.toFixed(2)}`}
  title="Price vs 52-Week Range" />

// Portfolio mandate utilization
<FKRangeChart
  data={limits.map(l => ({
    label: l.name, min: 0, max: l.limit, value: l.current
  }))}
  colorRule={(row) => row.value / row.max > 0.9 ? 'loss' : row.value / row.max > 0.75 ? 'warn' : 'gain'}
  format={v=>`${(v*100).toFixed(1)}%`}
  title="Mandate Utilization" />
```

---

### P10 — FKMetricGrid

**What it is**: Grid of KPI cards. The headline block. Always appears first in a layout.

**Covers**: portfolio summary numbers, stock quote, fund summary, any multi-metric snapshot.

```jsx
FKMetricGrid({
  cards,          // Array<{
                  //   label:   string
                  //   value:   string          — pre-formatted main number
                  //   delta?:  number          — drives badge color + top border color
                  //   sub?:    string          — small text beside badge
                  //   color?:  string          — override value color
                  //   spark?:  number[]        — tiny sparkline bottom-right of card
                  //   accent?: string          — left accent bar color (for asset class cards)
                  // }>
  cols,           // 2 | 3 | 4 — default 4
})
```

**Key rendering rules**:
- Card: `border-radius 12px`, `padding 20px 20px 16px`.
- Top border: 2px colored line. Color = `#16a34a` if delta > 0, `#dc2626` if delta < 0,
  `#6366f1` if no delta (neutral default).
- Label: 10px, uppercase, 0.06em letter-spacing, tertiary color.
- Value: 26–28px, monospace, weight 500, line-height 1.
- Delta badge (FKDelta) + sub text on same row below value.
- Sparkline: if `spark` provided, absolute-position bottom-right, 64×24, no dot, no area.
- Left accent bar: if `accent` provided, 3px wide left border in that color.
- Hover: `box-shadow: 0 0 0 1px var(--color-border-secondary)` transition 0.15s.

**Finance examples**:
```jsx
// Portfolio KPIs
<FKMetricGrid cols={4} cards={[
  { label:'Portfolio value', value:'$94,273', delta:1.99, sub:'today' },
  { label:'Total return',    value:'+20.25%', delta:20.25, color:'#16a34a' },
  { label:'Sharpe ratio',    value:'1.84',    sub:'Excellent' },
  { label:'Max drawdown',    value:'−23.4%',  color:'#dc2626', sub:'peak to trough' },
]} />

// Stock quote cards with sparklines
<FKMetricGrid cols={3} cards={[
  { label:'AAPL', value:'$217.30', delta:1.78, spark:priceHistory, sub:'▲ $3.80' },
  { label:'NVDA', value:'$876.40', delta:3.21, spark:nvdaHistory,  sub:'▲ $27.2' },
  { label:'MSFT', value:'$379.91', delta:0.92, spark:msftHistory,  sub:'▲ $3.46' },
]} />
```

---

### P11 — FKDataTable

**What it is**: Sortable, filterable data table with rich cell rendering.

**Covers**: holdings blotter, trade history, screener results, options chain,
any row-level data.

```jsx
FKDataTable({
  columns,        // Array<{
                  //   key:       string
                  //   label:     string
                  //   align?:    'left' | 'right' | 'center' — default 'left'
                  //   mono?:     boolean — monospace font for numbers
                  //   sortable?: boolean — default true
                  //   width?:    string — CSS width
                  //   format?:   (value, row) => ReactNode — custom cell renderer
                  //   colorRule?: (value, row) => 'gain' | 'loss' | 'warn' | 'neutral' | string
                  // }>
  rows,           // Array<Record<string, any>>
  defaultSort,    // string — column key to sort by initially
  defaultDir,     // 'asc' | 'desc' — default 'desc'
  sparkKey,       // string? — if provided, adds sparkline column using this data key
  maxRows,        // number? — truncate with "Showing N of M" footer
  stickyHeader,   // boolean — sticky column headers. default false
  onRowClick,     // (row) => void — optional row click handler

  title,
  subtitle,
  badge,
})
```

**Key rendering rules**:
- Column header: 10px, uppercase, 0.05em spacing, tertiary color.
  Background: `var(--color-background-secondary)`.
  Sort indicator: `↑` / `↓` at 60% opacity. Active column: primary color.
- Row hover: `background: var(--color-background-secondary)`, transition 0.1s.
- `colorRule` result maps to text color: gain→`#16a34a`, loss→`#dc2626`, warn→`#d97706`.
- If `colorRule` returns a full hex/css color, use that directly.
- `sparkKey` adds a column with FKSparkline(data[sparkKey], width=72, height=24).
- Empty state: centered "No data" in tertiary color.
- `maxRows`: shows first N rows + footer "Showing N of {total}  — View all".

**Finance examples**:
```jsx
// Holdings table
<FKDataTable
  defaultSort="value" title="Holdings"
  columns={[
    { key:'ticker', label:'Symbol' },
    { key:'value',  label:'Value',  align:'right', mono:true, format:v=>`$${v.toLocaleString()}` },
    { key:'weight', label:'Weight', align:'right', mono:true, format:v=>`${v.toFixed(1)}%` },
    { key:'return_pct', label:'Return', align:'right', mono:true,
      colorRule: v => v >= 0 ? 'gain' : 'loss',
      format: v => `${v>=0?'+':''}${v.toFixed(2)}%` },
    { key:'sector', label:'Sector' },
  ]}
  sparkKey="price_history"
  rows={holdings} />

// Options chain
<FKDataTable
  title="AAPL Options Chain" stickyHeader
  columns={[
    { key:'strike', label:'Strike', mono:true },
    { key:'expiry', label:'Expiry' },
    { key:'bid',    label:'Bid',    mono:true, align:'right' },
    { key:'ask',    label:'Ask',    mono:true, align:'right' },
    { key:'iv',     label:'IV',     mono:true, align:'right',
      colorRule: v => v > 0.4 ? 'loss' : v > 0.25 ? 'warn' : 'neutral' },
    { key:'delta',  label:'Delta',  mono:true, align:'right',
      colorRule: v => v > 0 ? 'gain' : 'loss' },
    { key:'oi',     label:'OI',     mono:true, align:'right' },
  ]}
  rows={optionsChain} />
```

---

## Complete finance question → primitive mapping

| Question | Primary primitive | Key config |
|---|---|---|
| QQQ 10-year performance | FKLineChart | xType=time, rangeSelector |
| Compare QQQ vs SPY | FKLineChart | multi series, normalized to 100 |
| Rolling Sharpe ratio | FKLineChart | referenceLines y=1 |
| Yield curve | FKLineChart | xType=category, xValues=[tenors] |
| Implied vs realized vol | FKLineChart | 2 series |
| Drawdown history | FKBandChart | baseline=0, fillBelow=#dc2626 |
| Underwater curve | FKBandChart | baseline=0, fillBelow=#dc2626 |
| Monthly P&L | FKBarChart | colorRule by sign |
| Annual returns | FKBarChart | colorRule by sign |
| P&L attribution | FKBarChart | mode=waterfall |
| Earnings beat/miss | FKBarChart | grouped, colorRule by beat |
| PE comparison | FKBarChart | horizontal, referenceValue=median |
| Sector rotation | FKAreaChart | mode=normalized |
| Portfolio allocation | FKPartChart | mode=donut |
| Portfolio treemap | FKPartChart | mode=treemap, colorBy=colorKey |
| Risk vs return | FKScatterChart | xKey=vol, yKey=return, sizeKey=weight |
| Screener scatter | FKScatterChart | xKey=vol, yKey=momentum, colorKey=sector |
| Correlation matrix | FKGridChart | rowKey=a, colKey=b, colorScale=diverging |
| Calendar returns | FKGridChart | rowKey=month, colKey=year |
| Sector heatmap | FKGridChart | rowKey=sector, colKey=period, periodSelector |
| Time-of-day P&L | FKGridChart | rowKey=hour, colKey=weekday |
| Return distribution | FKHistogram | overlayNormal, referenceLines x=0 |
| VaR histogram | FKHistogram | referenceLines x=var95 |
| 52W high/low range | FKRangeChart | min=low52w, max=high52w, target=analystTarget |
| Mandate limits | FKRangeChart | colorRule by utilization % |
| Portfolio KPIs | FKMetricGrid | cols=4, delta drives badge |
| Holdings table | FKDataTable | sparkKey=priceHistory |
| Trade blotter | FKDataTable | colorRule on return_pct |
| Options chain | FKDataTable | stickyHeader, colorRule on IV |
| Screener results | FKDataTable | colorRule quantile-based |

---

## What to build first (priority order)

1. `tokens.js` + `FKCard` + sub-primitives (Badge, Delta, Sparkline, RangeSelector, StatStrip)
2. `FKMetricGrid` — appears in every answer
3. `FKLineChart` — covers 8 question types
4. `FKBarChart` — covers 6 question types
5. `FKGridChart` — covers correlation + calendar + sector heatmap
6. `FKPartChart` — covers allocation, treemap
7. `FKDataTable` — covers holdings, trades, screener
8. `FKBandChart` — covers drawdown
9. `FKScatterChart` — covers risk/return
10. `FKHistogram` — covers distributions
11. `FKAreaChart` — covers sector rotation
12. `FKRangeChart` — covers 52W range, limits

## Export

Single entry point `src/index.js` exports everything.
Include a `README.md` with one usage example per primitive.
Include a `demo.html` (self-contained, CDN React + Recharts) that renders every primitive
with realistic financial mock data so the output can be verified without a build step.
