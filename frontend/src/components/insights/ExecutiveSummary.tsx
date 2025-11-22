'use client';

import Container from './Container';

interface ExecutiveSummaryItem {
  label: string;
  text: string;
  color?: 'blue' | 'green' | 'purple' | 'orange' | 'red';
}

interface ExecutiveSummaryProps {
  title?: string;
  items: ExecutiveSummaryItem[];
  onApprove?: () => void;
  onDisapprove?: () => void;
}

export default function ExecutiveSummary({ 
  title = "Executive Summary",
  items,
  onApprove, 
  onDisapprove 
}: ExecutiveSummaryProps) {
  
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
  
  return (
    <Container title={title} onApprove={onApprove} onDisapprove={onDisapprove}>
      <div className="p-4 space-y-3">
        {items.map((item, index) => (
          <div key={index}>
            <span className={`text-sm font-semibold ${getColorClasses(item.color)}`}>{item.label}: </span>
            <span className="text-sm text-gray-700">{item.text}</span>
          </div>
        ))}
      </div>
    </Container>
  );
}
