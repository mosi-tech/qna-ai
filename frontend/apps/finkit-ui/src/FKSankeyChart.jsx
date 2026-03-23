import React, { useState, useMemo, useRef, useLayoutEffect } from 'react'
import { FKCard, FKCardHeader } from './FKCard.jsx'
import { FKTooltip } from './FKTooltip.jsx'
import { color } from './tokens.js'

// ─── Sample data ──────────────────────────────────────────────────────────────
const SAMPLE_NODES = [
  { id: 'hardware', label: 'Hardware',     column: 0 },
  { id: 'software', label: 'Software',     column: 0 },
  { id: 'services', label: 'Services',     column: 0 },
  { id: 'americas', label: 'Americas',     column: 1 },
  { id: 'europe',   label: 'Europe',       column: 1 },
  { id: 'apac',     label: 'APAC',         column: 1 },
  { id: 'gross',    label: 'Gross Profit', column: 2 },
  { id: 'opex',     label: 'OpEx',         column: 2 },
]
const SAMPLE_FLOWS = [
  { from: 'hardware', to: 'americas', value: 42 },
  { from: 'hardware', to: 'europe',   value: 18 },
  { from: 'software', to: 'americas', value: 55 },
  { from: 'software', to: 'apac',     value: 31 },
  { from: 'services', to: 'americas', value: 28 },
  { from: 'services', to: 'europe',   value: 12 },
  { from: 'americas', to: 'gross',    value: 89 },
  { from: 'europe',   to: 'gross',    value: 34 },
  { from: 'apac',     to: 'gross',    value: 41 },
  { from: 'americas', to: 'opex',     value: 36 },
  { from: 'europe',   to: 'opex',     value: 14 },
]

const NODE_W  = 16
const NODE_GAP = 10

// ─── Layout calculation ────────────────────────────────────────────────────────
function calcLayout(nodes, flows, W, H) {
  const PAD_X = 60, PAD_Y = 24

  // Group nodes by column
  const colMap = {}
  nodes.forEach(n => { colMap[n.column] = (colMap[n.column] || []) ; colMap[n.column].push(n.id) })
  const cols = Object.keys(colMap).map(Number).sort((a, b) => a - b)
  const numCols = cols.length

  // Total flow per node
  const nodeValue = {}
  nodes.forEach(n => { nodeValue[n.id] = 0 })
  flows.forEach(f => {
    nodeValue[f.from] = (nodeValue[f.from] || 0) + f.value
    nodeValue[f.to]   = (nodeValue[f.to]   || 0) + f.value
  })

  // Column x positions
  const colX = {}
  cols.forEach((c, i) => {
    colX[c] = PAD_X + i * ((W - PAD_X * 2 - NODE_W) / (numCols - 1 || 1))
  })

  // Node y positions within each column
  const nodePos = {}
  cols.forEach(c => {
    const colNodes = colMap[c]
    const colTotal = colNodes.reduce((a, id) => a + (nodeValue[id] || 1), 0)
    const availH   = H - PAD_Y * 2 - (colNodes.length - 1) * NODE_GAP
    let   y        = PAD_Y
    colNodes.forEach(id => {
      const h = Math.max(8, (nodeValue[id] || 1) / colTotal * availH)
      nodePos[id] = { x: colX[c], y, h, column: c }
      y += h + NODE_GAP
    })
  })

  // Flow y offsets (how far down each node edge we've consumed)
  const fromOffset = {}, toOffset = {}
  nodes.forEach(n => { fromOffset[n.id] = 0; toOffset[n.id] = 0 })

  const flowPaths = flows.map(f => {
    const src   = nodePos[f.from], dst = nodePos[f.to]
    if (!src || !dst) return null

    const srcTotal = nodeValue[f.from] || 1
    const dstTotal = nodeValue[f.to]   || 1
    const fh       = (f.value / srcTotal) * src.h
    const th       = (f.value / dstTotal) * dst.h

    const y1s = src.y + fromOffset[f.from]
    const y1e = y1s + fh
    const y2s = dst.y + toOffset[f.to]
    const y2e = y2s + th

    fromOffset[f.from] += fh
    toOffset[f.to]     += th

    const x1 = src.x + NODE_W
    const x2 = dst.x
    const mx = (x1 + x2) / 2

    const path = `M ${x1} ${y1s} C ${mx} ${y1s}, ${mx} ${y2s}, ${x2} ${y2s}
                  L ${x2} ${y2e} C ${mx} ${y2e}, ${mx} ${y1e}, ${x1} ${y1e} Z`

    const nodeColor = SAMPLE_NODES.find(n => n.id === f.from)?.color ||
                      color.series[(nodePos[f.from]?.column || 0) % color.series.length]

    return { ...f, path, nodeColor, y1s, y1e, y2s, y2e }
  }).filter(Boolean)

  return { nodePos, flowPaths, colX, cols }
}

