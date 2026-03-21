import React from 'react';
import { Card } from '../../tremor/components/Card';
import { SparkAreaChart } from '../../tremor/components/SparkChart';
import { cx } from '../../lib/utils';

export interface SparkChart05HoldingItem {
    name: string;
    /** Override the data series key when it differs from `name` */
    dataKey?: string;
    /** Display value (e.g. price, NAV) */
    value?: string;
    change: string;
    changeType: 'positive' | 'negative' | 'neutral';
}

export interface SparkChart05Props {
    data: Array<Record<string, any>>;
    /** Key used for x-axis lookup; defaults to 'date' */
    dataIndex?: string;
    items: SparkChart05HoldingItem[];
  className?: string;
}

/**
 * SparkChart05: Private Holdings (Grid Layout)
 * Direct implementation matching tremor block structure (spark-chart-05.tsx)
 * Layout: Grid of cards (sm:grid-cols-2 lg:grid-cols-3) with company name + change on left, spark chart on right
 */
export const SparkChart05: React.FC<SparkChart05Props> = ({ data, dataIndex = 'date', items ,
    className
}) => {
    return (
        <dl className={cx('grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3', className)}>
            {items.map((item) => (
                <Card key={item.name}>
                    <div className="flex items-center justify-between space-x-4">
                        <div className="truncate">
                            <dt className="truncate text-sm font-medium text-gray-900 dark:text-gray-50">
                                {item.name}
                            </dt>
                            {item.value && (
                                <dd className="truncate text-sm font-semibold text-gray-900 dark:text-gray-50">
                                    {item.value}
                                </dd>
                            )}
                            <dd
                                className={cx(
                                    item.changeType === 'positive'
                                        ? 'text-emerald-700 dark:text-emerald-500'
                                        : item.changeType === 'negative'
                                            ? 'text-red-700 dark:text-red-500'
                                            : 'text-gray-600 dark:text-gray-400',
                                    'text-sm font-medium',
                                )}
                            >
                                {item.change}
                            </dd>
                        </div>
                        <SparkAreaChart
                            data={data}
                            index={dataIndex}
                            categories={[item.dataKey ?? item.name]}
                            fill="solid"
                            colors={
                                (item.changeType === 'positive'
                                    ? ['emerald']
                                    : item.changeType === 'negative'
                                        ? ['red']
                                        : ['gray']) as any
                            }
                            className="h-20 w-32 flex-none"
                        />
                    </div>
                </Card>
            ))}
        </dl>
    );
};
