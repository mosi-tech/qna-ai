import React, { useState } from 'react'
import {
  ResponsiveContainer, ComposedChart, BarChart, Bar, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, LabelList,
} from 'recharts'
import { FKCard, FKCardHeader } from './FKCard.jsx'
import { FKStatStrip, FKBadge } from './FKSparkline.jsx'
import { FKRangeSelector } from './FKRangeSelector.jsx'
import { color, axisProps, categoryAxisProps, gridProps, tooltipStyle, resolveColor } from './tokens.js'

// ─── Sample data ─────────────────────────────────────────────────────────────
const SAMPLE_DATA = [
  { label: 'Jan', value:  4200 },
  { label: 'Feb', value: -1800 },
  { label: 'Mar', value:  6100 },
  { label: 'Apr', value:  3400 },
  { label: 'May', value: -2200 },
  { label: 'Jun', value:  5800 },
  { label: 'Jul', value:  2100 },
  { label: 'Aug', value: -900  },
]

// ─── Bar fill helpers ────────────────────────────────────────────────────────
function defaultColorRule(row, key) {
  const v = key ? row[key] : row.value
  return v >= 0 ? 'gain' : 'loss'
}

function barFill(token) {
  if (token === 'gain')    return 'rgba(22,163,74,0.72)'
  if (token === 'loss')    return 'rgba(220,38,38,0.72)'
  if (token === 'warn')    return 'rgba(217,119,6,0.72)'
  if (token === 'neutral') return 'rgba(148,163,184,0.6)'
  return token
}
function barStroke(token) {
  if (token === 'gain')    return color.gain
  if (token === 'loss')    return color.loss
  if (token === 'warn')    return color.warn
  if (token === 'neutral') return '#94a3b8'
  return token
}

// ─── Custom tooltip ───────────────────────────────────────────────────────────
function BarTooltip({ active, payload, label, yFormat }) {
  if (!active || !payload?.length) return null
  return (
    <div style={tooltipStyle}>
      <div style={{ color: 'var(--color-text-secondary)', marginBottom: 6, fontSize: 13, fontFamily: 'var(--font-sans)' }}>{label}</div>
      {payload.filter(p => p.dataKey !== '_base').map((p, i) => (
        <div key={i} className="flex items-center gap-2" style={{ color: 'var(--color-text-primary)' }}>
          <span style={{ fontSize: 13, fontFamily: 'var(--font-sans)' }}>{p.name || p.dataKey}</span>
          <span style={{ fontWeight: 500, marginLeft: 'auto', paddingLeft: 12 }}>
            {yFormat ? yFormat(p.value) : p.value?.toLocaleString()}
          </span>
        </div>
      ))}
    </div>
  )
}

// ─── Waterfall helpers ────────────────────────────────────────────────────────
function buildWaterfallData(data, valueKey, colorRule) {
  let running = 0
  return data.map((row, i) => {
    const v      = row[valueKey] ?? 0
    const base   = v < 0 ? running + v : running
    const absVal = Math.abs(v)
    running     += v
    const token  = colorRule ? colorRule(row) : (v >= 0 ? 'gain' : 'loss')
    return { ...row, _base: base, _wfVal: absVal, _running: running, _token: token }
  })
}

// ─── FKBarChart ──────────────────────────────────────────────────────────────
const RANGE_COUNTS = { '1M': 1, '3M': 3, '6M': 6, '1Y': 12, '2Y': 24, 'ALL': Infinity }

