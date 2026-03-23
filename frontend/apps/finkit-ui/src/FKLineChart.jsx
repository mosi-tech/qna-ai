import React, { useState, useMemo } from 'react'
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
function CustomTooltip({ active, payload, label, yFormat, seriesColors, seriesMap, viewMode }) {
  if (!active || !payload?.length) return null
  // Keep only the last occurrence of each dataKey (Line comes after Area — has correct color)
  const last = {}
  payload.forEach(p => { last[p.dataKey] = p })
  const unique = Object.values(last).filter(p => seriesColors[p.dataKey])

  const fmt = viewMode === 'pct'
    ? v => `${v >= 0 ? '+' : ''}${v?.toFixed(2)}%`
    : yFormat || (v => v?.toFixed(2))

  return (
    <div style={tooltipStyle}>
      <div style={{ color: 'var(--color-text-tertiary)', marginBottom: 6, fontSize: 13,
                    fontFamily: 'var(--font-sans)', paddingBottom: 6,
                    borderBottom: '1px solid var(--color-border-tertiary)' }}>
        {label}
      </div>
      {unique.map((p, i) => {
        const c = seriesColors[p.dataKey]
        return (
          <div key={i} className="flex items-center justify-between gap-6 mt-1.5">
            <div className="flex items-center gap-2">
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: c, flexShrink: 0, display: 'inline-block' }} />
              <span style={{ fontSize: 13, fontFamily: 'var(--font-sans)', color: 'var(--color-text-secondary)' }}>
                {seriesMap[p.dataKey] || p.dataKey}
              </span>
            </div>
            <span style={{ fontSize: 13, fontFamily: 'var(--font-mono)', fontWeight: 500,
                           color: 'var(--color-text-primary)', tabularNums: true }}>
              {fmt(p.value)}
            </span>
          </div>
        )
      })}
    </div>
  )
}

// ─── % change normalizer ─────────────────────────────────────────────────────
function normalizeToPercent(data, series) {
  const firsts = {}
  series.forEach(s => {
    const first = data.find(r => r[s.key] != null)
    if (first) firsts[s.key] = first[s.key]
  })
  return data.map(row => {
    const out = { ...row }
    series.forEach(s => {
      const base = firsts[s.key]
      if (row[s.key] != null && base) {
        out[s.key] = parseFloat(((row[s.key] / base - 1) * 100).toFixed(3))
      }
    })
    return out
  })
}

