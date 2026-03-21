import React, { useState } from 'react';
import { Card, Badge } from '../tremor';
import { GRID_TEMPLATES } from './GridTemplates';
import { BLOCK_REGISTRY, getBlockDefinition } from './BlockRegistry';
import { GridTemplateId, SlotConfig, ComposerState, BlockType } from './types';

export const LayoutComposer: React.FC = () => {
  const [state, setState] = useState<ComposerState>({
    templateId: '2-col',
    slotConfigs: [],
    selectedSlot: null,
  });

  const template = GRID_TEMPLATES[state.templateId];
  
  // Initialize slot configs when template changes
  const initializeSlots = (templateId: GridTemplateId) => {
    const newTemplate = GRID_TEMPLATES[templateId];
    const configs: SlotConfig[] = newTemplate.slots.map((slot) => ({
      slotId: slot.id,
      blockType: 'empty' as BlockType,
    }));
    setState((prev) => ({
      ...prev,
      templateId,
      slotConfigs: configs,
    }));
  };

  const handleTemplateChange = (templateId: GridTemplateId) => {
    initializeSlots(templateId);
  };

  const handleBlockChange = (slotId: string, blockType: BlockType) => {
    setState((prev) => ({
      ...prev,
      slotConfigs: prev.slotConfigs.map((config) =>
        config.slotId === slotId ? { ...config, blockType } : config
      ),
    }));
  };

  const getSlotBlock = (slotId: string): BlockType => {
    const config = state.slotConfigs.find((c) => c.slotId === slotId);
    return config?.blockType || 'empty';
  };

  const renderSlot = (slotId: string) => {
    const blockType = getSlotBlock(slotId);
    const blockDef = getBlockDefinition(blockType);

    if (!blockDef) return null;

    const Component = blockDef.component;
    const props = blockDef.defaultProps || {};

    return (
      <div
        key={slotId}
        onClick={() => setState((prev) => ({ ...prev, selectedSlot: slotId }))}
        className={`p-4 rounded-lg border-2 transition cursor-pointer ${
          state.selectedSlot === slotId
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
            : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
        }`}
      >
        <Component {...props} />
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="space-y-4">
        {/* Template Selector */}
        <div>
          <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
            Grid Layout
          </h3>
          <div className="grid grid-cols-3 gap-2">
            {Object.values(GRID_TEMPLATES).map((t) => (
              <button
                key={t.id}
                onClick={() => handleTemplateChange(t.id)}
                className={`p-3 rounded text-sm font-medium transition ${
                  state.templateId === t.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-300'
                }`}
              >
                {t.name}
              </button>
            ))}
          </div>
        </div>

        {/* Block Picker */}
        {state.selectedSlot && (
          <Card>
            <div>
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                Select Block for {state.selectedSlot}
              </h3>
              <div className="grid grid-cols-2 gap-2">
                {Object.values(BLOCK_REGISTRY).map((block) => (
                  <button
                    key={block.id}
                    onClick={() => {
                      handleBlockChange(
                        state.selectedSlot!,
                        block.id as BlockType
                      );
                    }}
                    className={`p-3 text-left rounded text-sm transition border ${
                      getSlotBlock(state.selectedSlot) === block.id
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <div className="font-medium text-gray-900 dark:text-white">
                      {block.name}
                    </div>
                    <div className="text-xs text-gray-500">{block.description}</div>
                  </button>
                ))}
              </div>
            </div>
          </Card>
        )}
      </div>

      {/* Preview */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Preview
          </h3>
          <Badge color="gray">
            {template.name} • {template.slots.length} slots
          </Badge>
        </div>
        <div className={`grid ${template.cssClass} gap-4`}>
          {template.slots.map((slot) => renderSlot(slot.id))}
        </div>
      </div>

      {/* Config Display */}
      <Card>
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
          Layout Config (JSON)
        </h3>
        <pre className="bg-gray-900 dark:bg-gray-950 text-green-400 p-4 rounded text-xs overflow-auto">
          {JSON.stringify(
            {
              template: state.templateId,
              slots: state.slotConfigs,
            },
            null,
            2
          )}
        </pre>
      </Card>
    </div>
  );
};

export default LayoutComposer;
