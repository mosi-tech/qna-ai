/**
 * Dashboard Viewer Page
 * Renders any View from VIEWS_CATALOG by ID
 * Composes multiple finBlocks into complete dashboard layouts
 */

import React, { useState, useEffect } from 'react';

interface ViewDefinition {
  id: string;
  name: string;
  description: string;
  finBlocks: string[];
  layout: {
    type: string;
    sections: Array<{
      name?: string;
      rows?: number;
      cols?: number;
      blocks: string[];
    }>;
  };
  mcpRequired: string[];
  estimatedTime: string;
}

interface FinBlockDefinition {
  id: string;
  name: string;
  description: string;
  blockType: string;
  blockCatalogRef: string;
  dataContract: any;
  mcpRequired: string[];
  estimatedDataFetch: string;
}

export const DashboardViewerPage: React.FC<{ viewId?: string }> = ({ viewId = 'portfolio-daily-check' }) => {
  const [view, setView] = useState<ViewDefinition | null>(null);
  const [finBlocks, setFinBlocks] = useState<{ [key: string]: FinBlockDefinition }>({});
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadViewAndBlocks();
  }, [viewId]);

  const loadViewAndBlocks = async () => {
    try {
      setLoading(true);
      setError(null);

      // TODO: Load from VIEWS_CATALOG.json and FINBLOCK_CATALOG.json
      // For now, show placeholder
      const placeholderView: ViewDefinition = {
        id: viewId,
        name: 'Dashboard View',
        description: 'Loading view definition...',
        finBlocks: [],
        layout: { type: 'grid', sections: [] },
        mcpRequired: [],
        estimatedTime: '4 seconds',
      };

      setView(placeholderView);
    } catch (err) {
      setError(`Failed to load view: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingState />;
  }

  if (error) {
    return <ErrorState error={error} />;
  }

  if (!view) {
    return <ErrorState error="View not found" />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            {view.name}
          </h1>
          <p className="text-gray-600 dark:text-gray-300 mb-4">
            {view.description}
          </p>

          {/* Metadata */}
          <div className="flex flex-wrap gap-4 text-sm">
            <div className="bg-white dark:bg-slate-800 rounded px-3 py-1 text-gray-700 dark:text-gray-300">
              ⏱️ {view.estimatedTime}
            </div>
            <div className="bg-white dark:bg-slate-800 rounded px-3 py-1 text-gray-700 dark:text-gray-300">
              📦 {view.finBlocks.length} finBlocks
            </div>
            <div className="bg-white dark:bg-slate-800 rounded px-3 py-1 text-gray-700 dark:text-gray-300">
              🔗 {view.mcpRequired.length} MCP calls
            </div>
          </div>
        </div>

        {/* Layout Sections */}
        <div className="space-y-6">
          {view.layout.sections.map((section, idx) => (
            <div key={idx}>
              {section.name && (
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                  {section.name}
                </h2>
              )}

              <div
                className={`grid gap-6 ${
                  section.cols === 1
                    ? 'grid-cols-1'
                    : section.cols === 2
                      ? 'grid-cols-1 lg:grid-cols-2'
                      : 'grid-cols-1 lg:grid-cols-3'
                }`}
              >
                {section.blocks.map((blockId) => (
                  <FinBlockPlaceholder key={blockId} blockId={blockId} />
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Debug Info */}
        <div className="mt-12 bg-white dark:bg-slate-800 rounded-lg shadow p-6">
          <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
            DEBUG: View Configuration
          </h3>
          <pre className="bg-gray-50 dark:bg-slate-900 rounded p-3 text-xs overflow-auto text-gray-800 dark:text-gray-200">
            {JSON.stringify(
              {
                viewId: view.id,
                finBlockCount: view.finBlocks.length,
                mcpCallsRequired: view.mcpRequired,
                layoutType: view.layout.type,
              },
              null,
              2
            )}
          </pre>
        </div>
      </div>
    </div>
  );
};

/**
 * Placeholder for finBlock rendering
 * Once finBlocks are generated, this will import and render the actual component
 */
const FinBlockPlaceholder: React.FC<{ blockId: string }> = ({ blockId }) => {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow p-6 border-2 border-dashed border-gray-300 dark:border-slate-700">
      <div className="text-center">
        <div className="w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center mx-auto mb-3">
          <span className="text-xl">📦</span>
        </div>
        <p className="font-semibold text-gray-900 dark:text-white mb-1">{blockId}</p>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Waiting for finblock-builder to generate component
        </p>
      </div>
    </div>
  );
};

const LoadingState: React.FC = () => (
  <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center p-4">
    <div className="text-center">
      <div className="w-16 h-16 rounded-full border-4 border-gray-200 border-t-blue-500 animate-spin mx-auto mb-4"></div>
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
        Loading Dashboard View
      </h2>
      <p className="text-gray-600 dark:text-gray-300">
        Fetching view definition and finBlock components...
      </p>
    </div>
  </div>
);

const ErrorState: React.FC<{ error: string }> = ({ error }) => (
  <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center p-4">
    <div className="text-center max-w-md">
      <div className="w-16 h-16 rounded-full bg-red-100 dark:bg-red-900 flex items-center justify-center mx-auto mb-4">
        <span className="text-2xl">⚠️</span>
      </div>
      <h2 className="text-2xl font-bold text-red-600 dark:text-red-400 mb-2">Error Loading View</h2>
      <p className="text-gray-600 dark:text-gray-300 mb-6">{error}</p>
      <button
        onClick={() => window.location.reload()}
        className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded font-medium transition"
      >
        Try Again
      </button>
    </div>
  </div>
);

export default DashboardViewerPage;
