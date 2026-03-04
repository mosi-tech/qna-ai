import React from 'react';
import { BarList } from '../../tremor/components/BarList';
import { Card } from '../../tremor/components/Card';
import { cx } from '../../lib/utils';

export interface BarListItem {
    name: string;
    value: number;
}

export interface BarList07Props {
    data?: BarListItem[];
    valueFormatter?: (value: number) => string;
    title: string;
  className?: string;
}

export const BarList07: React.FC<BarList07Props> = ({
    data = [],
    valueFormatter = (value) => `${value}`,
    title,

    className
}) => {
    const [selectedItem, setSelectedItem] = React.useState<string | undefined>();

    if (!data || data.length === 0) {
        return null;
    }

    const handleBarClick = (item: BarListItem) => {
        setSelectedItem(selectedItem === item.name ? undefined : item.name);
    };

    const selectedValue = selectedItem
        ? data.find((item) => item.name === selectedItem)?.value || 0
        : data.reduce((sum, item) => sum + item.value, 0);

    return (
        <>
            {/* Summary metric card */}
            <div className="rounded-lg border border-dashed border-gray-300 p-6 dark:border-gray-600 sm:mx-auto sm:max-w-lg">
                <h4 className="text-sm text-gray-500 dark:text-gray-500">
                    {selectedItem || 'Total'}
                </h4>
                <p className="text-3xl font-semibold text-gray-900 dark:text-gray-50">
                    {valueFormatter(selectedValue)}
                </p>
            </div>
            <Card className="mt-4 sm:mx-auto sm:max-w-lg">
                <div className="flex flex-wrap items-start justify-between gap-2">
                    <p className="font-medium leading-7 text-gray-900 dark:text-gray-50">
                        {title}
                    </p>
                    {selectedItem && (
                        <button
                            type="button"
                            onClick={() => setSelectedItem(undefined)}
                            className="inline-flex rounded-md bg-gray-50 px-2 py-1.5 text-xs text-gray-900 ring-1 ring-inset ring-gray-200 dark:bg-gray-500/20 dark:text-gray-50 dark:ring-gray-400/20"
                        >
                            Clear selection
                        </button>
                    )}
                </div>
                <div className="mt-6">
                    <BarList
                        data={data}
                        valueFormatter={valueFormatter}
                        onValueChange={handleBarClick}
                    />
                </div>
            </Card>
        </>
    );
};
