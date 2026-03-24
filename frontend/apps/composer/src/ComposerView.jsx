import React, { useState, useCallback } from 'react'

// Row role → allowed column width combos (mirrors UI Planner rules)
const ROLE_WIDTHS = {
  headline:   [['full']],
  primary:    [['full'], ['2/3', '1/3'], ['3/4', '1/4']],
  supporting: [['1/2', '1/2'], ['1/3', '1/3', '1/3'], ['2/3', '1/3'], ['1/2', '1/4', '1/4']],
  detail:     [['full']],
}

// Width → Tailwind col-span
const COL_SPAN = {
  'full': 'col-span-12', '3/4': 'col-span-9', '2/3': 'col-span-8',
  '1/2': 'col-span-6',  '1/3': 'col-span-4', '1/4': 'col-span-3',
}

// Role labels
const ROLE_META = {
  headline:   { label: 'Headline',   hint: 'Full-width KPI row — FKMetricGrid',    color: 'bg-violet-500' },
  primary:    { label: 'Primary',    hint: 'Main visual that answers the question', color: 'bg-blue-500' },
  supporting: { label: 'Supporting', hint: 'Context / breakdown blocks',            color: 'bg-indigo-400' },
  detail:     { label: 'Detail',     hint: 'Dense table or ranked list',            color: 'bg-slate-400' },
}

function uid() { return Math.random().toString(36).slice(2, 7) }

function makeRow(role) {
  const widths = ROLE_WIDTHS[role][0]
  return {
    id: uid(),
    role,
    widthCombo: 0,
    columns: widths.map(w => ({ id: uid(), width: w, componentId: null })),
  }
}

const DEFAULT_ROWS = [makeRow('headline'), makeRow('primary'), makeRow('supporting')]

