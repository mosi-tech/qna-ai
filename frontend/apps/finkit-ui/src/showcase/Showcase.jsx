import React, { useState, useEffect } from 'react'

import { FKLineChart }       from '../FKLineChart.jsx'
import { FKAreaChart }       from '../FKAreaChart.jsx'
import { FKBandChart }       from '../FKBandChart.jsx'
import { FKCandleChart }     from '../FKCandleChart.jsx'
import { FKAnnotatedChart }  from '../FKAnnotatedChart.jsx'
import { FKMultiPanel }      from '../FKMultiPanel.jsx'
import { FKProjectionChart } from '../FKProjectionChart.jsx'
import { FKBarChart }        from '../FKBarChart.jsx'
import { FKWaterfall }       from '../FKWaterfall.jsx'
import { FKHeatGrid }        from '../FKHeatGrid.jsx'
import { FKHistogram }       from '../FKHistogram.jsx'
import { FKRadarChart }      from '../FKRadarChart.jsx'
import { FKScatterChart }    from '../FKScatterChart.jsx'
import { FKSankeyChart }     from '../FKSankeyChart.jsx'
import { FKPartChart }       from '../FKPartChart.jsx'
import { FKRangeChart }      from '../FKRangeChart.jsx'
import { FKBulletChart }     from '../FKBulletChart.jsx'
import { FKTable }           from '../FKTable.jsx'
import { FKRankedList }      from '../FKRankedList.jsx'
import { FKMetricGrid }      from '../FKMetricGrid.jsx'
import { FKTimeline }        from '../FKTimeline.jsx'
import { FKSparkline, FKDelta, FKBadge, FKStatStrip } from '../FKSparkline.jsx'
import { FKTooltip }         from '../FKTooltip.jsx'
import { FKRangeSelector }   from '../FKRangeSelector.jsx'

// =============================================================================
// DATA GENERATORS  (module-level — deterministic, never regenerated on render)
// =============================================================================

/** Seeded LCG pseudo-random number generator */
function makeLCG(seed) {
  let s = seed >>> 0
  return () => {
    s = Math.imul(s, 1664525) + 1013904223 >>> 0
    return s / 0x100000000
  }
}

/** Random-walk OHLCV generator */
function generateOHLCV(startPrice, days, seedVal, startDate) {
  const rng  = makeLCG(seedVal)
  const data = []
  let price  = startPrice
  let d      = new Date(startDate)
  for (let i = 0; i < days; i++) {
    while (d.getDay() === 0 || d.getDay() === 6) d = new Date(d.getTime() + 864e5)
    const open   = price
    const change = (rng() - 0.47) * 0.018 + 0.0004
    const close  = parseFloat(Math.max(1, open * (1 + change)).toFixed(2))
    const high   = parseFloat((Math.max(open, close) * (1 + rng() * 0.006)).toFixed(2))
    const low    = parseFloat((Math.min(open, close) * (1 - rng() * 0.006)).toFixed(2))
    const volume = Math.floor(30_000_000 + rng() * 80_000_000)
    data.push({ date: d.toISOString().slice(0, 10), open, close, high, low, volume })
    price = close
    d     = new Date(d.getTime() + 864e5)
  }
  return data
}

function toCloseSeries(ohlcv) {
  return ohlcv.map(r => ({ date: r.date, close: r.close }))
}

function normalizeToHundred(series, key) {
  const base = series[0]?.[key] || 1
  return series.map(r => ({ ...r, [key]: parseFloat((r[key] / base * 100).toFixed(3)) }))
}

function computeSMA(data, key, period) {
  return data.map((row, i) => {
    if (i < period - 1) return { ...row, [`sma${period}`]: null }
    const slice = data.slice(i - period + 1, i + 1)
    const avg   = slice.reduce((s, r) => s + r[key], 0) / period
    return { ...row, [`sma${period}`]: parseFloat(avg.toFixed(2)) }
  })
}

function computeRSI(data, key, period) {
  let gains = 0, losses = 0
  return data.map((row, i) => {
    if (i === 0) return { ...row, rsi: 50 }
    const delta = data[i][key] - data[i - 1][key]
    if (i <= period) {
      gains  += Math.max(0, delta)
      losses += Math.max(0, -delta)
      if (i < period) return { ...row, rsi: null }
      const rs = gains / (losses || 1e-9)
      return { ...row, rsi: parseFloat((100 - 100 / (1 + rs)).toFixed(1)) }
    }
    const avgGain = (gains  * (period - 1) + Math.max(0, delta))  / period
    const avgLoss = (losses * (period - 1) + Math.max(0, -delta)) / period
    gains  = avgGain; losses = avgLoss
    const rs = avgGain / (avgLoss || 1e-9)
    return { ...row, rsi: parseFloat((100 - 100 / (1 + rs)).toFixed(1)) }
  })
}

function computeDrawdown(data, key) {
  let peak = data[0]?.[key] || 1
  return data.map(row => {
    if (row[key] > peak) peak = row[key]
    return { ...row, drawdown: parseFloat(((row[key] - peak) / peak * 100).toFixed(3)) }
  })
}

// ── Generate raw OHLCV series ─────────────────────────────────────────────────
const AAPL_OHLCV  = generateOHLCV(180, 1300, 17, '2020-01-02')
const SPY_OHLCV   = generateOHLCV(330, 1300, 99, '2020-01-02')
const QQQ_OHLCV   = generateOHLCV(290, 1300, 77, '2020-01-02')
const BENCH_OHLCV = generateOHLCV(100, 1300, 55, '2020-01-02')

const AAPL_CLOSE  = toCloseSeries(AAPL_OHLCV)
const SPY_CLOSE   = toCloseSeries(SPY_OHLCV)
const QQQ_CLOSE   = toCloseSeries(QQQ_OHLCV)
const BENCH_CLOSE = toCloseSeries(BENCH_OHLCV)

// Normalized to 100 at first point
const AAPL_NORM  = normalizeToHundred(AAPL_CLOSE,  'close')
const SPY_NORM   = normalizeToHundred(SPY_CLOSE,   'close')
const QQQ_NORM   = normalizeToHundred(QQQ_CLOSE,   'close')
const BENCH_NORM = normalizeToHundred(BENCH_CLOSE, 'close')

// QQQ vs SPY merged 5Y
const QQQ_SPY_5Y = QQQ_NORM.slice(-1260).map((r, i) => ({
  date: r.date,
  qqq:  r.close,
  spy:  SPY_NORM.slice(-1260)[i]?.close ?? 100,
}))

// AAPL with SMA20 and SMA200
const AAPL_WITH_SMA = (() => {
  let d = AAPL_CLOSE.map(r => ({ date: r.date, price: r.close }))
  d = computeSMA(d, 'price', 20)
  d = computeSMA(d, 'price', 200)
  return d.slice(-1260)
})()

// Multi-panel data: price + SMA20 + volume + RSI
const MP_DATA = (() => {
  let d = AAPL_CLOSE.map((r, i) => ({ date: r.date, price: r.close, volume: AAPL_OHLCV[i]?.volume || 0 }))
  d = computeSMA(d, 'price', 20)
  d = computeRSI(d, 'price', 14)
  return d.slice(-252)
})()

// Drawdown series
const DD_DATA = computeDrawdown(AAPL_CLOSE.slice(-504), 'close')

// Portfolio equity curve (simulated)
const PORTFOLIO_CURVE = (() => {
  const rng = makeLCG(33)
  let v = 100_000
  return AAPL_CLOSE.slice(-252).map(r => {
    v = v * (1 + (rng() - 0.46) * 0.012)
    return { date: r.date, portfolio: parseFloat(v.toFixed(2)) }
  })
})()

// Sector ETF 6-series data (10Y weekly)
const SECTOR_6_DATA = (() => {
  const rng    = makeLCG(41)
  const labels = ['XLK','XLF','XLV','XLE','XLC','XLU']
  const n      = 520
  const vals   = labels.map((_, si) => {
    let v = 100 + si * 5
    return Array.from({ length: n }, () => { v = v * (1 + (rng() - 0.47) * 0.025); return parseFloat(v.toFixed(2)) })
  })
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
  return Array.from({ length: n }, (_, i) => {
    const yr  = 2015 + Math.floor(i / 52)
    const mo  = months[(Math.floor(i * 12 / 52)) % 12]
    const row = { date: `${mo} ${yr}` }
    labels.forEach((l, si) => { row[l] = vals[si][i] })
    return row
  })
})()

// Sector rotation stacked area (3Y)
const SECTOR_ROT_DATA = (() => {
  const rng    = makeLCG(51)
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
  return Array.from({ length: 36 }, (_, i) => {
    const yr = 2022 + Math.floor(i / 12)
    const mo = months[i % 12]
    return {
      date:   `${mo} ${yr}`,
      tech:   parseFloat((35 + rng() * 8).toFixed(1)),
      fin:    parseFloat((20 + rng() * 6).toFixed(1)),
      health: parseFloat((15 + rng() * 5).toFixed(1)),
      energy: parseFloat((12 + rng() * 4).toFixed(1)),
      other:  parseFloat((10 + rng() * 4).toFixed(1)),
    }
  })
})()

// Two-series spread data
const SPREAD_DATA = AAPL_CLOSE.slice(-504).map((r, i) => ({
  date:      r.date,
  portfolio: r.close,
  benchmark: BENCH_CLOSE.slice(-504)[i]?.close ?? r.close,
}))

// Monthly returns for HeatGrid
const MONTHLY_RETURNS = (() => {
  const rng    = makeLCG(9)
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
  const years  = ['2020','2021','2022','2023','2024']
  return years.flatMap(year =>
    months.map(month => ({
      month, year,
      return_pct: parseFloat(((rng() - 0.42) * 14).toFixed(2)),
    }))
  )
})()

// 8×8 sector heatmap
const SECTOR_HEAT = (() => {
  const rng     = makeLCG(23)
  const sectors = ['Tech','Fin','Health','Energy','Consumer','Util','Mats','Indus']
  const periods = ['Q1-22','Q2-22','Q3-22','Q4-22','Q1-23','Q2-23','Q3-23','Q4-23']
  return sectors.flatMap(sector => periods.map(period => ({
    sector, period, value: parseFloat(((rng() - 0.42) * 20).toFixed(2)),
  })))
})()

// Daily returns
const DAILY_RETURNS = AAPL_CLOSE.slice(1).map((r, i) => {
  const prev = AAPL_CLOSE[i].close
  return parseFloat(((r.close - prev) / prev * 100).toFixed(4))
})

