/**
 * Reusable Layout Component: Executive Summary Card
 * 
 * A standardized container for executive summary content
 * Can be used in any layout wrapper that needs a professional summary section
 */

'use client';

interface ExecutiveSummaryCardProps {
  children: React.ReactNode;
  className?: string;
}

export default function ExecutiveSummaryCard({
  children,
  className = ""
}: ExecutiveSummaryCardProps) {
  return (
    <div className={`h-full bg-white rounded-lg   ${className}`}>
      {children}
    </div>
  );
}