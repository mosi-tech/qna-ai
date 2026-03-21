import React, { useState, useMemo, useEffect } from 'react';
import { REAL_BLOCKS, BLOCKS_BY_CATEGORY, BLOCK_CATEGORIES } from './RealBlocksRegistry';

type WidthSize = 'full' | '1/2' | '1/3' | '2/3' | '1/4' | '3/4';
type ViewportMode = 'mobile' | 'tablet' | 'desktop';

interface WidthConfig {
  size: WidthSize;
  label: string;
  widthClass: string;
}

const WIDTHS: WidthConfig[] = [
  { size: 'full', label: 'Full Width (100%)', widthClass: 'w-full' },
  { size: '1/2', label: 'Half Width (50%)', widthClass: 'w-1/2' },
  { size: '1/3', label: 'Third Width (33%)', widthClass: 'w-1/3' },
  { size: '2/3', label: 'Two Thirds (66%)', widthClass: 'w-2/3' },
  { size: '1/4', label: 'Quarter Width (25%)', widthClass: 'w-1/4' },
  { size: '3/4', label: 'Three Quarters (75%)', widthClass: 'w-3/4' },
];

const VIEWPORT_CONFIGS = {
  mobile: { label: 'Mobile', width: '375px' },
  tablet: { label: 'Tablet', width: '768px' },
  desktop: { label: 'Desktop', width: '1280px' },
};

interface WidthState {
  category: string;
  blockIndex: number;
}

interface WidthCompatibilityTesterProps {
  onBack?: () => void;
}

