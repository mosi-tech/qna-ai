/**
 * Layout6: Quadrant Analysis
 * 
 * Grid Structure: 2x2 (2 columns, 2 rows)
 * 
 * Layout Map:
 * ┌─────────────────────────┬──────────────────────────┐
 * │ (1) Highlights & Summary│ (2) Time-Series Chart    │
 * ├─────────────────────────┼──────────────────────────┤
 * │ (3) Breakdown Table     │ (4) Heatmap / Histogram  │
 * └─────────────────────────┴──────────────────────────┘
 * 
 * When to Use This Layout:
 * ✅ Comprehensive analysis with equal-weight sections
 * ✅ Multi-dimensional data analysis
 * ✅ Performance dashboards with time series
 * ✅ Risk analysis with heatmaps
 * ✅ Quarterly/annual reports
 * ✅ Research analysis with multiple visualizations
 * 
 * Don't Use For:
 * ❌ Simple summaries (use Layout5)
 * ❌ Single focus analysis (use Layout4)
 * ❌ Side-by-side comparisons only (use Layout2)
 */

'use client';

import LayoutContainer from './components/LayoutContainer';
import LayoutHeader from './components/LayoutHeader';
import GridContainer2x2 from './components/GridContainer2x2';
import QuadrantTopLeft from './components/QuadrantTopLeft';
import QuadrantTopRight from './components/QuadrantTopRight';
import QuadrantBottomLeft from './components/QuadrantBottomLeft';
import QuadrantBottomRight from './components/QuadrantBottomRight';

interface Layout6Props {
  title?: React.ReactNode;
  topLeft?: React.ReactNode;        // QuadrantTopLeft - Highlights & Summary
  topRight?: React.ReactNode;       // QuadrantTopRight - Time-Series Chart
  bottomLeft?: React.ReactNode;     // QuadrantBottomLeft - Breakdown Table
  bottomRight?: React.ReactNode;    // QuadrantBottomRight - Heatmap / Histogram
}

export default function Layout6({
  title,
  topLeft,
  topRight,
  bottomLeft,
  bottomRight
}: Layout6Props) {
  return (
    <LayoutContainer>
      
      <LayoutHeader>
        {title}
      </LayoutHeader>

      <GridContainer2x2>
        
        <QuadrantTopLeft>
          {topLeft}
        </QuadrantTopLeft>

        <QuadrantTopRight>
          {topRight}
        </QuadrantTopRight>

        <QuadrantBottomLeft>
          {bottomLeft}
        </QuadrantBottomLeft>

        <QuadrantBottomRight>
          {bottomRight}
        </QuadrantBottomRight>

      </GridContainer2x2>
      
    </LayoutContainer>
  );
}