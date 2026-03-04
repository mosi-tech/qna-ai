/**
 * Positional Layout Component: Half Width Bottom Right (2x3)
 * 
 * Grid Position: col-span-1 row-span-2 (in 2x3 grid)
 * Common Uses: Charts, visualizations, graphs, trend analysis
 * Can be reused in any layout wrapper that has a 2-column structure
 */

'use client';

interface HalfWidthBottomRight2x3Props {
  children: React.ReactNode;
  className?: string;
}

export default function HalfWidthBottomRight2x3({
  children,
  className = ""
}: HalfWidthBottomRight2x3Props) {
  return (
    <div className={`col-span-1 row-span-2 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}