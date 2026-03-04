import React from 'react';
import { MetricItem, CommonFormattingProps } from './index';
import { Card } from '../../tremor/components/Card';
import { cx } from '../../lib/utils';

export interface KpiCard04Props extends CommonFormattingProps {
    metrics?: MetricItem[];
    cols?: number;
    valueFormatter?: (value: number | string) => string;
    className?: string;
}

const NavigationLinkCard: React.FC<{ item: MetricItem; valueFormatter?: (value: number | string) => string; valueSizeClass: string }> = ({ item, valueFormatter, valueSizeClass }) => (
    <Card className="!p-0">
        <div className="px-4 py-4">
            <dd className="flex items-start justify-between space-x-2">
                <span className="truncate text-sm text-gray-500 dark:text-gray-500">
                    {item.name}
                </span>
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
            </dd>
            <dd className={cx(valueSizeClass, 'mt-1 font-semibold text-gray-900 dark:text-gray-50')}>
                {valueFormatter ? valueFormatter(item.value ?? item.stat ?? '') : (item.value ?? item.stat)}
            </dd>
        </div>
        {item.href && (
            <div className="flex justify-end border-t border-gray-200 px-4 py-3 dark:border-gray-900">
                <a
                    href={item.href}
                    className="text-sm font-medium text-blue-500 hover:text-blue-600 dark:text-blue-500 hover:dark:text-blue-600"
                >
                    View more &#8594;
                </a>
            </div>
        )}
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

export const KpiCard04: React.FC<KpiCard04Props> = ({
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
            renderCard={(item) => <NavigationLinkCard item={item} valueFormatter={valueFormatter} valueSizeClass={valueSizeClass} />}
            cols={cols}
        />
    );
};
