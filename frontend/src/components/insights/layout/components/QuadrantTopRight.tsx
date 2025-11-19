/**
 * Positional Layout Component: Quadrant Top Right
 * 
 * Grid Position: col-span-1 row-span-1 (in 2x2 grid)
 * Common Uses: Time-series charts, trend visualizations, performance graphs
 * Can be reused in any layout wrapper that has a 2x2 quadrant structure
 */

'use client';

interface QuadrantTopRightProps {
  children: React.ReactNode;
  className?: string;
}

export default function QuadrantTopRight({
  children,
  className = ""
}: QuadrantTopRightProps) {
  return (
    <div className={`col-span-1 row-span-1 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}