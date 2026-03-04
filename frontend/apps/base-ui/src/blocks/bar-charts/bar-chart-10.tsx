import React from 'react';
import { AvailableChartColorsKeys } from '../../lib/chartUtils';
import { BarChart } from '../../tremor/components/BarChart';
import { Card } from '../../tremor/components/Card';
import { cx } from '../../lib/utils';

export interface BarChartDataItem {
    date: string;
    [key: string]: string | number;
}

export interface MetricConfig {
    title: string;
    description: string;
    data: BarChartDataItem[];
    metric: string;
    color: AvailableChartColorsKeys;
    value: string;
}

export interface BarChart10Props {
    metrics?: MetricConfig[];
    valueFormatter?: (value: number) => string;
  className?: string;
}

export const BarChart10: React.FC<BarChart10Props> = ({
    metrics = [],
    valueFormatter = (number: number) =>
        `${Intl.NumberFormat('us').format(number).toString()}`,

    className
}) => {
    return (
        <Card className={cx('mx-auto flex max-w-4xl flex-col gap-6', className)}>
            {metrics.map((metric) => (
                <div key={metric.title}>
                    <h1 className="text-sm text-gray-600 dark:text-gray-400">{metric.title}</h1>
                    <p className={`text-2xl font-semibold text-${metric.color}-500 dark:text-${metric.color}-500`}>
                        {metric.value}
                    </p>
                    <BarChart
                        syncId="sync"
                        data={metric.data}
                        index="date"
                        categories={[metric.metric]}
                        showLegend={false}
                        colors={[metric.color]}
                        showYAxis={false}
                        showGridLines={false}
                        valueFormatter={valueFormatter}
                        className="mt-2 !h-36"
                    />
                </div>
            ))}
        </Card>
    );
};
