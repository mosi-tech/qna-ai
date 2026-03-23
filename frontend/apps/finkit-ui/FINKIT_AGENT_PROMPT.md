# FINKIT Primitives — Coding Agent Prompt

## Your role

You are building **FINKIT**, a generic React visualization primitive library for financial analytics dashboards. You are a senior frontend engineer. You write clean, production-quality React. You do not improvise — you follow the spec below exactly.

---

## What you are building

A library of **18 React components** that are the visual foundation for any financial dashboard. These components know nothing about finance. They know about data shapes and visual encodings. Finance-specific meaning lives in how the props are configured and how data is prepared before it reaches the component.

The principle: **a drawdown chart is not a component. It is `FKAreaChart` with `fillMode="below"` and `fillReference={0}`. An earnings chart is not a component. It is `FKBarChart` with a `colorRule` that fires on beat/miss.** Every investment visualization maps to one of these 15 primitives via props configuration alone.

---

## Constraints — read these before writing a single line

1. **React 18 functional components + hooks only.** No class components.
2. **Recharts** for all chart rendering except `FKRangeChart`, `FKScatterChart`, `FKBulletChart`, and `FKWaterfall` which use raw Canvas or pure SVG.
3. **Tailwind CSS for all styling.** Use utility classes directly on JSX elements. No inline style objects except where Tailwind cannot express the value (e.g. exact pixel chart dimensions passed as props). No CSS modules. No styled-components.
4. **CSS variables for all surfaces and text colors.** Semantic finance colors (`gain`, `loss`) are hardcoded hex — never use CSS variables for those.
5. **No dependencies beyond React, Recharts, and Tailwind.** If you think you need another library, find a way to do it without.
6. **Every component must run with sample data when no props are passed.** This is non-negotiable — components must be self-demonstrating.
7. **Do not invent props** not listed in the spec. If something is unclear, implement the simpler interpretation.

---

## How to work through this

Work file by file in this exact order. Do not skip ahead.

```
1.  src/tokens.js              ← shared design tokens, import this everywhere
2.  src/FKCard.jsx             ← shared card wrapper, used by every component
3.  src/FKTooltip.jsx          ← universal tooltip component, used by every chart
4.  src/FKRangeSelector.jsx    ← period tab bar, used by all time-series charts
5.  src/FKSparkline.jsx        ← inline mini chart, used inside other components
6.  src/FKMetricGrid.jsx       ← KPI headline block
7.  src/FKLineChart.jsx        ← continuous x-axis, one or more series + step interpolation
8.  src/FKAreaChart.jsx        ← filled regions: above / below / between / stacked
9.  src/FKAnnotatedChart.jsx   ← line/area + events[] markers + bands[] + callouts[] overlays
10. src/FKMultiPanel.jsx       ← synchronized multi-panel chart (price + indicators, shared x-axis)
11. src/FKProjectionChart.jsx  ← historical line → projected fan with confidence bands
12. src/FKBarChart.jsx         ← categorical bars: grouped / stacked / lollipop
13. src/FKWaterfall.jsx        ← bars that flow from a running total (P&L bridge, revenue walk)
14. src/FKScatterChart.jsx     ← two-axis, size + color encoding (Canvas)
15. src/FKHeatGrid.jsx         ← two categorical dims, value → cell color
16. src/FKPartChart.jsx        ← part-of-whole: donut / treemap / stacked-bar
17. src/FKRangeChart.jsx       ← value within min-max range (Canvas)
18. src/FKBulletChart.jsx      ← performance bar inside a range with a target marker (Canvas)
19. src/FKCandleChart.jsx      ← OHLCV candlestick + volume
20. src/FKTimeline.jsx         ← events/durations on a time axis (dots or bars)
21. src/FKRadarChart.jsx       ← multivariate scores on radial axes (factor profiles, ESG)
22. src/FKSankeyChart.jsx      ← flow between categories (revenue decomposition, fund flows)
23. src/FKTable.jsx            ← sortable table with format + color rules + pivot mode
24. src/FKRankedList.jsx       ← ordered rows with metrics + sparklines
25. src/index.js               ← export everything
```

After all 25 files are complete, create a `src/showcase/Showcase.jsx` that renders every component with sample data so everything can be visually verified in one place.

---

## File structure

```
finkit-uikit/
├── package.json
├── src/
│   ├── tokens.js
│   ├── FKCard.jsx
│   ├── FKTooltip.jsx
│   ├── FKRangeSelector.jsx
│   ├── FKSparkline.jsx
│   ├── FKMetricGrid.jsx
│   ├── FKLineChart.jsx
│   ├── FKAreaChart.jsx
│   ├── FKAnnotatedChart.jsx
│   ├── FKMultiPanel.jsx
│   ├── FKProjectionChart.jsx
│   ├── FKBarChart.jsx
│   ├── FKWaterfall.jsx
│   ├── FKScatterChart.jsx
│   ├── FKHeatGrid.jsx
│   ├── FKPartChart.jsx
│   ├── FKRangeChart.jsx
│   ├── FKBulletChart.jsx
│   ├── FKCandleChart.jsx
│   ├── FKTimeline.jsx
│   ├── FKRadarChart.jsx
│   ├── FKSankeyChart.jsx
│   ├── FKTable.jsx
│   ├── FKRankedList.jsx
│   ├── index.js
│   └── showcase/
│       └── Showcase.jsx
```

---

## Definition of done

