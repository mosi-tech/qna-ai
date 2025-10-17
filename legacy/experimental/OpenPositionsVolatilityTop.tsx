import React from 'react';
import JsonCard from './components/JsonCard';
import data from './OpenPositionsVolatilityTop.json';

export default function OpenPositionsVolatilityTop() {
  return <JsonCard data={data as any} />;
}

