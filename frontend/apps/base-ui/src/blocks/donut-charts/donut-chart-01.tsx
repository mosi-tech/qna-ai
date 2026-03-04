import React from 'react';
import { DonutChart } from '../../tremor';
import { type AvailableChartColorsKeys } from '../../lib/chartUtils';
import { Card } from '../../tremor/components/Card';
import { cx } from '../../lib/utils';

export interface DataItem {
    name: string;
    value: number;
    share?: string;
    color?: string;
    [key: string]: any;
}

export interface DonutChart01Props {
    title: string;
    data: DataItem[];
    colors?: AvailableChartColorsKeys[];
    showLabel?: boolean;
    showTooltip?: boolean;
    categoryLabel?: string;
    amountLabel?: string;
    valueFormatter?: (value: number) => string;
  className?: string;
}

const defaultCurrencyFormatter = (number: number) =>
    '$' + Intl.NumberFormat('us').format(number).toString();

export const DonutChart01: React.FC<DonutChart01Props> = ({
    title,
    data,
    colors = ['cyan', 'blue', 'emerald', 'violet', 'fuchsia'] as const,
    showLabel = true,
    showTooltip = false,
    categoryLabel = 'Category',
    amountLabel = 'Amount / Share',
    valueFormatter = defaultCurrencyFormatter,

    className
}) => {
    return (
        <Card className={cx('sm:mx-auto sm:max-w-lg', className)}>
            <h3 className="text-sm font-medium text-gray-900 dark:text-gray-50">
                {title}
            </h3>
            <DonutChart
                className="mx-auto mt-8"
                data={data}
                category="name"
                value="value"
                showLabel={showLabel}
                valueFormatter={valueFormatter}
                showTooltip={showTooltip}
                colors={colors as AvailableChartColorsKeys[]}
            />
            <p className="mt-8 flex items-center justify-between text-xs text-gray-500 dark:text-gray-500">
                <span>{categoryLabel}</span>
                <span>{amountLabel}</span>
            </p>
            <ul
                role="list"
                className="mt-2 divide-y divide-gray-200 text-sm text-gray-500 dark:divide-gray-800 dark:text-gray-500"
            >
                {data.map((item) => (
                    <li
                        key={item.name}
                        className="relative flex items-center justify-between py-2"
                    >
                        <div className="flex items-center space-x-2.5 truncate">
                            <span
                                className={cx(
                                    item.color || 'bg-gray-300 dark:bg-gray-600',
                                    'size-2.5 shrink-0 rounded-sm'
                                )}
                                aria-hidden={true}
                            />
                            <span className="truncate dark:text-gray-300">
                                {item.name}
                            </span>
                        </div>
                        <p className="flex items-center space-x-2">
                            <span className="font-medium tabular-nums text-gray-900 dark:text-gray-50">
                                {valueFormatter(item.value)}
                            </span>
                            {item.share && (
                                <span className="rounded-md bg-gray-100 px-1.5 py-0.5 text-xs font-medium tabular-nums text-gray-700 dark:bg-gray-800 dark:text-gray-300">
                                    {item.share}
                                </span>
                            )}
                        </p>
                    </li>
                ))}
            </ul>
        </Card>
    );
};
