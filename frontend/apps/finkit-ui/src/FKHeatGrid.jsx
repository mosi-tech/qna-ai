import React, { useState, useMemo } from 'react'
import { FKCard, FKCardHeader } from './FKCard.jsx'
import { FKBadge } from './FKSparkline.jsx'

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

// ─── Color scale helpers ──────────────────────────────────────────────────────
function divergingCell(v, min, max) {
  const abs = Math.max(Math.abs(min), Math.abs(max)) || 1
  const r   = Math.min(Math.abs(v) / abs, 1)
  if (v >= 0) {
    if (r > 0.75)  return { bg: 'rgba(22,163,74,0.55)',  text: '#166534' }
    if (r > 0.4)   return { bg: 'rgba(22,163,74,0.35)',  text: '#15803d' }
    if (r > 0.15)  return { bg: 'rgba(22,163,74,0.18)',  text: '#16a34a' }
    return           { bg: 'rgba(22,163,74,0.08)',  text: '#22c55e' }
  } else {
    if (r > 0.75)  return { bg: 'rgba(220,38,38,0.55)',  text: '#7f1d1d' }
    if (r > 0.4)   return { bg: 'rgba(220,38,38,0.35)',  text: '#b91c1c' }
    if (r > 0.15)  return { bg: 'rgba(220,38,38,0.18)',  text: '#dc2626' }
    return           { bg: 'rgba(220,38,38,0.08)',  text: '#ef4444' }
  }
}

function sequentialCell(v, min, max) {
  const r = (v - min) / ((max - min) || 1)
  const a = 0.08 + r * 0.7
  return { bg: `rgba(99,102,241,${a.toFixed(2)})`, text: r > 0.5 ? '#4338ca' : '#6366f1' }
}

function gainOnlyCell(v, min, max) {
  const r = (v - min) / ((max - min) || 1)
  const a = 0.08 + r * 0.7
  return { bg: `rgba(22,163,74,${a.toFixed(2)})`, text: r > 0.5 ? '#166534' : '#16a34a' }
}

function getCellStyle(v, min, max, scale) {
  if (scale === 'sequential') return sequentialCell(v, min, max)
  if (scale === 'gain-only')  return gainOnlyCell(v, min, max)
  return divergingCell(v, min, max)
}

// ─── FKHeatGrid (spec name: FKGridChart) ─────────────────────────────────────
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
  title,
  subtitle,
  badge,
  stats,
}) {
  const resolvedData = data || SAMPLE_DATA
  const [period, setPeriod] = useState(defaultPeriod || periods?.[0])
  const fmtVal = valueFormat || (v => `${v?.toFixed(1)}%`)

  const filtered = periodKey && period
    ? resolvedData.filter(r => r[periodKey] === period)
    : resolvedData

  const { rows, cols, grid, min, max } = useMemo(() => {
    const rowSet = [...new Set(filtered.map(r => r[rowKey]))]
    const colSet = [...new Set(filtered.map(r => r[colKey]))]

    // Sort rows: months in calendar order, else alphabetical
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

      <div style={{ padding: '12px 20px 16px', overflowX: 'auto' }}>
        <table style={{ borderCollapse: 'separate', borderSpacing: 3 }}>
          <thead>
            <tr>
              {/* Empty corner */}
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
                  const v = grid[`${row}_${col}`]
                  const cs = v != null ? getCellStyle(v, min, max, colorScale) : { bg: 'var(--color-background-secondary)', text: 'var(--color-text-tertiary)' }
                  return (
                    <td key={col}>
                      <div
                        title={v != null ? fmtVal(v) : '—'}
                        style={{
                          width:        effectiveCellSize,
                          height:       effectiveCellSize,
                          background:   cs.bg,
                          borderRadius: shape === 'circle' ? '50%' : cellRadius,
                          display:      'flex',
                          alignItems:   'center',
                          justifyContent: 'center',
                          fontSize:     12,
                          fontFamily:   'var(--font-mono)',
                          fontWeight:   500,
                          color:        cs.text,
                          cursor:       'default',
                          transition:   'opacity 0.15s',
                        }}
                        onMouseEnter={e => e.currentTarget.style.opacity = '0.75'}
                        onMouseLeave={e => e.currentTarget.style.opacity = '1'}
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
              ? 'linear-gradient(to right, rgba(220,38,38,0.55), rgba(220,38,38,0.08) 40%, rgba(22,163,74,0.08) 60%, rgba(22,163,74,0.55))'
              : 'linear-gradient(to right, rgba(99,102,241,0.08), rgba(99,102,241,0.78))',
          }} />
          <span style={{ fontSize: 12, fontFamily: 'var(--font-sans)', color: 'var(--color-text-tertiary)' }}>
            {fmtVal(max)}
          </span>
        </div>
      </div>
    </FKCard>
  )
}
