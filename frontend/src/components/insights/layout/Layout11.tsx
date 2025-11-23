/**
 * Layout11: Comprehensive Multi-Level Analytics Dashboard
 * 
 * Grid Structure: 5x4 with mixed spans (8 sections)
 * 
 * Layout Map:
 * ┌─────────────────────────────────────────────────────────────────┐
 * │ (1) Highlights & Summary                                         │
 * ├──────────────┬──────────────┬──────────────┬──────────────┬─────┤
 * │ (2) Metric    │ (3) Line     │ (4) Histogram│ (5) Heatmap   │(6) │
 * │ Cards         │ Chart        │              │               │Scatter
 * ├──────────────┴──────────────┴──────────────┼──────────────┴─────┤
 * │                         (7) Sector/Group Breakdown Table          │
 * ├──────────────────────────────────────────────────────────────────┤
 * │                         (8) Detailed Raw Data Table               │
 * └──────────────────────────────────────────────────────────────────┘
 * 
 * When to Use This Layout:
 * ✅ Comprehensive enterprise dashboards with hierarchical data views
 * ✅ Multi-level analysis requiring summary, sector, and detailed views
 * ✅ Financial analysis with portfolio, sector, and security-level data
 * ✅ Complex reporting with KPIs, visualizations, and drill-down tables
 * ✅ Research analysis with overview, categorical, and raw data sections
 * ✅ Executive reporting with strategic, tactical, and operational views
 * 
 * Don't Use For:
 * ❌ Simple reporting (use Layout1-5)
 * ❌ Single-level analysis (use Layout6-10)
 * ❌ Mobile-first displays (too complex for small screens)
 */

'use client';

import LayoutContainer from './components/LayoutContainer';
import LayoutHeader from './components/LayoutHeader';
import GridContainer5x4Layout11 from './components/GridContainer5x4Layout11';
import FullWidthTopRow5x4 from './components/FullWidthTopRow5x4';
import FifthWidthChart from './components/FifthWidthChart';
import FifthWidthTallChart from './components/FifthWidthTallChart';
import FullWidthTable5x4 from './components/FullWidthTable5x4';

interface Layout11Props {
  title?: React.ReactNode;
  top?: React.ReactNode;                // FullWidthTopRow5x4 - Highlights & Summary
  middleLeft?: React.ReactNode;         // FifthWidthChart - Metric Cards
  middleCenter1?: React.ReactNode;      // FifthWidthChart - Line Chart  
  middleCenter2?: React.ReactNode;      // FifthWidthChart - Histogram
  middleCenter3?: React.ReactNode;      // FifthWidthChart - Heatmap
  middleRight?: React.ReactNode;        // FifthWidthTallChart - Scatter Plot (tall)
  bottom1?: React.ReactNode;            // FullWidthTable5x4 - Sector/Group Breakdown Table
  bottom2?: React.ReactNode;            // FullWidthTable5x4 - Detailed Raw Data Table
}

export default function Layout11({
  title,
  top,
  middleLeft,
  middleCenter1,
  middleCenter2,
  middleCenter3,
  middleRight,
  bottom1,
  bottom2
}: Layout11Props) {
  return (
    <LayoutContainer>
      
      <LayoutHeader>
        {title}
      </LayoutHeader>

      <GridContainer5x4Layout11>
        
        <FullWidthTopRow5x4>
          {top}
        </FullWidthTopRow5x4>

        <FifthWidthChart>
          {middleLeft}
        </FifthWidthChart>

        <FifthWidthChart>
          {middleCenter1}
        </FifthWidthChart>

        <FifthWidthChart>
          {middleCenter2}
        </FifthWidthChart>

        <FifthWidthChart>
          {middleCenter3}
        </FifthWidthChart>

        <FifthWidthTallChart>
          {middleRight}
        </FifthWidthTallChart>

        <FullWidthTable5x4>
          {bottom1}
        </FullWidthTable5x4>

        <FullWidthTable5x4>
          {bottom2}
        </FullWidthTable5x4>

      </GridContainer5x4Layout11>
      
    </LayoutContainer>
  );
}