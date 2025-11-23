/**
 * Positional Layout Component: Third Width Middle
 * 
 * Grid Position: col-span-1 row-span-1 (in 3x4 grid)
 * Common Uses: Secondary metrics, supporting data, quick stats
 * Can be reused in any layout wrapper that has a 3-column structure
 */

'use client';

interface ThirdWidthMiddleProps {
  children: React.ReactNode;
  className?: string;
}

export default function ThirdWidthMiddle({
  children,
  className = ""
}: ThirdWidthMiddleProps) {
  return (
    <div className={`col-span-1 row-span-1 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}