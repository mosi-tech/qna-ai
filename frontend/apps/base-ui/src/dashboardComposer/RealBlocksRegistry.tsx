// Import all real blocks from the blocks directory
// KPI Cards (29 total)
import * as KpiCardExamples from '../blocks/kpi-cards/examples';
import { KpiCard05 } from '../blocks/kpi-cards/kpi-card-05';
import { KpiCard06 } from '../blocks/kpi-cards/kpi-card-06';
import { KpiCard07 } from '../blocks/kpi-cards/kpi-card-07';
import { KpiCard08 } from '../blocks/kpi-cards/kpi-card-08';
import { KpiCard09 } from '../blocks/kpi-cards/kpi-card-09';
import { KpiCard10 } from '../blocks/kpi-cards/kpi-card-10';
import { KpiCard11 } from '../blocks/kpi-cards/kpi-card-11';
import { KpiCard12 } from '../blocks/kpi-cards/kpi-card-12';
import { KpiCard13 } from '../blocks/kpi-cards/kpi-card-13';
import { KpiCard14 } from '../blocks/kpi-cards/kpi-card-14';
import { KpiCard15 } from '../blocks/kpi-cards/kpi-card-15';
import { KpiCard16 } from '../blocks/kpi-cards/kpi-card-16';
import { KpiCard17 } from '../blocks/kpi-cards/kpi-card-17';
import { KpiCard18 } from '../blocks/kpi-cards/kpi-card-18';
import { KpiCard19 } from '../blocks/kpi-cards/kpi-card-19';
import { KpiCard20 } from '../blocks/kpi-cards/kpi-card-20';
import { KpiCard21 } from '../blocks/kpi-cards/kpi-card-21';
import { KpiCard22 } from '../blocks/kpi-cards/kpi-card-22';
import { KpiCard23 } from '../blocks/kpi-cards/kpi-card-23';
import { KpiCard24 } from '../blocks/kpi-cards/kpi-card-24';
import { KpiCard25 } from '../blocks/kpi-cards/kpi-card-25';
import { KpiCard26 } from '../blocks/kpi-cards/kpi-card-26';
import { KpiCard27 } from '../blocks/kpi-cards/kpi-card-27';
import { KpiCard28 } from '../blocks/kpi-cards/kpi-card-28';
import { KpiCard29 } from '../blocks/kpi-cards/kpi-card-29';

// Bar Charts (10 total)
import * as BarChartExamples from '../blocks/bar-charts/examples';

// Bar Lists (5 total)
import * as BarListExamples from '../blocks/bar-lists/examples';

// Line Charts (8 total)
import * as LineChartExamples from '../blocks/line-charts/examples';

// Donut Charts (7 total)
import * as DonutChartExamples from '../blocks/donut-charts/examples';

// Spark Charts (6 total)
import * as SparkChartExamples from '../blocks/spark-charts/examples';

// Status Monitoring (4 total)
import * as StatusMonitoringExamples from '../blocks/status-monitoring/examples';

// Tables (2 total)
import * as TableExamples from '../blocks/tables/examples';

// Heatmaps (1 total)
import * as HeatmapExamples from '../blocks/heatmaps/examples';

// Treemaps (1 total)
import * as TreemapExamples from '../blocks/treemaps/examples';

import { BlockDefinition } from './types';

// Mock data for blocks
const mockLineChartData = [
  { date: 'Jan 02', price: 585.11 },
  { date: 'Jan 03', price: 582.74 },
  { date: 'Jan 06', price: 587.30 },
  { date: 'Jan 07', price: 590.48 },
  { date: 'Jan 08', price: 588.92 },
  { date: 'Jan 09', price: 584.61 },
  { date: 'Jan 10', price: 579.34 },
  { date: 'Jan 13', price: 583.20 },
  { date: 'Jan 14', price: 587.85 },
  { date: 'Jan 15', price: 592.41 },
];

const mockBarChartData = [
  { name: 'Jan', date: 'Jan', 'Portfolio': 48, 'Benchmark': 40, 'Last Year': 35, 'This Year': 48 },
  { name: 'Feb', date: 'Feb', 'Portfolio': 35, 'Benchmark': 32, 'Last Year': 28, 'This Year': 35 },
  { name: 'Mar', date: 'Mar', 'Portfolio': 25, 'Benchmark': 28, 'Last Year': 32, 'This Year': 25 },
  { name: 'Apr', date: 'Apr', 'Portfolio': 51, 'Benchmark': 45, 'Last Year': 42, 'This Year': 51 },
  { name: 'May', date: 'May', 'Portfolio': 42, 'Benchmark': 38, 'Last Year': 38, 'This Year': 42 },
];

