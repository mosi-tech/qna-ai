import React from 'react'
import { defaultRangeOptions } from './tokens.js'

// ─── FKRangeSelector — period tab bar for time-series charts ─────────────────
//
// Usage:
//   <FKRangeSelector options={['1M','3M','1Y','5Y','ALL']} value={range} onChange={setRange} />
//
// Rules:
//   - Sits in the top-right of the card header, inline with the title
//   - Active tab: bg-[var(--color-background-primary)] + shadow
//   - Inactive: transparent, tertiary text, hover to secondary
//   - Use `defaultRangeOptions` from tokens when options not provided

export function FKRangeSelector({ options = defaultRangeOptions, value, onChange }) {
  return (
    <div
      className="flex items-center gap-0.5 rounded-md p-0.5"
      style={{ background: 'var(--color-background-tertiary)' }}
    >
      {options.map(opt => (
        <button
          key={opt}
          onClick={() => onChange?.(opt)}
          className={[
            'px-2.5 py-1 rounded text-[11px] font-mono font-medium transition-colors leading-none',
            value === opt
              ? 'shadow-sm'
              : 'hover:text-[var(--color-text-secondary)]',
          ].join(' ')}
          style={{
            background: value === opt ? 'var(--color-background-primary)' : 'transparent',
            color:      value === opt ? 'var(--color-text-primary)'       : 'var(--color-text-tertiary)',
            border:     'none',
            cursor:     'pointer',
          }}
        >
          {opt}
        </button>
      ))}
    </div>
  )
}
