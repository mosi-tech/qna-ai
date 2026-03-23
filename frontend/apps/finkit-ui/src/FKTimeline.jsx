import React, { useState, useMemo, useRef, useLayoutEffect } from 'react'
import { FKCard, FKCardHeader } from './FKCard.jsx'
import { FKTooltip } from './FKTooltip.jsx'
import { color } from './tokens.js'

// ─── Sample data ──────────────────────────────────────────────────────────────
const SAMPLE_EVENTS = [
  { date: '2025-01-30', label: 'AAPL Q1',     row: 'Earnings',  type: 'beat',     value: 'EPS $2.40 (+1.7%)' },
  { date: '2025-02-06', label: 'MSFT Q2',     row: 'Earnings',  type: 'beat',     value: 'EPS $3.23 (+3.8%)' },
  { date: '2025-02-27', label: 'NVDA Q4',     row: 'Earnings',  type: 'beat',     value: 'EPS $0.89 (+15%)' },
  { date: '2025-02-13', label: 'AAPL Div',    row: 'Dividends', type: 'dividend', value: '$0.25/share' },
  { date: '2025-03-19', label: 'Fed Meeting', row: 'Macro',     type: 'fed',      value: 'Rate hold expected' },
  { date: '2025-04-30', label: 'AAPL Q2',     row: 'Earnings',  type: 'miss',     value: 'EPS $1.52 (-2.1%)' },
  { date: '2025-05-07', label: 'Fed Meeting', row: 'Macro',     type: 'fed',      value: 'Rate decision' },
  { from: '2025-02-01', to: '2025-03-15',     label: 'AAPL Lock-up', row: 'Lock-ups', type: 'lockup', value: 'Insider lock-up period' },
]
const SAMPLE_COLOR_MAP = {
  beat:     color.gain,
  miss:     color.loss,
  dividend: '#6366f1',
  fed:      '#f59e0b',
  lockup:   '#94a3b8',
}

const DOT_R      = 5
const ROW_H      = 40
const LABEL_W    = 80
const AXIS_H     = 24
const PAD_TOP    = 12
const PAD_RIGHT  = 16

function parseDate(d) { return d ? new Date(d).getTime() : null }

