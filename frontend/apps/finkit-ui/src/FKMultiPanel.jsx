import React, { useState } from 'react'
import {
  ResponsiveContainer, ComposedChart, Line, Area, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine,
} from 'recharts'
import { FKCard, FKCardHeader } from './FKCard.jsx'
import { FKRangeSelector } from './FKRangeSelector.jsx'
import { FKTooltip } from './FKTooltip.jsx'
import { color, axisProps, gridProps } from './tokens.js'

// ─── Sample data ──────────────────────────────────────────────────────────────
function makeSampleData(n = 80) {
  let price = 412, sma20 = 412, rsi = 55
  const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
  return Array.from({ length: n }, (_, i) => {
    price  = +(price  + (Math.random() - 0.47) * 6).toFixed(2)
    sma20  = +(sma20  * 0.95 + price * 0.05).toFixed(2)
    const gain = price - (i > 0 ? price - (Math.random() - 0.47) * 6 : price)
    rsi    = Math.min(85, Math.max(15, rsi + (gain > 0 ? 2 : -2) + (Math.random() - 0.5) * 4))
    const vol = Math.floor(35_000_000 + Math.random() * 30_000_000)
    const d  = new Date(2024, Math.floor(i / 7) % 12, (i % 7) * 4 + 1)
    return { date: `${MONTHS[d.getMonth()]} ${d.getDate()}`, price, sma20, volume: vol, rsi: +rsi.toFixed(1) }
  })
}
const SAMPLE_DATA = makeSampleData()
const SAMPLE_PANELS = [
  {
    id: 'price', height: 280, yLabel: 'Price',
    series: [
      { key: 'price', label: 'QQQ', color: '#6366f1' },
      { key: 'sma20', label: 'SMA 20', color: '#f59e0b', strokeDash: '4 2' },
    ],
  },
  {
    id: 'volume', height: 80, yLabel: 'Volume',
    series: [{ key: 'volume', label: 'Volume', color: '#94a3b8', type: 'bar' }],
  },
  {
    id: 'rsi', height: 100, yLabel: 'RSI', yDomain: [0, 100],
    referenceLines: [
      { y: 70, label: 'OB', color: '#dc2626', dash: '3 3' },
      { y: 30, label: 'OS', color: '#16a34a', dash: '3 3' },
    ],
    series: [{ key: 'rsi', label: 'RSI (14)', color: '#8b5cf6' }],
  },
]

// ─── FKMultiPanel ─────────────────────────────────────────────────────────────
// All panels share syncId so Recharts handles crosshair synchronization automatically.
export function FKMultiPanel({
  data,
  xKey          = 'date',
  panels,
  title,
  subtitle,
  rangeSelector = true,
  defaultRange  = '3M',
}) {
  const resolvedData   = data   || SAMPLE_DATA
  const resolvedPanels = panels || SAMPLE_PANELS
  const rangeOptions   = ['1M', '3M', '6M', '1Y', 'ALL']
  const [range, setRange] = useState(defaultRange)

  const SYNC_ID = 'fk-multi-panel'

  return (
    <FKCard>
      <FKCardHeader
        title={title}
        subtitle={subtitle}
        actions={rangeSelector
          ? <FKRangeSelector options={rangeOptions} value={range} onChange={setRange} />
          : null
        }
      />

      <div style={{ padding: '8px 0 8px' }}>
        {resolvedPanels.map((panel, pi) => {
          const isLast     = pi === resolvedPanels.length - 1
          const panelH     = panel.height || (pi === 0 ? 280 : 120)
          const showXAxis  = isLast
          const bottomPad  = showXAxis ? 24 : 4

          return (
            <div
              key={panel.id}
              style={{
                height:      panelH,
                padding:     `4px 4px ${bottomPad}px 0`,
                borderTop:   pi > 0 ? '0.5px solid var(--color-border-tertiary)' : undefined,
              }}
            >
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart
                  data={resolvedData}
                  syncId={SYNC_ID}
                  margin={{ top: 2, right: 4, left: 0, bottom: 0 }}
                >
                  <CartesianGrid {...gridProps} />

                  <XAxis
                    dataKey={xKey}
                    {...axisProps}
                    hide={!showXAxis}
                    minTickGap={40}
                    maxRotation={0}
                  />

                  <YAxis
                    {...axisProps}
                    orientation="right"
                    width={52}
                    label={panel.yLabel ? {
                      value:    panel.yLabel,
                      position: 'insideRight',
                      angle:    -90,
                      offset:   -6,
                      style:    { fontSize: 12, fill: 'var(--color-text-tertiary)', fontFamily: 'var(--font-sans)' },
                    } : undefined}
                    domain={panel.yDomain || ['auto', 'auto']}
                  />

                  <Tooltip
                    content={<FKTooltip />}
                    cursor={{ stroke: 'var(--color-border-secondary)', strokeWidth: 1 }}
                  />

                  {/* Reference lines */}
                  {panel.referenceLines?.map((rl, i) => (
                    <ReferenceLine
                      key={i}
                      y={rl.y}
                      stroke={rl.color || 'var(--color-border-secondary)'}
                      strokeDasharray={rl.dash || '4 3'}
                      strokeWidth={1}
                      label={rl.label ? {
                        value:    rl.label,
                        position: 'right',
                        fill:     rl.color || 'var(--color-text-tertiary)',
                        fontSize: 12,
                        fontFamily: 'var(--font-sans)',
                      } : undefined}
                    />
                  ))}

                  {/* defs for area gradients */}
                  <defs>
                    {panel.series.filter(s => s.type === 'area').map((s, i) => {
                      const c = s.color || color.series[i]
                      return (
                        <linearGradient key={s.key} id={`mp-grad-${panel.id}-${s.key}`} x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%"   stopColor={c} stopOpacity={0.15} />
                          <stop offset="100%" stopColor={c} stopOpacity={0} />
                        </linearGradient>
                      )
                    })}
                  </defs>

                  {/* Series */}
                  {panel.series.map((s, si) => {
                    const c = s.color || color.series[si % color.series.length]
                    if (s.type === 'bar') {
                      return (
                        <Bar key={s.key} dataKey={s.key} name={s.label || s.key}
                          fill={c} fillOpacity={0.6} maxBarSize={8}
                          isAnimationActive={false} />
                      )
                    }
                    if (s.type === 'area') {
                      return (
                        <Area key={s.key} type="linear" dataKey={s.key} name={s.label || s.key}
                          stroke={c} strokeWidth={1.5}
                          strokeDasharray={s.strokeDash}
                          fill={`url(#mp-grad-${panel.id}-${s.key})`}
                          isAnimationActive={false} />
                      )
                    }
                    return (
                      <Line key={s.key} type="linear" dataKey={s.key} name={s.label || s.key}
                        stroke={c} strokeWidth={1.5}
                        strokeDasharray={s.strokeDash}
                        dot={false} isAnimationActive={false} />
                    )
                  })}
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          )
        })}
      </div>
    </FKCard>
  )
}
