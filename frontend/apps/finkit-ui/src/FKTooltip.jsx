import React from 'react'
import { tooltipStyle } from './tokens.js'

// ─── FKTooltip — universal custom tooltip for all FK charts ──────────────────
//
// Usage with Recharts:
//   <Tooltip content={<FKTooltip xFormat={formatDate} valueFormat={formatUSD} />} />
//
// For canvas charts (FKScatterChart, FKBulletChart, FKRangeChart):
//   render <FKTooltip.Box> positioned absolutely at {x, y} with items you build manually

export function FKTooltip({ xFormat, valueFormat, colorMap, active, payload, label }) {
  if (!active || !payload?.length) return null

  return (
    <div style={tooltipStyle}>
      {/* Header: x-axis value */}
      <div className="text-[11px] font-mono mb-2 pb-1.5 border-b border-[var(--color-border-tertiary)]"
        style={{ color: 'var(--color-text-tertiary)' }}>
        {xFormat ? xFormat(label) : label}
      </div>

      {/* One row per series — filter out hidden/base bars */}
      {payload.filter(e => e.dataKey !== '_base' && e.dataKey !== '__hidden').map((entry, i) => (
        <div key={i} className="flex items-center justify-between gap-4 mt-1">
          <div className="flex items-center gap-1.5">
            <span
              style={{ background: colorMap?.[entry.dataKey] ?? entry.color }}
              className="inline-block w-2 h-2 rounded-full flex-shrink-0"
            />
            <span className="text-[11px] font-mono" style={{ color: 'var(--color-text-secondary)' }}>
              {entry.name ?? entry.dataKey}
            </span>
          </div>
          <span className="text-[11px] font-mono font-medium" style={{ color: 'var(--color-text-primary)' }}>
            {valueFormat ? valueFormat(entry.value) : entry.value?.toLocaleString?.() ?? entry.value}
          </span>
        </div>
      ))}
    </div>
  )
}

// ─── FKTooltip.Box — for canvas charts that manage their own hover state ─────
// Wrap around manually built tooltip content, positioned absolutely
FKTooltip.Box = function TooltipBox({ children, style }) {
  return (
    <div style={{ ...tooltipStyle, position: 'absolute', pointerEvents: 'none', zIndex: 50, ...style }}>
      {children}
    </div>
  )
}

// ─── FKTooltip.Header — reusable date/category header row ────────────────────
FKTooltip.Header = function TooltipHeader({ children }) {
  return (
    <div className="text-[11px] font-mono mb-2 pb-1.5 border-b border-[var(--color-border-tertiary)]"
      style={{ color: 'var(--color-text-tertiary)' }}>
      {children}
    </div>
  )
}

// ─── FKTooltip.Row — reusable value row with color dot, label, value ─────────
FKTooltip.Row = function TooltipRow({ color, label, value }) {
  return (
    <div className="flex items-center justify-between gap-4 mt-1">
      <div className="flex items-center gap-1.5">
        {color && (
          <span style={{ background: color }} className="inline-block w-2 h-2 rounded-full flex-shrink-0" />
        )}
        <span className="text-[11px] font-mono" style={{ color: 'var(--color-text-secondary)' }}>{label}</span>
      </div>
      <span className="text-[11px] font-mono font-medium" style={{ color: 'var(--color-text-primary)' }}>
        {value}
      </span>
    </div>
  )
}
