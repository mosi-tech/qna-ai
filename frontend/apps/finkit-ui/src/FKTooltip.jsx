import React from 'react'
import { tooltipStyle } from './tokens.js'

// ─── FKTooltip — standard single/multi-series tooltip ────────────────────────
// Usage with Recharts:
//   <Tooltip content={<FKTooltip xFormat={d => formatDate(d)} valueFormat={v => `$${v}`} />} />
export function FKTooltip({ xFormat, valueFormat, colorMap, active, payload, label }) {
  if (!active || !payload?.length) return null
  // Filter internals then deduplicate by dataKey (Area+Line share the same key)
  const seen = new Set()
  const visible = payload.filter(e => {
    if (e.dataKey === '_base' || e.dataKey === '__hidden') return false
    if (seen.has(e.dataKey)) return false
    seen.add(e.dataKey)
    return true
  })
  if (!visible.length) return null
  return (
    <div style={tooltipStyle}>
      <div className="text-xs text-[var(--color-text-tertiary)] font-sans mb-2 pb-1.5
                      border-b border-[var(--color-border-tertiary)]">
        {xFormat ? xFormat(label) : label}
      </div>
      {visible.map((entry, i) => (
        <div key={i} className="flex items-center justify-between gap-6 mt-1.5">
          <div className="flex items-center gap-2">
            <span style={{ background: colorMap?.[entry.dataKey] ?? entry.color }}
                  className="w-2 h-2 rounded-full flex-shrink-0" />
            <span className="text-[13px] text-[var(--color-text-secondary)] font-sans">
              {entry.name ?? entry.dataKey}
            </span>
          </div>
          <span className="text-[13px] text-[var(--color-text-primary)] font-mono font-medium tabular-nums">
            {valueFormat ? valueFormat(entry.value) : entry.value?.toLocaleString?.() ?? entry.value}
          </span>
        </div>
      ))}
    </div>
  )
}

// ─── FKTooltip.OHLC — candlestick tooltip with 4 price values + volume ───────
FKTooltip.OHLC = function OHLCTooltip({ active, payload, label, xFormat, valueFormat }) {
  if (!active || !payload?.length) return null
  const d = payload[0]?.payload ?? {}
  const fmt = valueFormat ?? (v => v?.toFixed(2))
  const isUp = (d.close ?? 0) >= (d.open ?? 0)
  return (
    <div style={tooltipStyle}>
      <div className="text-xs text-[var(--color-text-tertiary)] font-sans mb-2 pb-1.5
                      border-b border-[var(--color-border-tertiary)]">
        {xFormat ? xFormat(label) : label}
      </div>
      {[
        { label: 'Open',  value: d.open,  color: 'var(--color-text-secondary)' },
        { label: 'High',  value: d.high,  color: '#16a34a' },
        { label: 'Low',   value: d.low,   color: '#dc2626' },
        { label: 'Close', value: d.close, color: isUp ? '#16a34a' : '#dc2626' },
      ].map(row => (
        <div key={row.label} className="flex items-center justify-between gap-6 mt-1.5">
          <span className="text-[13px] text-[var(--color-text-secondary)] font-sans">{row.label}</span>
          <span className="text-[13px] font-mono font-medium tabular-nums" style={{ color: row.color }}>
            {fmt(row.value)}
          </span>
        </div>
      ))}
      {d.volume != null && (
        <div className="flex items-center justify-between gap-6 mt-1.5 pt-1.5
                        border-t border-[var(--color-border-tertiary)]">
          <span className="text-[13px] text-[var(--color-text-secondary)] font-sans">Volume</span>
          <span className="text-[13px] font-mono tabular-nums text-[var(--color-text-tertiary)]">
            {(d.volume / 1_000_000).toFixed(1)}M
          </span>
        </div>
      )}
    </div>
  )
}

// ─── FKTooltip.Scatter — two-axis + label + size tooltip ─────────────────────
FKTooltip.Scatter = function ScatterTooltip({ data, xLabel, yLabel, xFormat, yFormat, sizeLabel }) {
  if (!data) return null
  return (
    <div style={tooltipStyle}>
      {data.label && (
        <div className="text-[13px] font-sans font-medium text-[var(--color-text-primary)] mb-2 pb-1.5
                        border-b border-[var(--color-border-tertiary)]">
          {data.label}
        </div>
      )}
      {[
        { label: xLabel ?? 'X', value: xFormat ? xFormat(data.x) : data.x },
        { label: yLabel ?? 'Y', value: yFormat ? yFormat(data.y) : data.y },
        sizeLabel && data.size != null
          ? { label: sizeLabel, value: data.size?.toLocaleString() }
          : null,
      ].filter(Boolean).map(row => (
        <div key={row.label} className="flex items-center justify-between gap-6 mt-1.5">
          <span className="text-[13px] text-[var(--color-text-secondary)] font-sans">{row.label}</span>
          <span className="text-[13px] font-mono font-medium tabular-nums text-[var(--color-text-primary)]">
            {row.value}
          </span>
        </div>
      ))}
    </div>
  )
}

// ─── FKTooltip.Box — for canvas charts that manage their own hover state ──────
// Positioned absolutely at {x, y} using pointer-events:none
FKTooltip.Box = function TooltipBox({ children, x, y, style }) {
  return (
    <div style={{
      ...tooltipStyle,
      position:      'absolute',
      pointerEvents: 'none',
      left:          (x ?? 0) + 12,
      top:           y ?? 0,
      transform:     'translateY(-50%)',
      zIndex:        50,
      ...style,
    }}>
      {children}
    </div>
  )
}

// ─── FKTooltip.Header + FKTooltip.Row — building blocks for Box tooltips ─────
FKTooltip.Header = function TooltipHeader({ children }) {
  return (
    <div className="text-xs text-[var(--color-text-tertiary)] font-sans mb-2 pb-1.5
                    border-b border-[var(--color-border-tertiary)]">
      {children}
    </div>
  )
}

FKTooltip.Row = function TooltipRow({ color, label, value }) {
  return (
    <div className="flex items-center justify-between gap-6 mt-1.5">
      <div className="flex items-center gap-2">
        {color && <span style={{ background: color }} className="w-2 h-2 rounded-full flex-shrink-0" />}
        <span className="text-[13px] text-[var(--color-text-secondary)] font-sans">{label}</span>
      </div>
      <span className="text-[13px] text-[var(--color-text-primary)] font-mono font-medium tabular-nums">
        {value}
      </span>
    </div>
  )
}
