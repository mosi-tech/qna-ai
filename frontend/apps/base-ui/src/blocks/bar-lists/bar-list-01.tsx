import React from 'react';
import { BarList } from '../../tremor/components/BarList';
import { Button } from '../../tremor/components/Button';
import { Card } from '../../tremor/components/Card';
import { cx } from '../../lib/utils';

export interface BarListItem {
    name: string;
    value: number;
}

export interface BarList01Props {
    data?: BarListItem[];
    valueFormatter?: (value: number) => string;
    title: string;
    subtitle: string;
  className?: string;
}

export const BarList01: React.FC<BarList01Props> = ({
    data = [],
    valueFormatter = (value) => `${value}`,
    title,
    subtitle,

    className
}) => {
    const [extended, setExtended] = React.useState(false);

    if (!data || data.length === 0) {
        return null;
    }

    return (
        <Card className={cx('!p-0 sm:mx-auto sm:max-w-lg', className)}>
            <div className="flex items-center justify-between border-b border-gray-200 p-6 dark:border-gray-900">
                <p className="font-medium text-gray-900 dark:text-gray-50">
                    {title}
                </p>
                <p className="text-xs font-medium uppercase text-gray-500 dark:text-gray-500">
                    {subtitle}
                </p>
            </div>
            <div
                className={`overflow-hidden p-6 ${extended ? '' : 'max-h-[260px]'}`}
            >
                <BarList data={data} valueFormatter={valueFormatter} />
            </div>
            <div
                className={`flex justify-center ${extended
                    ? 'px-6 pb-6'
                    : 'absolute inset-x-0 bottom-0 rounded-b-lg bg-gradient-to-t from-white to-transparent dark:from-[#090E1A] py-7'
                    }`}
            >
                <Button variant="secondary" onClick={() => setExtended(!extended)}>
                    {extended ? 'Show less' : 'Show more'}
                </Button>
            </div>
        </Card>
    );
};
