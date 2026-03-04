'use client';

interface ClarificationSummaryProps {
  message: string;
  expandedQuery?: string;
  status: 'pending' | 'answered' | 'rejected';
}

export default function ClarificationSummary({
  message,
  expandedQuery,
  status,
}: ClarificationSummaryProps) {
  const bgColor = status === 'pending' ? 'bg-gray-50' : 'bg-gray-100';
  const borderColor = status === 'pending' ? 'border-gray-200' : 'border-gray-300';
  const textColor = status === 'pending' ? 'text-gray-700' : 'text-gray-600';
  const icon = status === 'pending' ? '⏳' : status === 'answered' ? '✓' : '✗';
  const iconBg = status === 'pending' ? 'bg-gray-100' : status === 'answered' ? 'bg-green-100' : 'bg-red-100';
  const iconColor = status === 'pending' ? 'text-gray-600' : status === 'answered' ? 'text-green-600' : 'text-red-600';

  return (
    <div className="flex gap-2 w-full">
      <div className={`w-6 h-6 rounded-full ${iconBg} flex items-center justify-center flex-shrink-0`}>
        <span className={`${iconColor} text-xs font-semibold`}>{icon}</span>
      </div>
      <div className={`${bgColor} border ${borderColor} rounded px-3 py-2 max-w-2xl flex-1`}>
        <p className={`text-xs ${textColor}`}>{message}</p>
        {expandedQuery && (
          <p className="text-xs text-gray-500 mt-1 italic">→ {expandedQuery}</p>
        )}
      </div>
    </div>
  );
}
