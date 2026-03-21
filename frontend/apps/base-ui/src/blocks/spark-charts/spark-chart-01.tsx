import React from 'react';
import { Card } from '../../tremor/components/Card';
import { SparkAreaChart } from '../../tremor/components/SparkChart';
import { cx } from '../../lib/utils';

export interface SparkChart01Props {
    data: Array<Record<string, any>>;
    /** Key used for x-axis lookup; defaults to 'date' */
    dataIndex?: string;
    items: Array<{
        id: string;
        name: string;
        /** Override the data series key when it differs from `id` */
        dataKey?: string;
        description?: string;
        value?: string;
        change?: string;
        changeType?: 'positive' | 'negative' | 'neutral';
    }>;
    title?: string;
    description?: string;
  className?: string;
}

/**
 * SparkChart01: Multiple Ticker Price Tracking (Horizontal Layout)
 * Matches original Tremor spark-chart-01 layout
 * Finance: Portfolio holding prices over 2-week period
 */
export const SparkChart01: React.FC<SparkChart01Props> = ({
    data,
    dataIndex = 'date',
    items,
    title = 'Portfolio Holdings',
    description = 'Tech stock prices over 2-week period',

    className
}) => {
    return (
        <div className={cx('space-y-6', className)}>
            {title && (
                <>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                        {title}
                    </h3>
                    {description && (
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                            {description}
                        </p>
                    )}
                </>
            )}
            <dl className="space-y-6 sm:mx-auto sm:max-w-md">
                {items.map((item) => (
                    <Card
                        key={item.id}
                        className="flex items-center justify-between space-x-4 !p-4"
                    >
                        <div className="truncate">
                            <dt className="truncate text-sm font-medium text-gray-900 dark:text-gray-50">
                                {item.name}
                            </dt>
                            {item.description && (
                                <dd className="truncate text-xs text-gray-500 dark:text-gray-500">
                                    {item.description}
                                </dd>
                            )}
                        </div>
                        <div className="flex items-center space-x-3">
                            <SparkAreaChart
                                data={data}
                                index={dataIndex}
                                categories={[item.dataKey ?? item.id]}
                                colors={(item.changeType === 'positive' ? ['emerald'] : item.changeType === 'negative' ? ['red'] : ['gray']) as any}
                                className="h-16 w-32 flex-none sm:w-40"
                            />
                            <div
                                className={cx(
                                    item.changeType === 'positive'
                                        ? 'text-emerald-700 dark:text-emerald-500'
                                        : item.changeType === 'negative'
                                            ? 'text-red-700 dark:text-red-500'
                                            : 'text-gray-600 dark:text-gray-400',
                                    'flex w-28 items-center justify-end space-x-2 sm:w-32',
                                )}
                            >
                                {item.value && (
                                    <dd className="text-sm font-medium">{item.value}</dd>
                                )}
                                {item.change && (
                                    <dd
                                        className={cx(
                                            item.changeType === 'positive'
                                                ? 'bg-emerald-100 dark:bg-emerald-400/10'
                                                : item.changeType === 'negative'
                                                    ? 'bg-red-100 dark:bg-red-400/10'
                                                    : 'bg-gray-100 dark:bg-gray-400/10',
                                            'rounded px-1.5 py-1 text-xs font-medium tabular-nums',
                                        )}
                                    >
                                        {item.change}
                                    </dd>
                                )}
                            </div>
                        </div>
                    </Card>
                ))}
            </dl>
        </div>
    );
};
