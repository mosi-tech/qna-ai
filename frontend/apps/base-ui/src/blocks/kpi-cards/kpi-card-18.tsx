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

function formatChange(
    currentValue: number | undefined,
    previousValue: number | undefined,
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
    return `${percentageChange > 0 ? '+' : ''}${percentageChange.toFixed(1)}%`;
}

export interface KpiCard18Props extends CommonFormattingProps {
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
}

function KpiCardItem({ item, chartData, indexField }: KpiCardItemProps) {
    const [selectedChartData, setSelectedChartData] =
        React.useState<TooltipProps | null>(null);

    const formatter = item.valueFormatter ?? defaultNumberFormatter;
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

    return (
        <Card className="sm:mx-auto sm:max-w-lg">
            <div className="flex items-baseline justify-between">
                <dt className="text-sm text-gray-500 dark:text-gray-500">
                    {item.name}
                </dt>
                <dd className="rounded-md bg-gray-100 px-1.5 py-0.5 text-sm text-gray-700 dark:bg-gray-800 dark:text-gray-300">
                    {formatChange(value, prevValue)}
                </dd>
            </div>
            <dd className="mt-2 flex items-baseline justify-between">
                <span className="font-semibold text-gray-900 dark:text-gray-50">
                    {formattedValue}
                </span>
                <span className="text-sm text-gray-500 dark:text-gray-500">
                    On {currentDataItem ? String(currentDataItem[indexField] ?? '') : ''}
                </span>
            </dd>
            {chartData.length > 0 && (
                <AreaChart
                    className="mt-8 h-20"
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

export const KpiCard18: React.FC<KpiCard18Props> = ({
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

    return (
        <dl className={cx('grid gap-6', gridColsClass, className)}>
            {metrics.map((item) => (
                <KpiCardItem
                    key={item.name}
                    item={item}
                    chartData={chartData}
                    indexField={indexField}
                />
            ))}
        </dl>
    );
};