- [ ] All 25 source files created
- [ ] Every component renders without errors when no props are passed (uses built-in sample data)
- [ ] `FKTooltip` is used by every chart — no chart uses Recharts' default tooltip appearance
- [ ] `FKRangeSelector` appears in the card header of all time-series charts: FKLineChart, FKAreaChart, FKAnnotatedChart, FKCandleChart, FKMultiPanel, FKProjectionChart
- [ ] `FKLineChart` supports `interpolation='step'` for Fed rate / dividend / tier charts
- [ ] `FKAreaChart` correctly handles all four `fillMode` values: `above`, `below`, `between`, `stacked`
- [ ] `FKAnnotatedChart` correctly renders `events[]` markers, `bands[]` overlays, and `callouts[]` text boxes — independently and combined
- [ ] `FKAnnotatedChart` marker shapes: `triangle-up`, `triangle-down`, `circle`, `diamond` all working
- [ ] `FKMultiPanel` panels share the same x-axis — hover crosshair and zoom synchronized across all panels
- [ ] `FKProjectionChart` renders solid historical line transitioning to dashed projected line with widening confidence fan
- [ ] `FKBarChart` supports `mode='lollipop'` in addition to `grouped` and `stacked`
- [ ] `FKWaterfall` bars flow from a running total — bars do NOT start at zero
- [ ] `FKPartChart` correctly handles `donut`, `treemap`, and `stacked-bar` modes
- [ ] `FKRangeChart`, `FKScatterChart`, and `FKBulletChart` use Canvas with ResizeObserver and use `FKTooltip.Box` for hover tooltips
- [ ] `FKTimeline` renders dots for point events and horizontal bars for duration events (when both `from` and `to` are provided)
- [ ] `FKRadarChart` renders multivariate scores on radial axes with optional comparison series
- [ ] `FKSankeyChart` renders node-flow layout between two or more category sets
- [ ] `FKTable` supports optional `pivotRow` / `pivotCol` / `pivotValue` props for dynamic pivot mode
- [ ] All colors come from `tokens.js` — no hardcoded color literals except inside tokens.js itself
- [ ] `Showcase.jsx` renders all 20 components visually with sample data

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
  ScatterChart, RadarChart, ResponsiveContainer, XAxis, YAxis, Tooltip, ReferenceLine, Cell)
- Raw Canvas (via useRef + useEffect) for FKRangeChart, FKScatterChart, FKBulletChart
- Tailwind CSS v3 for all styling (utility classes on JSX, no inline style objects except
  for dynamic values like chart dimensions or data-driven colors)
- CSS variables for all surfaces and text colors (dark mode automatic)
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
  stroke:          'var(--color-border-tertiary)',
  vertical:        false,
  strokeDasharray: '2 4',
}

// Base style object for the Recharts <Tooltip> wrapperStyle prop.
// Every chart passes this to wrapperStyle — do NOT also pass contentStyle or itemStyle.
// All visual customisation is done through FKTooltip (see below).
export const tooltipStyle = {
  background:   'var(--color-background-primary)',
  border:       '0.5px solid var(--color-border-secondary)',
  borderRadius: 8,
  padding:      '10px 14px',
  fontSize:     12,
  fontFamily:   'var(--font-mono)',
  boxShadow:    '0 4px 16px rgba(0,0,0,0.08)',
  outline:      'none',
}

// Default range selector options — charts use this unless overridden
export const defaultRangeOptions = ['1M', '3M', '6M', '1Y', '3Y', '5Y', 'ALL']
```

---

## Shared tooltip (put in `src/FKTooltip.jsx`, import into every chart)

Every chart uses this single tooltip component. This ensures consistent formatting,
dark mode support, and layout across all chart types. Never use Recharts' default tooltip
appearance directly — always pass `content={<FKTooltip ... />}` or use the factory function.

```jsx
// FKTooltip — universal custom tooltip for all FK charts
//
// Usage with Recharts:
//   <Tooltip content={<FKTooltip xFormat={formatDate} valueFormat={formatUSD} />} />
//
// Or with canvas charts (FKScatterChart, FKBulletChart, FKRangeChart):
//   render a <FKTooltip.Box> positioned absolutely at {x, y} with items you build manually

export function FKTooltip({ xFormat, valueFormat, colorMap, active, payload, label }) {
  if (!active || !payload?.length) return null

  return (
    <div style={tooltipStyle}>
      {/* Header: the x-axis value (date, category) */}
      <div className="text-[11px] text-[var(--color-text-tertiary)] font-mono mb-2 pb-1.5
                      border-b border-[var(--color-border-tertiary)]">
        {xFormat ? xFormat(label) : label}
      </div>

      {/* Rows: one per series */}
      {payload.map((entry, i) => (
        <div key={i} className="flex items-center justify-between gap-4 mt-1">
          <div className="flex items-center gap-1.5">
            <span style={{ background: colorMap?.[entry.dataKey] ?? entry.color }}
                  className="inline-block w-2 h-2 rounded-full flex-shrink-0" />
            <span className="text-[11px] text-[var(--color-text-secondary)] font-mono">
              {entry.name ?? entry.dataKey}
            </span>
          </div>
          <span className="text-[11px] text-[var(--color-text-primary)] font-mono font-medium">
            {valueFormat ? valueFormat(entry.value) : entry.value}
          </span>
        </div>
      ))}
    </div>
  )
}

// FKTooltip.Box — for canvas charts that manage their own hover state
// Wrap this around manually constructed tooltip content
FKTooltip.Box = function TooltipBox({ children, style }) {
  return (
    <div style={{ ...tooltipStyle, position: 'absolute', pointerEvents: 'none', ...style }}>
      {children}
    </div>
  )
}

// FKTooltip.Header — reusable header row (date / category label)
FKTooltip.Header = function TooltipHeader({ children }) {
  return (
    <div className="text-[11px] text-[var(--color-text-tertiary)] font-mono mb-2 pb-1.5
                    border-b border-[var(--color-border-tertiary)]">
      {children}
    </div>
  )
}