// 500 random returns
const RETURNS_500 = (() => {
  const rng = makeLCG(3)
  return Array.from({ length: 500 }, () =>
    parseFloat(((rng() - 0.48) * 5 + (rng() - 0.5) * 1.5).toFixed(4))
  )
})()

// Earnings beat/miss
const EARNINGS_DATA = (() => {
  const rng = makeLCG(13)
  return Array.from({ length: 10 }, (_, i) => {
    const yr  = 2022 + Math.floor(i / 4)
    const est = 1.20 + i * 0.04
    const act = est + (rng() - 0.4) * 0.25
    return { label: `Q${(i % 4) + 1} ${yr}`, estimate: parseFloat(est.toFixed(2)), actual: parseFloat(act.toFixed(2)) }
  })
})()

// Lollipop: 30 tickers YTD return
const LOLLIPOP_DATA = (() => {
  const rng     = makeLCG(19)
  const tickers = ['AAPL','MSFT','NVDA','AMZN','GOOGL','META','TSLA','BRK.B','JPM','V','UNH','JNJ','PG','KO','PEP','WMT','DIS','NFLX','ADBE','CRM','ORCL','AMD','INTC','QCOM','TXN','AVGO','MU','AMAT','KLAC','LRCX']
  return tickers.map(label => ({ label, value: parseFloat(((rng() - 0.42) * 40).toFixed(1)) }))
})()

// P&L waterfall
const PNL_DATA = [
  { label: 'Start NAV',    value: 1_000_000, type: 'start' },
  { label: 'Long Alpha',   value:   84_000,  type: 'delta' },
  { label: 'Short Alpha',  value:  -12_000,  type: 'delta' },
  { label: 'Market Beta',  value:   31_000,  type: 'delta' },
  { label: 'Factor Risk',  value:  -18_000,  type: 'delta' },
  { label: 'FX Gains',     value:    9_500,  type: 'delta' },
  { label: 'Dividends',    value:   22_000,  type: 'delta' },
  { label: 'Fees & Cost',  value:  -14_500,  type: 'delta' },
  { label: 'Tax Drag',     value:   -7_000,  type: 'delta' },
  { label: 'Options P&L',  value:   16_000,  type: 'delta' },
  { label: 'Cash Drag',    value:   -4_000,  type: 'delta' },
  { label: 'End NAV',      value: 1_107_000, type: 'end'   },
]

// Scatter: 200 stocks
const SCATTER_200 = (() => {
  const rng     = makeLCG(27)
  const sectors = ['Technology','Financials','Healthcare','Consumer','Energy','Industrials']
  return Array.from({ length: 200 }, (_, i) => ({
    ticker: `T${i}`,
    sector: sectors[Math.floor(rng() * sectors.length)],
    vol:    parseFloat((10 + rng() * 35).toFixed(1)),
    ret:    parseFloat((-10 + rng() * 55).toFixed(1)),
    mktcap: parseFloat((1 + rng() * 99).toFixed(1)),
  }))
})()

// Radar data
const RADAR_AXES = [
  { key: 'value',    label: 'Value',    max: 100 },
  { key: 'quality',  label: 'Quality',  max: 100 },
  { key: 'momentum', label: 'Momentum', max: 100 },
  { key: 'growth',   label: 'Growth',   max: 100 },
  { key: 'safety',   label: 'Safety',   max: 100 },
]
const RADAR_SERIES_2 = [
  { key: 'AAPL', label: 'AAPL', data: { value: 62, quality: 88, momentum: 74, growth: 71, safety: 80 } },
  { key: 'MSFT', label: 'MSFT', data: { value: 55, quality: 91, momentum: 68, growth: 78, safety: 85 } },
]
const RADAR_AXES_8 = [
  { key: 'value',     label: 'Value',     max: 100 },
  { key: 'quality',   label: 'Quality',   max: 100 },
  { key: 'momentum',  label: 'Momentum',  max: 100 },
  { key: 'growth',    label: 'Growth',    max: 100 },
  { key: 'safety',    label: 'Safety',    max: 100 },
  { key: 'dividend',  label: 'Dividend',  max: 100 },
  { key: 'liquidity', label: 'Liquidity', max: 100 },
  { key: 'earnings',  label: 'Earnings',  max: 100 },
]
const RADAR_SERIES_3 = [
  { key: 'AAPL', label: 'AAPL', data: { value: 62, quality: 88, momentum: 74, growth: 71, safety: 80, dividend: 30, liquidity: 95, earnings: 78 } },
  { key: 'MSFT', label: 'MSFT', data: { value: 55, quality: 91, momentum: 68, growth: 78, safety: 85, dividend: 35, liquidity: 90, earnings: 82 } },
  { key: 'NVDA', label: 'NVDA', data: { value: 42, quality: 80, momentum: 95, growth: 92, safety: 52, dividend: 15, liquidity: 75, earnings: 90 } },
]

// Sankey: revenue decomposition
const SANKEY_REVENUE_NODES = [
  { id: 'iphone',   label: 'iPhone',       column: 0 },
  { id: 'mac',      label: 'Mac',          column: 0 },
  { id: 'services', label: 'Services',     column: 0 },
  { id: 'other',    label: 'Other',        column: 0 },
  { id: 'gross',    label: 'Gross Profit', column: 1 },
  { id: 'opex',     label: 'OpEx',         column: 1 },
  { id: 'ebit',     label: 'EBIT',         column: 2 },
  { id: 'tax',      label: 'Tax',          column: 2 },
  { id: 'net',      label: 'Net Income',   column: 3 },
]
const SANKEY_REVENUE_FLOWS = [
  { from: 'iphone',   to: 'gross', value: 120 },
  { from: 'mac',      to: 'gross', value: 30  },
  { from: 'services', to: 'gross', value: 80  },
  { from: 'other',    to: 'gross', value: 20  },
  { from: 'gross',    to: 'ebit',  value: 160 },
  { from: 'gross',    to: 'opex',  value: 90  },
  { from: 'ebit',     to: 'net',   value: 115 },
  { from: 'ebit',     to: 'tax',   value: 45  },
]

// Sankey: 4-column fund flow
const SANKEY_FUND_NODES = [
  { id: 'lp1',      label: 'LP Pension',    column: 0 },
  { id: 'lp2',      label: 'LP Endowment',  column: 0 },
  { id: 'lp3',      label: 'LP Family',     column: 0 },
  { id: 'fundA',    label: 'Fund A',         column: 1 },
  { id: 'fundB',    label: 'Fund B',         column: 1 },
  { id: 'equities', label: 'Equities',       column: 2 },
  { id: 'credit',   label: 'Credit',         column: 2 },
  { id: 'alts',     label: 'Alts',           column: 2 },
  { id: 'returnA',  label: 'Return A',       column: 3 },
  { id: 'returnB',  label: 'Return B',       column: 3 },
]
const SANKEY_FUND_FLOWS = [
  { from: 'lp1',      to: 'fundA',    value: 200 },
  { from: 'lp2',      to: 'fundA',    value: 150 },
  { from: 'lp2',      to: 'fundB',    value: 100 },
  { from: 'lp3',      to: 'fundB',    value: 80  },
  { from: 'fundA',    to: 'equities', value: 250 },
  { from: 'fundA',    to: 'credit',   value: 100 },
  { from: 'fundB',    to: 'equities', value: 80  },
  { from: 'fundB',    to: 'alts',     value: 100 },
  { from: 'equities', to: 'returnA',  value: 200 },
  { from: 'equities', to: 'returnB',  value: 130 },
  { from: 'credit',   to: 'returnA',  value: 100 },
  { from: 'alts',     to: 'returnB',  value: 100 },
]

// Holdings
const HOLDINGS_DATA = [
  { ticker: 'AAPL',  value: 42800, weight: 19.3, return_pct:  18.7, sector: 'Technology', spark: [130,138,142,148,145,152,158,162,170,178] },
  { ticker: 'MSFT',  value: 36200, weight: 16.3, return_pct:  14.2, sector: 'Technology', spark: [280,285,292,290,298,302,310,318,320,330] },
  { ticker: 'NVDA',  value: 29400, weight: 13.2, return_pct:  38.4, sector: 'Technology', spark: [400,430,420,460,490,510,540,560,590,620] },
  { ticker: 'AMZN',  value: 22600, weight: 10.2, return_pct:  -2.1, sector: 'Consumer',   spark: [170,175,178,172,174,178,176,180,178,174] },
  { ticker: 'GOOGL', value: 19300, weight:  8.7, return_pct:   8.5, sector: 'Technology', spark: [130,135,133,138,140,145,142,148,150,152] },
  { ticker: 'META',  value: 16700, weight:  7.5, return_pct:  24.1, sector: 'Technology', spark: [200,215,210,225,230,240,248,255,262,270] },
  { ticker: 'BRK.B', value: 14000, weight:  6.3, return_pct:   5.2, sector: 'Financials', spark: [310,312,315,318,316,320,322,320,325,326] },
  { ticker: 'JPM',   value: 12600, weight:  5.7, return_pct:   9.8, sector: 'Financials', spark: [145,148,150,152,155,153,157,160,162,166] },
  { ticker: 'UNH',   value: 11200, weight:  5.0, return_pct:  -3.4, sector: 'Healthcare', spark: [480,490,488,492,486,484,490,488,482,478] },
  { ticker: 'JNJ',   value:  9400, weight:  4.2, return_pct:  -1.8, sector: 'Healthcare', spark: [155,158,156,160,158,155,157,154,152,150] },
]

const TABLE_COLUMNS = [
  { key: 'ticker', label: 'Symbol' },
  { key: 'value',  label: 'Value',   align: 'right', mono: true, format: v => `$${v.toLocaleString()}` },
  { key: 'weight', label: 'Weight',  align: 'right', mono: true, format: v => `${v.toFixed(1)}%` },
  {
    key: 'return_pct', label: 'Return', align: 'right', mono: true,
    colorRule: v => v >= 0 ? 'gain' : 'loss',
    format:    v => `${v >= 0 ? '+' : ''}${v.toFixed(2)}%`,
  },
  { key: 'sector', label: 'Sector' },
]

