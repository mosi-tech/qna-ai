import React, { useState, useMemo, useEffect, useRef } from 'react'
import { FKCard, FKCardHeader } from './FKCard.jsx'
import { FKBadge } from './FKSparkline.jsx'
import { FKTooltip } from './FKTooltip.jsx'

// ─── Sample data ─────────────────────────────────────────────────────────────
const MONTHS   = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
const YEARS    = ['2021','2022','2023','2024']
function makeSampleData() {
  return MONTHS.flatMap(m => YEARS.map(y => ({
    month: m, year: y,
    return_pct: parseFloat((Math.random() * 12 - 4).toFixed(2)),
  })))
}
const SAMPLE_DATA = makeSampleData()

// ─── Dark-mode detector ───────────────────────────────────────────────────────
function useIsDark() {
  const [isDark, setIsDark] = useState(() => document.documentElement.classList.contains('dark'))
  useEffect(() => {
    const obs = new MutationObserver(() =>
      setIsDark(document.documentElement.classList.contains('dark'))
    )
    obs.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] })
    return () => obs.disconnect()
  }, [])
  return isDark
}

// ─── Color scale helpers ──────────────────────────────────────────────────────
// Always white text. Solid hex colors — no rgba transparency so cells are
// clearly visible in both modes. Text-shadow on lighter tiers for legibility.

const SHADOW_LIGHT = '0 1px 3px rgba(0,0,0,0.35)'  // for lighter cell backgrounds
const SHADOW_NONE  = 'none'

// 4-step solid palettes  [low → high intensity]
const PALETTES = {
  // Light mode
  light: {
    green:  ['#4ade80', '#22c55e', '#16a34a', '#15803d'],
    red:    ['#fca5a5', '#f87171', '#ef4444', '#dc2626'],
    indigo: ['#a5b4fc', '#818cf8', '#6366f1', '#4f46e5'],
  },
  // Dark mode
  dark: {
    green:  ['#166534', '#16a34a', '#22c55e', '#4ade80'],
    red:    ['#991b1b', '#b91c1c', '#ef4444', '#fca5a5'],
    indigo: ['#312e81', '#4338ca', '#6366f1', '#818cf8'],
  },
}
// Lighter tiers (index 0–1) need a shadow to make white legible
const NEEDS_SHADOW = [true, true, false, false]

function pickTier(t) {
  if (t > 0.75) return 3
  if (t > 0.4)  return 2
  if (t > 0.15) return 1
  return 0
}

function divergingCell(v, min, max, isDark) {
  const abs    = Math.max(Math.abs(min), Math.abs(max)) || 1
  const t      = Math.min(Math.abs(v) / abs, 1)
  const tier   = pickTier(t)
  const mode   = isDark ? 'dark' : 'light'
  const colors = v >= 0 ? PALETTES[mode].green : PALETTES[mode].red
  return { bg: colors[tier], text: '#fff', shadow: NEEDS_SHADOW[tier] ? SHADOW_LIGHT : SHADOW_NONE }
}

function sequentialCell(v, min, max, isDark) {
  const t      = (v - min) / ((max - min) || 1)
  const tier   = pickTier(t)
  const colors = PALETTES[isDark ? 'dark' : 'light'].indigo
  return { bg: colors[tier], text: '#fff', shadow: NEEDS_SHADOW[tier] ? SHADOW_LIGHT : SHADOW_NONE }
}

function gainOnlyCell(v, min, max, isDark) {
  const t      = (v - min) / ((max - min) || 1)
  const tier   = pickTier(t)
  const colors = PALETTES[isDark ? 'dark' : 'light'].green
  return { bg: colors[tier], text: '#fff', shadow: NEEDS_SHADOW[tier] ? SHADOW_LIGHT : SHADOW_NONE }
}

function getCellStyle(v, min, max, scale, isDark) {
  if (scale === 'sequential') return sequentialCell(v, min, max, isDark)
  if (scale === 'gain-only')  return gainOnlyCell(v, min, max, isDark)
  return divergingCell(v, min, max, isDark)
}

