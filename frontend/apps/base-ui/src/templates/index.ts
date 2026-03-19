/**
 * Template Library - Export all pre-built templates
 */

export { TEMPLATE_REGISTRY, getTemplateByIntent, findTemplateByKeywords } from './templateRegistry';
export type { TemplateDefinition, TemplateBlock } from './templateRegistry';

export { PortfolioOverviewTemplate } from './PortfolioOverviewTemplate';
export type { PortfolioOverviewData } from './PortfolioOverviewTemplate';

export { SectorAnalysisTemplate } from './SectorAnalysisTemplate';
export type { SectorAnalysisData } from './SectorAnalysisTemplate';

export { StockResearchTemplate } from './StockResearchTemplate';
export type { StockResearchData } from './StockResearchTemplate';

export { RiskDashboardTemplate } from './RiskDashboardTemplate';
export type { RiskDashboardData } from './RiskDashboardTemplate';
