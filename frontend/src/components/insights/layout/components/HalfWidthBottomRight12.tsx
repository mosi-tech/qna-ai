/**
 * Positional Layout Component: Half Width Bottom Right (Layout12)
 * 
 * Grid Position: col-span-2 row-span-1 (in 4x3 grid, bottom row)
 * Common Uses: Trades tables, execution data, detailed listings
 * Can be reused in any layout wrapper that has a 4-column structure
 */

'use client';

interface HalfWidthBottomRight12Props {
  children: React.ReactNode;
  className?: string;
}

export default function HalfWidthBottomRight12({
  children,
  className = ""
}: HalfWidthBottomRight12Props) {
  return (
    <div className={`col-span-2 row-span-1 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}