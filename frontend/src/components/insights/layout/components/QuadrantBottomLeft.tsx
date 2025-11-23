/**
 * Positional Layout Component: Quadrant Bottom Left
 * 
 * Grid Position: col-span-1 row-span-1 (in 2x2 grid)
 * Common Uses: Breakdown tables, detailed metrics, data analysis
 * Can be reused in any layout wrapper that has a 2x2 quadrant structure
 */

'use client';

interface QuadrantBottomLeftProps {
  children: React.ReactNode;
  className?: string;
}

export default function QuadrantBottomLeft({
  children,
  className = ""
}: QuadrantBottomLeftProps) {
  return (
    <div className={`col-span-1 row-span-1 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}