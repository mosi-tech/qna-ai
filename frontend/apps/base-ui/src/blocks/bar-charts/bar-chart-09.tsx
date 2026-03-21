import React from 'react';

import { AvailableChartColorsKeys } from '../../lib/chartUtils';
import { cx } from '../../lib/utils';

import { BarChart } from '../../tremor/components/BarChart';
import { Card } from '../../tremor/components/Card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../tremor/components/Tabs';

export interface BarChartDataItem {
    [key: string]: string | number;
}

export interface SummaryItem {
    name: string;
    total: number;
    color: string;
}

export interface TabConfig {
    name: string;
    data: BarChartDataItem[];
    categories: string[];
    colors: string[];
    type?: 'default' | 'stacked' | 'percent';
    summary: SummaryItem[];
    indexField?: string;
}

export interface BarChart09Props {
    tabs?: TabConfig[];
    valueFormatter?: (value: number) => string;
  className?: string;
}

export const BarChart09: React.FC<BarChart09Props> = ({
    tabs = [],
    valueFormatter = (number: number) =>
        `${Intl.NumberFormat('us').format(number).toString()}`,

    className
}) => {
    return (
        <Card className={cx('!p-0', className)}>
            <div className="p-6">
                <h3 className="font-medium text-gray-900 dark:text-gray-50">
                    Requests
                </h3>
                <p className="text-sm/6 text-gray-500 dark:text-gray-500">
                    Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam
                    nonumy eirmod tempor invidunt.{' '}
                    <a
                        href="#"
                        className="inline-flex items-center gap-1 text-sm text-blue-500 dark:text-blue-500"
                    >
                        Learn more
                    </a>
                </p>
            </div>
            <div className="border-t border-gray-200 p-6 dark:border-gray-900">
                <Tabs defaultValue={tabs[0]?.name || ''}>
                    <div className="md:flex md:items-center md:justify-between">
                        <TabsList variant="solid" className="w-full rounded-md md:w-60">
                            {tabs.map((tab) => (
                                <TabsTrigger key={tab.name} value={tab.name} className="w-full">
                                    {tab.name}
                                </TabsTrigger>
                            ))}
                        </TabsList>
                        <div className="hidden md:flex md:items-center md:space-x-2">
                            <span
                                className="shrink-0 animate-pulse rounded-full bg-emerald-500/30 p-1"
                                aria-hidden={true}
                            >
                                <span className="block size-2 rounded-full bg-emerald-500 dark:bg-emerald-500" />
                            </span>
                            <p className="mt-4 text-sm text-gray-500 dark:text-gray-500 md:mt-0">
                                Updated just now
                            </p>
                        </div>
                    </div>
                    {tabs.map((tab) => (
                        <TabsContent key={tab.name} value={tab.name}>
                            <ul role="list" className="mt-6 flex flex-wrap gap-x-20 gap-y-10">
                                {tab.summary.map((item) => (
                                    <li key={item.name}>
                                        <div className="flex items-center space-x-2">
                                            <span
                                                className={cx(item.color, 'size-3 shrink-0 rounded-sm')}
                                                aria-hidden={true}
                                            />
                                            <p className="font-semibold text-gray-900 dark:text-gray-50">
                                                {valueFormatter(item.total)}
                                            </p>
                                        </div>
                                        <p className="whitespace-nowrap text-sm text-gray-500 dark:text-gray-500">
                                            {item.name}
                                        </p>
                                    </li>
                                ))}
                            </ul>
                            <BarChart
                                data={tab.data}
                                index={tab.indexField || 'date'}
                                categories={tab.categories}
                                colors={tab.colors as AvailableChartColorsKeys[]}
                                type={tab.type || 'stacked'}
                                showLegend={false}
                                yAxisWidth={50}
                                showGridLines={true}
                                valueFormatter={valueFormatter}
                                className="mt-10 !h-72"
                            />
                        </TabsContent>
                    ))}
                </Tabs>
            </div>
        </Card>
    );
};
