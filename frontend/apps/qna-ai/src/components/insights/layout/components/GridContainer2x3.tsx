/**
 * Layout Component: 2x3 Grid Container
 * 
 * Standardized 2-column, 3-row grid system for highlight+table+chart layouts
 * Can be reused in any layout that needs top summary with bottom split view
 */

'use client';

interface GridContainer2x3Props {
  children: React.ReactNode;
  className?: string;
}

export default function GridContainer2x3({ 
  children, 
  className = "" 
}: GridContainer2x3Props) {
  return (
    <div className={`flex-1 grid grid-cols-2 grid-rows-3 gap-4 min-h-0 ${className}`}>
      {children}
    </div>
  );
}