// ─── ViewMode toggle ─────────────────────────────────────────────────────────
function ViewToggle({ value, onChange }) {
  return (
    <div className="flex items-center gap-0.5 bg-[var(--color-background-tertiary)] rounded-lg p-0.5">
      {['%', '$'].map(opt => (
        <button
          key={opt}
          onClick={() => onChange(opt === '%' ? 'pct' : 'value')}
          className={[
            'px-2.5 py-1 rounded-md text-[12px] font-sans font-medium transition-colors leading-none',
            value === (opt === '%' ? 'pct' : 'value')
              ? 'bg-[var(--color-background-primary)] text-[var(--color-text-primary)] shadow-sm'
              : 'text-[var(--color-text-tertiary)] hover:text-[var(--color-text-secondary)]',
          ].join(' ')}
          style={{ border: 'none', cursor: 'pointer', background: value === (opt === '%' ? 'pct' : 'value') ? undefined : 'transparent' }}
        >
          {opt}
        </button>
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
  interpolation,
  defaultViewMode,  // 'pct' | 'value' — overrides auto-detection
  title,
  subtitle,
  badge,
  stats,
}) {
  const resolvedData   = data   || SAMPLE_DATA
  const resolvedSeries = series || (yKey ? [{ key: yKey, label: yKey }] : SAMPLE_SERIES)
  const isMulti        = resolvedSeries.length >= 2

  // Default to % mode when multi-series, unless caller overrides
  const [viewMode, setViewMode] = useState(defaultViewMode || (isMulti ? 'pct' : 'value'))

  const rangeOptions = Array.isArray(rangeSelector) ? rangeSelector : ['1M', '3M', '6M', '1Y']
  const [range, setRange] = useState(defaultRange || rangeOptions[rangeOptions.length - 1])

  const seriesColors = Object.fromEntries(
    resolvedSeries.map((s, i) => [s.key, s.color || color.series[i % color.series.length]])
  )
  const seriesMap = Object.fromEntries(resolvedSeries.map(s => [s.key, s.label || s.key]))

  const handleRangeChange = r => { setRange(r); onRangeChange?.(r) }

  const chartData = useMemo(
    () => viewMode === 'pct' ? normalizeToPercent(resolvedData, resolvedSeries) : resolvedData,
    [resolvedData, resolvedSeries, viewMode]
  )

  // Tight y-axis domain: pad by 5% of the actual data range (not the values)
  const yDomain = useMemo(() => {
    if (viewMode === 'pct') return ['auto', 'auto']
    const vals = resolvedSeries.flatMap(s => chartData.map(d => d[s.key])).filter(v => v != null)
    if (!vals.length) return ['auto', 'auto']
    const lo  = Math.min(...vals)
    const hi  = Math.max(...vals)
    const pad = (hi - lo) * 0.05 || Math.abs(lo) * 0.02 || 1
    return [lo - pad, hi + pad]
  }, [chartData, resolvedSeries, viewMode])

  // y-axis format: in pct mode always show %, in value mode use caller's yFormat
  const activeYFormat = viewMode === 'pct'
    ? v => `${v >= 0 ? '+' : ''}${v?.toFixed(1)}%`
    : yFormat

  const curveType = interpolation
    ? (interpolation === 'step' ? 'stepAfter' : interpolation)
    : smooth ? 'monotone' : 'linear'

  const actions = (
    <div className="flex items-center gap-2">
      {isMulti && <ViewToggle value={viewMode} onChange={setViewMode} />}
      {rangeSelector && <FKRangeSelector options={rangeOptions} value={range} onChange={handleRangeChange} />}
      {!rangeSelector && badge && <FKBadge variant="neutral">{badge}</FKBadge>}
    </div>
  )

  return (
    <FKCard>
      <FKCardHeader title={title} subtitle={subtitle} actions={actions} />
      <div style={{ height, padding: '12px 4px 8px 0' }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 4, right: 4, left: 8, bottom: 0 }}>
            <defs>
              {resolvedSeries.map((s, i) => {
                const c = seriesColors[s.key]
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
              padding={{ left: 16, right: 8 }}
            />
            <YAxis
              {...axisProps}
              orientation="right"
              width={52}
              tickFormatter={activeYFormat}
              domain={yDomain}
            />

            <Tooltip
              content={
                <CustomTooltip
                  yFormat={yFormat}
                  seriesColors={seriesColors}
                  seriesMap={seriesMap}
                  viewMode={viewMode}
                />
              }
              cursor={{ stroke: 'var(--color-border-secondary)', strokeWidth: 1 }}
            />

            {/* Gradient fills — Area comes first (below lines) */}
            {resolvedSeries.map(s => (
              <Area
                key={`area-${s.key}`}
                type={curveType}
                dataKey={s.key}
                fill={`url(#fkline-grad-${s.key})`}
                stroke="none"
                connectNulls={connectNulls}
                legendType="none"
                tooltipType="none"
                isAnimationActive={false}
              />
            ))}

            {/* Lines */}
            {resolvedSeries.map(s => {
              const c = seriesColors[s.key]
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
                label={rl.label ? {
                  value: rl.label,
                  fill: rl.color || 'var(--color-text-tertiary)',
                  fontSize: 12,
                  fontFamily: 'var(--font-sans)',
                } : undefined}
                stroke={rl.color || (rl.y === 0 ? 'rgba(0,0,0,0.15)' : 'var(--color-border-secondary)')}
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
