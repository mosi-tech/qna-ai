'use client';

import Container from './Container';

interface CalloutItem {
  id: string;
  title: string;
  content: string;
  type: 'info' | 'warning' | 'success' | 'error';
}

interface CalloutListProps {
  title?: string;
  items: CalloutItem[];
  onApprove?: () => void;
  onDisapprove?: () => void;
}

export default function CalloutList({ 
  title,
  items,
  onApprove, 
  onDisapprove 
}: CalloutListProps) {
  
  const getItemStyleClasses = (type: string) => {
    switch (type) {
      case 'success':
        return 'bg-green-50 border-green-200 text-green-800';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'error':
        return 'bg-red-50 border-red-200 text-red-800';
      case 'info':
      default:
        return 'bg-blue-50 border-blue-200 text-blue-800';
    }
  };

  const getIcon = (type: string) => {
    switch (type) {
      case 'success':
        return '✓';
      case 'warning':
        return '⚠';
      case 'error':
        return '✗';
      case 'info':
      default:
        return 'ℹ';
    }
  };

  const getTitleColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'text-green-900';
      case 'warning':
        return 'text-yellow-900';
      case 'error':
        return 'text-red-900';
      case 'info':
      default:
        return 'text-blue-900';
    }
  };
  
  return (
    <Container title={title} onApprove={onApprove} onDisapprove={onDisapprove}>
      <div className="p-4 space-y-3">
        {items.map((item) => (
          <div 
            key={item.id} 
            className={`border rounded-lg p-3 ${getItemStyleClasses(item.type)}`}
          >
            <div className="flex items-start space-x-2">
              <div className="flex-shrink-0 text-sm">
                {getIcon(item.type)}
              </div>
              <div className="flex-1 min-w-0">
                <h4 className={`text-sm font-medium mb-1 ${getTitleColor(item.type)} truncate`}>
                  {item.title}
                </h4>
                <p className="text-sm break-words">
                  {item.content}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </Container>
  );
}