// ─── Default tooltip content ──────────────────────────────────────────────────
function DefaultTooltipContent({ row, col, value, fmtVal, rowKey, colKey }) {
  return (
    <>
      <FKTooltip.Header>{row} · {col}</FKTooltip.Header>
      <FKTooltip.Row label={`${rowKey} / ${colKey}`} value={fmtVal(value)} />
    </>
  )
}

// ─── FKHeatGrid ───────────────────────────────────────────────────────────────
export function FKHeatGrid({
  data,
  rowKey        = 'month',
  colKey        = 'year',
  valueKey      = 'return_pct',
  colorScale    = 'diverging',
  colorDomain,
  showValues    = true,
  valueFormat,
  shape         = 'square',
  cellSize,
  cellRadius    = 6,
  periodKey,
  periods,
  defaultPeriod,
  // tooltip: false = no tooltip, true = default, function(cell) = custom content
  tooltip       = true,
  title,
  subtitle,
  badge,
  stats,
}) {
  const resolvedData = data || SAMPLE_DATA
  const isDark       = useIsDark()
  const [period, setPeriod] = useState(defaultPeriod || periods?.[0])
  const fmtVal = valueFormat || (v => `${v?.toFixed(1)}%`)

  // Hover state for custom tooltip
  const [hovered, setHovered] = useState(null)  // { x, y, row, col, value }
  const containerRef = useRef(null)

  const filtered = periodKey && period
    ? resolvedData.filter(r => r[periodKey] === period)
    : resolvedData

  const { rows, cols, grid, min, max } = useMemo(() => {
    const rowSet = [...new Set(filtered.map(r => r[rowKey]))]
    const colSet = [...new Set(filtered.map(r => r[colKey]))]

    const MONTH_ORDER = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    const sortedRows = rowSet.sort((a, b) => {
      const ai = MONTH_ORDER.indexOf(a)
      const bi = MONTH_ORDER.indexOf(b)
      if (ai !== -1 && bi !== -1) return ai - bi
      return a.localeCompare(b)
    })
    const sortedCols = colSet.sort((a, b) => a.localeCompare(b))

    const map = {}
    filtered.forEach(r => { map[`${r[rowKey]}_${r[colKey]}`] = r[valueKey] })

    const allVals = filtered.map(r => r[valueKey]).filter(v => v != null)
    const [mn, mx] = colorDomain || [Math.min(...allVals), Math.max(...allVals)]

    return { rows: sortedRows, cols: sortedCols, grid: map, min: mn, max: mx }
  }, [filtered, rowKey, colKey, valueKey, colorDomain])

  const effectiveCellSize = cellSize || Math.max(36, Math.min(64, Math.floor(540 / Math.max(cols.length, 1))))

  function handleMouseEnter(e, row, col, v) {
    if (!tooltip) return
    const rect = containerRef.current?.getBoundingClientRect()
    const cellRect = e.currentTarget.getBoundingClientRect()
    setHovered({
      x: cellRect.left - (rect?.left ?? 0) + cellRect.width / 2,
      y: cellRect.top  - (rect?.top  ?? 0),
      row, col, value: v,
    })
  }
  function handleMouseLeave() { setHovered(null) }

  return (
    <FKCard>
      <FKCardHeader
        title={title}
        subtitle={subtitle}
        actions={
          periods ? (
            <div className="flex gap-0.5">
              {periods.map(p => (
                <button
                  key={p}
                  onClick={() => setPeriod(p)}
                  className="text-[12px] font-sans rounded"
                  style={{
                    padding: '3px 7px',
                    background: p === period ? 'var(--color-background-secondary)' : 'transparent',
                    color: p === period ? 'var(--color-text-primary)' : 'var(--color-text-tertiary)',
                    border: '0.5px solid ' + (p === period ? 'var(--color-border-secondary)' : 'transparent'),
                    cursor: 'pointer',
                  }}
                >
                  {p}
                </button>
              ))}
            </div>
          ) : badge ? <FKBadge variant="neutral">{badge}</FKBadge> : null
        }
      />

      <div ref={containerRef} style={{ padding: '12px 20px 16px', overflowX: 'auto', position: 'relative' }}>
        <table style={{ borderCollapse: 'separate', borderSpacing: 3 }}>
          <thead>
            <tr>
              <th style={{ width: 52 }} />
              {cols.map(c => (
                <th key={c} style={{ fontSize: 12, fontFamily: 'var(--font-sans)', fontWeight: 500, color: 'var(--color-text-tertiary)', textAlign: 'center', paddingBottom: 4, width: effectiveCellSize }}>
                  {c}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map(row => (
              <tr key={row}>
                <td style={{ fontSize: 12, fontFamily: 'var(--font-sans)', color: 'var(--color-text-tertiary)', paddingRight: 8, whiteSpace: 'nowrap', textAlign: 'right' }}>
                  {row}
                </td>
                {cols.map(col => {
                  const v  = grid[`${row}_${col}`]
                  const cs = v != null
                    ? getCellStyle(v, min, max, colorScale, isDark)
                    : { bg: 'var(--color-background-secondary)', text: 'var(--color-text-tertiary)', shadow: SHADOW_NONE }
                  return (
                    <td key={col}>
                      <div
                        style={{
                          width:          effectiveCellSize,
                          height:         effectiveCellSize,
                          background:     cs.bg,
                          borderRadius:   shape === 'circle' ? '50%' : cellRadius,
                          display:        'flex',
                          alignItems:     'center',
                          justifyContent: 'center',
                          fontSize:       11,
                          fontFamily:     'var(--font-mono)',
                          fontWeight:     600,
                          color:          cs.text,
                          textShadow:     cs.shadow,
                          cursor:         'default',
                          transition:     'opacity 0.15s',
                        }}
                        onMouseEnter={e => handleMouseEnter(e, row, col, v)}
                        onMouseLeave={handleMouseLeave}
                      >
                        {showValues && v != null && effectiveCellSize > 32
                          ? fmtVal(v)
                          : null}
                      </div>
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>

        {/* Color legend */}
        <div style={{ marginTop: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 12, fontFamily: 'var(--font-sans)', color: 'var(--color-text-tertiary)' }}>
            {fmtVal(min)}
          </span>
          <div style={{
            flex: 1,
            height: 5,
            borderRadius: 3,
            background: colorScale === 'diverging'
              ? (isDark
                  ? 'linear-gradient(to right, #991b1b, #b91c1c 35%, #166534 65%, #22c55e)'
                  : 'linear-gradient(to right, #dc2626, #fca5a5 35%, #4ade80 65%, #15803d)')
              : (isDark
                  ? 'linear-gradient(to right, #312e81, #6366f1, #818cf8)'
                  : 'linear-gradient(to right, #a5b4fc, #6366f1, #4f46e5)'),
          }} />
          <span style={{ fontSize: 12, fontFamily: 'var(--font-sans)', color: 'var(--color-text-tertiary)' }}>
            {fmtVal(max)}
          </span>
        </div>

        {/* Tooltip */}
        {tooltip && hovered && hovered.value != null && (
          <FKTooltip.Box x={hovered.x} y={hovered.y} style={{ transform: 'translate(-50%, -100%) translateY(-8px)' }}>
            {typeof tooltip === 'function'
              ? tooltip({ row: hovered.row, col: hovered.col, value: hovered.value })
              : <DefaultTooltipContent
                  row={hovered.row}
                  col={hovered.col}
                  value={hovered.value}
                  fmtVal={fmtVal}
                  rowKey={rowKey}
                  colKey={colKey}
                />
            }
          </FKTooltip.Box>
        )}
      </div>
    </FKCard>
  )
}
