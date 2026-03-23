import React, { useState } from 'react'
import {
  ResponsiveContainer, ComposedChart, Line, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine,
} from 'recharts'
import { FKCard, FKCardHeader } from './FKCard.jsx'
import { FKRangeSelector, FKStatStrip, FKBadge } from './FKSparkline.jsx'
import { color, axisProps, gridProps, tooltipStyle } from './tokens.js'

// ─── Sample data ─────────────────────────────────────────────────────────────
function makeSampleData() {
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
  let v = 100, b = 100
  return Array.from({ length: 24 }, (_, i) => {
    v = v + (Math.random() - 0.45) * 8
    b = b + (Math.random() - 0.47) * 5
    return {
      date:  `${months[i % 12]} '${String(22 + Math.floor(i / 12)).padStart(2, '0')}`,
      value: parseFloat(v.toFixed(2)),
      bench: parseFloat(b.toFixed(2)),
    }
  })
}
const SAMPLE_DATA   = makeSampleData()
const SAMPLE_SERIES = [
  { key: 'value', label: 'Portfolio' },
  { key: 'bench', label: 'Benchmark', dashed: true },
]

// ─── Custom tooltip ───────────────────────────────────────────────────────────
function CustomTooltip({ active, payload, label, yFormat, seriesMap }) {
  if (!active || !payload?.length) return null
  return (
    <div style={tooltipStyle}>
      <div style={{ color: 'var(--color-text-secondary)', marginBottom: 6, fontSize: 11 }}>
        {label}
      </div>
      {payload.map((p, i) => (
        <div key={i} className="flex items-center gap-2" style={{ color: p.color }}>
          <span style={{ fontSize: 11 }}>{seriesMap?.[p.dataKey] || p.dataKey}</span>
          <span style={{ fontWeight: 500, marginLeft: 'auto', paddingLeft: 12 }}>
            {yFormat ? yFormat(p.value) : p.value?.toFixed(2)}
          </span>
        </div>
      ))}
    </div>
  )
}

// ─── FKLineChart ─────────────────────────────────────────────────────────────
export function FKLineChart({
  data,
  series,
  xKey          = 'date',
  yKey,
  xType         = 'time',
  yFormat,
  xFormat,
  referenceLines,
  height        = 240,
  rangeSelector,
  defaultRange,
  onRangeChange,
  smooth        = false,
  connectNulls  = false,
  dot           = false,
  interpolation,        // 'linear' | 'step' | 'stepBefore' | 'stepAfter'
  title,
  subtitle,
  badge,
  stats,
}) {
  const resolvedData   = data   || SAMPLE_DATA
  const resolvedSeries = series || (yKey ? [{ key: yKey, label: yKey }] : SAMPLE_SERIES)
  const rangeOptions   = Array.isArray(rangeSelector) ? rangeSelector : ['1M', '3M', '6M', '1Y']
  const [range, setRange] = useState(defaultRange || rangeOptions[rangeOptions.length - 1])

  const seriesMap = Object.fromEntries(resolvedSeries.map(s => [s.key, s.label || s.key]))

  const handleRangeChange = r => { setRange(r); onRangeChange?.(r) }

  const actions = rangeSelector
    ? <FKRangeSelector options={rangeOptions} value={range} onChange={handleRangeChange} />
    : badge
    ? <FKBadge variant="neutral">{badge}</FKBadge>
    : null

  // interpolation prop takes precedence over smooth boolean
  const curveType = interpolation
    ? (interpolation === 'step' ? 'stepAfter' : interpolation)
    : smooth ? 'monotone' : 'linear'

  return (
    <FKCard>
      <FKCardHeader title={title} subtitle={subtitle} actions={actions} />
      <div style={{ height, padding: '12px 4px 8px 0' }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={resolvedData} margin={{ top: 4, right: 4, left: 0, bottom: 0 }}>
            <defs>
              {resolvedSeries.map((s, i) => {
                const c = s.color || color.series[i % color.series.length]
                return (
                  <linearGradient key={s.key} id={`fkline-grad-${s.key}`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%"   stopColor={c} stopOpacity={0.15} />
                    <stop offset="100%" stopColor={c} stopOpacity={0} />
                  </linearGradient>
                )
              })}
            </defs>

            <CartesianGrid {...gridProps} />

            <XAxis
              dataKey={xKey}
              {...axisProps}
              minTickGap={40}
              maxRotation={0}
              tickFormatter={xFormat}
              interval={xType === 'category' ? 0 : 'preserveStartEnd'}
            />
            <YAxis
              {...axisProps}
              orientation="right"
              width={52}
              tickFormatter={yFormat}
            />

            <Tooltip
              content={
                <CustomTooltip yFormat={yFormat} seriesMap={seriesMap} />
              }
              cursor={{ stroke: 'var(--color-border-secondary)', strokeWidth: 1 }}
            />

            {/* Gradient fills (rendered before lines so lines sit on top) */}
            {resolvedSeries.map((s, i) => {
              const c = s.color || color.series[i % color.series.length]
              return (
                <Area
                  key={`area-${s.key}`}
                  type={curveType}
                  dataKey={s.key}
                  fill={`url(#fkline-grad-${s.key})`}
                  stroke="none"
                  connectNulls={connectNulls}
                  legendType="none"
                  isAnimationActive={false}
                />
              )
            })}

            {/* Lines */}
            {resolvedSeries.map((s, i) => {
              const c = s.color || color.series[i % color.series.length]
              return (
                <Line
                  key={`line-${s.key}`}
                  type={curveType}
                  dataKey={s.key}
                  name={s.label || s.key}
                  stroke={c}
                  strokeWidth={1.5}
                  strokeDasharray={s.dashed ? '4 3' : undefined}
                  dot={dot ? { fill: c, r: 3, strokeWidth: 0 } : false}
                  connectNulls={connectNulls}
                  isAnimationActive={false}
                />
              )
            })}

            {/* Reference lines */}
            {referenceLines?.map((rl, i) => (
              <ReferenceLine
                key={i}
                x={rl.x !== undefined ? rl.x : undefined}
                y={rl.y !== undefined ? rl.y : undefined}
                label={
                  rl.label
                    ? {
                        value:    rl.label,
                        fill:     rl.color || 'var(--color-text-tertiary)',
                        fontSize: 10,
                        fontFamily: 'var(--font-mono)',
                      }
                    : undefined
                }
                stroke={
                  rl.color ||
                  (rl.y === 0 ? 'rgba(0,0,0,0.15)' : 'var(--color-border-secondary)')
                }
                strokeDasharray={rl.dashed ? '4 3' : undefined}
                strokeWidth={1}
              />
            ))}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      {stats && <FKStatStrip stats={stats} />}
    </FKCard>
  )
}
