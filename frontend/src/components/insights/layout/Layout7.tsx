/**
 * Layout7: Multi-Chart Dashboard
 * 
 * Grid Structure: 3x2 (3 columns, 2 rows)
 * 
 * Layout Map:
 * ┌─────────────────────────────────────────────────────────┐
 * │ (1) Highlights & Summary                                │
 * ├─────────────────────────┬───────────────────┬───────────┤
 * │ (2) Chart A (line)      │ (3) Chart B       │ (4) Chart C│
 * └─────────────────────────┴───────────────────┴───────────┘
 * 
 * When to Use This Layout:
 * ✅ Multi-chart analysis dashboards
 * ✅ Performance tracking across multiple metrics
 * ✅ Time-series comparison between different assets
 * ✅ Technical analysis with multiple indicators
 * ✅ Market overview with various visualizations
 * ✅ Research analysis requiring multiple chart types
 * 
 * Don't Use For:
 * ❌ Simple single-chart analysis (use Layout4 or Layout5)
 * ❌ Table-heavy analysis (use Layout1 or Layout6)
 * ❌ Equal-weight quadrant analysis (use Layout6)
 */

'use client';

import LayoutContainer from './components/LayoutContainer';
import LayoutHeader from './components/LayoutHeader';
import GridContainer3x2 from './components/GridContainer3x2';
import FullWidthTop3x2 from './components/FullWidthTop3x2';
import ThirdWidthBottomLeft from './components/ThirdWidthBottomLeft';
import ThirdWidthBottomCenter from './components/ThirdWidthBottomCenter';
import ThirdWidthBottomRight from './components/ThirdWidthBottomRight';

interface Layout7Props {
  title?: React.ReactNode;
  top?: React.ReactNode;            // FullWidthTop3x2 - Highlights & Summary
  bottomLeft?: React.ReactNode;     // ThirdWidthBottomLeft - Chart A (line)
  bottomCenter?: React.ReactNode;   // ThirdWidthBottomCenter - Chart B
  bottomRight?: React.ReactNode;    // ThirdWidthBottomRight - Chart C
}

export default function Layout7({
  title,
  top,
  bottomLeft,
  bottomCenter,
  bottomRight
}: Layout7Props) {
  return (
    <LayoutContainer>
      
      <LayoutHeader>
        {title}
      </LayoutHeader>

      <GridContainer3x2>
        
        <FullWidthTop3x2>
          {top}
        </FullWidthTop3x2>

        <ThirdWidthBottomLeft>
          {bottomLeft}
        </ThirdWidthBottomLeft>

        <ThirdWidthBottomCenter>
          {bottomCenter}
        </ThirdWidthBottomCenter>

        <ThirdWidthBottomRight>
          {bottomRight}
        </ThirdWidthBottomRight>

      </GridContainer3x2>
      
    </LayoutContainer>
  );
}