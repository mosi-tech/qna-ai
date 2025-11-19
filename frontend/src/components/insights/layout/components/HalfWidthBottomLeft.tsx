/**
 * Positional Layout Component: Half Width Bottom Left
 * 
 * Grid Position: col-span-2 row-span-1 (in 4x3 grid, bottom row)
 * Common Uses: Heatmaps, correlation matrices, large visualizations
 * Can be reused in any layout wrapper that has a 4-column structure
 */

'use client';

interface HalfWidthBottomLeftProps {
  children: React.ReactNode;
  className?: string;
}

export default function HalfWidthBottomLeft({
  children,
  className = ""
}: HalfWidthBottomLeftProps) {
  return (
    <div className={`col-span-2 row-span-1 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}