// Range chart data
const RANGE_52W = [
  { label: 'AAPL',  min: 143.90, max: 223.45, value: 189.30, target: 210.00 },
  { label: 'MSFT',  min: 309.00, max: 468.35, value: 379.91, target: 430.00 },
  { label: 'NVDA',  min: 402.75, max: 974.00, value: 876.40, target: 950.00 },
  { label: 'AMZN',  min: 101.20, max: 201.20, value: 187.55, target: 215.00 },
  { label: 'GOOGL', min:  91.00, max: 193.31, value: 166.80, target: 190.00 },
  { label: 'META',  min: 164.08, max: 589.00, value: 481.60, target: 540.00 },
  { label: 'BRK.B', min: 311.00, max: 404.50, value: 361.30, target: 385.00 },
  { label: 'JPM',   min: 135.19, max: 225.48, value: 201.18, target: 220.00 },
]

const MANDATE_DATA = [
  { label: 'Equities',    min: 0, max: 80, value: 74, target: 60 },
  { label: 'Fixed Inc',   min: 0, max: 60, value: 42, target: 40 },
  { label: 'Alternatives',min: 0, max: 30, value: 28, target: 20 },
  { label: 'Cash',        min: 0, max: 20, value:  6, target: 10 },
  { label: 'Commodities', min: 0, max: 15, value: 12, target: 10 },
]

// Bullet chart data
const BULLET_STOCKS = [
  { label: 'AAPL price',  value: 189.30, target: 210.00, rangeMin: 130, rangeMax: 250 },
  { label: 'MSFT price',  value: 379.91, target: 430.00, rangeMin: 280, rangeMax: 480 },
  { label: 'NVDA price',  value: 876.40, target: 950.00, rangeMin: 400, rangeMax: 1050 },
  { label: 'AMZN price',  value: 187.55, target: 215.00, rangeMin: 100, rangeMax: 240 },
  { label: 'GOOGL price', value: 166.80, target: 190.00, rangeMin:  90, rangeMax: 210 },
]

const BULLET_EPS = [
  { label: 'AAPL EPS ($)',     value: 2.40, target: 2.35, rangeMin: 2.00, rangeMax: 2.80 },
  { label: 'MSFT EPS ($)',     value: 3.23, target: 3.10, rangeMin: 2.70, rangeMax: 3.60 },
  { label: 'NVDA EPS ($)',     value: 0.89, target: 0.77, rangeMin: 0.50, rangeMax: 1.10 },
  { label: 'Revenue ($B)',     value: 89.5, target: 88.0, rangeMin: 82.0, rangeMax: 96.0 },
]

// Portfolio donut
const PORTFOLIO_DONUT = [
  { label: 'US Equities',   value: 52.3 },
  { label: 'Intl Equities', value: 18.4 },
  { label: 'Fixed Income',  value: 14.7 },
  { label: 'Alternatives',  value:  8.6 },
  { label: 'Cash',          value:  4.2 },
  { label: 'Commodities',   value:  1.8 },
]

// Treemap with return coloring
const TREEMAP_DATA = HOLDINGS_DATA.map(r => ({
  label:  r.ticker,
  value:  r.value / 1000,
  return: r.return_pct,
}))

// Ranked list
const TOP_MOVERS = HOLDINGS_DATA.slice(0, 8).map(r => ({
  label: r.ticker,
  value: `${r.return_pct >= 0 ? '+' : ''}${r.return_pct.toFixed(1)}%`,
  delta: r.return_pct,
  sub:   r.sector,
  spark: r.spark,
}))

const MOVERS_20 = (() => {
  const rng = makeLCG(61)
  const tickers = ['AAPL','MSFT','NVDA','AMZN','GOOGL','META','TSLA','BRK.B','JPM','V','UNH','JNJ','PG','KO','PEP','WMT','DIS','NFLX','ADBE','CRM']
  return tickers.map(label => {
    const d = parseFloat(((rng() - 0.42) * 12).toFixed(2))
    return {
      label, sub: 'Equity',
      value: `${d >= 0 ? '+' : ''}${d.toFixed(1)}%`,
      delta: d,
      spark: Array.from({ length: 10 }, () => parseFloat((50 + rng() * 30).toFixed(1))),
    }
  })
})()

// KPI cards
const PORTFOLIO_METRICS = [
  { label: 'Portfolio Value', value: '$221,700', delta: 1.99,  sub: 'today',           spark: [190,195,200,205,202,210,215,218,220,222] },
  { label: 'YTD Return',      value: '+18.4%',   delta: 18.4,  sub: 'vs benchmark +11.2%' },
  { label: 'Sharpe Ratio',    value: '1.84',     sub: '3-year' },
  { label: 'Max Drawdown',    value: '−21.3%',   color: '#dc2626', sub: 'peak to trough' },
]

const METRICS_STRESS = [
  { label: 'Portfolio Value',  value: '$221,700',  delta:  1.99, sub: 'today',           spark: [190,195,200,205,202,210,215,218,220,222] },
  { label: 'YTD Return',       value: '+18.4%',    delta: 18.4,  sub: 'vs SPY +11.2%',  spark: [95,100,102,105,108,110,112,115,118,122] },
  { label: 'Alpha (3Y Ann)',   value: '+7.2%',     delta:  7.2,  sub: 'vs benchmark',   spark: [100,102,103,105,104,106,107,108,109,110] },
  { label: 'Sharpe Ratio',     value: '1.84',       sub: '3-year rolling',              spark: [1.2,1.4,1.5,1.6,1.7,1.8,1.75,1.82,1.84,1.84] },
  { label: 'Sortino Ratio',    value: '2.31',       sub: 'threshold 0%',               spark: [1.8,1.9,2.0,2.1,2.2,2.1,2.3,2.3,2.3,2.3] },
  { label: 'Beta (1Y)',        value: '0.87',       sub: 'vs S&P 500',                 spark: [0.9,0.88,0.87,0.86,0.87,0.88,0.87,0.87,0.87,0.87] },
  { label: 'Max Drawdown',     value: '−21.3%',    color: '#dc2626', sub: 'peak to trough' },
  { label: 'Volatility (Ann)', value: '14.2%',      sub: '252-day', color: '#f59e0b' },
]

// Timeline events
const TIMELINE_EVENTS = [
  { date: '2025-01-28', label: 'AAPL Q1',     row: 'Earnings',  type: 'beat',     value: 'EPS $2.40 beat $2.35' },
  { date: '2025-02-05', label: 'MSFT Q2',     row: 'Earnings',  type: 'beat',     value: 'EPS $3.23 beat $3.10' },
  { date: '2025-02-26', label: 'NVDA Q4',     row: 'Earnings',  type: 'beat',     value: 'EPS $0.89 beat $0.77' },
  { date: '2025-04-29', label: 'AAPL Q2',     row: 'Earnings',  type: 'miss',     value: 'EPS $1.52 miss $1.55' },
  { date: '2025-02-13', label: 'AAPL Div',    row: 'Dividends', type: 'dividend', value: '$0.25/share' },
  { date: '2025-05-15', label: 'MSFT Div',    row: 'Dividends', type: 'dividend', value: '$0.75/share' },
  { date: '2025-01-29', label: 'Fed Hold',    row: 'Macro',     type: 'fed',      value: 'Rates unchanged 5.25–5.5%' },
  { date: '2025-03-19', label: 'Fed Meeting', row: 'Macro',     type: 'fed',      value: 'Rate decision' },
  { from: '2025-02-01', to: '2025-03-15', label: 'AAPL Lock-up', row: 'Events', type: 'lockup', value: 'Insider lock-up period' },
  { from: '2025-03-01', to: '2025-04-10', label: 'SEC Filing',   row: 'Events', type: 'filing', value: '10-Q deadline window' },
]
const TIMELINE_COLORMAP = {
  beat:     '#16a34a',
  miss:     '#dc2626',
  dividend: '#6366f1',
  fed:      '#f59e0b',
  lockup:   '#94a3b8',
  filing:   '#06b6d4',
}

const TIMELINE_STRESS = [
  { date: '2025-01-15', label: 'Earnings Q1', row: 'Earnings',  type: 'beat',  value: 'EPS $2.40' },
  { date: '2025-02-15', label: 'Earnings Q4', row: 'Guidance',  type: 'miss',  value: 'EPS $1.52' },
  { date: '2025-03-15', label: 'Earnings Q1', row: 'Earnings',  type: 'beat',  value: 'EPS $3.23' },
  { date: '2025-04-15', label: 'Guidance Q2', row: 'Guidance',  type: 'beat',  value: 'EPS $0.89' },
  { date: '2025-05-15', label: 'Earnings Q2', row: 'Earnings',  type: 'miss',  value: 'EPS $1.43' },
  { date: '2025-06-15', label: 'Guidance Q3', row: 'Guidance',  type: 'beat',  value: 'EPS $2.10' },
  { date: '2025-07-15', label: 'Earnings Q2', row: 'Earnings',  type: 'beat',  value: 'EPS $3.50' },
  { date: '2025-08-15', label: 'Guidance Q4', row: 'Guidance',  type: 'miss',  value: 'EPS $1.20' },
  { from: '2025-01-01', to: '2025-03-31', label: 'Q1 Period', row: 'Fiscal', type: 'lockup', value: 'Q1 fiscal quarter' },
  { from: '2025-04-01', to: '2025-06-30', label: 'Q2 Period', row: 'Fiscal', type: 'filing', value: 'Q2 fiscal quarter' },
  { from: '2025-07-01', to: '2025-09-30', label: 'Q3 Period', row: 'Fiscal', type: 'lockup', value: 'Q3 fiscal quarter' },
]

// Projection data
const PROJ_HIST = (() => {
  let v = 50_000
  const rng = makeLCG(89)
  return Array.from({ length: 20 }, (_, i) => {
    v = v * (1 + 0.07 + (rng() - 0.5) * 0.04)
    return { date: String(2005 + i), value: Math.round(v) }
  })
})()

const PROJ_FAN = (() => {
  const last = PROJ_HIST[PROJ_HIST.length - 1].value
  return Array.from({ length: 30 }, (_, i) => ({
    date:   String(2025 + i),
    median: Math.round(last * Math.pow(1.07, i + 1)),
    p25:    Math.round(last * Math.pow(1.05, i + 1)),
    p75:    Math.round(last * Math.pow(1.09, i + 1)),
    p10:    Math.round(last * Math.pow(1.03, i + 1)),
    p90:    Math.round(last * Math.pow(1.11, i + 1)),
  }))
})()

