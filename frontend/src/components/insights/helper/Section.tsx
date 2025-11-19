/**
 * Section
 * 
 * Description: Titled grouping container for organizing related analysis content
 * Use Cases: Report sections, analysis categories, thematic groupings
 * Data Format: Title string and child components
 * 
 * @param title - Section title
 * @param children - Child components to group
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

import { ReactNode } from 'react';

interface SectionProps {
  title: string;
  children: ReactNode;
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'wide';
}

export default function Section({
  title,
  children,
  onApprove,
  onDisapprove,
  variant = 'default'
}: SectionProps) {

  const getVariantConfig = () => {
    switch (variant) {
      case 'compact':
        return {
          containerPadding: 'p-3 sm:p-4',
          headerPadding: 'px-0 py-0',
          titleSize: 'text-sm sm:text-base font-semibold',
          spacing: 'space-y-3 sm:space-y-4',
          showBorder: false,
          showHeaderBg: false
        };
      case 'wide':
        return {
          containerPadding: 'p-4 sm:p-6 lg:p-8',
          headerPadding: 'px-4 py-3 sm:px-6 sm:py-4 lg:px-8 lg:py-6',
          titleSize: 'text-lg sm:text-xl font-bold',
          spacing: 'space-y-4 sm:space-y-6 lg:space-y-8',
          showBorder: true,
          showHeaderBg: true
        };
      default:
        return {
          containerPadding: 'p-3 sm:p-4 lg:p-6',
          headerPadding: 'px-3 py-2.5 sm:px-4 sm:py-3 lg:px-6 lg:py-4',
          titleSize: 'text-base sm:text-lg font-semibold',
          spacing: 'space-y-3 sm:space-y-4 lg:space-y-6',
          showBorder: true,
          showHeaderBg: true
        };
    }
  };

  const config = getVariantConfig();

  return (
    <div className={`bg-white ${config.showBorder ? '' : ''} rounded-lg overflow-hidden`}>
      {variant === 'compact' ? (
        // Compact variant - simple title without header background
        <div className={config.containerPadding}>
          <h2 className={`${config.titleSize} text-gray-900 mb-3`}>{title}</h2>
          <div className={config.spacing}>
            {children}
          </div>
        </div>
      ) : (
        // Default/wide variants with header background
        <>
          <div className={`${config.headerPadding} ${config.showHeaderBg ? 'border-b border-gray-200 bg-gray-50' : ''} flex justify-between items-center flex-wrap gap-2`}>
            <h2 className={`${config.titleSize} text-gray-900 truncate`}>{title}</h2>

            {(onApprove || onDisapprove) && (
              <div className="flex gap-2">
                {onApprove && (
                  <button
                    onClick={onApprove}
                    className="px-3 py-1 bg-green-50 text-green-700 rounded hover:bg-green-100 transition-colors text-sm"
                  >
                    ✓
                  </button>
                )}
                {onDisapprove && (
                  <button
                    onClick={onDisapprove}
                    className="px-3 py-1 bg-red-50 text-red-700 rounded hover:bg-red-100 transition-colors text-sm"
                  >
                    ✗
                  </button>
                )}
              </div>
            )}
          </div>

          <div className={`${config.containerPadding} ${config.spacing}`}>
            {children}
          </div>
        </>
      )}
    </div>
  );
}