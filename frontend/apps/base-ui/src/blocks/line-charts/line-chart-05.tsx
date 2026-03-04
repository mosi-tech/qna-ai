import React from 'react';
import { Card } from '../../tremor/components/Card';
import { LineChart } from '../../tremor/components/LineChart';
import { cx } from '../../lib/utils';

export interface LineChart05Props {
    data: Array<Record<string, any>>;
    description?: string;
    colors?: string[];
    categories?: string[];
    valueFormatter?: (num: number) => string;
    highlightCategory?: string;
    referenceLine?: { value: number; label: string };
    /** Key in the data objects used as the x-axis index. Defaults to 'date'. */
    indexField?: string;
  className?: string;
}

/**
 * LineChart05: Month-to-date cumulative data with reference line
 */
export const LineChart05: React.FC<LineChart05Props> = ({
    data,
    description = 'Customized chart using a month to date calculation',
    colors = ['lightGray', 'blue'],
    categories = ['lastMonth', 'currentMonth'],
    valueFormatter = (num) => Intl.NumberFormat('en').format(num),
    highlightCategory = 'currentMonth',
    referenceLine,
    indexField = 'date',

    className
}) => {
    return (
        <div className={cx('obfuscate', className)}>
            <p className="mb-4 text-center text-sm text-gray-500 dark:text-gray-500">
                {description}
            </p>
            <Card className="mx-auto max-w-2xl">
                <LineChart
                    referenceLine={referenceLine}
                    data={data}
                    valueFormatter={valueFormatter}
                    index={indexField}
                    colors={colors as any}
                    categories={categories}
                    connectNulls={false}
                    yAxisWidth={70}
                    highlightLastIndexCategory={highlightCategory}
                    className="hidden sm:block"
                />
                <LineChart
                    referenceLine={referenceLine}
                    data={data}
                    valueFormatter={valueFormatter}
                    index={indexField}
                    colors={colors as any}
                    categories={categories}
                    connectNulls={false}
                    showYAxis={false}
                    highlightLastIndexCategory={highlightCategory}
                    className="block sm:hidden"
                />
            </Card>
        </div>
    );
};

// Example usage with sample data
