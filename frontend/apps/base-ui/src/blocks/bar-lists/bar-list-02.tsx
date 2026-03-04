import React from 'react';
import { BarList } from '../../tremor/components/BarList';
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
import { cx } from '../../lib/utils';

export interface BarListItem {
    name: string;
    value: number;
}

export interface BarList02Props {
    data?: BarListItem[];
    valueFormatter?: (value: number) => string;
    title?: string;
    subtitle?: string;
  className?: string;
}

function useResizeObserver(
    elementRef: React.RefObject<Element>,
): ResizeObserverEntry | undefined {
    const [entry, setEntry] = React.useState<ResizeObserverEntry>();

    const updateEntry = ([entry]: ResizeObserverEntry[]): void => {
        setEntry(entry);
    };

    React.useEffect(() => {
        const node = elementRef?.current;
        if (!node) return;

        const observer = new ResizeObserver(updateEntry);
        observer.observe(node);

        return () => observer.disconnect();
    }, [elementRef]);

    return entry;
}

const FilterScroll = React.forwardRef<
    HTMLDivElement,
    React.PropsWithChildren
>(({ children }, forwardedRef) => {
    const ref = React.useRef<HTMLDivElement>(null);
    React.useImperativeHandle(forwardedRef, () => ref.current as HTMLDivElement);

    const [scrollProgress, setScrollProgress] = React.useState(1);

    const updateScrollProgress = React.useCallback(() => {
        if (!ref.current) return;
        const { scrollTop, scrollHeight, clientHeight } = ref.current;

        setScrollProgress(
            scrollHeight === clientHeight ? 1 : scrollTop / (scrollHeight - clientHeight),
        );
    }, []);

    const resizeObserverEntry = useResizeObserver(ref);

    React.useEffect(updateScrollProgress, [resizeObserverEntry]);

    return (
        <>
            <div
                className="h-96 overflow-y-scroll py-4"
                ref={ref}
                onScroll={updateScrollProgress}
            >
                {children}
            </div>
            <div
                className="pointer-events-none absolute bottom-0 left-0 h-16 w-full bg-gradient-to-t from-white"
                style={{ opacity: 1 - Math.pow(scrollProgress, 2) }}
            ></div>
        </>
    );
});

FilterScroll.displayName = 'FilterScroll';

export const BarList02: React.FC<BarList02Props> = ({
    data = [],
    valueFormatter = (value) => `${value}`,
    title = 'Top Pages',
    subtitle = 'Visitors',

    className
}) => {
    const [searchQuery, setSearchQuery] = React.useState('');
    const filteredItems = data.filter((item) =>
        item.name.toLowerCase().includes(searchQuery.toLowerCase()),
    );
    const mainListContainer = React.useRef<HTMLDivElement>(null);

    return (
        <div className={cx(className)}>
            <Card className="!p-0 sm:mx-auto sm:max-w-lg">
                <div className="flex items-center justify-between border-b border-gray-200 p-6 dark:border-gray-900">
                    <p className="font-medium text-gray-900 dark:text-gray-50">
                        {title}
                    </p>
                    <p className="text-xs font-medium uppercase text-gray-500 dark:text-gray-500">
                        {subtitle}
                    </p>
                </div>
                <BarList
                    data={data.slice(0, 5)}
                    valueFormatter={valueFormatter}
                    className="p-6"
                />
                <div className="absolute inset-x-0 bottom-0 flex justify-center rounded-b-lg bg-gradient-to-t from-white to-transparent dark:from-[#090E1A] py-7">
                    <Dialog>
                        <DialogTrigger asChild>
                            <Button variant="secondary">Show more</Button>
                        </DialogTrigger>
                        <DialogContent className="!p-0">
                            <DialogHeader className="border-b border-gray-200 px-6 pb-4 pt-6 dark:border-gray-900">
                                <DialogTitle className="flex items-center justify-between">
                                    <p className="text-base font-medium text-gray-900 dark:text-gray-50">
                                        Pages
                                    </p>
                                    <p className="text-xs font-medium uppercase text-gray-500 dark:text-gray-500">
                                        {subtitle}
                                    </p>
                                </DialogTitle>
                                <Input
                                    type="search"
                                    placeholder="Search page..."
                                    className="mt-2"
                                    value={searchQuery}
                                    onChange={(event) => setSearchQuery(event.target.value)}
                                />
                            </DialogHeader>
                            <div className="relative pl-6">
                                <FilterScroll ref={mainListContainer}>
                                    {filteredItems.length > 0 ? (
                                        <BarList
                                            data={filteredItems}
                                            valueFormatter={valueFormatter}
                                            className="pr-6"
                                        />
                                    ) : (
                                        <p className="flex h-full items-center justify-center text-sm text-gray-900 dark:text-gray-50">
                                            No results.
                                        </p>
                                    )}
                                </FilterScroll>
                            </div>
                            <DialogFooter className="border-t border-gray-200 bg-gray-50 px-6 py-6 dark:border-gray-900 dark:bg-[#090E1A]">
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
