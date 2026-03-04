import React from 'react';
import { Card } from '../../tremor/components/Card';
import { LineChart } from '../../tremor/components/LineChart';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../tremor/components/Tabs';
import { cx } from '../../lib/utils';
import type { RangeTab } from './line-chart-07';

export interface LineChart01Props {
    data: Array<Record<string, any>>;
    title: string;
    categories: string[];
    colors?: string[];
    summary: Array<{ name: string; value: number }>;
    valueFormatter?: (num: number) => string;
    /** Key in the data objects used as the x-axis index. Defaults to 'date'. */
    indexField?: string;
    /**
     * Optional range selector rendered as solid pill tabs above the chart.
     * When omitted, the full `data` array is rendered as-is.
     */
    rangeTabs?: RangeTab[];
    className?: string;
}

/**
 * LineChart01: Multi-Series with Summary Metrics (colored dots)
 * Direct implementation matching tremor block structure
 */
export const LineChart01: React.FC<LineChart01Props> = ({
    data,
    title,
    categories,
    colors = ['blue', 'violet', 'fuchsia'],
    summary,
    valueFormatter = (num) => Intl.NumberFormat('en').format(num),
    indexField = 'date',
    rangeTabs,
    className
}) => {
    const colorMap: Record<string, string> = {
        blue: 'bg-blue-500 dark:bg-blue-500',
        violet: 'bg-violet-500 dark:bg-violet-500',
        fuchsia: 'bg-fuchsia-500 dark:bg-fuchsia-500',
    };

    return (
        <div className="obfuscate">
            <Card className={cx(className)}>
                {/* Title */}
                <h3 className="text-sm font-medium text-gray-900 dark:text-gray-50">
                    {title}
                </h3>

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
                                    colors={colors as any}
                                    valueFormatter={valueFormatter}
                                    showLegend={false}
                                    showYAxis={false}
                                    startEndOnly={true}
                                    className="!h-32"
                                />
                            </TabsContent>
                        ))}
                    </Tabs>
                ) : (
                    <LineChart
                        data={data}
                        index={indexField}
                        categories={categories}
                        colors={colors as any}
                        valueFormatter={valueFormatter}
                        showLegend={false}
                        showYAxis={false}
                        startEndOnly={true}
                        className="mt-6 !h-32"
                    />
                )}

                {/* Summary with colored dots */}
                <ul
                    role="list"
                    className="mt-2 divide-y divide-gray-200 text-sm text-gray-500 dark:divide-gray-800 dark:text-gray-500"
                >
                    {summary.map((item, idx) => (
                        <li
                            key={item.name}
                            className="flex items-center justify-between py-2.5"
                        >
                            <div className="flex items-center space-x-2">
                                <span
                                    className={cx(
                                        colorMap[colors[idx]] ||
                                        'bg-gray-400',
                                        'h-[3px] w-3.5 shrink-0 rounded-full',
                                    )}
                                    aria-hidden={true}
                                />
                                <span>{item.name}</span>
                            </div>
                            <span className="font-medium text-gray-900 dark:text-gray-50">
                                {valueFormatter(item.value)}
                            </span>
                        </li>
                    ))}
                </ul>
            </Card>
        </div>
    );
};

// Example usage with sample data
