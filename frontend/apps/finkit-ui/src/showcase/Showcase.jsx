import React from 'react'
import { FKMetricGrid }      from '../FKMetricGrid.jsx'
import { FKLineChart }       from '../FKLineChart.jsx'
import { FKAreaChart }       from '../FKAreaChart.jsx'
import { FKAnnotatedChart }  from '../FKAnnotatedChart.jsx'
import { FKMultiPanel }      from '../FKMultiPanel.jsx'
import { FKProjectionChart } from '../FKProjectionChart.jsx'
import { FKBarChart }        from '../FKBarChart.jsx'
import { FKWaterfall }       from '../FKWaterfall.jsx'
import { FKScatterChart }    from '../FKScatterChart.jsx'
import { FKHeatGrid }        from '../FKHeatGrid.jsx'
import { FKPartChart }       from '../FKPartChart.jsx'
import { FKRangeChart }      from '../FKRangeChart.jsx'
import { FKBulletChart }     from '../FKBulletChart.jsx'
import { FKCandleChart }     from '../FKCandleChart.jsx'
import { FKTimeline }        from '../FKTimeline.jsx'
import { FKRadarChart }      from '../FKRadarChart.jsx'
import { FKSankeyChart }     from '../FKSankeyChart.jsx'
import { FKTable }           from '../FKTable.jsx'
import { FKRankedList }      from '../FKRankedList.jsx'
import { color }             from '../tokens.js'

// ─── Mock data ────────────────────────────────────────────────────────────────

// Price history for sparklines
const spark = (base, n = 20) =>
  Array.from({ length: n }, (_, i) => parseFloat((base + Math.sin(i * 0.4) * 5 + i * 0.3 + Math.random() * 3).toFixed(2)))

// Monthly returns data
const MONTHLY_PNL = [
  { month: 'Jan', pnl:  4200 }, { month: 'Feb', pnl: -1800 },
  { month: 'Mar', pnl:  6100 }, { month: 'Apr', pnl:  3400 },
  { month: 'May', pnl: -2200 }, { month: 'Jun', pnl:  5800 },
  { month: 'Jul', pnl:  2100 }, { month: 'Aug', pnl: -900  },
  { month: 'Sep', pnl:  3700 }, { month: 'Oct', pnl:  4900 },
  { month: 'Nov', pnl: -1100 }, { month: 'Dec', pnl:  7200 },
]

// Line chart — rolling Sharpe
const MONTHS_LABELS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
const ROLLING_SHARPE = Array.from({ length: 24 }, (_, i) => ({
  date:     `${MONTHS_LABELS[i % 12]} '${i < 12 ? '23' : '24'}`,
  sharpe:   parseFloat((0.6 + Math.sin(i * 0.4) * 0.6 + i * 0.04).toFixed(2)),
  bench:    parseFloat((0.4 + Math.random() * 0.4).toFixed(2)),
}))

// Holdings data
const HOLDINGS = [
  { ticker: 'AAPL',  weight: 19.3, return_pct:  1.78, sector: 'Technology', value: 18240, price_history: spark(180, 20) },
  { ticker: 'MSFT',  weight: 15.7, return_pct:  0.92, sector: 'Technology', value: 14820, price_history: spark(370, 20) },
  { ticker: 'NVDA',  weight: 12.6, return_pct:  3.21, sector: 'Technology', value: 11940, price_history: spark(850, 20) },
  { ticker: 'AMZN',  weight: 10.2, return_pct: -0.44, sector: 'Consumer',   value:  9610, price_history: spark(185, 20) },
  { ticker: 'GOOGL', weight:  8.7, return_pct:  0.65, sector: 'Technology', value:  8250, price_history: spark(160, 20) },
  { ticker: 'META',  weight:  7.5, return_pct:  2.14, sector: 'Technology', value:  7120, price_history: spark(490, 20) },
  { ticker: 'BRK.B', weight:  6.7, return_pct: -0.18, sector: 'Financials', value:  6340, price_history: spark(395, 20) },
  { ticker: 'JPM',   weight:  6.2, return_pct:  1.03, sector: 'Financials', value:  5900, price_history: spark(200, 20) },
  { ticker: 'UNH',   weight:  5.4, return_pct: -1.22, sector: 'Healthcare', value:  5120, price_history: spark(520, 20) },
  { ticker: 'V',     weight:  4.8, return_pct:  0.55, sector: 'Financials', value:  4560, price_history: spark(275, 20) },
]

