import React from 'react';
import { RiAddFill } from '@remixicon/react';
import { cx } from '../../lib/utils';
import { Card } from '../../tremor/components/Card';
import { LineChart } from '../../tremor/components/LineChart';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../tremor/components/Tabs';
import type { RangeTab } from './line-chart-07';

export interface SeriesSummaryItem {
    name: string;
    value: string;
    bgColor: string;
}

/** @deprecated Use SeriesSummaryItem instead. */
export type ETFSidebarItem = SeriesSummaryItem;

export interface LineChart08Props {
    data: Array<Record<string, any>>;
    title: string;
    subtitle: string;
    categories?: string[];
    colors?: string[];
    summary: SeriesSummaryItem[];
    valueFormatter?: (num: number) => string;
    /** Key in the data objects used as the x-axis index. Defaults to 'date'. */
    indexField?: string;
    /** Label for the compare action button. Defaults to 'Compare asset'. */
    compareLabel?: string;
    /** Callback fired when the compare button is clicked. */
    onCompare?: () => void;
    /**
     * Optional compact range selector rendered as solid pill tabs above the chart.
     * When omitted, the chart renders with the full `data` array as-is.
     */
    rangeTabs?: RangeTab[];
  className?: string;
}

/**
 * LineChart08: Two-column grid layout with chart and sidebar summary
 */
export const LineChart08: React.FC<LineChart08Props> = ({
    data,
    title,
    subtitle,
    categories = ['ETF Shares Vital', 'Vitainvest Core', 'iShares Tech Growth'],
    colors = ['blue', 'violet', 'fuchsia'],
    summary,
    valueFormatter = (number) => Intl.NumberFormat('en').format(number),
    indexField = 'date',
    compareLabel = 'Compare asset',
    onCompare,
    rangeTabs,

    className
}) => {
    return (
        <div className={cx('obfuscate', className)}>
            <h3 className="font-medium text-gray-900 dark:text-gray-50">
                {title}
            </h3>
            <p className="mt-1 text-sm/6 text-gray-500 dark:text-gray-500">
                {subtitle}
            </p>
            <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-3">
                <Card className="lg:col-span-2">
                    {rangeTabs && rangeTabs.length > 0 ? (
                        <Tabs defaultValue={rangeTabs[0].name}>
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
                                        yAxisWidth={55}
                                        showLegend={false}
                                        className="hidden !h-72 sm:block"
                                    />
                                    <LineChart
                                        data={t.dataRange}
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
                        </Tabs>
                    ) : (
                        <>
                            <LineChart
                                data={data}
                                index={indexField}
                                categories={categories}
                                colors={colors as any}
                                valueFormatter={valueFormatter}
                                yAxisWidth={55}
                                showLegend={false}
                                className="hidden !h-72 sm:block"
                            />
                            <LineChart
                                data={data}
                                index={indexField}
                                categories={categories}
                                colors={colors as any}
                                valueFormatter={valueFormatter}
                                showYAxis={false}
                                showLegend={false}
                                startEndOnly={true}
                                className="!h-72 sm:hidden"
                            />
                        </>
                    )}
                </Card>
                <Card className="lg:col-span-1">
                    <ul
                        role="list"
                        className="divide-y divide-gray-200 dark:divide-gray-800"
                    >
                        {summary.map((item) => (
                            <li
                                key={item.name}
                                className="flex space-x-3 py-4 first:py-0 first:pb-4"
                            >
                                <span
                                    className={cx(item.bgColor, 'w-1 shrink-0 rounded')}
                                    aria-hidden={true}
                                />
                                <div className="flex w-full items-center justify-between space-x-4 truncate">
                                    <p className="truncate text-sm text-gray-500 dark:text-gray-500">
                                        {item.name}
                                    </p>
                                    <p className="font-medium text-gray-900 dark:text-gray-50">
                                        {item.value}
                                    </p>
                                </div>
                            </li>
                        ))}
                    </ul>
                    <button
                        type="button"
                        className="mt-4 inline-flex items-center gap-1.5 whitespace-nowrap py-2 text-sm font-medium text-blue-500 hover:text-blue-600 dark:text-blue-500 dark:hover:text-blue-600"
                        onClick={onCompare}
                    >
                        <RiAddFill className="size-5 shrink-0" aria-hidden={true} />
                        {compareLabel}
                    </button>
                </Card>
            </div>
        </div>
    );
};

// Example usage with sample data
