import React from 'react';
import { AvailableChartColorsKeys } from '../../lib/chartUtils';
import { BarChart } from '../../tremor/components/BarChart';
import { cx } from '../../lib/utils';

export interface BarChartDataItem {
    [key: string]: string | number;
}

export interface BarChart12Props {
    data?: BarChartDataItem[];
    title: string;
    description: string;
    indexField?: string;
    categories?: string[];
    colors?: AvailableChartColorsKeys[];
    type?: 'default' | 'stacked' | 'percent';
    /** Y-axis label (e.g., "% of criteria addressed", "Return %", etc.) - optional */
    yAxisLabel?: string;
    barCategoryGap?: string;
    valueFormatter?: (value: number) => string;
  className?: string;
}

export const BarChart12: React.FC<BarChart12Props> = ({
    data = [],
    title,
    description,
    indexField = 'date',
    categories = [],
    colors = [],
    type = 'default',
    yAxisLabel,
    barCategoryGap,
    valueFormatter = (value: number) => `${value}`,

    className
}) => {
    // Use provided categories/colors or derive from data
    const finalCategories = categories.length > 0 ? categories : data[0] ? Object.keys(data[0]).filter(k => k !== indexField) : [];
    const finalColors: AvailableChartColorsKeys[] = colors.length > 0 ? colors : (finalCategories.length > 0 ? finalCategories.map(() => 'blue' as AvailableChartColorsKeys) : []);
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
                categories={finalCategories}
                colors={finalColors}
                type={type}
                yAxisWidth={55}
                yAxisLabel={yAxisLabel}
                barCategoryGap={barCategoryGap}
                className="mt-4 hidden h-60 md:block"
            />
            <BarChart
                data={data}
                index={indexField}
                categories={finalCategories}
                colors={finalColors}
                type={type}
                showYAxis={false}
                barCategoryGap={barCategoryGap}
                className="mt-4 h-60 md:hidden"
            />
        </div>
    );
};
