'use client';

import { cn } from './shared/styles';

interface ContainerProps {
  title?: string;
  children: React.ReactNode;
  onApprove?: () => void;
  onDisapprove?: () => void;
}

export default function Container({
  title,
  children,
  onApprove,
  onDisapprove
}: ContainerProps) {
  const titleClass = 'text-base font-semibold text-slate-900';

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      {title && (
        <div className="px-4 py-3 border-b border-slate-100">
          <div className="flex justify-between items-start">
            <h3 className={titleClass}>{title}</h3>
            {(onApprove || onDisapprove) && (
              <div className="flex gap-1">
                {onApprove && (
                  <button
                    onClick={onApprove}
                    className="px-2 py-1 bg-emerald-50 text-emerald-700 rounded text-xs hover:bg-emerald-100 transition-colors"
                  >
                    ✓
                  </button>
                )}
                {onDisapprove && (
                  <button
                    onClick={onDisapprove}
                    className="px-2 py-1 bg-rose-50 text-rose-700 rounded text-xs hover:bg-rose-100 transition-colors"
                  >
                    ✗
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Content */}
      <div className="flex-1 overflow-auto">
        {children}
      </div>
    </div>
  );
}
