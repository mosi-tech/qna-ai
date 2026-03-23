import React from 'react'
import { color } from './tokens.js'

// ─── FKBadge ─────────────────────────────────────────────────────────────────
// variant: 'gain' | 'loss' | 'warn' | 'neutral' | 'info'
const BADGE_VARIANTS = {
  gain:    { bg: color.gainBg,              text: color.gain },
  loss:    { bg: color.lossBg,              text: color.loss },
  warn:    { bg: 'rgba(217,119,6,0.09)',    text: color.warn },
  neutral: { bg: 'var(--color-background-secondary)', text: 'var(--color-text-secondary)' },
  info:    { bg: 'rgba(99,102,241,0.09)',   text: '#6366f1' },
}

export function FKBadge({ children, variant = 'neutral', style }) {
  const v = BADGE_VARIANTS[variant] || BADGE_VARIANTS.neutral
  return (
    <span
      className="inline-flex items-center rounded-full text-[10px] font-medium leading-none"
      style={{
        padding:    '3px 8px',
        background: v.bg,
        color:      v.text,
        ...style,
      }}
    >
      {children}
    </span>
  )
}

// ─── FKDelta ──────────────────────────────────────────────────────────────────
// Renders ▲/▼ + value with gain/loss color
export function FKDelta({ value, decimals = 2, suffix = '%' }) {
  const isPos  = value >= 0
  const arrow  = isPos ? '▲' : '▼'
  const fill   = isPos ? color.gain : color.loss
  const abs    = Math.abs(value)
  return (
    <span
      className="inline-flex items-center gap-0.5 text-[11px] font-medium font-mono"
      style={{ color: fill }}
    >
      {arrow} {abs.toFixed(decimals)}{suffix}
    </span>
  )
}

// ─── FKSparkline ─────────────────────────────────────────────────────────────
// Pure SVG inline sparkline — no Recharts.
// Auto-detects direction from first/last value for color.
export function FKSparkline({ data = [], width = 72, height = 28, positive, showArea }) {
  if (!data || data.length < 2) return null
  const mn    = Math.min(...data)
  const mx    = Math.max(...data)
  const range = mx - mn || 1
  const pts   = data.map((v, i) => ({
    x: (i / (data.length - 1)) * width,
    y: height - ((v - mn) / range) * (height - 2) - 1,
  }))
  const isPos      = positive !== undefined ? positive : data[data.length - 1] >= data[0]
  const strokeCol  = isPos ? color.gain : color.loss
  const fillCol    = isPos ? color.gainBg : color.lossBg
  const linePath   = pts.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ')
  const areaPath   = linePath + ` L${width},${height} L0,${height} Z`

  return (
    <svg width={width} height={height} style={{ display: 'block', overflow: 'visible' }}>
      {showArea && <path d={areaPath} fill={fillCol} />}
      <path d={linePath} fill="none" stroke={strokeCol} strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

// ─── FKRangeSelector ─────────────────────────────────────────────────────────
// Period tab bar: ["1M","3M","6M","1Y"] style
export function FKRangeSelector({ options = ['1M', '3M', '6M', '1Y'], value, onChange }) {
  return (
    <div className="flex gap-0.5">
      {options.map(opt => {
        const active = opt === value
        return (
          <button
            key={opt}
            onClick={() => onChange?.(opt)}
            className="px-2 rounded transition-colors text-[10px] font-mono leading-none"
            style={{
              padding:    '4px 8px',
              background: active ? 'var(--color-background-secondary)' : 'transparent',
              color:      active ? 'var(--color-text-primary)'         : 'var(--color-text-tertiary)',
              border:     active ? '0.5px solid var(--color-border-secondary)' : '0.5px solid transparent',
              cursor:     'pointer',
            }}
          >
            {opt}
          </button>
        )
      })}
    </div>
  )
}

// ─── FKStatStrip ─────────────────────────────────────────────────────────────
// Horizontal key-value bar docked below charts
// stats = [{ label, value, color? }]
export function FKStatStrip({ stats = [] }) {
  return (
    <div
      className="flex items-center flex-wrap gap-x-6 gap-y-2"
      style={{
        padding:    '10px 20px',
        borderTop:  '0.5px solid var(--color-border-tertiary)',
        background: 'var(--color-background-secondary)',
      }}
    >
      {stats.map((s, i) => (
        <div key={i} className="flex flex-col gap-0.5">
          <span
            className="text-[9px] uppercase tracking-widest"
            style={{ color: 'var(--color-text-tertiary)' }}
          >
            {s.label}
          </span>
          <span
            className="text-[12px] font-mono font-medium"
            style={{ color: s.color || 'var(--color-text-primary)' }}
          >
            {s.value}
          </span>
        </div>
      ))}
    </div>
  )
}
