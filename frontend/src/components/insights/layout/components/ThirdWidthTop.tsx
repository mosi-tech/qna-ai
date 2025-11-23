/**
 * Positional Layout Component: Third Width Top
 * 
 * Grid Position: col-span-1 row-span-2 (in 3x4 grid)
 * Common Uses: Main metrics, primary analysis, key performance indicators
 * Can be reused in any layout wrapper that has a 3-column structure
 */

'use client';

interface ThirdWidthTopProps {
  children: React.ReactNode;
  className?: string;
}

export default function ThirdWidthTop({
  children,
  className = ""
}: ThirdWidthTopProps) {
  return (
    <div className={`col-span-1 row-span-2 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}