const PROJ_SCENARIOS_HIST = [
  { date: '2020', value: 100_000 },
  { date: '2021', value: 118_000 },
  { date: '2022', value: 109_000 },
  { date: '2023', value: 134_000 },
  { date: '2024', value: 158_000 },
]
const PROJ_SCENARIOS = [
  { key: 'bull', label: 'Bull Case', color: '#16a34a', data: [{ date: '2025', value: 182000 }, { date: '2027', value: 240000 }, { date: '2030', value: 390000 }] },
  { key: 'base', label: 'Base Case', color: '#6366f1', data: [{ date: '2025', value: 172000 }, { date: '2027', value: 210000 }, { date: '2030', value: 270000 }] },
  { key: 'bear', label: 'Bear Case', color: '#dc2626', data: [{ date: '2025', value: 155000 }, { date: '2027', value: 143000 }, { date: '2030', value: 165000 }] },
]

// Pivot table data
const PIVOT_MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
const PIVOT_YEARS  = ['2021','2022','2023','2024']
const PIVOT_DATA   = (() => {
  const rng = makeLCG(71)
  return PIVOT_YEARS.flatMap(year =>
    PIVOT_MONTHS.map(month => ({
      year, month,
      return: parseFloat(((rng() - 0.42) * 14).toFixed(2)),
    }))
  )
})()

// =============================================================================
// LAYOUT COMPONENTS
// =============================================================================

function NavLink({ label, active, onClick, indent }) {
  return (
    <button
      onClick={onClick}
      style={{
        display:     'block',
        width:       '100%',
        textAlign:   'left',
        padding:     indent ? '6px 20px 6px 28px' : '7px 20px',
        fontSize:    12,
        fontFamily:  'var(--font-sans)',
        fontWeight:  active ? 600 : 400,
        color:       active ? 'var(--color-text-primary)' : 'var(--color-text-secondary)',
        background:  active ? 'var(--color-background-secondary)' : 'transparent',
        borderLeft:  active ? '2px solid #6366f1' : '2px solid transparent',
        border:      'none',
        cursor:      'pointer',
        transition:  'background 0.1s',
        lineHeight:  1.4,
      }}
      onMouseEnter={e => { if (!active) e.currentTarget.style.background = 'var(--color-background-secondary)' }}
      onMouseLeave={e => { if (!active) e.currentTarget.style.background = 'transparent' }}
    >
      {label}
    </button>
  )
}

function NavSection({ title }) {
  return (
    <div style={{
      padding:       '12px 20px 4px',
      fontSize:      9,
      fontWeight:    700,
      letterSpacing: '0.08em',
      textTransform: 'uppercase',
      color:         'var(--color-text-tertiary)',
      fontFamily:    'var(--font-mono)',
      borderTop:     '0.5px solid var(--color-border-tertiary)',
      marginTop:     4,
    }}>
      {title}
    </div>
  )
}

function PageTitle({ name, desc }) {
  return (
    <div style={{ marginBottom: 28 }}>
      <h1 style={{ fontSize: 26, fontWeight: 700, fontFamily: 'var(--font-sans)', color: 'var(--color-text-primary)', margin: 0, lineHeight: 1.2 }}>
        {name}
      </h1>
      {desc && (
        <p style={{ fontSize: 14, color: 'var(--color-text-secondary)', marginTop: 6, marginBottom: 0, lineHeight: 1.5 }}>
          {desc}
        </p>
      )}
      <div style={{ height: 1, background: 'var(--color-border-tertiary)', marginTop: 16 }} />
    </div>
  )
}

