'use client';

import React from 'react';
import { CommonFormattingProps } from './index';
import { AreaChart, TooltipProps } from '../../tremor/components/AreaChart';
import { Card } from '../../tremor/components/Card';
import { cx } from '../../lib/utils';

const defaultNumberFormatter = (number: number) =>
    Intl.NumberFormat('en-US').format(number).toString();

export interface SparkMetricItem {
    /** Card label / metric name */
    name: string;
    /** Optional static display value override (used when chartData is empty) */
    stat?: string | number;
    /** Key in chartData rows to plot on the AreaChart and to display as the card value */
    chartCategory: string;
    /** Per-metric number formatter */
    valueFormatter?: (n: number) => string;
    /** Per-metric formatter for the absolute delta in the change badge (kpi-card-19; defaults to valueFormatter) */
    deltaFormatter?: (n: number) => string;
}

export interface KpiCard17Props extends CommonFormattingProps {
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

const KpiCardItem = ({ item, chartData, indexField }: KpiCardItemProps) => {
    const [selectedChartData, setSelectedChartData] =
        React.useState<TooltipProps | null>(null);

    const formatter = item.valueFormatter ?? defaultNumberFormatter;
    const payload = selectedChartData?.payload[0];
    const displayRow = payload
        ? payload.payload
        : chartData.length > 0
            ? chartData[chartData.length - 1]
            : null;

    const rawValue = displayRow != null ? displayRow[item.chartCategory] : undefined;
    const formattedValue =
        rawValue !== undefined
            ? formatter(rawValue as number)
            : item.stat !== undefined
                ? String(item.stat)
                : '--';

    return (
        <Card>
            <dt className="text-sm text-gray-500 dark:text-gray-500">{item.name}</dt>
            <dd className="mt-1 flex items-baseline justify-between">
                <span className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                    {formattedValue}
                </span>
                <span className="text-sm text-gray-500 dark:text-gray-500">
                    {displayRow ? String(displayRow[indexField] ?? '') : ''}
                </span>
            </dd>
            {chartData.length > 0 && (
                <AreaChart
                    data={chartData}
                    index={indexField}
                    categories={[item.chartCategory]}
                    showLegend={false}
                    showTooltip={false}
                    showYAxis={false}
                    showGridLines={false}
                    startEndOnly={true}
                    fill="solid"
                    className="-mb-2 mt-3 h-32"
                    tooltipCallback={(props) => {
                        if (props.active) {
                            setSelectedChartData((prev) =>
                                prev?.label === props.label ? prev : props,
                            );
                        } else {
                            setSelectedChartData(null);
                        }
                        return null;
                    }}
                />
            )}
        </Card>
    );
};

export const KpiCard17: React.FC<KpiCard17Props> = ({
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
