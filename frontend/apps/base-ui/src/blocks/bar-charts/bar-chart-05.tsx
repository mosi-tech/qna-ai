import React from 'react';
import { AvailableChartColorsKeys } from '../../lib/chartUtils';
import { cx } from '../../lib/utils';
import { BarChart } from '../../tremor/components/BarChart';
import { Card } from '../../tremor/components/Card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../tremor/components/Tabs';
import { defaultCurrencyFormatter } from '../../lib/financeFormatters';

export interface BarChartDataItem {
    [key: string]: string | number;
}

export interface DetailItem {
    name: string;
    value: number;
}

export interface SummaryTabItem {
    name: string;
    data: BarChartDataItem[];
    details: DetailItem[];
}

export interface BarChart05Props {
    summary?: SummaryTabItem[];
    title: string;
    indexField?: string;
    categories?: string[];
    colors?: AvailableChartColorsKeys[];
    type?: 'default' | 'stacked' | 'percent';
    /** Map detail item names to their colors (e.g., {'Buy': 'bg-green-500', 'Sell': 'bg-red-500'}) */
    detailItemColorMap?: Record<string, string>;
    valueFormatter?: (value: number) => string;
  className?: string;
}

/** Default color mapping - can be overridden via detailItemColorMap prop */
const defaultDetailColor = (index: number): string => {
    const colors = [
        'bg-blue-500 dark:bg-blue-500',
        'bg-violet-500 dark:bg-violet-500',
        'bg-fuchsia-500 dark:bg-fuchsia-500',
        'bg-cyan-500 dark:bg-cyan-500',
        'bg-emerald-500 dark:bg-emerald-500',
    ];
    return colors[index % colors.length];
};

export const BarChart05: React.FC<BarChart05Props> = ({
    summary = [],
    title,
    indexField = 'date',
    categories = [],
    colors = [],
    type = 'stacked' as const,
    detailItemColorMap,
    valueFormatter = defaultCurrencyFormatter,

    className
}) => {
    // Use provided categories/colors or derive from summary data
    const finalCategories = categories.length > 0 ? categories : summary[0]?.data ? Object.keys(summary[0].data).filter(k => k !== indexField) : [];
    const finalColors = colors.length > 0 ? colors : (finalCategories.length > 0 ? finalCategories.map(() => 'blue') : []) as AvailableChartColorsKeys[];

    return (
        <Card className="sm:mx-auto sm:max-w-lg">
            <h3 className="font-medium text-gray-900 dark:text-gray-50">
                {title}
            </h3>
            <Tabs defaultValue={summary[0]?.name || ''} className="mt-8">
                <TabsList>
                    {summary.map((tab) => (
                        <TabsTrigger key={tab.name} value={tab.name}>
                            {tab.name}
                        </TabsTrigger>
                    ))}
                </TabsList>
                {summary.map((region) => (
                    <TabsContent key={region.name} value={region.name}>
                        <BarChart
                            data={region.data}
                            index={indexField}
                            categories={finalCategories}
                            colors={finalColors as AvailableChartColorsKeys[]}
                            valueFormatter={valueFormatter}
                            type={type}
                            showLegend={false}
                            showYAxis={false}
                            startEndOnly={true}
                            className="mt-8 !h-48"
                        />
                        <ul
                            role="list"
                            className="mt-2 divide-y divide-gray-200 text-sm text-gray-500 dark:divide-gray-800 dark:text-gray-500"
                        >
                            {region.details.map((item, idx) => {
                                const itemColor = detailItemColorMap?.[item.name] || defaultDetailColor(idx);
                                return (
                                    <li
                                        key={item.name}
                                        className="flex items-center justify-between py-1.5"
                                    >
                                        <div className="flex items-center space-x-2">
                                            <span
                                                className={cx(
                                                    itemColor,
                                                    'size-2 shrink-0 rounded-sm',
                                                )}
                                                aria-hidden={true}
                                            />
                                            <span>{item.name}</span>
                                        </div>
                                        <span className="font-medium text-gray-900 dark:text-gray-50">
                                            {valueFormatter(item.value)}
                                        </span>
                                    </li>
                                );
                            })}
                        </ul>
                    </TabsContent>
                ))}
            </Tabs>
        </Card>
    );
};
