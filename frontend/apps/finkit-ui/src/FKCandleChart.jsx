import React, { useRef, useEffect, useCallback } from 'react'
import { FKCard, FKCardHeader } from './FKCard.jsx'
import { FKStatStrip, FKBadge } from './FKSparkline.jsx'
import { color } from './tokens.js'

// ─── Sample OHLCV data ────────────────────────────────────────────────────────
function makeSampleOHLCV(n = 60) {
  let price = 200
  const result = []
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
  for (let i = 0; i < n; i++) {
    const open   = price
    const change = (Math.random() - 0.48) * 6
    const close  = parseFloat((open + change).toFixed(2))
    const high   = parseFloat((Math.max(open, close) + Math.random() * 3).toFixed(2))
    const low    = parseFloat((Math.min(open, close) - Math.random() * 3).toFixed(2))
    const volume = Math.floor(1_000_000 + Math.random() * 4_000_000)
    const d      = new Date(2024, Math.floor(i / 5) % 12, (i % 5) * 5 + 1)
    result.push({
      date: `${months[d.getMonth()]} ${d.getDate()}`,
      open, close, high, low, volume,
    })
    price = close
  }
  return result
}
const SAMPLE_DATA = makeSampleOHLCV()

// ─── Draw ─────────────────────────────────────────────────────────────────────
function drawCandles(canvas, data, opts) {
  const { xKey = 'date', openKey = 'open', closeKey = 'close', highKey = 'high', lowKey = 'low', volumeKey = 'volume', height, showVolume } = opts
  const dpr  = window.devicePixelRatio || 1
  const W    = canvas.offsetWidth
  const H    = height || 300
  canvas.width  = W * dpr
  canvas.height = H * dpr
  canvas.style.height = H + 'px'
  const ctx  = canvas.getContext('2d')
  ctx.scale(dpr, dpr)

  const isDark  = window.matchMedia('(prefers-color-scheme: dark)').matches
  const bg      = isDark ? '#0f1117' : '#ffffff'
  const gridCol = isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)'
  const textCol = isDark ? 'rgba(255,255,255,0.4)'  : 'rgba(0,0,0,0.4)'

  // Layout
  const PAD    = { top: 12, right: 8, bottom: showVolume ? 60 : 28, left: 8 }
  const volH   = showVolume ? 48 : 0
  const chartH = H - PAD.top - PAD.bottom - volH
  const cW     = W - PAD.left - PAD.right
  const n      = data.length
  if (!n) return

  // Price domain
  const allHigh  = data.map(r => r[highKey])
  const allLow   = data.map(r => r[lowKey])
  const yMin     = Math.min(...allLow)  * 0.998
  const yMax     = Math.max(...allHigh) * 1.002

  // Volume domain
  const allVol   = data.map(r => r[volumeKey] || 0)
  const volMax   = Math.max(...allVol) || 1

  const toY  = v => PAD.top + (1 - (v - yMin) / (yMax - yMin)) * chartH
  const barW = Math.max(2, Math.floor(cW / n) - 1)
  const toX  = i => PAD.left + (i + 0.5) * (cW / n)

  // Y grid lines
  ctx.font = `9px var(--font-mono, monospace)`
  for (let t = 0; t <= 4; t++) {
    const yv  = yMin + (t / 4) * (yMax - yMin)
    const sy  = toY(yv)
    ctx.strokeStyle = gridCol; ctx.lineWidth = 0.5
    ctx.beginPath(); ctx.moveTo(PAD.left, sy); ctx.lineTo(PAD.left + cW, sy); ctx.stroke()
    ctx.fillStyle = textCol; ctx.textAlign = 'right'
    ctx.fillText(`$${yv.toFixed(0)}`, W - 4, sy + 3)
  }

  // Candles
  data.forEach((row, i) => {
    const o    = row[openKey]
    const c    = row[closeKey]
    const h    = row[highKey]
    const l    = row[lowKey]
    const isUp = c >= o
    const fill = isUp ? color.gain : color.loss
    const cx   = toX(i)
    const oy   = toY(o), cy2 = toY(c), hy = toY(h), ly = toY(l)
    const bTop = Math.min(oy, cy2), bH = Math.max(1, Math.abs(cy2 - oy))

    // Wick
    ctx.strokeStyle = fill; ctx.lineWidth = 1
    ctx.beginPath(); ctx.moveTo(cx, hy); ctx.lineTo(cx, ly); ctx.stroke()

    // Body
    ctx.fillStyle = fill
    const halfW = Math.max(1, barW / 2)
    ctx.beginPath()
    ctx.roundRect(cx - halfW, bTop, halfW * 2, bH, 1)
    ctx.fill()
  })

  // Volume bars
  if (showVolume) {
    const volTop = PAD.top + chartH + 8
    data.forEach((row, i) => {
      const v    = row[volumeKey] || 0
      const isUp = row[closeKey] >= row[openKey]
      const bH   = (v / volMax) * (volH - 4)
      const cx   = toX(i)
      const halfW= Math.max(1, barW / 2)
      ctx.fillStyle = isUp ? 'rgba(22,163,74,0.4)' : 'rgba(220,38,38,0.4)'
      ctx.fillRect(cx - halfW, volTop + (volH - bH), halfW * 2, bH)
    })
    ctx.fillStyle = textCol; ctx.font = `9px var(--font-mono, monospace)`
    ctx.textAlign = 'left'
    ctx.fillText('Volume', PAD.left + 4, volTop + 10)
  }

  // X axis labels (every ~10 candles)
  const step = Math.ceil(n / 8)
  data.forEach((row, i) => {
    if (i % step !== 0) return
    ctx.fillStyle = textCol; ctx.font = `9px var(--font-mono, monospace)`
    ctx.textAlign = 'center'
    ctx.fillText(row[xKey], toX(i), H - 6)
  })
}

// ─── FKCandleChart ────────────────────────────────────────────────────────────
export function FKCandleChart({
  data,
  xKey        = 'date',
  openKey     = 'open',
  closeKey    = 'close',
  highKey     = 'high',
  lowKey      = 'low',
  volumeKey   = 'volume',
  height      = 300,
  showVolume  = true,
  title,
  subtitle,
  badge,
  stats,
}) {
  const canvasRef    = useRef(null)
  const resolvedData = data || SAMPLE_DATA

  const redraw = useCallback(() => {
    const c = canvasRef.current
    if (!c) return
    drawCandles(c, resolvedData, { xKey, openKey, closeKey, highKey, lowKey, volumeKey, height, showVolume })
  }, [resolvedData, xKey, openKey, closeKey, highKey, lowKey, volumeKey, height, showVolume])

  useEffect(() => {
    redraw()
    const c = canvasRef.current
    if (!c) return
    const ro = new ResizeObserver(redraw)
    ro.observe(c.parentElement || c)
    return () => ro.disconnect()
  }, [redraw])

  return (
    <FKCard>
      <FKCardHeader
        title={title}
        subtitle={subtitle}
        actions={badge ? <FKBadge variant="neutral">{badge}</FKBadge> : null}
      />
      <div style={{ padding: '8px 0 0', position: 'relative' }}>
        <canvas
          ref={canvasRef}
          style={{ width: '100%', height, display: 'block' }}
        />
      </div>
      {stats && <FKStatStrip stats={stats} />}
    </FKCard>
  )
}
