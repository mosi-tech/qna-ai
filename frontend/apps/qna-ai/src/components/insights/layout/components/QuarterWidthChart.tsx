/**
 * Positional Layout Component: Quarter Width Chart
 * 
 * Grid Position: col-span-1 row-span-1 (in 4x3 grid)
 * Common Uses: Charts, visualizations, plots, statistical graphics
 * Can be reused in any layout wrapper that has a 4-column structure
 */

'use client';

interface QuarterWidthChartProps {
  children: React.ReactNode;
  className?: string;
}

export default function QuarterWidthChart({
  children,
  className = ""
}: QuarterWidthChartProps) {
  return (
    <div className={`col-span-1 row-span-1 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}