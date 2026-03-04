/**
 * Subsection
 * 
 * Description: Nested grouping container for organizing content within sections
 * Use Cases: Sub-analysis within sections, detailed breakdowns, nested categories
 * Data Format: Title string and child components
 * 
 * @param title - Subsection title
 * @param children - Child components to group
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

import { ReactNode } from 'react';

interface SubsectionProps {
  title: string;
  children: ReactNode;
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'detailed';
}

export default function Subsection({ 
  title,
  children,
  onApprove, 
  onDisapprove,
  variant = 'default' 
}: SubsectionProps) {
  
  return (
    <div className="border border-gray-100 rounded-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-100 bg-gray-25 flex justify-between items-center">
        <h3 className="text-md font-medium text-gray-900">{title}</h3>
        
        {(onApprove || onDisapprove) && (
          <div className="flex gap-1">
            {onApprove && (
              <button
                onClick={onApprove}
                className="px-2 py-1 bg-green-50 text-green-700 rounded text-xs hover:bg-green-100 transition-colors"
              >
                ✓
              </button>
            )}
            {onDisapprove && (
              <button
                onClick={onDisapprove}
                className="px-2 py-1 bg-red-50 text-red-700 rounded text-xs hover:bg-red-100 transition-colors"
              >
                ✗
              </button>
            )}
          </div>
        )}
      </div>
      
      <div className="p-4 space-y-4">
        {children}
      </div>
    </div>
  );
}