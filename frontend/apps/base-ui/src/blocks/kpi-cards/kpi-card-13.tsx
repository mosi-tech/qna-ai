'use client';

import React from 'react';
import { MetricItem, CommonFormattingProps } from './index';
import { Card } from '../../tremor/components/Card';
import { ProgressCircle } from '../../tremor';
import { cx } from '../../lib/utils';

export interface KpiCard13Props extends CommonFormattingProps {
    metrics?: MetricItem[];
    cols?: number;
    valueFormatter?: (value: number | string) => string;
  className?: string;
}

export interface BudgetMetricItem extends MetricItem {
    progress?: number;
    budget?: string;
    current?: string;
    href?: string;
}

const BudgetCard: React.FC<{ item: BudgetMetricItem }> = ({ item }) => {
    const Component = item.href ? 'a' : 'div';

    return (
        <Card className="!p-0">
            <Component
                href={item.href}
                className={item.href ? 'block no-underline focus:outline-none' : ''}
            >
                <div className="flex items-center space-x-3 px-6 pt-6">
                    <ProgressCircle value={item.progress || 0} radius={25} strokeWidth={5}>
                        <span className="text-xs font-medium text-gray-900 dark:text-gray-50">
                            {item.progress}&#37;
                        </span>
                    </ProgressCircle>
                    <div>
                        <dd className="text-sm font-medium text-gray-900 dark:text-gray-50">
                            {item.current} / {item.budget}
                        </dd>
                        <dt className="text-sm text-gray-500 dark:text-gray-500">
                            Budget {item.name}
                        </dt>
                    </div>
                </div>
                <div className="mt-8 flex items-center justify-end border-t border-gray-200 px-6 py-3 dark:border-gray-900">
                    <span className="text-sm font-medium text-blue-500 dark:text-blue-500">
                        View more &#8594;
                    </span>
                </div>
            </Component>
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

export const KpiCard13: React.FC<KpiCard13Props> = ({
    metrics = [],
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
                <BudgetCard item={item as BudgetMetricItem} />
            )}
            cols={cols}
        />
    );
};
