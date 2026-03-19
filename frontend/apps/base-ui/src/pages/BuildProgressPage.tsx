/**
 * Build Progress Page - Real-time monitoring of agent-based finBlock and View building
 * Displays progress from .claude/agents/progress.json
 */

import React, { useState, useEffect } from 'react';

interface ProgressData {
  lastUpdated: string;
  overallStatus: string;
  phases: {
    [key: string]: {
      name: string;
      status: string;
      total: number;
      completed: number;
      errors: number;
      categories?: {
        [key: string]: {
          total: number;
          completed: number;
          status: string;
        };
      };
    };
  };
  currentPhase: string;
  agentStatuses: {
    [key: string]: {
      status: string;
      lastCheckin: string | null;
      workingOn: string | null;
    };
  };
  timeline: {
    [key: string]: string;
  };
  notes: string[];
}

const statusColors: { [key: string]: string } = {
  pending: 'bg-gray-100 text-gray-700',
  running: 'bg-blue-100 text-blue-700',
  completed: 'bg-green-100 text-green-700',
  error: 'bg-red-100 text-red-700',
  ready: 'bg-blue-100 text-blue-700',
  waiting: 'bg-yellow-100 text-yellow-700',
  ready_parallel: 'bg-blue-100 text-blue-700',
};

const statusBorderColors: { [key: string]: string } = {
  pending: 'border-gray-300',
  running: 'border-blue-400',
  completed: 'border-green-400',
  error: 'border-red-400',
};