function DemoVariant({ title, children, props: chipProps }) {
  const chips = chipProps || []
  return (
    <div style={{ marginBottom: 32 }}>
      <div style={{
        fontSize: 11, fontWeight: 600, color: 'var(--color-text-tertiary)',
        marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.06em',
        fontFamily: 'var(--font-mono)',
      }}>
        {title}
      </div>
      {children}
      {chips.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 10 }}>
          {chips.map((p, i) => (
            <span key={i} style={{
              padding: '2px 8px',
              background: 'var(--color-background-tertiary)',
              color: 'var(--color-text-secondary)',
              borderRadius: 6, fontSize: 11,
              fontFamily: 'var(--font-mono)',
              border: '1px solid var(--color-border-tertiary)',
            }}>
              {p}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}

// =============================================================================
// PAGE COMPONENTS
// =============================================================================

function OverviewPage() {
  const annotEvents = [
    { date: PORTFOLIO_CURVE[20]?.date,  type: 'buy',  label: 'Rebalanced',  value: 'Q1 rebalance' },
    { date: PORTFOLIO_CURVE[80]?.date,  type: 'sell', label: 'Risk-off',    value: 'Reduced equities' },
    { date: PORTFOLIO_CURVE[150]?.date, type: 'buy',  label: 'Added Alpha', value: 'Long NVDA' },
  ]
  const annotBands = [
    { from: PORTFOLIO_CURVE[40]?.date, to: PORTFOLIO_CURVE[60]?.date, color: 'rgba(220,38,38,0.07)', label: 'Drawdown' },
  ]
  const annotCallouts = [
    { date: PORTFOLIO_CURVE[10]?.date,  label: 'Fed hike +25bp', color: '#f59e0b' },
    { date: PORTFOLIO_CURVE[120]?.date, label: 'Earnings beat',  color: '#16a34a' },
  ]
  return (
    <div>
      <PageTitle name="Overview" desc="A realistic portfolio dashboard composing multiple FINKIT components." />
      <div style={{ marginBottom: 20 }}>
        <FKMetricGrid cards={PORTFOLIO_METRICS} cols={4} />
      </div>
      <div style={{ marginBottom: 20 }}>
        <FKAnnotatedChart
          data={PORTFOLIO_CURVE}
          xKey="date"
          series={[{ key: 'portfolio', label: 'Portfolio NAV', type: 'area', color: '#6366f1' }]}
          events={annotEvents}
          bands={annotBands}
          callouts={annotCallouts}
          height={300}
          title="Portfolio Equity Curve"
          subtitle="1-Year daily NAV with event annotations"
          defaultRange="1Y"
        />
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16, marginBottom: 20 }}>
        <FKPartChart
          data={PORTFOLIO_DONUT}
          mode="donut"
          title="Allocation"
          subtitle="Portfolio weights"
          innerLabel="$221.7K"
          innerSub="NAV"
        />
        <FKRankedList
          data={TOP_MOVERS.slice(0, 6)}
          title="Top Holdings"
          subtitle="By portfolio contribution"
        />
        <FKBulletChart
          data={BULLET_STOCKS.slice(0, 4)}
          title="Price vs Target"
          subtitle="Analyst consensus targets"
          valueFormat={v => `$${v.toFixed(0)}`}
        />
      </div>
      <FKTable
        columns={TABLE_COLUMNS}
        rows={HOLDINGS_DATA}
        sparkKey="spark"
        defaultSort="value"
        title="Holdings"
        subtitle="Full portfolio position table"
        stickyHeader
      />
    </div>
  )
}

// ── Time Series ───────────────────────────────────────────────────────────────

function FKLineChartPage() {
  const stressSeries = ['XLK','XLF','XLV','XLE','XLC','XLU'].map((k, i) => ({
    key: k, label: k,
    color: ['#6366f1','#06b6d4','#10b981','#f59e0b','#8b5cf6','#ec4899'][i],
  }))
  return (
    <div>
      <PageTitle name="FKLineChart" desc="Multi-series line chart with optional gradient fills, reference lines, and range selector." />
      <DemoVariant title="Default — no props (built-in sample data)">
        <FKLineChart />
      </DemoVariant>
      <DemoVariant
        title="Finance-realistic — QQQ vs SPY normalized to 100 (5Y)"
        props={['series=[{key:"qqq"},{key:"spy",dashed:true}]', 'yFormat={v => v.toFixed(1)}', 'rangeSelector', 'defaultRange="1Y"']}
      >
        <FKLineChart
          data={QQQ_SPY_5Y}
          xKey="date"
          series={[
            { key: 'qqq', label: 'QQQ', color: '#6366f1' },
            { key: 'spy', label: 'SPY', color: '#f59e0b', dashed: true },
          ]}
          yFormat={v => v.toFixed(1)}
          rangeSelector
          defaultRange="1Y"
          title="QQQ vs SPY"
          subtitle="Normalized to 100 at start — 5Y"
          height={260}
        />
      </DemoVariant>
      <DemoVariant
        title="Stress — 6 sector ETFs (10Y), referenceLines at 100"
        props={['series (6 ETFs)', 'referenceLines=[{y:100}]', 'height={300}']}
      >
        <FKLineChart
          data={SECTOR_6_DATA.slice(-520)}
          xKey="date"
          series={stressSeries}
          yFormat={v => v.toFixed(0)}
          referenceLines={[{ y: 100, label: 'Base', dashed: true, color: 'rgba(0,0,0,0.25)' }]}
          height={300}
          title="Sector ETF Performance"
          subtitle="6 sectors, 10-year, normalized"
        />
      </DemoVariant>
    </div>
  )
}

function FKAreaChartPage() {
  const stackedSeries = [
    { key: 'tech',   label: 'Technology' },
    { key: 'fin',    label: 'Financials' },
    { key: 'health', label: 'Healthcare' },
    { key: 'energy', label: 'Energy' },
    { key: 'other',  label: 'Other' },
  ]
  return (
    <div>
      <PageTitle name="FKAreaChart" desc="Stacked and normalized area chart for part-of-whole and sector rotation." />
      <DemoVariant title="Default — no props">
        <FKAreaChart />
      </DemoVariant>
      <DemoVariant
        title="Finance-realistic — Sector rotation, mode='normalized' (3Y)"
        props={['mode="normalized"', 'series (5 sectors)', 'rangeSelector']}
      >
        <FKAreaChart
          data={SECTOR_ROT_DATA}
          series={stackedSeries}
          xKey="date"
          mode="normalized"
          rangeSelector
          defaultRange="1Y"
          title="Sector Allocation Over Time"
          subtitle="% share normalized to 100%"
          height={280}
        />
      </DemoVariant>
      <DemoVariant
        title="Stress — 5 stacked series (mode='stacked')"
        props={['mode="stacked"', 'series (5)']}
      >
        <FKAreaChart
          data={SECTOR_ROT_DATA}
          series={stackedSeries}
          xKey="date"
          mode="stacked"
          title="Sector $ Exposure (Stacked)"
          subtitle="Absolute weights stacked area"
          height={280}
        />
      </DemoVariant>
    </div>
  )
}

function FKBandChartPage() {
  return (
    <div>
      <PageTitle name="FKBandChart" desc="Single-series fill above/below baseline, or two-series fill-between band chart." />
      <DemoVariant title="Default — no props">
        <FKBandChart />
      </DemoVariant>
      <DemoVariant
        title="Finance-realistic — Drawdown chart (fill below only)"
        props={['series=[{key:"drawdown"}]', 'fillAbove={null}', 'fillBelow="#dc2626"', 'baseline={0}']}
      >
        <FKBandChart
          data={DD_DATA}
          xKey="date"
          series={[{ key: 'drawdown', label: 'Drawdown %' }]}
          baseline={0}
          fillAbove={null}
          fillBelow="#dc2626"
          fillBelowOpacity={0.35}
          yFormat={v => `${v.toFixed(1)}%`}
          title="Portfolio Drawdown"
          subtitle="% decline from rolling peak — 2Y"
          height={200}
        />
      </DemoVariant>
      <DemoVariant
        title="Stress — Two-series spread (portfolio vs benchmark, 5Y)"
        props={['series (2)', 'fillAbove="#6366f1"']}
      >
        <FKBandChart
          data={SPREAD_DATA}
          xKey="date"
          series={[
            { key: 'portfolio', label: 'Portfolio', color: '#6366f1' },
            { key: 'benchmark', label: 'Benchmark', color: '#94a3b8' },
          ]}
          fillAbove="#6366f1"
          fillAboveOpacity={0.12}
          title="Portfolio vs Benchmark Spread"
          subtitle="5-year, fill shows outperformance"
          height={220}
        />
      </DemoVariant>
    </div>
  )
}

function FKCandleChartPage() {
  const longData = generateOHLCV(120, 2520, 37, '2015-01-02')
  return (
    <div>
      <PageTitle name="FKCandleChart" desc="Canvas-rendered OHLC candlestick chart with volume bars, scroll and zoom." />
      <DemoVariant title="Default — no props">
        <FKCandleChart />
      </DemoVariant>
      <DemoVariant
        title="Finance-realistic — AAPL 5Y with volume + range selector"
        props={['data={aaplOHLCV}', 'showVolume={true}', 'rangeSelector={true}', 'defaultRange="1Y"']}
      >
        <FKCandleChart
          data={AAPL_OHLCV}
          showVolume
          rangeSelector
          defaultRange="1Y"
          height={360}
          title="AAPL Price"
          subtitle="5Y OHLCV with volume bars, scrollable"
        />
      </DemoVariant>
      <DemoVariant
        title="Stress — 10Y dataset (2520 candles)"
        props={['data (2520 candles)', 'defaultRange="5Y"']}
      >
        <FKCandleChart
          data={longData}
          showVolume
          rangeSelector
          defaultRange="5Y"
          height={300}
          title="10-Year Price History"
          subtitle="2520 trading days, drag to pan, scroll to zoom"
        />
      </DemoVariant>
    </div>
  )
}

function FKAnnotatedChartPage() {
  const finEvents = [
    { date: AAPL_WITH_SMA[30]?.date,  type: 'buy',  label: 'Golden Cross', value: 'SMA20 crossed above SMA200' },
    { date: AAPL_WITH_SMA[120]?.date, type: 'sell', label: 'Death Cross',  value: 'SMA20 crossed below SMA200' },
    { date: AAPL_WITH_SMA[200]?.date, type: 'buy',  label: 'Re-Entry',     value: 'Price reclaimed SMA20' },
  ]
  const finBands = [
    { from: AAPL_WITH_SMA[80]?.date, to: AAPL_WITH_SMA[130]?.date, color: 'rgba(220,38,38,0.07)', label: 'Bear regime' },
  ]
  const finCallouts = [
    { date: AAPL_WITH_SMA[50]?.date,  label: 'Fed +50bps',   color: '#f59e0b' },
    { date: AAPL_WITH_SMA[180]?.date, label: 'Earnings beat', color: '#16a34a' },
  ]
  const stressEvents = [
    { date: AAPL_WITH_SMA[10]?.date,  type: 'buy',  label: 'Buy' },
    { date: AAPL_WITH_SMA[40]?.date,  type: 'sell', label: 'Sell' },
    { date: AAPL_WITH_SMA[90]?.date,  type: 'buy',  label: 'Buy' },
    { date: AAPL_WITH_SMA[130]?.date, type: 'sell', label: 'Sell' },
    { date: AAPL_WITH_SMA[170]?.date, type: 'buy',  label: 'Buy' },
  ]
  const stressBands = [
    { from: AAPL_WITH_SMA[0]?.date,   to: AAPL_WITH_SMA[30]?.date,  color: 'rgba(22,163,74,0.07)',  label: 'Bull' },
    { from: AAPL_WITH_SMA[60]?.date,  to: AAPL_WITH_SMA[100]?.date, color: 'rgba(220,38,38,0.07)', label: 'Bear' },
    { from: AAPL_WITH_SMA[140]?.date, to: AAPL_WITH_SMA[180]?.date, color: 'rgba(99,102,241,0.07)', label: 'Sideways' },
  ]
  return (
    <div>
      <PageTitle name="FKAnnotatedChart" desc="Price chart with event markers (buy/sell), shaded regime bands, and callout boxes." />
      <DemoVariant title="Default — no props">
        <FKAnnotatedChart />
      </DemoVariant>
      <DemoVariant
        title="Finance-realistic — Price + SMA20 + SMA200 + signals + recession bands"
        props={['series (price+sma20+sma200)', 'events (3)', 'bands (1)', 'callouts (2)']}
      >
        <FKAnnotatedChart
          data={AAPL_WITH_SMA}
          xKey="date"
          series={[
            { key: 'price',  label: 'AAPL Price', type: 'area', color: '#6366f1' },
            { key: 'sma20',  label: 'SMA 20',     color: '#f59e0b', strokeDash: '4 2' },
            { key: 'sma200', label: 'SMA 200',    color: '#94a3b8', strokeDash: '4 2' },
          ]}
          events={finEvents}
          bands={finBands}
          callouts={finCallouts}
          height={320}
          title="AAPL Technical Analysis"
          subtitle="Price + moving averages + signals + regime bands"
        />
      </DemoVariant>
      <DemoVariant
        title="Stress — all overlay types (5 events + 3 bands + 2 callouts)"
        props={['events (5)', 'bands (3)', 'callouts (2)', 'height={360}']}
      >
        <FKAnnotatedChart
          data={AAPL_WITH_SMA}
          xKey="date"
          series={[
            { key: 'price',  label: 'AAPL',    type: 'area', color: '#6366f1' },
            { key: 'sma200', label: 'SMA 200', color: '#94a3b8', strokeDash: '4 2' },
          ]}
          events={stressEvents}
          bands={stressBands}
          callouts={[
            { date: AAPL_WITH_SMA[20]?.date,  label: 'Fed hike', color: '#f59e0b' },
            { date: AAPL_WITH_SMA[150]?.date, label: 'Earnings', color: '#16a34a', position: 'below' },
          ]}
          height={360}
          title="AAPL — Full Annotation Stress"
          subtitle="All overlay types simultaneously"
        />
      </DemoVariant>
    </div>
  )
}

function FKMultiPanelPage() {
  const panels3 = [
    { id: 'price', height: 200, yLabel: 'Price',
      series: [
        { key: 'price', label: 'AAPL',   color: '#6366f1' },
        { key: 'sma20', label: 'SMA 20', color: '#f59e0b', strokeDash: '4 2' },
      ],
    },
    { id: 'vol', height: 70, yLabel: 'Volume',
      series: [{ key: 'volume', label: 'Volume', color: '#94a3b8', type: 'bar' }],
    },
    { id: 'rsi', height: 90, yLabel: 'RSI', yDomain: [0, 100],
      referenceLines: [{ y: 70, label: 'OB', color: '#dc2626', dash: '3 3' }, { y: 30, label: 'OS', color: '#16a34a', dash: '3 3' }],
      series: [{ key: 'rsi', label: 'RSI (14)', color: '#8b5cf6' }],
    },
  ]
  return (
    <div>
      <PageTitle name="FKMultiPanel" desc="Synchronized multi-panel chart sharing x-axis. Each panel can render lines, areas, or bars." />
      <DemoVariant
        title="Default — single price panel"
        props={['data', 'panels=[{id:"price",series:[{key:"close",type:"area"}]}]']}
      >
        <FKMultiPanel
          data={AAPL_CLOSE.slice(-252).map(r => ({ date: r.date, close: r.close }))}
          xKey="date"
          panels={[{ id: 'price', height: 200, series: [{ key: 'close', label: 'AAPL Close', color: '#6366f1', type: 'area' }] }]}
          title="AAPL Price"
        />
      </DemoVariant>
      <DemoVariant
        title="Finance-realistic — Price + SMA20 + Volume + RSI (3 panels)"
        props={['panels (3)', 'rangeSelector', 'syncId shared across panels']}
      >
        <FKMultiPanel
          data={MP_DATA}
          xKey="date"
          panels={panels3}
          title="AAPL Technical Multi-Panel"
          subtitle="Price + SMA20 + Volume + RSI(14)"
          rangeSelector
          defaultRange="3M"
        />
      </DemoVariant>
      <DemoVariant
        title="Stress — 4 panels (price+SMA + volume + RSI + extra indicator)"
        props={['panels (4)', 'height per panel varies']}
      >
        <FKMultiPanel
          data={MP_DATA}
          xKey="date"
          panels={[
            { id: 'price', height: 180, yLabel: 'Price',
              series: [
                { key: 'price', label: 'AAPL',   color: '#6366f1', type: 'area' },
                { key: 'sma20', label: 'SMA 20', color: '#f59e0b', strokeDash: '4 2' },
              ],
            },
            { id: 'vol',   height: 60, yLabel: 'Vol',   series: [{ key: 'volume', label: 'Volume', color: '#94a3b8', type: 'bar' }] },
            { id: 'rsi',   height: 80, yLabel: 'RSI', yDomain: [0, 100],
              referenceLines: [{ y: 70, color: '#dc2626', dash: '3 3' }, { y: 30, color: '#16a34a', dash: '3 3' }],
              series: [{ key: 'rsi', label: 'RSI (14)', color: '#8b5cf6' }],
            },
            { id: 'sma2',  height: 60, yLabel: 'SMA',  series: [{ key: 'sma20', label: 'SMA 20', color: '#06b6d4' }] },
          ]}
          title="AAPL — 4-Panel Stress"
          subtitle="All panel types simultaneously"
        />
      </DemoVariant>
    </div>
  )
}

function FKProjectionChartPage() {
  return (
    <div>
      <PageTitle name="FKProjectionChart" desc="Historical line plus fan-chart projection bands (p10/p25/p75/p90) or scenario lines." />
      <DemoVariant title="Default — built-in sample data">
        <FKProjectionChart />
      </DemoVariant>
      <DemoVariant
        title="Finance-realistic — Retirement projection: 20Y history + 30Y fan"
        props={['historical (20Y)', 'projection (30Y)', 'valueFormat', 'splitDate']}
      >
        <FKProjectionChart
          historical={PROJ_HIST}
          projection={PROJ_FAN}
          splitDate="2024"
          valueFormat={v => '$' + Math.round(v).toLocaleString()}
          title="Retirement Portfolio Projection"
          subtitle="20-year history + 30-year fan (p10/p25/p75/p90)"
          height={340}
        />
      </DemoVariant>
      <DemoVariant
        title="Stress — Bull / Base / Bear scenario lines"
        props={['scenarios (3)', 'splitDate="2024"', 'no fan bands']}
      >
        <FKProjectionChart
          historical={PROJ_SCENARIOS_HIST}
          scenarios={PROJ_SCENARIOS}
          splitDate="2024"
          valueFormat={v => '$' + Math.round(v).toLocaleString()}
          title="Portfolio Scenario Analysis"
          subtitle="Bull, base and bear case projections"
          height={320}
        />
      </DemoVariant>
    </div>
  )
}

// ── Categorical ───────────────────────────────────────────────────────────────

function FKBarChartPage() {
  return (
    <div>
      <PageTitle name="FKBarChart" desc="Single, grouped, stacked, waterfall, and lollipop bar charts — vertical or horizontal." />
      <DemoVariant title="Default — no props">
        <FKBarChart />
      </DemoVariant>
      <DemoVariant
        title="Finance-realistic — Earnings beat/miss, grouped (10 quarters)"
        props={['mode="grouped"', 'series=[{key:"estimate"},{key:"actual"}]', 'colorRule']}
      >
        <FKBarChart
          data={EARNINGS_DATA}
          mode="grouped"
          labelKey="label"
          series={[
            { key: 'estimate', label: 'Estimate', color: '#94a3b8' },
            { key: 'actual',   label: 'Actual',   color: '#6366f1' },
          ]}
          colorRule={(row, key) => key === 'estimate' ? 'neutral' : row.actual >= row.estimate ? 'gain' : 'loss'}
          yFormat={v => `$${v.toFixed(2)}`}
          height={240}
          title="Quarterly EPS"
          subtitle="Estimate vs Actual, 10 quarters"
        />
      </DemoVariant>
      <DemoVariant
        title="Stress — Lollipop mode, 30 tickers"
        props={['mode="lollipop"', '30 data points', 'colorRule (gain/loss)']}
      >
        <FKBarChart
          data={LOLLIPOP_DATA}
          mode="lollipop"
          labelKey="label"
          valueKey="value"
          colorRule={row => row.value >= 0 ? 'gain' : 'loss'}
          yFormat={v => `${v > 0 ? '+' : ''}${v.toFixed(0)}%`}
          referenceValue={0}
          height={320}
          title="YTD Returns — 30 Stocks"
          subtitle="Lollipop mode"
        />
      </DemoVariant>
    </div>
  )
}

function FKWaterfallPage() {
  const bridgeData = [
    { label: 'Q2 Rev',       value: 850, type: 'start' },
    { label: 'New Contracts',value: 124, type: 'delta' },
    { label: 'Churn',        value: -47, type: 'delta' },
    { label: 'Upsell',       value:  62, type: 'delta' },
    { label: 'FX Impact',    value: -22, type: 'delta' },
    { label: 'Q3 Rev',       value: 967, type: 'end'   },
  ]
  return (
    <div>
      <PageTitle name="FKWaterfall" desc="Bridge chart showing cumulative impact of sequential changes." />
      <DemoVariant title="Default — no props">
        <FKWaterfall />
      </DemoVariant>
      <DemoVariant
        title="Finance-realistic — Q2→Q3 Revenue Bridge"
        props={['data (6 steps)', 'valueFormat']}
      >
        <FKWaterfall
          data={bridgeData}
          title="Q2 → Q3 Revenue Bridge"
          subtitle="$M, quarterly change attribution"
          valueFormat={v => `${v >= 0 ? '+' : ''}$${Math.abs(v).toFixed(0)}M`}
          height={280}
        />
      </DemoVariant>
      <DemoVariant
        title="Stress — 12-step P&L attribution"
        props={['data (12 steps)', 'valueFormat=$K']}
      >
        <FKWaterfall
          data={PNL_DATA}
          title="Annual P&L Attribution"
          subtitle="Start NAV → End NAV, 12-step bridge"
          valueFormat={v => `$${Math.round(v / 1000)}K`}
          yFormat={v => `$${Math.round(v / 1000)}K`}
          height={360}
        />
      </DemoVariant>
    </div>
  )
}

function FKHeatGridPage() {
  return (
    <div>
      <PageTitle name="FKHeatGrid" desc="Grid of colored cells for a value matrix, with diverging or sequential color scales." />
      <DemoVariant title="Default — no props">
        <FKHeatGrid />
      </DemoVariant>
      <DemoVariant
        title="Finance-realistic — Monthly returns calendar (12×5), diverging"
        props={['rowKey="month"', 'colKey="year"', 'valueKey="return_pct"', 'colorScale="diverging"']}
      >
        <FKHeatGrid
          data={MONTHLY_RETURNS}
          rowKey="month"
          colKey="year"
          valueKey="return_pct"
          colorScale="diverging"
          valueFormat={v => `${v >= 0 ? '+' : ''}${v.toFixed(1)}%`}
          title="Monthly Returns Calendar"
          subtitle="Diverging: green = positive, red = negative"
        />
      </DemoVariant>
      <DemoVariant
        title="Stress — 8×8 sector × period heatmap"
        props={['rowKey="sector"', 'colKey="period"', '8×8 = 64 cells']}
      >
        <FKHeatGrid
          data={SECTOR_HEAT}
          rowKey="sector"
          colKey="period"
          valueKey="value"
          colorScale="diverging"
          valueFormat={v => `${v >= 0 ? '+' : ''}${v.toFixed(0)}%`}
          title="Sector × Period Return Heatmap"
          subtitle="8 sectors × 8 quarters"
        />
      </DemoVariant>
    </div>
  )
}

function FKHistogramPage() {
  const varLevel = -2.5
  const varRule  = mid => mid < varLevel ? 'loss' : mid >= 0 ? 'gain' : 'neutral'
  return (
    <div>
      <PageTitle name="FKHistogram" desc="Distribution histogram with optional normal curve overlay and reference lines." />
      <DemoVariant title="Default — no props">
        <FKHistogram />
      </DemoVariant>
      <DemoVariant
        title="Finance-realistic — Daily return distribution with normal overlay"
        props={['data={dailyReturns}', 'overlayNormal={true}', 'referenceLines=[{x:0}]']}
      >
        <FKHistogram
          data={DAILY_RETURNS}
          overlayNormal
          referenceLines={[{ x: 0, color: 'rgba(0,0,0,0.3)', label: '0' }]}
          title="AAPL Daily Return Distribution"
          subtitle="5-year daily returns with normal curve overlay"
          height={240}
        />
      </DemoVariant>
      <DemoVariant
        title="Stress — 500 values, colorRule for VaR tail"
        props={['data (500 values)', 'colorRule (VaR tail < −2.5%)', 'referenceLines x=−2.5']}
      >
        <FKHistogram
          data={RETURNS_500}
          colorRule={varRule}
          referenceLines={[
            { x: varLevel, color: '#dc2626', label: `VaR ${varLevel}%` },
            { x: 0,        color: 'rgba(0,0,0,0.2)' },
          ]}
          title="Return Distribution (n=500)"
          subtitle="VaR tail highlighted in red"
          height={240}
        />
      </DemoVariant>
    </div>
  )
}

function FKRadarChartPage() {
  return (
    <div>
      <PageTitle name="FKRadarChart" desc="Spider / radar chart for multi-dimensional factor profiles." />
      <DemoVariant title="Default — no props">
        <FKRadarChart />
      </DemoVariant>
      <DemoVariant
        title="Finance-realistic — AAPL vs MSFT factor profile (5 axes)"
        props={['axes (5)', 'series (2 stocks)', 'fillOpacity={0.15}']}
      >
        <FKRadarChart
          axes={RADAR_AXES}
          series={RADAR_SERIES_2}
          fillOpacity={0.15}
          title="AAPL vs MSFT Factor Profile"
          subtitle="Value / Quality / Momentum / Growth / Safety"
          height={320}
        />
      </DemoVariant>
      <DemoVariant
        title="Stress — 3 stocks, 8 axes"
        props={['axes (8)', 'series (3 stocks)']}
      >
        <FKRadarChart
          axes={RADAR_AXES_8}
          series={RADAR_SERIES_3}
          fillOpacity={0.12}
          title="AAPL / MSFT / NVDA Factor Comparison"
          subtitle="8-axis factor radar"
          height={340}
        />
      </DemoVariant>
    </div>
  )
}

// ── Relational ────────────────────────────────────────────────────────────────

function FKScatterChartPage() {
  return (
    <div>
      <PageTitle name="FKScatterChart" desc="Canvas-rendered scatter / bubble chart with optional OLS trendline and quadrant overlay." />
      <DemoVariant title="Default — no props">
        <FKScatterChart />
      </DemoVariant>
      <DemoVariant
        title="Finance-realistic — Vol vs Return, size=mktcap, color=sector, trendline"
        props={['xKey="vol"', 'yKey="ret"', 'sizeKey="mktcap"', 'colorKey="sector"', 'trendLine={true}', 'quadrants={true}']}
      >
        <FKScatterChart
          data={SCATTER_200.slice(0, 80)}
          xKey="vol"
          yKey="ret"
          sizeKey="mktcap"
          colorKey="sector"
          xLabel="Volatility (%)"
          yLabel="Return (%)"
          xFormat={v => `${v.toFixed(0)}%`}
          yFormat={v => `${v >= 0 ? '+' : ''}${v.toFixed(0)}%`}
          trendLine
          quadrants
          height={320}
          title="Volatility vs Return — S&P 500 (80 stocks)"
          subtitle="Bubble size = market cap, color = sector"
        />
      </DemoVariant>
      <DemoVariant
        title="Stress — 200 dots"
        props={['data (200 points)', 'trendLine', 'referenceLines']}
      >
        <FKScatterChart
          data={SCATTER_200}
          xKey="vol"
          yKey="ret"
          colorKey="sector"
          xLabel="Volatility (%)"
          yLabel="Return (%)"
          xFormat={v => `${v.toFixed(0)}%`}
          yFormat={v => `${v >= 0 ? '+' : ''}${v.toFixed(0)}%`}
          trendLine
          referenceLines={[{ y: 0, color: 'rgba(0,0,0,0.15)' }]}
          height={320}
          title="Volatility vs Return (200 stocks)"
          subtitle="Full universe scatter with trendline"
        />
      </DemoVariant>
    </div>
  )
}

function FKSankeyChartPage() {
  return (
    <div>
      <PageTitle name="FKSankeyChart" desc="Flow diagram showing proportional volume through a multi-stage process." />
      <DemoVariant title="Default — no props">
        <FKSankeyChart />
      </DemoVariant>
      <DemoVariant
        title="Finance-realistic — Revenue decomposition (product→profit layers)"
        props={['nodes (9)', 'flows (8)', 'valueFormat']}
      >
        <FKSankeyChart
          nodes={SANKEY_REVENUE_NODES}
          flows={SANKEY_REVENUE_FLOWS}
          valueFormat={v => `$${v}B`}
          title="Revenue Decomposition"
          subtitle="Product lines → gross profit → EBIT → net income"
          height={380}
        />
      </DemoVariant>
      <DemoVariant
        title="Stress — 4-column fund flow diagram (10 nodes, 12 flows)"
        props={['nodes (10)', 'flows (12)', '4 columns']}
      >
        <FKSankeyChart
          nodes={SANKEY_FUND_NODES}
          flows={SANKEY_FUND_FLOWS}
          valueFormat={v => `$${v}M`}
          title="Fund Flow Diagram"
          subtitle="LPs → Funds → Asset Classes → Returns"
          height={420}
        />
      </DemoVariant>
    </div>
  )
}

function FKPartChartPage() {
  return (
    <div>
      <PageTitle name="FKPartChart" desc="Part-of-whole chart in donut, treemap, or bars mode." />
      <DemoVariant title="Default — no props">
        <FKPartChart />
      </DemoVariant>
      <DemoVariant
        title="Finance-realistic — Portfolio donut with center label"
        props={['mode="donut"', 'innerLabel="$221.7K"', 'innerSub="NAV"']}
      >
        <FKPartChart
          data={PORTFOLIO_DONUT}
          mode="donut"
          innerLabel="$221.7K"
          innerSub="Total NAV"
          title="Portfolio Allocation"
          subtitle="Asset class breakdown"
        />
      </DemoVariant>
      <DemoVariant
        title="Stress — Treemap mode with return-based coloring"
        props={['mode="treemap"', 'colorBy="colorKey"', 'colorKey="return"']}
      >
        <FKPartChart
          data={TREEMAP_DATA}
          valueKey="value"
          labelKey="label"
          colorKey="return"
          mode="treemap"
          colorBy="colorKey"
          height={280}
          title="Holdings Treemap"
          subtitle="Size = position value, color = return"
        />
      </DemoVariant>
    </div>
  )
}

// ── Range & Gauge ─────────────────────────────────────────────────────────────

function FKRangeChartPage() {
  return (
    <div>
      <PageTitle name="FKRangeChart" desc="52-week range bars showing current price vs min/max/target positions." />
      <DemoVariant title="Default — no props">
        <FKRangeChart />
      </DemoVariant>
      <DemoVariant
        title="Finance-realistic — 52W range for 8 holdings with analyst targets"
        props={['data (8 rows)', 'targetKey="target"', 'format', 'showValues']}
      >
        <FKRangeChart
          data={RANGE_52W}
          targetKey="target"
          format={v => `$${v.toFixed(0)}`}
          showValues
          title="52-Week Price Range"
          subtitle="Current price (dot) vs analyst target (diamond)"
        />
      </DemoVariant>
      <DemoVariant
        title="Stress — Mandate utilization with colorRule (warn when near limit)"
        props={['colorRule (gain/warn/loss)', 'format=pct', 'targetKey']}
      >
        <FKRangeChart
          data={MANDATE_DATA}
          targetKey="target"
          format={v => `${v.toFixed(0)}%`}
          showValues
          colorRule={row => {
            const pct = (row.value - row.min) / (row.max - row.min)
            return pct > 0.85 ? 'loss' : pct > 0.65 ? 'warn' : 'gain'
          }}
          title="Mandate Utilization"
          subtitle="Allocation vs limit — color by utilization level"
        />
      </DemoVariant>
    </div>
  )
}

function FKBulletChartPage() {
  return (
    <div>
      <PageTitle name="FKBulletChart" desc="Bullet chart comparing actual vs target values with a qualitative range background." />
      <DemoVariant title="Default — no props">
        <FKBulletChart />
      </DemoVariant>
      <DemoVariant
        title="Finance-realistic — Price vs analyst target for 5 stocks"
        props={['data (5 rows)', 'valueFormat={v => `$${v.toFixed(0)}`}']}
      >
        <FKBulletChart
          data={BULLET_STOCKS}
          valueFormat={v => `$${v.toFixed(0)}`}
          title="Price vs Analyst Target"
          subtitle="Current price relative to 12-month consensus target"
        />
      </DemoVariant>
      <DemoVariant
        title="Stress — EPS/Revenue vs guidance (mixed scales)"
        props={['data (4 rows)', 'mixed value scales']}
      >
        <FKBulletChart
          data={BULLET_EPS}
          valueFormat={v => v > 10 ? `$${v.toFixed(1)}B` : `$${v.toFixed(2)}`}
          title="Q3 Actuals vs Guidance"
          subtitle="EPS and revenue vs analyst guidance"
        />
      </DemoVariant>
    </div>
  )
}

// ── Tabular ───────────────────────────────────────────────────────────────────

function FKTablePage() {
  return (
    <div>
      <PageTitle name="FKTable" desc="Sortable data table with sparklines, color rules, and pivot mode." />
      <DemoVariant title="Default — no props">
        <FKTable />
      </DemoVariant>
      <DemoVariant
        title="Finance-realistic — Holdings table with sparklines"
        props={['columns (5)', 'rows (10)', 'sparkKey="spark"', 'defaultSort="value"']}
      >
        <FKTable
          columns={TABLE_COLUMNS}
          rows={HOLDINGS_DATA}
          sparkKey="spark"
          defaultSort="value"
          stickyHeader
          title="Portfolio Holdings"
          subtitle="Sortable by any column, sparklines in last column"
        />
      </DemoVariant>
      <DemoVariant
        title="Stress — Pivot mode: years × months monthly returns"
        props={['pivotRow="year"', 'pivotCol="month"', 'pivotValue="return"']}
      >
        <FKTable
          rows={PIVOT_DATA}
          pivotRow="year"
          pivotCol="month"
          pivotValue="return"
          title="Monthly Returns Pivot"
          subtitle="Years as rows, months as columns"
        />
      </DemoVariant>
    </div>
  )
}

function FKRankedListPage() {
  return (
    <div>
      <PageTitle name="FKRankedList" desc="Ranked items list with sparklines, delta badges, and color-coded rank bars." />
      <DemoVariant title="Default — no props">
        <FKRankedList />
      </DemoVariant>
      <DemoVariant
        title="Finance-realistic — Top movers with sparklines"
        props={['data (8 rows)', 'sparkKey', 'deltaKey']}
      >
        <FKRankedList
          data={TOP_MOVERS}
          title="Top Movers"
          subtitle="Portfolio holdings ranked by YTD return"
        />
      </DemoVariant>
      <DemoVariant
        title="Stress — 20 items"
        props={['data (20 rows)', 'sparkKey', 'deltaKey']}
      >
        <FKRankedList
          data={MOVERS_20}
          title="Full Universe Movers (20 stocks)"
          subtitle="Ranked by YTD return"
        />
      </DemoVariant>
    </div>
  )
}

function FKMetricGridPage() {
  return (
    <div>
      <PageTitle name="FKMetricGrid" desc="KPI card grid with delta indicators, sparklines, and colored accent borders." />
      <DemoVariant title="Default — no props">
        <FKMetricGrid />
      </DemoVariant>
      <DemoVariant
        title="Finance-realistic — Portfolio summary (4 KPIs)"
        props={['cards (4)', 'cols={4}', 'spark on value card']}
      >
        <FKMetricGrid cards={PORTFOLIO_METRICS} cols={4} />
      </DemoVariant>
      <DemoVariant
        title="Stress — 8 cards, cols=4, all with sparklines + delta"
        props={['cards (8)', 'cols={4}', 'all cards with spark+delta']}
      >
        <FKMetricGrid cards={METRICS_STRESS} cols={4} />
      </DemoVariant>
    </div>
  )
}

// ── Events ────────────────────────────────────────────────────────────────────

function FKTimelinePage() {
  return (
    <div>
      <PageTitle name="FKTimeline" desc="Horizontal event timeline with swim lanes, point events, and duration bars." />
      <DemoVariant title="Default — built-in sample data">
        <FKTimeline />
      </DemoVariant>
      <DemoVariant
        title="Finance-realistic — Earnings + dividends + macro + lock-up windows"
        props={['events (10)', 'colorMap', '4 swim lanes']}
      >
        <FKTimeline
          events={TIMELINE_EVENTS}
          colorMap={TIMELINE_COLORMAP}
          title="Corporate Event Calendar"
          subtitle="Earnings, dividends, Fed meetings, and lock-up windows"
        />
      </DemoVariant>
      <DemoVariant
        title="Stress — Duration bars + point events combined (11 events)"
        props={['events (8 point + 3 duration)', 'mixed types', '5 swim lanes']}
      >
        <FKTimeline
          events={TIMELINE_STRESS}
          colorMap={TIMELINE_COLORMAP}
          title="Fiscal Calendar — Mixed Events"
          subtitle="Point events (earnings) and duration bars (fiscal periods)"
        />
      </DemoVariant>
    </div>
  )
}

// ── Primitives ────────────────────────────────────────────────────────────────

function PrimitivesPage() {
  const sparkPos  = [40, 43, 41, 46, 44, 49, 48, 53, 55, 58, 56, 62]
  const sparkNeg  = [80, 76, 78, 72, 74, 68, 70, 64, 66, 60, 62, 56]
  const sparkFlat = [50, 51, 49, 52, 50, 51, 50, 52, 49, 51, 50, 51]
  const [range, setRange] = useState('3M')

  return (
    <div>
      <PageTitle name="Primitives" desc="FKSparkline, FKDelta, FKBadge, FKStatStrip, FKTooltip, FKRangeSelector — foundational display atoms." />

      <DemoVariant title="FKSparkline — positive, negative, flat, wide" props={['data', 'width', 'height', 'showArea']}>
        <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap', padding: '16px 0', alignItems: 'flex-end' }}>
          {[
            { label: 'positive', data: sparkPos },
            { label: 'negative', data: sparkNeg },
            { label: 'flat',     data: sparkFlat },
          ].map(({ label, data }) => (
            <div key={label} style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              <span style={{ fontSize: 10, color: 'var(--color-text-tertiary)', fontFamily: 'var(--font-mono)' }}>{label}</span>
              <FKSparkline data={data} width={80} height={32} showArea />
            </div>
          ))}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <span style={{ fontSize: 10, color: 'var(--color-text-tertiary)', fontFamily: 'var(--font-mono)' }}>wide (no area)</span>
            <FKSparkline data={sparkPos} width={160} height={40} />
          </div>
        </div>
      </DemoVariant>

      <DemoVariant title="FKDelta — various values" props={['value', 'decimals', 'suffix']}>
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', padding: '12px 0', alignItems: 'center' }}>
          <FKDelta value={18.7}  decimals={1} />
          <FKDelta value={-4.2}  decimals={2} />
          <FKDelta value={0.55}  decimals={2} />
          <FKDelta value={-0.01} decimals={2} />
          <FKDelta value={142.5} decimals={0} suffix="bps" />
        </div>
      </DemoVariant>

      <DemoVariant title="FKBadge — all variants" props={['variant']}>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', padding: '12px 0', alignItems: 'center' }}>
          <FKBadge variant="gain">gain</FKBadge>
          <FKBadge variant="loss">loss</FKBadge>
          <FKBadge variant="warn">warn</FKBadge>
          <FKBadge variant="neutral">neutral</FKBadge>
          <FKBadge variant="info">info</FKBadge>
          <FKBadge variant="gain">+18.7%</FKBadge>
          <FKBadge variant="loss">−4.2%</FKBadge>
        </div>
      </DemoVariant>

      <DemoVariant title="FKStatStrip — horizontal key-value bar" props={['stats (array of {label, value, color?})']}>
        <FKStatStrip stats={[
          { label: 'Mean',       value: '+0.34%',  color: '#16a34a' },
          { label: 'Std Dev',    value: '1.42%' },
          { label: '% Positive', value: '53.8%' },
          { label: 'Sharpe',     value: '1.84' },
          { label: 'Max DD',     value: '−21.3%', color: '#dc2626' },
          { label: 'N',          value: '1,260' },
        ]} />
      </DemoVariant>

      <DemoVariant title="FKRangeSelector — period tab bars" props={['options', 'value', 'onChange']}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16, padding: '12px 0' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <span style={{ fontSize: 11, color: 'var(--color-text-tertiary)', fontFamily: 'var(--font-mono)', width: 120 }}>Standard options:</span>
            <FKRangeSelector
              options={['1M','3M','6M','1Y','3Y','5Y','ALL']}
              value={range}
              onChange={setRange}
            />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <span style={{ fontSize: 11, color: 'var(--color-text-tertiary)', fontFamily: 'var(--font-mono)', width: 120 }}>Custom options:</span>
            <FKRangeSelector
              options={['YTD','1Y','2Y','Since Inception']}
              value="1Y"
              onChange={() => {}}
            />
          </div>
        </div>
      </DemoVariant>
    </div>
  )
}

// =============================================================================
// NAVIGATION STRUCTURE
// =============================================================================

const NAV_STRUCTURE = [
  { id: 'overview', label: 'Overview' },
  { section: 'Time Series' },
  { id: 'FKLineChart',       label: 'FKLineChart',       indent: true },
  { id: 'FKAreaChart',       label: 'FKAreaChart',       indent: true },
  { id: 'FKBandChart',       label: 'FKBandChart',       indent: true },
  { id: 'FKCandleChart',     label: 'FKCandleChart',     indent: true },
  { id: 'FKAnnotatedChart',  label: 'FKAnnotatedChart',  indent: true },
  { id: 'FKMultiPanel',      label: 'FKMultiPanel',      indent: true },
  { id: 'FKProjectionChart', label: 'FKProjectionChart', indent: true },
  { section: 'Categorical' },
  { id: 'FKBarChart',        label: 'FKBarChart',        indent: true },
  { id: 'FKWaterfall',       label: 'FKWaterfall',       indent: true },
  { id: 'FKHeatGrid',        label: 'FKHeatGrid',        indent: true },
  { id: 'FKHistogram',       label: 'FKHistogram',       indent: true },
  { id: 'FKRadarChart',      label: 'FKRadarChart',      indent: true },
  { section: 'Relational' },
  { id: 'FKScatterChart',    label: 'FKScatterChart',    indent: true },
  { id: 'FKSankeyChart',     label: 'FKSankeyChart',     indent: true },
  { id: 'FKPartChart',       label: 'FKPartChart',       indent: true },
  { section: 'Range & Gauge' },
  { id: 'FKRangeChart',      label: 'FKRangeChart',      indent: true },
  { id: 'FKBulletChart',     label: 'FKBulletChart',     indent: true },
  { section: 'Tabular' },
  { id: 'FKTable',           label: 'FKTable',           indent: true },
  { id: 'FKRankedList',      label: 'FKRankedList',      indent: true },
  { id: 'FKMetricGrid',      label: 'FKMetricGrid',      indent: true },
  { section: 'Events' },
  { id: 'FKTimeline',        label: 'FKTimeline',        indent: true },
  { section: 'Primitives' },
  { id: 'primitives',        label: 'FKSparkline + more', indent: true },
]

const PAGE_COMPONENTS = {
  overview:          OverviewPage,
  FKLineChart:       FKLineChartPage,
  FKAreaChart:       FKAreaChartPage,
  FKBandChart:       FKBandChartPage,
  FKCandleChart:     FKCandleChartPage,
  FKAnnotatedChart:  FKAnnotatedChartPage,
  FKMultiPanel:      FKMultiPanelPage,
  FKProjectionChart: FKProjectionChartPage,
  FKBarChart:        FKBarChartPage,
  FKWaterfall:       FKWaterfallPage,
  FKHeatGrid:        FKHeatGridPage,
  FKHistogram:       FKHistogramPage,
  FKRadarChart:      FKRadarChartPage,
  FKScatterChart:    FKScatterChartPage,
  FKSankeyChart:     FKSankeyChartPage,
  FKPartChart:       FKPartChartPage,
  FKRangeChart:      FKRangeChartPage,
  FKBulletChart:     FKBulletChartPage,
  FKTable:           FKTablePage,
  FKRankedList:      FKRankedListPage,
  FKMetricGrid:      FKMetricGridPage,
  FKTimeline:        FKTimelinePage,
  primitives:        PrimitivesPage,
}

// =============================================================================
// MAIN SHOWCASE
// =============================================================================

export function Showcase() {
  const [page, setPage] = useState('overview')
  const [dark, setDark] = useState(() => {
    try { return window.matchMedia('(prefers-color-scheme: dark)').matches } catch { return false }
  })

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    document.documentElement.classList.toggle('light', !dark)
  }, [dark])

  const PageComponent = PAGE_COMPONENTS[page] || OverviewPage

  return (
    <div style={{
      display:       'flex',
      height:        '100vh',
      fontFamily:    'var(--font-sans)',
      background:    'var(--color-background-primary)',
      color:         'var(--color-text-primary)',
      overflow:      'hidden',
    }}>
      {/* ── Left Navigation ──────────────────────────────────────────────────── */}
      <nav style={{
        width:         200,
        flexShrink:    0,
        overflowY:     'auto',
        background:    'var(--color-background-primary)',
        borderRight:   '0.5px solid var(--color-border-tertiary)',
        display:       'flex',
        flexDirection: 'column',
        paddingTop:    8,
        paddingBottom: 24,
      }}>
        {/* Logo */}
        <div style={{
          padding:      '12px 20px 16px',
          borderBottom: '0.5px solid var(--color-border-tertiary)',
          marginBottom: 8,
        }}>
          <div style={{ fontSize: 13, fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--color-text-primary)', letterSpacing: '-0.02em' }}>
            FINKIT
          </div>
          <div style={{ fontSize: 10, color: 'var(--color-text-tertiary)', marginTop: 2 }}>
            Component Explorer
          </div>
        </div>

        {NAV_STRUCTURE.map((item, i) => {
          if (item.section) return <NavSection key={`sec-${i}`} title={item.section} />
          return (
            <NavLink
              key={item.id}
              label={item.label}
              active={page === item.id}
              indent={item.indent}
              onClick={() => setPage(item.id)}
            />
          )
        })}
      </nav>

      {/* ── Main Content ─────────────────────────────────────────────────────── */}
      <main style={{ flex: 1, overflowY: 'auto', background: 'var(--color-background-primary)', display: 'flex', flexDirection: 'column' }}>
        {/* Sticky header */}
        <div style={{
          display:        'flex',
          alignItems:     'center',
          justifyContent: 'space-between',
          padding:        '0 24px',
          height:         48,
          borderBottom:   '0.5px solid var(--color-border-tertiary)',
          background:     'var(--color-background-primary)',
          flexShrink:     0,
          position:       'sticky',
          top:             0,
          zIndex:          10,
        }}>
          <span style={{ fontSize: 12, fontWeight: 500, fontFamily: 'var(--font-mono)', color: 'var(--color-text-secondary)', letterSpacing: '0.04em' }}>
            FINKIT · Component Explorer
          </span>
          <button
            onClick={() => setDark(d => !d)}
            style={{
              display:     'flex',
              alignItems:  'center',
              gap:          6,
              padding:     '6px 12px',
              background:  'var(--color-background-secondary)',
              border:      '0.5px solid var(--color-border-secondary)',
              borderRadius: 8,
              cursor:      'pointer',
              fontSize:    11,
              fontFamily:  'var(--font-mono)',
              color:       'var(--color-text-secondary)',
            }}
          >
            {dark ? '☀ Light' : '☾ Dark'}
          </button>
        </div>

        {/* Page */}
        <div style={{ flex: 1, padding: '32px 32px 64px', maxWidth: 1100, width: '100%', margin: '0 auto', boxSizing: 'border-box' }}>
          <PageComponent />
        </div>
      </main>
    </div>
  )
}

export default Showcase
