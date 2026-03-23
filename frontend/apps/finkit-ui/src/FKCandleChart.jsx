import React, { useRef, useEffect, useCallback, useState } from 'react'
import { FKCard, FKCardHeader } from './FKCard.jsx'
import { FKTooltip } from './FKTooltip.jsx'
import { FKRangeSelector } from './FKRangeSelector.jsx'
import { FKStatStrip, FKBadge } from './FKSparkline.jsx'
import { color } from './tokens.js'

// ─── Sample OHLCV data ────────────────────────────────────────────────────────
function makeSampleOHLCV(n = 500) {
  let price = 200
  const result = []
  let d = new Date('2022-01-03')
  for (let i = 0; i < n; i++) {
    if (d.getDay() === 0) { d.setDate(d.getDate() + 1) }
    if (d.getDay() === 6) { d.setDate(d.getDate() + 2) }
    const open   = price
    const change = (Math.random() - 0.48) * price * 0.02
    const close  = parseFloat(Math.max(1, open + change).toFixed(2))
    const high   = parseFloat((Math.max(open, close) * (1 + Math.random() * 0.008)).toFixed(2))
    const low    = parseFloat((Math.min(open, close) * (1 - Math.random() * 0.008)).toFixed(2))
    const volume = Math.floor(40_000_000 + Math.random() * 80_000_000)
    result.push({ date: d.toISOString().slice(0, 10), open, close, high, low, volume })
    price = close
    d = new Date(d); d.setDate(d.getDate() + 1)
  }
  return result
}
const SAMPLE_DATA = makeSampleOHLCV()

const RANGE_COUNTS = { '1M': 21, '3M': 63, '6M': 126, '1Y': 252, '3Y': 756, '5Y': 1260 }

// ─── Canvas draw ──────────────────────────────────────────────────────────────
function drawCandles(canvas, data, opts, tooltip) {
  const { height, showVolume, yAxisW = 56 } = opts
  const dpr = window.devicePixelRatio || 1
  const W   = canvas.offsetWidth
  const H   = height
  canvas.width  = W * dpr
  canvas.height = H * dpr
  canvas.style.height = H + 'px'
  const ctx = canvas.getContext('2d')
  ctx.scale(dpr, dpr)

  const isDark  = window.matchMedia('(prefers-color-scheme: dark)').matches
  const gridCol = isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)'
  const textCol = isDark ? 'rgba(255,255,255,0.35)'  : 'rgba(0,0,0,0.35)'

  const PAD   = { top: 12, right: yAxisW, bottom: showVolume ? 64 : 28, left: 8 }
  const volH  = showVolume ? 48 : 0
  const chartH = H - PAD.top - PAD.bottom - volH
  const cW    = W - PAD.left - PAD.right
  const n     = data.length
  if (!n) return

  const allHigh = data.map(r => r.high)
  const allLow  = data.map(r => r.low)
  const yMin    = Math.min(...allLow) * 0.998
  const yMax    = Math.max(...allHigh) * 1.002
  const allVol  = data.map(r => r.volume || 0)
  const volMax  = Math.max(...allVol) || 1

  const toY    = v => PAD.top + (1 - (v - yMin) / (yMax - yMin)) * chartH
  const candleW = Math.max(1, Math.floor(cW / n) - 1)
  const toX    = i => PAD.left + (i + 0.5) * (cW / n)

  // Y grid + labels
  ctx.font = `12px var(--font-mono, monospace)`
  for (let t = 0; t <= 4; t++) {
    const yv = yMin + (t / 4) * (yMax - yMin)
    const sy = toY(yv)
    ctx.strokeStyle = gridCol; ctx.lineWidth = 0.5
    ctx.beginPath(); ctx.moveTo(PAD.left, sy); ctx.lineTo(W - PAD.right, sy); ctx.stroke()
    ctx.fillStyle = textCol; ctx.textAlign = 'right'
    ctx.fillText(`$${yv.toFixed(0)}`, W - 4, sy + 3)
  }

  // Candles
  data.forEach((row, i) => {
    const isUp = row.close >= row.open
    const fill = isUp ? color.gain : color.loss
    const cx   = toX(i)
    const oy   = toY(row.open), cy = toY(row.close), hy = toY(row.high), ly = toY(row.low)
    const bTop = Math.min(oy, cy), bH = Math.max(1, Math.abs(cy - oy))
    ctx.strokeStyle = fill; ctx.lineWidth = 1
    ctx.beginPath(); ctx.moveTo(cx, hy); ctx.lineTo(cx, ly); ctx.stroke()
    ctx.fillStyle = fill
    const hw = Math.max(1, candleW / 2)
    ctx.beginPath(); ctx.roundRect(cx - hw, bTop, hw * 2, bH, 1); ctx.fill()
  })

  // Crosshair
  if (tooltip?.hovIdx != null) {
    const cx = toX(tooltip.hovIdx)
    ctx.strokeStyle = isDark ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.15)'
    ctx.lineWidth = 0.5; ctx.setLineDash([3, 3])
    ctx.beginPath(); ctx.moveTo(cx, PAD.top); ctx.lineTo(cx, PAD.top + chartH); ctx.stroke()
    ctx.setLineDash([])
  }

  // Volume bars
  if (showVolume) {
    const volTop = PAD.top + chartH + 8
    data.forEach((row, i) => {
      const bH = (row.volume / volMax) * (volH - 4)
      const cx = toX(i)
      const hw = Math.max(1, candleW / 2)
      ctx.fillStyle = row.close >= row.open ? 'rgba(22,163,74,0.4)' : 'rgba(220,38,38,0.4)'
      ctx.fillRect(cx - hw, volTop + (volH - bH), hw * 2, bH)
    })
    ctx.fillStyle = textCol; ctx.font = `12px var(--font-mono, monospace)`
    ctx.textAlign = 'left'
    ctx.fillText('Volume', PAD.left + 4, volTop + 10)
  }

  // X labels (every ~8 candles)
  const step = Math.max(1, Math.ceil(n / 7))
  ctx.fillStyle = textCol; ctx.font = `12px var(--font-mono, monospace)`
  ctx.textAlign = 'center'
  data.forEach((row, i) => {
    if (i % step !== 0) return
    const label = typeof row.date === 'string' ? row.date.slice(0, 7) : row.date
    ctx.fillText(label, toX(i), H - (showVolume ? 8 : 6))
  })

  // Store layout info for hit testing
  canvas._layout = { toX, PAD, cW, n, yAxisW, candleW }
}

