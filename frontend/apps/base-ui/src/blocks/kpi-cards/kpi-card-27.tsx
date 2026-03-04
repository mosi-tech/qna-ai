'use client';

import React from 'react';
import { CommonFormattingProps } from './index';
import { Card } from '../../tremor/components/Card';
import { LineChart } from '../../tremor/components/LineChart';
import { cx } from '../../lib/utils';

export interface ChartDataPoint {
    time: string;
    [key: string]: string | number;
}

export interface ChartMetric {
    title: string;
    labels: { [key: string]: string };
    values: { [key: string]: number | string };
    data: ChartDataPoint[];
    categories: string[];
    colors: string[];
}

export interface KpiCard27Props extends CommonFormattingProps {
    metrics?: ChartMetric[];
    valueFormatter?: (value: number | string) => string;
  className?: string;
}

export const KpiCard27: React.FC<KpiCard27Props> = ({ metrics = [], valueFormatter ,
    className
}) => {
    if (!metrics || metrics.length === 0) {
        return null;
    }

    return (
        <div className={cx('obfuscate', className)}>
            <dl className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {metrics.map((metric) => (
                    <Card key={metric.title}>
                        <dt className="text-sm font-medium text-gray-900 dark:text-gray-50">
                            {metric.title}
                        </dt>
                        <div className="mt-4 flex items-center gap-x-8 gap-y-4">
                            <dd className="space-y-3 whitespace-nowrap">
                                {Object.entries(metric.labels).map(([key, label]) => (
                                    <div key={key}>
                                        <div className="flex items-center gap-2">
                                            <span
                                                className={`size-2.5 shrink-0 rounded-sm bg-${metric.categories.indexOf(key) === 0
                                                    ? 'blue-500 dark:bg-blue-500'
                                                    : 'gray-500 dark:bg-gray-500'
                                                    }`}
                                                aria-hidden="true"
                                            />
                                            <span className="text-sm text-gray-900 dark:text-gray-50">
                                                {label}
                                            </span>
                                        </div>
                                        <span className="mt-1 block text-2xl font-semibold text-gray-900 dark:text-gray-50">
                                            {metric.values[key]}
                                        </span>
                                    </div>
                                ))}
                            </dd>
                            <LineChart
                                className="h-28"
                                data={metric.data}
                                index="time"
                                categories={metric.categories}
                                colors={metric.colors as any}
                                showTooltip={false}
                                valueFormatter={(number: number) =>
                                    Intl.NumberFormat('us').format(number).toString()
                                }
                                startEndOnly={true}
                                showYAxis={false}
                                showLegend={false}
                            />
                        </div>
                    </Card>
                ))}
            </dl>
        </div>
    );
};
