import React from 'react';

import { AvailableChartColorsKeys } from '../../lib/chartUtils';
import { cx } from '../../lib/utils';
import { BarChart } from '../../tremor/components/BarChart';
import { Card } from '../../tremor/components/Card';
import { defaultCurrencyFormatter } from '../../lib/financeFormatters';

export interface BarChartDataItem {
    [key: string]: string | number;
}

export interface SummaryMetric {
    name: string;
    total: number;
    color: string;
}

export interface BarChart08Props {
    data?: BarChartDataItem[];
    summary?: SummaryMetric[];
    categories?: string[];
    colors?: AvailableChartColorsKeys[];
    type?: 'default' | 'stacked' | 'percent';
    indexField?: string;
    valueFormatter?: (value: number) => string;
    title: string;
    description: string;
    /** Optional link for "Learn more". If provided, the link is shown. */
    learnMoreLink?: string;
  className?: string;
}

export const BarChart08: React.FC<BarChart08Props> = ({
    data = [],
    summary = [],
    categories = [],
    colors = ['blue', 'red'] as AvailableChartColorsKeys[],
    type = 'stacked' as const,
    indexField = 'date',
    valueFormatter = defaultCurrencyFormatter,
    title,
    description,
    learnMoreLink,

    className
}) => {
    return (
        <Card className={cx('!p-0', className)}>
            <div className="p-6">
                <h3 className="font-medium text-gray-900 dark:text-gray-50">
                    {title}
                </h3>
                <p className="mt-1 text-sm/6 text-gray-500 dark:text-gray-500">
                    {description}
                    {learnMoreLink && (
                        <a
                            href={learnMoreLink}
                            className="inline-flex items-center gap-1 text-sm text-blue-500 dark:text-blue-500"
                        >
                            Learn more
                        </a>
                    )}
                </p>
            </div>
            <div className="border-t border-gray-200 p-6 dark:border-gray-900">
                <ul role="list" className="flex flex-wrap gap-x-20 gap-y-10">
                    {summary.map((item) => (
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
                    data={data}
                    index={indexField}
                    categories={categories}
                    colors={colors as AvailableChartColorsKeys[]}
                    type={type}
                    showLegend={false}
                    yAxisWidth={50}
                    showGridLines={true}
                    valueFormatter={valueFormatter}
                    className="mt-10 !h-72"
                />
            </div>
        </Card>
    );
};
