import React from 'react';
import JsonCard from './components/JsonCard';
import data from './TotalUnrealizedPnL.json';

export default function TotalUnrealizedPnL() {
  return <JsonCard data={data as any} />;
}

