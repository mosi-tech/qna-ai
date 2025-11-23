'use client';

import { cn } from './shared/styles';

interface ContainerProps {
  title?: string;
  subtitle?: string;
  children: React.ReactNode;
}

export default function Container({
  title,
  subtitle,
  children
}: ContainerProps) {

  return (
    <div className="flex flex-col h-full bg-white rounded-xl shadow-md shadow-slate-200/40 border border-slate-100/50 hover:shadow-lg hover:shadow-slate-300/50 transition-all duration-300 overflow-hidden">
      {/* Header with gradient background */}
      {title && (
        <div className="relative bg-gradient-to-r from-slate-50 to-slate-100/50 px-4 py-4">
          {/* Subtle bottom divider */}
          <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-slate-200 via-slate-200/50 to-transparent"></div>
          
          <div className="flex-1">
            <h3 className="text-base font-medium text-slate-900">{title}</h3>
            {subtitle && (
              <p className="text-sm text-slate-600 mt-1">{subtitle}</p>
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