const mockBarListData = [
  { name: 'Apple', value: 2400 },
  { name: 'Microsoft', value: 1398 },
  { name: 'Google', value: 9800 },
  { name: 'Amazon', value: 3908 },
  { name: 'Meta', value: 4800 },
];

const mockDonutData = [
  { name: 'Technology', value: 45 },
  { name: 'Healthcare', value: 25 },
  { name: 'Finance', value: 20 },
  { name: 'Energy', value: 10 },
];

const mockTableData = [
  { id: '1', position: 'AAPL', quantity: 100, price: '$150.25', change: '+2.5%' },
  { id: '2', position: 'MSFT', quantity: 50, price: '$380.10', change: '-1.2%' },
  { id: '3', position: 'GOOGL', quantity: 75, price: '$155.80', change: '+5.3%' },
];

const mockSparkData = [
  { date: '2026-01-01', AAPL: 150, MSFT: 380, GOOGL: 155 },
  { date: '2026-01-02', AAPL: 152, MSFT: 382, GOOGL: 157 },
  { date: '2026-01-03', AAPL: 151, MSFT: 379, GOOGL: 154 },
  { date: '2026-01-04', AAPL: 155, MSFT: 385, GOOGL: 160 },
  { date: '2026-01-05', AAPL: 153, MSFT: 381, GOOGL: 158 },
];

const mockSparkItems = [
  { id: 'AAPL', name: 'Apple', description: 'Tech', value: '$153.00', change: '+2%', changeType: 'positive' as const },
  { id: 'MSFT', name: 'Microsoft', description: 'Tech', value: '$381.00', change: '+0.3%', changeType: 'positive' as const },
  { id: 'GOOGL', name: 'Google', description: 'Tech', value: '$158.00', change: '+1.9%', changeType: 'positive' as const },
];

const mockHeatmapLabels = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'];
const mockHeatmapMatrix = [
  [1.0, 0.85, 0.72, 0.65, 0.58],
  [0.85, 1.0, 0.78, 0.70, 0.62],
  [0.72, 0.78, 1.0, 0.75, 0.68],
  [0.65, 0.70, 0.75, 1.0, 0.72],
  [0.58, 0.62, 0.68, 0.72, 1.0],
];


