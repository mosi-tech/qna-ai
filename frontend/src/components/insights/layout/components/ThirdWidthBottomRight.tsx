/**
 * Positional Layout Component: Third Width Bottom Right
 * 
 * Grid Position: col-span-1 row-span-1 (in 3x3 grid)
 * Common Uses: Additional insights, sidebars, supplementary information
 * Can be reused in any layout wrapper that has a 3-column structure
 */

'use client';

interface ThirdWidthBottomRightProps {
  children: React.ReactNode;
  className?: string;
}

export default function ThirdWidthBottomRight({
  children,
  className = ""
}: ThirdWidthBottomRightProps) {
  return (
    <div className={`col-span-1 row-span-1 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}