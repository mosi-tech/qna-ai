import React, { useRef, useEffect, useState, useCallback } from 'react'
import { FKCard, FKCardHeader } from './FKCard.jsx'
import { FKStatStrip, FKBadge } from './FKSparkline.jsx'
import { color } from './tokens.js'

// ─── Sample data ──────────────────────────────────────────────────────────────
const TICKERS = ['AAPL','MSFT','NVDA','AMZN','GOOGL','META','TSLA','BRK.B','JPM','V','UNH','JNJ']
const SECTORS = { AAPL:'Technology', MSFT:'Technology', NVDA:'Technology', AMZN:'Consumer', GOOGL:'Technology', META:'Technology', TSLA:'Consumer', 'BRK.B':'Financials', JPM:'Financials', V:'Financials', UNH:'Healthcare', JNJ:'Healthcare' }
const SECTOR_COLORS = { Technology:'#6366f1', Consumer:'#f59e0b', Financials:'#06b6d4', Healthcare:'#10b981' }
const SAMPLE_DATA = TICKERS.map(t => ({
  ticker: t, sector: SECTORS[t],
  volatility:       parseFloat((10 + Math.random() * 25).toFixed(1)),
  return_pct:       parseFloat((-5 + Math.random() * 30).toFixed(1)),
  portfolio_weight: parseFloat((2 + Math.random() * 12).toFixed(1)),
}))

// ─── OLS regression ──────────────────────────────────────────────────────────
function olsLine(pts) {
  const n  = pts.length
  if (n < 2) return null
  const sx = pts.reduce((a, p) => a + p.x, 0)
  const sy = pts.reduce((a, p) => a + p.y, 0)
  const sxy= pts.reduce((a, p) => a + p.x * p.y, 0)
  const sx2= pts.reduce((a, p) => a + p.x * p.x, 0)
  const denom = n * sx2 - sx * sx
  if (!denom) return null
  const m = (n * sxy - sx * sy) / denom
  const b = (sy - m * sx) / n
  return { m, b }
}

