/**
 * Overflow Fix Manager Component
 * Provides interface for viewing, analyzing, and applying bulk fixes
 */

'use client';

import React, { useState, useEffect } from 'react';
import { 
  getOverflowData, 
  getOverflowStats, 
  markRecordAsFixed,
  removeOverflowRecord,
  OverflowRecord,
  ComponentFix
} from '../utils/overflowTracker';
import { 
  generateBulkFixes, 
  generateFixReport, 
  analyzeOverflowRecord,
  getComponentSuggestionsForSpace
} from '../utils/overflowFixer';

export default function OverflowFixManager() {
  const [records, setRecords] = useState<OverflowRecord[]>([]);
  const [fixes, setFixes] = useState<ComponentFix[]>([]);
  const [showDetails, setShowDetails] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState<OverflowRecord | null>(null);
  const [fixReport, setFixReport] = useState<any>(null);

  useEffect(() => {
    refreshData();
  }, []);

  const refreshData = () => {
    const data = getOverflowData();
    setRecords(data);
    
    if (data.length > 0) {
      const generatedFixes = generateBulkFixes(data);
      setFixes(generatedFixes);
      setFixReport(generateFixReport(generatedFixes));
    }
  };

  const handleMarkAsFixed = (recordId: string) => {
    markRecordAsFixed(recordId);
    refreshData();
  };

  const handleRemoveRecord = (recordId: string) => {
    if (confirm('Are you sure you want to remove this record?')) {
      removeOverflowRecord(recordId);
      refreshData();
    }
  };

  const applyAllFixes = () => {
    if (confirm(`Apply ${fixes.length} automated fixes? This will update component configurations.`)) {
      // Mark all records as fixed
      fixes.forEach(fix => markRecordAsFixed(fix.id));
      
      // Generate fix configuration
      const config = {
        appliedAt: new Date().toISOString(),
        fixes: fixes,
        report: fixReport
      };
      
      // Download configuration file
      const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `overflow-fixes-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
      
      refreshData();
      alert(`Applied ${fixes.length} fixes successfully! Configuration downloaded.`);
    }
  };

  const stats = getOverflowStats();
  
  if (records.length === 0) {
    return (
      <div className="p-6 text-center text-gray-500">
        <h3 className="text-lg font-medium mb-2">No overflow data recorded yet</h3>
        <p className="text-sm">Enable debug mode and start marking components to see fix suggestions here.</p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Overflow Fix Manager</h2>
            <p className="text-gray-600">Analyze issues and apply automated fixes</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={refreshData}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              🔄 Refresh
            </button>
            {fixes.length > 0 && (
              <button
                onClick={applyAllFixes}
                className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
              >
                ✅ Apply All Fixes ({fixes.length})
              </button>
            )}
          </div>
        </div>

        {/* Stats Summary */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="text-2xl font-bold text-blue-600">{stats.total}</div>
            <div className="text-sm text-blue-600">Total Issues</div>
          </div>
          <div className="p-4 bg-red-50 rounded-lg border border-red-200">
            <div className="text-2xl font-bold text-red-600">{stats.unfixed}</div>
            <div className="text-sm text-red-600">Unfixed</div>
          </div>
          <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
            <div className="text-2xl font-bold text-yellow-600">
              {stats.qualityStats.avgRating.toFixed(1)}★
            </div>
            <div className="text-sm text-yellow-600">Avg Quality</div>
          </div>
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <div className="text-2xl font-bold text-green-600">{fixes.length}</div>
            <div className="text-sm text-green-600">Auto Fixes</div>
          </div>
        </div>

        {/* Fix Report Summary */}
        {fixReport && (
          <div className="mb-6 p-4 bg-gray-50 rounded-lg border">
            <h3 className="font-semibold mb-2">Fix Analysis Summary</h3>
            <p className="text-sm text-gray-700 mb-3">{fixReport.summary}</p>
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <strong>By Type:</strong>
                <ul className="mt-1">
                  {Object.entries(fixReport.byType).map(([type, count]) => (
                    <li key={type} className="flex justify-between">
                      <span className="capitalize">{type}:</span>
                      <span>{count as number}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <strong>By Confidence:</strong>
                <ul className="mt-1">
                  {Object.entries(fixReport.byConfidence).map(([conf, count]) => (
                    <li key={conf} className="flex justify-between">
                      <span className="capitalize">{conf}:</span>
                      <span>{count as number}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <strong>Priority Fixes:</strong>
                <div className="mt-1">
                  <span className="text-green-600 font-medium">
                    {fixReport.highPriorityFixes.length} high-priority fixes ready
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Records Table */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Component</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Layout/Space</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Issues</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Quality</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Suggested Fix</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {records.filter(r => !r.fixed).map(record => {
                const suggestions = analyzeOverflowRecord(record);
                const primaryFix = suggestions.find(s => s.confidence === 'high') || suggestions[0];
                
                return (
                  <tr key={record.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div>
                        <div className="font-medium">{record.componentName}</div>
                        <div className="text-xs text-gray-500">{record.componentType}</div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div>
                        <div className="font-medium">{record.layoutName}</div>
                        <div className="text-xs text-gray-500">
                          {record.spaceName} ({record.spaceType})
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-1">
                        {record.hasOverflow && (
                          <span className="px-1.5 py-0.5 bg-red-100 text-red-700 text-xs rounded">
                            Overflow
                          </span>
                        )}
                        {record.issues?.poorDesign && (
                          <span className="px-1.5 py-0.5 bg-orange-100 text-orange-700 text-xs rounded">
                            Poor Design
                          </span>
                        )}
                        {record.issues?.wrongVariant && (
                          <span className="px-1.5 py-0.5 bg-blue-100 text-blue-700 text-xs rounded">
                            Wrong Variant
                          </span>
                        )}
                        {record.issues?.misplacedComponent && (
                          <span className="px-1.5 py-0.5 bg-purple-100 text-purple-700 text-xs rounded">
                            Misplaced
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      {record.qualityRating ? (
                        <div className="flex items-center">
                          <span className="text-lg">★</span>
                          <span className="ml-1">{record.qualityRating}</span>
                        </div>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      {primaryFix ? (
                        <div>
                          <div className="font-medium text-sm">{primaryFix.action}</div>
                          <div className="text-xs text-gray-500">{primaryFix.reason}</div>
                          <span className={`inline-block mt-1 px-1.5 py-0.5 text-xs rounded ${
                            primaryFix.confidence === 'high' ? 'bg-green-100 text-green-700' :
                            primaryFix.confidence === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                            'bg-gray-100 text-gray-700'
                          }`}>
                            {primaryFix.confidence} confidence
                          </span>
                        </div>
                      ) : (
                        <span className="text-gray-400">No suggestions</span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-1">
                        <button
                          onClick={() => setSelectedRecord(record)}
                          className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded hover:bg-blue-200"
                          title="View details"
                        >
                          👁️
                        </button>
                        <button
                          onClick={() => handleMarkAsFixed(record.id)}
                          className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded hover:bg-green-200"
                          title="Mark as fixed"
                        >
                          ✅
                        </button>
                        <button
                          onClick={() => handleRemoveRecord(record.id)}
                          className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded hover:bg-red-200"
                          title="Remove record"
                        >
                          🗑️
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Record Detail Modal */}
      {selectedRecord && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Record Details</h3>
              <button
                onClick={() => setSelectedRecord(null)}
                className="text-gray-500 hover:text-gray-700 text-xl"
              >
                ×
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <h4 className="font-medium mb-2">Component Information</h4>
                <div className="bg-gray-50 p-3 rounded text-sm space-y-1">
                  <div><strong>Name:</strong> {selectedRecord.componentName}</div>
                  <div><strong>Type:</strong> {selectedRecord.componentType}</div>
                  <div><strong>Layout:</strong> {selectedRecord.layoutName}</div>
                  <div><strong>Space:</strong> {selectedRecord.spaceName} ({selectedRecord.spaceType})</div>
                  <div><strong>Recorded:</strong> {new Date(selectedRecord.timestamp).toLocaleString()}</div>
                </div>
              </div>

              {selectedRecord.qualityRating && (
                <div>
                  <h4 className="font-medium mb-2">Quality Rating</h4>
                  <div className="bg-gray-50 p-3 rounded text-sm">
                    <div className="flex items-center">
                      <span className="text-2xl mr-2">★</span>
                      <span className="text-lg font-medium">{selectedRecord.qualityRating}/5</span>
                    </div>
                  </div>
                </div>
              )}

              {selectedRecord.userNotes && (
                <div>
                  <h4 className="font-medium mb-2">User Notes</h4>
                  <div className="bg-gray-50 p-3 rounded text-sm">
                    {selectedRecord.userNotes}
                  </div>
                </div>
              )}

              <div>
                <h4 className="font-medium mb-2">Fix Suggestions</h4>
                <div className="space-y-2">
                  {analyzeOverflowRecord(selectedRecord).map((suggestion, index) => (
                    <div key={index} className="bg-blue-50 p-3 rounded border border-blue-200">
                      <div className="font-medium text-blue-800">{suggestion.action}</div>
                      <div className="text-sm text-blue-600 mt-1">{suggestion.reason}</div>
                      <span className={`inline-block mt-2 px-2 py-1 text-xs rounded ${
                        suggestion.confidence === 'high' ? 'bg-green-100 text-green-700' :
                        suggestion.confidence === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {suggestion.confidence} confidence
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="font-medium mb-2">Space Configuration</h4>
                <div className="bg-gray-50 p-3 rounded text-sm">
                  {(() => {
                    const suggestions = getComponentSuggestionsForSpace(selectedRecord.spaceType);
                    return (
                      <div>
                        <div className="mb-2"><strong>Description:</strong> {suggestions.description}</div>
                        <div className="mb-2">
                          <strong>Suitable components:</strong> {suggestions.suitable.join(', ') || 'None specified'}
                        </div>
                        <div>
                          <strong>Unsuitable components:</strong> {suggestions.unsuitable.join(', ') || 'None specified'}
                        </div>
                      </div>
                    );
                  })()}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}