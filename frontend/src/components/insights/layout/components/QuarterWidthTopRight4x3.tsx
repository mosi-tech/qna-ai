/**
 * Positional Layout Component: Quarter Width Top Right (4x3)
 * 
 * Grid Position: col-span-1 row-span-1 (in 4x3 grid)
 * Common Uses: Supporting metrics, alerts, status indicators
 * Can be reused in any layout wrapper that has a 4-column structure
 */

'use client';

interface QuarterWidthTopRight4x3Props {
  children: React.ReactNode;
  className?: string;
}

export default function QuarterWidthTopRight4x3({
  children,
  className = ""
}: QuarterWidthTopRight4x3Props) {
  return (
    <div className={`col-span-1 row-span-1 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}