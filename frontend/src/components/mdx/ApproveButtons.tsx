'use client';

import React from 'react';

interface ApproveButtonsProps {
  component: string;
}

export function ApproveButtons({ component }: ApproveButtonsProps) {
  return (
    <div className="flex items-center gap-3 my-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
      <span className="text-sm text-gray-600 font-medium">
        Component: {component}
      </span>
      <div className="flex gap-2">
        <button className="px-3 py-1 text-xs font-medium text-green-700 bg-green-100 rounded-md hover:bg-green-200 transition-colors">
          ✓ Approve
        </button>
        <button className="px-3 py-1 text-xs font-medium text-red-700 bg-red-100 rounded-md hover:bg-red-200 transition-colors">
          ✗ Reject
        </button>
        <button className="px-3 py-1 text-xs font-medium text-blue-700 bg-blue-100 rounded-md hover:bg-blue-200 transition-colors">
          ✎ Modify
        </button>
      </div>
    </div>
  );
}