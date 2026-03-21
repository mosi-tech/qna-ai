'use client';

import React from 'react';
import { CommonFormattingProps } from './index';
import type { SparkMetricItem } from './kpi-card-17';
export type { SparkMetricItem };
import { AreaChart, TooltipProps } from '../../tremor/components/AreaChart';
import { Card } from '../../tremor/components/Card';
import { cx } from '../../lib/utils';

const defaultNumberFormatter = (number: number) =>
    Intl.NumberFormat('en-US').format(number).toString();

const defaultCurrencyFormatter = (number: number) =>
    `$${Intl.NumberFormat('en-US').format(number)}`;

function formatChange(
    currentValue: number | undefined,
    previousValue: number | undefined,
    absFormatter: (n: number) => string,
) {
    if (
        currentValue === undefined ||
        previousValue === undefined ||
        isNaN(currentValue) ||
        isNaN(previousValue)
    ) {
        return '--';
    }
    const percentageChange =
        ((currentValue - previousValue) / previousValue) * 100;
    const absoluteChange = currentValue - previousValue;

    const formattedPercentage = `${percentageChange > 0 ? '+' : ''}${percentageChange.toFixed(1)}%`;
    const sign = absoluteChange >= 0 ? '+' : '-';
    const formattedAbsolute = `${sign}${absFormatter(Math.abs(absoluteChange))}`;

    return `${formattedPercentage} (${formattedAbsolute})`;
}

export interface KpiCard19Props extends CommonFormattingProps {
    /** Time-series rows, e.g. [{date:'Jan 26',nav:1200000,pnl:45000}] */
    chartData?: Record<string, string | number>[];
    /** One entry per card; one KPI card is rendered per metric */
    metrics?: SparkMetricItem[];
    /** Key used for the X-axis and the date label. Default: 'date' */
    indexField?: string;
    /** Grid column count. Default: 3 */
    cols?: number;
    className?: string;
}

interface KpiCardItemProps {
    item: SparkMetricItem;
    chartData: Record<string, string | number>[];
    indexField: string;
    valueSizeClass: string;
}

function KpiCardItem({ item, chartData, indexField, valueSizeClass }: KpiCardItemProps) {
    const [selectedChartData, setSelectedChartData] =
        React.useState<TooltipProps | null>(null);

    const formatter = item.valueFormatter ?? defaultNumberFormatter;
    const deltaFmt = item.deltaFormatter ?? item.valueFormatter ?? defaultCurrencyFormatter;

    const lastDataItem = chartData.length > 0 ? chartData[chartData.length - 1] : null;
    const payload = selectedChartData?.payload[0];
    const currentDataItem = payload ? payload.payload : lastDataItem;

    const value =
        currentDataItem != null
            ? (currentDataItem[item.chartCategory] as number)
            : undefined;

    const currentIndex = chartData.findIndex(
        (e) => e[indexField] === currentDataItem?.[indexField],
    );
    const previousDataItem =
        currentIndex > 0 ? chartData[currentIndex - 1] : undefined;
    const prevValue = previousDataItem
        ? (previousDataItem[item.chartCategory] as number)
        : undefined;

    const formattedValue =
        value !== undefined
            ? formatter(value)
            : item.stat !== undefined
                ? String(item.stat)
                : '--';

    const changeStr = formatChange(value, prevValue, deltaFmt);
    const isPositive = value !== undefined && prevValue !== undefined && value > prevValue;
    const isNeutral = changeStr === '--';

    return (
        <Card className={cx('sm:mx-auto sm:max-w-lg', valueSizeClass === 'text-xl' ? 'p-3' : valueSizeClass === 'text-2xl' ? 'p-4' : '')}>
            <dt className="text-sm text-gray-500 dark:text-gray-500">{item.name}</dt>
            <dd className={cx(valueSizeClass, 'mt-2 font-semibold text-gray-900 dark:text-gray-50')}>
                {formattedValue}
            </dd>
            <dd className="mt-1 flex items-baseline justify-between">
                <span className="text-sm text-gray-500 dark:text-gray-500">
                    On {currentDataItem ? String(currentDataItem[indexField] ?? '') : ''}
                </span>
                <span
                    className={cx(
                        'rounded-md p-2 text-sm font-medium',
                        isNeutral
                            ? 'text-gray-700 dark:text-gray-300'
                            : isPositive
                                ? 'text-emerald-700 dark:text-emerald-500'
                                : 'text-red-700 dark:text-red-500',
                    )}
                >
                    {changeStr}
                </span>
            </dd>
            {chartData.length > 0 && (
                <AreaChart
                    className="mt-8 h-28"
                    data={chartData}
                    index={indexField}
                    categories={[item.chartCategory]}
                    showLegend={false}
                    showYAxis={false}
                    showTooltip={false}
                    showGridLines={false}
                    startEndOnly={true}
                    fill="solid"
                    tooltipCallback={(props) => {
                        if (props.active) {
                            setSelectedChartData((prev) => {
                                if (prev?.label === props.label) return prev;
                                return props;
                            });
                        } else {
                            setSelectedChartData(null);
                        }
                        return null;
                    }}
                />
            )}
        </Card>
    );
}

export const KpiCard19: React.FC<KpiCard19Props> = ({
    chartData = [],
    metrics = [],
    indexField = 'date',
    cols = 3,
    className,
}) => {
    const gridColsClass =
        cols === 1
            ? 'grid-cols-1'
            : cols === 2
                ? 'grid-cols-1 sm:grid-cols-2'
                : 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3';
    const valueSizeClass = cols >= 5 ? 'text-xl' : cols === 4 ? 'text-2xl' : 'text-3xl';

    return (
        <dl className={cx('grid gap-6', gridColsClass, className)}>
            {metrics.map((item) => (
                <KpiCardItem
                    key={item.name}
                    item={item}
                    chartData={chartData}
                    indexField={indexField}
                    valueSizeClass={valueSizeClass}
                />
            ))}
        </dl>
    );
};
