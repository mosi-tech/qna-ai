import React from 'react'

export function FKCard({ children, className = '', style }) {
  return (
    <div
      className={`rounded-xl overflow-hidden ${className}`}
      style={{
        background:   'var(--color-background-primary)',
        border:       '0.5px solid var(--color-border-tertiary)',
        borderRadius: 12,
        overflow:     'hidden',
        ...style,
      }}
    >
      {children}
    </div>
  )
}

export function FKCardHeader({ title, subtitle, actions }) {
  return (
    <div className="flex justify-between items-start" style={{ padding: '18px 20px 0' }}>
      <div>
        {title && (
          <div
            className="text-sm font-medium"
            style={{ color: 'var(--color-text-primary)', marginBottom: 2 }}
          >
            {title}
          </div>
        )}
        {subtitle && (
          <div className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>
            {subtitle}
          </div>
        )}
      </div>
      {actions && (
        <div className="flex gap-1.5 items-center">{actions}</div>
      )}
    </div>
  )
}
