import React from 'react';
import { MetricItem, CommonFormattingProps } from './index';
import { Card } from '../../tremor/components/Card';
import { cx } from '../../lib/utils';

export interface KpiCard09Props extends CommonFormattingProps {
    metrics?: MetricItem[];
    cols?: number;
    valueFormatter?: (value: number | string) => string;
    className?: string;
}

const ColoredLeftAccentCard: React.FC<{ item: MetricItem; valueFormatter?: (value: number | string) => string; valueSizeClass: string }> = ({ item, valueFormatter, valueSizeClass }) => (
    <Card className={valueSizeClass === 'text-xl' ? 'p-3' : valueSizeClass === 'text-2xl' ? 'p-4' : ''}>
        <div className="flex space-x-3">
            <div
                className={cx(item.color || 'bg-blue-500', 'w-1 shrink-0 rounded')}
            />
            <dt className="flex w-full items-center justify-between space-x-3 truncate text-sm text-gray-500 dark:text-gray-500">
                <span className="truncate">{item.name}</span>
                <span className="font-medium text-gray-700 dark:text-gray-300">
                    {item.change}
                </span>
            </dt>
        </div>
        <div className="mt-2 pl-4">
            <dd className={cx(valueSizeClass, 'font-semibold text-gray-900 dark:text-gray-50')}>
                {valueFormatter ? valueFormatter(item.stat ?? item.value ?? '') : (item.stat ?? item.value)}
            </dd>
        </div>
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

export const KpiCard09: React.FC<KpiCard09Props> = ({
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
            renderCard={(item) => <ColoredLeftAccentCard item={item} valueFormatter={valueFormatter} valueSizeClass={valueSizeClass} />}
            cols={cols}
        />
    );
};
