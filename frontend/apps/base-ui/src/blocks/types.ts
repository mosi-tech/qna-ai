// ─── Canonical shared types for DashboardSpec / BlockSpec ────────────────────
// These types are the single source of truth used by all apps (ai-builder,
// qna-ai) and the backend UIPlanner service. Moved here from ai-builder in
// Phase 1 so that @ui-gen/base-ui can export them to consumers.

export type BlockCategory =
    | 'kpi-cards'
    | 'line-charts'
    | 'bar-charts'
    | 'bar-lists'
    | 'donut-charts'
    | 'spark-charts'
    | 'tables'
    | 'status-monitoring'
    | 'treemaps'
    | 'heatmaps';

export type DataContractType =
    | 'kpi'
    | 'timeseries'
    | 'categorical'
    | 'ranked-list'
    | 'table-rows'
    | 'spark'
    | 'tracker';

export interface DataContract {
    type: DataContractType;
    description: string;
    points?: number;
    categories?: string[];
}

export interface BlockSpec {
    blockId: string;          // matches BLOCK_CATALOG.json id
    category: BlockCategory;
    title: string;
    dataContract: DataContract;
    // Sub-question extensions (populated when coming from UIPlanner)
    sub_question?: string;
    canonical_params?: Record<string, string>;
    cache_key?: string;
}

export type RowWidth = 'full' | '3/4' | '2/3' | '1/2' | '1/3' | '1/4';
export type RowRole = 'headline' | 'primary' | 'supporting' | 'detail';

export interface DashboardRowColumn {
    width: RowWidth;
    blockId: string;
}

export interface DashboardRow {
    role: RowRole;
    columns: DashboardRowColumn[];
}

export interface DashboardSpec {
    dashboard_id?: string;    // set after backend persists
    title: string;
    subtitle: string;
    layout: 'wide' | 'grid';
    blocks: BlockSpec[];
    // Row-based layout from updated UI Planner (rows with explicit widths)
    rows?: DashboardRow[];
    // Grid layout with slot assignments (from orchestrator, legacy)
    gridTemplate?: string;    // e.g., 'two-col', 'three-col', 'quad-balance'
    gridSlots?: Record<string, string>;  // slot-id => block-id mapping
}

// 'idle' is kept for ai-builder backward compatibility.
// 'cached' is added for Phase 8 (cache-hit fast paint).
export type BlockLoadState = 'idle' | 'loading' | 'loaded' | 'error' | 'cached';

export interface BlockState {
    spec: BlockSpec;
    loadState: BlockLoadState;
    data?: Record<string, unknown>;
    error?: string;
}
