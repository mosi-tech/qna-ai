/**
 * Layout Component: 5x4 Layout11 Grid Container
 * 
 * Grid system for 8-section comprehensive analytics layout
 * Layout structure:
 * - Row 1: Full width (5 cols) - Highlights
 * - Row 2: Four sections (1 col each) + One tall section (1 col, 2 rows) - Charts
 * - Row 3: Sector breakdown table (5 cols)
 * - Row 4: Detailed raw data table (5 cols)
 */

'use client';

interface GridContainer5x4Layout11Props {
  children: React.ReactNode;
  className?: string;
}

export default function GridContainer5x4Layout11({ 
  children, 
  className = "" 
}: GridContainer5x4Layout11Props) {
  return (
    <div className={`flex-1 grid grid-cols-5 grid-rows-4 gap-4 min-h-0 ${className}`}>
      {children}
    </div>
  );
}