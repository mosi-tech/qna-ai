/**
 * Positional Layout Component: Sixth Width Top
 * 
 * Grid Position: col-span-1 row-span-1 (in 6x2 grid)
 * Common Uses: Timeline steps, process stages, sequential headers
 * Can be reused in any layout wrapper that has a 6-column structure
 */

'use client';

interface SixthWidthTopProps {
  children: React.ReactNode;
  className?: string;
}

export default function SixthWidthTop({
  children,
  className = ""
}: SixthWidthTopProps) {
  return (
    <div className={`col-span-1 row-span-1 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}