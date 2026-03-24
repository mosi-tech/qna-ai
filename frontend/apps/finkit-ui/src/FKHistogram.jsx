import React, { useMemo } from 'react'
import {
  ResponsiveContainer, ComposedChart, Bar, Cell, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine,
} from 'recharts'
import { FKCard, FKCardHeader } from './FKCard.jsx'
import { FKTooltip } from './FKTooltip.jsx'
import { FKStatStrip, FKBadge } from './FKSparkline.jsx'
import { color, axisProps, gridProps } from './tokens.js'

// ─── Sample data ──────────────────────────────────────────────────────────────
const SAMPLE_RETURNS = Array.from({ length: 200 }, () =>
  parseFloat(((Math.random() - 0.48) * 6 + (Math.random() - 0.5) * 2).toFixed(3))
)

// ─── Bin computation ──────────────────────────────────────────────────────────
function computeBins(values, binCount, binWidth) {
  if (!values?.length) return []
  const min = Math.min(...values)
  const max = Math.max(...values)
  const n   = values.length

  let width
  if (binWidth) {
    width = binWidth
  } else {
    // Sturges rule
    const k = binCount || Math.ceil(1 + Math.log2(n))
    width = (max - min) / k
  }
  if (width === 0) width = 1

  const bins = new Map()
  values.forEach(v => {
    const idx = Math.floor((v - min) / width)
    const mid = parseFloat((min + (idx + 0.5) * width).toFixed(4))
    bins.set(mid, (bins.get(mid) || 0) + 1)
  })

  return Array.from(bins.entries())
    .sort((a, b) => a[0] - b[0])
    .map(([mid, count]) => ({ mid, count }))
}

// ─── Normal curve (density scaled to histogram) ───────────────────────────────
function normalDensity(x, mean, std) {
  return (1 / (std * Math.sqrt(2 * Math.PI))) * Math.exp(-0.5 * ((x - mean) / std) ** 2)
}

// ─── FKHistogram ──────────────────────────────────────────────────────────────
export function FKHistogram({
  data,
  binCount,
  binWidth,
  overlayNormal  = false,
  referenceLines,
  colorRule,
  xFormat,
  yFormat,
  height         = 220,
  title,
  subtitle,
  badge,
  stats,
}) {
  const values = data || SAMPLE_RETURNS

  const bins = useMemo(() => computeBins(values, binCount, binWidth), [values, binCount, binWidth])

  const { mean, std, pctPos } = useMemo(() => {
    const n   = values.length
    const mu  = values.reduce((s, v) => s + v, 0) / n
    const sig = Math.sqrt(values.reduce((s, v) => s + (v - mu) ** 2, 0) / n)
    const pp  = values.filter(v => v >= 0).length / n * 100
    return { mean: mu, std: sig, pctPos: pp }
  }, [values])

  const defaultColorRule = (mid) => mid >= 0 ? 'gain' : 'loss'
  const resolvedRule = colorRule || defaultColorRule

  function fillFor(token) {
    if (token === 'gain')    return 'rgba(22,163,74,0.72)'
    if (token === 'loss')    return 'rgba(220,38,38,0.72)'
    if (token === 'warn')    return 'rgba(217,119,6,0.72)'
    if (token === 'neutral') return 'rgba(148,163,184,0.6)'
    return token
  }
  function strokeFor(token) {
    if (token === 'gain')    return color.gain
    if (token === 'loss')    return color.loss
    if (token === 'warn')    return color.warn
    if (token === 'neutral') return '#94a3b8'
    return token
  }

  // Normal curve overlay: scale density to match bin counts
  const maxCount = Math.max(...bins.map(b => b.count), 1)
  const maxDensity = normalDensity(mean, mean, std)
  const normalScale = maxCount / maxDensity

  const chartData = bins.map(b => ({
    ...b,
    normal: overlayNormal
      ? parseFloat((normalDensity(b.mid, mean, std) * normalScale).toFixed(2))
      : undefined,
  }))

  const xFmt = xFormat || (v => `${v > 0 ? '+' : ''}${parseFloat(v).toFixed(1)}%`)
  const yFmt = yFormat || (v => v)

  const autoStats = stats || [
    { label: 'Mean',     value: xFmt(mean),    color: mean >= 0 ? color.gain : color.loss },
    { label: 'Std Dev',  value: xFmt(std) },
    { label: '% Positive', value: `${pctPos.toFixed(1)}%` },
    { label: 'N',        value: values.length },
  ]

  return (
    <FKCard>
      <FKCardHeader
        title={title}
        subtitle={subtitle}
        actions={badge ? <FKBadge variant="neutral">{badge}</FKBadge> : null}
      />
      <div style={{ height, padding: '12px 8px 8px 8px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
            <CartesianGrid {...gridProps} />
            <XAxis dataKey="mid" {...axisProps} tickFormatter={xFmt} minTickGap={40} type="number" domain={['dataMin', 'dataMax']} />
            <YAxis {...axisProps} orientation="right" width={36} tickFormatter={yFmt} />
            <Tooltip
              content={<FKTooltip
                xFormat={xFmt}
                valueFormat={v => String(v)}
              />}
              cursor={{ fill: 'rgba(0,0,0,0.04)' }}
            />

            {referenceLines?.map((rl, i) => (
              <ReferenceLine
                key={i}
                x={rl.x}
                stroke={rl.color || 'var(--color-border-secondary)'}
                strokeDasharray={rl.dashed !== false ? '4 3' : undefined}
                strokeWidth={1}
                label={rl.label ? { value: rl.label, fill: rl.color || 'var(--color-text-tertiary)', fontSize: 12, fontFamily: 'var(--font-sans)' } : undefined}
              />
            ))}

            <Bar dataKey="count" name="Count" maxBarSize={24} isAnimationActive={false}>
              {chartData.map((entry, i) => {
                const token = resolvedRule(entry.mid)
                return <Cell key={i} fill={fillFor(token)} stroke={strokeFor(token)} strokeWidth={1} />
              })}
            </Bar>

            {overlayNormal && (
              <Line
                type="monotone"
                dataKey="normal"
                name="Normal"
                stroke={color.series[0]}
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
              />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      <FKStatStrip stats={autoStats} />
    </FKCard>
  )
}
