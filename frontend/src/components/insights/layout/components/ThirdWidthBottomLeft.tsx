/**
 * Positional Layout Component: Third Width Bottom Left
 * 
 * Grid Position: col-span-1 row-span-1 (in 3x2 grid)
 * Common Uses: Primary charts, line charts, performance tracking
 * Can be reused in any layout wrapper that has a 3-column structure
 */

'use client';

interface ThirdWidthBottomLeftProps {
  children: React.ReactNode;
  className?: string;
}

export default function ThirdWidthBottomLeft({
  children,
  className = ""
}: ThirdWidthBottomLeftProps) {
  return (
    <div className={`col-span-1 row-span-1 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}