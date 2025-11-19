/**
 * Grid
 * 
 * Description: 2–4 column responsive layout container for organizing components
 * Use Cases: Dashboard layouts, metric displays, comparison layouts
 * Data Format: Child components arranged in responsive grid
 * 
 * @param children - Child components to arrange in grid
 * @param columns - Number of columns (2-4)
 * @param gap - Gap size between grid items
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

import { ReactNode } from 'react';

interface GridProps {
  children: ReactNode;
  columns?: 2 | 3 | 4;
  gap?: 'sm' | 'md' | 'lg';
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'detailed';
}

export default function Grid({ 
  children,
  columns = 2,
  gap = 'md',
  onApprove, 
  onDisapprove,
  variant = 'default' 
}: GridProps) {
  
  const getGridClasses = () => {
    const baseClasses = 'grid';
    
    const columnClasses = {
      2: 'grid-cols-1 md:grid-cols-2',
      3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
      4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4'
    };
    
    const gapClasses = {
      sm: 'gap-3',
      md: 'gap-6',
      lg: 'gap-8'
    };
    
    return `${baseClasses} ${columnClasses[columns]} ${gapClasses[gap]}`;
  };
  
  return (
    <div className="space-y-4">
      <div className={getGridClasses()}>
        {children}
      </div>
      
      {(onApprove || onDisapprove) && (
        <div className="flex gap-2 justify-end">
          {onApprove && (
            <button
              onClick={onApprove}
              className="px-3 py-1 bg-green-50 text-green-700 rounded hover:bg-green-100 transition-colors text-sm"
            >
              Approve Layout
            </button>
          )}
          {onDisapprove && (
            <button
              onClick={onDisapprove}
              className="px-3 py-1 bg-red-50 text-red-700 rounded hover:bg-red-100 transition-colors text-sm"
            >
              Disapprove Layout
            </button>
          )}
        </div>
      )}
    </div>
  );
}