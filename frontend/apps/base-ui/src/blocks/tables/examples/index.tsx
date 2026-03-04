'use client';

import React from 'react';
import { ColumnDef } from '@tanstack/react-table';

import { Table01, TableColumn, statusBadge } from '../table-01';
import { TableAction01, WorkspaceData } from '../table-action-01';

// ─── Table01Example ───────────────────────────────────────────────────────────

interface WorkspaceItem extends Record<string, unknown> {
    workspace: string;
    owner: string;
    status: string;
    costs: string;
    region: string;
    capacity: string;
}

const workspaceColumns: TableColumn<WorkspaceItem>[] = [
    { key: 'workspace', label: 'Workspace' },
    { key: 'owner', label: 'Owner' },
    { key: 'status', label: 'Status', render: (v) => statusBadge(String(v)) },
    { key: 'costs', label: 'Costs', align: 'right' },
    { key: 'region', label: 'Region' },
    { key: 'capacity', label: 'Capacity', align: 'right' },
];

const workspaceData: WorkspaceItem[] = [
    { workspace: 'sales_by_day_api', owner: 'John Doe', status: 'Live', costs: '$3,509.00', region: 'US-West 1', capacity: '31.1%' },
    { workspace: 'marketing_campaign', owner: 'Jane Smith', status: 'Live', costs: '$5,720.00', region: 'US-East 2', capacity: '81.3%' },
    { workspace: 'test_environment', owner: 'David Clark', status: 'Inactive', costs: '$800.00', region: 'EU-Central 1', capacity: '40.8%' },
    { workspace: 'sales_campaign', owner: 'Emma Stone', status: 'Downtime', costs: '$5,720.00', region: 'US-East 2', capacity: '51.4%' },
    { workspace: 'development_env', owner: 'Mike Johnson', status: 'Inactive', costs: '$4,200.00', region: 'EU-West 1', capacity: '60.4%' },
    { workspace: 'new_workspace_1', owner: 'Alice Brown', status: 'Inactive', costs: '$2,100.00', region: 'US-West 2', capacity: '75.9%' },
];

export const Table01Example = () => (
    <Table01
        data={workspaceData}
        columns={workspaceColumns}
        getRowKey={(row) => row.workspace}
    />
);

// ─── TableAction01Example ─────────────────────────────────────────────────────

const workspaces: WorkspaceData[] = [
    { workspace: 'sales_by_day_api', owner: 'John Doe', status: 'live', costs: '$3,509.00', region: 'US-West 1', capacity: '99%', lastEdited: '23/09/2023 13:00' },
    { workspace: 'marketing_campaign', owner: 'Jane Smith', status: 'live', costs: '$5,720.00', region: 'US-East 2', capacity: '80%', lastEdited: '22/09/2023 10:45' },
    { workspace: 'sales_campaign', owner: 'Jane Smith', status: 'live', costs: '$5,720.00', region: 'US-East 2', capacity: '80%', lastEdited: '22/09/2023 10:45' },
    { workspace: 'development_env', owner: 'Mike Johnson', status: 'live', costs: '$4,200.00', region: 'EU-West 1', capacity: '60%', lastEdited: '21/09/2023 14:30' },
    { workspace: 'new_workspace_1', owner: 'Alice Brown', status: 'live', costs: '$2,100.00', region: 'US-West 2', capacity: '75%', lastEdited: '24/09/2023 09:15' },
    { workspace: 'test_environment', owner: 'David Clark', status: 'inactive', costs: '$800.00', region: 'EU-Central 1', capacity: '40%', lastEdited: '25/09/2023 16:20' },
    { workspace: 'analytics_dashboard', owner: 'Sarah Wilson', status: 'live', costs: '$6,500.00', region: 'US-West 1', capacity: '90%', lastEdited: '26/09/2023 11:30' },
    { workspace: 'research_project', owner: 'Michael Adams', status: 'live', costs: '$3,900.00', region: 'US-East 1', capacity: '70%', lastEdited: '27/09/2023 08:45' },
    { workspace: 'training_environment', owner: 'Laura White', status: 'live', costs: '$2,500.00', region: 'EU-North 1', capacity: '55%', lastEdited: '28/09/2023 12:15' },
];

const workspacesColumns: ColumnDef<WorkspaceData>[] = [
    { header: 'Workspace', accessorKey: 'workspace', enableSorting: true, meta: { align: 'text-left' } },
    { header: 'Owner', accessorKey: 'owner', enableSorting: true, meta: { align: 'text-left' } },
    { header: 'Status', accessorKey: 'status', enableSorting: false, meta: { align: 'text-left' } },
    { header: 'Region', accessorKey: 'region', enableSorting: false, meta: { align: 'text-left' } },
    { header: 'Capacity', accessorKey: 'capacity', enableSorting: false, meta: { align: 'text-left' } },
    { header: 'Costs', accessorKey: 'costs', enableSorting: false, meta: { align: 'text-right' } },
    { header: 'Last edited', accessorKey: 'lastEdited', enableSorting: false, meta: { align: 'text-right' } },
];

export const TableAction01Example = () => (
    <TableAction01
        data={workspaces}
        columns={workspacesColumns}
        initialSortId="workspace"
        initialSortDesc={false}
    />
);
