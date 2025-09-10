import React from 'react';
import JsonCard from './components/JsonCard';
import data from './PositionCorrelation.json';

export default function PositionCorrelation() {
  return <JsonCard data={data as any} />;
}

