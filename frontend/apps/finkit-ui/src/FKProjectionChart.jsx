import React, { useMemo } from 'react'
import {
  ResponsiveContainer, ComposedChart, Line, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine,
} from 'recharts'
import { FKCard, FKCardHeader } from './FKCard.jsx'
import { FKTooltip } from './FKTooltip.jsx'
import { color, axisProps, gridProps } from './tokens.js'

// ─── Sample data ──────────────────────────────────────────────────────────────
const SAMPLE_HISTORICAL = [
  { date: '2020', value: 100_000 },
  { date: '2021', value: 118_000 },
  { date: '2022', value: 109_000 },
  { date: '2023', value: 134_000 },
  { date: '2024', value: 158_000 },
]
const SAMPLE_PROJECTION = [
  { date: '2025', median: 172_000, p10: 145_000, p25: 158_000, p75: 189_000, p90: 210_000 },
  { date: '2026', median: 188_000, p10: 148_000, p25: 168_000, p75: 214_000, p90: 244_000 },
  { date: '2027', median: 205_000, p10: 155_000, p25: 178_000, p75: 238_000, p90: 278_000 },
  { date: '2028', median: 224_000, p10: 158_000, p25: 190_000, p75: 266_000, p90: 316_000 },
  { date: '2030', median: 260_000, p10: 172_000, p25: 210_000, p75: 325_000, p90: 410_000 },
]

function defaultFormat(v) {
  if (v == null) return ''
  return '$' + Math.round(v).toLocaleString()
}

// ─── Legend ───────────────────────────────────────────────────────────────────
function ProjLegend({ scenarios }) {
  const seriesColor = color.series[0]
  return (
    <div className="flex flex-wrap gap-x-4 gap-y-1" style={{ padding: '6px 20px 12px' }}>
      <div className="flex items-center gap-1.5">
        <div style={{ width: 20, height: 2, background: seriesColor }} />
        <span style={{ fontSize: 13, fontFamily: 'var(--font-sans)', color: 'var(--color-text-secondary)' }}>Historical</span>
      </div>
      {!scenarios ? (
        <>
          <div className="flex items-center gap-1.5">
            <div style={{ width: 20, height: 2, background: seriesColor, borderTop: `1.5px dashed ${seriesColor}`, borderBottom: 'none' }} />
            <span style={{ fontSize: 13, fontFamily: 'var(--font-sans)', color: 'var(--color-text-secondary)' }}>Median projection</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div style={{ width: 12, height: 10, background: `${color.series[0]}30`, borderRadius: 2 }} />
            <span style={{ fontSize: 13, fontFamily: 'var(--font-sans)', color: 'var(--color-text-secondary)' }}>50% range</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div style={{ width: 12, height: 10, background: `${color.series[0]}12`, borderRadius: 2 }} />
            <span style={{ fontSize: 13, fontFamily: 'var(--font-sans)', color: 'var(--color-text-secondary)' }}>80% range</span>
          </div>
        </>
      ) : scenarios.map((s, i) => (
        <div key={s.key} className="flex items-center gap-1.5">
          <div style={{ width: 20, height: 2, background: s.color || color.series[i + 1], borderTop: `1.5px dashed ${s.color}` }} />
          <span style={{ fontSize: 13, fontFamily: 'var(--font-sans)', color: 'var(--color-text-secondary)' }}>{s.label || s.key}</span>
        </div>
      ))}
    </div>
  )
}

// ─── Build merged chart data ──────────────────────────────────────────────────
function buildChartData(historical, projection, scenarios, splitDate) {
  const hist = (historical || SAMPLE_HISTORICAL).map(r => ({
    date: r.date, value: r.value, isHistorical: true,
  }))

  const proj = (projection || SAMPLE_PROJECTION).map(r => ({
    date: r.date,
    projected: r.median,
    p25: r.p25, p75: r.p75,
    p10: r.p10, p90: r.p90,
    isHistorical: false,
  }))

  // Bridge point: carry last historical value into first projection point
  if (hist.length && proj.length) {
    const lastHist = hist[hist.length - 1]
    proj[0].projected = proj[0].projected ?? lastHist.value
  }

  // Scenario lines
  const scenarioCols = {}
  if (scenarios) {
    scenarios.forEach(s => {
      s.data?.forEach(r => {
        const existing = [...hist, ...proj].find(row => row.date === r.date)
        if (!scenarioCols[r.date]) scenarioCols[r.date] = { date: r.date }
        scenarioCols[r.date][s.key] = r.value
      })
    })
  }

  // Merge all
  const allDates = [...new Set([...hist.map(r => r.date), ...proj.map(r => r.date), ...Object.keys(scenarioCols)])]
  return allDates.map(date => ({
    date,
    ...hist.find(r => r.date === date),
    ...proj.find(r => r.date === date),
    ...(scenarioCols[date] || {}),
  }))
}

