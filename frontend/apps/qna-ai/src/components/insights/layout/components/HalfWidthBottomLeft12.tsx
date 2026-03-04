/**
 * Positional Layout Component: Half Width Bottom Left (Layout12)
 * 
 * Grid Position: col-span-2 row-span-1 (in 4x3 grid, bottom row)
 * Common Uses: Signals tables, trading data, analytical breakdowns
 * Can be reused in any layout wrapper that has a 4-column structure
 */

'use client';

interface HalfWidthBottomLeft12Props {
  children: React.ReactNode;
  className?: string;
}

export default function HalfWidthBottomLeft12({
  children,
  className = ""
}: HalfWidthBottomLeft12Props) {
  return (
    <div className={`col-span-2 row-span-1 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}