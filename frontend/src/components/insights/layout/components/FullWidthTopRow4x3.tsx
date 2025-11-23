/**
 * Positional Layout Component: Full Width Top Row (4x3 Grid)
 * 
 * Grid Position: col-span-4 row-span-1 (in 4x3 grid)
 * Common Uses: Highlights, executive summaries, key findings, overview content
 * Can be reused in any layout wrapper that has a 4-column structure
 */

'use client';

interface FullWidthTopRow4x3Props {
  children: React.ReactNode;
  className?: string;
}

export default function FullWidthTopRow4x3({
  children,
  className = ""
}: FullWidthTopRow4x3Props) {
  return (
    <div className={`col-span-4 row-span-1 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}