export const BuildProgressPage: React.FC = () => {
  const [progress, setProgress] = useState<ProgressData | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);

  useEffect(() => {
    const fetchProgress = async () => {
      try {
        // In real implementation, this would fetch from the progress.json file
        // For now, simulate with local state
        const response = await fetch('/.claude/agents/progress.json');
        if (response.ok) {
          const data = await response.json();
          setProgress(data);
          setLastRefresh(new Date());
        }
      } catch (error) {
        console.log('Progress file not yet available, using placeholder');
      } finally {
        setLoading(false);
      }
    };

    fetchProgress();
    const interval = setInterval(fetchProgress, 5000); // Refresh every 5 seconds

    return () => clearInterval(interval);
  }, []);

  if (loading && !progress) {
    return (
      <div className="p-8 text-center">
        <p className="text-gray-600">Loading build progress...</p>
      </div>
    );
  }

  if (!progress) {
    return <PlaceholderProgress />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Multi-Agent Build Progress
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Real-time monitoring of finBlock and View component generation
          </p>
          {lastRefresh && (
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
              Last updated: {lastRefresh.toLocaleTimeString()}
            </p>
          )}
        </div>

        {/* Overall Status */}
        <div className="mb-8 bg-white dark:bg-slate-800 rounded-lg shadow-md p-6 border-l-4 border-blue-500">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Overall Status</h2>
            <span
              className={`px-4 py-2 rounded-full font-semibold text-sm ${
                statusColors[progress.overallStatus] || 'bg-gray-100 text-gray-700'
              }`}
            >
              {progress.overallStatus.toUpperCase()}
            </span>
          </div>
          <p className="text-gray-600 dark:text-gray-300">
            Current Phase: <span className="font-semibold">{progress.currentPhase}</span>
          </p>
        </div>

        {/* Phase Timeline */}
        <div className="mb-8 bg-white dark:bg-slate-800 rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Timeline</h3>
          <div className="space-y-2">
            {Object.entries(progress.timeline).map(([key, value]) => (
              <div key={key} className="flex justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-400">{value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Phases Progress */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {Object.entries(progress.phases).map(([phaseKey, phase]) => (
            <PhaseCard key={phaseKey} phase={phase} phaseKey={phaseKey} />
          ))}
        </div>

        {/* Agent Statuses */}
        <div className="mb-8 bg-white dark:bg-slate-800 rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6">Agent Status</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(progress.agentStatuses).map(([agentKey, agent]) => (
              <AgentStatusCard key={agentKey} agentName={agentKey} agent={agent} />
            ))}
          </div>
        </div>

        {/* Notes */}
        {progress.notes.length > 0 && (
          <div className="bg-white dark:bg-slate-800 rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Notes</h3>
            <ul className="space-y-2">
              {progress.notes.map((note, idx) => (
                <li key={idx} className="flex items-start text-gray-600 dark:text-gray-300">
                  <span className="mr-3 text-blue-500">•</span>
                  {note}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

interface PhaseCardProps {
  phase: any;
  phaseKey: string;
}

const PhaseCard: React.FC<PhaseCardProps> = ({ phase, phaseKey }) => {
  const progress = phase.total > 0 ? (phase.completed / phase.total) * 100 : 0;
  const isActive = phase.status === 'running';

  return (
    <div
      className={`bg-white dark:bg-slate-800 rounded-lg shadow-md p-6 border-l-4 ${
        statusBorderColors[phase.status] || 'border-gray-300'
      }`}
    >
      <h4 className="text-lg font-bold text-gray-900 dark:text-white mb-2">{phase.name}</h4>

      <div className="mb-4">
        <span
          className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${
            statusColors[phase.status] || 'bg-gray-100 text-gray-700'
          }`}
        >
          {phase.status.toUpperCase()}
        </span>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex justify-between text-sm mb-2">
          <span className="text-gray-600 dark:text-gray-400">
            {phase.completed} / {phase.total}
          </span>
          <span className="font-semibold text-gray-900 dark:text-white">{progress.toFixed(0)}%</span>
        </div>
        <div className="w-full bg-gray-200 dark:bg-slate-700 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-300 ${
              isActive ? 'bg-blue-500' : 'bg-green-500'
            }`}
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Categories */}
      {phase.categories && (
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-slate-700">
          <h5 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
            Categories
          </h5>
          <div className="space-y-2">
            {Object.entries(phase.categories).map(([catKey, cat]: [string, any]) => {
              const catProgress = cat.total > 0 ? (cat.completed / cat.total) * 100 : 0;
              return (
                <div key={catKey}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-gray-600 dark:text-gray-400">{catKey}</span>
                    <span className="text-gray-500 dark:text-gray-500">
                      {cat.completed}/{cat.total}
                    </span>
                  </div>
                  <div className="w-full bg-gray-100 dark:bg-slate-700 rounded-full h-1">
                    <div
                      className="h-1 rounded-full bg-blue-400 transition-all duration-300"
                      style={{ width: `${catProgress}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Error Count */}
      {phase.errors > 0 && (
        <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 rounded border border-red-200 dark:border-red-800">
          <p className="text-sm text-red-700 dark:text-red-300">
            ⚠️ {phase.errors} error{phase.errors !== 1 ? 's' : ''}
          </p>
        </div>
      )}
    </div>
  );
};

interface AgentStatusCardProps {
  agentName: string;
  agent: any;
}

const AgentStatusCard: React.FC<AgentStatusCardProps> = ({ agentName, agent }) => {
  return (
    <div
      className={`bg-white dark:bg-slate-700 rounded-lg p-4 border border-gray-200 dark:border-slate-600 ${
        agent.status === 'running' ? 'ring-2 ring-blue-500' : ''
      }`}
    >
      <div className="flex items-center justify-between mb-2">
        <h5 className="font-semibold text-gray-900 dark:text-white text-sm">{agentName}</h5>
        <span
          className={`px-2 py-1 rounded text-xs font-semibold ${
            statusColors[agent.status] || 'bg-gray-100 text-gray-700'
          }`}
        >
          {agent.status}
        </span>
      </div>
      {agent.workingOn && (
        <p className="text-xs text-gray-600 dark:text-gray-300 mb-1">
          Working on: <span className="font-mono">{agent.workingOn}</span>
        </p>
      )}
      {agent.lastCheckin && (
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Last checkin: {new Date(agent.lastCheckin).toLocaleTimeString()}
        </p>
      )}
    </div>
  );
};

// Placeholder when progress.json not available
const PlaceholderProgress: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Multi-Agent Build Progress
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Build system is initializing...
          </p>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-lg shadow-md p-8 text-center">
          <div className="inline-block mb-6">
            <div className="w-16 h-16 rounded-full border-4 border-gray-200 border-t-blue-500 animate-spin"></div>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
            Initializing Agents
          </h2>
          <p className="text-gray-600 dark:text-gray-300 mb-6">
            Setting up finblock-builder, view-builder, classifier-builder, and orchestrator-builder agents...
          </p>

          <div className="bg-blue-50 dark:bg-blue-900/20 rounded p-4 text-sm text-blue-800 dark:text-blue-200 mb-6">
            <p className="font-semibold mb-2">What&apos;s happening:</p>
            <ul className="text-left space-y-1">
              <li>✓ Agent definitions created</li>
              <li>✓ Progress tracking system initialized</li>
              <li>→ Awaiting agent startup...</li>
              <li>→ finblock-builder will start building 110 finBlock components</li>
              <li>→ classifier-builder will build intent classification system</li>
            </ul>
          </div>

          <p className="text-xs text-gray-500 dark:text-gray-400">
            Page auto-refreshes every 5 seconds
          </p>
        </div>

        <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatsCard label="finBlock Components" value="110" subtext="Pending" />
          <StatsCard label="View Pages" value="105" subtext="Waiting" />
          <StatsCard label="Intent Classifiers" value="1" subtext="Ready to build" />
          <StatsCard label="Data Orchestrators" value="1" subtext="Waiting" />
        </div>
      </div>
    </div>
  );
};

interface StatsCardProps {
  label: string;
  value: string;
  subtext: string;
}

const StatsCard: React.FC<StatsCardProps> = ({ label, value, subtext }) => {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow p-4 text-center">
      <p className="text-gray-600 dark:text-gray-400 text-sm mb-2">{label}</p>
      <p className="text-3xl font-bold text-gray-900 dark:text-white">{value}</p>
      <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">{subtext}</p>
    </div>
  );
};

export default BuildProgressPage;