// ─── FKCandleChart ────────────────────────────────────────────────────────────
export function FKCandleChart({
  data,
  height       = 320,
  showVolume   = true,
  rangeSelector = true,
  defaultRange = '6M',
  title,
  subtitle,
  badge,
  stats,
}) {
  const allData   = data || SAMPLE_DATA
  const totalN    = allData.length

  const [viewCount, setViewCount] = useState(() => {
    const c = RANGE_COUNTS[defaultRange] || 126
    return Math.min(c, totalN)
  })
  const [viewStart, setViewStart] = useState(() => Math.max(0, totalN - (RANGE_COUNTS[defaultRange] || 126)))
  const [range, setRange]         = useState(defaultRange)
  const [hovIdx, setHovIdx]       = useState(null)
  const [tooltipData, setTooltipData] = useState(null)
  const [tooltipPos, setTooltipPos]   = useState({ x: 0, y: 0 })

  const canvasRef  = useRef(null)
  const isDragging = useRef(false)
  const dragStartX = useRef(0)
  const dragStartViewStart = useRef(0)
  const tooltipRef = useRef({ hovIdx: null })

  const visibleData = allData.slice(viewStart, viewStart + viewCount)

  const redraw = useCallback(() => {
    const c = canvasRef.current
    if (!c) return
    drawCandles(c, visibleData, { height, showVolume }, tooltipRef.current)
  }, [visibleData, height, showVolume])

  useEffect(() => { redraw() }, [redraw])

  useEffect(() => {
    const c = canvasRef.current
    if (!c) return
    const ro = new ResizeObserver(redraw)
    ro.observe(c.parentElement || c)
    return () => ro.disconnect()
  }, [redraw])

  // ── Range selector ──────────────────────────────────────────────────────────
  const rangeOptions = Array.isArray(rangeSelector) ? rangeSelector : ['1M','3M','6M','1Y','3Y','5Y','ALL']

  function handleRangeChange(r) {
    setRange(r)
    const cnt = r === 'ALL' ? totalN : Math.min(RANGE_COUNTS[r] || 126, totalN)
    setViewCount(cnt)
    setViewStart(Math.max(0, totalN - cnt))
  }

  // ── Mouse interactions ──────────────────────────────────────────────────────
  function getHovIdx(e) {
    const c = canvasRef.current
    if (!c?._layout) return null
    const rect = c.getBoundingClientRect()
    const mx = e.clientX - rect.left
    const { PAD, cW, n } = c._layout
    if (mx < PAD.left || mx > PAD.left + cW) return null
    const idx = Math.floor((mx - PAD.left) / (cW / n))
    return idx >= 0 && idx < n ? idx : null
  }

  const handleMouseMove = useCallback((e) => {
    if (isDragging.current) {
      const dx   = e.clientX - dragStartX.current
      const step = Math.floor(-dx / 4)
      const ns   = Math.max(0, Math.min(totalN - viewCount, dragStartViewStart.current + step))
      setViewStart(ns)
      return
    }
    const idx = getHovIdx(e)
    tooltipRef.current = { hovIdx: idx }
    setHovIdx(idx)
    if (idx != null) {
      const row = visibleData[idx]
      setTooltipData(row)
      const rect = canvasRef.current.getBoundingClientRect()
      setTooltipPos({ x: e.clientX - rect.left, y: e.clientY - rect.top })
    } else {
      setTooltipData(null)
    }
  }, [visibleData, totalN, viewCount])

  const handleMouseDown = useCallback((e) => {
    isDragging.current = true
    dragStartX.current = e.clientX
    dragStartViewStart.current = viewStart
  }, [viewStart])

  const handleMouseUp = useCallback(() => { isDragging.current = false }, [])

  const handleWheel = useCallback((e) => {
    e.preventDefault()
    if (Math.abs(e.deltaY) > Math.abs(e.deltaX)) {
      // Vertical scroll → zoom
      const delta = e.deltaY > 0 ? 10 : -10
      const newCount = Math.max(20, Math.min(totalN, viewCount + delta))
      setViewCount(newCount)
      setViewStart(vs => Math.max(0, Math.min(totalN - newCount, vs)))
    } else {
      // Horizontal scroll → pan
      const step = Math.round(e.deltaX / 4)
      setViewStart(vs => Math.max(0, Math.min(totalN - viewCount, vs + step)))
    }
  }, [viewCount, totalN])

  const handleMouseLeave = useCallback(() => {
    tooltipRef.current = { hovIdx: null }
    setHovIdx(null)
    setTooltipData(null)
    isDragging.current = false
  }, [])

  // Scrollbar drag
  const scrollbarRef = useRef(null)
  const isScrollDragging = useRef(false)
  const scrollDragStartX = useRef(0)
  const scrollDragStartVS = useRef(0)

  function handleScrollbarMouseDown(e) {
    isScrollDragging.current = true
    scrollDragStartX.current = e.clientX
    scrollDragStartVS.current = viewStart
    e.preventDefault()
  }

  useEffect(() => {
    function onMove(e) {
      if (!isScrollDragging.current) return
      const sb = scrollbarRef.current
      if (!sb) return
      const trackW = sb.offsetWidth
      const dx = e.clientX - scrollDragStartX.current
      const scrollRange = totalN - viewCount
      const fraction = dx / trackW
      const ns = Math.max(0, Math.min(scrollRange, Math.round(scrollDragStartVS.current + fraction * totalN)))
      setViewStart(ns)
    }
    function onUp() { isScrollDragging.current = false }
    document.addEventListener('mousemove', onMove)
    document.addEventListener('mouseup', onUp)
    return () => { document.removeEventListener('mousemove', onMove); document.removeEventListener('mouseup', onUp) }
  }, [totalN, viewCount])

  const thumbW   = Math.max(24, (viewCount / totalN) * 100)
  const thumbLeft = (viewStart / totalN) * 100

  const actions = rangeSelector
    ? <FKRangeSelector options={rangeOptions} value={range} onChange={handleRangeChange} />
    : badge
    ? <FKBadge variant="neutral">{badge}</FKBadge>
    : null

  return (
    <FKCard>
      <FKCardHeader title={title} subtitle={subtitle} actions={actions} />
      <div
        style={{ padding: '8px 0 0', position: 'relative', cursor: isDragging.current ? 'grabbing' : 'crosshair' }}
        onMouseMove={handleMouseMove}
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseLeave}
        onWheel={handleWheel}
      >
        <canvas
          ref={canvasRef}
          style={{ width: '100%', height, display: 'block', userSelect: 'none' }}
        />

        {/* Scrollbar */}
        <div
          ref={scrollbarRef}
          style={{
            height: 4, margin: '4px 8px 8px',
            background: 'var(--color-border-tertiary)',
            borderRadius: 99, position: 'relative',
          }}
        >
          <div
            onMouseDown={handleScrollbarMouseDown}
            style={{
              position:     'absolute',
              top:          0,
              left:         `${thumbLeft}%`,
              width:        `${thumbW}%`,
              height:       '100%',
              background:   'var(--color-text-tertiary)',
              borderRadius: 99,
              cursor:       'grab',
            }}
          />
        </div>

        {/* OHLC Tooltip */}
        {tooltipData && (
          <FKTooltip.OHLC
            active
            payload={[{ payload: tooltipData }]}
            label={tooltipData.date}
            valueFormat={v => `$${v?.toFixed(2)}`}
          />
        )}
        {tooltipData && (
          <div style={{
            position:      'absolute',
            pointerEvents: 'none',
            left:          Math.min(tooltipPos.x + 12, canvasRef.current?.offsetWidth - 160 || 0),
            top:           tooltipPos.y,
            transform:     'translateY(-50%)',
            zIndex:        50,
          }}>
            <FKTooltip.OHLC
              active
              payload={[{ payload: tooltipData }]}
              label={tooltipData.date}
              valueFormat={v => `$${v?.toFixed(2)}`}
            />
          </div>
        )}
      </div>
      {stats && <FKStatStrip stats={stats} />}
    </FKCard>
  )
}
