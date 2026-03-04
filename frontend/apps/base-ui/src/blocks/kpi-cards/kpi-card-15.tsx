'use client';

import React from 'react';
import { MetricItem, CommonFormattingProps } from './index';
import { Card } from '../../tremor/components/Card';
import { ProgressBar } from '../../tremor';
import { cx } from '../../lib/utils';

export interface KpiCard15Props extends CommonFormattingProps {
    metrics?: MetricItem[];
    cols?: number;
    valueFormatter?: (value: number | string) => string;
    className?: string;
}

export interface QuotaMetricItem extends MetricItem {
    limit?: string;
    percentage?: number;
}

const QuotaCard: React.FC<{ item: QuotaMetricItem; valueSizeClass: string }> = ({ item, valueSizeClass }) => {
    const percentage = item.percentage ?? 0;

    return (
        <Card className={valueSizeClass === 'text-xl' ? 'p-3' : valueSizeClass === 'text-2xl' ? 'p-4' : ''}>
            <dt className="text-sm text-gray-500 dark:text-gray-500">
                {item.name}
            </dt>
            <dd className={cx(valueSizeClass, 'font-semibold text-gray-900 dark:text-gray-50')}>
                {item.stat}
            </dd>
            <ProgressBar value={percentage} className="mt-6" />
            <dd className="mt-2 flex items-center justify-between text-sm">
                <span className="text-blue-500 dark:text-blue-500">
                    {percentage}&#37;
                </span>
                <span className="text-gray-500 dark:text-gray-500">
                    {item.stat} of {item.limit}
                </span>
            </dd>
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

export const KpiCard15: React.FC<KpiCard15Props> = ({
    metrics = [],
    cols = 3,
    valueFormatter,

    className
}) => {
    if (!metrics || metrics.length === 0) {
        return null;
    }
    const valueSizeClass = cols >= 5 ? 'text-xl' : cols === 4 ? 'text-2xl' : 'text-3xl';

    return (
        <MetricCardGrid
            className={className}
            items={metrics}
            renderCard={(item) => (
                <QuotaCard item={item as QuotaMetricItem} valueSizeClass={valueSizeClass} />
            )}
            cols={cols}
        />
    );
};
