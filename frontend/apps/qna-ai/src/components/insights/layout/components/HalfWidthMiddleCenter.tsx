/**
 * Positional Layout Component: Half Width Middle Center
 * 
 * Grid Position: col-span-2 row-span-3 (in 4x6 grid)
 * Common Uses: Detailed tables, main content, primary data breakdowns
 * Can be reused in any layout wrapper that has a 4-column grid
 */

'use client';

interface HalfWidthMiddleCenterProps {
  children: React.ReactNode;
  className?: string;
}

export default function HalfWidthMiddleCenter({
  children,
  className = ""
}: HalfWidthMiddleCenterProps) {
  return (
    <div className={`col-span-2 row-span-3 ${className}`}>
      <div className="h-full bg-white rounded-lg border border-gray-200">
        {children}
      </div>
    </div>
  );
}