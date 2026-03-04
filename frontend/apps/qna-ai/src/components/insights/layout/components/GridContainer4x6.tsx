/**
 * Layout Component: 4x6 Grid Container
 * 
 * Standardized 4-column, 6-row grid system
 * Can be reused in any layout that needs this grid structure
 */

'use client';

interface GridContainer4x6Props {
  children: React.ReactNode;
  className?: string;
}

export default function GridContainer4x6({ 
  children, 
  className = "" 
}: GridContainer4x6Props) {
  return (
    <div className={`flex-1 grid grid-cols-4 grid-rows-6 gap-4 min-h-0 ${className}`}>
      {children}
    </div>
  );
}