/**
 * Dashboard Composer - Type definitions
 */

export type GridTemplateId = '1-col' | '2-col' | '3-col' | '2-1' | '1-2' | '3-1-2' | 'custom';

export type ApprovedWidth = 'full' | '1/2' | '1/3' | '2/3' | '1/4' | '3/4';

export interface GridSlot {
  id: string;
  colSpan: number;
  rowSpan: number;
  width?: ApprovedWidth;
}

export interface GridTemplate {
  id: GridTemplateId;
  name: string;
  description: string;
  cols: number;
  slots: GridSlot[];
  cssClass: string;
}

export type BlockType = 
  | 'account-info'
  | 'open-positions'
  | 'empty'
  | 'metric-card'
  | 'chart-placeholder'
  | 'table-placeholder';

export interface BlockDefinition {
  id: BlockType;
  name: string;
  description: string;
  component: React.ComponentType<any>;
  defaultProps?: Record<string, any>;
}

export interface SlotConfig {
  slotId: string;
  blockType: BlockType;
  props?: Record<string, any>;
}

export interface LayoutConfig {
  id: string;
  name: string;
  description: string;
  templateId: GridTemplateId;
  slots: SlotConfig[];
  createdAt: string;
  updatedAt: string;
}

export interface ComposerState {
  templateId: GridTemplateId;
  slotConfigs: SlotConfig[];
  selectedSlot: string | null;
}
