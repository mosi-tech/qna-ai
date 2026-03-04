/**
 * Layout Component: 4x3 Layout10 Grid Container
 * 
 * Grid system for 7-section mixed layout
 * Layout structure:
 * - Row 1: Full width (4 cols) - Highlights
 * - Row 2: Four sections (1 col each) - Metric Cards, Line Chart, Histogram, Bar Chart
 * - Row 3: Two sections (2 cols each) - Heatmap, Table
 */

'use client';

interface GridContainer4x3Layout10Props {
  children: React.ReactNode;
  className?: string;
}

export default function GridContainer4x3Layout10({ 
  children, 
  className = "" 
}: GridContainer4x3Layout10Props) {
  return (
    <div className={`flex-1 grid grid-cols-4 grid-rows-3 gap-4 min-h-0 ${className}`}>
      {children}
    </div>
  );
}