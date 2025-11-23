/**
 * Positional Layout Component: Full Width Bottom
 * 
 * Grid Position: col-span-2 row-span-1 (in 2x5 grid)
 * Common Uses: Summaries, conclusions, actions, full-width content at bottom
 * Can be reused in any layout wrapper that needs full-width bottom section
 */

'use client';

interface FullWidthBottomProps {
  children: React.ReactNode;
  className?: string;
}

export default function FullWidthBottom({
  children,
  className = ""
}: FullWidthBottomProps) {
  return (
    <div className={`col-span-2 row-span-1 ${className}`}>
      <div className="h-full bg-white rounded-lg border border-gray-200">
        {children}
      </div>
    </div>
  );
}