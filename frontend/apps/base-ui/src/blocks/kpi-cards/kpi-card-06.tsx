import React from 'react';
import { RiArrowDownSFill, RiArrowUpSFill } from '@remixicon/react';
import { MetricItem, CommonFormattingProps } from './index';
import { Card } from '../../tremor/components/Card';
import { cx } from '../../lib/utils';

export interface KpiCard06Props extends CommonFormattingProps {
    metrics?: MetricItem[];
    cols?: number;
    valueFormatter?: (value: number | string) => string;
    className?: string;
}

const ArrowIconVariantCard: React.FC<{ item: MetricItem; valueFormatter?: (value: number | string) => string; valueSizeClass: string }> = ({ item, valueFormatter, valueSizeClass }) => (
    <Card className={valueSizeClass === 'text-xl' ? 'p-3' : valueSizeClass === 'text-2xl' ? 'p-4' : ''}>
        <div className="flex items-center justify-between">
            <dt className="text-sm font-medium text-gray-500 dark:text-gray-500">
                {item.name}
            </dt>
            <dd
                className={cx(
                    item.changeType === 'positive'
                        ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-400/10 dark:text-emerald-500'
                        : item.changeType === 'negative'
                            ? 'bg-red-100 text-red-800 dark:bg-red-400/10 dark:text-red-500'
                            : 'bg-gray-100 text-gray-800 dark:bg-gray-400/10 dark:text-gray-500',
                    'inline-flex items-center gap-x-1 rounded-md px-1.5 py-0.5 text-xs font-medium',
                )}
            >
                {item.changeType === 'positive' ? (
                    <RiArrowUpSFill className="-ml-0.5 size-4 shrink-0" aria-hidden />
                ) : item.changeType === 'negative' ? (
                    <RiArrowDownSFill className="-ml-0.5 size-4 shrink-0" aria-hidden />
                ) : null}
                {item.change}
            </dd>
        </div>
        <dd className={cx(valueSizeClass, 'font-semibold text-gray-900 dark:text-gray-50')}>
            {valueFormatter ? valueFormatter(item.stat ?? item.value ?? '') : (item.stat ?? item.value)}
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

export const KpiCard06: React.FC<KpiCard06Props> = ({
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
            renderCard={(item) => <ArrowIconVariantCard item={item} valueFormatter={valueFormatter} valueSizeClass={valueSizeClass} />}
            cols={cols}
        />
    );
};
