import React from 'react'

export function FKCard({ children, className = '', style }) {
  return (
    <div
      className={`bg-[var(--color-background-primary)] border border-[var(--color-border-tertiary)] rounded-2xl overflow-hidden ${className}`}
      style={style}
    >
      {children}
    </div>
  )
}

export function FKCardHeader({ title, subtitle, actions }) {
  return (
    <div className="flex items-start justify-between px-5 pt-5 pb-0">
      <div>
        {title && (
          <div className="text-[16px] font-sans font-semibold text-[var(--color-text-primary)] leading-tight">
            {title}
          </div>
        )}
        {subtitle && (
          <div className="text-[13px] font-sans text-[var(--color-text-tertiary)] mt-0.5">
            {subtitle}
          </div>
        )}
      </div>
      {actions && (
        <div className="flex items-center gap-2 ml-4 flex-shrink-0">
          {actions}
        </div>
      )}
    </div>
  )
}

export function FKCardBody({ children, className = '' }) {
  return (
    <div className={`px-5 pb-5 pt-3 ${className}`}>
      {children}
    </div>
  )
}
