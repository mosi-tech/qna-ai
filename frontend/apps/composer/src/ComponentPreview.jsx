import React from 'react'

// Renders a FK component in an overflow-clipped container
export default function ComponentPreview({ component, width = 'full', height = 240 }) {
  const C = component.component
  const props = component.sampleProps
  return (
    <div style={{ height, overflow: 'hidden', position: 'relative' }}>
      <C {...props} />
    </div>
  )
}
