'use client';

import { useState } from 'react';
import Layout10 from '@/components/insights/layout/Layout10';
import SummaryConclusion from '@/components/insights/SummaryConclusion';
import StatGroup from '@/components/insights/StatGroup';
import Section from '@/components/insights/Section';
import MatrixTable from '@/components/insights/MatrixTable';
import ComparisonTable from '@/components/insights/ComparisonTable';
import { getRandomComponentsForLayout } from '@/components/insights/layout/utils/layout-randomizer';

export default function Layout10Demo() {
  const layout10Positions = ['top', 'middleLeft', 'middleCenter', 'middleRight1_10', 'middleRight2_10', 'bottomLeft', 'bottomRight'];
  const [randomComponents, setRandomComponents] = useState<Record<string, React.ReactNode>>({});
  const [useRandom, setUseRandom] = useState(false);

  const generateRandomLayout = () => {
    const newComponents = getRandomComponentsForLayout(layout10Positions);
    setRandomComponents(newComponents);
    setUseRandom(true);
  };

  const resetToOriginal = () => {
    setUseRandom(false);
  };

  const originalComponents = {
    top: (
      <SummaryConclusion
        title="Q4 Business Performance Summary"
        keyFindings={[
          "Revenue exceeded targets by 18.5% with $47.2M total quarterly performance",
          "Customer acquisition cost reduced by 23% through improved marketing efficiency",
          "Product category diversification driving 34% increase in cross-selling opportunities",
          "Geographic expansion into APAC region showing 127% growth quarter-over-quarter"
        ]}
        conclusion="Exceptional Q4 performance demonstrates successful execution of strategic initiatives. Strong fundamentals across all business units support aggressive growth targets for next fiscal year."
        nextSteps={[
          "Scale APAC operations with additional $12M investment",
          "Launch premium product tier to capture high-value segment",
          "Implement predictive analytics for customer retention"
        ]}
        confidence="very-high"
      />
    ),
    middleLeft: (
      <StatGroup
        title="Key Metrics"
        stats={[
          {
            label: "Revenue",
            value: "$47.2M",
            change: "+18.5%",
            changeType: "positive"
          },
          {
            label: "CAC",
            value: "$234",
            change: "-23%",
            changeType: "positive"
          },
          {
            label: "NPS",
            value: "74",
            change: "+8",
            changeType: "positive"
          },
          {
            label: "Churn",
            value: "2.1%",
            change: "-1.2%",
            changeType: "positive"
          }
        ]}
        columns={4}
      />
    ),
    middleCenter: (
      <Section title="Revenue Trend">
        <div className="h-full flex flex-col">
          <div className="flex-1 bg-gray-100 rounded border-2 border-dashed border-gray-300 flex items-center justify-center mb-2">
            <div className="text-center">
              <div className="text-sm font-semibold text-gray-700 mb-1">Monthly Revenue</div>
              <div className="text-xs text-gray-500 mb-2">12-Month Trend</div>
              <div className="bg-white p-2 rounded shadow-sm text-xs">
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-blue-600">Growth:</span>
                    <span className="font-medium">+18.5%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Trajectory:</span>
                    <span className="font-medium text-green-600">↗ Strong</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="text-xs text-center">
            <span className="text-green-600 font-medium">Accelerating Growth</span>
          </div>
        </div>
      </Section>
    ),
    middleRight1_10: (
      <Section title="Deal Size Distribution">
        <div className="h-full flex flex-col">
          <div className="flex-1 bg-gray-100 rounded border-2 border-dashed border-gray-300 flex items-center justify-center mb-2">
            <div className="text-center">
              <div className="text-sm font-semibold text-gray-700 mb-1">Contract Values</div>
              <div className="text-xs text-gray-500 mb-2">Distribution Analysis</div>
              <div className="bg-white p-2 rounded shadow-sm text-xs">
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Median:</span>
                    <span className="font-medium">$12.4K</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Mode:</span>
                    <span className="font-medium">$8.5K</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="text-xs text-center">
            <span className="text-blue-600 font-medium">Healthy Distribution</span>
          </div>
        </div>
      </Section>
    ),
    middleRight2_10: (
      <Section title="Category Performance">
        <div className="h-full flex flex-col">
          <div className="flex-1 bg-gray-100 rounded border-2 border-dashed border-gray-300 flex items-center justify-center mb-2">
            <div className="text-center">
              <div className="text-sm font-semibold text-gray-700 mb-1">Product Categories</div>
              <div className="text-xs text-gray-500 mb-2">Revenue Contribution</div>
              <div className="bg-white p-2 rounded shadow-sm text-xs">
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Enterprise:</span>
                    <span className="font-medium">42%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Mid-Market:</span>
                    <span className="font-medium">35%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">SMB:</span>
                    <span className="font-medium">23%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="text-xs text-center">
            <span className="text-purple-600 font-medium">Balanced Portfolio</span>
          </div>
        </div>
      </Section>
    ),
    bottomLeft: (
      <MatrixTable
        title="Regional Risk Assessment Matrix"
        matrix={[
          ["✓", "", ""],
          ["✓", "", ""],
          ["", "✓", ""],
          ["", "", "✓"],
          ["", "✓", ""]
        ]}
        rowLabels={["North America", "Europe", "APAC", "Latin America", "Middle East"]}
        columnLabels={["Low Risk", "Medium Risk", "High Risk"]}
        format="number"
        colorScale={true}
      />
    ),
    bottomRight: (
      <ComparisonTable
        title="Top Performance Segments"
        entities={[
          { id: "enterprise", name: "Enterprise Software", subtitle: "42% • High Growth • Premium Tier" },
          { id: "midmarket", name: "Mid-Market Solutions", subtitle: "35% • Stable Growth • Core Product" },
          { id: "smb", name: "Small Business Tools", subtitle: "23% • Volume Growth • Basic Tier" },
          { id: "consulting", name: "Professional Services", subtitle: "8% • High Margin • Support Revenue" }
        ]}
        metrics={[
          { id: "revenue", name: "Revenue", format: "currency" },
          { id: "growth", name: "Growth", format: "percentage" },
          { id: "margin", name: "Margin", format: "percentage" },
          { id: "customers", name: "Customers", format: "number" }
        ]}
        data={{
          "enterprise": { 
            "revenue": "$19.8M", 
            "growth": "+24.3%", 
            "margin": "68%",
            "customers": "142"
          },
          "midmarket": { 
            "revenue": "$16.5M", 
            "growth": "+16.7%", 
            "margin": "45%",
            "customers": "1,247"
          },
          "smb": { 
            "revenue": "$10.9M", 
            "growth": "+12.1%", 
            "margin": "32%",
            "customers": "8,934"
          },
          "consulting": { 
            "revenue": "$3.8M", 
            "growth": "+31.2%", 
            "margin": "78%",
            "customers": "89"
          }
        }}
      />
    )
  };

  const activeComponents = useRandom ? randomComponents : originalComponents;

  return (
    <>
      {/* Randomizer Controls */}
      <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-medium text-yellow-800">Layout Testing Controls</h3>
            <p className="text-xs text-yellow-600">Test different component combinations in sub-layouts</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={generateRandomLayout}
              className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
            >
              🎲 Randomize Components
            </button>
            <button
              onClick={resetToOriginal}
              className="px-3 py-1.5 bg-gray-600 text-white text-sm rounded hover:bg-gray-700 transition-colors"
            >
              🔄 Reset Original
            </button>
          </div>
        </div>
        {useRandom && (
          <div className="mt-2 text-xs text-yellow-700">
            🎯 Showing randomized components to test variant compatibility
          </div>
        )}
      </div>

    <Layout10
      title={
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Executive Business Intelligence Dashboard {useRandom && '(Randomized)'}</h1>
          <p className="text-gray-600 mt-1">KPIs • Performance Analytics • Categorical Analysis • Risk Assessment</p>
        </div>
      }
      
      top={activeComponents.top}
      middleLeft={activeComponents.middleLeft}
      middleCenter={activeComponents.middleCenter}
      middleRight1={activeComponents.middleRight1_10}
      middleRight2={activeComponents.middleRight2_10}
      bottomLeft={activeComponents.bottomLeft}
      bottomRight={activeComponents.bottomRight}
    />
    </>
  );
}