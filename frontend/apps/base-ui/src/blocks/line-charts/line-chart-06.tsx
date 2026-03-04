import React from 'react';
import { cx } from '../../lib/utils';
import { Card } from '../../tremor/components/Card';
import { LineChart } from '../../tremor/components/LineChart';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../tremor/components/Tabs';

export interface ChartSummaryItem {
    name: string;
    value: string;
    changeType: 'positive' | 'negative' | null;
}

/** @deprecated Use ChartSummaryItem instead. */
export type PortfolioSummaryItem = ChartSummaryItem;

export interface TabDefinition {
    name: string;
    dataRange: Array<Record<string, any>>;
}

export interface LineChart06Props {
    data: Array<Record<string, any>>;
    headline: string;
    headlineValue: string;
    change: string;
    /** Controls the color of the change value. Defaults to 'positive'. */
    changeType?: 'positive' | 'negative' | 'neutral';
    categories?: string[];
    colors?: string[];
    summary: ChartSummaryItem[];
    tabs: TabDefinition[];
    defaultTab?: string;
    valueFormatter?: (num: number) => string;
    /** Key in the data objects used as the x-axis index. Defaults to 'date'. */
    indexField?: string;
    /** Label shown next to the change value. Defaults to 'Past 24 hours'. */
    periodLabel?: string;
  className?: string;
}

/**
 * LineChart06: Portfolio performance with tabs and summary grid
 */
export const LineChart06: React.FC<LineChart06Props> = ({
    data,
    headline,
    headlineValue,
    change,
    changeType = 'positive',
    categories = ['Portfolio', 'Market Index'],
    colors = ['blue', 'cyan'],
    summary,
    tabs,
    defaultTab,
    valueFormatter = (number) => Intl.NumberFormat('en').format(number),
    indexField = 'date',
    periodLabel = 'Past 24 hours',

    className
}) => {
    // Compute defaultTab safely inside the component
    const activeTab = defaultTab || tabs?.[2]?.name || tabs?.[0]?.name || 'Tab';

    return (
        <div className={cx('obfuscate', className)}>
            <Card className="!p-0">
                <div className="p-6">
                    <h3 className="text-sm text-gray-500 dark:text-gray-500">
                        {headline}
                    </h3>
                    <p className="mt-1 text-3xl font-semibold text-gray-900 dark:text-gray-50">
                        {headlineValue}
                    </p>
                    <p className="mt-1 text-sm font-medium">
                        <span
                            className={
                                changeType === 'positive'
                                    ? 'text-emerald-700 dark:text-emerald-500'
                                    : changeType === 'negative'
                                        ? 'text-red-700 dark:text-red-500'
                                        : 'text-gray-900 dark:text-gray-50'
                            }
                        >
                            {change}
                        </span>{' '}
                        <span className="font-normal text-gray-500 dark:text-gray-500">
                            {periodLabel}
                        </span>
                    </p>
                </div>
                <Tabs defaultValue={activeTab}>
                    <TabsList variant="line" className="px-6">
                        {tabs.map((tab: any) => (
                            <TabsTrigger key={tab.name} value={tab.name}>
                                {tab.name}
                            </TabsTrigger>
                        ))}
                    </TabsList>
                    <div className="mt-6 px-6">
                        {tabs.map((tab: any) => (
                            <TabsContent key={tab.name} value={tab.name}>
                                <LineChart
                                    data={tab.dataRange}
                                    index={indexField}
                                    categories={categories}
                                    colors={colors as any}
                                    valueFormatter={valueFormatter}
                                    yAxisWidth={40}
                                    tickGap={10}
                                    showLegend={false}
                                    className="hidden !h-72 sm:block"
                                />
                                <LineChart
                                    data={tab.dataRange}
                                    index={indexField}
                                    categories={categories}
                                    colors={colors as any}
                                    valueFormatter={valueFormatter}
                                    showYAxis={false}
                                    showLegend={false}
                                    startEndOnly={true}
                                    className="!h-72 sm:hidden"
                                />
                            </TabsContent>
                        ))}
                    </div>
                </Tabs>

                <div className="p-6">
                    <h4 className="text-sm font-medium text-gray-900 dark:text-gray-50">
                        Portfolio summary
                    </h4>
                    <div className="mt-4 sm:flex sm:items-center sm:gap-8">
                        <ul
                            role="list"
                            className="w-full divide-y divide-gray-200 truncate text-sm text-gray-500 dark:divide-gray-800 dark:text-gray-500"
                        >
                            {summary.slice(0, 3).map((item: any) => (
                                <li
                                    key={item.name}
                                    className="flex items-center justify-between py-2.5"
                                >
                                    <span>{item.name}</span>
                                    <span className="font-medium text-gray-900 dark:text-gray-50">
                                        {item.value}
                                    </span>
                                </li>
                            ))}
                        </ul>
                        <ul
                            role="list"
                            className="mt-4 w-full divide-y divide-gray-200 truncate text-sm text-gray-500 dark:divide-gray-800 dark:text-gray-500 sm:mt-0"
                        >
                            {summary.slice(3, 6).map((item: any) => (
                                <li
                                    key={item.name}
                                    className="flex items-center justify-between py-2.5"
                                >
                                    <span>{item.name}</span>
                                    <span
                                        className={cx(
                                            item.changeType === 'positive'
                                                ? 'text-emerald-700 dark:text-emerald-500'
                                                : item.changeType === 'negative'
                                                    ? 'text-red-700 dark:text-red-500'
                                                    : 'text-gray-900 dark:text-gray-50',
                                            'font-medium',
                                        )}
                                    >
                                        {item.value}
                                    </span>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>
            </Card>
        </div>
    );
};

// Example usage with sample data
