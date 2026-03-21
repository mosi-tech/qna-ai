import React from 'react';
import { Card } from '../../tremor/components/Card';
import { SparkAreaChart } from '../../tremor/components/SparkChart';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../tremor/components/Tabs';
import { cx } from '../../lib/utils';

export interface SparkChart03Stock {
    ticker: string;
    /** Override the data series key when it differs from `ticker` */
    dataKey?: string;
    description: string;
    value: string;
    change: string;
    changeType: 'positive' | 'negative' | 'neutral';
}

export interface SparkChart03Tab {
    name: string;
    /** Items to display in this tab */
    items: SparkChart03Stock[];
}

export interface SparkChart03Props {
    data: Array<Record<string, any>>;
    /** Key used for x-axis lookup; defaults to 'date' */
    dataIndex?: string;
    tabs: SparkChart03Tab[];
    headerItem?: {
        totalValue: string;
        dailyChange: string;
        dailyChangeType: 'positive' | 'negative' | 'neutral';
    };
    headerLabel?: string;
    todayLabel?: string;
  className?: string;
}

/**
 * SparkChart03: Tabbed Watchlist Layout
 * Direct implementation matching tremor block structure (spark-chart-03.tsx)
 * Finance: Multi-tab watchlist with categorized stock positions (Trending vs Watchlist)
 */
export const SparkChart03: React.FC<SparkChart03Props> = ({
    data,
    dataIndex = 'date',
    tabs,
    headerItem,
    headerLabel = 'Watchlist',
    todayLabel = 'Today',

    className
}) => {
    const changeColor =
        headerItem?.dailyChangeType === 'positive'
            ? 'text-emerald-700 dark:text-emerald-500'
            : headerItem?.dailyChangeType === 'negative'
                ? 'text-red-700 dark:text-red-500'
                : 'text-gray-600 dark:text-gray-400';

    const stockChangeColor = (changeType: 'positive' | 'negative' | 'neutral') =>
        changeType === 'positive'
            ? 'text-emerald-700 dark:text-emerald-500'
            : changeType === 'negative'
                ? 'text-red-700 dark:text-red-500'
                : 'text-gray-600 dark:text-gray-400';

    return (
        <Card className={cx('sm:mx-auto sm:max-w-md', className)}>
            {headerItem && (
                <>
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
                </>
            )}
            <Tabs defaultValue={tabs[0]?.name || ''} className={headerItem ? 'mt-6' : ''}>
                <TabsList className="grid w-full grid-cols-2" variant="solid">
                    {tabs.map((tab) => (
                        <TabsTrigger key={tab.name} value={tab.name}>
                            {tab.name}
                        </TabsTrigger>
                    ))}
                </TabsList>
                <div className="mt-8">
                    {tabs.map((tab) => (
                        <TabsContent key={tab.name} value={tab.name}>
                            <ul role="list" className="space-y-6">
                                {tab.items.map((stock) => (
                                    <li
                                        key={stock.ticker}
                                        className="flex items-center justify-between space-x-6"
                                    >
                                        <div>
                                            <p className="text-sm font-medium text-gray-900 dark:text-gray-50">
                                                {stock.description}
                                            </p>
                                            <p
                                                className={cx(
                                                    stockChangeColor(stock.changeType),
                                                    'flex items-center space-x-1 text-sm',
                                                )}
                                            >
                                                <span className="font-medium">{stock.value}</span>
                                                <span>({stock.change})</span>
                                            </p>
                                        </div>
                                        <SparkAreaChart
                                            data={data}
                                            index={dataIndex}
                                            categories={[stock.dataKey ?? stock.ticker]}
                                            colors={
                                                (stock.changeType === 'positive'
                                                    ? ['emerald']
                                                    : stock.changeType === 'negative'
                                                        ? ['red']
                                                        : ['gray']) as any
                                            }
                                            className="h-20 w-48 flex-none sm:w-56"
                                        />
                                    </li>
                                ))}
                            </ul>
                        </TabsContent>
                    ))}
                </div>
            </Tabs>
        </Card>
    );
};
