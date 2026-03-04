'use client';

import React from 'react';
import { MetricItem, CommonFormattingProps } from './index';
import { Card } from '../../tremor/components/Card';
import { ProgressCircle } from '../../tremor';
import { cx } from '../../lib/utils';

export interface KpiCard16Props extends CommonFormattingProps {
    metrics?: MetricItem[];
    cols?: number;
    valueFormatter?: (value: number | string) => string;
    className?: string;
}

export interface ScoreMetricItem extends MetricItem {
    value?: number;
}

const ScoreCard: React.FC<{ item: ScoreMetricItem; valueSizeClass: string }> = ({ item, valueSizeClass }) => {
    const value = typeof item.stat === 'number' ? item.stat : (item.value ?? 0);

    return (
        <Card className={valueSizeClass === 'text-xl' ? 'p-3' : valueSizeClass === 'text-2xl' ? 'p-4' : ''}>
            <dt className="text-sm text-gray-500 dark:text-gray-500">
                {item.name}
            </dt>
            <dd className="mt-3 flex items-center justify-between">
                <p className={cx(valueSizeClass, 'font-medium text-gray-900 dark:text-gray-50')}>
                    {value}
                    <span className="text-base text-gray-500 dark:text-gray-500">
                        /100
                    </span>
                </p>
                <ProgressCircle
                    value={value}
                    radius={25}
                    strokeWidth={5}
                    color={
                        value >= 75
                            ? 'emerald'
                            : value > 50
                                ? 'orange'
                                : 'red'
                    }
                >
                    <span className="text-xs font-medium text-gray-900 dark:text-gray-50">
                        {value}
                    </span>
                </ProgressCircle>
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

export const KpiCard16: React.FC<KpiCard16Props> = ({
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
        <>
            <div className="block sm:flex sm:items-start sm:justify-between sm:space-x-6">
                <div>
                    <h3 className="text-lg font-medium text-gray-900 dark:text-gray-50">
                        Web vitals scores
                    </h3>
                    <p className="mt-1 text-sm/6 text-gray-500 dark:text-gray-500">
                        Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam
                        nonumy eirmod tempor.
                    </p>
                </div>
                <span className="mt-6 inline-flex w-full justify-center space-x-4 whitespace-nowrap rounded-md border border-gray-200 px-2 py-1 text-xs text-gray-900 dark:border-gray-900 dark:text-gray-50 sm:mt-0 sm:w-fit sm:items-center">
                    <span tabIndex={1} className="flex items-center gap-1.5">
                        <span
                            aria-hidden={true}
                            className="size-2.5 rounded-sm bg-red-600 dark:bg-red-500"
                        />
                        0-50
                    </span>
                    <span tabIndex={1} className="flex items-center gap-1.5">
                        <span
                            aria-hidden={true}
                            className="size-2.5 rounded-sm bg-orange-600 dark:bg-orange-500"
                        />
                        50-75
                    </span>
                    <span tabIndex={1} className="flex items-center gap-1.5">
                        <span
                            aria-hidden={true}
                            className="size-2.5 rounded-sm bg-emerald-600 dark:bg-emerald-500"
                        />
                        75-100
                    </span>
                </span>
            </div>
            <div className="mt-6">
                <MetricCardGrid
                    className={className}
                    items={metrics}
                    renderCard={(item) => (
                        <ScoreCard item={item as ScoreMetricItem} valueSizeClass={valueSizeClass} />
                    )}
                    cols={cols}
                />
            </div>
        </>
    );
};
