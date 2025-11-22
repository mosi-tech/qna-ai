/**
 * BulletList
 * 
 * Description: Simple bullet points for key findings, risks, or recommendations
 * Use Cases: Risk factors, key points, action items, features
 * Data Format: Array of strings or objects with text and optional metadata
 * 
 * @param items - Array of bullet point items
 * @param title - Optional title for the bullet list
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

import Container from './Container';

interface BulletItem {
  text: string;
  emphasis?: 'normal' | 'strong' | 'subtle';
}

interface BulletListProps {
  items: (string | BulletItem)[];
  title?: string;
  onApprove?: () => void;
  onDisapprove?: () => void;
}

export default function BulletList({
  items,
  title,
  onApprove,
  onDisapprove
}: BulletListProps) {

  const getTextClasses = (emphasis: string = 'normal') => {
    switch (emphasis) {
      case 'strong':
        return 'text-gray-900 font-medium';
      case 'subtle':
        return 'text-gray-500';
      case 'normal':
      default:
        return 'text-gray-700';
    }
  };

  return (
    <Container title={title} onApprove={onApprove} onDisapprove={onDisapprove}>
      <div className="p-4">
        <ul className="space-y-3">
          {items.map((item, index) => {
            const isObject = typeof item === 'object';
            const text = isObject ? item.text : item;
            const emphasis = isObject ? item.emphasis || 'normal' : 'normal';

            return (
              <li key={index} className="flex items-start">
                <div className="w-1.5 h-1.5 bg-gray-400 rounded-full mt-2.5 mr-3 flex-shrink-0"></div>
                <span className={getTextClasses(emphasis)}>{text}</span>
              </li>
            );
          })}
        </ul>
      </div>
    </Container>
  );
}