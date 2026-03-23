import React from 'react'
import { FKCard, FKCardHeader } from './FKCard.jsx'
import { FKDelta, FKSparkline, FKBadge } from './FKSparkline.jsx'
import { color, resolveColor } from './tokens.js'

// ─── Sample data ──────────────────────────────────────────────────────────────
const SAMPLE_DATA = [
  { label: 'NVDA',  value: '+38.4%', delta:  38.4, sub: 'Technology', spark: [40,52,48,61,55,68,72,76,70,88] },
  { label: 'META',  value: '+24.1%', delta:  24.1, sub: 'Technology', spark: [30,35,32,38,41,44,40,48,51,55] },
  { label: 'AAPL',  value: '+18.7%', delta:  18.7, sub: 'Technology', spark: [60,62,59,64,63,67,65,70,68,74] },
  { label: 'MSFT',  value: '+12.3%', delta:  12.3, sub: 'Technology', spark: [50,52,54,51,55,58,56,60,59,63] },
  { label: 'AMZN',  value:  '+8.9%', delta:   8.9, sub: 'Consumer',   spark: [40,42,41,44,43,46,45,48,47,50] },
  { label: 'BRK.B', value:  '+5.2%', delta:   5.2, sub: 'Financials', spark: [70,71,72,70,73,72,74,73,75,74] },
  { label: 'JPM',   value:  '-2.4%', delta:  -2.4, sub: 'Financials', spark: [55,54,56,53,55,52,54,51,53,50] },
  { label: 'TSLA',  value: '-11.8%', delta: -11.8, sub: 'Consumer',   spark: [80,75,72,68,70,65,62,58,55,52] },
]

// ─── FKRankedList ─────────────────────────────────────────────────────────────
export function FKRankedList({
  data,
  labelKey    = 'label',
  valueKey    = 'value',
  deltaKey    = 'delta',
  subKey      = 'sub',
  sparkKey    = 'spark',
  valueFormat,
  colorRule,
  title,
  subtitle,
  badge,
}) {
  const resolvedData = data || SAMPLE_DATA

  return (
    <FKCard>
      <FKCardHeader
        title={title}
        subtitle={subtitle}
        actions={badge ? <FKBadge variant="neutral">{badge}</FKBadge> : null}
      />
      <div style={{ padding: '8px 0 4px' }}>
        {resolvedData.map((row, i) => {
          const delta     = row[deltaKey]
          const sparkData = row[sparkKey]
          const token     = colorRule ? colorRule(row) : (delta != null ? (delta >= 0 ? 'gain' : 'loss') : null)
          const valueCol  = token ? resolveColor(token) : 'var(--color-text-primary)'

          return (
            <div
              key={i}
              className="flex items-center gap-3"
              style={{
                padding:    '10px 20px',
                borderBottom: i < resolvedData.length - 1
                  ? '0.5px solid var(--color-border-tertiary)'
                  : undefined,
                transition: 'background 0.1s',
              }}
              onMouseEnter={e => e.currentTarget.style.background = 'var(--color-background-secondary)'}
              onMouseLeave={e => e.currentTarget.style.background = ''}
            >
              {/* Rank number */}
              <span
                className="text-[12px] font-mono w-5 text-right flex-shrink-0"
                style={{ color: 'var(--color-text-tertiary)' }}
              >
                {i + 1}
              </span>

              {/* Colored accent bar */}
              <div style={{
                width: 3, height: 32, borderRadius: 99, flexShrink: 0,
                background: delta != null
                  ? (delta >= 0 ? color.gain : color.loss)
                  : color.series[i % color.series.length],
              }} />

              {/* Label + sub */}
              <div className="flex flex-col gap-0.5 flex-1 min-w-0">
                <span
                  className="text-sm font-medium truncate"
                  style={{ color: 'var(--color-text-primary)' }}
                >
                  {row[labelKey]}
                </span>
                {row[subKey] && (
                  <span className="text-[12px] font-sans truncate" style={{ color: 'var(--color-text-tertiary)' }}>
                    {row[subKey]}
                  </span>
                )}
              </div>

              {/* Sparkline */}
              {sparkKey && sparkData && (
                <div className="flex-shrink-0">
                  <FKSparkline data={sparkData} width={60} height={24} />
                </div>
              )}

              {/* Value */}
              <span
                className="text-sm font-mono font-medium text-right flex-shrink-0"
                style={{ minWidth: 56, color: valueCol }}
              >
                {valueFormat ? valueFormat(row[valueKey], row) : row[valueKey]}
              </span>

              {/* Delta badge */}
              {deltaKey && row[deltaKey] != null && (
                <div className="flex-shrink-0">
                  <FKDelta value={row[deltaKey]} decimals={1} />
                </div>
              )}
            </div>
          )
        })}
      </div>
    </FKCard>
  )
}
