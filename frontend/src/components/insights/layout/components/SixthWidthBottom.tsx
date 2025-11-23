/**
 * Positional Layout Component: Sixth Width Bottom
 * 
 * Grid Position: col-span-1 row-span-1 (in 6x2 grid)
 * Common Uses: Timeline details, process metrics, step-specific data
 * Can be reused in any layout wrapper that has a 6-column structure
 */

'use client';

interface SixthWidthBottomProps {
  children: React.ReactNode;
  className?: string;
}

export default function SixthWidthBottom({
  children,
  className = ""
}: SixthWidthBottomProps) {
  return (
    <div className={`col-span-1 row-span-1 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}