// Organize blocks by category - ALL 81 BLOCKS
const kpiCards: (BlockDefinition & { category: string })[] = [
  { id: 'kpi-01', name: 'KPI Card 01', description: 'Basic metrics', component: KpiCardExamples.KpiCard01Example, category: 'KPI Cards', defaultProps: {} },
  { id: 'kpi-02', name: 'KPI Card 02', description: 'Active users', component: KpiCardExamples.KpiCard02Example, category: 'KPI Cards', defaultProps: {} },
  { id: 'kpi-03', name: 'KPI Card 03', description: 'Revenue metrics', component: KpiCardExamples.KpiCard03Example, category: 'KPI Cards', defaultProps: {} },
  { id: 'kpi-04', name: 'KPI Card 04', description: 'Growth tracking', component: KpiCardExamples.KpiCard04Example, category: 'KPI Cards', defaultProps: {} },
  { id: 'kpi-05', name: 'KPI Card 05', description: 'Metric display', component: KpiCardExamples.KpiCard05Example, category: 'KPI Cards', defaultProps: {} },
  { id: 'kpi-06', name: 'KPI Card 06', description: 'Metric with trend', component: KpiCardExamples.KpiCard06Example, category: 'KPI Cards', defaultProps: {} },
  { id: 'kpi-07', name: 'KPI Card 07', description: 'Compact metric', component: KpiCardExamples.KpiCard07Example, category: 'KPI Cards', defaultProps: {} },
  { id: 'kpi-08', name: 'KPI Card 08', description: 'Metric variant', component: KpiCardExamples.KpiCard08Example, category: 'KPI Cards', defaultProps: {} },
  { id: 'kpi-09', name: 'KPI Card 09', description: 'Performance metric', component: KpiCardExamples.KpiCard09Example, category: 'KPI Cards', defaultProps: {} },
  { id: 'kpi-10', name: 'KPI Card 10', description: 'Metric variant', component: KpiCardExamples.KpiCard10Example, category: 'KPI Cards', defaultProps: {} },
  { id: 'kpi-11', name: 'KPI Card 11', description: 'Value metric', component: KpiCardExamples.KpiCard11Example, category: 'KPI Cards', defaultProps: {} },
  { id: 'kpi-12', name: 'KPI Card 12', description: 'Metric display', component: KpiCardExamples.KpiCard12Example, category: 'KPI Cards', defaultProps: {} },
  { id: 'kpi-13', name: 'KPI Card 13', description: 'Metric variant', component: KpiCardExamples.KpiCard13Example, category: 'KPI Cards', defaultProps: {} },
  { id: 'kpi-14', name: 'KPI Card 14', description: 'Metric display', component: KpiCardExamples.KpiCard14Example, category: 'KPI Cards', defaultProps: {} },
  { id: 'kpi-15', name: 'KPI Card 15', description: 'Value metric', component: KpiCardExamples.KpiCard15Example, category: 'KPI Cards', defaultProps: {} },
  { id: 'kpi-16', name: 'KPI Card 16', description: 'Metric variant', component: KpiCardExamples.KpiCard16Example, category: 'KPI Cards', defaultProps: {} },
  { id: 'kpi-17', name: 'KPI Card 17', description: 'Metric display', component: KpiCardExamples.KpiCard17Example, category: 'KPI Cards', defaultProps: {} },
  { id: 'kpi-18', name: 'KPI Card 18', description: 'Metric variant', component: KpiCardExamples.KpiCard18Example, category: 'KPI Cards', defaultProps: {} },
  { id: 'kpi-19', name: 'KPI Card 19', description: 'Value metric', component: KpiCardExamples.KpiCard19Example, category: 'KPI Cards', defaultProps: {} },
  { id: 'kpi-20', name: 'KPI Card 20', description: 'Heart rate zones', component: KpiCardExamples.KpiCard20Example, category: 'KPI Cards', defaultProps: {} },
  { id: 'kpi-21', name: 'KPI Card 21', description: 'Metric variant', component: KpiCardExamples.KpiCard21Example, category: 'KPI Cards', defaultProps: {} },
  { id: 'kpi-22', name: 'KPI Card 22', description: 'Value metric', component: KpiCardExamples.KpiCard22Example, category: 'KPI Cards', defaultProps: {} },
  { id: 'kpi-23', name: 'KPI Card 23', description: 'Metric display', component: KpiCardExamples.KpiCard23Example, category: 'KPI Cards', defaultProps: {} },
  { id: 'kpi-24', name: 'KPI Card 24', description: 'Metric variant', component: KpiCardExamples.KpiCard24Example, category: 'KPI Cards', defaultProps: {} },
  { id: 'kpi-25', name: 'KPI Card 25', description: 'Value metric', component: KpiCardExamples.KpiCard25Example, category: 'KPI Cards', defaultProps: {} },
  { id: 'kpi-26', name: 'KPI Card 26', description: 'SLA performance', component: KpiCardExamples.KpiCard26Example, category: 'KPI Cards', defaultProps: {} },
  { id: 'kpi-27', name: 'KPI Card 27', description: 'Metric variant', component: KpiCardExamples.KpiCard27Example, category: 'KPI Cards', defaultProps: {} },
  { id: 'kpi-28', name: 'KPI Card 28', description: 'Value metric', component: KpiCardExamples.KpiCard28Example, category: 'KPI Cards', defaultProps: {} },
  { id: 'kpi-29', name: 'KPI Card 29', description: 'Ratio indicator', component: KpiCardExamples.KpiCard29Example, category: 'KPI Cards', defaultProps: {} },
  { id: 'kpi-four-items', name: 'KPI Card (4 Items)', description: '4-item metric test', component: KpiCardExamples.KpiCard05FourItemsExample, category: 'KPI Cards', defaultProps: {} },
];

