/**
 * Positional Layout Component: Half Width Bottom Left (2x3)
 * 
 * Grid Position: col-span-1 row-span-2 (in 2x3 grid)
 * Common Uses: Data tables, key metrics, detailed breakdowns
 * Can be reused in any layout wrapper that has a 2-column structure
 */

'use client';

interface HalfWidthBottomLeft2x3Props {
  children: React.ReactNode;
  className?: string;
}

export default function HalfWidthBottomLeft2x3({
  children,
  className = ""
}: HalfWidthBottomLeft2x3Props) {
  return (
    <div className={`col-span-1 row-span-2 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}