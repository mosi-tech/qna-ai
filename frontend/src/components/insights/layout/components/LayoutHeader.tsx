/**
 * Layout Component: Layout Header
 * 
 * Standardized header for all layout templates
 * Consistent spacing and typography across layouts
 */

'use client';

interface LayoutHeaderProps {
  children: React.ReactNode;
  className?: string;
}

export default function LayoutHeader({ 
  children, 
  className = "" 
}: LayoutHeaderProps) {
  return (
    <div className={`mb-2 ${className}`}>
      {children}
    </div>
  );
}