// Correlation matrix data
const ASSETS = ['AAPL','MSFT','NVDA','SPY','BND']
const CORR_DATA = ASSETS.flatMap(a => ASSETS.map(b => ({
  asset_a: a, asset_b: b,
  correlation: a === b ? 1 : parseFloat((0.3 + (a[0] === b[0] ? 0.4 : 0) + Math.random() * 0.3 - 0.1).toFixed(2)),
})))

// Screener scatter
const SCREENER = [
  { ticker: 'AAPL',  vol: 18.2, momentum: 12.4, mkt_cap: 3200, sector: 'Technology' },
  { ticker: 'MSFT',  vol: 16.8, momentum:  9.1, mkt_cap: 3100, sector: 'Technology' },
  { ticker: 'NVDA',  vol: 42.1, momentum: 38.4, mkt_cap: 2200, sector: 'Technology' },
  { ticker: 'AMZN',  vol: 22.4, momentum:  8.9, mkt_cap: 1900, sector: 'Consumer' },
  { ticker: 'META',  vol: 28.6, momentum: 24.1, mkt_cap: 1300, sector: 'Technology' },
  { ticker: 'TSLA',  vol: 54.3, momentum: -11.8, mkt_cap: 700, sector: 'Consumer' },
  { ticker: 'BRK.B', vol: 11.2, momentum:  5.2, mkt_cap: 900, sector: 'Financials' },
  { ticker: 'JPM',   vol: 19.8, momentum: -2.4, mkt_cap: 600, sector: 'Financials' },
  { ticker: 'JNJ',   vol: 13.4, momentum: -4.1, mkt_cap: 500, sector: 'Healthcare' },
  { ticker: 'UNH',   vol: 21.3, momentum: -1.2, mkt_cap: 480, sector: 'Healthcare' },
]
const SECTOR_COLORS = { Technology: '#6366f1', Consumer: '#f59e0b', Financials: '#06b6d4', Healthcare: '#10b981' }

// 52-week range
const W52_DATA = HOLDINGS.slice(0, 6).map(h => ({
  label:  h.ticker,
  min:    h.value * 0.72,
  max:    h.value * 1.32,
  value:  h.value,
  target: h.value * 1.15,
}))

// Price time series for annotated / multi-panel / projection
const PRICE_SERIES = Array.from({ length: 60 }, (_, i) => {
  const d = new Date('2024-01-02')
  d.setDate(d.getDate() + i)
  return {
    date:   d.toISOString().slice(0, 10),
    price:  parseFloat((180 + Math.sin(i * 0.2) * 12 + i * 0.4 + Math.random() * 4).toFixed(2)),
    volume: Math.floor(50e6 + Math.random() * 30e6),
    rsi:    parseFloat((50 + Math.sin(i * 0.3) * 18 + Math.random() * 6).toFixed(1)),
  }
})

// Waterfall P&L bridge
const WATERFALL_DATA = [
  { label: 'Q2 Revenue', value: 28400, type: 'start' },
  { label: 'New Contracts', value: 4200, type: 'delta' },
  { label: 'Churn', value: -1800, type: 'delta' },
  { label: 'Upsell', value: 2100, type: 'delta' },
  { label: 'FX Impact', value: -600, type: 'delta' },
  { label: 'Q3 Revenue', value: 32300, type: 'end' },
]

// Bullet chart data
const BULLET_DATA = [
  { label: 'AAPL', value: 212, target: 220, rangeMin: 165, rangeMax: 235 },
  { label: 'MSFT', value: 418, target: 400, rangeMin: 340, rangeMax: 460 },
  { label: 'NVDA', value: 875, target: 920, rangeMin: 600, rangeMax: 1000 },
  { label: 'AMZN', value: 195, target: 210, rangeMin: 155, rangeMax: 225 },
  { label: 'GOOGL', value: 173, target: 168, rangeMin: 130, rangeMax: 190 },
]

