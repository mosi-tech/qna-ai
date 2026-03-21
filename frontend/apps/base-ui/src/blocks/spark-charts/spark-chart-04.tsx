import React from 'react';
import { Card } from '../../tremor/components/Card';
import { SparkAreaChart } from '../../tremor/components/SparkChart';
import { cx } from '../../lib/utils';

export interface SparkChart04MetricItem {
    name: string;
    stat: string;
    /** Override the data series key when it differs from `name` */
    dataKey?: string;
    change?: string;
    changeType?: 'positive' | 'negative' | 'neutral';
    /** Tremor color name for the spark chart (e.g. 'emerald', 'blue', 'indigo') */
    color?: string;
}

export interface SparkChart04Props {
    data: Array<Record<string, any>>;
    /** Key used for x-axis lookup; defaults to 'date' */
    dataIndex?: string;
    items: SparkChart04MetricItem[];
  className?: string;
}

/**
 * SparkChart04: Metrics Dashboard (Grid Layout)
 * Direct implementation matching tremor block structure (spark-chart-04.tsx)
 * Layout: Grid of cards (sm:grid-cols-2 lg:grid-cols-3) with large stat on left and spark chart on right
 */
export const SparkChart04: React.FC<SparkChart04Props> = ({ data, dataIndex = 'date', items ,
    className
}) => {
    return (
        <dl className={cx('grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3', className)}>
            {items.map((item) => (
                <Card key={item.name}>
                    <dt className="text-sm text-gray-500 dark:text-gray-500">
                        {item.name}
                    </dt>
                    <div className="flex items-center justify-between space-x-8">
                        <div>
                            <dd className="text-3xl font-semibold text-gray-900 dark:text-gray-50">
                                {item.stat}
                            </dd>
                            {item.change && (
                                <dd
                                    className={cx(
                                        item.changeType === 'positive'
                                            ? 'text-emerald-700 dark:text-emerald-500'
                                            : item.changeType === 'negative'
                                                ? 'text-red-700 dark:text-red-500'
                                                : 'text-gray-600 dark:text-gray-400',
                                        'mt-1 text-sm font-medium',
                                    )}
                                >
                                    {item.change}
                                </dd>
                            )}
                        </div>
                        <SparkAreaChart
                            data={data}
                            index={dataIndex}
                            categories={[item.dataKey ?? item.name]}
                            fill="solid"
                            colors={item.color ? ([item.color] as any) : undefined}
                            className="h-20 w-32 flex-none"
                        />
                    </div>
                </Card>
            ))}
        </dl>
    );
};
