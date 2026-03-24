import React, { useState, useMemo } from 'react'
import {
  ResponsiveContainer, ComposedChart, Line, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, ReferenceArea, Customized,
} from 'recharts'
import { FKCard, FKCardHeader } from './FKCard.jsx'
import { FKRangeSelector } from './FKRangeSelector.jsx'
import { FKTooltip } from './FKTooltip.jsx'
import { color, axisProps, gridProps } from './tokens.js'

// ─── Sample data ──────────────────────────────────────────────────────────────
function makeSampleData(n = 60) {
  let price = 380, sma10 = 380, sma200 = 375
  const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
  return Array.from({ length: n }, (_, i) => {
    price  = +(price  + (Math.random() - 0.47) * 8).toFixed(2)
    sma10  = +(sma10  * 0.9  + price * 0.1).toFixed(2)
    sma200 = +(sma200 * 0.99 + price * 0.01).toFixed(2)
    const d = new Date(2024, Math.floor(i / 5) % 12, (i % 5) * 5 + 1)
    return { date: `${MONTHS[d.getMonth()]} ${d.getDate()}, '24`, price, sma10, sma200 }
  })
}
const SAMPLE_DATA   = makeSampleData()
const SAMPLE_SERIES = [
  { key: 'price',  label: 'QQQ Price', color: '#6366f1' },
  { key: 'sma10',  label: 'SMA 10',    color: '#f59e0b', strokeDash: '4 2' },
  { key: 'sma200', label: 'SMA 200',   color: '#94a3b8', strokeDash: '4 2' },
]
const SAMPLE_EVENTS = [
  { date: SAMPLE_DATA[20]?.date, type: 'buy',  label: 'SMA Crossover Buy',  value: 'SMA10 crossed above SMA200' },
  { date: SAMPLE_DATA[45]?.date, type: 'sell', label: 'SMA Crossover Sell', value: 'SMA10 crossed below SMA200' },
]
const SAMPLE_BANDS = [
  { from: SAMPLE_DATA[30]?.date, to: SAMPLE_DATA[42]?.date, color: 'rgba(220,38,38,0.08)', label: 'Bear regime' },
]
const SAMPLE_CALLOUTS = [
  { date: SAMPLE_DATA[15]?.date, label: 'Fed hikes 25bps', color: '#f59e0b' },
  { date: SAMPLE_DATA[50]?.date, label: 'Earnings miss',   color: '#dc2626', position: 'below' },
]

const DEFAULT_COLOR_MAP = { buy: '#16a34a', sell: '#dc2626' }
const DEFAULT_SHAPE_MAP = { buy: 'triangle-up', sell: 'triangle-down' }

// ─── Event marker shapes ──────────────────────────────────────────────────────
function MarkerShape({ shape, cx, cy, r = 6, fill }) {
  switch (shape) {
    case 'triangle-up':
      return <polygon points={`${cx},${cy - r} ${cx - r},${cy + r * 0.6} ${cx + r},${cy + r * 0.6}`} fill={fill} />
    case 'triangle-down':
      return <polygon points={`${cx},${cy + r} ${cx - r},${cy - r * 0.6} ${cx + r},${cy - r * 0.6}`} fill={fill} />
    case 'diamond':
      return <polygon points={`${cx},${cy - r} ${cx + r},${cy} ${cx},${cy + r} ${cx - r},${cy}`} fill={fill} />
    default: // circle
      return <circle cx={cx} cy={cy} r={r} fill={fill} />
  }
}

