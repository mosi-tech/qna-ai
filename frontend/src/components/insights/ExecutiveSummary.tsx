/**
 * ExecutiveSummary
 * 
 * Description: Key findings and recommendations summary for investment analysis
 * Use Cases: Portfolio reports, analysis summaries, executive overviews
 * Data Format: Object with key finding, performance summary, and recommendation
 * 
 * @param keyFinding - Main finding or result
 * @param performance - Performance summary
 * @param recommendation - Actionable recommendation
 * @param variant - Component variant for different space sizes
 */

'use client';

interface ExecutiveSummaryItem {
  label: string;
  text: string;
  color?: 'blue' | 'green' | 'purple' | 'orange' | 'red';
}

interface ExecutiveSummaryProps {
  title?: string;
  items: ExecutiveSummaryItem[];
  variant?: 'default' | 'compact' | 'detailed';
  onApprove?: () => void;
  onDisapprove?: () => void;
}

export default function ExecutiveSummary({ 
  title = "Executive Summary",
  items,
  variant = 'default',
  onApprove, 
  onDisapprove 
}: ExecutiveSummaryProps) {
  
  const getVariantConfig = () => {
    switch (variant) {
      case 'compact':
        return {
          containerPadding: 'p-4 sm:p-5',
          titleSize: 'text-lg sm:text-xl font-bold',
          contentSize: 'text-sm',
          spacing: 'space-y-2',
          labelSize: 'text-xs font-semibold',
          borderRadius: 'rounded-lg'
        };
      case 'detailed':
        return {
          containerPadding: 'p-6 sm:p-8',
          titleSize: 'text-xl sm:text-2xl font-bold',
          contentSize: 'text-base',
          spacing: 'space-y-4',
          labelSize: 'text-sm font-bold',
          borderRadius: 'rounded-xl'
        };
      default:
        return {
          containerPadding: 'p-5 sm:p-6',
          titleSize: 'text-xl font-bold',
          contentSize: 'text-sm sm:text-base',
          spacing: 'space-y-3',
          labelSize: 'text-sm font-semibold',
          borderRadius: 'rounded-lg'
        };
    }
  };

  const getColorClasses = (color: string = 'blue') => {
    switch (color) {
      case 'green':
        return 'text-green-700';
      case 'purple':
        return 'text-purple-700';
      case 'orange':
        return 'text-orange-700';
      case 'red':
        return 'text-red-700';
      default:
        return 'text-blue-700';
    }
  };

  const config = getVariantConfig();
  
  return (
    <div className={`bg-white ${config.borderRadius} ${config.containerPadding}`}>
      <div className="flex justify-between items-start mb-4">
        <h2 className={`${config.titleSize} text-gray-900`}>{title}</h2>
        
        {(onApprove || onDisapprove) && (
          <div className="flex gap-2">
            {onApprove && (
              <button
                onClick={onApprove}
                className="px-3 py-1 bg-green-50 text-green-700 rounded hover:bg-green-100 transition-colors text-sm font-medium"
              >
                ✓
              </button>
            )}
            {onDisapprove && (
              <button
                onClick={onDisapprove}
                className="px-3 py-1 bg-red-50 text-red-700 rounded hover:bg-red-100 transition-colors text-sm font-medium"
              >
                ✗
              </button>
            )}
          </div>
        )}
      </div>
      
      <div className={config.spacing}>
        {items.map((item, index) => (
          <div key={index}>
            <span className={`${config.labelSize} ${getColorClasses(item.color)}`}>{item.label}: </span>
            <span className={`${config.contentSize} text-gray-700`}>{item.text}</span>
          </div>
        ))}
      </div>
    </div>
  );
}