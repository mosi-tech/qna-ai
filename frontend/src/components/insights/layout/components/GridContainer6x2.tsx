/**
 * Layout Component: 6x2 Grid Container
 * 
 * Standardized 6-column, 2-row grid system for timeline/flow layouts
 * Can be reused in any layout that needs horizontal sequential flow
 */

'use client';

interface GridContainer6x2Props {
  children: React.ReactNode;
  className?: string;
}

export default function GridContainer6x2({ 
  children, 
  className = "" 
}: GridContainer6x2Props) {
  return (
    <div className={`flex-1 grid grid-cols-6 grid-rows-2 gap-4 min-h-0 ${className}`}>
      {children}
    </div>
  );
}