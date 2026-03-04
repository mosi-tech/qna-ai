import React from 'react';
import { DonutChart } from '../../tremor';
import { type AvailableChartColorsKeys } from '../../lib/chartUtils';
import { Card } from '../../tremor/components/Card';
import { cx } from '../../lib/utils';

export interface DataItem {
    name: string;
    value: number;
    share?: string;
    href?: string;
    borderColor?: string;
    [key: string]: any;
}

export interface DonutChart06Props {
    title: string;
    description?: string;
    data: DataItem[];
    colors?: AvailableChartColorsKeys[];
    showLabel?: boolean;
    showTooltip?: boolean;
    chartClassName?: string;
    valueFormatter?: (value: number) => string;
  className?: string;
}

const defaultCurrencyFormatter = (number: number) => {
    return '$' + Intl.NumberFormat('us').format(number).toString();
};

export const DonutChart06: React.FC<DonutChart06Props> = ({
    title,
    description,
    data,
    colors = ['blue', 'violet', 'fuchsia'] as const,
    showLabel = true,
    showTooltip = false,
    chartClassName = 'mx-auto h-40',
    valueFormatter = defaultCurrencyFormatter,

    className
}) => {
    return (
        <Card className={cx('sm:mx-auto sm:max-w-xl', className)}>
            <h3 className="text-sm font-medium text-gray-900 dark:text-gray-50">
                {title}
            </h3>
            {description && (
                <p className="mt-1 text-sm/6 text-gray-500 dark:text-gray-500">
                    {description}
                </p>
            )}
            <div className="mt-6 grid grid-cols-1 gap-0 sm:grid-cols-2 sm:gap-8">
                <DonutChart
                    data={data}
                    value="value"
                    category="name"
                    valueFormatter={valueFormatter}
                    showTooltip={showTooltip}
                    className={chartClassName}
                    showLabel={showLabel}
                    colors={colors as AvailableChartColorsKeys[]}
                />
                <div className="mt-6 flex items-center sm:mt-0">
                    <ul role="list" className="space-y-3">
                        {data.map((item) => (
                            <li key={item.name} className="flex space-x-3">
                                <span
                                    className={cx(item.borderColor || 'bg-gray-300 dark:bg-gray-600', 'w-1 shrink-0 rounded')}
                                />
                                <div>
                                    <p className="text-sm font-medium text-gray-900 dark:text-gray-50">
                                        {valueFormatter(item.value)}{' '}
                                        {item.share && <span className="font-normal">({item.share})</span>}
                                    </p>
                                    <p className="mt-0.5 whitespace-nowrap text-sm text-gray-500 dark:text-gray-500">
                                        {item.name}
                                    </p>
                                </div>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        </Card>
    );
};
