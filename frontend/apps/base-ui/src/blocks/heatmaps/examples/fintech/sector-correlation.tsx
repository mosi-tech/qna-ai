'use client';

import React from 'react';
import { Heatmap01 } from '../../heatmap-01';

// 7 S&P 500 GICS sectors — 90-day rolling pairwise return correlations
const labels = ['Tech', 'Fin', 'Health', 'Energy', 'Cons D', 'Util', 'RE'];

// Full symmetric matrix (not lower-triangle) to show grid layout
const matrix: number[][] = [
    //  Tech   Fin   Health  Energy  ConsD   Util    RE
    [1.00, 0.72, 0.41, 0.28, 0.78, -0.19, -0.08], // Tech
    [0.72, 1.00, 0.38, 0.44, 0.63, -0.11, 0.14], // Fin
    [0.41, 0.38, 1.00, 0.12, 0.35, 0.09, 0.07], // Health
    [0.28, 0.44, 0.12, 1.00, 0.31, 0.17, 0.22], // Energy
    [0.78, 0.63, 0.35, 0.31, 1.00, -0.07, 0.04], // Cons D
    [-0.19, -0.11, 0.09, 0.17, -0.07, 1.00, 0.58], // Util
    [-0.08, 0.14, 0.07, 0.22, 0.04, 0.58, 1.00], // RE
];

export function SectorCorrelationExample() {
    return (
        <Heatmap01
            labels={labels}
            matrix={matrix}
            title="S&P 500 Sector Correlations"
            description="90-day rolling return correlations · GICS sectors · Feb 28, 2026"
            showValues
            decimals={2}
            triangle="full"
        />
    );
}
