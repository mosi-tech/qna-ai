/**
 * Positional Layout Component: Quarter Width Middle Left
 * 
 * Grid Position: col-span-1 row-span-3 (in 4x6 grid)
 * Common Uses: Highlights, sidebar content, secondary metrics
 * Can be reused in any layout wrapper that has a 4-column grid
 */

'use client';

interface QuarterWidthMiddleLeftProps {
  children: React.ReactNode;
  className?: string;
}

export default function QuarterWidthMiddleLeft({
  children,
  className = ""
}: QuarterWidthMiddleLeftProps) {
  return (
    <div className={`col-span-1 row-span-3 ${className}`}>
      <div className="h-full bg-white rounded-lg border border-gray-200">
        {children}
      </div>
    </div>
  );
}