'use client';

interface DividerProps {
  label?: string;
  variant?: 'line' | 'space' | 'dotted';
  onApprove?: () => void;
  onDisapprove?: () => void;
}

export default function Divider({ 
  label,
  variant = 'line',
  onApprove, 
  onDisapprove
}: DividerProps) {
  
  const renderDivider = () => {
    switch (variant) {
      case 'space':
        return <div className="py-6" />;
      case 'dotted':
        return <div className="border-t border-dotted border-gray-300" />;
      case 'line':
      default:
        return <div className="border-t border-gray-200" />;
    }
  };

  if (label) {
    return (
      <div className="relative py-4">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-gray-200" />
        </div>
        <div className="relative flex justify-center">
          <span className="bg-gray-50 px-4 text-sm text-gray-500 font-medium">
            {label}
          </span>
        </div>
      </div>
    );
  }

  return renderDivider();
}
