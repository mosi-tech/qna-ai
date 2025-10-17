import React from 'react';
import JsonCard from './components/JsonCard';
import data from './WatchlistRiskAdjustedReturns.json';

export default function WatchlistRiskAdjustedReturns() {
  return <JsonCard data={data as any} />;
}

