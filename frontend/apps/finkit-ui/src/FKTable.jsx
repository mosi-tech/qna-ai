import React, { useState, useMemo } from 'react'
import { FKCard, FKCardHeader } from './FKCard.jsx'
import { FKBadge } from './FKSparkline.jsx'
import { FKSparkline } from './FKSparkline.jsx'
import { color, resolveColor } from './tokens.js'

// ─── Sample data ──────────────────────────────────────────────────────────────
const SAMPLE_COLUMNS = [
  { key: 'ticker', label: 'Symbol' },
  { key: 'value',  label: 'Value',   align: 'right', mono: true, format: v => `$${v.toLocaleString()}` },
  { key: 'weight', label: 'Weight',  align: 'right', mono: true, format: v => `${v.toFixed(1)}%` },
  {
    key: 'return_pct', label: 'Return', align: 'right', mono: true,
    colorRule: v => v >= 0 ? 'gain' : 'loss',
    format:    v => `${v >= 0 ? '+' : ''}${v.toFixed(2)}%`,
  },
  { key: 'sector', label: 'Sector' },
]
const SAMPLE_ROWS = [
  { ticker: 'AAPL', value: 18240, weight: 19.3, return_pct:  1.78, sector: 'Technology' },
  { ticker: 'MSFT', value: 14820, weight: 15.7, return_pct:  0.92, sector: 'Technology' },
  { ticker: 'NVDA', value: 11940, weight: 12.6, return_pct:  3.21, sector: 'Technology' },
  { ticker: 'AMZN', value:  9610, weight: 10.2, return_pct: -0.44, sector: 'Consumer' },
  { ticker: 'GOOGL', value: 8250, weight:  8.7, return_pct:  0.65, sector: 'Technology' },
  { ticker: 'META',  value: 7120, weight:  7.5, return_pct:  2.14, sector: 'Technology' },
  { ticker: 'BRK.B', value: 6340, weight:  6.7, return_pct: -0.18, sector: 'Financials' },
  { ticker: 'JPM',   value: 5900, weight:  6.2, return_pct:  1.03, sector: 'Financials' },
]

// ─── Sort utility ─────────────────────────────────────────────────────────────
function sortRows(rows, col, dir) {
  if (!col) return rows
  return [...rows].sort((a, b) => {
    const av = a[col], bv = b[col]
    if (av == null) return 1
    if (bv == null) return -1
    const cmp = typeof av === 'string' ? av.localeCompare(bv) : av - bv
    return dir === 'asc' ? cmp : -cmp
  })
}

