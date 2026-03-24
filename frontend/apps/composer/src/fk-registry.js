import {
  FKMetricGrid,
  FKLineChart, FKAreaChart, FKBandChart,
  FKAnnotatedChart, FKCandleChart, FKMultiPanel, FKProjectionChart,
  FKBarChart, FKWaterfall, FKHistogram,
  FKPartChart, FKHeatGrid, FKScatterChart,
  FKBulletChart, FKRangeChart,
  FKRankedList, FKTable, FKTimeline, FKRadarChart, FKSankeyChart,
} from '@finkit/ui'

// ─── Seeded sample data (stable across renders) ───────────────────────────────

function lcg(seed) {
  let s = seed >>> 0
  return () => {
    s = (Math.imul(s, 1664525) + 1013904223) >>> 0
    return s / 0x100000000
  }
}

function makeTimeseries(n = 24, startVal = 100, volatility = 0.018, seed = 1) {
  const rng = lcg(seed)
  const now = new Date('2026-01-01')
  let val = startVal
  return Array.from({ length: n }, (_, i) => {
    val = Math.max(1, val * (1 + (rng() - 0.47) * volatility))
    const d = new Date(now)
    d.setMonth(d.getMonth() + i)
    return { date: d.toISOString().slice(0, 7), value: Math.round(val * 100) / 100 }
  })
}

function makeDailyOHLCV(n = 60, start = 180, seed = 2) {
  const rng = lcg(seed)
  const now = new Date('2025-10-01')
  let price = start
  return Array.from({ length: n }, (_, i) => {
    const open  = price
    const move  = (rng() - 0.47) * 0.022
    const close = Math.round(open * (1 + move) * 100) / 100
    const high  = Math.round(Math.max(open, close) * (1 + rng() * 0.008) * 100) / 100
    const low   = Math.round(Math.min(open, close) * (1 - rng() * 0.008) * 100) / 100
    const volume = Math.round(1e6 + rng() * 5e6)
    const d = new Date(now)
    d.setDate(d.getDate() + i)
    price = close
    return { date: d.toISOString().slice(0, 10), open, high, low, close, volume }
  })
}

const TS = makeTimeseries(24, 100, 0.018, 1)
const TS2 = makeTimeseries(24, 100, 0.012, 99)
const TS_DUAL = TS.map((row, i) => ({ ...row, bench: TS2[i].value }))
const OHLCV = makeDailyOHLCV(90)

// 24 months of grouped revenue data for bar chart range selector demo
const rng3 = lcg(42)
const MONTHLY_REVENUE = Array.from({ length: 24 }, (_, i) => {
  const d = new Date('2024-01-01')
  d.setMonth(d.getMonth() + i)
  const label = d.toISOString().slice(0, 7)
  return {
    label,
    product:  Math.round(800 + rng3() * 400),
    services: Math.round(300 + rng3() * 200),
    other:    Math.round(100 + rng3() * 100),
  }
})

// ─── FK Component Registry ────────────────────────────────────────────────────
// supportedWidths: derived from the UI Planner system prompt constraints
// sampleProps: minimal props — most components fall back to built-in sample data

