import React from 'react';
import { RiArrowDownSFill, RiArrowUpSFill } from '@remixicon/react';
import { MetricItem, CommonFormattingProps } from './index';
import { Card } from '../../tremor/components/Card';
import { cx } from '../../lib/utils';

export interface KpiCard08Props extends CommonFormattingProps {
    metrics?: MetricItem[];
    cols?: number;
    valueFormatter?: (value: number | string) => string;
    className?: string;
}

// Arrow icon at bottom with period comparison
const ArrowIconPeriodCard: React.FC<{ item: MetricItem; valueFormatter?: (value: number | string) => string; valueSizeClass: string }> = ({ item, valueFormatter, valueSizeClass }) => (
    <Card className={valueSizeClass === 'text-xl' ? 'p-3' : valueSizeClass === 'text-2xl' ? 'p-4' : ''}>
        <dt className="text-sm font-medium text-gray-500 dark:text-gray-500">
            {item.name}
        </dt>
        <dd className="mt-1 flex items-baseline space-x-2.5">
            <p className={cx(valueSizeClass, 'font-semibold text-gray-900 dark:text-gray-50')}>
                {valueFormatter ? valueFormatter(item.stat ?? item.value ?? '') : (item.stat ?? item.value)}
            </p>
            {item.previousStat && (
                <p className="text-sm text-gray-500 dark:text-gray-500">
                    from {item.previousStat}
                </p>
            )}
        </dd>
        <dd className="mt-4 flex items-center space-x-2">
            <p className="flex items-center space-x-0.5">
                {item.changeType === 'positive' ? (
                    <RiArrowUpSFill
                        className="size-5 shrink-0 text-emerald-700 dark:text-emerald-500"
                        aria-hidden={true}
                    />
                ) : (
                    <RiArrowDownSFill
                        className="size-5 shrink-0 text-red-700 dark:text-red-500"
                        aria-hidden={true}
                    />
                )}
                <span
                    className={cx(
                        item.changeType === 'positive'
                            ? 'text-emerald-700 dark:text-emerald-500'
                            : item.changeType === 'negative'
                                ? 'text-red-700 dark:text-red-500'
                                : 'text-gray-700 dark:text-gray-400',
                        'text-sm font-medium',
                    )}
                >
                    {item.change}
                </span>
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-500">
                from previous month
            </p>
        </dd>
    </Card>
);

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

export const KpiCard08: React.FC<KpiCard08Props> = ({
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
            renderCard={(item) => <ArrowIconPeriodCard item={item} valueFormatter={valueFormatter} valueSizeClass={valueSizeClass} />}
            cols={cols}
        />
    );
};
