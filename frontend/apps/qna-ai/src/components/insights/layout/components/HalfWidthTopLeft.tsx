/**
 * Positional Layout Component: Half Width Top Left
 * 
 * Grid Position: col-span-2 row-span-2 (in 4x6 grid)
 * Common Uses: Executive summary, main content, primary analysis
 * Can be reused in any layout wrapper that has a 4-column grid
 */

'use client';

interface HalfWidthTopLeftProps {
  children: React.ReactNode;
  className?: string;
}

export default function HalfWidthTopLeft({
  children,
  className = ""
}: HalfWidthTopLeftProps) {
  return (
    <div className={`col-span-2 row-span-2 ${className}`}>
      <div className="h-full bg-white rounded-lg border border-gray-200">
        {children}
      </div>
    </div>
  );
}