// ─── Custom overlay for events + callouts ─────────────────────────────────────
function AnnotationLayer({ xAxisMap, yAxisMap, data, events, callouts, colorMap, shapeMap, xKey, series }) {
  if (!xAxisMap || !yAxisMap) return null
  const xAxis = Object.values(xAxisMap)[0]
  const yAxis = Object.values(yAxisMap)[0]
  if (!xAxis?.scale || !yAxis?.scale) return null

  const xLabels    = data.map(r => r[xKey || 'date'])
  const primaryKey = series?.[0]?.key

  // Categorical XAxis: pass the string value directly, not the index
  function getX(dateLabel) {
    const x = xAxis.scale(dateLabel)
    if (x == null || isNaN(x)) return null
    return x + (xAxis.scale.bandwidth?.() || 0) / 2
  }

  // Get the pixel-y of the primary series value at a given date
  function getDataY(dateLabel) {
    if (!primaryKey) return null
    const idx = xLabels.indexOf(dateLabel)
    if (idx < 0) return null
    const val = data[idx]?.[primaryKey]
    return val != null ? yAxis.scale(val) : null
  }

  const yDomain = yAxis.scale.domain()
  const yTop    = yAxis.scale(yDomain[1])   // small pixel y = top of plot area
  const yBottom = yAxis.scale(yDomain[0])   // large pixel y = bottom of plot area

  const markers = (events || []).map((ev, i) => {
    const x = getX(ev.date)
    if (x == null) return null
    const c     = (colorMap || DEFAULT_COLOR_MAP)[ev.type] || color.series[0]
    const shape = (shapeMap || DEFAULT_SHAPE_MAP)[ev.type] || 'circle'
    // up-shapes (buy) sit just above the bottom edge; down-shapes (sell) just below the top
    const isUpShape = shape === 'triangle-up' || shape === 'circle'
    const y = isUpShape ? yBottom - 10 : yTop + 10
    return { ev, x, y, c, shape, key: `ev-${i}` }
  }).filter(Boolean)

  const calloutEls = (callouts || []).map((ca, i) => {
    const x = getX(ca.date)
    if (x == null) return null
    const c      = ca.color || color.series[0]
    const above  = ca.position !== 'below'
    // Box center: near top/bottom of the plot area with a small margin
    const boxCenterY = above ? yTop + 14 : yBottom - 14
    // Leader line ends at the actual data value, falling back to the plot edge
    const leaderEndY = getDataY(ca.date) ?? (above ? yTop : yBottom)
    return { ca, x, boxCenterY, leaderEndY, c, above, key: `ca-${i}` }
  }).filter(Boolean)

  return (
    <g>
      {/* Event markers */}
      {markers.map(({ ev, x, y, c, shape, key }) => (
        <MarkerShape key={key} shape={shape} cx={x} cy={y} r={6} fill={c} />
      ))}

      {/* Callout boxes */}
      {calloutEls.map(({ ca, x, boxCenterY, leaderEndY, c, above, key }) => {
        const labelW    = ca.label.length * 6.5 + 16
        const boxH      = 20
        const boxX      = x - labelW / 2
        const boxY      = boxCenterY - boxH / 2
        const lineStart = above ? boxY + boxH : boxY   // leader starts at bottom/top of box
        return (
          <g key={key}>
            {/* Leader line from box edge to the data value */}
            <line
              x1={x} y1={lineStart}
              x2={x} y2={leaderEndY}
              stroke={c} strokeWidth={0.5} strokeDasharray="3 2" opacity={0.7}
            />
            {/* Dot at data value */}
            <circle cx={x} cy={leaderEndY} r={3} fill={c} />
            {/* Label box */}
            <rect x={boxX} y={boxY} width={labelW} height={boxH} rx={4}
              fill="var(--color-background-primary)" stroke={c} strokeWidth={0.5} />
            <text x={x} y={boxY + 13} textAnchor="middle"
              fontSize={12} fontFamily="var(--font-sans)" fill={c} fontWeight={500}>
              {ca.label}
            </text>
          </g>
        )
      })}
    </g>
  )
}

// ─── Legend row ───────────────────────────────────────────────────────────────
function AnnotationLegend({ series, events, bands, colorMap, shapeMap }) {
  return (
    <div className="flex flex-wrap gap-x-4 gap-y-1" style={{ padding: '6px 20px 12px' }}>
      {series?.map((s, i) => {
        const c = s.color || color.series[i % color.series.length]
        return (
          <div key={s.key} className="flex items-center gap-1.5">
            <div style={{ width: 20, height: 2, background: c, borderRadius: 1, borderTop: s.strokeDash ? `1px dashed ${c}` : undefined }} />
            <span style={{ fontSize: 13, fontFamily: 'var(--font-sans)', color: 'var(--color-text-secondary)' }}>{s.label || s.key}</span>
          </div>
        )
      })}
      {[...new Set((events || []).map(e => e.type))].map(type => {
        const c = (colorMap || DEFAULT_COLOR_MAP)[type] || color.series[0]
        return (
          <div key={type} className="flex items-center gap-1.5">
            <svg width={12} height={12} style={{ flexShrink: 0 }}>
              <MarkerShape shape={(shapeMap || DEFAULT_SHAPE_MAP)[type] || 'circle'} cx={6} cy={6} r={5} fill={c} />
            </svg>
            <span style={{ fontSize: 13, fontFamily: 'var(--font-sans)', color: 'var(--color-text-secondary)', textTransform: 'capitalize' }}>{type}</span>
          </div>
        )
      })}
      {(bands || []).map((b, i) => (
        <div key={i} className="flex items-center gap-1.5">
          <div style={{ width: 12, height: 10, background: b.color || 'rgba(99,102,241,0.2)', borderRadius: 2 }} />
          <span style={{ fontSize: 13, fontFamily: 'var(--font-sans)', color: 'var(--color-text-secondary)' }}>{b.label}</span>
        </div>
      ))}
    </div>
  )
}

