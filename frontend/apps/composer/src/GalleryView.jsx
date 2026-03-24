import React, { useState } from 'react'
import { CATEGORIES, ALL_WIDTHS } from './fk-registry'
import ComponentPreview from './ComponentPreview'

export default function GalleryView({ registry, approvals, onToggle }) {
  const [activeCategory, setActiveCategory] = useState('All')
  const [selectedId, setSelectedId] = useState(null)

  const categories = ['All', ...CATEGORIES]
  const filtered = activeCategory === 'All'
    ? registry
    : registry.filter(c => c.category === activeCategory)

  const selected = selectedId ? registry.find(c => c.id === selectedId) : null

  return (
    <div className="flex h-full min-h-0">
      {/* Left: Component list */}
      <aside className="w-56 flex-shrink-0 border-r border-[var(--color-border-secondary)] bg-[var(--color-background-primary)] overflow-y-auto p-3">
        {/* Category filter */}
        <div className="mb-3">
          <div className="text-[10px] uppercase tracking-widest font-semibold text-[var(--color-text-tertiary)] mb-1.5 px-1">Category</div>
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`w-full text-left px-2.5 py-1.5 rounded-lg text-xs font-medium transition-colors mb-0.5 ${
                activeCategory === cat
                  ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300'
                  : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-background-secondary)]'
              }`}
            >
              {cat}
              <span className="ml-1 text-[var(--color-text-tertiary)] font-normal">
                ({cat === 'All' ? registry.length : registry.filter(c => c.category === cat).length})
              </span>
            </button>
          ))}
        </div>

        <div className="border-t border-[var(--color-border-tertiary)] pt-3">
          <div className="text-[10px] uppercase tracking-widest font-semibold text-[var(--color-text-tertiary)] mb-1.5 px-1">Components</div>
          {filtered.map(c => {
            const approved = approvals[c.id] || []
            const isSelected = selectedId === c.id
            return (
              <button
                key={c.id}
                onClick={() => setSelectedId(isSelected ? null : c.id)}
                className={`w-full text-left px-2.5 py-2 rounded-lg text-xs transition-colors mb-0.5 ${
                  isSelected
                    ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300'
                    : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-background-secondary)]'
                }`}
              >
                <div className="font-medium">{c.name}</div>
                <div className="text-[var(--color-text-tertiary)] font-normal mt-0.5">
                  {approved.length}/{c.supportedWidths.length} widths
                </div>
              </button>
            )
          })}
        </div>
      </aside>

      {/* Right: Preview area */}
      <div className="flex-1 overflow-y-auto p-6">
        {selected ? (
          <ComponentDetail
            component={selected}
            approvals={approvals[selected.id] || []}
            onToggle={onToggle}
          />
        ) : (
          <ComponentGrid
            components={filtered}
            approvals={approvals}
            onToggle={onToggle}
            onSelect={setSelectedId}
          />
        )}
      </div>
    </div>
  )
}

// ─── Component grid (overview) ────────────────────────────────────────────────

