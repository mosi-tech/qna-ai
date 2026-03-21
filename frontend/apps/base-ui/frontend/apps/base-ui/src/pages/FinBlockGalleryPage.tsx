import React from 'react';
import { AccountInfoComponent, MOCK_ACCOUNT_INFO } from '../finBlocks/components/account';
import { OpenPositionsTable, MOCK_POSITIONS } from '../finBlocks/components/positions';

export default function FinBlockGalleryPage() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 p-8">
      <div className="max-w-7xl mx-auto space-y-12">
        {/* Header */}
        <div>
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            FinBlocks Gallery
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Production-ready financial UI components built with Tremor
          </p>
        </div>

        {/* Account Info Component */}
        <div>
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
            Account Info
          </h2>
          <AccountInfoComponent data={MOCK_ACCOUNT_INFO} />
        </div>

        {/* Open Positions Component */}
        <div>
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
            Open Positions
          </h2>
          <OpenPositionsTable data={MOCK_POSITIONS} />
        </div>
      </div>
    </div>
  );
}