export const FK_REGISTRY = [
  {
    id: 'FKMetricGrid',
    name: 'Metric Grid',
    description: 'Headline KPI cards row — always full-width',
    category: 'KPI',
    supportedWidths: ['full', '3/4', '2/3', '1/2', '1/3'],
    component: FKMetricGrid,
    sampleProps: { title: 'Key Metrics', subtitle: 'Portfolio snapshot · today' },
  },
  {
    id: 'FKLineChart',
    name: 'Line Chart',
    description: 'Time-series line chart with range selector',
    category: 'Time-Series',
    supportedWidths: ['full', '3/4', '2/3', '1/2'],
    component: FKLineChart,
    sampleProps: {
      title: 'Portfolio NAV',
      subtitle: 'vs benchmark · rebased to 100',
      data: TS_DUAL,
      series: [{ key: 'value', label: 'Portfolio' }, { key: 'bench', label: 'Benchmark', dashed: true }],
    },
  },
  {
    id: 'FKAreaChart',
    name: 'Area Chart',
    description: 'Filled area — drawdown, portfolio value, sector rotation',
    category: 'Time-Series',
    supportedWidths: ['full', '3/4', '2/3', '1/2'],
    component: FKAreaChart,
    sampleProps: {
      title: 'Sector Allocation',
      subtitle: 'Stacked area · % of portfolio over time',
    },
  },
  {
    id: 'FKAnnotatedChart',
    name: 'Annotated Chart',
    description: 'Line chart with events, bands and callouts',
    category: 'Time-Series',
    supportedWidths: ['full', '3/4', '2/3'],
    component: FKAnnotatedChart,
    sampleProps: {
      title: 'Price + Events',
      subtitle: 'Buy/sell signals with consolidation zone',
      data: TS,
      series: [{ key: 'value', label: 'Price' }],
      events: [
        { date: '2026-03', type: 'buy',  label: 'Buy Signal' },
        { date: '2026-07', type: 'sell', label: 'Take Profit' },
      ],
      bands: [{ from: '2026-04', to: '2026-06', label: 'Consolidation' }],
      callouts: [],
    },
  },
  {
    id: 'FKCandleChart',
    name: 'Candle Chart',
    description: 'OHLCV candlestick chart with volume',
    category: 'Time-Series',
    supportedWidths: ['full', '3/4', '2/3'],
    component: FKCandleChart,
    sampleProps: {
      title: 'AAPL Daily',
      subtitle: 'OHLCV · last 90 sessions',
      data: OHLCV,
    },
  },
  {
    id: 'FKMultiPanel',
    name: 'Multi Panel',
    description: 'Stacked panels — price + volume + RSI + MACD',
    category: 'Time-Series',
    supportedWidths: ['full', '3/4', '2/3'],
    component: FKMultiPanel,
    sampleProps: {
      title: 'Technical Overview',
      subtitle: 'Price · Volume · RSI',
    },
  },
  {
    id: 'FKProjectionChart',
    name: 'Projection Chart',
    description: 'Historical + Monte Carlo fan projection',
    category: 'Time-Series',
    supportedWidths: ['full', '3/4', '2/3'],
    component: FKProjectionChart,
    sampleProps: {
      title: 'Portfolio Projection',
      subtitle: 'Monte Carlo fan · 85% confidence interval',
      historical: TS.slice(0, 18),
      projection: Array.from({ length: 12 }, (_, i) => {
        const d = new Date('2027-07')
        d.setMonth(d.getMonth() + i)
        const base = 120 + i * 2
        return { date: d.toISOString().slice(0, 7), median: base, low: base * 0.85, high: base * 1.18 }
      }),
      splitDate: '2027-07',
    },
  },
  {
    id: 'FKBandChart',
    name: 'Band Chart',
    description: 'Confidence band around a central line',
    category: 'Time-Series',
    supportedWidths: ['full', '1/2'],
    component: FKBandChart,
    sampleProps: {
      title: 'Bollinger Bands',
      subtitle: '20-day SMA · ±2 standard deviations',
      data: TS.map(r => ({ ...r, upper: r.value * 1.06, lower: r.value * 0.94 })),
      series: [{ key: 'value', label: 'Price' }, { key: 'upper', label: 'Upper' }, { key: 'lower', label: 'Lower' }],
    },
  },
  {
    id: 'FKBarChart',
    name: 'Bar Chart',
    description: 'Grouped / stacked / diverging bars',
    category: 'Bar',
    supportedWidths: ['full', '3/4', '2/3', '1/2'],
    component: FKBarChart,
    sampleProps: { title: 'Sector Returns', subtitle: 'YTD performance by sector', rangeSelector: true },
  },
  {
    id: 'FKBarChart_Grouped',
    name: 'Bar Chart (Grouped)',
    description: 'Grouped bars — multi-series time-series with range selector',
    category: 'Bar',
    supportedWidths: ['full', '3/4', '2/3', '1/2'],
    component: FKBarChart,
    sampleProps: {
      title: 'Monthly Revenue',
      subtitle: 'Product · Services · Other',
      mode: 'grouped',
      labelKey: 'label',
      data: MONTHLY_REVENUE,
      series: [
        { key: 'product',  label: 'Product' },
        { key: 'services', label: 'Services' },
        { key: 'other',    label: 'Other' },
      ],
      rangeSelector: true,
      defaultRange: '6M',
      yFormat: v => `$${(v/1000).toFixed(0)}k`,
    },
  },
  {
    id: 'FKWaterfall',
    name: 'Waterfall',
    description: 'Running-total waterfall / bridge chart',
    category: 'Bar',
    supportedWidths: ['full', '1/2'],
    component: FKWaterfall,
    sampleProps: { title: 'P&L Bridge', subtitle: 'Jan → Dec attribution' },
  },
  {
    id: 'FKHistogram',
    name: 'Histogram',
    description: 'Return distribution with optional normal overlay',
    category: 'Distribution',
    supportedWidths: ['full', '1/2', '1/3'],
    component: FKHistogram,
    sampleProps: { title: 'Return Distribution', subtitle: 'Daily returns · last 252 sessions' },
  },
  {
    id: 'FKScatterChart',
    name: 'Scatter Chart',
    description: 'Risk/return scatter with optional trend line',
    category: 'Distribution',
    supportedWidths: ['full', '1/2', '1/3'],
    component: FKScatterChart,
    sampleProps: { title: 'Risk / Return', subtitle: 'Annualised · peer universe' },
  },
  {
    id: 'FKRadarChart',
    name: 'Radar Chart',
    description: 'Multi-axis factor profile / spider chart',
    category: 'Distribution',
    supportedWidths: ['full', '1/2', '1/3'],
    component: FKRadarChart,
    sampleProps: { title: 'Factor Profile', subtitle: 'vs benchmark' },
  },
  {
    id: 'FKPartChart',
    name: 'Part Chart',
    description: 'Donut / pie / treemap for proportional data',
    category: 'Part-of-Whole',
    supportedWidths: ['full', '1/2', '1/3'],
    component: FKPartChart,
    sampleProps: { title: 'Allocation', subtitle: 'By asset class · current' },
  },
  {
    id: 'FKHeatGrid',
    name: 'Heat Grid',
    description: 'Correlation matrix or monthly-returns heat map',
    category: 'Grid',
    supportedWidths: ['full', '2/3', '1/2'],
    component: FKHeatGrid,
    sampleProps: { title: 'Correlation Matrix', subtitle: '12-month rolling · major assets' },
  },
  {
    id: 'FKSankeyChart',
    name: 'Sankey Chart',
    description: 'Flow diagram — product → region → profit',
    category: 'Flow',
    supportedWidths: ['full', '2/3'],
    component: FKSankeyChart,
    sampleProps: { title: 'Revenue Flow', subtitle: 'Product → Region → Profit' },
  },
  {
    id: 'FKRangeChart',
    name: 'Range Chart',
    description: 'Min / max / current value range bars',
    category: 'Comparative',
    supportedWidths: ['full', '1/2'],
    component: FKRangeChart,
    sampleProps: { title: '52-Week Range', subtitle: 'Current vs high / low' },
  },
  {
    id: 'FKBulletChart',
    name: 'Bullet Chart',
    description: 'Actual vs target with performance bands',
    category: 'Comparative',
    supportedWidths: ['full', '1/2'],
    component: FKBulletChart,
    sampleProps: { title: 'Targets vs Actual', subtitle: 'Q1 2026 · all metrics' },
  },
  {
    id: 'FKRankedList',
    name: 'Ranked List',
    description: 'Horizontal bar list ranked by value',
    category: 'List',
    supportedWidths: ['full', '1/2', '1/3'],
    component: FKRankedList,
    sampleProps: { title: 'Top Holdings', subtitle: 'By portfolio weight' },
  },
  {
    id: 'FKTimeline',
    name: 'Timeline',
    description: 'Event timeline — earnings, dividends, macro',
    category: 'List',
    supportedWidths: ['full', '2/3'],
    component: FKTimeline,
    sampleProps: { title: 'Upcoming Events', subtitle: 'Earnings · dividends · macro' },
  },
  {
    id: 'FKTable',
    name: 'Data Table',
    description: 'Sortable table with optional sparklines — detail row',
    category: 'Table',
    supportedWidths: ['full'],
    component: FKTable,
    sampleProps: { title: 'Holdings Detail', subtitle: 'Sortable · click column to sort' },
  },
]

// Default approvals = nothing approved — user must verify each width visually
export const DEFAULT_APPROVALS = Object.fromEntries(
  FK_REGISTRY.map(c => [c.id, []])
)

export const ALL_WIDTHS = ['full', '3/4', '2/3', '1/2', '1/3', '1/4']

export const WIDTH_FRACTION = {
  'full': 1,
  '3/4':  0.75,
  '2/3':  0.667,
  '1/2':  0.5,
  '1/3':  0.333,
  '1/4':  0.25,
}

export const CATEGORIES = [...new Set(FK_REGISTRY.map(c => c.category))]
