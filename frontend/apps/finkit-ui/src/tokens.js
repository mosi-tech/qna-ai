// ─── FINKIT design tokens ───────────────────────────────────────────
// Import this everywhere. Never hardcode colors outside this file
// except where the spec explicitly states hardcoded hex (gain/loss/warn).

export const color = {
  gain:     '#16a34a',
  loss:     '#dc2626',
  warn:     '#d97706',
  gainBg:   'rgba(22,163,74,0.09)',
  lossBg:   'rgba(220,38,38,0.09)',
  series:   ['#6366f1', '#06b6d4', '#f59e0b', '#ec4899', '#10b981', '#94a3b8'],
  seriesBg: [
    'rgba(99,102,241,0.12)',
    'rgba(6,182,212,0.08)',
    'rgba(245,158,11,0.08)',
    'rgba(236,72,153,0.08)',
    'rgba(16,185,129,0.08)',
    'rgba(148,163,184,0.06)',
  ],
}

export const surface = {
  card:    'var(--color-background-primary)',
  raised:  'var(--color-background-secondary)',
  page:    'var(--color-background-tertiary)',
  border:  'var(--color-border-tertiary)',
  border2: 'var(--color-border-secondary)',
}

export const font = {
  sans: 'var(--font-sans)',
  mono: 'var(--font-mono)',
}

// Single source of truth for Recharts axis/grid/tooltip props
export const axisProps = {
  tick:     { fontSize: 10, fill: 'var(--color-text-tertiary)', fontFamily: 'var(--font-mono)' },
  axisLine: false,
  tickLine: false,
}

export const gridProps = {
  stroke:          'var(--color-border-tertiary)',
  strokeDasharray: '0',
  vertical:        false,
}

export const tooltipStyle = {
  background:   'var(--color-background-primary)',
  border:       '0.5px solid var(--color-border-secondary)',
  borderRadius: 8,
  padding:      '10px 12px',
  fontSize:     12,
  fontFamily:   'var(--font-mono)',
  boxShadow:    '0 4px 16px rgba(0,0,0,0.08)',
}

// Default range selector options — charts use this unless overridden
export const defaultRangeOptions = ['1M', '3M', '6M', '1Y', '3Y', '5Y', 'ALL']

/**
 * Resolve a colorRule string token → CSS color string.
 * 'gain' | 'loss' | 'warn' | 'neutral' | any CSS string
 */
export function resolveColor(token) {
  if (!token) return 'var(--color-text-primary)'
  if (token === 'gain')    return color.gain
  if (token === 'loss')    return color.loss
  if (token === 'warn')    return color.warn
  if (token === 'neutral') return 'var(--color-text-secondary)'
  return token
}
