import React from 'react';
import { AvailableChartColorsKeys } from '../../lib/chartUtils';
import { BarChart } from '../../tremor/components/BarChart';
import { cx } from '../../lib/utils';

export interface BarChartDataItem {
    [key: string]: string | number;
}

export interface BarChart11Props {
    data?: BarChartDataItem[];
    title: string;
    description: string;
    metric?: string;
    indexField?: string;
    colors?: AvailableChartColorsKeys[];
    yAxisLabel?: string;
    barCategoryGap?: string;
    valueFormatter?: (value: number) => string;
  className?: string;
}

export const formatPercentage = ({ number, decimals }: { number: number; decimals: number }) =>
    `${(number * 100).toFixed(decimals)}%`;

export const BarChart11: React.FC<BarChart11Props> = ({
    data = [],
    title,
    description,
    metric = 'Density',
    indexField = 'date',
    colors = ['amber'] as AvailableChartColorsKeys[],
    yAxisLabel = 'Competition density (%)',
    barCategoryGap = '30%',
    valueFormatter = (value: number) =>
        formatPercentage({ number: value, decimals: 0 }),

    className
}) => {
    return (
        <div className={cx('flex flex-col justify-between', className)}>
            <div>
                <dt className="text-sm font-semibold text-gray-900 dark:text-gray-50">
                    {title}
                </dt>
                <dd className="mt-0.5 text-sm/6 text-gray-500 dark:text-gray-500">
                    {description}
                </dd>
            </div>
            <BarChart
                data={data}
                index={indexField}
                categories={[metric]}
                colors={colors}
                valueFormatter={valueFormatter}
                yAxisWidth={55}
                yAxisLabel={yAxisLabel}
                barCategoryGap={barCategoryGap}
                className="mt-4 hidden h-60 md:block"
            />
            <BarChart
                data={data}
                index={indexField}
                categories={[metric]}
                colors={colors}
                valueFormatter={valueFormatter}
                showYAxis={false}
                barCategoryGap={barCategoryGap}
                className="mt-4 h-60 md:hidden"
            />
        </div>
    );
};
