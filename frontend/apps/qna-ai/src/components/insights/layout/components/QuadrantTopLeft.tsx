/**
 * Positional Layout Component: Quadrant Top Left
 * 
 * Grid Position: col-span-1 row-span-1 (in 2x2 grid)
 * Common Uses: Highlights, executive summaries, key findings
 * Can be reused in any layout wrapper that has a 2x2 quadrant structure
 */

'use client';

interface QuadrantTopLeftProps {
  children: React.ReactNode;
  className?: string;
}

export default function QuadrantTopLeft({
  children,
  className = ""
}: QuadrantTopLeftProps) {
  return (
    <div className={`col-span-1 row-span-1 ${className}`}>
      <div className="h-full bg-white rounded-lg  ">
        {children}
      </div>
    </div>
  );
}