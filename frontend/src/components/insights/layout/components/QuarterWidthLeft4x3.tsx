/**
 * Positional Layout Component: Quarter Width Left (4x3)
 * 
 * Grid Position: col-span-1 row-span-1 (in 4x3 grid)
 * Common Uses: Context panels, parameter controls, filters
 * Can be reused in any layout wrapper that has a 4-column structure
 */

'use client';

interface QuarterWidthLeft4x3Props {
  children: React.ReactNode;
  className?: string;
}

export default function QuarterWidthLeft4x3({
  children,
  className = ""
}: QuarterWidthLeft4x3Props) {
  return (
    <div className={`col-span-1 row-span-1 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}