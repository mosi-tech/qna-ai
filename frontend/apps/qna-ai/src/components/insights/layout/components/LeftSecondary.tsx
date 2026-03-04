/**
 * Positional Layout Component: Left Secondary
 * 
 * Grid Position: col-span-1 row-span-2 (in 2x5 grid)
 * Common Uses: Left side secondary analysis, detailed breakdown, supporting data
 * Can be reused in any layout wrapper that has a 2-column comparison grid
 */

'use client';

interface LeftSecondaryProps {
  children: React.ReactNode;
  className?: string;
}

export default function LeftSecondary({
  children,
  className = ""
}: LeftSecondaryProps) {
  return (
    <div className={`col-span-1 row-span-2 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}