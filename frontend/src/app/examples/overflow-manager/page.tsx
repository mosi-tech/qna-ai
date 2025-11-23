/**
 * Overflow Manager Page
 * Dedicated page for managing component overflow issues and applying fixes
 */

'use client';

import OverflowFixManager from '@/components/insights/layout/components/OverflowFixManager';

export default function OverflowManagerPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <OverflowFixManager />
    </div>
  );
}