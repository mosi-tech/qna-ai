/**
 * Positional Layout Component: Full Width Bottom Table
 * 
 * Grid Position: col-span-4 row-span-1 (in 4x3 grid)
 * Common Uses: Detailed data tables, comprehensive listings, analytical breakdowns
 * Can be reused in any layout wrapper that has a 4-column structure
 */

'use client';

interface FullWidthBottomTableProps {
  children: React.ReactNode;
  className?: string;
}

export default function FullWidthBottomTable({
  children,
  className = ""
}: FullWidthBottomTableProps) {
  return (
    <div className={`col-span-4 row-span-1 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}