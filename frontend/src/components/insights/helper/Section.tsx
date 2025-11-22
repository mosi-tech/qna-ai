'use client';

import { ReactNode } from 'react';

interface SectionProps {
  title: string;
  children: ReactNode;
  onApprove?: () => void;
  onDisapprove?: () => void;
}

export default function Section({
  title,
  children,
  onApprove,
  onDisapprove
}: SectionProps) {

  return (
    <div className="bg-white rounded-lg overflow-hidden">
      <div className="px-3 py-2.5 sm:px-4 sm:py-3 lg:px-6 lg:py-4 bg-gray-50 border-b">
        <h3 className="text-base sm:text-lg font-semibold text-gray-900">{title}</h3>
      </div>
      <div className="p-3 sm:p-4 lg:p-6 space-y-3 sm:space-y-4 lg:space-y-6">
        {children}
      </div>
    </div>
  );
}
