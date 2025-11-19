/**
 * Positional Layout Component: Full Width Top (3x2)
 * 
 * Grid Position: col-span-3 row-span-1 (in 3x2 grid)
 * Common Uses: Highlights, executive summaries, key findings, overview content
 * Can be reused in any layout wrapper that has a 3-column structure
 */

'use client';

interface FullWidthTop3x2Props {
  children: React.ReactNode;
  className?: string;
}

export default function FullWidthTop3x2({
  children,
  className = ""
}: FullWidthTop3x2Props) {
  return (
    <div className={`col-span-3 row-span-1 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}