import React from 'react';
import { Card } from '../../tremor/components/Card';
import { LineChart } from '../../tremor/components/LineChart';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../tremor/components/Tabs';
import { cx } from '../../lib/utils';
import type { RangeTab } from './line-chart-07';

export interface LineChart02Props {
    data: Array<Record<string, any>>;
    subtitle: string;
    value: string;
    change: string;
    changeType: 'positive' | 'negative';
    summary: Array<{ name: string; value: string }>;
    valueFormatter?: (num: number) => string;
    /** Key in the data objects used as the x-axis index. Defaults to 'date'. */
    indexField?: string;
    /** Series keys to plot. Defaults to ['price']. */
    categories?: string[];
    /** Label shown next to the change value. Defaults to 'Past 24 hours'. */
    periodLabel?: string;
    /**
     * Optional range selector rendered as solid pill tabs above the chart.
     * When omitted, the full `data` array is rendered as-is.
     */
    rangeTabs?: RangeTab[];
    className?: string;
}

/**
 * LineChart02: Price chart with headline metrics and dual-column summary
 * Direct implementation matching tremor block structure
 */
export const LineChart02: React.FC<LineChart02Props> = ({
    data,
    subtitle,
    value,
    change,
    changeType,
    summary,
    valueFormatter = (num) => Intl.NumberFormat('en').format(num),
    indexField = 'date',
    categories = ['price'],
    periodLabel = 'Past 24 hours',
    rangeTabs,
    className
}) => {
    return (
        <div className={cx('obfuscate', className)}>
            <Card className="sm:mx-auto sm:max-w-lg">
                {/* Header: Subtitle */}
                <h3 className="text-sm text-gray-500 dark:text-gray-500">
                    {subtitle}
                </h3>

                {/* Header: Large Price Value */}
                <p className="mt-1 text-3xl font-semibold text-gray-900 dark:text-gray-50">
                    {value}
                </p>

                {/* Header: Change Indicator */}
                <p className="mt-1 text-sm font-medium">
                    <span
                        className={
                            changeType === 'positive'
                                ? 'text-emerald-700 dark:text-emerald-500'
                                : 'text-red-700 dark:text-red-500'
                        }
                    >
                        {change}
                    </span>{' '}
                    <span className="font-normal text-gray-500 dark:text-gray-500">
                        {periodLabel}
                    </span>
                </p>

                {/* Line Chart */}
                {rangeTabs && rangeTabs.length > 0 ? (
                    <Tabs defaultValue={rangeTabs[0].name} className="mt-4">
                        <div className="flex justify-end mb-2">
                            <TabsList variant="solid">
                                {rangeTabs.map((t) => (
                                    <TabsTrigger key={t.name} value={t.name}>
                                        {t.name}
                                    </TabsTrigger>
                                ))}
                            </TabsList>
                        </div>
                        {rangeTabs.map((t) => (
                            <TabsContent key={t.name} value={t.name}>
                                <LineChart
                                    data={t.dataRange}
                                    index={indexField}
                                    categories={categories}
                                    valueFormatter={valueFormatter}
                                    showLegend={false}
                                    showYAxis={false}
                                    className="!h-48"
                                />
                            </TabsContent>
                        ))}
                    </Tabs>
                ) : (
                    <LineChart
                        data={data}
                        index={indexField}
                        categories={categories}
                        valueFormatter={valueFormatter}
                        showLegend={false}
                        showYAxis={false}
                        className="mt-6 !h-48"
                    />
                )}

                {/* Dual-Column Summary */}
                <div className="justify-betwee mt-4 flex gap-6">
                    <ul
                        role="list"
                        className="mt-2 w-full divide-y divide-gray-200 truncate text-sm text-gray-500 dark:divide-gray-800 dark:text-gray-500"
                    >
                        {summary.slice(0, 3).map((item) => (
                            <li
                                key={item.name}
                                className="flex items-center justify-between py-2.5"
                            >
                                <span className="truncate">{item.name}</span>
                                <span className="font-medium text-gray-900 dark:text-gray-50">
                                    {item.value}
                                </span>
                            </li>
                        ))}
                    </ul>
                    <ul
                        role="list"
                        className="mt-2 w-full divide-y divide-gray-200 truncate text-sm text-gray-500 dark:divide-gray-800 dark:text-gray-500"
                    >
                        {summary.slice(3, 6).map((item) => (
                            <li
                                key={item.name}
                                className="flex items-center justify-between py-2.5"
                            >
                                <span className="truncate">{item.name}</span>
                                <span className="font-medium text-gray-900 dark:text-gray-50">
                                    {item.value}
                                </span>
                            </li>
                        ))}
                    </ul>
                </div>
            </Card>
        </div>
    );
};

// Example usage with sample data
