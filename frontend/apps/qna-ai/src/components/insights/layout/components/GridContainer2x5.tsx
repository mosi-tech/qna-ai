/**
 * Layout Component: 2x5 Grid Container
 * 
 * Standardized 2-column, 5-row grid system for comparisons
 * Can be reused in any layout that needs side-by-side comparison structure
 */

'use client';

interface GridContainer2x5Props {
  children: React.ReactNode;
  className?: string;
}

export default function GridContainer2x5({ 
  children, 
  className = "" 
}: GridContainer2x5Props) {
  return (
    <div className={`flex-1 grid grid-cols-2 grid-rows-5 gap-4 min-h-0 ${className}`}>
      {children}
    </div>
  );
}