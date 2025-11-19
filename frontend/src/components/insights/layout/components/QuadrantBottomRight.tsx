/**
 * Positional Layout Component: Quadrant Bottom Right
 * 
 * Grid Position: col-span-1 row-span-1 (in 2x2 grid)
 * Common Uses: Heatmaps, histograms, distribution charts, correlation matrices
 * Can be reused in any layout wrapper that has a 2x2 quadrant structure
 */

'use client';

interface QuadrantBottomRightProps {
  children: React.ReactNode;
  className?: string;
}

export default function QuadrantBottomRight({
  children,
  className = ""
}: QuadrantBottomRightProps) {
  return (
    <div className={`col-span-1 row-span-1 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}