// Timeline events
const TIMELINE_EVENTS = [
  { date: '2024-01-15', label: 'Q4 Earnings', type: 'earnings', row: 'AAPL', value: '+EPS Beat' },
  { date: '2024-02-01', label: 'Fed Meeting', type: 'macro', row: 'Macro', value: 'Rate Hold' },
  { date: '2024-02-08', label: 'Q4 Earnings', type: 'earnings', row: 'MSFT', value: '+EPS Beat' },
  { date: '2024-03-05', label: 'CPI Print', type: 'macro', row: 'Macro', value: '3.2% YoY' },
  { date: '2024-03-15', label: 'Dividend', type: 'dividend', row: 'AAPL', value: '$0.25/sh' },
  { date: '2024-04-01', label: 'Analyst Upgrade', type: 'research', row: 'NVDA', value: 'PT $1100' },
  { from: '2024-02-15', to: '2024-03-01', label: 'Buyback Window', type: 'corporate', row: 'MSFT' },
  { from: '2024-03-10', to: '2024-04-05', label: 'Quiet Period', type: 'corporate', row: 'AAPL' },
]

// Radar factor profile
const RADAR_AXES = [
  { key: 'momentum', label: 'Momentum', max: 100 },
  { key: 'quality',  label: 'Quality',  max: 100 },
  { key: 'value',    label: 'Value',    max: 100 },
  { key: 'growth',   label: 'Growth',   max: 100 },
  { key: 'low_vol',  label: 'Low Vol',  max: 100 },
]
const RADAR_SERIES = [
  { key: 'portfolio', label: 'Portfolio', data: { momentum: 78, quality: 65, value: 42, growth: 81, low_vol: 38 } },
  { key: 'benchmark', label: 'Benchmark', data: { momentum: 54, quality: 70, value: 58, growth: 62, low_vol: 60 }, color: '#94a3b8' },
]

// Sankey revenue flow
const SANKEY_NODES = [
  { id: 'revenue',   label: 'Revenue',    column: 0 },
  { id: 'product',   label: 'Product',    column: 1 },
  { id: 'services',  label: 'Services',   column: 1 },
  { id: 'other',     label: 'Other',      column: 1 },
  { id: 'cogs',      label: 'COGS',       column: 2 },
  { id: 'opex',      label: 'OpEx',       column: 2 },
  { id: 'gross',     label: 'Gross Profit', column: 2 },
  { id: 'ebit',      label: 'EBIT',       column: 3 },
  { id: 'taxes',     label: 'Taxes',      column: 3 },
  { id: 'net_income', label: 'Net Income', column: 3 },
]
const SANKEY_FLOWS = [
  { from: 'revenue',  to: 'product',    value: 6200 },
  { from: 'revenue',  to: 'services',   value: 3400 },
  { from: 'revenue',  to: 'other',      value: 800  },
  { from: 'product',  to: 'cogs',       value: 2800 },
  { from: 'product',  to: 'gross',      value: 3400 },
  { from: 'services', to: 'cogs',       value: 900  },
  { from: 'services', to: 'gross',      value: 2500 },
  { from: 'other',    to: 'gross',      value: 600  },
  { from: 'gross',    to: 'opex',       value: 2800 },
  { from: 'gross',    to: 'ebit',       value: 3700 },
  { from: 'ebit',     to: 'taxes',      value: 740  },
  { from: 'ebit',     to: 'net_income', value: 2960 },
]

// Projection fan data
const HIST_DATA = PRICE_SERIES.slice(0, 45).map(d => ({ date: d.date, value: d.price }))
const PROJ_DATA = Array.from({ length: 20 }, (_, i) => {
  const d = new Date('2024-03-18')
  d.setDate(d.getDate() + i)
  const base = 205 + i * 0.6
  return {
    date:   d.toISOString().slice(0, 10),
    median: parseFloat(base.toFixed(2)),
    p10:    parseFloat((base - 18 - i * 0.3).toFixed(2)),
    p25:    parseFloat((base - 9  - i * 0.15).toFixed(2)),
    p75:    parseFloat((base + 9  + i * 0.15).toFixed(2)),
    p90:    parseFloat((base + 18 + i * 0.3).toFixed(2)),
  }
})

// ─── Section wrapper ──────────────────────────────────────────────────────────
function Section({ title, children }) {
  return (
    <div style={{ marginBottom: 48 }}>
      <div
        style={{
          fontSize: 11, fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase',
          color: 'var(--color-text-tertiary)', marginBottom: 14,
          paddingBottom: 8, borderBottom: '0.5px solid var(--color-border-tertiary)',
        }}
      >
        {title}
      </div>
      {children}
    </div>
  )
}

