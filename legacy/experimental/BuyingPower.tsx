import React from 'react';
import JsonCard from './components/JsonCard';
import data from './BuyingPower.json';

export default function BuyingPower() {
  return <JsonCard data={data as any} />;
}

