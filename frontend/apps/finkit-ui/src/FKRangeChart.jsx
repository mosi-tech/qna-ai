import React, { useRef, useEffect, useCallback } from 'react'
import { FKCard, FKCardHeader } from './FKCard.jsx'
import { FKBadge } from './FKSparkline.jsx'
import { color } from './tokens.js'

// ─── Sample data ──────────────────────────────────────────────────────────────
const SAMPLE_DATA = [
  { label: 'AAPL', min: 124.17, max: 223.45, value: 189.30, target: 210.00 },
  { label: 'MSFT', min: 309.00, max: 468.35, value: 379.91, target: 430.00 },
  { label: 'NVDA', min: 402.75, max: 974.00, value: 876.40, target: 950.00 },
  { label: 'AMZN', min: 101.20, max: 201.20, value: 187.55, target: 215.00 },
  { label: 'GOOGL', min:  91.00, max: 193.31, value: 166.80, target: 190.00 },
]

// ─── Draw helpers ─────────────────────────────────────────────────────────────
function getRowColor(row, colorRule) {
  if (colorRule) {
    const token = colorRule(row)
    if (token === 'gain')    return color.gain
    if (token === 'loss')    return color.loss
    if (token === 'warn')    return color.warn
    if (token === 'neutral') return '#94a3b8'
    return token
  }
  const pct = (row.value - row.min) / ((row.max - row.min) || 1)
  return pct > 0.6 ? color.gain : pct < 0.35 ? color.loss : color.warn
}

function drawChart(canvas, data, opts) {
  const { labelKey, minKey, maxKey, valueKey, targetKey, value2Key, format, showValues, colorRule, rowHeight } = opts
  const dpr = window.devicePixelRatio || 1
  const W   = canvas.offsetWidth
  const H   = data.length * rowHeight
  canvas.width  = W * dpr
  canvas.height = H * dpr
  canvas.style.height = H + 'px'
  const ctx = canvas.getContext('2d')
  ctx.scale(dpr, dpr)

  const isDark   = window.matchMedia('(prefers-color-scheme: dark)').matches
  const labelCol = isDark ? 'rgba(255,255,255,0.55)' : 'rgba(0,0,0,0.45)'
  const valCol   = isDark ? 'rgba(255,255,255,0.75)' : 'rgba(0,0,0,0.7)'

  const LABEL_W   = 88
  const VALUE_W   = showValues ? 88 : 0
  const BAR_LEFT  = LABEL_W + 12
  const BAR_RIGHT = W - VALUE_W - 8
  const BAR_W     = BAR_RIGHT - BAR_LEFT

  data.forEach((row, i) => {
    const y      = i * rowHeight + rowHeight / 2
    const mn     = row[minKey]
    const mx     = row[maxKey]
    const v      = row[valueKey]
    const range  = mx - mn || 1
    const pct    = (v - mn) / range
    const barH   = 6
    const markerR= 5
    const fillC  = getRowColor(row, colorRule)

    // Label
    ctx.font      = `500 15px system-ui, -apple-system, sans-serif`
    ctx.fillStyle = labelCol
    ctx.textAlign = 'right'
    ctx.textBaseline = 'middle'
    ctx.fillText(row[labelKey], LABEL_W, y)

    // Range track
    ctx.fillStyle   = isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)'
    const tx        = BAR_LEFT, ty = y - barH / 2
    ctx.beginPath()
    ctx.roundRect(tx, ty, BAR_W, barH, 99)
    ctx.fill()

    // Value marker
    const markerX = BAR_LEFT + Math.min(Math.max(pct, 0), 1) * BAR_W
    ctx.fillStyle  = fillC
    ctx.beginPath(); ctx.arc(markerX, y, markerR, 0, Math.PI * 2); ctx.fill()
    ctx.strokeStyle= fillC; ctx.lineWidth = 1
    ctx.stroke()

    // Target marker (diamond in #6366f1)
    if (targetKey && row[targetKey] != null) {
      const tPct    = (row[targetKey] - mn) / range
      const tx2     = BAR_LEFT + Math.min(Math.max(tPct, 0), 1) * BAR_W
      const ds      = 4
      ctx.fillStyle = '#6366f1'
      ctx.beginPath()
      ctx.moveTo(tx2, y - ds)
      ctx.lineTo(tx2 + ds, y)
      ctx.lineTo(tx2, y + ds)
      ctx.lineTo(tx2 - ds, y)
      ctx.closePath()
      ctx.fill()
    }

    // value2 marker
    if (value2Key && row[value2Key] != null) {
      const v2Pct = (row[value2Key] - mn) / range
      const v2X   = BAR_LEFT + Math.min(Math.max(v2Pct, 0), 1) * BAR_W
      ctx.fillStyle = '#f59e0b'
      ctx.beginPath(); ctx.arc(v2X, y, 3.5, 0, Math.PI * 2); ctx.fill()
    }

    // Min/max labels
    if (showValues) {
      ctx.fillStyle = labelCol; ctx.font = `14px ui-monospace, 'SF Mono', Consolas, monospace`
      ctx.textAlign = 'left'
      ctx.fillText(format ? format(mn) : mn.toFixed(2), BAR_LEFT, y + markerR + 14)
      ctx.textAlign = 'right'
      ctx.fillText(format ? format(mx) : mx.toFixed(2), BAR_RIGHT, y + markerR + 14)

      // Current value right of bar
      ctx.fillStyle = valCol; ctx.font = `600 15px ui-monospace, 'SF Mono', Consolas, monospace`
      ctx.textAlign = 'left'
      ctx.fillText(format ? format(v) : v.toFixed(2), BAR_RIGHT + 6, y)
    }
  })
}

// ─── FKRangeChart ─────────────────────────────────────────────────────────────
export function FKRangeChart({
  data,
  labelKey   = 'label',
  minKey     = 'min',
  maxKey     = 'max',
  valueKey   = 'value',
  targetKey,
  value2Key,
  format,
  showValues = true,
  colorRule,
  rowHeight  = 64,
  title,
  subtitle,
  badge,
}) {
  const canvasRef    = useRef(null)
  const resolvedData = data || SAMPLE_DATA

  const redraw = useCallback(() => {
    const c = canvasRef.current
    if (!c) return
    drawChart(c, resolvedData, { labelKey, minKey, maxKey, valueKey, targetKey, value2Key, format, showValues, colorRule, rowHeight })
  }, [resolvedData, labelKey, minKey, maxKey, valueKey, targetKey, value2Key, format, showValues, colorRule, rowHeight])

  useEffect(() => {
    redraw()
    const c = canvasRef.current
    if (!c) return
    const ro = new ResizeObserver(redraw)
    ro.observe(c.parentElement || c)
    return () => ro.disconnect()
  }, [redraw])

  const totalHeight = resolvedData.length * rowHeight

  return (
    <FKCard>
      <FKCardHeader
        title={title}
        subtitle={subtitle}
        actions={badge ? <FKBadge variant="neutral">{badge}</FKBadge> : null}
      />
      <div style={{ padding: '12px 20px 16px' }}>
        <canvas
          ref={canvasRef}
          style={{ width: '100%', height: totalHeight, display: 'block' }}
        />
      </div>
    </FKCard>
  )
}