const barCharts: (BlockDefinition & { category: string })[] = [
  { id: 'bar-chart-02', name: 'Bar Chart 02', description: 'Vertical bars', component: BarChartExamples.BarChart02Example, category: 'Bar Charts', defaultProps: {} },
  { id: 'bar-chart-03', name: 'Bar Chart 03', description: 'Stacked bars', component: BarChartExamples.BarChart03Example, category: 'Bar Charts', defaultProps: {} },
  { id: 'bar-chart-04', name: 'Bar Chart 04', description: 'Percent bars', component: BarChartExamples.BarChart04Example, category: 'Bar Charts', defaultProps: {} },
  { id: 'bar-chart-05', name: 'Bar Chart 05', description: 'Grouped bars', component: BarChartExamples.BarChart05Example, category: 'Bar Charts', defaultProps: {} },
  { id: 'bar-chart-06', name: 'Bar Chart 06', description: 'Horizontal bars', component: BarChartExamples.BarChart06Example, category: 'Bar Charts', defaultProps: {} },
  { id: 'bar-chart-08', name: 'Bar Chart 08', description: 'Waterfall chart', component: BarChartExamples.BarChart08Example, category: 'Bar Charts', defaultProps: {} },
  { id: 'bar-chart-09', name: 'Bar Chart 09', description: 'Variant bars', component: BarChartExamples.BarChart09Example, category: 'Bar Charts', defaultProps: {} },
  { id: 'bar-chart-10', name: 'Bar Chart 10', description: 'Diverging bars', component: BarChartExamples.BarChart10Example, category: 'Bar Charts', defaultProps: {} },
  { id: 'bar-chart-11', name: 'Bar Chart 11', description: 'Range bars', component: BarChartExamples.BarChart11Example, category: 'Bar Charts', defaultProps: {} },
  { id: 'bar-chart-12', name: 'Bar Chart 12', description: 'Custom bars', component: BarChartExamples.BarChart12Example, category: 'Bar Charts', defaultProps: {} },
];

const lineCharts: (BlockDefinition & { category: string })[] = [
  { id: 'line-chart-02', name: 'Line Chart 02', description: 'Trend over time', component: LineChartExamples.LineChart02Example, category: 'Line Charts', defaultProps: {} },
  { id: 'line-chart-03', name: 'Line Chart 03', description: 'Performance trend', component: LineChartExamples.LineChart03Example, category: 'Line Charts', defaultProps: {} },
  { id: 'line-chart-04', name: 'Line Chart 04', description: 'Multi-line chart', component: LineChartExamples.LineChart04Example, category: 'Line Charts', defaultProps: {} },
  { id: 'line-chart-05', name: 'Line Chart 05', description: 'Smooth curves', component: LineChartExamples.LineChart05Example, category: 'Line Charts', defaultProps: {} },
  { id: 'line-chart-06', name: 'Line Chart 06', description: 'Filled area', component: LineChartExamples.LineChart06Example, category: 'Line Charts', defaultProps: {} },
  { id: 'line-chart-07', name: 'Line Chart 07', description: 'Step chart', component: LineChartExamples.LineChart07Example, category: 'Line Charts', defaultProps: {} },
  { id: 'line-chart-08', name: 'Line Chart 08', description: 'Multiple series', component: LineChartExamples.LineChart08Example, category: 'Line Charts', defaultProps: {} },
  { id: 'line-chart-09', name: 'Line Chart 09', description: 'Advanced chart', component: LineChartExamples.LineChart09Example, category: 'Line Charts', defaultProps: {} },
];

const donutCharts: (BlockDefinition & { category: string })[] = [
  { id: 'donut-01', name: 'Donut Chart 01', description: 'Pie chart', component: DonutChartExamples.DonutChart01Example, category: 'Donut Charts', defaultProps: {} },
  { id: 'donut-02', name: 'Donut Chart 02', description: 'Donut variant', component: DonutChartExamples.DonutChart02Example, category: 'Donut Charts', defaultProps: {} },
  { id: 'donut-03', name: 'Donut Chart 03', description: 'Allocation', component: DonutChartExamples.DonutChart03Example, category: 'Donut Charts', defaultProps: {} },
  { id: 'donut-04', name: 'Donut Chart 04', description: 'Breakdown', component: DonutChartExamples.DonutChart04Example, category: 'Donut Charts', defaultProps: {} },
  { id: 'donut-05', name: 'Donut Chart 05', description: 'Distribution', component: DonutChartExamples.DonutChart05Example, category: 'Donut Charts', defaultProps: {} },
  { id: 'donut-06', name: 'Donut Chart 06', description: 'Composition', component: DonutChartExamples.DonutChart06Example, category: 'Donut Charts', defaultProps: {} },
  { id: 'donut-07', name: 'Donut Chart 07', description: 'Structure', component: DonutChartExamples.DonutChart07Example, category: 'Donut Charts', defaultProps: {} },
];

const sparkCharts: (BlockDefinition & { category: string })[] = [
  { id: 'spark-01', name: 'Spark Chart 01', description: 'Stock tracking', component: SparkChartExamples.SparkChart01Example, category: 'Spark Charts', defaultProps: {} },
  { id: 'spark-02', name: 'Spark Chart 02', description: 'Price sparklines', component: SparkChartExamples.SparkChart02Example, category: 'Spark Charts', defaultProps: {} },
  { id: 'spark-03', name: 'Spark Chart 03', description: 'Performance mini', component: SparkChartExamples.SparkChart03Example, category: 'Spark Charts', defaultProps: {} },
  { id: 'spark-04', name: 'Spark Chart 04', description: 'Trend sparkles', component: SparkChartExamples.SparkChart04Example, category: 'Spark Charts', defaultProps: {} },
  { id: 'spark-05', name: 'Spark Chart 05', description: 'Volatility mini', component: SparkChartExamples.SparkChart05Example, category: 'Spark Charts', defaultProps: {} },
  { id: 'spark-06', name: 'Spark Chart 06', description: 'Advanced spark', component: SparkChartExamples.SparkChart06Example, category: 'Spark Charts', defaultProps: {} },
];

