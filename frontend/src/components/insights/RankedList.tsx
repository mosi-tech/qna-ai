/**
 * RankedList
 * 
 * Description: Sorted list of items with ranking indicators and values
 * Use Cases: Top performers, risk rankings, contribution analysis
 * Data Format: Array of items with rank, name, value, and optional metadata
 * 
 * @param items - Array of ranked items
 * @param title - Optional title for the list
 * @param showValues - Whether to display values alongside rankings
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

import Container from './Container';

interface RankedItem {
  id: string;
  name: string;
  value?: string | number;
  change?: string | number;
  changeType?: 'positive' | 'negative' | 'neutral';
  subtitle?: string;
}

interface RankedListProps {
  items: RankedItem[];
  title?: string;
  showValues?: boolean;
  maxItems?: number;
  onApprove?: () => void;
  onDisapprove?: () => void;
}

export default function RankedList({
  items,
  title,
  showValues = true,
  maxItems,
  onApprove,
  onDisapprove,
  
}: RankedListProps) {

  const displayItems = maxItems ? items.slice(0, maxItems) : items;

  const getRankBadgeClasses = (rank: number) => {
    if (rank === 1) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    if (rank === 2) return 'bg-gray-100 text-gray-800 border-gray-200';
    if (rank === 3) return 'bg-orange-100 text-orange-800 border-orange-200';
    return 'bg-blue-50 text-blue-700 border-blue-200';
  };

  const getChangeClasses = (type: string = 'neutral') => {
    switch (type) {
      case 'positive':
        return 'text-green-600';
      case 'negative':
        return 'text-red-600';
      case 'neutral':
      default:
        return 'text-gray-600';
    }
  };

  return (
    <Container title={title} onApprove={onApprove} onDisapprove={onDisapprove}>
      <div className="p-4">
        <div className="space-y-3">
        {displayItems.map((item, index) => (
          <div key={item.id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
            <div className="flex items-center space-x-3">
              <span className={`inline-flex items-center justify-center w-8 h-8 text-sm font-semibold border rounded-full ${getRankBadgeClasses(index + 1)}`}>
                {index + 1}
              </span>
              <div>
                <div className="text-sm font-medium text-gray-900">{item.name}</div>
                {item.subtitle && (
                  <div className="text-xs text-gray-500">{item.subtitle}</div>
                )}
              </div>
            </div>

            {showValues && (item.value !== undefined) && (
              <div className="text-right">
                <div className="text-sm font-semibold text-gray-900">
                  {typeof item.value === 'number' ? item.value.toLocaleString() : item.value}
                </div>
                {item.change && (
                  <div className={`text-xs font-medium ${getChangeClasses(item.changeType)}`}>
                    {typeof item.change === 'number' && item.change > 0 ? '+' : ''}{item.change}
                    {typeof item.change === 'number' && '%'}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
        </div>

        {maxItems && items.length > maxItems && (
          <div className="mt-4 text-center">
            <span className="text-sm text-gray-500">
              Showing top {maxItems} of {items.length} items
            </span>
          </div>
        )}
      </div>
    </Container>
  );
}