/**
 * Positional Layout Component: Half Width Bottom Right
 * 
 * Grid Position: col-span-2 row-span-1 (in 4x3 grid, bottom row)
 * Common Uses: Data tables, detailed listings, summary tables
 * Can be reused in any layout wrapper that has a 4-column structure
 */

'use client';

interface HalfWidthBottomRightProps {
  children: React.ReactNode;
  className?: string;
}

export default function HalfWidthBottomRight({
  children,
  className = ""
}: HalfWidthBottomRightProps) {
  return (
    <div className={`col-span-2 row-span-1 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}