function ComponentGrid({ components, approvals, onToggle, onSelect }) {
  return (
    <div>
      <h2 className="text-base font-semibold text-[var(--color-text-primary)] mb-4">
        All Components
        <span className="ml-2 text-sm font-normal text-[var(--color-text-tertiary)]">
          — click a component to inspect at each width
        </span>
      </h2>
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
        {components.map(c => {
          const approved = approvals[c.id] || []
          return (
            <div
              key={c.id}
              className="bg-[var(--color-background-primary)] rounded-xl border border-[var(--color-border-secondary)] overflow-hidden hover:border-indigo-300 dark:hover:border-indigo-700 transition-colors cursor-pointer"
              onClick={() => onSelect(c.id)}
            >
              {/* Header */}
              <div className="flex items-start justify-between px-4 py-3 border-b border-[var(--color-border-tertiary)]">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-[var(--color-text-primary)]">{c.name}</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-[var(--color-background-tertiary)] text-[var(--color-text-tertiary)] font-medium uppercase tracking-wide">
                      {c.category}
                    </span>
                  </div>
                  <p className="text-xs text-[var(--color-text-secondary)] mt-0.5">{c.description}</p>
                </div>
                {/* Width approval pills */}
                <div className="flex items-center gap-1 flex-shrink-0 ml-3 flex-wrap justify-end">
                  {ALL_WIDTHS.map(w => {
                    const isApproved = approved.includes(w)
                    return (
                      <button
                        key={w}
                        onClick={e => { e.stopPropagation(); onToggle(c.id, w) }}
                        title={isApproved ? `Remove approval for ${w}` : `Approve for ${w}`}
                        className={`text-[10px] px-1.5 py-0.5 rounded-md font-mono font-medium transition-all ${
                          isApproved
                            ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950 dark:text-emerald-300 dark:border-emerald-800'
                            : 'bg-amber-50 text-amber-600 border border-amber-300 dark:bg-amber-950 dark:text-amber-400 dark:border-amber-800 hover:bg-amber-100'
                        }`}
                      >
                        {w}
                      </button>
                    )
                  })}
                </div>
              </div>

              {/* Preview */}
              <div className="p-4 pointer-events-none">
                <ComponentPreview component={c} width="full" height={200} />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ─── Component detail (per-width view) ────────────────────────────────────────

function ComponentDetail({ component, approvals, onToggle }) {
  const c = component

  return (
    <div>
      {/* Detail header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-1">
          <h2 className="text-lg font-semibold text-[var(--color-text-primary)]">{c.name}</h2>
          <span className="text-xs px-2 py-0.5 rounded-full bg-[var(--color-background-tertiary)] text-[var(--color-text-tertiary)] font-medium">
            {c.category}
          </span>
        </div>
        <p className="text-sm text-[var(--color-text-secondary)]">{c.description}</p>
        <div className="text-xs text-[var(--color-text-tertiary)] mt-1 font-mono">{c.id}</div>
      </div>

      {/* Per-width previews */}
      <div className="space-y-6">
        {ALL_WIDTHS.map(width => {
          const isApproved = approvals.includes(width)
          return (
            <div key={width} className="bg-[var(--color-background-primary)] rounded-xl border overflow-hidden transition-colors"
              style={{ borderColor: isApproved ? 'rgb(167 243 208)' : 'var(--color-border-secondary)' }}>
              {/* Width header */}
              <div className="flex items-center justify-between px-4 py-2.5 border-b border-[var(--color-border-tertiary)]">
                <div className="flex items-center gap-2.5">
                  <span className="font-mono text-sm font-semibold text-[var(--color-text-primary)]">{width}</span>
                  <WidthBar width={width} />
                </div>
                <label className="flex items-center gap-2 cursor-pointer">
                  <span className="text-xs text-[var(--color-text-secondary)]">
                    {isApproved ? 'Approved' : 'Not approved'}
                  </span>
                  <input
                    type="checkbox"
                    checked={isApproved}
                    onChange={() => onToggle(c.id, width)}
                    className="sr-only peer"
                  />
                  <div className={`relative w-8 h-4 rounded-full transition-colors ${
                    isApproved ? 'bg-emerald-500' : 'bg-amber-400'
                  }`}>
                    <div className={`absolute top-0.5 left-0.5 w-3 h-3 bg-white rounded-full shadow-sm transition-transform ${
                      isApproved ? 'translate-x-4' : ''
                    }`} />
                  </div>
                </label>
              </div>

              {/* Preview at this width */}
              <div className="p-4 bg-[var(--color-background-secondary)]">
                <WidthConstrainedPreview component={c} width={width} />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ─── Width bar visualisation ──────────────────────────────────────────────────

function WidthBar({ width }) {
  const pct = { full: 100, '3/4': 75, '2/3': 66.7, '1/2': 50, '1/3': 33.3, '1/4': 25 }[width] || 100
  return (
    <div className="h-2 w-20 bg-[var(--color-background-tertiary)] rounded-full overflow-hidden">
      <div className="h-full bg-indigo-400 rounded-full" style={{ width: `${pct}%` }} />
    </div>
  )
}

// ─── Constrained preview at a given width ─────────────────────────────────────

function WidthConstrainedPreview({ component, width }) {
  const pct = { full: 100, '3/4': 75, '2/3': 66.7, '1/2': 50, '1/3': 33.3, '1/4': 25 }[width] || 100
  const C = component.component
  const props = component.sampleProps
  return (
    <div style={{ width: `${pct}%`, minWidth: 180 }}>
      <C {...props} />
    </div>
  )
}

export { WidthConstrainedPreview }
