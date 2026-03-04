import React from 'react';
import { RiArrowRightSLine } from '@remixicon/react';
import { DonutChart } from '../../tremor';
import { type AvailableChartColorsKeys } from '../../lib/chartUtils';
import { Card } from '../../tremor/components/Card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../tremor/components/Tabs';
import { cx } from '../../lib/utils';

export interface DataItem {
    name: string;
    value: number;
    share?: string;
    href?: string;
    borderColor?: string;
    [key: string]: any;
}

export interface TabDataSet {
    id: string;
    label: string;
    data: DataItem[];
}

export interface DonutChart05Props {
    title: string;
    tabSets: TabDataSet[];
    description?: string;
    colors?: AvailableChartColorsKeys[];
    showLabel?: boolean;
    showTooltip?: boolean;
    valueFormatter?: (value: number) => string;
  className?: string;
}

const defaultCurrencyFormatter = (number: number) => {
    return '$' + Intl.NumberFormat('us').format(number).toString();
};

export const DonutChart05: React.FC<DonutChart05Props> = ({
    title,
    tabSets,
    description,
    colors = ['blue', 'emerald', 'cyan', 'violet', 'fuchsia'] as const,
    showLabel = true,
    showTooltip = false,
    valueFormatter = defaultCurrencyFormatter,

    className
}) => {
    return (
        <Card className={cx('overflow-hidden !p-0 sm:mx-auto sm:max-w-lg', className)}>
            <div className="px-6 pt-6">
                <h3 className="text-sm font-medium text-gray-900 dark:text-gray-50">
                    {title}
                </h3>
                {description && (
                    <p className="mt-1 text-sm/6 text-gray-500 dark:text-gray-500">
                        {description}
                    </p>
                )}
            </div>
            <Tabs defaultValue={tabSets[0]?.id}>
                <TabsList className="px-6 pt-6">
                    {tabSets.map((tabSet) => (
                        <TabsTrigger key={tabSet.id} value={tabSet.id}>
                            {tabSet.label}
                        </TabsTrigger>
                    ))}
                </TabsList>
                <div className="pt-8">
                    {tabSets.map((tabSet) => (
                        <TabsContent key={tabSet.id} value={tabSet.id}>
                            <div className="px-6 pb-6">
                                <DonutChart
                                    className="mx-auto"
                                    data={tabSet.data}
                                    value="value"
                                    category="name"
                                    valueFormatter={valueFormatter}
                                    showLabel={showLabel}
                                    showTooltip={showTooltip}
                                    colors={colors as AvailableChartColorsKeys[]}
                                />
                            </div>
                            <ul
                                role="list"
                                className="mt-2 divide-y divide-gray-200 border-t border-gray-200 text-sm text-gray-500 dark:divide-gray-800 dark:border-gray-900 dark:text-gray-500"
                            >
                                {tabSet.data.map((item) => (
                                    <li
                                        key={item.name}
                                        className="group relative flex items-center justify-between space-x-4 truncate pr-4 hover:bg-gray-50 hover:dark:bg-gray-900"
                                    >
                                        <div
                                            className={cx(
                                                item.borderColor || 'border-gray-300 dark:border-gray-600',
                                                'flex h-12 items-center truncate border-l-2 pl-4',
                                            )}
                                        >
                                            <span className="truncate group-hover:text-gray-700 dark:text-gray-300 group-hover:dark:text-gray-50">
                                                <a href={item.href || '#'} className="focus:outline-none">
                                                    {/* extend link to entire list item */}
                                                    <span
                                                        className="absolute inset-0"
                                                        aria-hidden={true}
                                                    />
                                                    {item.name}
                                                </a>
                                            </span>
                                        </div>
                                        <div className="flex items-center space-x-1.5">
                                            <span className="font-medium tabular-nums text-gray-900 dark:text-gray-50">
                                                {valueFormatter(item.value)}{' '}
                                                {item.share && (
                                                    <span className="font-normal text-gray-500 dark:text-gray-500">
                                                        ({item.share})
                                                    </span>
                                                )}
                                            </span>
                                            <RiArrowRightSLine
                                                className="size-4 shrink-0 text-gray-400 group-hover:text-gray-500 dark:text-gray-600 group-hover:dark:text-gray-500"
                                                aria-hidden={true}
                                            />
                                        </div>
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
