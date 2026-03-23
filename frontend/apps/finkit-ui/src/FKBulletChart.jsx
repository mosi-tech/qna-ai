import React, { useRef, useEffect, useCallback, useState } from 'react'
import { FKCard, FKCardHeader } from './FKCard.jsx'
import { FKTooltip } from './FKTooltip.jsx'
import { color } from './tokens.js'

// ─── Sample data ──────────────────────────────────────────────────────────────
const SAMPLE_DATA = [
  { label: 'AAPL price target', value: 213,  target: 225,  rangeMin: 180,  rangeMax: 260  },
  { label: 'Q3 EPS',            value: 1.52, target: 1.43, rangeMin: 1.20, rangeMax: 1.65 },
  { label: 'Revenue ($B)',      value: 89.5, target: 92.0, rangeMin: 84.0, rangeMax: 96.0 },
  { label: 'Gross Margin',      value: 0.44, target: 0.46, rangeMin: 0.40, rangeMax: 0.50 },
]

const ROW_H    = 52
const LABEL_W  = 140
const VALUE_W  = 72
const H_PAD    = 16
const BAR_H    = 10
const FILL_H   = 6

function drawBullet(canvas, data, fmt) {
  const dpr = window.devicePixelRatio || 1
  const W   = canvas.offsetWidth
  const H   = data.length * ROW_H + H_PAD * 2
  canvas.width  = W * dpr
  canvas.height = H * dpr
  canvas.style.height = H + 'px'
  const ctx = canvas.getContext('2d')
  ctx.scale(dpr, dpr)

  const isDark  = window.matchMedia('(prefers-color-scheme: dark)').matches
  const labelC  = isDark ? 'rgba(255,255,255,0.55)' : 'rgba(0,0,0,0.5)'
  const valueC  = isDark ? 'rgba(255,255,255,0.8)'  : 'rgba(0,0,0,0.75)'

  const BAR_LEFT  = LABEL_W
  const BAR_RIGHT = W - VALUE_W - H_PAD
  const BAR_W     = BAR_RIGHT - BAR_LEFT

  ctx.font = '10px var(--font-mono, monospace)'

  data.forEach((row, i) => {
    const y     = H_PAD + i * ROW_H + ROW_H / 2
    const range = row.rangeMax - row.rangeMin || 1

    // Clamp values to range
    const valuePct  = Math.min(Math.max((row.value  - row.rangeMin) / range, 0), 1)
    const targetPct = Math.min(Math.max((row.target - row.rangeMin) / range, 0), 1)

    // Row label
    ctx.fillStyle = labelC
    ctx.textAlign = 'right'
    ctx.textBaseline = 'middle'
    ctx.font = '11px var(--font-sans, sans-serif)'
    ctx.fillText(row.label, LABEL_W - 8, y)

    // Background range track
    const tx = BAR_LEFT, ty = y - BAR_H / 2
    ctx.fillStyle = isDark ? 'rgba(255,255,255,0.10)' : 'rgba(0,0,0,0.08)'
    ctx.beginPath(); ctx.roundRect(tx, ty, BAR_W, BAR_H, 4); ctx.fill()

    // Performance bar (filled from left to current value)
    const barWidth = valuePct * BAR_W
    const aboveTarget = row.value >= row.target
    ctx.fillStyle = aboveTarget ? 'rgba(22,163,74,0.80)' : 'rgba(220,38,38,0.80)'
    ctx.beginPath()
    ctx.roundRect(BAR_LEFT, y - FILL_H / 2, Math.max(barWidth, 2), FILL_H, 3)
    ctx.fill()

    // Target marker (2px vertical tick)
    const targetX = BAR_LEFT + targetPct * BAR_W
    ctx.fillStyle = isDark ? 'rgba(255,255,255,0.9)' : 'rgba(0,0,0,0.85)'
    ctx.fillRect(targetX - 1, y - BAR_H / 2 - 2, 2, BAR_H + 4)

    // Value label
    ctx.font = '500 11px var(--font-mono, monospace)'
    ctx.fillStyle = aboveTarget ? color.gain : color.loss
    ctx.textAlign = 'left'
    ctx.textBaseline = 'middle'
    const formatted = row.format ? row.format(row.value) : fmt(row.value)
    ctx.fillText(formatted, BAR_RIGHT + 8, y)

    // vs target (small sub-label)
    ctx.font = '9px var(--font-mono, monospace)'
    ctx.fillStyle = labelC
    const targetFormatted = row.format ? row.format(row.target) : fmt(row.target)
    ctx.fillText(`vs ${targetFormatted}`, BAR_RIGHT + 8, y + 12)
  })
}

// ─── FKBulletChart ─────────────────────────────────────────────────────────
export function FKBulletChart({
  data,
  title,
  subtitle,
  valueFormat,
}) {
  const canvasRef    = useRef(null)
  const resolvedData = data || SAMPLE_DATA
  const fmt          = valueFormat || (v => v.toFixed(2))

  const [tooltip, setTooltip] = useState(null)

  const redraw = useCallback(() => {
    const c = canvasRef.current
    if (!c) return
    drawBullet(c, resolvedData, fmt)
  }, [resolvedData, fmt])

  useEffect(() => {
    redraw()
    const c = canvasRef.current
    if (!c) return
    const ro = new ResizeObserver(redraw)
    ro.observe(c.parentElement || c)
    return () => ro.disconnect()
  }, [redraw])

  // Hover detection for tooltip
  function handleMouseMove(e) {
    const canvas = canvasRef.current
    if (!canvas) return
    const rect  = canvas.getBoundingClientRect()
    const relY  = e.clientY - rect.top - H_PAD
    const idx   = Math.floor(relY / ROW_H)
    const row   = resolvedData[idx]
    if (row && idx >= 0 && idx < resolvedData.length) {
      setTooltip({ row, x: e.clientX - rect.left, y: idx * ROW_H + H_PAD })
    } else {
      setTooltip(null)
    }
  }

  const totalH = resolvedData.length * ROW_H + H_PAD * 2

  return (
    <FKCard>
      <FKCardHeader title={title} subtitle={subtitle} />
      <div style={{ padding: '12px 20px 16px', position: 'relative' }}>
        <canvas
          ref={canvasRef}
          style={{ width: '100%', height: totalH, display: 'block', cursor: 'default' }}
          onMouseMove={handleMouseMove}
          onMouseLeave={() => setTooltip(null)}
        />
        {tooltip && (
          <FKTooltip.Box style={{ top: tooltip.y + 16, left: Math.min(tooltip.x + 8, 400) }}>
            <FKTooltip.Header>{tooltip.row.label}</FKTooltip.Header>
            <FKTooltip.Row
              color={tooltip.row.value >= tooltip.row.target ? color.gain : color.loss}
              label="Actual"
              value={fmt(tooltip.row.value)}
            />
            <FKTooltip.Row color="#94a3b8" label="Target" value={fmt(tooltip.row.target)} />
            <FKTooltip.Row label="Range" value={`${fmt(tooltip.row.rangeMin)} – ${fmt(tooltip.row.rangeMax)}`} />
          </FKTooltip.Box>
        )}
      </div>
    </FKCard>
  )
}
