import React, { useState } from 'react'
import ReactDOM from 'react-dom/client'
import './global.css'
import { WidthCompatibilityTester } from './dashboardComposer/WidthCompatibilityTester'
import { LayoutComposerV2 } from './dashboardComposer/LayoutComposerV2'

type Page = 'home' | 'tester' | 'composer';

function App() {
  const [page, setPage] = useState<Page>('home');

  if (page === 'tester') {
    return <WidthCompatibilityTester onBack={() => setPage('home')} />;
  }

  if (page === 'composer') {
    return <LayoutComposerV2 onBack={() => setPage('home')} />;
  }

  return (
    <div className="h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full space-y-6">
        <div className="text-center space-y-3 mb-12">
          <h1 className="text-5xl font-black text-white">Dashboard Tools</h1>
          <p className="text-lg text-slate-400">Test components and design dashboards</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Width Tester */}
          <button
            onClick={() => setPage('tester')}
            className="group relative overflow-hidden rounded-2xl bg-white dark:bg-gray-800 p-8 shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105 text-left border border-gray-200 dark:border-gray-700"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-cyan-500/10 opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="relative z-10">
              <div className="text-4xl mb-3">📏</div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Width Compatibility Tester
              </h2>
              <p className="text-gray-600 dark:text-gray-400 text-sm mb-4">
                Test components at different widths (full, 1/2, 1/3, 2/3, 1/4, 3/4) and approve them for production use.
              </p>
              <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400 font-semibold">
                Open Tester <span className="text-xl">→</span>
              </div>
            </div>
          </button>

          {/* Layout Composer */}
          <button
            onClick={() => setPage('composer')}
            className="group relative overflow-hidden rounded-2xl bg-white dark:bg-gray-800 p-8 shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105 text-left border border-gray-200 dark:border-gray-700"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/10 to-green-500/10 opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="relative z-10">
              <div className="text-4xl mb-3">🎨</div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Dashboard Composer
              </h2>
              <p className="text-gray-600 dark:text-gray-400 text-sm mb-4">
                Design responsive dashboards using approved components. See which blocks work at which widths.
              </p>
              <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-semibold">
                Open Composer <span className="text-xl">→</span>
              </div>
            </div>
          </button>
        </div>

        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 text-center text-sm text-slate-400">
          <p>✓ API Server running on port 3001 | Data syncs between localStorage and backend file</p>
        </div>
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