export function FKBarChart({
  data,
  series,
  valueKey        = 'value',
  labelKey        = 'label',
  orientation     = 'vertical',
  mode            = 'single',
  colorRule,
  referenceValue,
  height          = 200,
  maxBarSize,
  showRunningTotal = true,
  totalLabel      = 'Total',
  yFormat,
  rangeSelector,
  defaultRange,
  title,
  subtitle,
  badge,
  stats,
}) {
  const rangeOptions = Array.isArray(rangeSelector) ? rangeSelector : ['3M', '6M', '1Y', 'ALL']
  const [range, setRange] = useState(defaultRange || rangeOptions[rangeOptions.length - 1])

  const resolvedColorRule = colorRule || ((row, key) => defaultColorRule(row, key || valueKey))
  const rawData = data || SAMPLE_DATA

  // Slice to range when rangeSelector is enabled
  const rangeFiltered = rangeSelector
    ? rawData.slice(-Math.min(rawData.length, RANGE_COUNTS[range] ?? Infinity))
    : rawData

  let resolvedData = rangeFiltered

  const actions = rangeSelector
    ? <FKRangeSelector options={rangeOptions} value={range} onChange={setRange} />
    : badge ? <FKBadge variant="neutral">{badge}</FKBadge> : null

  // ── Horizontal: sort descending ──────────────────────────────────────────
  if (orientation === 'horizontal') {
    resolvedData = [...resolvedData].sort((a, b) => (b[valueKey] || 0) - (a[valueKey] || 0))
  }

  // ── Waterfall ─────────────────────────────────────────────────────────────
  if (mode === 'waterfall') {
    const wfData = buildWaterfallData(resolvedData, valueKey, colorRule)
    const defaultMax = 24
    return (
      <FKCard>
        <FKCardHeader
          title={title}
          subtitle={subtitle}
          actions={actions}
        />
        <div style={{ height, padding: '12px 8px 8px 8px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={wfData} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
              <CartesianGrid {...gridProps} />
              <XAxis dataKey={labelKey} {...axisProps} />
              <YAxis {...axisProps} orientation="right" width={52} tickFormatter={yFormat} />
              <Tooltip content={<BarTooltip yFormat={yFormat} />} />
              {/* Invisible base bar */}
              <Bar dataKey="_base" stackId="wf" fill="transparent" stroke="none" maxBarSize={maxBarSize || defaultMax} isAnimationActive={false} legendType="none" />
              {/* Visible colored bar */}
              <Bar dataKey="_wfVal" stackId="wf" maxBarSize={maxBarSize || defaultMax} isAnimationActive={false}
                radius={[4, 4, 0, 0]}
              >
                {wfData.map((row, i) => (
                  <Cell key={i} fill={barFill(row._token)} stroke={barStroke(row._token)} strokeWidth={1} />
                ))}
              </Bar>
            </ComposedChart>
          </ResponsiveContainer>
        </div>
        {stats && <FKStatStrip stats={stats} />}
      </FKCard>
    )
  }

  // ── Grouped ───────────────────────────────────────────────────────────────
  if (mode === 'grouped' && series?.length) {
    return (
      <FKCard>
        <FKCardHeader
          title={title}
          subtitle={subtitle}
          actions={actions}
        />
        <div style={{ height, padding: '12px 8px 8px 8px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={resolvedData} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
              <CartesianGrid {...gridProps} />
              <XAxis dataKey={labelKey} {...axisProps} />
              <YAxis {...axisProps} orientation="right" width={52} tickFormatter={yFormat} />
              <Tooltip content={<BarTooltip yFormat={yFormat} />} />
              {referenceValue !== undefined && (
                <ReferenceLine y={referenceValue} stroke="var(--color-border-secondary)" strokeDasharray="4 3" strokeWidth={1} />
              )}
              {series.map((s, si) => (
                <Bar key={s.key} dataKey={s.key} name={s.label || s.key}
                  maxBarSize={maxBarSize || 24} radius={[4, 4, 0, 0]} isAnimationActive={false}
                >
                  {resolvedData.map((row, i) => {
                    const token = colorRule ? colorRule(row, s.key) : 'neutral'
                    return <Cell key={i} fill={barFill(token)} stroke={barStroke(token)} strokeWidth={1} />
                  })}
                </Bar>
              ))}
            </BarChart>
          </ResponsiveContainer>
        </div>
        {stats && <FKStatStrip stats={stats} />}
      </FKCard>
    )
  }

  // ── Stacked ───────────────────────────────────────────────────────────────
  if (mode === 'stacked' && series?.length) {
    return (
      <FKCard>
        <FKCardHeader
          title={title}
          subtitle={subtitle}
          actions={actions}
        />
        <div style={{ height, padding: '12px 8px 8px 8px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={resolvedData} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
              <CartesianGrid {...gridProps} />
              <XAxis dataKey={labelKey} {...axisProps} />
              <YAxis {...axisProps} orientation="right" width={52} tickFormatter={yFormat} />
              <Tooltip content={<BarTooltip yFormat={yFormat} />} />
              {series.map((s, si) => {
                const c = s.color || color.series[si % color.series.length]
                return (
                  <Bar key={s.key} dataKey={s.key} name={s.label || s.key}
                    stackId="stack" fill={c} maxBarSize={maxBarSize || 40}
                    radius={si === series.length - 1 ? [4, 4, 0, 0] : [0, 0, 0, 0]}
                    isAnimationActive={false}
                  />
                )
              })}
            </BarChart>
          </ResponsiveContainer>
        </div>
        {stats && <FKStatStrip stats={stats} />}
      </FKCard>
    )
  }

  // ── Lollipop ──────────────────────────────────────────────────────────────
  if (mode === 'lollipop') {
    const STEM_W = 2, DOT_R = 8
    const LollipopBar = (props) => {
      const { x, y, width, height: h, value, index } = props
      const row   = resolvedData[index] || {}
      const token = resolvedColorRule(row, valueKey)
      const fill  = barStroke(token)
      const cx    = (x || 0) + (width || 0) / 2
      const isPos = (value || 0) >= 0
      const zeroY = (y || 0) + (isPos ? h : 0)
      return (
        <g>
          <rect x={cx - STEM_W / 2} y={Math.min(y, zeroY)} width={STEM_W} height={Math.abs(h)} fill={fill} opacity={0.5} />
          <circle cx={cx} cy={y} r={DOT_R} fill={fill} opacity={0.85} />
        </g>
      )
    }
    return (
      <FKCard>
        <FKCardHeader title={title} subtitle={subtitle} actions={badge ? <FKBadge variant="neutral">{badge}</FKBadge> : null} />
        <div style={{ height, padding: '12px 8px 8px 8px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={resolvedData} margin={{ top: 12, right: 8, left: 0, bottom: 0 }}>
              <CartesianGrid {...gridProps} />
              <XAxis dataKey={labelKey} {...axisProps} />
              <YAxis {...axisProps} orientation="right" width={52} tickFormatter={yFormat} />
              <Tooltip content={<BarTooltip yFormat={yFormat} />} />
              {referenceValue !== undefined && (
                <ReferenceLine y={referenceValue} stroke="var(--color-border-secondary)" strokeDasharray="4 3" strokeWidth={1} />
              )}
              <Bar dataKey={valueKey} maxBarSize={40} isAnimationActive={false} shape={<LollipopBar />} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        {stats && <FKStatStrip stats={stats} />}
      </FKCard>
    )
  }

  // ── Single (default) ─────────────────────────────────────────────────────
  const isHoriz  = orientation === 'horizontal'
  const defMax   = isHoriz ? 32 : 40
  const radius   = isHoriz ? [0, 4, 4, 0] : [4, 4, 0, 0]

  return (
    <FKCard>
      <FKCardHeader
        title={title}
        subtitle={subtitle}
        actions={badge ? <FKBadge variant="neutral">{badge}</FKBadge> : null}
      />
      <div style={{ height, padding: '12px 8px 8px 8px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={resolvedData}
            layout={isHoriz ? 'vertical' : 'horizontal'}
            margin={{ top: 4, right: isHoriz ? 52 : 8, left: isHoriz ? 60 : 0, bottom: 0 }}
          >
            <CartesianGrid {...gridProps} horizontal={!isHoriz} vertical={isHoriz} />
            {isHoriz ? (
              <>
                <XAxis type="number" {...axisProps} tickFormatter={yFormat} orientation="bottom" />
                <YAxis type="category" dataKey={labelKey} {...categoryAxisProps} width={56} />
              </>
            ) : (
              <>
                <XAxis dataKey={labelKey} {...axisProps} />
                <YAxis {...axisProps} orientation="right" width={52} tickFormatter={yFormat} />
              </>
            )}
            <Tooltip content={<BarTooltip yFormat={yFormat} />} />
            {referenceValue !== undefined && (
              <ReferenceLine
                y={!isHoriz ? referenceValue : undefined}
                x={isHoriz ? referenceValue : undefined}
                stroke="var(--color-border-secondary)"
                strokeDasharray="4 3"
                strokeWidth={1}
              />
            )}
            <Bar
              dataKey={valueKey}
              maxBarSize={maxBarSize || defMax}
              radius={radius}
              isAnimationActive={false}
            >
              {resolvedData.map((row, i) => {
                const token = resolvedColorRule(row, valueKey)
                return <Cell key={i} fill={barFill(token)} stroke={barStroke(token)} strokeWidth={1} />
              })}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      {stats && <FKStatStrip stats={stats} />}
    </FKCard>
  )
}
