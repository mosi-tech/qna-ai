/**
 * Positional Layout Component: Full Width Top Row
 * 
 * Grid Position: col-span-3 row-span-1 (in 3x3 grid)
 * Common Uses: Highlights, executive summaries, key findings, overview content
 * Can be reused in any layout wrapper that has a 3-column structure
 */

'use client';

interface FullWidthTopRowProps {
  children: React.ReactNode;
  className?: string;
}

export default function FullWidthTopRow({
  children,
  className = ""
}: FullWidthTopRowProps) {
  return (
    <div className={`col-span-3 row-span-1 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}