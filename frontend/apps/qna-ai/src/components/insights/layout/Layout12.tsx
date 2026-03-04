/**
 * Layout12: Trading & Signals Analytics Dashboard
 * 
 * Grid Structure: 4x3 with mixed spans (7 sections)
 * 
 * Layout Map:
 * ┌──────────────────────────────────────────────────────────┐
 * │ (1) Highlights & Summary (wide KPI banner)               │
 * ├──────────────┬──────────────┬──────────────┬─────────────┤
 * │ (2) Line     │ (3) Histogram│ (4) Heatmap  │ (5) Factor   │
 * │ Chart        │              │              │ Exposure     │
 * ├──────────────┴──────────────┬──────────────┴─────────────┤
 * │           (6) Signals Table │         (7) Trades Table     │
 * └──────────────────────────────────────────────────────────┘
 * 
 * When to Use This Layout:
 * ✅ Trading and investment signal analysis
 * ✅ Quantitative analytics with trading execution data
 * ✅ Real-time market analysis with signal generation
 * ✅ Factor-based investment strategies
 * ✅ Risk management with trading oversight
 * ✅ Portfolio management with execution tracking
 * 
 * Don't Use For:
 * ❌ Basic portfolio reporting (use Layout1-5)
 * ❌ Executive presentations (use Layout6-8)
 * ❌ Long-term strategic analysis (use Layout9-11)
 */

'use client';

import LayoutContainer from './components/LayoutContainer';
import LayoutHeader from './components/LayoutHeader';
import GridContainer4x3Layout12 from './components/GridContainer4x3Layout12';
import FullWidthTopRow4x3 from './components/FullWidthTopRow4x3';
import QuarterWidthChart from './components/QuarterWidthChart';
import HalfWidthBottomLeft12 from './components/HalfWidthBottomLeft12';
import HalfWidthBottomRight12 from './components/HalfWidthBottomRight12';

interface Layout12Props {
  title?: React.ReactNode;
  top?: React.ReactNode;               // FullWidthTopRow4x3 - Highlights & KPI Banner
  middleLeft?: React.ReactNode;        // QuarterWidthChart - Line Chart
  middleCenter1?: React.ReactNode;     // QuarterWidthChart - Histogram
  middleCenter2?: React.ReactNode;     // QuarterWidthChart - Heatmap
  middleRight?: React.ReactNode;       // QuarterWidthChart - Factor Exposure
  bottomLeft?: React.ReactNode;        // HalfWidthBottomLeft12 - Signals Table
  bottomRight?: React.ReactNode;       // HalfWidthBottomRight12 - Trades Table
}

export default function Layout12({
  title,
  top,
  middleLeft,
  middleCenter1,
  middleCenter2,
  middleRight,
  bottomLeft,
  bottomRight
}: Layout12Props) {
  return (
    <LayoutContainer>
      
      <LayoutHeader>
        {title}
      </LayoutHeader>

      <GridContainer4x3Layout12>
        
        <FullWidthTopRow4x3>
          {top}
        </FullWidthTopRow4x3>

        <QuarterWidthChart>
          {middleLeft}
        </QuarterWidthChart>

        <QuarterWidthChart>
          {middleCenter1}
        </QuarterWidthChart>

        <QuarterWidthChart>
          {middleCenter2}
        </QuarterWidthChart>

        <QuarterWidthChart>
          {middleRight}
        </QuarterWidthChart>

        <HalfWidthBottomLeft12>
          {bottomLeft}
        </HalfWidthBottomLeft12>

        <HalfWidthBottomRight12>
          {bottomRight}
        </HalfWidthBottomRight12>

      </GridContainer4x3Layout12>
      
    </LayoutContainer>
  );
}