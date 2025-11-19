/**
 * Positional Layout Component: Third Width Middle Left
 * 
 * Grid Position: col-span-1 row-span-1 (in 3x3 grid)
 * Common Uses: Metric cards, KPI displays, summary statistics
 * Can be reused in any layout wrapper that has a 3-column structure
 */

'use client';

interface ThirdWidthMiddleLeftProps {
  children: React.ReactNode;
  className?: string;
}

export default function ThirdWidthMiddleLeft({
  children,
  className = ""
}: ThirdWidthMiddleLeftProps) {
  return (
    <div className={`col-span-1 row-span-1 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}