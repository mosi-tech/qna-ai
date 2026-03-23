import React, { useState, useMemo, useCallback } from 'react'
import {
  ResponsiveContainer, PieChart, Pie, Cell, Tooltip,
} from 'recharts'
import { FKCard, FKCardHeader } from './FKCard.jsx'
import { FKBadge } from './FKSparkline.jsx'
import { color, tooltipStyle } from './tokens.js'

// ─── Sample data ──────────────────────────────────────────────────────────────
const SAMPLE_DATA = [
  { label: 'Technology', value: 34.2 },
  { label: 'Healthcare', value: 18.5 },
  { label: 'Financials', value: 15.8 },
  { label: 'Consumer',   value: 12.4 },
  { label: 'Energy',     value:  9.1 },
  { label: 'Other',      value: 10.0 },
]

// ─── Squarified treemap ───────────────────────────────────────────────────────
function squarify(items, x, y, w, h) {
  if (!items.length) return []
  const total = items.reduce((a, b) => a + b.value, 0)
  if (!total) return []

  const rects = []
  let remaining = [...items]

  function worst(row, side) {
    const rowSum = row.reduce((a, b) => a + b.value, 0)
    const max    = Math.max(...row.map(i => i.value))
    const min    = Math.min(...row.map(i => i.value))
    return Math.max((side * side * max) / (rowSum * rowSum), (rowSum * rowSum) / (side * side * min))
  }

  function layoutRow(row, isHoriz, cx, cy, cw, ch, rowTotal, grandTotal) {
    const frac = rowTotal / grandTotal
    const rowW = isHoriz ? cw : cw * frac
    const rowH = isHoriz ? ch * frac : ch
    let pos = isHoriz ? cx : cy
    row.forEach(item => {
      const itemFrac = item.value / rowTotal
      const iw = isHoriz ? rowW * itemFrac : rowW
      const ih = isHoriz ? rowH : rowH * itemFrac
      const ix = isHoriz ? pos : cx
      const iy = isHoriz ? cy : pos
      rects.push({ ...item, x: ix, y: iy, w: iw, h: ih })
      pos += isHoriz ? iw : ih
    })
    return isHoriz
      ? { cx, cy: cy + rowH, cw, ch: ch - rowH }
      : { cx: cx + rowW, cy, cw: cw - rowW, ch }
  }

  let cx = x, cy = y, cw = w, ch = h
  let rem = [...remaining]
  while (rem.length) {
    const side     = Math.min(cw, ch)
    const isHoriz  = cw >= ch
    const remTotal = rem.reduce((a, b) => a + b.value, 0)

    let row = [rem[0]]
    let i   = 1
    while (i < rem.length) {
      const newRow   = [...row, rem[i]]
      const rowTotal = newRow.reduce((a, b) => a + b.value, 0)
      const s2       = isHoriz ? cw : ch
      if (worst(row, side) < worst(newRow, side)) {
        row = newRow
        i++
      } else {
        break
      }
      i = newRow.length
      break
    }

    const rowTotal = row.reduce((a, b) => a + b.value, 0)
    const bounds   = layoutRow(row, isHoriz, cx, cy, cw, ch, rowTotal, remTotal)
    ;({ cx, cy, cw, ch } = bounds)
    rem = rem.slice(row.length)
  }
  return rects
}

