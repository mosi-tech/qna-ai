/**
 * Layout Component: Layout Container
 * 
 * Base container for all layout templates
 * Provides consistent outer spacing, max-width, and flex structure
 */

'use client';

interface LayoutContainerProps {
  children: React.ReactNode;
  className?: string;
  maxWidth?: 'max-w-6xl' | 'max-w-7xl' | 'max-w-8xl';
}

export default function LayoutContainer({ 
  children, 
  className = "",
  maxWidth = 'max-w-7xl'
}: LayoutContainerProps) {
  return (
    <div className="h-screen bg-gray-50 p-6 overflow-hidden">
      <div className={`${maxWidth} mx-auto h-full flex flex-col gap-4 ${className}`}>
        {children}
      </div>
    </div>
  );
}