export const WidthCompatibilityTester: React.FC<WidthCompatibilityTesterProps> = ({ onBack }) => {
  const [viewport, setViewport] = useState<ViewportMode>('desktop');
  const [widthStates, setWidthStates] = useState<Record<WidthSize, WidthState>>({
    full: { category: BLOCK_CATEGORIES[0], blockIndex: 0 },
    '1/2': { category: BLOCK_CATEGORIES[0], blockIndex: 0 },
    '1/3': { category: BLOCK_CATEGORIES[0], blockIndex: 0 },
    '2/3': { category: BLOCK_CATEGORIES[0], blockIndex: 0 },
    '1/4': { category: BLOCK_CATEGORIES[0], blockIndex: 0 },
    '3/4': { category: BLOCK_CATEGORIES[0], blockIndex: 0 },
  });
  const [approvals, setApprovals] = useState<Record<string, WidthSize[]>>({});
  const hasLoadedRef = React.useRef(false);

  // Load approvals from localStorage first, then sync with backend
  useEffect(() => {
    const loadApprovals = async () => {
      try {
        // Try localStorage first (fast)
        const saved = localStorage.getItem('widthApprovals');
        if (saved) {
          const parsed = JSON.parse(saved);
          console.log('✓ Loaded from localStorage:', parsed);
          setApprovals(parsed);
        }

        // Sync with backend file in background
        try {
          const response = await fetch('/api/width-approvals');
          if (response.ok) {
            const data = await response.json();
            const backendApprovals = data.data || {};
            // Use backend data if it's newer/different
            if (Object.keys(backendApprovals).length > 0) {
              console.log('✓ Synced from backend:', backendApprovals);
              setApprovals(backendApprovals);
              localStorage.setItem('widthApprovals', JSON.stringify(backendApprovals));
            }
          }
        } catch (err) {
          console.warn('Backend sync failed, using localStorage:', err.message);
        }
      } catch (err) {
        console.error('Error loading approvals:', err);
        setApprovals({});
      } finally {
        hasLoadedRef.current = true;
      }
    };

    loadApprovals();
  }, []);

  // Save approvals to localStorage immediately, sync with backend in background
  useEffect(() => {
    if (!hasLoadedRef.current) {
      return;
    }

    // Save to localStorage immediately (fast)
    try {
      console.log('💾 Saving to localStorage:', approvals);
      localStorage.setItem('widthApprovals', JSON.stringify(approvals));
    } catch (err) {
      console.error('Error saving to localStorage:', err);
    }

    // Sync to backend file in background (non-blocking)
    const syncToBackend = async () => {
      try {
        const response = await fetch('/api/width-approvals', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(approvals),
        });
        if (response.ok) {
          console.log('✓ Synced to backend file');
        } else {
          console.warn('Backend sync failed:', response.status);
        }
      } catch (err) {
        console.warn('Backend sync error (data safe in localStorage):', err.message);
      }
    };

    syncToBackend();
  }, [approvals]);

  const handleCategoryChange = (width: WidthSize, category: string) => {
    setWidthStates((prev) => ({
      ...prev,
      [width]: { ...prev[width], category, blockIndex: 0 },
    }));
  };

  const handleBlockNext = (width: WidthSize) => {
    const state = widthStates[width];
    const categoryBlocks =
      BLOCKS_BY_CATEGORY[state.category as keyof typeof BLOCKS_BY_CATEGORY] ||
      REAL_BLOCKS;
    setWidthStates((prev) => ({
      ...prev,
      [width]: {
        ...prev[width],
        blockIndex: (prev[width].blockIndex + 1) % categoryBlocks.length,
      },
    }));
  };

  const handleBlockPrev = (width: WidthSize) => {
    const state = widthStates[width];
    const categoryBlocks =
      BLOCKS_BY_CATEGORY[state.category as keyof typeof BLOCKS_BY_CATEGORY] ||
      REAL_BLOCKS;
    setWidthStates((prev) => ({
      ...prev,
      [width]: {
        ...prev[width],
        blockIndex:
          (prev[width].blockIndex - 1 + categoryBlocks.length) %
          categoryBlocks.length,
      },
    }));
  };

  const handleToggleApproval = (blockId: string, width: WidthSize) => {
    setApprovals((prev) => {
      const current = prev[blockId] || [];
      const updated = current.includes(width)
        ? current.filter((w) => w !== width)
        : [...current, width];
      return {
        ...prev,
        [blockId]: updated,
      };
    });
  };


  const renderWidth = (width: WidthConfig) => {
    const state = widthStates[width.size];
    const categoryBlocks =
      BLOCKS_BY_CATEGORY[state.category as keyof typeof BLOCKS_BY_CATEGORY] ||
      REAL_BLOCKS;
    const currentBlock = categoryBlocks[state.blockIndex];

    if (!currentBlock) {
      return <div className="text-red-600">No blocks available</div>;
    }

    const Component = currentBlock.component;
    const blockApprovals = approvals[currentBlock.id] || [];

    return (
      <div
        key={width.size}
        className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4"
      >
        {/* Width Header */}
        <div className="mb-3 pb-3 border-b border-gray-200 dark:border-gray-800 space-y-2">
          <div className="flex items-center justify-between gap-2">
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white">
                {width.label}
              </h3>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {width.size === 'full'
                  ? 'Full width'
                  : `${(parseFloat(width.size.split('/')[0]) / parseFloat(width.size.split('/')[1]) * 100).toFixed(0)}% width`}
              </p>
            </div>

            {/* Approval checkbox */}
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={blockApprovals.includes(width.size)}
                onChange={() => {
                  handleToggleApproval(currentBlock.id, width.size);
                }}
                className="w-4 h-4 rounded cursor-pointer"
              />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300 cursor-pointer whitespace-nowrap"
                onClick={() => handleToggleApproval(currentBlock.id, width.size)}>
                {blockApprovals.includes(width.size) ? '✓' : '○'}
              </span>
            </div>
          </div>

          {/* Controls row */}
          <div className="flex items-center gap-2 flex-wrap">
            {/* Category selector */}
            <select
              value={state.category}
              onChange={(e) => handleCategoryChange(width.size, e.target.value)}
              className="flex-1 min-w-[150px] px-2 py-1 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded text-xs font-medium text-gray-900 dark:text-white"
            >
              {BLOCK_CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>

            {/* Component name display */}
            <span className="text-xs font-semibold text-gray-700 dark:text-gray-300 px-2 py-1 bg-gray-200 dark:bg-gray-800 rounded whitespace-nowrap">
              {categoryBlocks.length > 0 ? `${state.category} (${state.blockIndex + 1}/${categoryBlocks.length})` : 'No blocks'}
            </span>

            {/* Navigation controls */}
            <button
              onClick={() => handleBlockPrev(width.size)}
              className="px-2 py-1 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded text-xs font-medium text-gray-900 dark:text-white transition flex-shrink-0"
            >
              ← Prev
            </button>
            <button
              onClick={() => handleBlockNext(width.size)}
              className="px-2 py-1 bg-blue-500 hover:bg-blue-600 rounded text-xs font-medium text-white transition flex-shrink-0"
            >
              Next →
            </button>
          </div>
        </div>

        {/* Component Preview - Container with viewport width */}
        <div
          style={{ width: VIEWPORT_CONFIGS[viewport].width, maxWidth: '100%' }}
          className="mx-auto bg-gray-100 dark:bg-gray-800 rounded p-2 overflow-x-auto border border-dashed border-gray-300 dark:border-gray-700"
        >
          {/* Content at specified width variant - Container Query Enabled */}
          <div
            className={`${width.widthClass} bg-white dark:bg-gray-900 rounded p-4`}
            style={{ containerType: 'inline-size' }}
          >
            <Component {...currentBlock.defaultProps} />
          </div>
        </div>
      </div>
    );
  };

  const viewportWidthStyle = {
    maxWidth: VIEWPORT_CONFIGS[viewport].width,
    width: '100%',
    margin: '0 auto',
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50 dark:bg-gray-950">
      {/* Viewport Selector & Controls - Floating */}
      <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-3 border border-gray-200 dark:border-gray-700">
        {onBack && (
          <button
            onClick={onBack}
            className="px-3 py-1 text-xs font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition"
          >
            ← Back
          </button>
        )}
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-gray-700 dark:text-gray-300 px-2">
            Viewport:
          </span>
          {(Object.keys(VIEWPORT_CONFIGS) as ViewportMode[]).map((mode) => (
            <button
              key={mode}
              onClick={() => setViewport(mode)}
              className={`px-3 py-1 rounded text-xs font-medium transition ${
                viewport === mode
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-300 dark:hover:bg-gray-600'
              }`}
            >
              {VIEWPORT_CONFIGS[mode].label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Scrollable Area - Constrained to viewport width */}
      <div
        className="flex-1 overflow-auto p-4 pt-20 bg-gray-200 dark:bg-gray-800"
        style={{
          fontSize:
            viewport === 'mobile'
              ? '13px'
              : viewport === 'tablet'
                ? '15px'
                : '17px',
          '--scale-factor':
            viewport === 'mobile'
              ? '0.75'
              : viewport === 'tablet'
                ? '0.9'
                : '1',
        } as React.CSSProperties & { '--scale-factor': string }}
      >
        <div style={viewportWidthStyle} className="bg-white dark:bg-gray-900 rounded-lg shadow-lg p-4">
          <div className="space-y-6">
            {WIDTHS.map((width) => renderWidth(width))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default WidthCompatibilityTester;
