/**
 * Positional Layout Component: Third Width Middle Right
 * 
 * Grid Position: col-span-1 row-span-1 (in 3x3 grid)
 * Common Uses: Histograms, distribution charts, frequency analysis
 * Can be reused in any layout wrapper that has a 3-column structure
 */

'use client';

interface ThirdWidthMiddleRightProps {
  children: React.ReactNode;
  className?: string;
}

export default function ThirdWidthMiddleRight({
  children,
  className = ""
}: ThirdWidthMiddleRightProps) {
  return (
    <div className={`col-span-1 row-span-1 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}