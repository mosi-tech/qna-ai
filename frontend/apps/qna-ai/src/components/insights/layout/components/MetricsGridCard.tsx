/**
 * Reusable Layout Component: Metrics Grid Card
 * 
 * A standardized container for 2x2 or 1x4 key metrics display
 * Can be used in any layout wrapper that needs metric grids
 */

'use client';

interface MetricsGridCardProps {
  children: React.ReactNode;
  gridType?: '2x2' | '1x4' | '4x1';
  className?: string;
}

export default function MetricsGridCard({
  children,
  gridType = '2x2',
  className = ""
}: MetricsGridCardProps) {
  const gridClasses = {
    '2x2': 'grid-cols-2 grid-rows-2',
    '1x4': 'grid-cols-1 grid-rows-4',
    '4x1': 'grid-cols-4 grid-rows-1'
  };

  return (
    <div className={`h-full bg-white rounded-lg   ${className}`}>
      <div className={`grid ${gridClasses[gridType]} gap-3 h-full`}>
        {children}
      </div>
    </div>
  );
}