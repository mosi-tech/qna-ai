import React from 'react';
import { AvailableChartColorsKeys } from '../../lib/chartUtils';
import { cx } from '../../lib/utils';
import { BarChart } from '../../tremor/components/BarChart';
import { Card } from '../../tremor/components/Card';
import { defaultCurrencyFormatter } from '../../lib/financeFormatters';

export interface TabItem {
    name: string;
    value: string;
    color: string;
}

export interface BarChartDataItem {
    [key: string]: string | number;
}

export interface BarChart02Props {
    tabs?: TabItem[];
    data?: BarChartDataItem[];
    title: string;
    description: string;
    indexField?: string;
    categories?: string[];
    colors?: AvailableChartColorsKeys[];
    type?: 'default' | 'stacked' | 'percent';
    valueFormatter?: (value: number) => string;
  className?: string;
}

export const BarChart02: React.FC<BarChart02Props> = ({
    tabs = [],
    data = [],
    title = 'Sales breakdown by regions',
    description = 'Check sales of top 3 regions over time',
    indexField = 'date',
    categories = ['Europe', 'Asia', 'North America'],
    colors = ['blue', 'cyan', 'violet'] as AvailableChartColorsKeys[],
    type = 'stacked' as const,
    valueFormatter = defaultCurrencyFormatter,

    className
}) => {
    return (
        <Card className={cx('sm:mx-auto sm:max-w-2xl', className)}>
            <h3 className="font-semibold text-gray-900 dark:text-gray-50">
                {title}
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-500">
                {description}
            </p>
            <ul
                role="list"
                className="mt-6 grid gap-3 sm:grid-cols-2 md:grid-cols-3"
            >
                {tabs.map((tab) => (
                    <li
                        key={tab.name}
                        className="rounded-md border border-gray-200 px-3 py-2 text-left dark:border-gray-800"
                    >
                        <div className="flex items-center space-x-1.5">
                            <span
                                className={cx(tab.color, 'size-2.5 rounded-sm')}
                                aria-hidden={true}
                            />
                            <p className="text-xs text-gray-500 dark:text-gray-500">
                                {tab.name}
                            </p>
                        </div>
                        <p className="mt-0.5 font-semibold text-gray-900 dark:text-gray-50">
                            {tab.value}
                        </p>
                    </li>
                ))}
            </ul>
            <BarChart
                data={data}
                index={indexField}
                categories={categories}
                colors={colors as AvailableChartColorsKeys[]}
                showLegend={false}
                valueFormatter={valueFormatter}
                yAxisWidth={50}
                type={type}
                className="mt-6 hidden !h-56 sm:block"
            />
            <BarChart
                data={data}
                index={indexField}
                categories={categories}
                colors={colors as AvailableChartColorsKeys[]}
                showLegend={false}
                valueFormatter={valueFormatter}
                showYAxis={false}
                type={type}
                className="mt-6 !h-48 sm:hidden"
            />
        </Card>
    );
};
