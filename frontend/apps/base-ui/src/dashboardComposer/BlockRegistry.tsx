import { BlockDefinition } from './types';
import { AccountInfoComponent, MOCK_ACCOUNT_INFO } from '../finBlocks/components/account';
import { OpenPositionsTable, MOCK_POSITIONS } from '../finBlocks/components/positions';

// Placeholder components
const EmptyBlock = () => (
  <div className="p-8 bg-gray-100 dark:bg-gray-800 rounded border-2 border-dashed border-gray-300 dark:border-gray-600 flex items-center justify-center min-h-[300px]">
    <p className="text-gray-500 dark:text-gray-400">Empty slot - Select a block</p>
  </div>
);

const MetricCardBlock = () => (
  <div className="p-6 bg-gradient-to-br from-blue-50 to-transparent dark:from-blue-900/20 rounded-lg border border-blue-100 dark:border-blue-800">
    <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">Metric Card</div>
    <div className="text-3xl font-bold text-gray-900 dark:text-white">$125,000</div>
    <div className="text-xs text-gray-500 mt-2">Sample metric display</div>
  </div>
);

const ChartPlaceholder = () => (
  <div className="p-8 bg-gray-50 dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-800 min-h-[300px] flex items-center justify-center">
    <div className="text-center">
      <div className="text-4xl mb-2">📊</div>
      <p className="text-gray-500 dark:text-gray-400">Chart Placeholder</p>
    </div>
  </div>
);

const TablePlaceholder = () => (
  <div className="p-8 bg-gray-50 dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-800 min-h-[300px] flex items-center justify-center">
    <div className="text-center">
      <div className="text-4xl mb-2">📋</div>
      <p className="text-gray-500 dark:text-gray-400">Table Placeholder</p>
    </div>
  </div>
);

export const BLOCK_REGISTRY: Record<string, BlockDefinition> = {
  'account-info': {
    id: 'account-info',
    name: 'Account Overview',
    description: 'Account equity, buying power, cash balance',
    component: AccountInfoComponent,
    defaultProps: { data: MOCK_ACCOUNT_INFO },
  },
  'open-positions': {
    id: 'open-positions',
    name: 'Open Positions',
    description: 'Sortable positions table with P&L',
    component: OpenPositionsTable,
    defaultProps: { data: MOCK_POSITIONS },
  },
  'empty': {
    id: 'empty',
    name: 'Empty Slot',
    description: 'Empty placeholder',
    component: EmptyBlock,
  },
  'metric-card': {
    id: 'metric-card',
    name: 'Metric Card',
    description: 'Single metric display',
    component: MetricCardBlock,
  },
  'chart-placeholder': {
    id: 'chart-placeholder',
    name: 'Chart Block',
    description: 'Placeholder for charts',
    component: ChartPlaceholder,
  },
  'table-placeholder': {
    id: 'table-placeholder',
    name: 'Table Block',
    description: 'Placeholder for tables',
    component: TablePlaceholder,
  },
};

export const getBlockDefinition = (blockType: string): BlockDefinition | undefined => {
  return BLOCK_REGISTRY[blockType];
};

export const getAvailableBlocks = () => {
  return Object.values(BLOCK_REGISTRY);
};
