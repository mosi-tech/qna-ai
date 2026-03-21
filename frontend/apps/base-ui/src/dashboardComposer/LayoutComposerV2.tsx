import React, { useState, useMemo, useEffect } from 'react';
import { Card, Badge } from '../tremor';
import { CREATIVE_GRIDS } from './CreativeGrids';
import { REAL_BLOCKS, BLOCKS_BY_CATEGORY, BLOCK_CATEGORIES } from './RealBlocksRegistry';
import { GridTemplateId, SlotConfig, BlockType } from './types';

interface Approvals {
  [blockId: string]: string[]; // Array of approved widths like ['full', '1/2', '1/3']
}

interface LayoutComposerV2Props {
  onBack?: () => void;
}

export const LayoutComposerV2: React.FC<LayoutComposerV2Props> = ({ onBack }) => {
  const gridIds = Object.keys(CREATIVE_GRIDS);
  const [templateId, setTemplateId] = useState<GridTemplateId>(gridIds[0] as GridTemplateId);
  const [selectedCategory, setSelectedCategory] = useState<string>(BLOCK_CATEGORIES[0]);
  const [slotBlocks, setSlotBlocks] = useState<Record<string, string>>({}); // Store block IDs instead of indices
  const [approvals, setApprovals] = useState<Approvals>({});
  const [filterApproved, setFilterApproved] = useState(false);

  const template = CREATIVE_GRIDS[templateId] || CREATIVE_GRIDS[gridIds[0]];

  // Load approvals from API (backend file) on mount
  useEffect(() => {
    const loadApprovals = async () => {
      try {
        // Fetch from API (approvals.json file on backend)
        const response = await fetch('/api/width-approvals');
        if (response.ok) {
          const data = await response.json();
          const backendApprovals = data.data || {};
          console.log('✓ Loaded approvals from backend:', backendApprovals);
          setApprovals(backendApprovals);
          // Also sync to localStorage
          localStorage.setItem('widthApprovals', JSON.stringify(backendApprovals));
        }
      } catch (err) {
        console.warn('Backend sync failed, trying localStorage:', err);
        // Fallback to localStorage if API fails
        try {
          const saved = localStorage.getItem('widthApprovals');
          if (saved) {
            setApprovals(JSON.parse(saved));
          }
        } catch (localErr) {
          console.error('Error loading approvals:', localErr);
        }
      }
    };
    loadApprovals();
  }, []);

  // Get blocks for selected category, optionally filtered by approvals
  const categoryBlocks = useMemo(() => {
    const blocks = BLOCKS_BY_CATEGORY[selectedCategory as keyof typeof BLOCKS_BY_CATEGORY] || REAL_BLOCKS;

    if (!filterApproved) return blocks;

    // Filter to only blocks with at least one approval
    return blocks.filter((block) => {
      const blockApprovals = approvals[block.id];
      return blockApprovals && blockApprovals.length > 0;
    });
  }, [selectedCategory, filterApproved, approvals]);

  if (!template) {
    return <div className="p-8 text-red-600">Error: No grid templates found</div>;
  }

  // Initialize slot blocks on template change
  React.useEffect(() => {
    if (template) {
      const newSlotBlocks: Record<string, string> = {};
      template.slots.forEach((slot) => {
        const slotWidth = slot.width || 'full';
        // Get blocks ONLY approved for this slot's width
        const validBlocksForSlot = REAL_BLOCKS.filter((block) => {
          const blockApprovals = approvals[block.id] || [];
          return blockApprovals.includes(slotWidth);
        });
        if (validBlocksForSlot.length > 0) {
          const randomBlock = validBlocksForSlot[Math.floor(Math.random() * validBlocksForSlot.length)];
          newSlotBlocks[slot.id] = randomBlock.id;
        }
      });
      setSlotBlocks(newSlotBlocks);
    }
  }, [templateId, template, approvals]);

  const handleTemplateChange = (id: string) => {
    setTemplateId(id as GridTemplateId);
    setSlotBlocks({}); // Clear old slot blocks when changing layout
  };

  const randomizeGridStructure = () => {
    // Randomly pick a grid layout
    const randomGrid = gridIds[Math.floor(Math.random() * gridIds.length)];
    setTemplateId(randomGrid as GridTemplateId);
  };

  const randomizeContent = () => {
    // Populate current grid with random approved blocks
    if (!template) return;

    const newSlotBlocks: Record<string, string> = {};
    template.slots.forEach((slot) => {
      const slotWidth = slot.width || 'full';
      // Get blocks ONLY approved for this slot's width
      const validBlocksForSlot = categoryBlocks.filter((block) => {
        const blockApprovals = approvals[block.id] || [];
        return blockApprovals.includes(slotWidth);
      });
      if (validBlocksForSlot.length > 0) {
        const randomBlock = validBlocksForSlot[Math.floor(Math.random() * validBlocksForSlot.length)];
        newSlotBlocks[slot.id] = randomBlock.id;
      }
    });
    setSlotBlocks(newSlotBlocks);
  };


  // Map colSpan to col-span class
  const getColSpanClass = (colSpan: number): string => {
    switch (colSpan) {
      case 1: return 'col-span-1';
      case 2: return 'col-span-2';
      case 3: return 'col-span-3';
      case 4: return 'col-span-4';
      case 5: return 'col-span-5';
      case 6: return 'col-span-6';
      default: return 'col-span-1';
    }
  };

  const renderSlot = (slotId: string) => {
    const slot = template.slots.find(s => s.id === slotId);
    const slotWidth = slot?.width || 'full';

    // Filter blocks: ONLY those approved for this slot's width
    const validBlocksForSlot = REAL_BLOCKS.filter((block) => {
      const blockApprovals = approvals[block.id];
      const isValid = blockApprovals && blockApprovals.includes(slotWidth);
      return isValid;
    });

    const currentBlockId = slotBlocks[slotId];
    const currentBlock = validBlocksForSlot.find(b => b.id === currentBlockId) || validBlocksForSlot[0];

    // Don't render anything if no blocks approved for this slot
    if (!currentBlock) {
      console.warn(`Slot ${slotId} has NO approved blocks for width ${slotWidth}`);
      return null;
    }

    const Component = currentBlock.component;
    const props = currentBlock.defaultProps || {};
    const colSpanClass = getColSpanClass(slot?.colSpan || 1);

    return (
      <div
        key={slotId}
        className={`${colSpanClass} bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-4 overflow-hidden`}
        style={{ containerType: 'inline-size' }}
      >
        {/* Block content only - no header/footer */}
        <Component {...props} />
      </div>
    );
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50 dark:bg-gray-950">
      {/* Fixed Control Panel */}
      <div className="fixed top-4 left-4 right-4 z-50 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 border border-gray-200 dark:border-gray-700">
        <div className="space-y-3">
          {/* Header Row */}
          <div className="flex items-center justify-between gap-4">
            <div className="flex-1 min-w-0">
              {onBack && (
                <button
                  onClick={onBack}
                  className="text-xs font-semibold text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition mb-1"
                >
                  ← Back
                </button>
              )}
              <div className="text-sm font-bold text-gray-900 dark:text-white">Dashboard Composer</div>
              <div className="text-xs text-gray-500 dark:text-gray-400">{gridIds.length} layouts • {Object.keys(approvals).length} approved</div>
            </div>
            <div className="flex items-center gap-2 flex-shrink-0">
              <button
                onClick={() => setFilterApproved(!filterApproved)}
                className={`px-3 py-1 rounded text-xs font-medium transition ${
                  filterApproved
                    ? 'bg-green-500 text-white hover:bg-green-600'
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-300'
                }`}
              >
                {filterApproved ? '✓ Approved' : 'All'}
              </button>
              <button
                onClick={randomizeGridStructure}
                className="px-3 py-1 bg-purple-500 hover:bg-purple-600 rounded text-xs font-medium text-white transition"
              >
                Grid
              </button>
              <button
                onClick={randomizeContent}
                className="px-3 py-1 bg-blue-500 hover:bg-blue-600 rounded text-xs font-medium text-white transition"
              >
                Content
              </button>
            </div>
          </div>

          {/* Layout Selector */}
          <div>
            <label className="text-xs font-semibold text-gray-700 dark:text-gray-300 block mb-2">Layouts</label>
            <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 gap-1 max-h-16 overflow-y-auto">
              {Object.values(CREATIVE_GRIDS).map((grid) => (
                <button
                  key={grid.id}
                  onClick={() => handleTemplateChange(grid.id)}
                  className={`px-2 py-1 rounded text-xs font-medium transition ${
                    templateId === grid.id
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-300'
                  }`}
                  title={grid.name}
                >
                  {grid.name.split(' ')[0]}
                </button>
              ))}
            </div>
          </div>

          {/* Info */}
          <div className="text-xs text-gray-600 dark:text-gray-400">
            {template.name} • {template.slots.length} slots
          </div>
        </div>
      </div>

      {/* Main Preview Area */}
      <div className="flex-1 overflow-auto p-4 bg-gray-100 dark:bg-gray-800" style={{ paddingTop: '20rem' }}>
        <div style={{ maxWidth: '1280px', width: '100%', margin: '0 auto' }} className="bg-white dark:bg-gray-900 rounded-lg shadow-lg p-4">
          <div className={`grid ${template.cssClass} auto-rows-max gap-6`}>
            {template.slots.map((slot) => renderSlot(slot.id))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LayoutComposerV2;
