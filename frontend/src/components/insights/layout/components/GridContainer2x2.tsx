/**
 * Layout Component: 2x2 Grid Container
 * 
 * Standardized 2-column, 2-row grid system for quadrant layouts
 * Can be reused in any layout that needs four equal-weight sections
 */

'use client';

interface GridContainer2x2Props {
  children: React.ReactNode;
  className?: string;
}

export default function GridContainer2x2({ 
  children, 
  className = "" 
}: GridContainer2x2Props) {
  return (
    <div className={`flex-1 grid grid-cols-2 grid-rows-2 gap-4 min-h-0 ${className}`}>
      {children}
    </div>
  );
}