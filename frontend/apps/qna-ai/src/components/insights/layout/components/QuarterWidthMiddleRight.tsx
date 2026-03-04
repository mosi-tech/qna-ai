/**
 * Positional Layout Component: Quarter Width Middle Right
 * 
 * Grid Position: col-span-1 row-span-3 (in 4x6 grid)
 * Common Uses: Insights, sidebar content, secondary metrics, contextual information
 * Can be reused in any layout wrapper that has a 4-column grid
 */

'use client';

interface QuarterWidthMiddleRightProps {
  children: React.ReactNode;
  className?: string;
}

export default function QuarterWidthMiddleRight({
  children,
  className = ""
}: QuarterWidthMiddleRightProps) {
  return (
    <div className={`col-span-1 row-span-3 ${className}`}>
      <div className="h-full bg-white rounded-lg border border-gray-200">
        {children}
      </div>
    </div>
  );
}