/**
 * Positional Layout Component: Right Primary
 * 
 * Grid Position: col-span-1 row-span-2 (in 2x5 grid)
 * Common Uses: Right side main content, primary entity analysis, Strategy B
 * Can be reused in any layout wrapper that has a 2-column comparison grid
 */

'use client';

interface RightPrimaryProps {
  children: React.ReactNode;
  className?: string;
}

export default function RightPrimary({
  children,
  className = ""
}: RightPrimaryProps) {
  return (
    <div className={`col-span-1 row-span-2 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}