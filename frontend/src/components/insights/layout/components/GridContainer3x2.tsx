/**
 * Layout Component: 3x2 Grid Container
 * 
 * Standardized 3-column, 2-row grid system for multi-chart layouts
 * Can be reused in any layout that needs full-width top with three-way split bottom
 */

'use client';

interface GridContainer3x2Props {
  children: React.ReactNode;
  className?: string;
}

export default function GridContainer3x2({ 
  children, 
  className = "" 
}: GridContainer3x2Props) {
  return (
    <div className={`flex-1 grid grid-cols-3 grid-rows-2 gap-4 min-h-0 ${className}`}>
      {children}
    </div>
  );
}