export default function ComposerView({ registry, approvals }) {
  const [rows, setRows] = useState(DEFAULT_ROWS)

  // Get all supported components for a width, with approval status
  const componentsForWidth = useCallback((width) => {
    return registry
      .filter(c => c.supportedWidths.includes(width))
      .map(c => ({ ...c, approved: (approvals[c.id] || []).includes(width) }))
  }, [registry, approvals])

  // Keep for randomize — only pick approved
  const approvedForWidth = useCallback((width) => {
    return registry.filter(c =>
      c.supportedWidths.includes(width) &&
      (approvals[c.id] || []).includes(width)
    )
  }, [registry, approvals])

  const addRow = (role) => {
    setRows(prev => [...prev, makeRow(role)])
  }

  const removeRow = (rowId) => {
    setRows(prev => prev.filter(r => r.id !== rowId))
  }

  const setWidthCombo = (rowId, comboIdx) => {
    setRows(prev => prev.map(r => {
      if (r.id !== rowId) return r
      const widths = ROLE_WIDTHS[r.role][comboIdx]
      return {
        ...r,
        widthCombo: comboIdx,
        columns: widths.map((w, i) => ({
          id: r.columns[i]?.id || uid(),
          width: w,
          componentId: r.columns[i]?.componentId || null,
        })),
      }
    }))
  }

  const setColumnComponent = (rowId, colId, componentId) => {
    setRows(prev => prev.map(r =>
      r.id !== rowId ? r : {
        ...r,
        columns: r.columns.map(c =>
          c.id !== colId ? c : { ...c, componentId }
        ),
      }
    ))
  }

  const randomize = () => {
    setRows(prev => prev.map(r => ({
      ...r,
      columns: r.columns.map(col => {
        const options = approvedForWidth(col.width)
        const picked = options[Math.floor(Math.random() * options.length)]
        return { ...col, componentId: picked?.id || null }
      }),
    })))
  }

  return (
    <div className="flex h-full min-h-0">
      {/* Left panel: row builder */}
      <aside className="w-64 flex-shrink-0 border-r border-[var(--color-border-secondary)] bg-[var(--color-background-primary)] overflow-y-auto flex flex-col">
        <div className="p-4 border-b border-[var(--color-border-tertiary)]">
          <div className="text-xs font-semibold text-[var(--color-text-primary)] mb-0.5">Row Builder</div>
          <div className="text-xs text-[var(--color-text-tertiary)]">Add rows and assign components</div>
        </div>

        {/* Row list */}
        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {rows.map((row, rowIdx) => (
            <RowControl
              key={row.id}
              row={row}
              rowIdx={rowIdx}
              componentsForWidth={componentsForWidth}
              registry={registry}
              onRemove={() => removeRow(row.id)}
              onWidthCombo={(idx) => setWidthCombo(row.id, idx)}
              onComponent={(colId, cId) => setColumnComponent(row.id, colId, cId)}
            />
          ))}
        </div>

        {/* Add row buttons */}
        <div className="p-3 border-t border-[var(--color-border-tertiary)] space-y-1.5">
          <div className="text-[10px] uppercase tracking-widest font-semibold text-[var(--color-text-tertiary)] mb-1">Add Row</div>
          {Object.entries(ROLE_META).map(([role, meta]) => (
            <button
              key={role}
              onClick={() => addRow(role)}
              className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs text-[var(--color-text-secondary)] hover:bg-[var(--color-background-secondary)] transition-colors text-left"
            >
              <span className={`w-2 h-2 rounded-full ${meta.color} flex-shrink-0`} />
              {meta.label}
            </button>
          ))}
          <button
            onClick={randomize}
            className="w-full mt-2 px-2.5 py-1.5 rounded-lg text-xs font-medium text-white bg-indigo-600 hover:bg-indigo-700 transition-colors"
          >
            Randomize
          </button>
        </div>
      </aside>

      {/* Right: live preview */}
      <div className="flex-1 overflow-y-auto p-6 bg-[var(--color-background-secondary)]">
        <div className="max-w-5xl mx-auto">
          <div className="text-xs font-semibold text-[var(--color-text-tertiary)] uppercase tracking-wide mb-4">
            Dashboard Preview
          </div>

          {rows.length === 0 ? (
            <div className="flex items-center justify-center h-64 text-[var(--color-text-tertiary)] text-sm">
              Add rows using the left panel
            </div>
          ) : (
            <div className="space-y-4">
              {rows.map(row => (
                <DashboardRow
                  key={row.id}
                  row={row}
                  registry={registry}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// ─── Row control (in sidebar) ─────────────────────────────────────────────────

function RowControl({ row, rowIdx, componentsForWidth, registry, onRemove, onWidthCombo, onComponent }) {
  const meta   = ROLE_META[row.role]
  const combos = ROLE_WIDTHS[row.role]

  return (
    <div className="rounded-lg border border-[var(--color-border-secondary)] bg-[var(--color-background-secondary)] overflow-hidden">
      {/* Row header */}
      <div className="flex items-center gap-2 px-2.5 py-1.5 bg-[var(--color-background-primary)] border-b border-[var(--color-border-tertiary)]">
        <span className={`w-2 h-2 rounded-full ${meta.color} flex-shrink-0`} />
        <span className="text-xs font-medium text-[var(--color-text-primary)] flex-1">{meta.label}</span>
        <span className="text-[10px] text-[var(--color-text-tertiary)]">Row {rowIdx + 1}</span>
        <button onClick={onRemove} className="text-[var(--color-text-tertiary)] hover:text-red-500 transition text-xs ml-1">✕</button>
      </div>

      <div className="p-2 space-y-1.5">
        {/* Width combo selector */}
        {combos.length > 1 && (
          <div>
            <div className="text-[10px] text-[var(--color-text-tertiary)] mb-1">Layout</div>
            <div className="flex gap-1 flex-wrap">
              {combos.map((combo, i) => (
                <button
                  key={i}
                  onClick={() => onWidthCombo(i)}
                  className={`px-1.5 py-0.5 rounded text-[10px] font-mono transition-colors ${
                    row.widthCombo === i
                      ? 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900 dark:text-indigo-300'
                      : 'bg-[var(--color-background-primary)] text-[var(--color-text-tertiary)] border border-[var(--color-border-secondary)]'
                  }`}
                >
                  {combo.join('+')}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Column selectors */}
        {row.columns.map(col => {
          const options = componentsForWidth(col.width)
          return (
            <div key={col.id}>
              <div className="text-[10px] text-[var(--color-text-tertiary)] mb-0.5 font-mono">{col.width}</div>
              <select
                value={col.componentId || ''}
                onChange={e => onComponent(col.id, e.target.value || null)}
                className="w-full text-xs rounded-md border border-[var(--color-border-secondary)] bg-[var(--color-background-primary)] text-[var(--color-text-primary)] px-2 py-1 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                <option value="">— select component —</option>
                {options.map(c => (
                  <option key={c.id} value={c.id}>{c.approved ? c.name : `⚠ ${c.name}`}</option>
                ))}
              </select>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ─── Dashboard row (preview) ──────────────────────────────────────────────────

function DashboardRow({ row, registry }) {
  const meta = ROLE_META[row.role]
  return (
    <div>
      {/* Role label */}
      <div className="flex items-center gap-1.5 mb-2">
        <span className={`w-1.5 h-1.5 rounded-full ${meta.color}`} />
        <span className="text-[10px] font-medium text-[var(--color-text-tertiary)] uppercase tracking-wide">{meta.label}</span>
      </div>
      <div className="grid grid-cols-12 gap-4">
        {row.columns.map(col => {
          const component = col.componentId ? registry.find(c => c.id === col.componentId) : null
          const C         = component?.component
          const props     = component?.sampleProps || {}
          return (
            <div key={col.id} className={COL_SPAN[col.width] || 'col-span-12'}>
              {C ? (
                <C {...props} />
              ) : (
                <EmptySlot width={col.width} role={row.role} />
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

function EmptySlot({ width, role }) {
  return (
    <div
      className="rounded-xl border-2 border-dashed border-[var(--color-border-secondary)] flex items-center justify-center text-[var(--color-text-tertiary)] text-xs"
      style={{ minHeight: role === 'headline' ? 100 : role === 'detail' ? 120 : 200 }}
    >
      <div className="text-center">
        <div className="font-mono text-[var(--color-border-primary)] text-lg mb-1">◫</div>
        <div>{width}</div>
      </div>
    </div>
  )
}
