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

// Recharts axis props — numeric/date axes (mono ticks)
export const axisProps = {
  tick:     { fontSize: 12, fill: 'var(--color-text-tertiary)', fontFamily: 'var(--font-mono)' },
  axisLine: false,
  tickLine: false,
}

// Category axis props — label axes (tickers, sector names, month names → sans)
export const categoryAxisProps = {
  tick:     { fontSize: 12, fill: 'var(--color-text-tertiary)', fontFamily: 'var(--font-sans)' },
  axisLine: false,
  tickLine: false,
}

export const gridProps = {
  stroke:          'var(--color-border-tertiary)',
  strokeOpacity:   0.3,
  vertical:        false,
  strokeDasharray: '3 6',
}

export const tooltipStyle = {
  background:   'var(--color-background-primary)',
  border:       '1px solid var(--color-border-tertiary)',
  borderRadius: 10,
  padding:      '10px 14px',
  fontSize:     13,
  fontFamily:   'var(--font-sans)',
  boxShadow:    '0 8px 24px rgba(0,0,0,0.08)',
  outline:      'none',
  minWidth:     140,
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
