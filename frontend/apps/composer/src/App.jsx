import React, { useState, useEffect } from 'react'
import GalleryView from './GalleryView'
import ApprovalsView from './ApprovalsView'
import ComposerView from './ComposerView'
import { FK_REGISTRY, DEFAULT_APPROVALS } from './fk-registry'

const STORAGE_KEY = 'fk_approvals_v2'

export default function App() {
  const [tab, setTab] = useState('gallery')
  const [dark, setDark] = useState(false)

  const [approvals, setApprovals] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      return saved ? JSON.parse(saved) : DEFAULT_APPROVALS
    } catch {
      return DEFAULT_APPROVALS
    }
  })

  // Persist approvals
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(approvals))
  }, [approvals])

  // Apply dark mode to <html>
  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
  }, [dark])

  const toggleApproval = (componentId, width) => {
    setApprovals(prev => {
      const current = prev[componentId] || []
      const has = current.includes(width)
      return {
        ...prev,
        [componentId]: has ? current.filter(w => w !== width) : [...current, width],
      }
    })
  }

  const exportApprovals = () => {
    const clean = Object.fromEntries(
      Object.entries(approvals).filter(([, widths]) => widths.length > 0)
    )
    const blob = new Blob([JSON.stringify(clean, null, 2)], { type: 'application/json' })
    const url  = URL.createObjectURL(blob)
    const a    = Object.assign(document.createElement('a'), { href: url, download: 'fk_approvals.json' })
    a.click()
    URL.revokeObjectURL(url)
  }

  const resetApprovals = () => {
    if (confirm('Reset all approvals to defaults?')) setApprovals(DEFAULT_APPROVALS)
  }

  const totalApproved = Object.values(approvals).reduce((n, ws) => n + ws.length, 0)

  const TABS = [
    { id: 'gallery',   label: 'Gallery' },
    { id: 'approvals', label: 'Approvals' },
    { id: 'composer',  label: 'Composer' },
  ]

  return (
    <div className="min-h-screen flex flex-col bg-[var(--color-background-secondary)]">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-[var(--color-background-primary)] border-b border-[var(--color-border-secondary)] px-5 h-12 flex items-center gap-5 flex-shrink-0">
        {/* Logo */}
        <div className="flex items-center gap-2 flex-shrink-0">
          <div className="w-6 h-6 rounded-md bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center text-white text-[10px] font-bold select-none">
            ◫
          </div>
          <span className="text-sm font-semibold text-[var(--color-text-primary)]">FK Composer</span>
        </div>

        {/* Tabs */}
        <nav className="flex items-center gap-0.5">
          {TABS.map(t => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                tab === t.id
                  ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300'
                  : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-background-tertiary)]'
              }`}
            >
              {t.label}
            </button>
          ))}
        </nav>

        {/* Right controls */}
        <div className="ml-auto flex items-center gap-2.5">
          <span className="text-xs text-[var(--color-text-tertiary)] hidden sm:block">
            {totalApproved} approved slot{totalApproved !== 1 ? 's' : ''} across {FK_REGISTRY.length} components
          </span>

          <button
            onClick={() => setDark(d => !d)}
            className="w-7 h-7 flex items-center justify-center rounded-lg hover:bg-[var(--color-background-tertiary)] text-[var(--color-text-secondary)] transition text-sm"
            title="Toggle dark mode"
          >
            {dark ? '☀' : '◑'}
          </button>

          <button
            onClick={resetApprovals}
            className="px-2.5 py-1 text-xs font-medium border border-[var(--color-border-secondary)] rounded-lg text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-background-secondary)] transition"
          >
            Reset
          </button>

          <button
            onClick={exportApprovals}
            className="px-2.5 py-1 text-xs font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition"
          >
            Export JSON
          </button>
        </div>
      </header>

      {/* Content */}
      <main className="flex-1 overflow-auto">
        {tab === 'gallery'   && <GalleryView   registry={FK_REGISTRY} approvals={approvals} onToggle={toggleApproval} />}
        {tab === 'approvals' && <ApprovalsView  registry={FK_REGISTRY} approvals={approvals} onToggle={toggleApproval} />}
        {tab === 'composer'  && <ComposerView   registry={FK_REGISTRY} approvals={approvals} />}
      </main>
    </div>
  )
}
