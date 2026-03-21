'use client';

import React from 'react';
import { MetricItem, CommonFormattingProps } from './index';
import { Card } from '../../tremor/components/Card';
import { SparkAreaChart } from '../../tremor/components/SparkChart';
import { cx } from '../../lib/utils';

export interface KpiCard14Props extends CommonFormattingProps {
    metrics?: MetricItem[];
    chartData?: Array<{ [key: string]: string | number }>;
    cols?: number;
    valueFormatter?: (value: number | string) => string;
  className?: string;
}

export interface StockMetricItem extends MetricItem {
    tickerSymbol?: string;
    value?: string;
    change?: string;
    percentageChange?: string;
    changeType?: 'positive' | 'negative';
}

const StockCard: React.FC<{
    item: StockMetricItem;
    chartData: Array<{ [key: string]: string | number }>;
}> = ({ item, chartData }) => {
    return (
        <Card>
            <dt className="text-sm font-medium text-gray-900 dark:text-gray-50">
                {item.name}{' '}
                <span className="font-normal">({item.tickerSymbol})</span>
            </dt>
            <div className="mt-1 flex items-baseline justify-between">
                <dd
                    className={cx(
                        item.changeType === 'positive'
                            ? 'text-emerald-700 dark:text-emerald-500'
                            : 'text-red-700 dark:text-red-500',
                        'text-lg font-semibold',
                    )}
                >
                    {item.value}
                </dd>
                <dd className="flex items-center space-x-1 text-sm">
                    <span className="font-medium text-gray-900 dark:text-gray-50">
                        {item.change}
                    </span>
                    <span
                        className={cx(
                            item.changeType === 'positive'
                                ? 'text-emerald-700 dark:text-emerald-500'
                                : 'text-red-700 dark:text-red-500',
                        )}
                    >
                        ({item.percentageChange})
                    </span>
                </dd>
            </div>
            <SparkAreaChart
                data={chartData}
                index="date"
                categories={[item.name]}
                colors={item.changeType === 'positive' ? ['emerald'] : ['red']}
                fill="solid"
                className="mt-4 h-16 w-full"
            />
        </Card>
    );
};

const MetricCardGrid: React.FC<{
    items: MetricItem[];
    renderCard: (item: MetricItem) => React.ReactNode;
    cols?: number;
    className?: string;
}> = ({ items, renderCard, cols = 3, className = '' }) => {
    const gridColsClass =
        cols === 1
            ? 'grid-cols-1'
            : cols === 2
                ? 'grid-cols-1 sm:grid-cols-2'
                : cols === 4
                    ? 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4'
                    : cols === 5
                        ? 'grid-cols-1 sm:grid-cols-3 lg:grid-cols-5'
                        : 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3';

    return (
        <dl className={cx('grid gap-6', gridColsClass, className)}>
            {items.map((item, index) => (
                <div key={`${item.name}-${index}`}>{renderCard(item)}</div>
            ))}
        </dl>
    );
};

export const KpiCard14: React.FC<KpiCard14Props> = ({
    metrics = [],
    chartData = [],
    cols = 3,
    valueFormatter,

    className
}) => {
    if (!metrics || metrics.length === 0) {
        return null;
    }

    return (
        <MetricCardGrid
                className={className}
            items={metrics}
            renderCard={(item) => (
                <StockCard
                    item={item as StockMetricItem}
                    chartData={chartData}
                />
            )}
            cols={cols}
        />
    );
};