function Grid({ cols = 2, children }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: `repeat(${cols}, 1fr)`, gap: 16 }}>
      {children}
    </div>
  )
}

// ─── Showcase ─────────────────────────────────────────────────────────────────
export function Showcase() {
  return (
    <div
      style={{
        maxWidth: 1200, margin: '0 auto',
        padding: '32px 24px 80px',
        fontFamily: 'var(--font-sans)',
      }}
    >
      {/* Header */}
      <div style={{ marginBottom: 40 }}>
        <div style={{ fontSize: 24, fontWeight: 700, color: 'var(--color-text-primary)', marginBottom: 4 }}>
          FINKIT Primitives
        </div>
        <div style={{ fontSize: 14, color: 'var(--color-text-secondary)' }}>
          Generic visualization primitives for financial analytics dashboards.
        </div>
      </div>

      {/* P10 — FKMetricGrid */}
      <Section title="FKMetricGrid — KPI headlines">
        <FKMetricGrid
          cols={4}
          cards={[
            { label: 'Portfolio Value', value: '$94,273',  delta: 1.99,  sub: 'today',          spark: spark(90, 20) },
            { label: 'Total Return',    value: '+20.25%',  delta: 20.25, color: color.gain,      spark: spark(100, 20) },
            { label: 'Sharpe Ratio',    value: '1.84',     sub: 'Excellent' },
            { label: 'Max Drawdown',    value: '−23.4%',   color: color.loss, sub: 'peak to trough' },
          ]}
        />
      </Section>

      {/* P1 — FKLineChart */}
      <Section title="FKLineChart — time series / multi-series">
        <Grid cols={2}>
          <FKLineChart
            data={ROLLING_SHARPE}
            series={[{ key: 'sharpe', label: '12M Sharpe' }]}
            xKey="date"
            yFormat={v => v.toFixed(2)}
            referenceLines={[
              { y: 1, label: 'Target', color: color.gain, dashed: true },
              { y: 0, color: 'rgba(0,0,0,0.15)' },
            ]}
            rangeSelector={['6M', '1Y', '2Y']}
            title="Rolling Sharpe Ratio"
            subtitle="12-month rolling window"
            height={220}
          />
          <FKLineChart
            data={ROLLING_SHARPE}
            series={[
              { key: 'sharpe', label: 'Portfolio' },
              { key: 'bench',  label: 'Benchmark', dashed: true },
            ]}
            xKey="date"
            yFormat={v => v.toFixed(2)}
            rangeSelector
            title="Portfolio vs Benchmark Sharpe"
            height={220}
          />
        </Grid>
      </Section>

      {/* P3 — FKBarChart */}
      <Section title="FKBarChart — single / grouped / stacked / waterfall">
        <Grid cols={2}>
          <FKBarChart
            data={MONTHLY_PNL}
            valueKey="pnl"
            labelKey="month"
            yFormat={v => `${v >= 0 ? '+' : ''}$${(v / 1000).toFixed(0)}k`}
            title="Monthly P&L"
            height={200}
          />
          <FKBarChart
            data={[
              { q: 'Q1 23', estimate: 4.2, actual: 4.8 },
              { q: 'Q2 23', estimate: 4.5, actual: 4.1 },
              { q: 'Q3 23', estimate: 4.8, actual: 5.2 },
              { q: 'Q4 23', estimate: 5.1, actual: 5.5 },
              { q: 'Q1 24', estimate: 5.3, actual: 4.9 },
            ]}
            mode="grouped"
            labelKey="q"
            series={[
              { key: 'estimate', label: 'Estimate' },
              { key: 'actual',   label: 'Actual' },
            ]}
            colorRule={(row, k) => k === 'actual'
              ? (row.actual > row.estimate ? 'gain' : 'loss')
              : 'neutral'
            }
            title="Earnings Beat / Miss"
            height={200}
          />
          <FKBarChart
            data={[
              { name: 'Alpha',   value:  3200 },
              { name: 'Fees',    value: -800  },
              { name: 'FX',      value: -600  },
              { name: 'Selection', value: 2100 },
              { name: 'Timing',  value: -400  },
              { name: 'Total',   value: 3500  },
            ]}
            mode="waterfall"
            valueKey="value"
            labelKey="name"
            yFormat={v => `$${(v / 1000).toFixed(1)}k`}
            title="P&L Attribution"
            height={200}
          />
          <FKBarChart
            data={HOLDINGS.map(h => ({ name: h.ticker, return_pct: h.return_pct }))}
            orientation="horizontal"
            valueKey="return_pct"
            labelKey="name"
            yFormat={v => `${v.toFixed(2)}%`}
            title="Holdings Return (Horizontal)"
            height={200}
          />
        </Grid>
      </Section>

      {/* P2 — FKAreaChart */}
      <Section title="FKAreaChart — stacked / normalized composition">
        <FKAreaChart
          series={[
            { key: 'tech',    label: 'Technology' },
            { key: 'finance', label: 'Financials' },
            { key: 'health',  label: 'Healthcare' },
            { key: 'energy',  label: 'Energy' },
            { key: 'other',   label: 'Other' },
          ]}
          mode="normalized"
          title="Sector Rotation"
          subtitle="Portfolio weight over time"
          height={240}
        />
      </Section>

      {/* P5 — FKScatterChart */}
      <Section title="FKScatterChart — Canvas bubble / scatter">
        <FKScatterChart
          data={SCREENER}
          xKey="vol"
          yKey="momentum"
          sizeKey="mkt_cap"
          colorKey="sector"
          colorMap={SECTOR_COLORS}
          labelKey="ticker"
          xLabel="30D Volatility (%)"
          yLabel="3M Momentum (%)"
          referenceLines={[{ y: 0 }, { x: 25 }]}
          trendLine
          quadrants
          title="Momentum vs Volatility Screener"
          height={300}
        />
      </Section>

      {/* P7 — FKHeatGrid */}
      <Section title="FKHeatGrid — heatmap / correlation / calendar">
        <Grid cols={2}>
          <FKHeatGrid
            data={CORR_DATA}
            rowKey="asset_a"
            colKey="asset_b"
            valueKey="correlation"
            colorScale="diverging"
            showValues
            colorDomain={[-1, 1]}
            valueFormat={v => v.toFixed(2)}
            title="Correlation Matrix"
          />
          <FKHeatGrid
            rowKey="month"
            colKey="year"
            valueKey="return_pct"
            colorScale="diverging"
            showValues
            valueFormat={v => `${v.toFixed(1)}%`}
            title="Monthly Returns Calendar"
          />
        </Grid>
      </Section>

      {/* P8 — FKPartChart */}
      <Section title="FKPartChart — donut / treemap / bars">
        <Grid cols={3}>
          <FKPartChart
            data={HOLDINGS.map(h => ({ label: h.ticker, value: h.weight }))}
            valueKey="value"
            labelKey="label"
            mode="donut"
            innerLabel="$94k"
            innerSub="total AUM"
            title="Portfolio Allocation"
          />
          <FKPartChart
            data={HOLDINGS.map(h => ({ label: h.ticker, value: h.value, return_pct: h.return_pct }))}
            valueKey="value"
            labelKey="label"
            colorKey="return_pct"
            colorBy="colorKey"
            mode="treemap"
            title="Portfolio Map"
            height={220}
          />
          <FKPartChart
            data={[
              { name: 'Technology', weight: 64.0 },
              { name: 'Financials', weight: 18.7 },
              { name: 'Consumer',   weight:  9.8 },
              { name: 'Healthcare', weight:  7.5 },
            ]}
            valueKey="weight"
            labelKey="name"
            mode="bars"
            showTotal
            title="Sector Weights"
          />
        </Grid>
      </Section>

      {/* P9 — FKRangeChart */}
      <Section title="FKRangeChart — Canvas 52W range / mandate limits">
        <Grid cols={2}>
          <FKRangeChart
            data={W52_DATA}
            format={v => `$${v.toFixed(0)}`}
            title="52-Week High / Low Range"
            subtitle="◆ Analyst target"
          />
          <FKRangeChart
            data={[
              { label: 'Equity Weight',  min: 0, max: 0.7, value: 0.64 },
              { label: 'Single Stock',   min: 0, max: 0.2, value: 0.193 },
              { label: 'Sector Conc.',   min: 0, max: 0.4, value: 0.351 },
              { label: 'EM Exposure',    min: 0, max: 0.3, value: 0.08  },
              { label: 'Duration',       min: 0, max: 8,   value: 6.2   },
            ]}
            colorRule={row => {
              const u = row.value / row.max
              return u > 0.9 ? 'loss' : u > 0.75 ? 'warn' : 'gain'
            }}
            format={v => typeof v === 'number' && v < 1 ? `${(v * 100).toFixed(1)}%` : v.toFixed(1)}
            title="Mandate Utilization"
          />
        </Grid>
      </Section>

      {/* FKCandleChart */}
      <Section title="FKCandleChart — Canvas OHLCV candlestick + volume">
        <FKCandleChart
          showVolume
          title="AAPL — Daily Candles"
          subtitle="60-day price action"
          height={320}
        />
      </Section>

      {/* P11 — FKTable */}
      <Section title="FKTable — sortable table with color rules">
        <FKTable
          columns={[
            { key: 'ticker', label: 'Symbol', width: 72 },
            { key: 'value',  label: 'Value',   align: 'right', mono: true, format: v => `$${v.toLocaleString()}` },
            { key: 'weight', label: 'Weight',  align: 'right', mono: true, format: v => `${v.toFixed(1)}%` },
            {
              key: 'return_pct', label: 'Return', align: 'right', mono: true,
              colorRule: v => v >= 0 ? 'gain' : 'loss',
              format:    v => `${v >= 0 ? '+' : ''}${v.toFixed(2)}%`,
            },
            { key: 'sector', label: 'Sector' },
          ]}
          rows={HOLDINGS}
          defaultSort="value"
          sparkKey="price_history"
          title="Holdings"
          maxRows={8}
        />
      </Section>

      {/* FKRankedList */}
      <Section title="FKRankedList — ranked rows with sparklines">
        <Grid cols={2}>
          <FKRankedList
            data={HOLDINGS.map((h, i) => ({
              label: h.ticker,
              value: `${h.return_pct >= 0 ? '+' : ''}${h.return_pct.toFixed(2)}%`,
              delta: h.return_pct,
              sub:   h.sector,
              spark: h.price_history,
            })).sort((a, b) => b.delta - a.delta)}
            title="Top Movers"
            subtitle="Today's performance"
          />
          <FKRankedList
            data={HOLDINGS.map(h => ({
              label: h.ticker,
              value: `$${(h.value / 1000).toFixed(1)}k`,
              delta: h.return_pct,
              sub:   h.sector,
              spark: h.price_history,
            })).sort((a, b) => b.value.localeCompare(a.value))}
            title="Holdings by Value"
            subtitle="Portfolio positions"
          />
        </Grid>
      </Section>

      {/* FKAnnotatedChart — signals + bands + callouts */}
      <Section title="FKAnnotatedChart — line/area + event markers, regime bands, callouts">
        <FKAnnotatedChart
          data={PRICE_SERIES}
          xKey="date"
          series={[{ key: 'price', label: 'Price' }]}
          events={[
            { date: '2024-01-22', type: 'buy',  label: 'Buy Signal',  value: 186.4 },
            { date: '2024-02-14', type: 'sell', label: 'Sell Signal', value: 201.2 },
            { date: '2024-03-05', type: 'buy',  label: 'Buy Signal',  value: 194.8 },
          ]}
          bands={[
            { from: '2024-02-01', to: '2024-02-20', color: 'rgba(220,38,38,0.08)', label: 'Bear Regime' },
            { from: '2024-03-10', to: '2024-03-28', color: 'rgba(22,163,74,0.08)',  label: 'Bull Regime' },
          ]}
          callouts={[
            { date: '2024-02-14', value: 201.2, label: 'Earnings Beat +12%', position: 'above', color: color.gain },
          ]}
          shapeMap={{ buy: 'triangle-up', sell: 'triangle-down' }}
          colorMap={{ buy: color.gain, sell: color.loss }}
          valueFormat={v => `$${v.toFixed(2)}`}
          title="AAPL — Backtest Signals"
          subtitle="Buy/sell markers with regime overlay"
          height={280}
        />
      </Section>

      {/* FKMultiPanel — synchronized price + volume + RSI */}
      <Section title="FKMultiPanel — synchronized multi-panel crosshair">
        <FKMultiPanel
          data={PRICE_SERIES}
          xKey="date"
          panels={[
            {
              id: 'price',
              height: 200,
              series: [{ key: 'price', label: 'Price', type: 'area' }],
              yLabel: 'Price',
            },
            {
              id: 'volume',
              height: 80,
              series: [{ key: 'volume', label: 'Volume', type: 'bar' }],
              yLabel: 'Volume',
            },
            {
              id: 'rsi',
              height: 80,
              series: [{ key: 'rsi', label: 'RSI(14)', type: 'line' }],
              referenceLines: [{ y: 70, dashed: true }, { y: 30, dashed: true }],
              yDomain: [0, 100],
              yLabel: 'RSI',
            },
          ]}
          title="AAPL — Price / Volume / RSI"
          subtitle="60-day daily chart with synchronized crosshair"
        />
      </Section>

      {/* FKProjectionChart — Monte Carlo fan */}
      <Section title="FKProjectionChart — historical line + forward projection fan">
        <Grid cols={2}>
          <FKProjectionChart
            historical={HIST_DATA}
            projection={PROJ_DATA}
            splitDate="2024-03-18"
            valueFormat={v => `$${v.toFixed(2)}`}
            title="Price Projection Fan"
            subtitle="p10/p25/p75/p90 Monte Carlo bands"
            height={280}
          />
          <FKProjectionChart
            historical={HIST_DATA}
            scenarios={[
              { key: 'bull',  label: 'Bull',  color: color.gain,    data: PROJ_DATA.map(d => ({ date: d.date, value: d.p90 })) },
              { key: 'base',  label: 'Base',  color: color.series?.[0] || '#6366f1', data: PROJ_DATA.map(d => ({ date: d.date, value: d.median })) },
              { key: 'bear',  label: 'Bear',  color: color.loss,    data: PROJ_DATA.map(d => ({ date: d.date, value: d.p10 })) },
            ]}
            splitDate="2024-03-18"
            valueFormat={v => `$${v.toFixed(2)}`}
            title="Bull / Base / Bear Scenarios"
            subtitle="Three scenario overlays"
            height={280}
          />
        </Grid>
      </Section>

      {/* FKWaterfall — P&L bridge */}
      <Section title="FKWaterfall — standalone waterfall / P&L bridge">
        <FKWaterfall
          data={WATERFALL_DATA}
          title="Q2 → Q3 Revenue Bridge"
          subtitle="Revenue drivers by category ($k)"
          valueFormat={v => `$${(v / 1000).toFixed(1)}k`}
          height={260}
        />
      </Section>

      {/* FKBulletChart — price vs analyst target */}
      <Section title="FKBulletChart — Canvas performance bar vs target">
        <FKBulletChart
          data={BULLET_DATA}
          title="Price vs Analyst Target"
          subtitle="Current price relative to 12M price target and 52W range"
          valueFormat={v => `$${v.toFixed(0)}`}
        />
      </Section>

      {/* FKTimeline — earnings + dividends + macro */}
      <Section title="FKTimeline — SVG events on time axis with swim lanes">
        <FKTimeline
          events={TIMELINE_EVENTS}
          dateMin="2024-01-01"
          dateMax="2024-04-15"
          colorMap={{ earnings: color.gain, macro: '#6366f1', dividend: '#f59e0b', research: '#06b6d4', corporate: '#94a3b8' }}
          title="Corporate Calendar"
          subtitle="Earnings, dividends, macro events"
          height={200}
        />
      </Section>

      {/* FKRadarChart — factor profile comparison */}
      <Section title="FKRadarChart — multi-series factor / risk radar">
        <Grid cols={2}>
          <FKRadarChart
            axes={RADAR_AXES}
            series={RADAR_SERIES}
            fillOpacity={0.18}
            title="Factor Profile"
            subtitle="Portfolio vs Benchmark"
            height={300}
          />
          <FKRadarChart
            axes={[
              { key: 'sharpe',   label: 'Sharpe',      max: 3 },
              { key: 'sortino',  label: 'Sortino',     max: 3 },
              { key: 'calmar',   label: 'Calmar',      max: 2 },
              { key: 'beta',     label: 'Beta (inv)',  max: 1 },
              { key: 'drawdown', label: 'Drawdown Ctl', max: 1 },
            ]}
            series={[
              { key: 'fund', label: 'Fund A', data: { sharpe: 1.84, sortino: 2.1, calmar: 0.9, beta: 0.72, drawdown: 0.65 } },
              { key: 'peer', label: 'Peer',   data: { sharpe: 1.21, sortino: 1.5, calmar: 0.6, beta: 0.88, drawdown: 0.48 }, color: '#94a3b8' },
            ]}
            title="Risk-Adjusted Metrics"
            subtitle="Fund A vs Peer"
            height={300}
          />
        </Grid>
      </Section>

      {/* FKSankeyChart — revenue decomposition */}
      <Section title="FKSankeyChart — SVG Sankey / flow diagram">
        <FKSankeyChart
          nodes={SANKEY_NODES}
          flows={SANKEY_FLOWS}
          valueFormat={v => `$${(v / 1000).toFixed(1)}B`}
          title="Revenue → Profit Decomposition"
          subtitle="Annual income statement flow"
          height={360}
        />
      </Section>

      {/* FKBarChart lollipop mode */}
      <Section title="FKBarChart (lollipop mode) — stem + dot encoding">
        <FKBarChart
          data={HOLDINGS.map(h => ({ ticker: h.ticker, alpha: parseFloat((h.return_pct - 0.8).toFixed(2)) }))}
          mode="lollipop"
          valueKey="alpha"
          labelKey="ticker"
          yFormat={v => `${v >= 0 ? '+' : ''}${v.toFixed(2)}%`}
          referenceValue={0}
          title="Holdings Alpha"
          subtitle="Return minus benchmark (lollipop)"
          height={220}
        />
      </Section>

      {/* FKLineChart step interpolation */}
      <Section title="FKLineChart (step interpolation) — regime / allocation step chart">
        <Grid cols={2}>
          <FKLineChart
            data={Array.from({ length: 20 }, (_, i) => ({
              date:  `W${i + 1}`,
              equity: parseFloat((0.55 + Math.round(Math.sin(i * 0.5) * 3) * 0.05).toFixed(2)),
              bonds:  parseFloat((0.30 - Math.round(Math.sin(i * 0.5) * 2) * 0.03).toFixed(2)),
            }))}
            series={[
              { key: 'equity', label: 'Equity' },
              { key: 'bonds',  label: 'Bonds', dashed: true },
            ]}
            xKey="date"
            interpolation="step"
            xType="category"
            yFormat={v => `${(v * 100).toFixed(0)}%`}
            title="Asset Allocation Shifts"
            subtitle="Step chart — discrete regime changes"
            height={220}
          />
          <FKLineChart
            data={Array.from({ length: 24 }, (_, i) => ({
              date:   `${['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][i % 12]} '${i < 12 ? '23' : '24'}`,
              rating: Math.max(1, Math.min(5, Math.round(3 + Math.sin(i * 0.6) * 1.5))),
            }))}
            series={[{ key: 'rating', label: 'Analyst Rating' }]}
            xKey="date"
            interpolation="stepBefore"
            yFormat={v => ['', 'Strong Sell', 'Sell', 'Hold', 'Buy', 'Strong Buy'][v] || v}
            title="Consensus Rating History"
            subtitle="stepBefore interpolation"
            height={220}
          />
        </Grid>
      </Section>

      {/* FKTable pivot mode */}
      <Section title="FKTable (pivot mode) — dynamic cross-tab">
        <FKTable
          rows={[
            { sector: 'Technology', quarter: 'Q1', return_pct:  4.2 },
            { sector: 'Technology', quarter: 'Q2', return_pct:  8.1 },
            { sector: 'Technology', quarter: 'Q3', return_pct: -2.4 },
            { sector: 'Technology', quarter: 'Q4', return_pct:  6.3 },
            { sector: 'Financials', quarter: 'Q1', return_pct:  1.8 },
            { sector: 'Financials', quarter: 'Q2', return_pct: -0.9 },
            { sector: 'Financials', quarter: 'Q3', return_pct:  3.1 },
            { sector: 'Financials', quarter: 'Q4', return_pct:  2.4 },
            { sector: 'Healthcare', quarter: 'Q1', return_pct: -1.2 },
            { sector: 'Healthcare', quarter: 'Q2', return_pct:  2.7 },
            { sector: 'Healthcare', quarter: 'Q3', return_pct:  0.8 },
            { sector: 'Healthcare', quarter: 'Q4', return_pct:  4.1 },
          ]}
          pivotRow="sector"
          pivotCol="quarter"
          pivotValue="return_pct"
          title="Sector Returns by Quarter (%)"
          subtitle="Pivot — rows × quarters"
        />
      </Section>
    </div>
  )
}
