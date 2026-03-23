import React, { useState, useMemo } from 'react'
import {
  ResponsiveContainer, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip,
} from 'recharts'
import { FKCard, FKCardHeader } from './FKCard.jsx'
import { FKRangeSelector, FKStatStrip, FKBadge } from './FKSparkline.jsx'
import { color, axisProps, gridProps, tooltipStyle } from './tokens.js'

// ─── Sample data ─────────────────────────────────────────────────────────────
const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
const SAMPLE_SERIES = [
  { key: 'tech',    label: 'Technology' },
  { key: 'finance', label: 'Financials' },
  { key: 'health',  label: 'Healthcare' },
  { key: 'energy',  label: 'Energy' },
  { key: 'other',   label: 'Other' },
]
function makeSampleData() {
  return Array.from({ length: 12 }, (_, i) => {
    const raw = { tech: 35 + Math.random() * 10, finance: 20 + Math.random() * 8, health: 15 + Math.random() * 6, energy: 12 + Math.random() * 5 }
    raw.other = Math.max(0, 100 - raw.tech - raw.finance - raw.health - raw.energy)
    return { date: MONTHS[i], ...raw }
  })
}
const SAMPLE_DATA = makeSampleData()

// ─── Tooltip ──────────────────────────────────────────────────────────────────
function AreaTooltip({ active, payload, label, mode, seriesMap }) {
  if (!active || !payload?.length) return null
  return (
    <div style={tooltipStyle}>
      <div style={{ color: 'var(--color-text-secondary)', marginBottom: 6, fontSize: 13, fontFamily: 'var(--font-sans)' }}>{label}</div>
      {[...payload].reverse().map((p, i) => (
        <div key={i} className="flex items-center gap-2" style={{ color: p.fill }}>
          <span style={{ fontSize: 13, fontFamily: 'var(--font-sans)' }}>{seriesMap?.[p.dataKey] || p.dataKey}</span>
          <span style={{ fontWeight: 500, marginLeft: 'auto', paddingLeft: 12 }}>
            {mode === 'normalized' ? `${p.value?.toFixed(1)}%` : p.value?.toFixed(1)}
          </span>
        </div>
      ))}
    </div>
  )
}

// ─── Legend row ───────────────────────────────────────────────────────────────
function AreaLegend({ series }) {
  return (
    <div className="flex flex-wrap gap-x-4 gap-y-1" style={{ padding: '8px 20px 12px' }}>
      {series.map((s, i) => {
        const c = s.color || color.series[i % color.series.length]
        return (
          <div key={s.key} className="flex items-center gap-1.5">
            <div style={{ width: 10, height: 10, borderRadius: 2, background: c, flexShrink: 0 }} />
            <span style={{ fontSize: 13, fontFamily: 'var(--font-sans)', color: 'var(--color-text-secondary)' }}>{s.label || s.key}</span>
          </div>
        )
      })}
    </div>
  )
}

// ─── FKAreaChart ─────────────────────────────────────────────────────────────
export function FKAreaChart({
  data,
  series,
  xKey          = 'date',
  mode          = 'normalized',
  yFormat,
  height        = 260,
  rangeSelector,
  defaultRange,
  onRangeChange,
  title,
  subtitle,
  badge,
}) {
  const rawData    = data   || SAMPLE_DATA
  const rawSeries  = series || SAMPLE_SERIES
  const rangeOpts  = Array.isArray(rangeSelector) ? rangeSelector : ['1M', '3M', '6M', '1Y']
  const [range, setRange] = useState(defaultRange || rangeOpts[rangeOpts.length - 1])

  // Compute normalized data (each x sums to 100%)
  const chartData = useMemo(() => {
    if (mode !== 'normalized') return rawData
    return rawData.map(row => {
      const sum = rawSeries.reduce((acc, s) => acc + (row[s.key] || 0), 0) || 1
      const out = { [xKey]: row[xKey] }
      rawSeries.forEach(s => { out[s.key] = parseFloat(((row[s.key] || 0) / sum * 100).toFixed(2)) })
      return out
    })
  }, [rawData, rawSeries, mode, xKey])

  const seriesMap = Object.fromEntries(rawSeries.map(s => [s.key, s.label || s.key]))

  const actions = rangeSelector
    ? <FKRangeSelector options={rangeOpts} value={range} onChange={r => { setRange(r); onRangeChange?.(r) }} />
    : badge ? <FKBadge variant="neutral">{badge}</FKBadge> : null

  const tickFmt = mode === 'normalized' ? (v => `${v}%`) : yFormat

  return (
    <FKCard>
      <FKCardHeader title={title} subtitle={subtitle} actions={actions} />
      <div style={{ height, padding: '12px 4px 4px 0' }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 4, right: 4, left: 0, bottom: 0 }}>
            <CartesianGrid {...gridProps} />
            <XAxis dataKey={xKey} {...axisProps} minTickGap={40} maxRotation={0} />
            <YAxis
              {...axisProps}
              orientation="right"
              width={48}
              domain={mode === 'normalized' ? [0, 100] : ['auto', 'auto']}
              tickFormatter={tickFmt}
            />
            <Tooltip
              content={<AreaTooltip mode={mode} seriesMap={seriesMap} />}
              cursor={{ stroke: 'var(--color-border-secondary)', strokeWidth: 1 }}
            />
            {rawSeries.map((s, i) => {
              const c = s.color || color.series[i % color.series.length]
              return (
                <Area
                  key={s.key}
                  type="monotone"
                  dataKey={s.key}
                  name={s.label || s.key}
                  stackId="1"
                  fill={c}
                  fillOpacity={0.75}
                  stroke="rgba(255,255,255,0.4)"
                  strokeWidth={1}
                  isAnimationActive={false}
                />
              )
            })}
          </AreaChart>
        </ResponsiveContainer>
      </div>
      <AreaLegend series={rawSeries} />
    </FKCard>
  )
}
