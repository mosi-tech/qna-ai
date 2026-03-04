/**
 * Debug Toggle Component
 * Controls debug mode for overflow tracking
 */

'use client';

import React from 'react';
import { useDebugMode } from './OverflowTracker';
import { getOverflowStats, clearAllOverflowData, exportOverflowData } from '../utils/overflowTracker';

export default function DebugToggle() {
  const { debugMode, setDebugMode } = useDebugMode();
  const [stats, setStats] = React.useState(getOverflowStats());
  
  const refreshStats = () => {
    setStats(getOverflowStats());
  };

  React.useEffect(() => {
    // Refresh stats when debug mode changes
    if (debugMode) {
      refreshStats();
      // Set up interval to refresh stats every 5 seconds when in debug mode
      const interval = setInterval(refreshStats, 5000);
      return () => clearInterval(interval);
    }
  }, [debugMode]);

  const handleExport = () => {
    const data = exportOverflowData();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `overflow-analysis-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleClear = () => {
    if (confirm('Are you sure you want to clear all overflow data? This cannot be undone.')) {
      clearAllOverflowData();
      refreshStats();
    }
  };

  return (
    <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg">
      <div className="flex items-center justify-between flex-wrap gap-4">
        {/* Debug Mode Toggle */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setDebugMode(!debugMode)}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              debugMode
                ? 'bg-red-500 text-white hover:bg-red-600 shadow-lg'
                : 'bg-blue-500 text-white hover:bg-blue-600'
            }`}
          >
            {debugMode ? '🛑 Exit Debug Mode' : '🐛 Enable Debug Mode'}
          </button>
          
          {debugMode && (
            <div className="text-sm text-blue-700">
              <span className="font-medium">Debug Active:</span> Hover over components to see tracking buttons
            </div>
          )}
        </div>

        {/* Stats & Controls */}
        {debugMode && (
          <div className="flex items-center gap-2 flex-wrap">
            {/* Quick stats */}
            <div className="flex items-center gap-4 text-sm">
              <div className="px-2 py-1 bg-white rounded border">
                <span className="text-gray-600">Total:</span> 
                <span className="font-semibold ml-1">{stats.total}</span>
              </div>
              <div className="px-2 py-1 bg-white rounded border">
                <span className="text-gray-600">Unfixed:</span> 
                <span className="font-semibold ml-1 text-red-600">{stats.unfixed}</span>
              </div>
              {stats.qualityStats.avgRating > 0 && (
                <div className="px-2 py-1 bg-white rounded border">
                  <span className="text-gray-600">Avg Quality:</span> 
                  <span className="font-semibold ml-1">
                    {stats.qualityStats.avgRating.toFixed(1)}★
                  </span>
                </div>
              )}
            </div>

            {/* Action buttons */}
            <div className="flex gap-2">
              <button
                onClick={refreshStats}
                className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
                title="Refresh stats"
              >
                🔄
              </button>
              
              {stats.total > 0 && (
                <>
                  <button
                    onClick={handleExport}
                    className="px-3 py-1.5 bg-green-600 text-white text-sm rounded hover:bg-green-700 transition-colors"
                    title="Export data"
                  >
                    💾 Export
                  </button>
                  
                  <button
                    onClick={handleClear}
                    className="px-3 py-1.5 bg-red-600 text-white text-sm rounded hover:bg-red-700 transition-colors"
                    title="Clear all data"
                  >
                    🗑️
                  </button>
                </>
              )}
            </div>
          </div>
        )}
      </div>
      
      {/* Extended stats when debug mode is on and there's data */}
      {debugMode && stats.total > 0 && (
        <div className="mt-4 p-3 bg-white rounded border">
          <h4 className="text-sm font-medium mb-2">Issue Breakdown</h4>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2 text-xs">
            <div>
              <span className="text-gray-600">Overflow:</span> 
              <span className="ml-1 font-medium">{stats.issueStats.overflow}</span>
            </div>
            <div>
              <span className="text-gray-600">Poor Design:</span> 
              <span className="ml-1 font-medium">{stats.issueStats.poorDesign}</span>
            </div>
            <div>
              <span className="text-gray-600">Wrong Variant:</span> 
              <span className="ml-1 font-medium">{stats.issueStats.wrongVariant}</span>
            </div>
            <div>
              <span className="text-gray-600">Misplaced:</span> 
              <span className="ml-1 font-medium">{stats.issueStats.misplacedComponent}</span>
            </div>
            <div>
              <span className="text-gray-600">Responsive:</span> 
              <span className="ml-1 font-medium">{stats.issueStats.responsive}</span>
            </div>
            <div>
              <span className="text-gray-600">Other:</span> 
              <span className="ml-1 font-medium">{stats.issueStats.other}</span>
            </div>
          </div>

          {stats.qualityStats.avgRating > 0 && (
            <div className="mt-2">
              <h4 className="text-sm font-medium mb-2">Quality Distribution</h4>
              <div className="flex gap-4 text-xs">
                <span>★★★★★: {stats.qualityStats.excellent}</span>
                <span>★★★★: {stats.qualityStats.good}</span>
                <span>★★★: {stats.qualityStats.average}</span>
                <span>★★: {stats.qualityStats.poor}</span>
                <span>★: {stats.qualityStats.veryPoor}</span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}