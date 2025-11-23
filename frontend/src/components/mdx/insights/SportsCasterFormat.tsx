'use client';

import React from 'react';

interface SportsCasterData {
  gameRecap: {
    title: string;
    finalScore: string;
    winner: string;
    summary: string;
  };
  mvpPlayers: Array<{
    player: string;
    stats: Record<string, any>;
    highlights: string[];
    performance: string;
  }>;
  keyPlays: Array<{
    moment: string;
    impact: string;
    description: string;
  }>;
  standings: Array<{
    rank: number;
    team: string;
    record: string;
    streak: string;
  }>;
  preview: {
    nextEvent: string;
    keyFactors: string[];
    predictions: string;
  };
}

interface SportsCasterFormatProps {
  data: SportsCasterData;
  title?: string;
}

export function SportsCasterFormat({
  data,
  title = "Performance Analysis"
}: SportsCasterFormatProps) {
  const { gameRecap, mvpPlayers, keyPlays, standings, preview } = data;

  const getPerformanceColor = (performance: string) => {
    const perf = performance.toLowerCase();
    if (perf.includes('outstanding') || perf.includes('excellent')) return 'text-green-800';
    if (perf.includes('good') || perf.includes('solid')) return 'text-blue-800';
    if (perf.includes('average')) return 'text-yellow-800';
    if (perf.includes('poor') || perf.includes('weak')) return 'text-red-800';
    return 'text-gray-800';
  };

  const getStreakColor = (streak: string) => {
    if (streak.toLowerCase().includes('w')) return 'text-green-700 bg-green-50';
    if (streak.toLowerCase().includes('l')) return 'text-red-700 bg-red-50';
    return 'text-gray-700 bg-gray-50';
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <p className="text-sm text-gray-500 mt-1">Momentum and performance assessment</p>
      </div>

      <div className="p-6 space-y-6">
        {/* Period Summary */}
        <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h4 className="text-sm font-semibold text-blue-800 mb-2">Period Summary</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <div className="text-lg font-bold text-blue-900">{gameRecap.title}</div>
              <div className="text-sm text-blue-700 mt-1">{gameRecap.summary}</div>
            </div>
            <div>
              <div className="text-sm text-blue-600">Final Result</div>
              <div className="font-semibold text-blue-900">{gameRecap.finalScore}</div>
              <div className="text-sm text-blue-700">Winner: {gameRecap.winner}</div>
            </div>
          </div>
        </div>

        {/* Top Performers */}
        <div>
          <h4 className="text-sm font-semibold text-gray-800 mb-3">Top Performers</h4>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {mvpPlayers.map((player, index) => (
              <div key={index} className="p-4 bg-green-50 rounded-lg border border-green-200">
                <div className="flex justify-between items-center mb-3">
                  <h5 className="font-semibold text-green-800">{player.player}</h5>
                  <span className={`text-sm font-medium ${getPerformanceColor(player.performance)}`}>
                    {player.performance}
                  </span>
                </div>

                <div className="grid grid-cols-3 gap-3 mb-3">
                  {Object.entries(player.stats).map(([stat, value]) => (
                    <div key={stat} className="text-center p-2 bg-white rounded border">
                      <div className="text-sm font-bold text-green-900">
                        {typeof value === 'number' ? value.toFixed(2) : value}
                      </div>
                      <div className="text-xs text-green-600">{stat}</div>
                    </div>
                  ))}
                </div>

                <div>
                  <h6 className="text-xs font-semibold text-green-800 mb-1 uppercase">Key Highlights</h6>
                  <ul className="space-y-1">
                    {player.highlights.map((highlight, idx) => (
                      <li key={idx} className="flex items-start space-x-2">
                        <div className="w-1.5 h-1.5 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                        <span className="text-sm text-green-700">{highlight}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Key Events */}
        <div>
          <h4 className="text-sm font-semibold text-gray-800 mb-3">Significant Events</h4>
          <div className="space-y-3">
            {keyPlays.map((play, index) => (
              <div key={index} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex justify-between items-start mb-2">
                  <h5 className="font-medium text-gray-900">{play.moment}</h5>
                  <span className="text-xs text-gray-600 bg-gray-200 px-2 py-1 rounded">
                    {play.impact}
                  </span>
                </div>
                <p className="text-sm text-gray-700">{play.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Performance Rankings */}
        <div>
          <h4 className="text-sm font-semibold text-gray-800 mb-3">Current Rankings</h4>
          <div className="overflow-hidden rounded-lg border border-gray-200">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rank</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Record</th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Current Streak</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {standings.map((standing) => (
                  <tr key={standing.rank} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">#{standing.rank}</td>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{standing.team}</td>
                    <td className="px-4 py-3 text-center text-sm text-gray-700">{standing.record}</td>
                    <td className="px-4 py-3 text-center">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getStreakColor(standing.streak)}`}>
                        {standing.streak}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Outlook */}
        <div className="p-4 bg-orange-50 rounded-lg border border-orange-200">
          <h4 className="text-sm font-semibold text-orange-800 mb-2">Forward Outlook</h4>
          <div className="mb-3">
            <h5 className="text-sm font-medium text-orange-800">{preview.nextEvent}</h5>
            <p className="text-sm text-orange-700 italic mt-1">{preview.predictions}</p>
          </div>
          
          <div>
            <h6 className="text-xs font-semibold text-orange-800 mb-2 uppercase">Key Factors to Monitor</h6>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {preview.keyFactors.map((factor, index) => (
                <div key={index} className="text-sm text-orange-700 p-2 bg-white rounded border">
                  {factor}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}