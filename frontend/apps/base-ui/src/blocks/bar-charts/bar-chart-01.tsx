import React from 'react';
import { AvailableChartColorsKeys } from '../../lib/chartUtils';
import { BarChart } from '../../tremor/components/BarChart';
import { Card } from '../../tremor/components/Card';
import { Divider } from '../../tremor/components/Divider';
import { Label } from '../../tremor/components/Label';
import { Switch } from '../../tremor/components/Switch';
import { defaultCurrencyFormatter } from '../../lib/financeFormatters';
import { cx } from '../../lib/utils';

export interface BarChartDataItem {
    [key: string]: string | number;
}

export interface BarChart01Props {
    data?: BarChartDataItem[];
    title: string;
    description: string;
    indexField?: string;
    categories?: string[];
    colors?: AvailableChartColorsKeys[];
    valueFormatter?: (value: number) => string;
    /** Label for comparison toggle (e.g., "Show comparison period"). If not provided, defaults are used. */
    comparisonLabel?: string;
    /** Default categories when comparison is OFF */
    defaultCategories?: string[];
    /** Default categories when comparison is ON */
    comparisonCategories?: string[];
    /** Default colors when comparison is OFF */
    defaultColors?: AvailableChartColorsKeys[];
    /** Default colors when comparison is ON */
    comparisonColors?: AvailableChartColorsKeys[];
    className?: string;
}

export const BarChart01: React.FC<BarChart01Props> = ({
    data = [],
    title,
    description,
    indexField = 'date',
    categories,
    colors,
    valueFormatter = defaultCurrencyFormatter,
    comparisonLabel = 'Show same period last year',
    defaultCategories = ['This Year'],
    comparisonCategories = ['Last Year', 'This Year'],
    defaultColors = ['blue'] as AvailableChartColorsKeys[],
    comparisonColors = ['cyan', 'blue'] as AvailableChartColorsKeys[],

    className
}) => {
    const [showComparison, setShowComparison] = React.useState(false);

    const finalCategories = categories || (showComparison ? comparisonCategories : defaultCategories);
    const finalColors = colors || (showComparison ? comparisonColors : defaultColors);

    return (
        <Card className={cx(className)}>
            <h3 className="font-semibold text-gray-900 dark:text-gray-50">
                {title}
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-500">
                {description}
            </p>
            <BarChart
                data={data}
                index={indexField}
                categories={finalCategories as any}
                colors={finalColors as AvailableChartColorsKeys[]}
                valueFormatter={valueFormatter}
                yAxisWidth={50}
                className="mt-6 hidden h-60 sm:block"
            />
            <BarChart
                data={data}
                index={indexField}
                categories={finalCategories as any}
                colors={finalColors as AvailableChartColorsKeys[]}
                valueFormatter={valueFormatter}
                showYAxis={false}
                className="mt-4 !h-56 sm:hidden"
            />
            <Divider />
            <div className="mb-2 flex items-center space-x-3">
                <Switch
                    checked={showComparison}
                    onCheckedChange={setShowComparison}
                />
                <Label>{comparisonLabel}</Label>
            </div>
        </Card>
    );
};
