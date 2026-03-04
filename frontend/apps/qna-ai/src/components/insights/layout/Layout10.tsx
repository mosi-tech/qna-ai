/**
 * Layout10: Comprehensive Analytics Dashboard with Categorical Analysis
 * 
 * Grid Structure: 4x3 with mixed spans (7 sections)
 * 
 * Layout Map:
 * ┌──────────────────────────────────────────────────────────┐
 * │ (1) Highlights & Summary                                  │
 * ├──────────────┬──────────────┬──────────────┬──────────────┤
 * │ (2) Metric    │ (3) Line     │ (4) Histogram│ (5) Bar Chart │
 * │ Cards         │ Chart        │              │ (categories)  │
 * ├──────────────┴──────────────┬──────────────┴──────────────┤
 * │             (6) Heatmap      │            (7) Table         │
 * └──────────────────────────────┴──────────────────────────────┘
 * 
 * When to Use This Layout:
 * ✅ Comprehensive business dashboards with KPIs and categorical data
 * ✅ Performance analysis with both time-series and categorical breakdowns
 * ✅ Executive reporting with metrics cards and detailed visualizations
 * ✅ Multi-dimensional analysis requiring diverse chart types
 * ✅ Financial analysis with risk matrices and performance tables
 * ✅ Marketing analytics with campaign performance and segmentation
 * 
 * Don't Use For:
 * ❌ Simple single-metric displays (use Layout4)
 * ❌ Timeline-focused analysis (use Layout5)
 * ❌ Basic comparison reports (use Layout1 or Layout2)
 */

'use client';

import LayoutContainer from './components/LayoutContainer';
import LayoutHeader from './components/LayoutHeader';
import GridContainer4x3Layout10 from './components/GridContainer4x3Layout10';
import FullWidthTopRow4x3 from './components/FullWidthTopRow4x3';
import QuarterWidthChart from './components/QuarterWidthChart';
import HalfWidthBottomLeft from './components/HalfWidthBottomLeft';
import HalfWidthBottomRight from './components/HalfWidthBottomRight';

interface Layout10Props {
  title?: React.ReactNode;
  top?: React.ReactNode;              // FullWidthTopRow4x3 - Highlights & Summary
  middleLeft?: React.ReactNode;       // QuarterWidthChart - Metric Cards
  middleCenter?: React.ReactNode;     // QuarterWidthChart - Line Chart
  middleRight1?: React.ReactNode;     // QuarterWidthChart - Histogram
  middleRight2?: React.ReactNode;     // QuarterWidthChart - Bar Chart (categories)
  bottomLeft?: React.ReactNode;       // HalfWidthBottomLeft - Heatmap
  bottomRight?: React.ReactNode;      // HalfWidthBottomRight - Table
}

export default function Layout10({
  title,
  top,
  middleLeft,
  middleCenter,
  middleRight1,
  middleRight2,
  bottomLeft,
  bottomRight
}: Layout10Props) {
  return (
    <LayoutContainer>
      
      <LayoutHeader>
        {title}
      </LayoutHeader>

      <GridContainer4x3Layout10>
        
        <FullWidthTopRow4x3>
          {top}
        </FullWidthTopRow4x3>

        <QuarterWidthChart>
          {middleLeft}
        </QuarterWidthChart>

        <QuarterWidthChart>
          {middleCenter}
        </QuarterWidthChart>

        <QuarterWidthChart>
          {middleRight1}
        </QuarterWidthChart>

        <QuarterWidthChart>
          {middleRight2}
        </QuarterWidthChart>

        <HalfWidthBottomLeft>
          {bottomLeft}
        </HalfWidthBottomLeft>

        <HalfWidthBottomRight>
          {bottomRight}
        </HalfWidthBottomRight>

      </GridContainer4x3Layout10>
      
    </LayoutContainer>
  );
}