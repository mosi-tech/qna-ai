import React from 'react';
import { Button } from '../../tremor/components/Button';
import { Card } from '../../tremor/components/Card';
import {
    Dialog,
    DialogClose,
    DialogContent,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from '../../tremor/components/Dialog';
import { Input } from '../../tremor/components/Input';
import { ProgressBar } from '../../tremor/components/ProgressBar';
import { cx } from '../../lib/utils';

export interface ListItem {
    [key: string]: string | number;
}

export interface OrderItem extends ListItem {
    name: string;
    date: string;
}

export interface BarList04Props {
    data?: ListItem[];
    title: string;
    progressValue?: number;
    fulfilledCount?: number;
    fulfilledPercent?: number;
    openCount?: number;
    openPercent?: number;
    fulfilledLabel?: string;
    openLabel?: string;
    statusColumnLabel?: string;
    dateColumnLabel?: string;
    searchPlaceholder?: string;
    nameField?: string;
    dateField?: string;
  className?: string;
}

export const BarList04: React.FC<BarList04Props> = ({
    data = [],
    title,
    progressValue = 78.2,
    fulfilledCount = 1543,
    fulfilledPercent = 78.2,
    openCount = 431,
    openPercent = 21.8,
    fulfilledLabel = 'Fulfilled',
    openLabel = 'Open',
    statusColumnLabel = 'Open orders',
    dateColumnLabel = 'Order date',
    searchPlaceholder = 'Search ID...',
    nameField = 'name',
    dateField = 'date',

    className
}) => {
    const [searchQuery, setSearchQuery] = React.useState('');
    const filteredItems = data.filter((item) =>
        String(item[nameField]).toLowerCase().includes(searchQuery.toLowerCase()),
    );

    const formatNumber = (num: number) =>
        Intl.NumberFormat('us').format(num).toString();

    return (
        <div className={cx(className)}>
            <Card className="sm:mx-auto sm:max-w-lg">
                <h3 className="font-medium text-gray-900 dark:text-gray-50">
                    {title}
                </h3>
                <ProgressBar
                    value={progressValue}
                    className="mt-6 [&>*]:bg-gray-200 [&>*]:dark:bg-gray-700"
                />
                <ul role="list" className="mt-4 flex items-center justify-between">
                    <li className="flex space-x-2.5">
                        <span
                            className="flex w-0.5 bg-blue-500 dark:bg-blue-500"
                            aria-hidden={true}
                        />
                        <div className="space-y-0.5">
                            <p className="text-sm text-gray-500 dark:text-gray-500">
                                {fulfilledLabel}
                            </p>
                            <p className="font-semibold text-gray-900 dark:text-gray-50">
                                {formatNumber(fulfilledCount)}{' '}
                                <span className="font-normal text-gray-500 dark:text-gray-500">
                                    ({fulfilledPercent}%)
                                </span>
                            </p>
                        </div>
                    </li>
                    <li className="flex justify-end space-x-2.5">
                        <div className="space-y-0.5">
                            <p className="text-right text-sm text-gray-500 dark:text-gray-500">
                                {openLabel}
                            </p>
                            <p className="font-semibold text-gray-900 dark:text-gray-50">
                                {formatNumber(openCount)}{' '}
                                <span className="font-normal text-gray-500 dark:text-gray-500">
                                    ({openPercent}%)
                                </span>
                            </p>
                        </div>
                        <span
                            className="flex w-0.5 bg-gray-200 dark:bg-gray-800"
                            aria-hidden={true}
                        />
                    </li>
                </ul>
                <div className="mt-6 flex items-center justify-between">
                    <p className="text-xs font-medium uppercase tracking-wide text-gray-900 dark:text-gray-50">
                        {statusColumnLabel}
                    </p>
                    <p className="text-xs font-medium uppercase tracking-wide text-gray-900 dark:text-gray-50">
                        {dateColumnLabel}
                    </p>
                </div>
                <ul
                    role="list"
                    className="divide-y divide-gray-200 text-sm text-gray-500 dark:divide-gray-800 dark:text-gray-500"
                >
                    {data.slice(0, 5).map((item, idx) => (
                        <li
                            key={idx}
                            className="flex items-center justify-between py-1.5"
                        >
                            <span>{item[nameField]}</span>
                            <span>{item[dateField]}</span>
                        </li>
                    ))}
                </ul>
                <div className="absolute inset-x-0 bottom-0 flex justify-center rounded-b-lg bg-gradient-to-t from-white to-transparent dark:from-[#090E1A] py-7">
                    <Dialog>
                        <DialogTrigger asChild>
                            <Button variant="secondary">Show more</Button>
                        </DialogTrigger>
                        <DialogContent className="!p-0">
                            <DialogHeader className="px-6 pb-4 pt-6">
                                <Input
                                    type="search"
                                    placeholder={searchPlaceholder}
                                    value={searchQuery}
                                    onChange={(event) => setSearchQuery(event.target.value)}
                                />
                                <DialogTitle className="mt-4 flex items-center justify-between">
                                    <p className="text-sm font-medium text-gray-900 dark:text-gray-50">
                                        {statusColumnLabel}
                                    </p>
                                    <p className="text-xs font-medium uppercase text-gray-700 dark:text-gray-300">
                                        {dateColumnLabel}
                                    </p>
                                </DialogTitle>
                            </DialogHeader>
                            <div className="h-96 overflow-y-scroll px-6">
                                {filteredItems.length > 0 ? (
                                    <ul
                                        role="list"
                                        className="divide-y divide-gray-200 text-sm text-gray-500 dark:divide-gray-800 dark:text-gray-500"
                                    >
                                        {filteredItems.map((item, idx) => (
                                            <li
                                                key={idx}
                                                className="flex items-center justify-between py-2"
                                            >
                                                <span>{item[nameField]}</span>
                                                <span className="tabular-nums">{item[dateField]}</span>
                                            </li>
                                        ))}
                                    </ul>
                                ) : (
                                    <p className="flex h-full items-center justify-center text-sm text-gray-900 dark:text-gray-50">
                                        No results.
                                    </p>
                                )}
                            </div>
                            <DialogFooter className="mt-4 border-t border-gray-200 bg-gray-50 p-6 dark:border-gray-900 dark:bg-gray-950">
                                <DialogClose asChild>
                                    <Button className="w-full" variant="secondary">
                                        Go back
                                    </Button>
                                </DialogClose>
                            </DialogFooter>
                        </DialogContent>
                    </Dialog>
                </div>
            </Card>
        </div>
    );
};