// ─── FKTimeline ───────────────────────────────────────────────────────────────
export function FKTimeline({
  events,
  dateMin,
  dateMax,
  colorMap,
  title,
  subtitle,
  height,
}) {
  const resolvedEvents   = events   || SAMPLE_EVENTS
  const resolvedColorMap = colorMap || SAMPLE_COLOR_MAP

  const [tooltip, setTooltip] = useState(null)
  const containerRef = useRef(null)
  const [width, setWidth] = useState(600)

  useLayoutEffect(() => {
    const el = containerRef.current
    if (!el) return
    const ro = new ResizeObserver(() => setWidth(el.clientWidth))
    ro.observe(el)
    setWidth(el.clientWidth)
    return () => ro.disconnect()
  }, [])

  // Compute rows, date domain, positions
  const { rows, tMin, tMax, chartWidth, today } = useMemo(() => {
    const pointEvents    = resolvedEvents.filter(e => e.date && !e.to)
    const durationEvents = resolvedEvents.filter(e => e.from && e.to)

    const rowSet = [...new Set(resolvedEvents.map(e => e.row || '__default').filter(Boolean))]
    if (rowSet.length === 0) rowSet.push('__default')

    const allDates = [
      ...pointEvents.map(e => parseDate(e.date)),
      ...durationEvents.flatMap(e => [parseDate(e.from), parseDate(e.to)]),
    ].filter(Boolean)

    const now = Date.now()
    const tMin = dateMin ? parseDate(dateMin) : (Math.min(...allDates) - 7 * 864e5)
    const tMax = dateMax ? parseDate(dateMax) : (Math.max(...allDates) + 7 * 864e5)

    return {
      rows:       rowSet,
      tMin,
      tMax,
      chartWidth: Math.max(1, width - LABEL_W - PAD_RIGHT),
      today:      now,
    }
  }, [resolvedEvents, dateMin, dateMax, width])

  function toX(t) {
    return LABEL_W + ((t - tMin) / (tMax - tMin)) * chartWidth
  }

  // X-axis ticks
  const ticks = useMemo(() => {
    const span     = tMax - tMin
    const tickCount = Math.min(8, Math.max(3, Math.floor(chartWidth / 80)))
    return Array.from({ length: tickCount + 1 }, (_, i) => {
      const t = tMin + (i / tickCount) * span
      return { t, label: new Date(t).toLocaleDateString('en-US', { month: 'short', year: '2-digit' }) }
    })
  }, [tMin, tMax, chartWidth])

  const totalH = height || (rows.length * ROW_H + PAD_TOP + AXIS_H + 8)

  function getColor(type) {
    return resolvedColorMap[type] || color.series[0]
  }

  return (
    <FKCard>
      <FKCardHeader title={title} subtitle={subtitle} />
      <div ref={containerRef} style={{ padding: '12px 0 8px', position: 'relative', overflowX: 'auto' }}>
        <svg width={width} height={totalH} style={{ display: 'block', fontFamily: 'var(--font-mono)' }}>

          {/* Row labels + lane backgrounds */}
          {rows.map((row, ri) => {
            const y = PAD_TOP + ri * ROW_H
            return (
              <g key={row}>
                <rect x={0} y={y} width={width} height={ROW_H}
                  fill={ri % 2 === 0 ? 'var(--color-background-secondary)' : 'transparent'}
                  opacity={0.4} />
                {row !== '__default' && (
                  <text x={LABEL_W - 8} y={y + ROW_H / 2 + 1} textAnchor="end"
                    fontSize={10} fill="var(--color-text-tertiary)" dominantBaseline="middle">
                    {row}
                  </text>
                )}
                {/* Horizontal lane guide */}
                <line x1={LABEL_W} y1={y + ROW_H} x2={LABEL_W + chartWidth} y2={y + ROW_H}
                  stroke="var(--color-border-tertiary)" strokeWidth={0.5} />
              </g>
            )
          })}

          {/* Today reference line */}
          {today >= tMin && today <= tMax && (
            <g>
              <line
                x1={toX(today)} y1={PAD_TOP}
                x2={toX(today)} y2={PAD_TOP + rows.length * ROW_H}
                stroke="var(--color-text-tertiary)" strokeWidth={1} strokeDasharray="4 3" opacity={0.5}
              />
              <text x={toX(today) + 3} y={PAD_TOP + 10} fontSize={9} fill="var(--color-text-tertiary)">
                Today
              </text>
            </g>
          )}

          {/* Duration bars */}
          {resolvedEvents.filter(e => e.from && e.to).map((ev, i) => {
            const ri  = rows.indexOf(ev.row || '__default')
            if (ri < 0) return null
            const x1  = toX(parseDate(ev.from))
            const x2  = toX(parseDate(ev.to))
            const y   = PAD_TOP + ri * ROW_H + ROW_H / 2
            const c   = getColor(ev.type)
            const key = `dur-${i}`
            return (
              <g key={key}>
                <rect
                  x={x1} y={y - 5} width={Math.max(2, x2 - x1)} height={10}
                  rx={99} fill={c} fillOpacity={0.3}
                  style={{ cursor: 'default' }}
                  onMouseEnter={e2 => setTooltip({ ev, x: x1 + (x2 - x1) / 2, y: y - 20 })}
                  onMouseLeave={() => setTooltip(null)}
                />
                <line x1={x1} y1={y} x2={x2} y2={y} stroke={c} strokeWidth={1.5} opacity={0.6} />
              </g>
            )
          })}

          {/* Point event dots */}
          {resolvedEvents.filter(e => e.date && !e.to).map((ev, i) => {
            const ri = rows.indexOf(ev.row || '__default')
            if (ri < 0) return null
            const x  = toX(parseDate(ev.date))
            const y  = PAD_TOP + ri * ROW_H + ROW_H / 2
            const c  = getColor(ev.type)
            return (
              <g key={`dot-${i}`}>
                <circle
                  cx={x} cy={y} r={DOT_R}
                  fill={c} fillOpacity={0.85}
                  stroke={c} strokeWidth={1}
                  style={{ cursor: 'default' }}
                  onMouseEnter={() => setTooltip({ ev, x, y: y - 16 })}
                  onMouseLeave={() => setTooltip(null)}
                />
              </g>
            )
          })}

          {/* X-axis */}
          <g transform={`translate(0, ${PAD_TOP + rows.length * ROW_H})`}>
            {ticks.map((tick, i) => (
              <g key={i} transform={`translate(${toX(tick.t)}, 0)`}>
                <line y1={0} y2={4} stroke="var(--color-border-secondary)" strokeWidth={0.5} />
                <text y={14} textAnchor="middle" fontSize={9} fill="var(--color-text-tertiary)">
                  {tick.label}
                </text>
              </g>
            ))}
            <line
              x1={LABEL_W} y1={0} x2={LABEL_W + chartWidth} y2={0}
              stroke="var(--color-border-secondary)" strokeWidth={0.5}
            />
          </g>
        </svg>

        {/* Hover tooltip */}
        {tooltip && (
          <div style={{
            position:   'absolute',
            left:       Math.min(tooltip.x, width - 200),
            top:        tooltip.y,
            pointerEvents: 'none',
            zIndex:     50,
          }}>
            <FKTooltip.Box style={{ position: 'relative' }}>
              <FKTooltip.Header>
                {tooltip.ev.date
                  ? new Date(tooltip.ev.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
                  : `${tooltip.ev.from} – ${tooltip.ev.to}`}
              </FKTooltip.Header>
              <FKTooltip.Row
                color={getColor(tooltip.ev.type)}
                label={tooltip.ev.label}
                value={tooltip.ev.value || ''}
              />
            </FKTooltip.Box>
          </div>
        )}
      </div>
    </FKCard>
  )
}
