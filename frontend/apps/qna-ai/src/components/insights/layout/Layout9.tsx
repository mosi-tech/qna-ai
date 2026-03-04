/**
 * Layout9: Multi-Chart Analytics with Detailed Table
 * 
 * Grid Structure: 4x3 with mixed spans
 * 
 * Layout Map:
 * ┌──────────────────────────────────────────────────────────┐
 * │ (1) Highlights & Summary                                  │
 * ├──────────────┬──────────────┬──────────────┬──────────────┤
 * │ (2) Line     │ (3) Histogram│ (4) Heatmap  │ (5) Scatter   │
 * ├──────────────┴──────────────┬──────────────┴──────────────┤
 * │                 (6) Data Table (detailed)                 │
 * └──────────────────────────────────────────────────────────┘
 * 
 * When to Use This Layout:
 * ✅ Advanced analytics dashboards with multiple visualizations
 * ✅ Research analysis requiring diverse chart types
 * ✅ Data exploration with comprehensive table support
 * ✅ Technical analysis with multiple indicators
 * ✅ Scientific or statistical analysis presentations
 * ✅ Performance analysis across multiple dimensions
 * 
 * Don't Use For:
 * ❌ Simple reporting (use Layout1 or Layout5)
 * ❌ Focus on single metric (use Layout4)
 * ❌ Executive summaries (use Layout1)
 */

'use client';

import LayoutContainer from './components/LayoutContainer';
import LayoutHeader from './components/LayoutHeader';
import GridContainer4x3Mixed from './components/GridContainer4x3Mixed';
import FullWidthTopRow4x3 from './components/FullWidthTopRow4x3';
import QuarterWidthChart from './components/QuarterWidthChart';
import FullWidthBottomTable from './components/FullWidthBottomTable';

interface Layout9Props {
  title?: React.ReactNode;
  top?: React.ReactNode;            // FullWidthTopRow4x3 - Highlights & Summary
  middleLeft?: React.ReactNode;     // QuarterWidthChart - Line Chart
  middleCenter?: React.ReactNode;   // QuarterWidthChart - Histogram
  middleRight1?: React.ReactNode;   // QuarterWidthChart - Heatmap
  middleRight2?: React.ReactNode;   // QuarterWidthChart - Scatter Plot
  bottom?: React.ReactNode;         // FullWidthBottomTable - Detailed Data Table
}

export default function Layout9({
  title,
  top,
  middleLeft,
  middleCenter,
  middleRight1,
  middleRight2,
  bottom
}: Layout9Props) {
  return (
    <LayoutContainer>
      
      <LayoutHeader>
        {title}
      </LayoutHeader>

      <GridContainer4x3Mixed>
        
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

        <FullWidthBottomTable>
          {bottom}
        </FullWidthBottomTable>

      </GridContainer4x3Mixed>
      
    </LayoutContainer>
  );
}