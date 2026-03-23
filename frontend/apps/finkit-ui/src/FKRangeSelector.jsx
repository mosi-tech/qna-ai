import React, { useState, useMemo } from 'react'
import { defaultRangeOptions } from './tokens.js'

// ─── FKRangeSelector — period tab bar for time-series charts ─────────────────
export function FKRangeSelector({ options = defaultRangeOptions, value, onChange }) {
  return (
    <div className="flex items-center gap-0.5 bg-[var(--color-background-tertiary)] rounded-lg p-0.5">
      {options.map(opt => (
        <button
          key={opt}
          onClick={() => onChange?.(opt)}
          className={[
            'px-2.5 py-1 rounded-md text-[12px] font-sans font-medium transition-colors leading-none',
            value === opt
              ? 'bg-[var(--color-background-primary)] text-[var(--color-text-primary)] shadow-sm'
              : 'text-[var(--color-text-tertiary)] hover:text-[var(--color-text-secondary)]',
          ].join(' ')}
          style={{ border: 'none', cursor: 'pointer', background: value === opt ? undefined : 'transparent' }}
        >
          {opt}
        </button>
      ))}
    </div>
  )
}

// ─── filterByRange — slice data array by a range string ───────────────────────
// Measures back from the LATEST date in the dataset (not from today).
export function filterByRange(data, range, dateKey = 'date') {
  if (!data?.length || range === 'ALL') return data

  const dates  = data.map(d => new Date(d[dateKey]).getTime()).filter(Boolean)
  const latest = new Date(Math.max(...dates))
  const cutoff = new Date(latest)

  switch (range) {
    case '1W':  cutoff.setDate(latest.getDate() - 7);           break
    case '1M':  cutoff.setMonth(latest.getMonth() - 1);         break
    case '3M':  cutoff.setMonth(latest.getMonth() - 3);         break
    case '6M':  cutoff.setMonth(latest.getMonth() - 6);         break
    case '1Y':  cutoff.setFullYear(latest.getFullYear() - 1);   break
    case '2Y':  cutoff.setFullYear(latest.getFullYear() - 2);   break
    case '3Y':  cutoff.setFullYear(latest.getFullYear() - 3);   break
    case '5Y':  cutoff.setFullYear(latest.getFullYear() - 5);   break
    case '10Y': cutoff.setFullYear(latest.getFullYear() - 10);  break
    default:    return data
  }

  return data.filter(d => new Date(d[dateKey]) >= cutoff)
}

// ─── useRangeFilter — hook wiring range selector + filtered data ──────────────
export function useRangeFilter(data, defaultRange = '1Y', dateKey = 'date') {
  const [range, setRange] = useState(() => {
    if (!data?.length) return 'ALL'
    const filtered = filterByRange(data, defaultRange, dateKey)
    return filtered.length > 1 ? defaultRange : 'ALL'
  })

  const filteredData = useMemo(
    () => filterByRange(data, range, dateKey),
    [data, range, dateKey]
  )

  return { range, setRange, filteredData }
}
