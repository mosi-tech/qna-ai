'use client';

import React from 'react';
import { RiExternalLinkLine } from '@remixicon/react';
import { MetricItem, CommonFormattingProps } from './index';
import { Card } from '../../tremor/components/Card';
import { ProgressCircle } from '../../tremor';
import { cx } from '../../lib/utils';

export interface KpiCard12Props extends CommonFormattingProps {
    metrics?: MetricItem[];
    cols?: number;
    valueFormatter?: (value: number | string) => string;
  className?: string;
}

export interface PlanMetricItem extends MetricItem {
    capacity?: number;
    current?: number;
    allowed?: number;
}

const PlanCard: React.FC<{ item: PlanMetricItem }> = ({ item }) => {
    const capacity = item.capacity ?? 0;

    return (
        <Card>
            <div className="flex items-center space-x-3">
                <ProgressCircle value={capacity} radius={25} strokeWidth={5}>
                    <span className="text-xs font-medium text-gray-900 dark:text-gray-50">
                        {capacity}&#37;
                    </span>
                </ProgressCircle>
                <div>
                    <dt className="text-sm font-medium text-gray-900 dark:text-gray-50">
                        {item.name}
                    </dt>
                    <dd className="text-sm text-gray-500 dark:text-gray-500">
                        {item.current} of {item.allowed} used
                    </dd>
                </div>
            </div>
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

export const KpiCard12: React.FC<KpiCard12Props> = ({
    metrics = [],
    cols = 3,
    valueFormatter,

    className
}) => {
    if (!metrics || metrics.length === 0) {
        return null;
    }

    return (
        <>
            <h2 className="text-lg font-medium text-gray-900 dark:text-gray-50">
                Plan overview
            </h2>
            <p className="mt-1 text-sm/6 text-gray-500 dark:text-gray-500">
                You are currently on the{' '}
                <span className="font-medium text-gray-900 dark:text-gray-500">
                    starter plan
                </span>
                .{' '}
                <a
                    href="#"
                    className="inline-flex items-center gap-1 text-blue-500 hover:underline hover:underline-offset-4 dark:text-blue-500"
                >
                    View other plans
                    <RiExternalLinkLine className="size-4" aria-hidden={true} />
                </a>
            </p>
            <div className="mt-8">
                <MetricCardGrid
                className={className}
                    items={metrics}
                    renderCard={(item) => (
                        <PlanCard item={item as PlanMetricItem} />
                    )}
                    cols={cols}
                />
            </div>
        </>
    );
};
