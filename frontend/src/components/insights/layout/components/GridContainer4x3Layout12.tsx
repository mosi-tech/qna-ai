/**
 * Layout Component: 4x3 Layout12 Grid Container
 * 
 * Grid system for trading/signals analytics layout
 * Layout structure:
 * - Row 1: Full width KPI banner (4 cols) - Highlights
 * - Row 2: Four equal chart sections (1 col each) - Charts & Analysis
 * - Row 3: Two half-width tables (2 cols each) - Signals & Trades
 */

'use client';

interface GridContainer4x3Layout12Props {
  children: React.ReactNode;
  className?: string;
}

export default function GridContainer4x3Layout12({ 
  children, 
  className = "" 
}: GridContainer4x3Layout12Props) {
  return (
    <div className={`flex-1 grid grid-cols-4 grid-rows-3 gap-4 min-h-0 ${className}`}>
      {children}
    </div>
  );
}