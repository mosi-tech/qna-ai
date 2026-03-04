/**
 * Positional Layout Component: Half Width Top (4x3)
 * 
 * Grid Position: col-span-2 row-span-1 (in 4x3 grid)
 * Common Uses: Chart titles, analysis headers, metric descriptions
 * Can be reused in any layout wrapper that has a 4-column structure
 */

'use client';

interface HalfWidthTop4x3Props {
  children: React.ReactNode;
  className?: string;
}

export default function HalfWidthTop4x3({
  children,
  className = ""
}: HalfWidthTop4x3Props) {
  return (
    <div className={`col-span-2 row-span-1 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}