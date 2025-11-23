/**
 * Positional Layout Component: Quarter Width Top Left (4x3)
 * 
 * Grid Position: col-span-1 row-span-1 (in 4x3 grid)
 * Common Uses: Supporting metrics, quick stats, contextual data
 * Can be reused in any layout wrapper that has a 4-column structure
 */

'use client';

interface QuarterWidthTopLeft4x3Props {
  children: React.ReactNode;
  className?: string;
}

export default function QuarterWidthTopLeft4x3({
  children,
  className = ""
}: QuarterWidthTopLeft4x3Props) {
  return (
    <div className={`col-span-1 row-span-1 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}