// ─── FKTable (spec: FKDataTable) ─────────────────────────────────────────────
export function FKTable({
  columns,
  rows,
  defaultSort,
  defaultDir    = 'desc',
  sparkKey,
  maxRows,
  stickyHeader  = false,
  onRowClick,
  pivotRow,
  pivotCol,
  pivotValue,
  title,
  subtitle,
  badge,
}) {
  // ── Pivot mode: derive columns + rows from data dynamically ────────────────
  const isPivot = pivotRow && pivotCol && pivotValue

  const { resolvedCols, resolvedRows } = useMemo(() => {
    if (!isPivot) return { resolvedCols: columns || SAMPLE_COLUMNS, resolvedRows: rows || SAMPLE_ROWS }
    const rawRows = rows || []
    const rowVals = [...new Set(rawRows.map(r => r[pivotRow]))]
    const colVals = [...new Set(rawRows.map(r => r[pivotCol]))]
    // Build cell lookup
    const lookup = {}
    rawRows.forEach(r => { lookup[`${r[pivotRow]}__${r[pivotCol]}`] = r[pivotValue] })
    // Derived columns: row-header column + one column per pivotCol value
    const derivedCols = [
      { key: '__pivotRow', label: pivotRow, sortable: false },
      ...colVals.map(cv => ({
        key:       `__col_${cv}`,
        label:     String(cv),
        align:     'right',
        mono:      true,
        sortable:  false,
        format:    v => v != null ? (typeof v === 'number' ? v.toFixed(2) : v) : '—',
        colorRule: v => typeof v === 'number' ? (v >= 0 ? 'gain' : 'loss') : null,
      })),
    ]
    // Derived rows: one per pivotRow value
    const derivedRows = rowVals.map(rv => {
      const rowObj = { __pivotRow: rv }
      colVals.forEach(cv => { rowObj[`__col_${cv}`] = lookup[`${rv}__${cv}`] ?? null })
      return rowObj
    })
    return { resolvedCols: derivedCols, resolvedRows: derivedRows }
  }, [isPivot, columns, rows, pivotRow, pivotCol, pivotValue])
  const [sortCol, setSortCol] = useState(defaultSort || null)
  const [sortDir, setSortDir] = useState(defaultDir)

  const sorted = useMemo(
    () => sortRows(resolvedRows, sortCol, sortDir),
    [resolvedRows, sortCol, sortDir]
  )

  const displayed  = maxRows ? sorted.slice(0, maxRows) : sorted
  const isHidden   = maxRows && sorted.length > maxRows

  function handleColClick(key, sortable) {
    if (sortable === false) return
    if (key === sortCol) setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    else { setSortCol(key); setSortDir('desc') }
  }

  const allCols = sparkKey
    ? [...resolvedCols, { key: '__spark', label: '', align: 'right', sortable: false }]
    : resolvedCols

  return (
    <FKCard>
      <FKCardHeader
        title={title}
        subtitle={subtitle}
        actions={badge ? <FKBadge variant="neutral">{badge}</FKBadge> : null}
      />
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr
              style={{
                background:   'var(--color-background-secondary)',
                position:     stickyHeader ? 'sticky' : undefined,
                top:          stickyHeader ? 0 : undefined,
                zIndex:       stickyHeader ? 1 : undefined,
              }}
            >
              {allCols.map(col => {
                const isActive  = col.key === sortCol
                const clickable = col.sortable !== false
                return (
                  <th
                    key={col.key}
                    onClick={() => handleColClick(col.key, col.sortable)}
                    style={{
                      padding:       '10px 16px',
                      textAlign:     col.align || 'left',
                      fontSize:      13,
                      fontFamily:    'var(--font-sans)',
                      fontWeight:    500,
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                      color:         isActive ? 'var(--color-text-primary)' : 'var(--color-text-tertiary)',
                      cursor:        clickable ? 'pointer' : 'default',
                      userSelect:    'none',
                      whiteSpace:    'nowrap',
                      width:         col.width,
                      borderBottom:  '0.5px solid var(--color-border-tertiary)',
                    }}
                  >
                    {col.label}
                    {isActive && (
                      <span style={{ marginLeft: 4, opacity: 0.6 }}>
                        {sortDir === 'asc' ? '↑' : '↓'}
                      </span>
                    )}
                  </th>
                )
              })}
            </tr>
          </thead>
          <tbody>
            {displayed.length === 0 && (
              <tr>
                <td
                  colSpan={allCols.length}
                  style={{ padding: 32, textAlign: 'center', color: 'var(--color-text-tertiary)', fontSize: 13 }}
                >
                  No data
                </td>
              </tr>
            )}
            {displayed.map((row, ri) => (
              <tr
                key={ri}
                onClick={() => onRowClick?.(row)}
                style={{ cursor: onRowClick ? 'pointer' : 'default', transition: 'background 0.1s' }}
                onMouseEnter={e => e.currentTarget.style.background = 'var(--color-background-secondary)'}
                onMouseLeave={e => e.currentTarget.style.background = ''}
              >
                {allCols.map(col => {
                  if (col.key === '__spark') {
                    const sparkData = row[sparkKey]
                    return (
                      <td key="__spark" style={{ padding: '8px 16px', textAlign: 'right' }}>
                        {sparkData && <FKSparkline data={sparkData} width={72} height={24} />}
                      </td>
                    )
                  }
                  const raw     = row[col.key]
                  const display = col.format ? col.format(raw, row) : raw
                  const token   = col.colorRule ? col.colorRule(raw, row) : null
                  const txtCol  = token ? resolveColor(token) : 'var(--color-text-primary)'
                  return (
                    <td
                      key={col.key}
                      style={{
                        padding:    '9px 16px',
                        textAlign:  col.align || 'left',
                        fontSize:   13,
                        fontFamily: col.mono ? 'var(--font-mono)' : 'var(--font-sans)',
                        color:      txtCol,
                        borderBottom: '0.5px solid var(--color-border-tertiary)',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {display}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {isHidden && (
        <div style={{ padding: '10px 16px', borderTop: '0.5px solid var(--color-border-tertiary)', fontSize: 12, color: 'var(--color-text-tertiary)' }}>
          Showing {displayed.length} of {sorted.length}
        </div>
      )}
    </FKCard>
  )
}
