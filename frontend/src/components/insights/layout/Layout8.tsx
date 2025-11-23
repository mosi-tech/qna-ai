/**
 * Layout8: Comprehensive Analytics Dashboard
 * 
 * Grid Structure: 3x3 with mixed spans
 * 
 * Layout Map:
 * ┌──────────────────────────────────────────────────────────┐
 * │ (1) Highlights & Summary                                  │
 * ├──────────────────────┬──────────────────────┬─────────────┤
 * │ (2) Metric Cards      │ (3) Line Chart       │ (4) Histogram│
 * ├──────────────────────┴──────────────────────┬─────────────┤
 * │                    (5) Data Table           │             │
 * └──────────────────────────────────────────────┴─────────────┘
 * 
 * When to Use This Layout:
 * ✅ Comprehensive analytics dashboards
 * ✅ Executive reporting with mixed content types
 * ✅ Performance analysis with metrics, charts, and data
 * ✅ Research reports requiring multiple visualization types
 * ✅ Business intelligence dashboards
 * ✅ Portfolio analysis with detailed breakdowns
 * 
 * Don't Use For:
 * ❌ Simple analysis (use Layout1 or Layout5)
 * ❌ Equal-weight comparisons (use Layout6)
 * ❌ Focus on single metric (use Layout4)
 */

'use client';

import LayoutContainer from './components/LayoutContainer';
import LayoutHeader from './components/LayoutHeader';
import GridContainer3x3Mixed from './components/GridContainer3x3Mixed';
import FullWidthTopRow from './components/FullWidthTopRow';
import ThirdWidthMiddleLeft from './components/ThirdWidthMiddleLeft';
import ThirdWidthMiddleCenter from './components/ThirdWidthMiddleCenter';
import ThirdWidthMiddleRight from './components/ThirdWidthMiddleRight';
import TwoThirdsWidthBottom from './components/TwoThirdsWidthBottom';

interface Layout8Props {
  title?: React.ReactNode;
  top?: React.ReactNode;            // FullWidthTopRow - Highlights & Summary
  middleLeft?: React.ReactNode;     // ThirdWidthMiddleLeft - Metric Cards
  middleCenter?: React.ReactNode;   // ThirdWidthMiddleCenter - Line Chart
  middleRight?: React.ReactNode;    // ThirdWidthMiddleRight - Histogram
  bottom?: React.ReactNode;         // TwoThirdsWidthBottom - Data Table
}

export default function Layout8({
  title,
  top,
  middleLeft,
  middleCenter,
  middleRight,
  bottom
}: Layout8Props) {
  return (
    <LayoutContainer>
      
      <LayoutHeader>
        {title}
      </LayoutHeader>

      <GridContainer3x3Mixed>
        
        <FullWidthTopRow>
          {top}
        </FullWidthTopRow>

        <ThirdWidthMiddleLeft>
          {middleLeft}
        </ThirdWidthMiddleLeft>

        <ThirdWidthMiddleCenter>
          {middleCenter}
        </ThirdWidthMiddleCenter>

        <ThirdWidthMiddleRight>
          {middleRight}
        </ThirdWidthMiddleRight>

        <TwoThirdsWidthBottom>
          {bottom}
        </TwoThirdsWidthBottom>

      </GridContainer3x3Mixed>
      
    </LayoutContainer>
  );
}