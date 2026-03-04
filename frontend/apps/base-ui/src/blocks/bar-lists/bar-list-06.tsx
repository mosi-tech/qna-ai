import React from 'react';
import { BarList } from '../../tremor/components/BarList';
import { Card } from '../../tremor/components/Card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../tremor/components/Tabs';
import { cx } from '../../lib/utils';

export interface BarListItem {
    name: string;
    value: number;
}

export interface TabData {
    name: string;
    data: BarListItem[];
}

export interface BarList06Props {
    tabs?: TabData[];
    valueFormatter?: (value: number) => string;
    title: string;
  className?: string;
}

export const BarList06: React.FC<BarList06Props> = ({
    tabs = [],
    valueFormatter = (value) => `${value}`,
    title,

    className
}) => {
    if (!tabs || tabs.length === 0) {
        return null;
    }

    return (
        <Card className={cx('sm:mx-auto sm:max-w-lg', className)}>
            <Tabs defaultValue={tabs[0].name}>
                <div className="flex items-center justify-between">
                    <p className="font-medium text-gray-900 dark:text-gray-50">
                        {title}
                    </p>
                    <TabsList
                        variant="solid"
                        className="!overflow-visible !bg-transparent !p-0 dark:!bg-transparent"
                    >
                        {tabs.map((item) => (
                            <TabsTrigger
                                key={item.name}
                                value={item.name}
                                className="rounded-md data-[state=active]:ring-1 data-[state=active]:ring-inset data-[state=active]:ring-gray-200 data-[state=active]:dark:ring-gray-800"
                            >
                                {item.name}
                            </TabsTrigger>
                        ))}
                    </TabsList>
                </div>
                <div className="mt-6">
                    {tabs.map((item) => (
                        <TabsContent key={item.name} value={item.name}>
                            <BarList data={item.data} valueFormatter={valueFormatter} />
                        </TabsContent>
                    ))}
                </div>
            </Tabs>
        </Card>
    );
};