const barLists: (BlockDefinition & { category: string })[] = [
  { id: 'bar-list-03', name: 'Bar List 03', description: 'Horizontal bars', component: BarListExamples.BarList03Example, category: 'Bar Lists', defaultProps: {} },
  { id: 'bar-list-04', name: 'Bar List 04', description: 'Position sizes', component: BarListExamples.BarList04Example, category: 'Bar Lists', defaultProps: {} },
  { id: 'bar-list-05', name: 'Bar List 05', description: 'Ranked list', component: BarListExamples.BarList05Example, category: 'Bar Lists', defaultProps: {} },
  { id: 'bar-list-06', name: 'Bar List 06', description: 'Sorted bars', component: BarListExamples.BarList06Example, category: 'Bar Lists', defaultProps: {} },
  { id: 'bar-list-07', name: 'Bar List 07', description: 'Custom list', component: BarListExamples.BarList07Example, category: 'Bar Lists', defaultProps: {} },
];

const statusMonitoring: (BlockDefinition & { category: string })[] = [
  { id: 'tracker-01', name: 'Status Tracker 01', description: 'Portfolio status', component: StatusMonitoringExamples.Tracker01Example, category: 'Status Monitoring', defaultProps: {} },
  { id: 'tracker-02', name: 'Status Tracker 02', description: 'Risk tracking', component: StatusMonitoringExamples.Tracker02Example, category: 'Status Monitoring', defaultProps: {} },
  { id: 'tracker-03', name: 'Status Tracker 03', description: 'Performance track', component: StatusMonitoringExamples.Tracker03Example, category: 'Status Monitoring', defaultProps: {} },
  { id: 'tracker-04', name: 'Status Tracker 04', description: 'Monitoring status', component: StatusMonitoringExamples.Tracker04Example, category: 'Status Monitoring', defaultProps: {} },
];

const otherBlocks: (BlockDefinition & { category: string })[] = [
  { id: 'table-action-01', name: 'Data Table', description: 'Structured data', component: TableExamples.TableAction01Example, category: 'Tables', defaultProps: {} },
  { id: 'heatmap-01', name: 'Heatmap 01', description: 'Portfolio correlation', component: HeatmapExamples.PortfolioCorrelationExample, category: 'Heatmaps', defaultProps: {} },
  { id: 'heatmap-02', name: 'Heatmap 02', description: 'Sector correlation', component: HeatmapExamples.SectorCorrelationExample, category: 'Heatmaps', defaultProps: {} },
  { id: 'treemap-01', name: 'Treemap 01', description: 'Equity by sector', component: TreemapExamples.EquityBookSectorExample, category: 'Treemaps', defaultProps: {} },
  { id: 'treemap-02', name: 'Treemap 02', description: 'S&P sectors', component: TreemapExamples.SpSectorsExample, category: 'Treemaps', defaultProps: {} },
];

// Combine all blocks (81 total)
export const REAL_BLOCKS: (BlockDefinition & { category: string })[] = [
  ...kpiCards,
  ...barCharts,
  ...lineCharts,
  ...donutCharts,
  ...sparkCharts,
  ...barLists,
  ...statusMonitoring,
  ...otherBlocks,
];

// Export blocks by category
export const BLOCKS_BY_CATEGORY = {
  'KPI Cards': kpiCards,
  'Bar Charts': barCharts,
  'Line Charts': lineCharts,
  'Donut Charts': donutCharts,
  'Spark Charts': sparkCharts,
  'Bar Lists': barLists,
  'Status Monitoring': statusMonitoring,
  'Tables': [otherBlocks[0]],
  'Heatmaps': [otherBlocks[1], otherBlocks[2]],
  'Treemaps': [otherBlocks[3], otherBlocks[4]],
};

export const BLOCK_CATEGORIES = Object.keys(BLOCKS_BY_CATEGORY);

export const BLOCK_REGISTRY_MAP = new Map(
  REAL_BLOCKS.map((block) => [block.id, block])
);
