import React, { useState, useMemo } from 'react';
import { Card, Badge } from '../tremor';
import { CREATIVE_GRIDS } from './CreativeGrids';
import { REAL_BLOCKS, BLOCKS_BY_CATEGORY, BLOCK_CATEGORIES } from './RealBlocksRegistry';
import { GridTemplateId, SlotConfig, BlockType } from './types';

export const LayoutComposerV2: React.FC = () => {
  const gridIds = Object.keys(CREATIVE_GRIDS);
  const [templateId, setTemplateId] = useState<GridTemplateId>(gridIds[0] as GridTemplateId);
  const [selectedCategory, setSelectedCategory] = useState<string>(BLOCK_CATEGORIES[0]);
  const [slotBlocks, setSlotBlocks] = useState<Record<string, number>>({});

  const template = CREATIVE_GRIDS[templateId] || CREATIVE_GRIDS[gridIds[0]];

  // Get blocks for selected category
  const categoryBlocks = useMemo(() => {
    return BLOCKS_BY_CATEGORY[selectedCategory as keyof typeof BLOCKS_BY_CATEGORY] || REAL_BLOCKS;
  }, [selectedCategory]);

  if (!template) {
    return <div className="p-8 text-red-600">Error: No grid templates found</div>;
  }

  // Initialize slot blocks on template change
  React.useEffect(() => {
    if (template) {
      const newSlotBlocks: Record<string, number> = {};
      template.slots.forEach((slot) => {
        newSlotBlocks[slot.id] = Math.floor(Math.random() * REAL_BLOCKS.length);
      });
      setSlotBlocks(newSlotBlocks);
    }
  }, [templateId, template]);

  const handleTemplateChange = (id: string) => {
    setTemplateId(id as GridTemplateId);
  };

  const handleRandomize = () => {
    // Randomize grid
    const randomGrid = gridIds[Math.floor(Math.random() * gridIds.length)];
    setTemplateId(randomGrid as GridTemplateId);

    // Randomize blocks will happen via useEffect
  };

  const handleBlockNext = (slotId: string) => {
    setSlotBlocks((prev) => ({
      ...prev,
      [slotId]: (prev[slotId] + 1) % categoryBlocks.length,
    }));
  };

  const handleBlockPrev = (slotId: string) => {
    setSlotBlocks((prev) => ({
      ...prev,
      [slotId]: (prev[slotId] - 1 + categoryBlocks.length) % categoryBlocks.length,
    }));
  };

  const renderSlot = (slotId: string) => {
    const blockIndex = slotBlocks[slotId] || 0;
    // Ensure blockIndex is within bounds
    const safeIndex = Math.min(blockIndex, categoryBlocks.length - 1);
    const currentBlock = categoryBlocks[safeIndex];

    if (!currentBlock) {
      return <div className="p-4 text-red-600">Error: No blocks available</div>;
    }

    const Component = currentBlock.component;
    const props = currentBlock.defaultProps || {};

    return (
      <div
        key={slotId}
        className="flex flex-col h-full bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 overflow-hidden shadow-sm hover:shadow-md transition"
      >
        {/* Block carousel header */}
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 p-3 flex items-center justify-between flex-shrink-0">
          <div className="flex-1 min-w-0">
            <div className="text-xs text-blue-100 font-semibold truncate">{slotId}</div>
            <div className="text-sm font-bold text-white truncate">{currentBlock.name}</div>
          </div>
          <div className="text-xs text-blue-100 bg-blue-700 px-2 py-1 rounded whitespace-nowrap ml-2">
            {safeIndex + 1}/{categoryBlocks.length}
          </div>
        </div>

        {/* Block content */}
        <div className="overflow-auto p-3 bg-gray-50 dark:bg-gray-800/30">
          <Component {...props} />
        </div>

        {/* Carousel controls */}
        <div className="border-t border-gray-200 dark:border-gray-800 p-2 flex items-center justify-between gap-2 bg-gray-50 dark:bg-gray-800 flex-shrink-0">
          <button
            onClick={() => handleBlockPrev(slotId)}
            className="px-2 py-1 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded text-xs font-medium text-gray-900 dark:text-white transition flex-shrink-0"
          >
            ← Prev
          </button>

          {/* Block Type Selector - Middle */}
          <select
            value={selectedCategory}
            onChange={(e) => {
              setSelectedCategory(e.target.value);
              setSlotBlocks({});
            }}
            className="flex-1 px-2 py-1 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded text-xs font-medium text-gray-900 dark:text-white hover:border-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 min-w-0"
          >
            {BLOCK_CATEGORIES.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>

          <button
            onClick={() => handleBlockNext(slotId)}
            className="px-2 py-1 bg-blue-500 hover:bg-blue-600 rounded text-xs font-medium text-white transition flex-shrink-0"
          >
            Next →
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50 dark:bg-gray-950">
      {/* Top Control Panel - Fixed */}
      <div className="flex-shrink-0 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 p-4 space-y-3">
        {/* Header with Randomize */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              Dashboard Composer
            </h2>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
              {gridIds.length} layouts • Select block type in slot controls
            </p>
          </div>
          <button
            onClick={handleRandomize}
            className="px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 rounded-lg text-white font-bold text-sm transition transform hover:scale-105"
          >
            🎲 Randomize
          </button>
        </div>

        {/* Template Selector Grid */}
        <div>
          <h3 className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">
            Layouts ({gridIds.length})
          </h3>
          <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-1 max-h-24 overflow-y-auto p-1 bg-gray-50 dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700">
            {Object.values(CREATIVE_GRIDS).map((grid) => (
              <button
                key={grid.id}
                onClick={() => handleTemplateChange(grid.id)}
                className={`p-1 rounded text-xs font-medium transition text-center transform hover:scale-105 ${
                  templateId === grid.id
                    ? 'bg-blue-600 text-white ring-2 ring-blue-400 shadow-lg'
                    : 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-100 dark:hover:bg-gray-600 border border-gray-200 dark:border-gray-600'
                }`}
                title={grid.description}
              >
                <div className="font-bold text-xs leading-tight">{grid.name}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Info Row */}
        <div className="flex items-center justify-between text-xs">
          <div className="text-gray-600 dark:text-gray-400">
            <strong>{template.name}</strong> • {template.slots.length} slots
          </div>
          <div className="text-gray-500 dark:text-gray-500">
            Scroll blocks • Prev/Next to cycle
          </div>
        </div>
      </div>

      {/* Main Preview Area - Scrollable */}
      <div className="flex-1 overflow-auto p-4">
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <div className={`grid ${template.cssClass} gap-3 auto-rows-max`}>
            {template.slots.map((slot) => renderSlot(slot.id))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LayoutComposerV2;
