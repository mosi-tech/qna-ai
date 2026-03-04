/**
 * Layout5: Highlights + Table & Chart
 * 
 * Grid Structure: 2x3 (2 columns, 3 rows)
 * 
 * Layout Map:
 * ┌───────────────────────────────────────────┐
 * │ (1) Highlights & Summary                  │
 * ├───────────────────────────┬───────────────┤
 * │ (2) Key Table             │ (3) Chart      │
 * └───────────────────────────┴───────────────┘
 * 
 * When to Use This Layout:
 * ✅ Report summaries with supporting data
 * ✅ Executive briefings with key metrics
 * ✅ Performance analysis with visualization
 * ✅ Research findings with data tables
 * ✅ Financial reports with charts
 * 
 * Don't Use For:
 * ❌ Complex multi-entity comparisons (use Layout2)
 * ❌ Deep single-topic analysis (use Layout4)
 * ❌ Multi-column dashboards (use Layout3)
 */

'use client';

import LayoutContainer from './components/LayoutContainer';
import LayoutHeader from './components/LayoutHeader';
import GridContainer2x3 from './components/GridContainer2x3';
import FullWidthTop2x3 from './components/FullWidthTop2x3';
import HalfWidthBottomLeft2x3 from './components/HalfWidthBottomLeft2x3';
import HalfWidthBottomRight2x3 from './components/HalfWidthBottomRight2x3';

interface Layout5Props {
  title?: React.ReactNode;
  top?: React.ReactNode;           // FullWidthTop2x3 - Highlights & Summary
  bottomLeft?: React.ReactNode;    // HalfWidthBottomLeft2x3 - Key Table
  bottomRight?: React.ReactNode;   // HalfWidthBottomRight2x3 - Chart/Visualization
}

export default function Layout5({
  title,
  top,
  bottomLeft,
  bottomRight
}: Layout5Props) {
  return (
    <LayoutContainer>
      
      <LayoutHeader>
        {title}
      </LayoutHeader>

      <GridContainer2x3>
        
        <FullWidthTop2x3>
          {top}
        </FullWidthTop2x3>

        <HalfWidthBottomLeft2x3>
          {bottomLeft}
        </HalfWidthBottomLeft2x3>

        <HalfWidthBottomRight2x3>
          {bottomRight}
        </HalfWidthBottomRight2x3>

      </GridContainer2x3>
      
    </LayoutContainer>
  );
}