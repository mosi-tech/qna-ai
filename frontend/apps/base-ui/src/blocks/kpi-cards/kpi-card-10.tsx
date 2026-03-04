import React from 'react';
import { RiCheckLine, RiErrorWarningLine, RiEyeLine } from '@remixicon/react';
import { MetricItem, CommonFormattingProps } from './index';
import { Card } from '../../tremor/components/Card';
import { cx } from '../../lib/utils';

export interface KpiCard10Props extends CommonFormattingProps {
    metrics?: MetricItem[];
    cols?: number;
    valueFormatter?: (value: number | string) => string;
    className?: string;
}

export interface ConstraintItem extends MetricItem {
    status?: 'within' | 'observe' | 'critical';
    range?: string;
}

const ConstraintStatusCard: React.FC<{ item: ConstraintItem; valueFormatter?: (value: number | string) => string; valueSizeClass: string }> = ({ item, valueFormatter, valueSizeClass }) => {
    const statusConfig = {
        within: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-400/10 dark:text-emerald-500',
        observe: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-400/10 dark:text-yellow-500',
        critical: 'bg-red-100 text-red-800 dark:bg-red-400/10 dark:text-red-500',
    };

    const getStatusIcon = (status?: string) => {
        if (status === 'within') {
            return <RiCheckLine className="size-4 shrink-0" aria-hidden={true} />;
        } else if (status === 'observe') {
            return <RiEyeLine className="size-4 shrink-0" aria-hidden={true} />;
        } else if (status === 'critical') {
            return <RiErrorWarningLine className="size-4 shrink-0" aria-hidden={true} />;
        }
        return null;
    };

    return (
        <Card className={valueSizeClass === 'text-xl' ? 'p-3' : valueSizeClass === 'text-2xl' ? 'p-4' : ''}>
            <dt className="text-sm font-medium text-gray-500 dark:text-gray-500">
                {item.name}
            </dt>
            <dd className={cx(valueSizeClass, 'font-semibold text-gray-900 dark:text-gray-50')}>
                {valueFormatter ? valueFormatter(item.stat ?? item.value ?? '') : (item.stat ?? item.value)}
            </dd>
            {item.status && (
                <dd
                    className={cx(
                        statusConfig[item.status],
                        'mt-4 inline-flex items-center gap-x-1.5 rounded-md px-2 py-1.5 text-xs font-medium',
                    )}
                >
                    {getStatusIcon(item.status)}
                    {item.status}: {item.range}
                </dd>
            )}
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

export const KpiCard10: React.FC<KpiCard10Props> = ({
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
            renderCard={(item) => <ConstraintStatusCard item={item as ConstraintItem} valueFormatter={valueFormatter} valueSizeClass={valueSizeClass} />}
            cols={cols}
        />
    );
};
