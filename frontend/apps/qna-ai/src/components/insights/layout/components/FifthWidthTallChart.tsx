/**
 * Positional Layout Component: Fifth Width Tall Chart
 * 
 * Grid Position: col-span-1 row-span-2 (in 5x4 grid)
 * Common Uses: Tall charts, vertical visualizations, scatter plots
 * Can be reused in any layout wrapper that has a 5-column structure
 */

'use client';

interface FifthWidthTallChartProps {
  children: React.ReactNode;
  className?: string;
}

export default function FifthWidthTallChart({
  children,
  className = ""
}: FifthWidthTallChartProps) {
  return (
    <div className={`col-span-1 row-span-2 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}