// ─── FKAnnotatedChart ─────────────────────────────────────────────────────────
export function FKAnnotatedChart({
  data,
  xKey          = 'date',
  series,
  events,
  bands,
  callouts,
  colorMap,
  shapeMap,
  height        = 320,
  rangeSelector = true,
  defaultRange  = '1Y',
  title,
  subtitle,
  valueFormat,
}) {
  const resolvedData   = data   || SAMPLE_DATA
  const resolvedSeries = series || SAMPLE_SERIES
  const resolvedEvents = events !== undefined ? events : SAMPLE_EVENTS
  const resolvedBands  = bands  !== undefined ? bands  : SAMPLE_BANDS
  const resolvedCallouts = callouts !== undefined ? callouts : SAMPLE_CALLOUTS

  const rangeOptions = ['1M', '3M', '6M', '1Y', 'ALL']
  const [range, setRange] = useState(defaultRange)

  const [hoveredMarker, setHoveredMarker] = useState(null)

  const actions = rangeSelector
    ? <FKRangeSelector options={rangeOptions} value={range} onChange={setRange} />
    : null

  const curveType = 'linear'

  // Tight y-axis domain: rounded to a nice step so ticks are clean integers
  const yDomain = useMemo(() => {
    const vals = resolvedSeries.flatMap(s => resolvedData.map(d => d[s.key])).filter(v => v != null)
    if (!vals.length) return ['auto', 'auto']
    const lo   = Math.min(...vals)
    const hi   = Math.max(...vals)
    const pad  = (hi - lo) * 0.05 || Math.abs(lo) * 0.02 || 1
    const step = Math.pow(10, Math.floor(Math.log10((hi - lo) || 1)))
    return [
      Math.floor((lo - pad) / step) * step,
      Math.ceil((hi + pad)  / step) * step,
    ]
  }, [resolvedData, resolvedSeries])

  return (
    <FKCard>
      <FKCardHeader title={title} subtitle={subtitle} actions={actions} />
      <div style={{ height, padding: '12px 8px 4px 8px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={resolvedData} margin={{ top: 20, right: 4, left: 8, bottom: 0 }}>
            {/* Gradient fills */}
            <defs>
              {resolvedSeries.filter(s => s.type === 'area').map((s, i) => {
                const c = s.color || color.series[i % color.series.length]
                return (
                  <linearGradient key={s.key} id={`ann-grad-${s.key}`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%"   stopColor={c} stopOpacity={0.2} />
                    <stop offset="100%" stopColor={c} stopOpacity={0} />
                  </linearGradient>
                )
              })}
            </defs>

            <CartesianGrid {...gridProps} />
            <XAxis dataKey={xKey} {...axisProps} minTickGap={40} maxRotation={0} padding={{ left: 16, right: 8 }} />
            <YAxis {...axisProps} orientation="right" width={52} tickFormatter={valueFormat} domain={yDomain} tickCount={5} />

            <Tooltip
              content={<FKTooltip valueFormat={valueFormat} />}
              cursor={{ stroke: 'var(--color-border-secondary)', strokeWidth: 1 }}
            />

            {/* Background bands (ReferenceArea) */}
            {(resolvedBands || []).map((b, i) => (
              <ReferenceArea
                key={i}
                x1={b.from}
                x2={b.to}
                fill={b.color || 'rgba(99,102,241,0.08)'}
                stroke="none"
                ifOverflow="extendDomain"
              />
            ))}

            {/* Series */}
            {resolvedSeries.map((s, i) => {
              const c = s.color || color.series[i % color.series.length]
              if (s.type === 'area') {
                return (
                  <Area key={s.key} type={curveType} dataKey={s.key} name={s.label || s.key}
                    stroke={c} strokeWidth={1.5}
                    strokeDasharray={s.strokeDash}
                    fill={`url(#ann-grad-${s.key})`}
                    isAnimationActive={false} />
                )
              }
              return (
                <Line key={s.key} type={curveType} dataKey={s.key} name={s.label || s.key}
                  stroke={c} strokeWidth={1.5}
                  strokeDasharray={s.strokeDash}
                  dot={false} isAnimationActive={false} />
              )
            })}

            {/* Annotation overlay (events + callouts) */}
            <Customized
              component={({ xAxisMap, yAxisMap }) => (
                <AnnotationLayer
                  xAxisMap={xAxisMap}
                  yAxisMap={yAxisMap}
                  data={resolvedData}
                  events={resolvedEvents}
                  callouts={resolvedCallouts}
                  colorMap={colorMap || DEFAULT_COLOR_MAP}
                  shapeMap={shapeMap || DEFAULT_SHAPE_MAP}
                  xKey={xKey}
                  series={resolvedSeries}
                />
              )}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      <AnnotationLegend
        series={resolvedSeries}
        events={resolvedEvents}
        bands={resolvedBands}
        colorMap={colorMap || DEFAULT_COLOR_MAP}
        shapeMap={shapeMap || DEFAULT_SHAPE_MAP}
      />
    </FKCard>
  )
}
