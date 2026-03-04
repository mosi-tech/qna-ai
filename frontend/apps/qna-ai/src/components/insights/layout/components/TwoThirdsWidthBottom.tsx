/**
 * Positional Layout Component: Two Thirds Width Bottom
 * 
 * Grid Position: col-span-2 row-span-1 (in 3x3 grid)
 * Common Uses: Data tables, detailed breakdowns, comprehensive lists
 * Can be reused in any layout wrapper that has a 3-column structure
 */

'use client';

interface TwoThirdsWidthBottomProps {
  children: React.ReactNode;
  className?: string;
}

export default function TwoThirdsWidthBottom({
  children,
  className = ""
}: TwoThirdsWidthBottomProps) {
  return (
    <div className={`col-span-2 row-span-1 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}