/**
 * Layout Component: 3x4 Grid Container
 * 
 * Standardized 3-column, 4-row grid system for dashboard layouts
 * Can be reused in any layout that needs three-column structure
 */

'use client';

interface GridContainer3x4Props {
  children: React.ReactNode;
  className?: string;
}

export default function GridContainer3x4({ 
  children, 
  className = "" 
}: GridContainer3x4Props) {
  return (
    <div className={`flex-1 grid grid-cols-3 grid-rows-4 gap-4 min-h-0 ${className}`}>
      {children}
    </div>
  );
}