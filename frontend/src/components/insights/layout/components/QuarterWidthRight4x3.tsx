/**
 * Positional Layout Component: Quarter Width Right (4x3)
 * 
 * Grid Position: col-span-1 row-span-1 (in 4x3 grid)
 * Common Uses: Context panels, related metrics, drill-down options
 * Can be reused in any layout wrapper that has a 4-column structure
 */

'use client';

interface QuarterWidthRight4x3Props {
  children: React.ReactNode;
  className?: string;
}

export default function QuarterWidthRight4x3({
  children,
  className = ""
}: QuarterWidthRight4x3Props) {
  return (
    <div className={`col-span-1 row-span-1 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}