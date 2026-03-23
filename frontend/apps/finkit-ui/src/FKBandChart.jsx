import React from 'react'
import {
  ResponsiveContainer, ComposedChart, Area, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine,
} from 'recharts'
import { FKCard, FKCardHeader } from './FKCard.jsx'
import { FKTooltip } from './FKTooltip.jsx'
import { FKRangeSelector, useRangeFilter } from './FKRangeSelector.jsx'
import { FKStatStrip, FKBadge } from './FKSparkline.jsx'
import { color, axisProps, gridProps, defaultRangeOptions } from './tokens.js'

// ─── Sample data ──────────────────────────────────────────────────────────────
function makeSampleData(n = 60) {
  let v = 0
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
  return Array.from({ length: n }, (_, i) => {
    v = parseFloat((v + (Math.random() - 0.52) * 1.5).toFixed(2))
    const d = new Date(2023, Math.floor(i / 5) % 12, (i % 5) * 5 + 1)
    return { date: `${months[d.getMonth()]} '${String(23 + Math.floor(i / 12)).slice(-2)}`, value: v }
  })
}
const SAMPLE_DATA = makeSampleData()

// ─── Split fills above / below baseline ──────────────────────────────────────
function buildSplitData(data, valueKey, baseline) {
  return data.map(row => {
    const v = row[valueKey] ?? 0
    return {
      ...row,
      _above: v >= baseline ? v : baseline,
      _below: v <= baseline ? v : baseline,
      _baseline: baseline,
    }
  })
}

// ─── FKBandChart ──────────────────────────────────────────────────────────────
export function FKBandChart({
  data,
  series,
  xKey                 = 'date',
  baseline             = 0,
  fillAbove,
  fillBelow,
  fillAboveOpacity     = 0.15,
  fillBelowOpacity     = 0.30,
  yFormat,
  referenceLines,
  height               = 200,
  rangeSelector        = true,
  defaultRange         = '1Y',
  onRangeChange,
  title,
  subtitle,
  badge,
  stats,
}) {
  const rawData   = data   || SAMPLE_DATA
  const resolvedSeries = series || [{ key: 'value', label: 'Value' }]
  const isTwoSeries    = resolvedSeries.length >= 2

  const rangeOptions = Array.isArray(rangeSelector) ? rangeSelector : defaultRangeOptions
  const { range, setRange, filteredData } = useRangeFilter(rawData, defaultRange)

  const handleRangeChange = r => { setRange(r); onRangeChange?.(r) }

  const resolvedAbove = fillAbove !== undefined ? fillAbove : color.gain
  const resolvedBelow = fillBelow !== undefined ? fillBelow : color.loss

  // Y domain from filtered data
  const allVals = filteredData.flatMap(row => resolvedSeries.map(s => row[s.key] ?? 0))
  const yMin = Math.min(...allVals, baseline)
  const yMax = Math.max(...allVals, baseline)
  const pad  = (yMax - yMin) * 0.08 || 1
  const yDomain = [yMin - pad, yMax + pad]

  const chartData = isTwoSeries ? filteredData : buildSplitData(filteredData, resolvedSeries[0].key, baseline)
  const s0color   = resolvedSeries[0].color || color.series[0]
  const s1color   = resolvedSeries[1]?.color || color.series[1]

  const actions = rangeSelector
    ? <FKRangeSelector options={rangeOptions} value={range} onChange={handleRangeChange} />
    : badge
    ? <FKBadge variant="neutral">{badge}</FKBadge>
    : null

  return (
    <FKCard>
      <FKCardHeader title={title} subtitle={subtitle} actions={actions} />
      <div style={{ height, padding: '12px 4px 8px 0' }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 4, right: 4, left: 0, bottom: 0 }}>
            <defs>
              {resolvedAbove && (
                <linearGradient id="fkband-above" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%"   stopColor={resolvedAbove} stopOpacity={fillAboveOpacity} />
                  <stop offset="100%" stopColor={resolvedAbove} stopOpacity={0} />
                </linearGradient>
              )}
              {resolvedBelow && (
                <linearGradient id="fkband-below" x1="0" y1="1" x2="0" y2="0">
                  <stop offset="0%"   stopColor={resolvedBelow} stopOpacity={fillBelowOpacity} />
                  <stop offset="100%" stopColor={resolvedBelow} stopOpacity={0} />
                </linearGradient>
              )}
            </defs>

            <CartesianGrid {...gridProps} />
            <XAxis dataKey={xKey} {...axisProps} minTickGap={40} maxRotation={0} />
            <YAxis {...axisProps} orientation="right" width={52} tickFormatter={yFormat} domain={yDomain} />
            <Tooltip
              content={<FKTooltip yFormat={yFormat} valueFormat={yFormat} />}
              cursor={{ stroke: 'var(--color-border-secondary)', strokeWidth: 1 }}
            />

            {/* Baseline reference line */}
            <ReferenceLine
              y={baseline}
              stroke="rgba(0,0,0,0.2)"
              strokeWidth={1}
            />

            {/* User reference lines */}
            {referenceLines?.map((rl, i) => (
              <ReferenceLine
                key={i}
                x={rl.x}
                y={rl.y}
                stroke={rl.color || 'var(--color-border-secondary)'}
                strokeDasharray={rl.dashed ? '4 3' : undefined}
                strokeWidth={1}
                label={rl.label ? { value: rl.label, fill: rl.color || 'var(--color-text-tertiary)', fontSize: 12, fontFamily: 'var(--font-sans)' } : undefined}
              />
            ))}

            {isTwoSeries ? (
              /* Two-series: fill between the two lines */
              <>
                {resolvedAbove && (
                  <Area
                    type="linear"
                    dataKey={resolvedSeries[0].key}
                    stroke={s0color}
                    strokeWidth={1.5}
                    fill={resolvedAbove}
                    fillOpacity={fillAboveOpacity}
                    isAnimationActive={false}
                  />
                )}
                <Line
                  type="linear"
                  dataKey={resolvedSeries[1].key}
                  stroke={s1color}
                  strokeWidth={1.5}
                  dot={false}
                  isAnimationActive={false}
                />
              </>
            ) : (
              /* Single series: fill above and/or below baseline separately */
              <>
                {resolvedAbove && (
                  <Area
                    type="linear"
                    dataKey="_above"
                    stroke="none"
                    fill="url(#fkband-above)"
                    isAnimationActive={false}
                    legendType="none"
                  />
                )}
                {resolvedBelow && (
                  <Area
                    type="linear"
                    dataKey="_below"
                    stroke="none"
                    fill="url(#fkband-below)"
                    isAnimationActive={false}
                    legendType="none"
                  />
                )}
                <Line
                  type="linear"
                  dataKey={resolvedSeries[0].key}
                  name={resolvedSeries[0].label || resolvedSeries[0].key}
                  stroke={s0color}
                  strokeWidth={1.5}
                  dot={false}
                  isAnimationActive={false}
                />
              </>
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      {stats && <FKStatStrip stats={stats} />}
    </FKCard>
  )
}
