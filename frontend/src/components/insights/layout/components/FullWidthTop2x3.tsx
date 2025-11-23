/**
 * Positional Layout Component: Full Width Top (2x3)
 * 
 * Grid Position: col-span-2 row-span-1 (in 2x3 grid)
 * Common Uses: Highlights, executive summaries, key findings
 * Can be reused in any layout wrapper that has a 2-column structure
 */

'use client';

interface FullWidthTop2x3Props {
  children: React.ReactNode;
  className?: string;
}

export default function FullWidthTop2x3({
  children,
  className = ""
}: FullWidthTop2x3Props) {
  return (
    <div className={`col-span-2 row-span-1 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}