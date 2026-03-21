import React from 'react';
import { Card } from '../../tremor/components/Card';
import { SparkAreaChart } from '../../tremor/components/SparkChart';
import { cx } from '../../lib/utils';

export interface SparkChart02WatchlistItem {
    ticker: string;
    /** Override the data series key when it differs from `ticker` */
    dataKey?: string;
    description: string;
    value: string;
    change: string;
    changeType: 'positive' | 'negative' | 'neutral';
}

export interface SparkChart02HeaderItem {
    totalValue: string;
    dailyChange: string;
    dailyChangeType: 'positive' | 'negative' | 'neutral';
}

export interface SparkChart02Props {
    data: Array<Record<string, any>>;
    /** Key used for x-axis lookup; defaults to 'date' */
    dataIndex?: string;
    headerItem: SparkChart02HeaderItem;
    items: SparkChart02WatchlistItem[];
    headerLabel?: string;
    todayLabel?: string;
  className?: string;
}

/**
 * SparkChart02: Watchlist Layout
 * Direct implementation matching tremor block structure (spark-chart-02.tsx)
 * Layout: Card with watchlist header, total value, daily change summary, and list of stock positions
 */
export const SparkChart02: React.FC<SparkChart02Props> = ({
    data,
    dataIndex = 'date',
    headerItem,
    items,
    headerLabel = 'Watchlist',
    todayLabel = 'Today',

    className
}) => {
    const changeColor =
        headerItem.dailyChangeType === 'positive'
            ? 'text-emerald-700 dark:text-emerald-500'
            : headerItem.dailyChangeType === 'negative'
                ? 'text-red-700 dark:text-red-500'
                : 'text-gray-600 dark:text-gray-400';

    const itemChangeColor = (changeType: 'positive' | 'negative' | 'neutral') =>
        changeType === 'positive'
            ? 'text-emerald-700 dark:text-emerald-500'
            : changeType === 'negative'
                ? 'text-red-700 dark:text-red-500'
                : 'text-gray-600 dark:text-gray-400';

    return (
        <Card className={cx('sm:mx-auto sm:max-w-md', className)}>
            <p className="text-sm text-gray-500 dark:text-gray-500">{headerLabel}</p>
            <p className="text-3xl font-semibold text-gray-900 dark:text-gray-50">
                {headerItem.totalValue}
            </p>
            <p className="mt-1 text-sm font-medium">
                <span className={changeColor}>{headerItem.dailyChange}</span>{' '}
                <span className="font-normal text-gray-500 dark:text-gray-500">
                    {todayLabel}
                </span>
            </p>
            <ul role="list" className="mt-8 space-y-8">
                {items.map((item: any) => (
                    <li
                        key={item.ticker}
                        className="flex items-center justify-between space-x-6"
                    >
                        <div className="truncate">
                            <p className="truncate text-sm font-medium text-gray-900 dark:text-gray-50">
                                {item.ticker}
                            </p>
                            <p className="truncate text-xs text-gray-500 dark:text-gray-500">
                                {item.description}
                            </p>
                        </div>
                        <div className="flex items-center space-x-4">
                            <SparkAreaChart
                                data={data}
                                index={dataIndex}
                                categories={[item.dataKey ?? item.ticker]}
                                colors={
                                    (item.changeType === 'positive'
                                        ? ['emerald']
                                        : item.changeType === 'negative'
                                            ? ['red']
                                            : ['gray']) as any
                                }
                                className="h-20 w-40 flex-none sm:w-56"
                            />
                            <div className="w-14 text-right sm:w-16">
                                <p className="text-sm font-medium text-gray-900 dark:text-gray-50">
                                    {item.value}
                                </p>
                                <p
                                    className={cx(
                                        itemChangeColor(item.changeType),
                                        'text-xs font-medium',
                                    )}
                                >
                                    {item.change}
                                </p>
                            </div>
                        </div>
                    </li>
                ))}
            </ul>
        </Card>
    );
};
