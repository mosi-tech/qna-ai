/**
 * Positional Layout Component: Full Width Top Row (5x4 Grid)
 * 
 * Grid Position: col-span-5 row-span-1 (in 5x4 grid)
 * Common Uses: Highlights, executive summaries, key findings, overview content
 * Can be reused in any layout wrapper that has a 5-column structure
 */

'use client';

interface FullWidthTopRow5x4Props {
  children: React.ReactNode;
  className?: string;
}

export default function FullWidthTopRow5x4({
  children,
  className = ""
}: FullWidthTopRow5x4Props) {
  return (
    <div className={`col-span-5 row-span-1 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}