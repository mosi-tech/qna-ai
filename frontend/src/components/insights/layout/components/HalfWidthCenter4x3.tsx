/**
 * Positional Layout Component: Half Width Center (4x3)
 * 
 * Grid Position: col-span-2 row-span-1 (in 4x3 grid)
 * Common Uses: Main charts, primary analysis, focus content
 * This is the hero/focus area of the layout
 * Can be reused in any layout wrapper that has a 4-column structure
 */

'use client';

interface HalfWidthCenter4x3Props {
  children: React.ReactNode;
  className?: string;
}

export default function HalfWidthCenter4x3({
  children,
  className = ""
}: HalfWidthCenter4x3Props) {
  return (
    <div className={`col-span-2 row-span-1 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}