// ─── Donut mode ───────────────────────────────────────────────────────────────
function DonutChart({ data, valueKey, labelKey, colorKey, innerLabel, innerSub, size = 160 }) {
  const [active, setActive] = useState(null)
  const total = data.reduce((a, b) => a + (b[valueKey] || 0), 0)

  return (
    <div className="flex items-center gap-6" style={{ padding: '12px 20px 16px' }}>
      <div style={{ position: 'relative', width: size, height: size, flexShrink: 0 }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%" cy="50%"
              innerRadius={size * 0.35}
              outerRadius={size * 0.48}
              paddingAngle={2}
              strokeWidth={0}
              dataKey={valueKey}
              onMouseEnter={(_, i) => setActive(i)}
              onMouseLeave={() => setActive(null)}
            >
              {data.map((row, i) => {
                const c = row[colorKey] || color.series[i % color.series.length]
                return (
                  <Cell key={i} fill={c} opacity={active === null || active === i ? 1 : 0.4} />
                )
              })}
            </Pie>
            <Tooltip
              formatter={(v, name) => [`${((v / total) * 100).toFixed(1)}%`, name]}
              contentStyle={tooltipStyle}
            />
          </PieChart>
        </ResponsiveContainer>
        {/* Center label */}
        {(innerLabel || innerSub) && (
          <div style={{
            position: 'absolute', inset: 0, display: 'flex',
            flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            pointerEvents: 'none',
          }}>
            {innerLabel && (
              <span style={{ fontSize: 16, fontWeight: 600, fontFamily: 'var(--font-mono)', color: 'var(--color-text-primary)' }}>
                {innerLabel}
              </span>
            )}
            {innerSub && (
              <span style={{ fontSize: 12, fontFamily: 'var(--font-sans)', color: 'var(--color-text-tertiary)', marginTop: 2 }}>
                {innerSub}
              </span>
            )}
          </div>
        )}
      </div>

      {/* Legend with bars */}
      <div className="flex flex-col gap-2 flex-1 min-w-0">
        {data.map((row, i) => {
          const c   = row[colorKey] || color.series[i % color.series.length]
          const pct = total ? (row[valueKey] || 0) / total * 100 : 0
          return (
            <div key={i}
              className="flex items-center gap-2 cursor-default"
              style={{ opacity: active === null || active === i ? 1 : 0.4 }}
              onMouseEnter={() => setActive(i)}
              onMouseLeave={() => setActive(null)}
            >
              <div style={{ width: 10, height: 10, borderRadius: 3, background: c, flexShrink: 0 }} />
              <span className="text-xs truncate flex-1" style={{ color: 'var(--color-text-primary)' }}>
                {row[labelKey]}
              </span>
              <span className="text-[13px] font-mono" style={{ color: 'var(--color-text-secondary)', flexShrink: 0 }}>
                {pct.toFixed(1)}%
              </span>
              <div style={{ width: 60, height: 3, borderRadius: 99, background: 'var(--color-background-secondary)' }}>
                <div style={{ height: '100%', borderRadius: 99, background: c, width: `${Math.max(2, pct)}%` }} />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ─── Treemap mode ─────────────────────────────────────────────────────────────
function TreemapChart({ data, valueKey, labelKey, colorKey, colorBy = 'index', height = 260 }) {
  const [hov, setHov] = useState(null)
  const sorted = useMemo(() => [...data].sort((a, b) => (b[valueKey] || 0) - (a[valueKey] || 0)), [data, valueKey])

  const [dims, setDims] = useState({ w: 560, h: height - 20 })
  const rects = useMemo(() => squarify(sorted.map(r => ({ ...r, value: r[valueKey] || 0 })), 0, 0, dims.w, dims.h), [sorted, dims])

  function cellColor(row, i) {
    if (colorBy === 'index') return color.series[i % color.series.length]
    if (colorBy === 'colorKey' && row[colorKey] != null) {
      // diverging by return value
      const v = row[colorKey]
      return v >= 0 ? `rgba(22,163,74,${Math.min(0.8, 0.2 + Math.abs(v) * 0.06)})` : `rgba(220,38,38,${Math.min(0.8, 0.2 + Math.abs(v) * 0.06)})`
    }
    return color.series[i % color.series.length]
  }

  return (
    <div
      style={{ position: 'relative', height: dims.h + 20, padding: '10px 20px 10px', overflow: 'hidden' }}
      ref={el => {
        if (el) {
          const w = el.clientWidth - 40
          if (Math.abs(w - dims.w) > 4) setDims({ w, h: height - 20 })
        }
      }}
    >
      <div style={{ position: 'relative', width: dims.w, height: dims.h }}>
        {rects.map((rect, i) => {
          const c = cellColor(rect, i)
          return (
            <div
              key={i}
              onMouseEnter={() => setHov(i)}
              onMouseLeave={() => setHov(null)}
              title={`${rect[labelKey]}: ${rect[valueKey]?.toFixed(1)}`}
              style={{
                position:     'absolute',
                left:         rect.x + 2,
                top:          rect.y + 2,
                width:        Math.max(0, rect.w - 4),
                height:       Math.max(0, rect.h - 4),
                background:   c,
                borderRadius: 6,
                border:       `1px solid ${c}28`,
                overflow:     'hidden',
                cursor:       'default',
                opacity:      hov === null || hov === i ? 1 : 0.7,
                display:      'flex',
                flexDirection:'column',
                alignItems:   'center',
                justifyContent: 'center',
                padding:      4,
              }}
            >
              {rect.w > 48 && (
                <span style={{ fontSize: Math.min(12, rect.w / 7), fontFamily: 'var(--font-sans)', fontWeight: 600, color: '#fff', textShadow: '0 1px 2px rgba(0,0,0,0.3)', textAlign: 'center', lineHeight: 1.2, overflow: 'hidden', whiteSpace: 'nowrap' }}>
                  {rect[labelKey]}
                </span>
              )}
              {rect.w > 72 && rect.h > 32 && (
                <span style={{ fontSize: Math.min(12, rect.w / 8), color: 'rgba(255,255,255,0.8)', marginTop: 2, fontFamily: 'var(--font-mono)' }}>
                  {rect[valueKey]?.toFixed(1)}
                </span>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ─── Bars mode ────────────────────────────────────────────────────────────────
function BarsChart({ data, valueKey, labelKey, showTotal = true }) {
  const sorted = useMemo(() => [...data].sort((a, b) => (b[valueKey] || 0) - (a[valueKey] || 0)), [data, valueKey])
  const total  = sorted.reduce((a, b) => a + (b[valueKey] || 0), 0)
  const max    = Math.max(...sorted.map(r => r[valueKey] || 0)) || 1

  return (
    <div style={{ padding: '10px 20px 16px' }}>
      {showTotal && (
        <div style={{ fontSize: 20, fontWeight: 600, fontFamily: 'var(--font-mono)', color: 'var(--color-text-primary)', marginBottom: 12 }}>
          {total.toFixed(1)}%
          <span style={{ fontSize: 13, fontFamily: 'var(--font-sans)', fontWeight: 400, marginLeft: 6, color: 'var(--color-text-tertiary)' }}>total</span>
        </div>
      )}
      <div className="flex flex-col gap-3">
        {sorted.map((row, i) => {
          const c   = color.series[i % color.series.length]
          const pct = (row[valueKey] || 0) / max * 100
          return (
            <div key={i} className="flex items-center gap-3">
              <span className="text-sm min-w-[100px]" style={{ color: 'var(--color-text-primary)' }}>
                {row[labelKey]}
              </span>
              <div style={{ flex: 1, height: 4, borderRadius: 99, background: 'var(--color-background-secondary)' }}>
                <div style={{ height: '100%', borderRadius: 99, background: c, width: `${Math.max(1, pct)}%`, transition: 'width 0.3s' }} />
              </div>
              <span className="text-[13px] font-mono min-w-[40px] text-right" style={{ color: 'var(--color-text-secondary)' }}>
                {row[valueKey]?.toFixed(1)}%
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ─── FKPartChart ─────────────────────────────────────────────────────────────
export function FKPartChart({
  data,
  valueKey    = 'value',
  labelKey    = 'label',
  colorKey,
  mode        = 'donut',
  innerLabel,
  innerSub,
  size        = 160,
  colorBy     = 'index',
  showTotal   = true,
  height      = 200,
  title,
  subtitle,
  badge,
}) {
  const resolvedData = data || SAMPLE_DATA
  const actions      = badge ? <FKBadge variant="neutral">{badge}</FKBadge> : null

  return (
    <FKCard>
      <FKCardHeader title={title} subtitle={subtitle} actions={actions} />
      {mode === 'donut' && (
        <DonutChart
          data={resolvedData}
          valueKey={valueKey}
          labelKey={labelKey}
          colorKey={colorKey}
          innerLabel={innerLabel}
          innerSub={innerSub}
          size={size}
        />
      )}
      {mode === 'treemap' && (
        <TreemapChart
          data={resolvedData}
          valueKey={valueKey}
          labelKey={labelKey}
          colorKey={colorKey}
          colorBy={colorBy}
          height={height || 260}
        />
      )}
      {mode === 'bars' && (
        <BarsChart
          data={resolvedData}
          valueKey={valueKey}
          labelKey={labelKey}
          showTotal={showTotal}
        />
      )}
    </FKCard>
  )
}