// ─── Draw function ────────────────────────────────────────────────────────────
function draw(canvas, data, opts) {
  const { xKey, yKey, sizeKey, colorKey, colorMap, labelKey, xLabel, yLabel, xFormat, yFormat, referenceLines, trendLine, quadrants } = opts
  const dpr = window.devicePixelRatio || 1
  const W   = canvas.offsetWidth
  const H   = canvas.offsetHeight
  canvas.width  = W * dpr
  canvas.height = H * dpr
  const ctx = canvas.getContext('2d')
  ctx.scale(dpr, dpr)

  const PAD = { top: 20, right: 20, bottom: 40, left: 50 }
  const cW  = W - PAD.left - PAD.right
  const cH  = H - PAD.top  - PAD.bottom

  // Compute domains
  const xs    = data.map(r => r[xKey])
  const ys    = data.map(r => r[yKey])
  const sizes = sizeKey ? data.map(r => r[sizeKey] || 0) : null
  const xMin  = Math.min(...xs), xMax = Math.max(...xs)
  const yMin  = Math.min(...ys), yMax = Math.max(...ys)
  const xPad  = (xMax - xMin) * 0.1 || 1
  const yPad  = (yMax - yMin) * 0.1 || 1
  const xd    = [xMin - xPad, xMax + xPad]
  const yd    = [yMin - yPad, yMax + yPad]

  const sizeMin = sizes ? Math.min(...sizes) : 0
  const sizeMax = sizes ? Math.max(...sizes) : 0
  const sRange  = sizeMax - sizeMin || 1

  function toScreen(x, y) {
    return {
      sx: PAD.left + ((x - xd[0]) / (xd[1] - xd[0])) * cW,
      sy: PAD.top  + (1 - (y - yd[0]) / (yd[1] - yd[0])) * cH,
    }
  }

  // Grid
  const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  const gridCol = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)'
  const tickCol = isDark ? 'rgba(255,255,255,0.3)'  : 'rgba(0,0,0,0.35)'
  const textCol = isDark ? 'rgba(255,255,255,0.6)'  : 'rgba(0,0,0,0.5)'

  ctx.font = `12px var(--font-mono, monospace)`
  const TICKS = 5
  for (let i = 0; i <= TICKS; i++) {
    const x = PAD.left + (i / TICKS) * cW
    const y = PAD.top  + (i / TICKS) * cH
    ctx.strokeStyle = gridCol
    ctx.lineWidth   = 0.5
    // Horizontal grid
    ctx.beginPath(); ctx.moveTo(PAD.left, y); ctx.lineTo(PAD.left + cW, y); ctx.stroke()
    // Vertical grid
    ctx.beginPath(); ctx.moveTo(x, PAD.top); ctx.lineTo(x, PAD.top + cH); ctx.stroke()
    // X tick labels
    const xVal = xd[0] + (i / TICKS) * (xd[1] - xd[0])
    ctx.fillStyle = textCol
    ctx.textAlign = 'center'
    ctx.fillText(xFormat ? xFormat(xVal) : xVal.toFixed(1), x, H - PAD.bottom + 14)
    // Y tick labels
    const yVal = yd[0] + (1 - i / TICKS) * (yd[1] - yd[0])
    ctx.textAlign = 'right'
    ctx.fillText(yFormat ? yFormat(yVal) : yVal.toFixed(1), PAD.left - 6, PAD.top + (i / TICKS) * cH + 4)
  }

  // Axis labels
  if (xLabel) {
    ctx.font = `12px var(--font-sans, system-ui)`
    ctx.fillStyle = textCol; ctx.textAlign = 'center'
    ctx.fillText(xLabel, PAD.left + cW / 2, H - 4)
  }
  if (yLabel) {
    ctx.save(); ctx.translate(12, PAD.top + cH / 2); ctx.rotate(-Math.PI / 2)
    ctx.font = `12px var(--font-sans, system-ui)`
    ctx.textAlign = 'center'; ctx.fillStyle = textCol; ctx.fillText(yLabel, 0, 0)
    ctx.restore()
  }

  // Quadrant crosshair
  if (quadrants) {
    const medX = (xMax + xMin) / 2
    const medY = (yMax + yMin) / 2
    const { sx: qx } = toScreen(medX, yd[0])
    const { sy: qy } = toScreen(xd[0], medY)
    ctx.strokeStyle = 'rgba(0,0,0,0.06)'; ctx.lineWidth = 0.5
    ctx.beginPath(); ctx.moveTo(qx, PAD.top); ctx.lineTo(qx, PAD.top + cH); ctx.stroke()
    ctx.beginPath(); ctx.moveTo(PAD.left, qy); ctx.lineTo(PAD.left + cW, qy); ctx.stroke()
  }

  // Reference lines
  referenceLines?.forEach(rl => {
    ctx.strokeStyle = rl.color || 'rgba(0,0,0,0.15)'
    ctx.lineWidth   = 1
    ctx.setLineDash([4, 3])
    if (rl.x !== undefined) {
      const { sx } = toScreen(rl.x, yd[0])
      ctx.beginPath(); ctx.moveTo(sx, PAD.top); ctx.lineTo(sx, PAD.top + cH); ctx.stroke()
    }
    if (rl.y !== undefined) {
      const { sy } = toScreen(xd[0], rl.y)
      ctx.beginPath(); ctx.moveTo(PAD.left, sy); ctx.lineTo(PAD.left + cW, sy); ctx.stroke()
    }
    ctx.setLineDash([])
  })

  // Trend line
  if (trendLine) {
    const pts = data.map(r => ({ x: r[xKey], y: r[yKey] }))
    const ols = olsLine(pts)
    if (ols) {
      const x1 = xd[0], x2 = xd[1]
      const p1  = toScreen(x1, ols.m * x1 + ols.b)
      const p2  = toScreen(x2, ols.m * x2 + ols.b)
      ctx.strokeStyle = 'rgba(0,0,0,0.2)'; ctx.lineWidth = 1.5
      ctx.setLineDash([4, 3])
      ctx.beginPath(); ctx.moveTo(p1.sx, p1.sy); ctx.lineTo(p2.sx, p2.sy); ctx.stroke()
      ctx.setLineDash([])
    }
  }

  // Bubbles
  data.forEach((row, i) => {
    const { sx, sy } = toScreen(row[xKey], row[yKey])
    const r = sizes
      ? 5 + ((row[sizeKey] - sizeMin) / sRange) * 18
      : 7
    const baseColor = colorKey && colorMap && row[colorKey]
      ? (colorMap[row[colorKey]] || color.series[0])
      : (colorKey && row[colorKey])
      ? (SECTOR_COLORS[row[colorKey]] || color.series[i % color.series.length])
      : color.series[0]

    // Fill
    ctx.globalAlpha = 0.7
    ctx.fillStyle   = baseColor
    ctx.beginPath(); ctx.arc(sx, sy, r, 0, Math.PI * 2); ctx.fill()
    // Stroke
    ctx.globalAlpha = 1
    ctx.strokeStyle = baseColor; ctx.lineWidth = 1.5
    ctx.beginPath(); ctx.arc(sx, sy, r, 0, Math.PI * 2); ctx.stroke()

    // Label inside bubble
    if (labelKey && r >= 10) {
      ctx.fillStyle  = '#fff'
      ctx.font       = `500 12px var(--font-sans, system-ui)`
      ctx.textAlign  = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText(row[labelKey], sx, sy)
    }
  })
  ctx.globalAlpha = 1
}

// ─── FKScatterChart ───────────────────────────────────────────────────────────
export function FKScatterChart({
  data,
  xKey          = 'volatility',
  yKey          = 'return_pct',
  sizeKey,
  colorKey,
  colorMap,
  labelKey,
  xLabel,
  yLabel,
  xFormat,
  yFormat,
  referenceLines,
  trendLine     = false,
  quadrants     = false,
  height        = 280,
  title,
  subtitle,
  stats,
}) {
  const canvasRef = useRef(null)
  const resolvedData = data || SAMPLE_DATA

  const drawAll = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    draw(canvas, resolvedData, { xKey, yKey, sizeKey, colorKey, colorMap, labelKey, xLabel, yLabel, xFormat, yFormat, referenceLines, trendLine, quadrants })
  }, [resolvedData, xKey, yKey, sizeKey, colorKey, colorMap, labelKey, xLabel, yLabel, xFormat, yFormat, referenceLines, trendLine, quadrants])

  useEffect(() => {
    drawAll()
    const canvas = canvasRef.current
    if (!canvas) return
    const ro = new ResizeObserver(drawAll)
    ro.observe(canvas.parentElement || canvas)
    return () => ro.disconnect()
  }, [drawAll])

  return (
    <FKCard>
      <FKCardHeader title={title} subtitle={subtitle} />
      <div style={{ padding: '8px 8px 0', height, position: 'relative' }}>
        <canvas ref={canvasRef} style={{ width: '100%', height: '100%', display: 'block' }} />
      </div>
      {stats && <FKStatStrip stats={stats} />}
    </FKCard>
  )
}
