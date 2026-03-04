import React from 'react';
import { AvailableChartColorsKeys } from '../../lib/chartUtils';
import { BarChart } from '../../tremor/components/BarChart';
import { Card } from '../../tremor/components/Card';
import { defaultCurrencyFormatter } from '../../lib/financeFormatters';
import { cx } from '../../lib/utils';

export interface BarChartDataItem {
    [key: string]: string | number;
}

export interface SummaryMetric {
    label: string;
    value: string;
    color: string;
    change?: string;
}

export interface BarChart03Props {
    data?: BarChartDataItem[];
    title: string;
    description: string;
    indexField?: string;
    categories?: string[];
    colors?: AvailableChartColorsKeys[];
    summary?: SummaryMetric[];
    valueFormatter?: (value: number) => string;
  className?: string;
}

export const BarChart03: React.FC<BarChart03Props> = ({
    data = [],
    title = 'Sales overview',
    description = 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr.',
    indexField = 'date',
    categories = ['Last Year', 'This Year'],
    colors = ['cyan', 'blue'] as AvailableChartColorsKeys[],
    summary = [
        { label: 'This year', value: '$0.8M', color: 'bg-blue-500 dark:bg-blue-500', change: '+16%' },
        { label: 'Last year', value: '$0.7M', color: 'bg-cyan-500 dark:bg-cyan-500' },
    ],
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
            <ul role="list" className="mt-6 flex gap-10">
                {summary.map((item, idx) => (
                    <li key={idx}>
                        <div className="flex items-center space-x-1.5">
                            <span
                                className={`size-2.5 rounded-sm ${item.color}`}
                                aria-hidden={true}
                            />
                            <p className="text-xs text-gray-500 dark:text-gray-500">
                                {item.label}
                            </p>
                        </div>
                        <div className="flex items-center space-x-1.5">
                            <p className="mt-0.5 text-lg font-semibold text-gray-900 dark:text-gray-50">
                                {item.value}
                            </p>
                            {item.change && (
                                <span className="rounded bg-gray-100 px-1.5 py-0.5 text-xs font-medium text-gray-600 dark:bg-gray-800 dark:text-gray-400">
                                    {item.change}
                                </span>
                            )}
                        </div>
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
                className="mt-8 hidden !h-56 sm:block"
            />
            <BarChart
                data={data}
                index={indexField}
                categories={categories}
                colors={colors as AvailableChartColorsKeys[]}
                showLegend={false}
                valueFormatter={valueFormatter}
                showYAxis={false}
                className="mt-8 !h-48 sm:hidden"
            />
        </Card>
    );
};
