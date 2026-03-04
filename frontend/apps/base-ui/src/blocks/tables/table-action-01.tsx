'use client';

import React from 'react';
import { RiArrowDownSLine, RiArrowUpSLine } from '@remixicon/react';
import {
    flexRender,
    getCoreRowModel,
    getSortedRowModel,
    SortDirection,
    useReactTable,
    ColumnDef,
} from '@tanstack/react-table';

import { cx } from '../../lib/utils';

import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeaderCell,
    TableRoot,
    TableRow,
} from '../../tremor/components/Table';

// ─── @tanstack/react-table meta augmentation ──────────────────────────────────

declare module '@tanstack/react-table' {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    interface ColumnMeta<TData, TValue> {
        align?: string;
    }
}

// ─── Types ────────────────────────────────────────────────────────────────────

/** Demo row shape — kept for use in TableAction01Example */
export interface WorkspaceData {
    workspace: string;
    owner: string;
    status: 'live' | 'inactive';
    costs: string;
    region: string;
    capacity: string;
    lastEdited: string;
}

export interface TableAction01Props<TData extends object = WorkspaceData> {
    data?: TData[];
    columns?: ColumnDef<TData>[];
    initialSortId?: string;
    initialSortDesc?: boolean;
    className?: string;
}

// ─── Component ────────────────────────────────────────────────────────────────

/**
 * TableAction01: Generic sortable table backed by @tanstack/react-table.
 * Accepts any row shape — suitable for workspace monitoring, trade blotters,
 * portfolio holdings, order books, and more.
 *
 * @example
 * // Finance usage
 * <TableAction01<TradeRow>
 *   data={trades}
 *   columns={tradeColumns}
 *   initialSortId="executedAt"
 *   initialSortDesc
 * />
 */
export function TableAction01<TData extends object>({
    data = [],
    columns = [],
    initialSortId = 'workspace',
    initialSortDesc = false,
    className = '',
}: TableAction01Props<TData>) {
    const table = useReactTable({
        data,
        columns,
        getCoreRowModel: getCoreRowModel(),
        getSortedRowModel: getSortedRowModel(),
        initialState: {
            sorting: [
                {
                    id: initialSortId,
                    desc: initialSortDesc,
                },
            ],
        },
    });

    return (
        <div className={cx('obfuscate', className)}>
            <TableRoot>
                <Table>
                    <TableHead>
                        {table.getHeaderGroups().map((headerGroup) => (
                            <TableRow key={headerGroup.id}>
                                {headerGroup.headers.map((header) => {
                                    const sortingHandler =
                                        header.column.getToggleSortingHandler?.();
                                    const getAriaSortValue = (
                                        isSorted: false | SortDirection,
                                    ) => {
                                        switch (isSorted) {
                                            case 'asc':
                                                return 'ascending';
                                            case 'desc':
                                                return 'descending';
                                            case false:
                                            default:
                                                return 'none';
                                        }
                                    };

                                    return (
                                        <TableHeaderCell
                                            key={header.id}
                                            onClick={sortingHandler}
                                            onKeyDown={(event) => {
                                                if (event.key === 'Enter' && sortingHandler) {
                                                    sortingHandler(event);
                                                }
                                            }}
                                            className={cx(
                                                header.column.getCanSort()
                                                    ? 'cursor-pointer select-none'
                                                    : '',
                                                '!px-0.5 !py-1.5',
                                            )}
                                            tabIndex={header.column.getCanSort() ? 0 : -1}
                                            aria-sort={getAriaSortValue(
                                                header.column.getIsSorted(),
                                            )}
                                        >
                                            <div
                                                className={cx(
                                                    header.column.columnDef.enableSorting === true
                                                        ? 'flex items-center justify-between gap-2 hover:bg-gray-50 hover:dark:bg-gray-900'
                                                        : header.column.columnDef.meta?.align,
                                                    'rounded-md px-3 py-1.5',
                                                )}
                                            >
                                                {flexRender(
                                                    header.column.columnDef.header,
                                                    header.getContext(),
                                                )}
                                                {header.column.getCanSort() ? (
                                                    <div className="-space-y-2">
                                                        <RiArrowUpSLine
                                                            className={cx(
                                                                'size-4 text-gray-900 dark:text-gray-50',
                                                                header.column.getIsSorted() === 'desc'
                                                                    ? 'opacity-30'
                                                                    : '',
                                                            )}
                                                            aria-hidden={true}
                                                        />
                                                        <RiArrowDownSLine
                                                            className={cx(
                                                                'size-4 text-gray-900 dark:text-gray-50',
                                                                header.column.getIsSorted() === 'asc'
                                                                    ? 'opacity-30'
                                                                    : '',
                                                            )}
                                                            aria-hidden={true}
                                                        />
                                                    </div>
                                                ) : null}
                                            </div>
                                        </TableHeaderCell>
                                    );
                                })}
                            </TableRow>
                        ))}
                    </TableHead>
                    <TableBody>
                        {table.getRowModel().rows.map((row) => (
                            <TableRow key={row.id}>
                                {row.getVisibleCells().map((cell) => (
                                    <TableCell
                                        key={cell.id}
                                        className={cx(cell.column.columnDef.meta?.align)}
                                    >
                                        {flexRender(
                                            cell.column.columnDef.cell,
                                            cell.getContext(),
                                        )}
                                    </TableCell>
                                ))}
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableRoot>
        </div>
    );
}
