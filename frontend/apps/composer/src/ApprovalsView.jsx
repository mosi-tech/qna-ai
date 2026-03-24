import React, { useState } from 'react'
import { ALL_WIDTHS, CATEGORIES } from './fk-registry'

export default function ApprovalsView({ registry, approvals, onToggle }) {
  const [activeCategory, setActiveCategory] = useState('All')

  const filtered = activeCategory === 'All'
    ? registry
    : registry.filter(c => c.category === activeCategory)

  const categories = ['All', ...CATEGORIES]

  const totalApproved = Object.values(approvals).reduce((n, ws) => n + ws.length, 0)
  const totalPossible = registry.reduce((n, c) => n + c.supportedWidths.length, 0)

  return (
    <div className="p-6">
      {/* Page header */}
      <div className="mb-5 flex items-end justify-between">
        <div>
          <h2 className="text-base font-semibold text-[var(--color-text-primary)]">Width Approvals</h2>
          <p className="text-sm text-[var(--color-text-secondary)] mt-0.5">
            Check which widths each component is visually approved for.
            These approvals constrain what the UI Planner can place in each layout slot.
          </p>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <div className="text-right">
            <div className="text-xl font-bold font-mono text-[var(--color-text-primary)]">{totalApproved}</div>
            <div className="text-xs text-[var(--color-text-tertiary)]">of {totalPossible} possible</div>
          </div>
          <ProgressArc value={totalApproved} max={totalPossible} />
        </div>
      </div>

      {/* Category tabs */}
      <div className="flex items-center gap-1 mb-4 flex-wrap">
        {categories.map(cat => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${
              activeCategory === cat
                ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300'
                : 'bg-[var(--color-background-primary)] text-[var(--color-text-secondary)] border border-[var(--color-border-secondary)] hover:border-slate-300'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="bg-[var(--color-background-primary)] rounded-xl border border-[var(--color-border-secondary)] overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-[var(--color-border-secondary)]">
              <th className="text-left px-4 py-2.5 text-xs font-semibold text-[var(--color-text-tertiary)] uppercase tracking-wide w-52">
                Component
              </th>
              <th className="text-left px-3 py-2.5 text-xs font-semibold text-[var(--color-text-tertiary)] uppercase tracking-wide w-20">
                Category
              </th>
              {ALL_WIDTHS.map(w => (
                <th key={w} className="text-center px-2 py-2.5 text-xs font-mono font-semibold text-[var(--color-text-secondary)]">
                  {w}
                </th>
              ))}
              <th className="text-center px-3 py-2.5 text-xs font-semibold text-[var(--color-text-tertiary)] uppercase tracking-wide">
                Score
              </th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((c, i) => {
              const approved  = approvals[c.id] || []
              const score     = approved.length
              const maxScore  = c.supportedWidths.length

              return (
                <tr
                  key={c.id}
                  className={`border-b border-[var(--color-border-tertiary)] transition-colors hover:bg-[var(--color-background-secondary)] ${
                    i % 2 === 0 ? '' : 'bg-[var(--color-background-secondary)] bg-opacity-40'
                  }`}
                >
                  {/* Name */}
                  <td className="px-4 py-2.5">
                    <div className="font-medium text-[var(--color-text-primary)] text-xs">{c.name}</div>
                    <div className="font-mono text-[10px] text-[var(--color-text-tertiary)] mt-0.5">{c.id}</div>
                  </td>

                  {/* Category */}
                  <td className="px-3 py-2.5">
                    <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-[var(--color-background-tertiary)] text-[var(--color-text-tertiary)] font-medium">
                      {c.category}
                    </span>
                  </td>

                  {/* Width checkboxes */}
                  {ALL_WIDTHS.map(w => {
                    const isSupported = c.supportedWidths.includes(w)
                    const isApproved  = approved.includes(w)
                    return (
                      <td key={w} className="px-2 py-2.5 text-center">
                        {isSupported ? (
                          <button
                            onClick={() => onToggle(c.id, w)}
                            title={isApproved ? `Revoke ${w} approval` : `Approve for ${w}`}
                            className={`w-5 h-5 rounded transition-all flex items-center justify-center mx-auto ${
                              isApproved
                                ? 'bg-emerald-500 text-white hover:bg-emerald-600'
                                : 'border-2 border-amber-400 text-amber-400 hover:bg-amber-50 dark:hover:bg-amber-950'
                            }`}
                          >
                            {isApproved ? (
                              <svg width="10" height="8" viewBox="0 0 10 8" fill="none">
                                <path d="M1 4L3.5 6.5L9 1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                              </svg>
                            ) : (
                              <svg width="8" height="8" viewBox="0 0 8 8" fill="none">
                                <path d="M1 1L7 7M7 1L1 7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
                              </svg>
                            )}
                          </button>
                        ) : (
                          <span className="text-[var(--color-border-secondary)] text-xs">—</span>
                        )}
                      </td>
                    )
                  })}

                  {/* Score */}
                  <td className="px-3 py-2.5 text-center">
                    <div className="flex items-center justify-center gap-1">
                      <span className={`text-xs font-mono font-semibold ${
                        score === 0 ? 'text-red-500' :
                        score === maxScore ? 'text-emerald-600' :
                        'text-amber-600'
                      }`}>
                        {score}/{maxScore}
                      </span>
                    </div>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Legend */}
      <div className="mt-3 flex items-center gap-5 text-xs text-[var(--color-text-tertiary)]">
        <div className="flex items-center gap-1.5">
          <div className="w-4 h-4 rounded bg-emerald-500 flex items-center justify-center">
            <svg width="8" height="6" viewBox="0 0 10 8" fill="none">
              <path d="M1 4L3.5 6.5L9 1" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          Approved
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-4 h-4 rounded border-2 border-amber-400 flex items-center justify-center text-amber-400">
            <svg width="8" height="8" viewBox="0 0 8 8" fill="none">
              <path d="M1 1L7 7M7 1L1 7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
          </div>
          Not approved (but supported)
        </div>
        <div className="flex items-center gap-1.5">
          <span>—</span>
          Not supported at this width
        </div>
      </div>
    </div>
  )
}

// Simple arc progress indicator
function ProgressArc({ value, max }) {
  const pct = max > 0 ? value / max : 0
  const r = 18
  const circ = 2 * Math.PI * r
  const dash = pct * circ
  return (
    <svg width="48" height="48" viewBox="0 0 48 48">
      <circle cx="24" cy="24" r={r} fill="none" stroke="var(--color-border-secondary)" strokeWidth="3" />
      <circle
        cx="24" cy="24" r={r}
        fill="none"
        stroke={pct >= 0.9 ? '#10b981' : pct >= 0.5 ? '#6366f1' : '#f59e0b'}
        strokeWidth="3"
        strokeDasharray={`${dash} ${circ - dash}`}
        strokeDashoffset={circ / 4}
        strokeLinecap="round"
      />
      <text x="24" y="28" textAnchor="middle" fontSize="10" fontFamily="var(--font-mono)" fill="var(--color-text-secondary)" fontWeight="600">
        {Math.round(pct * 100)}%
      </text>
    </svg>
  )
}
