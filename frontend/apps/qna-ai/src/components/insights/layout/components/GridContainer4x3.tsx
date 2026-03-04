/**
 * Layout Component: 4x3 Grid Container
 * 
 * Standardized 4-column, 3-row grid system for focus+detail layouts
 * Can be reused in any layout that needs focus area with surrounding context
 */

'use client';

interface GridContainer4x3Props {
  children: React.ReactNode;
  className?: string;
}

export default function GridContainer4x3({ 
  children, 
  className = "" 
}: GridContainer4x3Props) {
  return (
    <div className={`flex-1 grid grid-cols-4 grid-rows-3 gap-4 min-h-0 ${className}`}>
      {children}
    </div>
  );
}