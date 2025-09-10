import React from 'react';
import JsonCard from './components/JsonCard';
import data from './TradingPerformanceDashboard.json';

export default function TradingPerformanceDashboard() {
  return <JsonCard data={data as any} />;
}