// ─── FKSankeyChart ────────────────────────────────────────────────────────────
export function FKSankeyChart({
  nodes,
  flows,
  valueFormat,
  title,
  subtitle,
  height = 400,
}) {
  const resolvedNodes  = nodes  || SAMPLE_NODES
  const resolvedFlows  = flows  || SAMPLE_FLOWS
  const fmt            = valueFormat || (v => v.toLocaleString())

  const [tooltip, setTooltip]   = useState(null)
  const [hovNode, setHovNode]   = useState(null)
  const [hovFlow, setHovFlow]   = useState(null)
  const containerRef = useRef(null)
  const [width, setWidth]       = useState(640)

  useLayoutEffect(() => {
    const el = containerRef.current
    if (!el) return
    const ro = new ResizeObserver(() => setWidth(el.clientWidth))
    ro.observe(el)
    setWidth(el.clientWidth)
    return () => ro.disconnect()
  }, [])

  const { nodePos, flowPaths, cols } = useMemo(
    () => calcLayout(resolvedNodes, resolvedFlows, width, height - 40),
    [resolvedNodes, resolvedFlows, width, height]
  )

  const isLastCol = (col) => col === Math.max(...cols)

  return (
    <FKCard>
      <FKCardHeader title={title} subtitle={subtitle} />
      <div ref={containerRef} style={{ padding: '12px 0 16px', position: 'relative' }}>
        <svg width={width} height={height - 40} style={{ display: 'block', overflow: 'visible' }}>
          {/* Flow paths */}
          {flowPaths.map((f, i) => {
            const isHov     = hovFlow === i
            const nodeIsHov = hovNode === f.from || hovNode === f.to
            const opacity   = hovFlow !== null ? (isHov ? 0.45 : 0.1)
                            : hovNode !== null ? (nodeIsHov ? 0.45 : 0.1)
                            : 0.25
            return (
              <path
                key={i}
                d={f.path}
                fill={f.nodeColor}
                opacity={opacity}
                style={{ cursor: 'default', transition: 'opacity 0.15s' }}
                onMouseEnter={e => { setHovFlow(i); setTooltip({ f, x: e.nativeEvent.offsetX, y: e.nativeEvent.offsetY }) }}
                onMouseLeave={() => { setHovFlow(null); setTooltip(null) }}
              />
            )
          })}

          {/* Nodes */}
          {resolvedNodes.map((n, i) => {
            const pos  = nodePos[n.id]
            if (!pos) return null
            const c    = n.color || color.series[pos.column % color.series.length]
            const last = isLastCol(pos.column)
            const isHov = hovNode === n.id
            return (
              <g key={n.id}
                onMouseEnter={() => setHovNode(n.id)}
                onMouseLeave={() => setHovNode(null)}
                style={{ cursor: 'default' }}
              >
                <rect
                  x={pos.x} y={pos.y}
                  width={NODE_W} height={pos.h}
                  rx={3} fill={c}
                  opacity={isHov ? 1 : 0.85}
                />
                <text
                  x={last ? pos.x - 6 : pos.x + NODE_W + 6}
                  y={pos.y + pos.h / 2}
                  textAnchor={last ? 'end' : 'start'}
                  dominantBaseline="middle"
                  fontSize={11}
                  fontFamily="var(--font-mono)"
                  fill="var(--color-text-primary)"
                >
                  {n.label}
                </text>
              </g>
            )
          })}
        </svg>

        {tooltip && (
          <div style={{ position: 'absolute', left: Math.min(tooltip.x + 8, width - 180), top: tooltip.y - 8, pointerEvents: 'none', zIndex: 50 }}>
            <FKTooltip.Box style={{ position: 'relative' }}>
              <FKTooltip.Header>
                {tooltip.f.from} → {tooltip.f.to}
              </FKTooltip.Header>
              <FKTooltip.Row color={tooltip.f.nodeColor} label="Flow" value={fmt(tooltip.f.value)} />
            </FKTooltip.Box>
          </div>
        )}
      </div>
    </FKCard>
  )
}
