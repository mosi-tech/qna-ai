/**
 * Layout Component: 3x3 Mixed Grid Container
 * 
 * Complex grid system for comprehensive dashboards with mixed spans
 * Layout structure:
 * - Row 1: Full width (3 cols)
 * - Row 2: Three equal sections (1 col each)
 * - Row 3: Two-thirds + one-third (2 cols + 1 col)
 */

'use client';

interface GridContainer3x3MixedProps {
  children: React.ReactNode;
  className?: string;
}

export default function GridContainer3x3Mixed({ 
  children, 
  className = "" 
}: GridContainer3x3MixedProps) {
  return (
    <div className={`flex-1 grid grid-cols-3 grid-rows-3 gap-4 min-h-0 ${className}`}>
      {children}
    </div>
  );
}