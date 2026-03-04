/**
 * Layout Component: 4x3 Mixed Grid Container
 * 
 * Grid system for multi-chart layouts with detailed table
 * Layout structure:
 * - Row 1: Full width (4 cols)
 * - Row 2: Four equal chart sections (1 col each)
 * - Row 3: Full width table (4 cols)
 */

'use client';

interface GridContainer4x3MixedProps {
  children: React.ReactNode;
  className?: string;
}

export default function GridContainer4x3Mixed({ 
  children, 
  className = "" 
}: GridContainer4x3MixedProps) {
  return (
    <div className={`flex-1 grid grid-cols-4 grid-rows-3 gap-4 min-h-0 ${className}`}>
      {children}
    </div>
  );
}