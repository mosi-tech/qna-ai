import React, { useMemo } from 'react'
import {
  ResponsiveContainer, ComposedChart, Bar, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, LabelList,
} from 'recharts'
import { FKCard, FKCardHeader } from './FKCard.jsx'
import { FKTooltip } from './FKTooltip.jsx'
import { color, axisProps, categoryAxisProps, gridProps } from './tokens.js'

// ─── Sample data ──────────────────────────────────────────────────────────────
const SAMPLE_DATA = [
  { label: 'Q2 Revenue',    value: 850, type: 'start' },
  { label: 'New Contracts', value: 120, type: 'delta' },
  { label: 'Churn',         value: -45, type: 'delta' },
  { label: 'Upsell',        value:  60, type: 'delta' },
  { label: 'FX Impact',     value: -20, type: 'delta' },
  { label: 'Q3 Revenue',    value: 965, type: 'end'   },
]

// ─── Bar fill helpers ──────────────────────────────────────────────────────────
function cellFill(row) {
  if (row.type === 'start' || row.type === 'end') return 'rgba(148,163,184,0.7)'
  return row.value >= 0 ? 'rgba(22,163,74,0.72)' : 'rgba(220,38,38,0.72)'
}
function cellStroke(row) {
  if (row.type === 'start' || row.type === 'end') return '#94a3b8'
  return row.value >= 0 ? color.gain : color.loss
}

// ─── Value label formatter ────────────────────────────────────────────────────
function defaultFormat(v) {
  if (v == null) return ''
  return v.toLocaleString()
}

// ─── Build chart data for stacked invisible-base approach ─────────────────────
function buildWaterfallRows(data) {
  let running = 0
  return data.map((row, i) => {
    const isAbsolute = row.type === 'start' || row.type === 'end'
    let base, barH, finalRunning

    if (isAbsolute) {
      base = 0
      barH = row.value
      finalRunning = row.value
    } else {
      base      = row.value >= 0 ? running : running + row.value
      barH      = Math.abs(row.value)
      finalRunning = running + row.value
    }

    const result = { ...row, _base: base, _barH: barH, _running: running, _next: finalRunning }
    running = finalRunning
    return result
  })
}

// ─── Connector line custom shape ─────────────────────────────────────────────
function ConnectorLine({ data, xAxisMap, yAxisMap, barWidth }) {
  if (!data?.length || !xAxisMap || !yAxisMap) return null
  const xAxis = Object.values(xAxisMap)[0]
  const yAxis = Object.values(yAxisMap)[0]
  if (!xAxis?.scale || !yAxis?.scale) return null

  const lines = data.slice(0, -1).map((row, i) => {
    const x1 = xAxis.scale(i)     + xAxis.scale.bandwidth()
    const x2 = xAxis.scale(i + 1)
    const y  = yAxis.scale(row._next)
    return <line key={i} x1={x1} y1={y} x2={x2} y2={y}
      stroke="var(--color-border-secondary)" strokeWidth={1} strokeDasharray="3 2" />
  })

  return <g>{lines}</g>
}

// ─── Custom tooltip ───────────────────────────────────────────────────────────
function WaterfallTooltip({ active, payload, label, valueFormat }) {
  if (!active || !payload?.length) return null
  const row = payload[0]?.payload
  if (!row) return null
  const fmt = valueFormat || defaultFormat
  return (
    <FKTooltip.Box>
      <FKTooltip.Header>{label}</FKTooltip.Header>
      <FKTooltip.Row
        color={cellFill(row)}
        label={row.type === 'start' || row.type === 'end' ? 'Total' : 'Change'}
        value={(row.value >= 0 && row.type === 'delta' ? '+' : '') + fmt(row.value)}
      />
      {row.type === 'delta' && (
        <FKTooltip.Row label="Running total" value={fmt(row._next)} />
      )}
    </FKTooltip.Box>
  )
}

// ─── FKWaterfall ──────────────────────────────────────────────────────────────
export function FKWaterfall({
  data,
  title,
  subtitle,
  height       = 320,
  valueFormat,
  yFormat,
}) {
  const rows = useMemo(() => buildWaterfallRows(data || SAMPLE_DATA), [data])
  const fmt  = valueFormat || defaultFormat

  return (
    <FKCard>
      <FKCardHeader title={title} subtitle={subtitle} />
      <div style={{ height, padding: '16px 8px 8px 8px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={rows} margin={{ top: 20, right: 8, left: 0, bottom: 0 }}>
            <CartesianGrid {...gridProps} />
            <XAxis dataKey="label" {...categoryAxisProps} />
            <YAxis
              {...axisProps}
              orientation="right"
              width={60}
              tickFormatter={yFormat || (v => v.toLocaleString())}
            />
            <Tooltip
              content={<WaterfallTooltip valueFormat={valueFormat} />}
              cursor={{ fill: 'var(--color-background-secondary)', opacity: 0.5 }}
            />

            {/* Invisible base bar */}
            <Bar dataKey="_base" stackId="wf" fill="transparent" stroke="none"
              maxBarSize={48} isAnimationActive={false} legendType="none" />

            {/* Visible colored bar */}
            <Bar dataKey="_barH" stackId="wf" maxBarSize={48} isAnimationActive={false}
              radius={[4, 4, 0, 0]}
            >
              {rows.map((row, i) => (
                <Cell key={i} fill={cellFill(row)} stroke={cellStroke(row)} strokeWidth={1} />
              ))}
              {/* Value labels above bars */}
              <LabelList
                dataKey="value"
                position="top"
                content={({ x, y, width, value, index }) => {
                  const row = rows[index]
                  if (!row) return null
                  const sign = row.type === 'delta' && value > 0 ? '+' : ''
                  const display = sign + fmt(value)
                  const textColor = cellStroke(row)
                  return (
                    <text
                      x={(x || 0) + (width || 0) / 2}
                      y={(y || 0) - 4}
                      textAnchor="middle"
                      fontSize={12}
                      fontFamily="var(--font-mono)"
                      fontWeight={500}
                      fill={textColor}
                    >
                      {display}
                    </text>
                  )
                }}
              />
            </Bar>
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </FKCard>
  )
}