// FKTooltip.Row — reusable value row with color dot, label, value
FKTooltip.Row = function TooltipRow({ color, label, value }) {
  return (
    <div className="flex items-center justify-between gap-4 mt-1">
      <div className="flex items-center gap-1.5">
        <span style={{ background: color }}
              className="inline-block w-2 h-2 rounded-full flex-shrink-0" />
        <span className="text-[11px] text-[var(--color-text-secondary)] font-mono">{label}</span>
      </div>
      <span className="text-[11px] text-[var(--color-text-primary)] font-mono font-medium">
        {value}
      </span>
    </div>
  )
}
```

**Tooltip rules that apply to every chart:**
- Always use `<FKTooltip>` — never Recharts' default tooltip appearance
- `xFormat` formats the header (date → "Jan 15, 2024", number → "Q3 2023")
- `valueFormat` formats every value row (default: raw number)
- `colorMap` overrides Recharts' entry color — use this when series colors are data-driven
- Canvas charts (FKScatterChart, FKRangeChart, FKBulletChart) use `FKTooltip.Box` +
  `FKTooltip.Header` + `FKTooltip.Row` manually, positioned via `position: absolute`
- Tooltip must never clip outside the card boundary — use Recharts' `allowEscapeViewBox`
  or constrain canvas tooltip position to card bounds

---

## Shared range selector (put in `src/FKRangeSelector.jsx`, import into charts that need it)

A period tab bar rendered in the card header. Charts that display time-series data
**must** support a range selector. This includes: FKLineChart, FKAreaChart,
FKAnnotatedChart, FKCandleChart, FKMultiPanel, FKProjectionChart.

Charts that show categorical or relational data (FKBarChart, FKHeatGrid, FKScatterChart,
FKPartChart, FKRadarChart, FKSankeyChart) do NOT get a range selector — they show
whatever data they receive.

```jsx
// FKRangeSelector — period tab bar for time-series charts
//
// Usage:
//   <FKRangeSelector options={['1M','3M','1Y','5Y','ALL']} value={range} onChange={setRange} />

