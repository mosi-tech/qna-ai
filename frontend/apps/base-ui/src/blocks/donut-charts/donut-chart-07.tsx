import React from 'react';
import { DonutChart } from '../../tremor';
import { type AvailableChartColorsKeys } from '../../lib/chartUtils';
import { cx } from '../../lib/utils';

export interface DataItem {
    name: string;
    value: number;
    share?: string;
    href?: string;
    borderColor?: string;
    [key: string]: any;
}

export interface DonutChart07Props {
    title: string;
    data: DataItem[];
    totalValue?: number;
    totalLabel?: string;
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

export const DonutChart07: React.FC<DonutChart07Props> = ({
    title,
    data,
    totalValue,
    totalLabel = 'Total asset value',
    colors = ['blue', 'violet', 'fuchsia'] as const,
    showLabel = false,
    showTooltip = false,
    chartClassName = '!h-20 !w-20',
    valueFormatter = defaultCurrencyFormatter,

    className
}) => {
    const displayTotal = totalValue || data.reduce((sum, item) => sum + item.value, 0);

    return (
        <div className={cx('max-w-7xl', className)}>
            <h3 className="text-sm font-medium text-gray-900 dark:text-gray-50">
                {title}
            </h3>
            <div className="mt-6 lg:flex lg:items-end lg:justify-between">
                <div className="flex items-center justify-start space-x-4 lg:items-end">
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
                    <div>
                        <p className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                            {valueFormatter(displayTotal)}
                        </p>
                        <p className="text-sm text-gray-500 dark:text-gray-500">
                            {totalLabel}
                        </p>
                    </div>
                </div>
                <ul
                    role="list"
                    className="mt-6 grid grid-cols-1 gap-px bg-gray-200 dark:bg-gray-800 lg:mt-0 lg:grid-cols-3"
                >
                    {data.map((item) => (
                        <li
                            key={item.name}
                            className="bg-white px-0 py-3 dark:bg-gray-950 lg:px-4 lg:py-0 lg:text-right"
                        >
                            <p className="text-sm font-semibold text-gray-900 dark:text-gray-50">
                                {valueFormatter(item.value)}{' '}
                                {item.share && <span className="font-normal">({item.share})</span>}
                            </p>
                            <div className="flex items-center space-x-2 lg:justify-end">
                                <span
                                    className={cx(
                                        item.borderColor || 'bg-gray-300 dark:bg-gray-600',
                                        'size-2.5 shrink-0 rounded-sm',
                                    )}
                                    aria-hidden={true}
                                />
                                <p className="text-sm text-gray-500 dark:text-gray-500">
                                    {item.name}
                                </p>
                            </div>
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
};
