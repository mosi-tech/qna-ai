import React, { useState } from 'react'
import { color } from './tokens.js'
import { FKDelta } from './FKSparkline.jsx'
import { FKSparkline } from './FKSparkline.jsx'

const SAMPLE_CARDS = [
  { label: 'Portfolio Value', value: '$94,273',  delta: 1.99,  sub: 'today' },
  { label: 'Total Return',    value: '+20.25%',  delta: 20.25, color: color.gain },
  { label: 'Sharpe Ratio',    value: '1.84',     sub: 'Excellent' },
  { label: 'Max Drawdown',    value: '−23.4%',   color: color.loss, sub: 'peak to trough' },
]

const COLS_CLASS = { 2: 'grid-cols-2', 3: 'grid-cols-3', 4: 'grid-cols-4' }

export function FKMetricGrid({ cards = SAMPLE_CARDS, cols = 4 }) {
  const colClass = COLS_CLASS[cols] || 'grid-cols-4'

  return (
    <div className={`grid ${colClass} gap-3`}>
      {cards.map((card, i) => (
        <MetricCard key={i} card={card} />
      ))}
    </div>
  )
}

function MetricCard({ card }) {
  const [hovered, setHovered] = useState(false)

  const topColor =
    card.delta !== undefined
      ? card.delta > 0 ? color.gain : card.delta < 0 ? color.loss : '#6366f1'
      : '#6366f1'

  return (
    <div
      className="relative rounded-xl transition-shadow duration-150 cursor-default select-none"
      style={{
        padding:     '20px 20px 16px',
        background:  'var(--color-background-primary)',
        border:      '0.5px solid var(--color-border-tertiary)',
        borderTop:   `2px solid ${topColor}`,
        ...(card.accent ? { borderLeft: `3px solid ${card.accent}` } : {}),
        boxShadow:   hovered ? '0 0 0 1px var(--color-border-secondary)' : undefined,
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {/* Label */}
      <div
        className="text-[10px] uppercase tracking-[0.06em] mb-2"
        style={{ color: 'var(--color-text-tertiary)', letterSpacing: '0.06em' }}
      >
        {card.label}
      </div>

      {/* Value */}
      <div
        className="font-mono font-medium leading-none mb-2"
        style={{
          fontSize: 26,
          color: card.color || 'var(--color-text-primary)',
        }}
      >
        {card.value}
      </div>

      {/* Delta + sub */}
      <div className="flex items-center gap-2 flex-wrap">
        {card.delta !== undefined && <FKDelta value={card.delta} />}
        {card.sub && (
          <span className="text-[11px]" style={{ color: 'var(--color-text-tertiary)' }}>
            {card.sub}
          </span>
        )}
      </div>

      {/* Sparkline — absolute bottom-right */}
      {card.spark && (
        <div className="absolute bottom-3 right-4 opacity-80">
          <FKSparkline data={card.spark} width={64} height={24} />
        </div>
      )}
    </div>
  )
}