export function FKRangeSelector({ options = defaultRangeOptions, value, onChange }) {
  return (
    <div className="flex items-center gap-0.5 bg-[var(--color-background-tertiary)]
                    rounded-md p-0.5">
      {options.map(opt => (
        <button
          key={opt}
          onClick={() => onChange(opt)}
          className={[
            'px-2.5 py-1 rounded text-[11px] font-mono font-medium transition-colors',
            value === opt
              ? 'bg-[var(--color-background-primary)] text-[var(--color-text-primary)] shadow-sm'
              : 'text-[var(--color-text-tertiary)] hover:text-[var(--color-text-secondary)]'
          ].join(' ')}
        >
          {opt}
        </button>
      ))}
    </div>
  )
}
```

**Range selector rules that apply to every time-series chart:**
- Range selector always sits in the **top-right of the card header**, inline with the title
- The selected range filters the data slice shown — the chart component handles the slicing
  internally based on the selected option and the latest date in the data
- `defaultRange` prop sets the initial selection — default is `'1Y'` if data supports it,
  otherwise the largest available range
- `onRangeChange` is optional — if not provided, the chart manages range state internally
- When the data window changes, x-axis ticks and y-axis domain must recalculate
- `'ALL'` option always shows the full dataset regardless of date range

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

---

## New primitives — added from gap analysis

These three components were identified as genuine gaps that cannot be expressed by configuring existing primitives. Build them with the same discipline as the others.

---

### FKWaterfall

**What it encodes:** Bars that flow from a running total. Each bar starts where the previous one ended. Used for P&L attribution, revenue bridges, cost breakdowns, earnings walks — any question of the form "how did we get from A to B?"

**Why FKBarChart cannot cover this:** FKBarChart bars always start at zero. Waterfall bars start at the previous cumulative value. This is a fundamentally different visual encoding.

**Props:**
```js
FKWaterfall.propTypes = {
  data: PropTypes.arrayOf(PropTypes.shape({
    label:  PropTypes.string.isRequired,  // e.g. "Q3 Revenue", "COGS", "OpEx", "Net Income"
    value:  PropTypes.number.isRequired,  // positive = up bar, negative = down bar
    type:   PropTypes.oneOf(['start', 'delta', 'end']), // 'start' and 'end' bars go from zero
  })),
  title:      PropTypes.string,
  subtitle:   PropTypes.string,
  height:     PropTypes.number,           // default 320
  valueFormat: PropTypes.func,            // default: (v) => v.toLocaleString()
}
```

**Rendering rules:**
- `start` and `end` type bars always go from zero to their value (total bars, rendered in neutral color)
- `delta` type bars: positive = `color.gain`, negative = `color.loss`, start from running total
- Draw a thin connector line between the top of each bar and the start of the next
- Show the value label above/below each bar
- x-axis shows labels, y-axis shows running total scale

**Sample data:**
```js
const sample = [
  { label: 'Q2 Revenue', value: 850, type: 'start' },
  { label: 'New Contracts', value: 120, type: 'delta' },
  { label: 'Churn', value: -45, type: 'delta' },
  { label: 'Upsell', value: 60, type: 'delta' },
  { label: 'FX Impact', value: -20, type: 'delta' },
  { label: 'Q3 Revenue', value: 965, type: 'end' },
]
```

---

### FKBulletChart

**What it encodes:** A performance bar positioned inside a qualitative range, with a target marker. Used for "price vs analyst target", "actual vs budget", "EPS vs guidance", "portfolio vs benchmark". The key visual is: here is where we are, here is the range we expected, here is the target.

**Why FKRangeChart cannot cover this:** FKRangeChart shows a value positioned in a range — a dot or marker. FKBulletChart shows a *filled bar* representing performance up to the current value, layered inside a background range. Different visual encoding, different question answered.

**Props:**
```js
FKBulletChart.propTypes = {
  data: PropTypes.arrayOf(PropTypes.shape({
    label:    PropTypes.string.isRequired,   // e.g. "AAPL", "Revenue", "Portfolio"
    value:    PropTypes.number.isRequired,   // current actual value
    target:   PropTypes.number.isRequired,   // target / consensus / benchmark
    rangeMin: PropTypes.number.isRequired,   // low end of expected range
    rangeMax: PropTypes.number.isRequired,   // high end of expected range
    format:   PropTypes.func,                // optional per-row formatter
  })),
  title:       PropTypes.string,
  subtitle:    PropTypes.string,
  valueFormat: PropTypes.func,              // default: (v) => v.toFixed(2)
}
```

**Rendering rules:**
- Background band = full rangeMin → rangeMax (light neutral fill)
- Foreground bar = 0 → value (narrow, `color.gain` if value >= target, `color.loss` if below)
- Target marker = a vertical tick line at the target position (2px wide, dark)
- Multiple rows stack vertically — one bullet per data item
- Labels on the left, values on the right

**Sample data:**
```js
const sample = [
  { label: 'AAPL price target', value: 213, target: 225, rangeMin: 180, rangeMax: 260 },
  { label: 'Q3 EPS',            value: 1.52, target: 1.43, rangeMin: 1.20, rangeMax: 1.65 },
  { label: 'Revenue ($B)',      value: 89.5, target: 92.0, rangeMin: 84.0, rangeMax: 96.0 },
]
```

---

### FKTimeline

**What it encodes:** Events positioned on a horizontal time axis, optionally grouped into rows. Used for earnings calendars, economic event schedules, dividend dates, Fed meeting calendars, lock-up expirations, watchlist event views. The key question: *when does something happen?*

**Why FKTable cannot cover this:** FKTable with date columns is a lookup tool, not a visual time axis. FKTimeline communicates relative spacing between events — two events in the same week look close together, events a quarter apart look far apart. That temporal spacing is the information.

**Props:**
```js
FKTimeline.propTypes = {
  events: PropTypes.arrayOf(PropTypes.shape({
    date:     PropTypes.string.isRequired,  // ISO date string "2025-01-29"
    label:    PropTypes.string.isRequired,  // e.g. "AAPL Earnings"
    row:      PropTypes.string,             // optional grouping row label e.g. "Earnings", "Dividends"
    type:     PropTypes.string,             // optional: drives dot color via colorMap
    value:    PropTypes.string,             // optional: shown in tooltip e.g. "EPS $2.84 (+6.4%)"
  })),
  dateMin:   PropTypes.string,             // ISO — start of visible window, default: earliest event
  dateMax:   PropTypes.string,             // ISO — end of visible window, default: latest event
  colorMap:  PropTypes.object,             // { [type]: color } — maps event type to dot color
  title:     PropTypes.string,
  subtitle:  PropTypes.string,
  height:    PropTypes.number,             // default: auto based on row count
}
```

**Rendering rules:**
- Horizontal axis = time, scaled linearly between dateMin and dateMax
- Each event = a dot (10px circle) positioned at its date
- If `row` is provided, events group into labeled swim lanes (one row per unique `row` value)
- If no `row`, all events share a single lane
- Dot color driven by `type` + `colorMap`; default = `color.series[0]`
- Today's date shown as a vertical reference line (dashed, neutral)
- Hover on dot shows tooltip with label, date, and value
- x-axis shows month/year ticks at sensible intervals

**Sample data:**
```js
const sample = [
  { date: '2025-01-30', label: 'AAPL Q1', row: 'Earnings', type: 'beat', value: 'EPS $2.40 (+1.7%)' },
  { date: '2025-02-06', label: 'MSFT Q2', row: 'Earnings', type: 'beat', value: 'EPS $3.23 (+3.8%)' },
  { date: '2025-02-13', label: 'AAPL Div', row: 'Dividends', type: 'dividend', value: '$0.25/share' },
  { date: '2025-03-19', label: 'Fed Meeting', row: 'Macro', type: 'fed', value: 'Rate hold expected' },
  { date: '2025-05-01', label: 'AAPL Q2', row: 'Earnings', type: 'miss', value: 'EPS $1.65 (+1.2%)' },
  { date: '2025-05-07', label: 'Fed Meeting', row: 'Macro', type: 'fed', value: 'Rate decision' },
]
const colorMap = { beat: '#16a34a', miss: '#dc2626', dividend: '#6366f1', fed: '#f59e0b' }
```

---

### FKAnnotatedChart

**What it encodes:** A line or area chart with two types of overlays rendered directly on the same canvas — typed event markers at specific dates, and shaded background bands across date ranges. This is the canonical chart for any signal-based or regime-based analysis.

**Why no existing primitive covers this:**
- `FKLineChart` draws series only — no overlay layer
- `FKTimeline` is a separate swim-lane view — cannot overlay onto a price chart
- `FKCandleChart` has `referenceLines[]` but only plain vertical lines, not typed markers with shapes or tooltips
- `FKAreaChart` has no event or band overlay capability

This pattern appears in two confirmed question categories:
1. **Backtest analysis** — price + indicator lines + buy ▲ / sell ▼ markers
2. **Regime analysis** — price + shaded date ranges (oil-up periods, recessions, Fed hiking cycles)

**Props:**
```js
FKAnnotatedChart.propTypes = {
  // Series data — same shape as FKLineChart
  data: PropTypes.arrayOf(PropTypes.object).isRequired, // array of { date, [key]: value }
  xKey: PropTypes.string,                // default: 'date'
  series: PropTypes.arrayOf(PropTypes.shape({
    key:       PropTypes.string.isRequired,
    label:     PropTypes.string,
    color:     PropTypes.string,
    type:      PropTypes.oneOf(['line', 'area']), // default: 'line'
    fillMode:  PropTypes.oneOf(['above', 'below']), // only when type='area'
    strokeDash: PropTypes.string,        // e.g. '4 2' for dashed SMA lines
  })),

  // Overlay 1: point events — dots or shaped markers at specific dates
  events: PropTypes.arrayOf(PropTypes.shape({
    date:    PropTypes.string.isRequired, // ISO date
    type:    PropTypes.string,            // drives shape + color via colorMap
    label:   PropTypes.string,            // shown in tooltip
    value:   PropTypes.string,            // shown in tooltip e.g. '+6.4% surprise'
  })),

  // Overlay 2: background bands — shaded date ranges
  bands: PropTypes.arrayOf(PropTypes.shape({
    from:    PropTypes.string.isRequired, // ISO date — band start
    to:      PropTypes.string.isRequired, // ISO date — band end
    color:   PropTypes.string,            // fill color, default: rgba(99,102,241,0.08)
    label:   PropTypes.string,            // shown in legend + tooltip
  })),

  // Event marker appearance
  colorMap: PropTypes.object,            // { [type]: color } e.g. { buy: '#16a34a', sell: '#dc2626' }
  shapeMap: PropTypes.object,            // { [type]: 'triangle-up' | 'triangle-down' | 'circle' | 'diamond' }
                                         // default: { buy: 'triangle-up', sell: 'triangle-down' }

  title:       PropTypes.string,
  subtitle:    PropTypes.string,
  height:      PropTypes.number,         // default: 320
  valueFormat: PropTypes.func,
}
```

**Rendering rules:**
- Bands render first (lowest z-order) — semi-transparent fills behind all series and markers
- Series lines render next — same rules as FKLineChart (shared axis, tooltip, legend)
- Event markers render on top — positioned at their date on the x-axis, vertically centered on the nearest series value
- Marker shapes: `triangle-up` (▲ 10px), `triangle-down` (▼ 10px), `circle` (8px dot), `diamond` (◆ 10px)
- Hover on marker shows tooltip: label, date, value
- Hover on band region shows band label
- Legend shows: series labels + event type legend (colored shape + label) + band legend (colored swatch + label)
- x-axis and y-axis follow the same token styles as FKLineChart

**Sample data — backtest use case:**
```js
const data = [
  { date: '2020-01-02', price: 212, sma10: 208, sma200: 195 },
  { date: '2020-03-15', price: 165, sma10: 190, sma200: 192 },
  // ... daily data
]
const series = [
  { key: 'price',  label: 'QQQ Price', color: '#6366f1' },
  { key: 'sma10',  label: 'SMA 10',    color: '#f59e0b', strokeDash: '4 2' },
  { key: 'sma200', label: 'SMA 200',   color: '#94a3b8', strokeDash: '4 2' },
]
const events = [
  { date: '2020-04-02', type: 'buy',  label: 'Crossover buy',  value: 'SMA10 crossed above SMA200' },
  { date: '2020-09-14', type: 'sell', label: 'Crossover sell', value: 'SMA10 crossed below SMA200' },
]
const colorMap = { buy: '#16a34a', sell: '#dc2626' }
const shapeMap = { buy: 'triangle-up', sell: 'triangle-down' }
```

**Sample data — regime use case:**
```js
const data = [
  { date: '2020-01-02', oil: 62.2, xom: 70.1 },
  // ... daily data
]
const series = [
  { key: 'oil', label: 'Oil (WTI)', color: '#f59e0b' },
  { key: 'xom', label: 'XOM',       color: '#6366f1' },
]
const bands = [
  { from: '2021-10-01', to: '2022-06-30', color: 'rgba(22,163,74,0.10)',  label: 'Oil up regime' },
  { from: '2020-03-01', to: '2020-05-01', color: 'rgba(220,38,38,0.10)', label: 'Oil crash' },
]
```

---

### FKMultiPanel

**What it encodes:** A vertically stacked set of chart panels that share the same x-axis. The top panel is always the primary series (price, equity curve). Below it sit one or more indicator panels (RSI, MACD, volume, ATR). All panels respond to the same hover crosshair and zoom interaction — when you hover or zoom on any panel, all panels update together.

**Why no existing primitive covers this:** You cannot fake this by stacking multiple `FKLineChart` instances. Separate components have separate x-axes, separate hover states, and separate zoom controls. The synchronized crosshair and shared time axis are the entire value of this primitive — they are impossible without a single coordinated render.

**Props:**
```js
FKMultiPanel.propTypes = {
  data: PropTypes.arrayOf(PropTypes.object).isRequired, // shared dataset, all panels read from this
  xKey: PropTypes.string,                // default: 'date'

  panels: PropTypes.arrayOf(PropTypes.shape({
    id:       PropTypes.string.isRequired,
    height:   PropTypes.number,           // px, default: first panel 280, subsequent 120
    series: PropTypes.arrayOf(PropTypes.shape({
      key:        PropTypes.string.isRequired,
      label:      PropTypes.string,
      color:      PropTypes.string,
      type:       PropTypes.oneOf(['line', 'area', 'bar']), // default: 'line'
      fillMode:   PropTypes.oneOf(['above', 'below']),      // only when type='area'
      strokeDash: PropTypes.string,
    })),
    referenceLines: PropTypes.arrayOf(PropTypes.shape({
      y:     PropTypes.number,
      label: PropTypes.string,
      color: PropTypes.string,
      dash:  PropTypes.string,
    })),
    yDomain:  PropTypes.arrayOf(PropTypes.number), // [min, max] — e.g. [0, 100] for RSI
    yLabel:   PropTypes.string,                    // panel label shown on y-axis
  })),

  title:    PropTypes.string,
  subtitle: PropTypes.string,
}
```

**Rendering rules:**
- Panels stack vertically inside a single card, separated by a 1px border
- All panels share exactly the same x-axis scale — the bottom panel renders x-axis ticks, upper panels render none
- Hover crosshair is a single vertical line that spans all panels simultaneously
- Tooltip aggregates values from all panels at the hovered date into one tooltip
- Each panel has its own independent y-axis and y-scale
- `referenceLines` on RSI panel: horizontal dashed lines at y=30 and y=70 (overbought/oversold)
- Bar series in a panel (e.g. volume) renders as filled bars from zero, color from `color.series`

**Sample data:**
```js
const data = [
  { date: '2024-01-02', price: 412, sma20: 408, volume: 52000000, rsi: 58 },
  { date: '2024-01-03', price: 408, sma20: 409, volume: 61000000, rsi: 52 },
  // ...
]
const panels = [
  {
    id: 'price',
    height: 280,
    yLabel: 'Price',
    series: [
      { key: 'price', label: 'QQQ', color: '#6366f1' },
      { key: 'sma20', label: 'SMA 20', color: '#f59e0b', strokeDash: '4 2' },
    ],
  },
  {
    id: 'volume',
    height: 80,
    yLabel: 'Volume',
    series: [{ key: 'volume', label: 'Volume', color: '#94a3b8', type: 'bar' }],
  },
  {
    id: 'rsi',
    height: 100,
    yLabel: 'RSI',
    yDomain: [0, 100],
    referenceLines: [
      { y: 70, label: 'Overbought', color: '#dc2626', dash: '3 3' },
      { y: 30, label: 'Oversold',   color: '#16a34a', dash: '3 3' },
    ],
    series: [{ key: 'rsi', label: 'RSI (14)', color: '#8b5cf6' }],
  },
]
```

---

### FKProjectionChart

**What it encodes:** A line that splits at a "today" point — to the left is historical (solid line), to the right is projected (dashed line) with a widening confidence fan showing percentile bands. Used for Monte Carlo retirement projections, analyst price targets, and bull/base/bear scenario analysis.

**Why `FKAreaChart` cannot cover this:** `FKAreaChart` with `fillMode=between` fakes a single band. A projection fan needs: (1) a solid-to-dashed line transition at a specific date, (2) multiple nested percentile bands that widen as they go further into the future, (3) a distinct visual language that communicates "this is a forecast, not history." These three things together require a dedicated primitive.

**Props:**
```js
FKProjectionChart.propTypes = {
  // Historical data — rendered as solid line
  historical: PropTypes.arrayOf(PropTypes.shape({
    date:  PropTypes.string.isRequired,
    value: PropTypes.number.isRequired,
  })).isRequired,

  // Projection data — rendered as dashed median + confidence bands
  projection: PropTypes.arrayOf(PropTypes.shape({
    date:   PropTypes.string.isRequired,
    median: PropTypes.number.isRequired,  // central dashed line
    p10:    PropTypes.number,             // 10th percentile — outer band lower bound
    p25:    PropTypes.number,             // 25th percentile — inner band lower bound
    p75:    PropTypes.number,             // 75th percentile — inner band upper bound
    p90:    PropTypes.number,             // 90th percentile — outer band upper bound
  })),

  // Optional scenario lines (bull/base/bear — no bands, just labeled lines)
  scenarios: PropTypes.arrayOf(PropTypes.shape({
    key:   PropTypes.string.isRequired,
    label: PropTypes.string,
    color: PropTypes.string,
    data:  PropTypes.arrayOf(PropTypes.shape({ date: PropTypes.string, value: PropTypes.number })),
  })),

  splitDate:   PropTypes.string,   // ISO date where historical ends and projection begins. Default: last historical date
  valueFormat: PropTypes.func,     // default: (v) => '$' + Math.round(v).toLocaleString()
  title:       PropTypes.string,
  subtitle:    PropTypes.string,
  height:      PropTypes.number,   // default: 320
}
```

**Rendering rules:**
- Historical line: solid, `color.series[0]`, full opacity
- Projection median: dashed (`strokeDash='5 3'`), same color as historical line
- Inner band (p25–p75): filled area, `color.seriesBg[0]`, ~0.35 opacity — labeled "50% range" in legend
- Outer band (p10–p90): filled area, `color.seriesBg[0]`, ~0.15 opacity — labeled "80% range" in legend
- A vertical dashed line at `splitDate` separates historical from projection, labeled "Today" or the date
- If `scenarios` provided instead of percentile bands: render each as a distinct dashed line with its label, no fan
- Legend shows: historical line, median projection, inner band swatch, outer band swatch (or scenario lines)
- Tooltip shows all values at hovered date: historical value OR median + p25/p75/p10/p90

**Sample data — Monte Carlo fan:**
```js
const historical = [
  { date: '2020-01-01', value: 100000 },
  { date: '2021-01-01', value: 118000 },
  { date: '2022-01-01', value: 109000 },
  { date: '2023-01-01', value: 134000 },
  { date: '2024-01-01', value: 158000 },
]
const projection = [
  { date: '2025-01-01', median: 172000, p10: 145000, p25: 158000, p75: 189000, p90: 210000 },
  { date: '2027-01-01', median: 205000, p10: 155000, p25: 178000, p75: 238000, p90: 278000 },
  { date: '2030-01-01', median: 260000, p10: 172000, p25: 210000, p75: 325000, p90: 410000 },
]
```

**Sample data — bull/base/bear scenarios:**
```js
const scenarios = [
  { key: 'bull', label: 'Bull case (+15%/yr)', color: '#16a34a',
    data: [{ date: '2025-01-01', value: 182000 }, { date: '2030-01-01', value: 366000 }] },
  { key: 'base', label: 'Base case (+8%/yr)',  color: '#6366f1',
    data: [{ date: '2025-01-01', value: 170000 }, { date: '2030-01-01', value: 250000 }] },
  { key: 'bear', label: 'Bear case (+2%/yr)',  color: '#dc2626',
    data: [{ date: '2025-01-01', value: 161000 }, { date: '2030-01-01', value: 178000 }] },
]
```

---

### FKAnnotatedChart — callouts[] extension

**This is not a new component.** It is a third overlay prop added to `FKAnnotatedChart`, which already supports `events[]` and `bands[]`. Add `callouts[]` to the existing `FKAnnotatedChart` prop API.

**What callouts add:** A text label box pinned to a specific date and value coordinate on the chart, connected to that point by a thin leader line. Used by journalists and analysts to label significant events directly on the chart: "Fed hikes 75bps", "SVB collapse", "Earnings miss −12%".

**Difference from events[]:** `events[]` places a small shape marker (▲▼●◆) at a coordinate — good for high-density signals like trade entries. `callouts[]` places a readable text box — good for low-density, high-importance labeled annotations where the text itself is the content.

**Add to FKAnnotatedChart propTypes:**
```js
callouts: PropTypes.arrayOf(PropTypes.shape({
  date:     PropTypes.string.isRequired,  // ISO date — x position
  value:    PropTypes.number,             // y position (data value). If omitted, pins to top of chart area
  label:    PropTypes.string.isRequired,  // text shown in the callout box
  position: PropTypes.oneOf(['above', 'below']), // default: 'above'
  color:    PropTypes.string,             // callout box border + text color, default: color.series[0]
})),
```

**Rendering rules for callouts:**
- Callout box: small rounded rect (border-radius 4px), 0.5px border in `color`, background `surface.card`
- Text: 11px mono, same `color` as border
- Leader line: thin 0.5px line from the box to the data point coordinate, dashed
- Dot at the data point coordinate: 4px filled circle, same `color`
- Callouts must not overlap each other — if two callouts land within 80px on the x-axis, offset the second one vertically
- Callouts render above series lines and bands, but below tooltip

**Sample data:**
```js
const callouts = [
  { date: '2022-03-16', value: 320, label: 'Fed hikes 25bps', color: '#f59e0b' },
  { date: '2023-03-10', value: 285, label: 'SVB collapse',    color: '#dc2626', position: 'below' },
  { date: '2024-09-18', value: 480, label: 'Fed cuts 50bps',  color: '#16a34a' },
]
```

---

### FKRadarChart

**What it encodes:** Multivariate scores on radial axes — each axis represents one dimension, the polygon shape formed by connecting the scores is the information. Used for factor profiles (value, quality, momentum, growth, safety), ESG scores, analyst rating dimensions, stock screener comparisons. The visual "shape" communicates the overall profile at a glance — something a bar chart cannot do.

**Why FKBarChart cannot cover this:** A bar chart shows the same data as individual values. A radar shows the gestalt shape — two stocks with identical individual scores but different shapes are immediately distinguishable. Comparison between two series is also more readable on radar (two overlapping polygons) than on grouped bars.

**Props:**
```js
FKRadarChart.propTypes = {
  // Each item is one axis on the radar
  axes: PropTypes.arrayOf(PropTypes.shape({
    key:   PropTypes.string.isRequired,  // data key
    label: PropTypes.string.isRequired,  // axis label shown on chart
    max:   PropTypes.number,             // max value for this axis, default: 100
  })).isRequired,

  // Each series is one polygon on the radar
  series: PropTypes.arrayOf(PropTypes.shape({
    key:   PropTypes.string.isRequired,  // identifier
    label: PropTypes.string,             // legend label
    data:  PropTypes.object.isRequired,  // { [axisKey]: value } — one value per axis
    color: PropTypes.string,             // default: color.series[i]
  })).isRequired,

  fillOpacity: PropTypes.number,         // polygon fill opacity, default: 0.15
  title:       PropTypes.string,
  subtitle:    PropTypes.string,
  height:      PropTypes.number,         // default: 320
}
```

**Rendering rules:**
- Use Recharts `RadarChart` + `Radar` + `PolarGrid` + `PolarAngleAxis`
- Each series renders as a filled polygon with `fillOpacity` and a solid stroke at full opacity
- Grid lines: concentric polygons in `color.border`, not circles
- Axis labels: 11px mono, `color.text.tertiary`, positioned outside the polygon
- If multiple series: render each with its `color.series[i]`, show legend
- Tooltip on hover: show all axis values for the hovered series
- Use `FKTooltip` for tooltip rendering

**Sample data:**
```js
const axes = [
  { key: 'value',    label: 'Value',    max: 100 },
  { key: 'quality',  label: 'Quality',  max: 100 },
  { key: 'momentum', label: 'Momentum', max: 100 },
  { key: 'growth',   label: 'Growth',   max: 100 },
  { key: 'safety',   label: 'Safety',   max: 100 },
]
const series = [
  { key: 'AAPL', label: 'AAPL', data: { value: 62, quality: 88, momentum: 74, growth: 71, safety: 80 } },
  { key: 'MSFT', label: 'MSFT', data: { value: 55, quality: 91, momentum: 68, growth: 78, safety: 85 } },
]
```

---

### FKSankeyChart

**What it encodes:** Flows between two or more sets of categories. The width of each flow is proportional to its value. Used for revenue decomposition (product → region → margin bucket), fund flows (asset class → fund → strategy), portfolio attribution (factor → sector → stock), "where did the money go" journalism pieces.

**Why no existing primitive covers this:** Sankey requires node layout + flow path calculation — a unique visual encoding that cannot be approximated with bars, heatmaps, or part-of-whole charts.

**Implementation note:** Use a pure SVG implementation with manually calculated node positions and cubic bezier flow paths. Do not add a Sankey library dependency. The layout algorithm: (1) group nodes by column, (2) distribute node heights proportionally within each column, (3) draw cubic bezier paths between source and target node edges.

**Props:**
```js
FKSankeyChart.propTypes = {
  nodes: PropTypes.arrayOf(PropTypes.shape({
    id:     PropTypes.string.isRequired,
    label:  PropTypes.string.isRequired,
    column: PropTypes.number.isRequired,  // 0 = leftmost column
    color:  PropTypes.string,             // default: color.series[column % 6]
  })).isRequired,

  flows: PropTypes.arrayOf(PropTypes.shape({
    from:  PropTypes.string.isRequired,   // node id
    to:    PropTypes.string.isRequired,   // node id
    value: PropTypes.number.isRequired,
  })).isRequired,

  valueFormat: PropTypes.func,            // default: (v) => v.toLocaleString()
  title:       PropTypes.string,
  subtitle:    PropTypes.string,
  height:      PropTypes.number,          // default: 400
}
```

**Rendering rules:**
- Nodes: rectangles, width 16px, height proportional to total flow through node
- Node color: from `color` prop or `color.series[column % 6]`
- Node label: 11px mono, right of node for left columns, left of node for rightmost column
- Flows: cubic bezier paths, fill = source node color at 0.3 opacity, no stroke
- Hover on flow: highlight that flow, show tooltip with from → to + value
- Hover on node: highlight all flows touching that node
- Column spacing: evenly distributed across chart width
- Use `FKTooltip.Box` for canvas-style tooltip

**Sample data:**
```js
const nodes = [
  { id: 'hardware', label: 'Hardware',  column: 0 },
  { id: 'software', label: 'Software',  column: 0 },
  { id: 'services', label: 'Services',  column: 0 },
  { id: 'americas', label: 'Americas',  column: 1 },
  { id: 'europe',   label: 'Europe',    column: 1 },
  { id: 'apac',     label: 'APAC',      column: 1 },
  { id: 'gross',    label: 'Gross profit', column: 2 },
  { id: 'opex',     label: 'OpEx',      column: 2 },
]
const flows = [
  { from: 'hardware', to: 'americas', value: 42 },
  { from: 'hardware', to: 'europe',   value: 18 },
  { from: 'software', to: 'americas', value: 55 },
  { from: 'software', to: 'apac',     value: 31 },
  { from: 'services', to: 'americas', value: 28 },
  { from: 'americas', to: 'gross',    value: 89 },
  { from: 'europe',   to: 'gross',    value: 34 },
  { from: 'apac',     to: 'gross',    value: 41 },
  { from: 'americas', to: 'opex',     value: 36 },
  { from: 'europe',   to: 'opex',     value: 14 },
]
```

---

### Prop extensions to existing components

These are additions to components already specified above. The agent must incorporate
these into the relevant component files — they are not new files.

#### FKLineChart — `interpolation` prop
Add to FKLineChart props:
```js
interpolation: PropTypes.oneOf(['linear', 'step', 'stepBefore', 'stepAfter']),
// default: 'linear'
// 'step' holds the previous value flat until the next data point — essential for
// Fed funds rate, dividend history, fee tiers, any data that changes discretely.
// Maps to Recharts type prop on Line: 'linear' | 'stepAfter' | 'stepBefore'
```

#### FKBarChart — `mode='lollipop'`
Add `'lollipop'` to the mode prop:
```js
mode: PropTypes.oneOf(['grouped', 'stacked', 'lollipop']),
// 'lollipop': renders a thin 1.5px vertical stem from zero to value,
// capped with an 8px filled circle. Same colorRule support as bar mode.
// Use when there are many categories (20+ tickers) and bars become too dense.
```

#### FKTable — pivot mode
Add to FKTable props:
```js
pivotRow:   PropTypes.string,  // data key whose unique values become row headers
pivotCol:   PropTypes.string,  // data key whose unique values become column headers
pivotValue: PropTypes.string,  // data key whose value fills each cell
// When all three are provided, FKTable derives rows and columns from the data
// dynamically instead of using the static columns[] prop.
// Example: pivotRow='year' pivotCol='month' pivotValue='return'
// → monthly returns table where rows=years, cols=Jan–Dec
// colorRules still apply to cell values in pivot mode.
```

#### FKTimeline — duration bars
Add to FKTimeline event shape:
```js
// In the events[] array, if an item has both `from` and `to`:
from: PropTypes.string,  // ISO date — bar start (replaces `date` for duration events)
to:   PropTypes.string,  // ISO date — bar end
// → render a horizontal bar from `from` to `to` instead of a dot at `date`
// `date` is still used for point events (no `to` provided)
// Duration bars and point dots can coexist in the same FKTimeline instance
// Use case: holding period analysis, bond maturity ladder, option expiry schedule
```