// ─── Custom tooltip ───────────────────────────────────────────────────────────
function ProjectionTooltip({ active, payload, label, valueFormat }) {
  if (!active || !payload?.length) return null
  const fmt  = valueFormat || defaultFormat
  const rows = payload.filter(p => p.value != null && !['p10', 'p90', 'p25Ref', 'p75Ref'].includes(p.dataKey))
  return (
    <FKTooltip.Box style={{ position: 'relative' }}>
      <FKTooltip.Header>{label}</FKTooltip.Header>
      {rows.map((p, i) => (
        <FKTooltip.Row key={i} color={p.color} label={p.name || p.dataKey} value={fmt(p.value)} />
      ))}
    </FKTooltip.Box>
  )
}

// ─── FKProjectionChart ────────────────────────────────────────────────────────
export function FKProjectionChart({
  historical,
  projection,
  scenarios,
  splitDate,
  valueFormat,
  title,
  subtitle,
  height = 320,
}) {
  const fmt      = valueFormat || defaultFormat
  const chartData = useMemo(
    () => buildChartData(historical, projection, scenarios, splitDate),
    [historical, projection, scenarios, splitDate]
  )

  const resolvedSplit = splitDate ||
    (historical || SAMPLE_HISTORICAL).slice(-1)[0]?.date ||
    chartData.find(r => r.projected != null)?.date

  const mainColor = color.series[0]

  return (
    <FKCard>
      <FKCardHeader title={title} subtitle={subtitle} />
      <div style={{ height, padding: '12px 4px 4px 0' }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 4, right: 4, left: 0, bottom: 0 }}>
            <defs>
              {/* p25-p75 band */}
              <linearGradient id="proj-inner" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={mainColor} stopOpacity={0.30} />
                <stop offset="100%" stopColor={mainColor} stopOpacity={0.20} />
              </linearGradient>
              {/* p10-p90 band */}
              <linearGradient id="proj-outer" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={mainColor} stopOpacity={0.12} />
                <stop offset="100%" stopColor={mainColor} stopOpacity={0.06} />
              </linearGradient>
            </defs>

            <CartesianGrid {...gridProps} />
            <XAxis dataKey="date" {...axisProps} minTickGap={40} maxRotation={0} />
            <YAxis {...axisProps} orientation="right" width={64} tickFormatter={v => fmt(v).replace('$','$').slice(0, 7)} />

            <Tooltip
              content={<ProjectionTooltip valueFormat={valueFormat} />}
              cursor={{ stroke: 'var(--color-border-secondary)', strokeWidth: 1 }}
            />

            {/* Split date reference */}
            {resolvedSplit && (
              <ReferenceLine
                x={resolvedSplit}
                stroke="var(--color-text-tertiary)"
                strokeDasharray="4 3"
                strokeWidth={1}
                label={{
                  value: 'Today',
                  position: 'insideTopLeft',
                  fill: 'var(--color-text-tertiary)',
                  fontSize: 12,
                  fontFamily: 'var(--font-sans)',
                }}
              />
            )}

            {/* Outer band (p10–p90) */}
            {!scenarios && (
              <Area type="monotone" dataKey="p90" name="p90"
                fill="url(#proj-outer)" stroke="none" isAnimationActive={false} legendType="none"
                activeDot={false} />
            )}
            {!scenarios && (
              <Area type="monotone" dataKey="p10" name="p10"
                fill="var(--color-background-primary)" stroke="none"
                isAnimationActive={false} legendType="none" activeDot={false} />
            )}

            {/* Inner band (p25–p75) */}
            {!scenarios && (
              <Area type="monotone" dataKey="p75" name="50% range"
                fill="url(#proj-inner)" stroke="none" isAnimationActive={false} legendType="none"
                activeDot={false} />
            )}
            {!scenarios && (
              <Area type="monotone" dataKey="p25" name="50% range low"
                fill="var(--color-background-primary)" stroke="none"
                isAnimationActive={false} legendType="none" activeDot={false} />
            )}

            {/* Historical line */}
            <Line type="monotone" dataKey="value" name="Historical"
              stroke={mainColor} strokeWidth={2}
              dot={false} isAnimationActive={false} connectNulls />

            {/* Projected median */}
            {!scenarios && (
              <Line type="monotone" dataKey="projected" name="Median"
                stroke={mainColor} strokeWidth={1.5} strokeDasharray="5 3"
                dot={false} isAnimationActive={false} connectNulls />
            )}

            {/* Scenario lines */}
            {scenarios?.map((s, i) => (
              <Line key={s.key} type="monotone" dataKey={s.key} name={s.label || s.key}
                stroke={s.color || color.series[i + 1]}
                strokeWidth={1.5} strokeDasharray="5 3"
                dot={false} isAnimationActive={false} connectNulls />
            ))}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      <ProjLegend scenarios={scenarios} />
    </FKCard>
  )
}
