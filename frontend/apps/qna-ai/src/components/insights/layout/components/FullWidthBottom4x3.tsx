/**
 * Positional Layout Component: Full Width Bottom (4x3)
 * 
 * Grid Position: col-span-4 row-span-1 (in 4x3 grid)
 * Common Uses: Summary insights, actions, analysis conclusions
 * Can be reused in any layout wrapper that needs full-width bottom section
 */

'use client';

interface FullWidthBottom4x3Props {
  children: React.ReactNode;
  className?: string;
}

export default function FullWidthBottom4x3({
  children,
  className = ""
}: FullWidthBottom4x3Props) {
  return (
    <div className={`col-span-4 row-span-1 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}