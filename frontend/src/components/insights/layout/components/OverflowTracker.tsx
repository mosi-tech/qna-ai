/**
 * Overflow Tracker Component
 * Provides interactive overlay for tracking component overflow and quality issues
 */

'use client';

import React, { useState, useContext, createContext } from 'react';
import { addOverflowRecord, OverflowRecord, updateOverflowRecord } from '../utils/overflowTracker';

// Debug mode context
interface DebugContextType {
  debugMode: boolean;
  setDebugMode: (enabled: boolean) => void;
}

const DebugContext = createContext<DebugContextType>({
  debugMode: false,
  setDebugMode: () => {},
});

export const DebugProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [debugMode, setDebugMode] = useState(false);
  
  return (
    <DebugContext.Provider value={{ debugMode, setDebugMode }}>
      {children}
    </DebugContext.Provider>
  );
};

export const useDebugMode = () => useContext(DebugContext);

// Get space mapping from the tracker utils
const spaceMapping: Record<string, string> = {
  // Layout 1 (4x6 mixed)
  "halfWidthTopLeft": "half_width",
  "halfWidthTopRight": "half_width",
  "quarterWidthMiddleLeft": "quarter_width", 
  "halfWidthMiddleCenter": "half_width",
  "quarterWidthMiddleRight": "quarter_width",
  "fullWidthBottom": "full_width",
  
  // Layout 2 (2x5)
  "leftPrimary": "half_width",
  "rightPrimary": "half_width",
  "leftSecondary": "half_width",
  "rightSecondary": "half_width",
  "fullWidthBottom2x5": "full_width",
  
  // Add more as needed...
};

interface OverflowTrackerProps {
  componentName: string;
  componentType: string;
  layoutName: string;
  spaceName: string;
  children: React.ReactNode;
  className?: string;
}

export default function OverflowTracker({
  componentName,
  componentType,
  layoutName,
  spaceName,
  children,
  className = "",
}: OverflowTrackerProps) {
  const { debugMode } = useDebugMode();
  const [showModal, setShowModal] = useState(false);
  const [isRecorded, setIsRecorded] = useState(false);
  
  // Form state
  const [hasOverflow, setHasOverflow] = useState(false);
  const [qualityRating, setQualityRating] = useState<1 | 2 | 3 | 4 | 5 | null>(null);
  const [userNotes, setUserNotes] = useState('');
  const [issues, setIssues] = useState({
    overflow: false,
    poorDesign: false,
    wrongVariant: false,
    misplacedComponent: false,
    responsive: false,
    other: false,
  });

  const spaceType = spaceMapping[spaceName] || 'unknown';

  const handleQuickOverflow = () => {
    // Quick record for just overflow
    const record = {
      componentName,
      componentType,
      layoutName,
      spaceName,
      spaceType,
      hasOverflow: true,
      issues: { overflow: true },
    };
    
    addOverflowRecord(record);
    setIsRecorded(true);
    
    // Auto-hide after 2 seconds
    setTimeout(() => setIsRecorded(false), 2000);
  };

  const handleDetailedRecord = () => {
    const record = {
      componentName,
      componentType,
      layoutName,
      spaceName,
      spaceType,
      hasOverflow,
      qualityRating: qualityRating || undefined,
      userNotes: userNotes.trim() || undefined,
      issues,
    };
    
    addOverflowRecord(record);
    setShowModal(false);
    setIsRecorded(true);
    
    // Reset form
    setHasOverflow(false);
    setQualityRating(null);
    setUserNotes('');
    setIssues({
      overflow: false,
      poorDesign: false,
      wrongVariant: false,
      misplacedComponent: false,
      responsive: false,
      other: false,
    });
    
    // Auto-hide after 3 seconds
    setTimeout(() => setIsRecorded(false), 3000);
  };

  const handleIssueChange = (issueType: keyof typeof issues) => {
    setIssues(prev => ({
      ...prev,
      [issueType]: !prev[issueType]
    }));
  };

  if (!debugMode) {
    return <>{children}</>;
  }

  return (
    <>
      <div className={`relative group ${className}`}>
        {/* Debug buttons overlay */}
        <div className="absolute top-1 right-1 z-50 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          {/* Quick overflow button */}
          <button
            onClick={handleQuickOverflow}
            className={`px-2 py-1 text-xs rounded transition-colors ${
              isRecorded 
                ? 'bg-green-500 text-white' 
                : 'bg-red-500 text-white hover:bg-red-600'
            }`}
            title="Quick mark overflow"
          >
            {isRecorded ? '✓' : '⚠️'}
          </button>
          
          {/* Detailed feedback button */}
          <button
            onClick={() => setShowModal(true)}
            className="px-2 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
            title="Detailed feedback"
          >
            📝
          </button>
        </div>
        
        {/* Component content */}
        {children}
      </div>

      {/* Detailed feedback modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[100]">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Component Feedback</h3>
              <button
                onClick={() => setShowModal(false)}
                className="text-gray-500 hover:text-gray-700 text-xl"
              >
                ×
              </button>
            </div>
            
            {/* Component info */}
            <div className="mb-4 p-3 bg-gray-50 rounded text-sm">
              <div><strong>Component:</strong> {componentType}</div>
              <div><strong>Layout:</strong> {layoutName}</div>
              <div><strong>Space:</strong> {spaceName} ({spaceType})</div>
            </div>

            {/* Quality Rating */}
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Quality Rating</label>
              <div className="flex gap-1">
                {[1, 2, 3, 4, 5].map((rating) => (
                  <button
                    key={rating}
                    onClick={() => setQualityRating(rating as 1 | 2 | 3 | 4 | 5)}
                    className={`w-8 h-8 rounded text-sm transition-colors ${
                      qualityRating === rating
                        ? 'bg-yellow-400 text-white'
                        : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                    }`}
                  >
                    ★
                  </button>
                ))}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                1 = Very Poor, 3 = Average, 5 = Excellent
              </div>
            </div>

            {/* Issues checklist */}
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Issues (select all that apply)</label>
              <div className="space-y-2">
                {Object.entries({
                  overflow: 'Content overflows container',
                  poorDesign: 'Poor visual design/layout',
                  wrongVariant: 'Wrong component variant',
                  misplacedComponent: 'Wrong component for this space',
                  responsive: 'Responsive behavior issues',
                  other: 'Other issues',
                }).map(([key, label]) => (
                  <label key={key} className="flex items-center text-sm">
                    <input
                      type="checkbox"
                      checked={issues[key as keyof typeof issues]}
                      onChange={() => handleIssueChange(key as keyof typeof issues)}
                      className="mr-2 rounded"
                    />
                    {label}
                  </label>
                ))}
              </div>
            </div>

            {/* Notes */}
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Notes</label>
              <textarea
                value={userNotes}
                onChange={(e) => setUserNotes(e.target.value)}
                placeholder="Additional feedback, suggestions for improvement..."
                className="w-full p-2 border rounded text-sm"
                rows={3}
              />
            </div>

            {/* Action buttons */}
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => setShowModal(false)}
                className="px-4 py-2 text-sm bg-gray-300 text-gray-700 rounded hover:bg-gray-400 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleDetailedRecord}
                className="px-4 py-2 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
              >
                Record Feedback
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}