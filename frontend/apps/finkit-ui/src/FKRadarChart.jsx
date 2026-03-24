import React from 'react'
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer, Tooltip, Legend,
} from 'recharts'
import { FKCard, FKCardHeader } from './FKCard.jsx'
import { FKTooltip } from './FKTooltip.jsx'
import { color } from './tokens.js'

// ─── Sample data ──────────────────────────────────────────────────────────────
const SAMPLE_AXES = [
  { key: 'value',    label: 'Value',    max: 100 },
  { key: 'quality',  label: 'Quality',  max: 100 },
  { key: 'momentum', label: 'Momentum', max: 100 },
  { key: 'growth',   label: 'Growth',   max: 100 },
  { key: 'safety',   label: 'Safety',   max: 100 },
]
const SAMPLE_SERIES = [
  { key: 'AAPL', label: 'AAPL', data: { value: 62, quality: 88, momentum: 74, growth: 71, safety: 80 } },
  { key: 'MSFT', label: 'MSFT', data: { value: 55, quality: 91, momentum: 68, growth: 78, safety: 85 } },
]

// ─── Normalize data for Recharts RadarChart ────────────────────────────────────
// Recharts RadarChart expects: Array<{ subject: string, [seriesKey]: normalizedValue }>
function buildRadarData(axes, seriesList) {
  return axes.map(axis => {
    const row = { subject: axis.label }
    seriesList.forEach(s => {
      const raw = s.data[axis.key] ?? 0
      const max = axis.max || 100
      row[s.key] = parseFloat(((raw / max) * 100).toFixed(1))
      row[`_raw_${s.key}`] = raw
    })
    return row
  })
}

// ─── Custom tooltip ────────────────────────────────────────────────────────────
function RadarTooltip({ active, payload, label, seriesList }) {
  if (!active || !payload?.length) return null
  return (
    <FKTooltip.Box style={{ position: 'relative' }}>
      <FKTooltip.Header>{label}</FKTooltip.Header>
      {payload.map((entry, i) => {
        const s = seriesList.find(s => s.key === entry.dataKey)
        const axis = SAMPLE_AXES.find(a => a.label === label)
        const rawKey = `_raw_${entry.dataKey}`
        const rawVal = entry.payload?.[rawKey]
        return (
          <FKTooltip.Row
            key={i}
            color={entry.color}
            label={s?.label || entry.dataKey}
            value={rawVal != null ? rawVal.toFixed(0) : entry.value?.toFixed(1)}
          />
        )
      })}
    </FKTooltip.Box>
  )
}

// ─── FKRadarChart ──────────────────────────────────────────────────────────────
export function FKRadarChart({
  axes,
  series,
  fillOpacity = 0.15,
  title,
  subtitle,
  height      = 320,
}) {
  const resolvedAxes   = axes   || SAMPLE_AXES
  const resolvedSeries = series || SAMPLE_SERIES

  const chartData = buildRadarData(resolvedAxes, resolvedSeries)

  return (
    <FKCard>
      <FKCardHeader title={title} subtitle={subtitle} />
      <div style={{ height, padding: '8px 8px 0' }}>
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={chartData} margin={{ top: 16, right: 24, bottom: 16, left: 24 }}>
            <PolarGrid
              gridType="polygon"
              stroke="var(--color-border-secondary)"
              strokeWidth={0.5}
            />
            <PolarAngleAxis
              dataKey="subject"
              tick={{
                fontSize:   12,
                fill:       'var(--color-text-secondary)',
                fontFamily: 'var(--font-sans)',
              }}
            />
            <PolarRadiusAxis
              angle={90}
              domain={[0, 100]}
              tick={{ fontSize: 12, fill: 'var(--color-text-tertiary)', fontFamily: 'var(--font-mono)' }}
              tickCount={4}
              axisLine={false}
            />
            <Tooltip
              content={<RadarTooltip seriesList={resolvedSeries} />}
            />
            {resolvedSeries.map((s, i) => {
              const c = s.color || color.series[i % color.series.length]
              return (
                <Radar
                  key={s.key}
                  name={s.label || s.key}
                  dataKey={s.key}
                  stroke={c}
                  strokeWidth={1.5}
                  fill={c}
                  fillOpacity={fillOpacity}
                  isAnimationActive={false}
                />
              )
            })}
            {resolvedSeries.length > 1 && (
              <Legend
                iconType="circle"
                iconSize={8}
                wrapperStyle={{ fontSize: 13, fontFamily: 'var(--font-sans)', paddingTop: 8 }}
              />
            )}
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </FKCard>
  )
}
