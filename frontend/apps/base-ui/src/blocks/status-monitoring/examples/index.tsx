import React from 'react';

import { Tracker01, Tracker01DataItem } from '../tracker-01';
import { Tracker02, Tracker02DataItem } from '../tracker-02';
import { Tracker03, Tracker03DataItem, Tracker03Status } from '../tracker-03';
import { Tracker04, Tracker04DataItem, TrackerIncident } from '../tracker-04';

export const Tracker01Example = () => {
    const data: Tracker01DataItem[] = [
        { tooltip: '23 Sep, 2023', status: 'Operational' },
        { tooltip: '24 Sep, 2023', status: 'Operational' },
        { tooltip: '25 Sep, 2023', status: 'Operational' },
        { tooltip: '26 Sep, 2023', status: 'Operational' },
        { tooltip: '27 Sep, 2023', status: 'Operational' },
        { tooltip: '28 Sep, 2023', status: 'Operational' },
        { tooltip: '29 Sep, 2023', status: 'Operational' },
        { tooltip: '30 Sep, 2023', status: 'Operational' },
        { tooltip: '1 Oct, 2023', status: 'Operational' },
        { tooltip: '2 Oct, 2023', status: 'Operational' },
        { tooltip: '3 Oct, 2023', status: 'Operational' },
        { tooltip: '4 Oct, 2023', status: 'Operational' },
        { tooltip: '5 Oct, 2023', status: 'Operational' },
        { tooltip: '6 Oct, 2023', status: 'Operational' },
        { tooltip: '7 Oct, 2023', status: 'Operational' },
        { tooltip: '8 Oct, 2023', status: 'Operational' },
        { tooltip: '9 Oct, 2023', status: 'Operational' },
        { tooltip: '10 Oct, 2023', status: 'Operational' },
        { tooltip: '11 Oct, 2023', status: 'Operational' },
        { tooltip: '12 Oct, 2023', status: 'Operational' },
        { tooltip: '13 Oct, 2023', status: 'Operational' },
        { tooltip: '14 Oct, 2023', status: 'Operational' },
        { tooltip: '15 Oct, 2023', status: 'Operational' },
        { tooltip: '16 Oct, 2023', status: 'Operational' },
        { tooltip: '17 Oct, 2023', status: 'Operational' },
        { tooltip: '18 Oct, 2023', status: 'Operational' },
        { tooltip: '19 Oct, 2023', status: 'Operational' },
        { tooltip: '20 Oct, 2023', status: 'Operational' },
        { tooltip: '21 Oct, 2023', status: 'Downtime' },
        { tooltip: '22 Oct, 2023', status: 'Operational' },
        { tooltip: '23 Oct, 2023', status: 'Operational' },
        { tooltip: '24 Oct, 2023', status: 'Operational' },
        { tooltip: '25 Oct, 2023', status: 'Operational' },
        { tooltip: '26 Oct, 2023', status: 'Operational' },
        { tooltip: '27 Oct, 2023', status: 'Operational' },
        { tooltip: '28 Oct, 2023', status: 'Operational' },
        { tooltip: '29 Oct, 2023', status: 'Operational' },
        { tooltip: '30 Oct, 2023', status: 'Operational' },
        { tooltip: '31 Oct, 2023', status: 'Operational' },
        { tooltip: '1 Nov, 2023', status: 'Operational' },
        { tooltip: '2 Nov, 2023', status: 'Operational' },
        { tooltip: '3 Nov, 2023', status: 'Operational' },
        { tooltip: '4 Nov, 2023', status: 'Operational' },
        { tooltip: '5 Nov, 2023', status: 'Operational' },
        { tooltip: '6 Nov, 2023', status: 'Operational' },
        { tooltip: '7 Nov, 2023', status: 'Operational' },
        { tooltip: '8 Nov, 2023', status: 'Operational' },
        { tooltip: '9 Nov, 2023', status: 'Operational' },
        { tooltip: '10 Nov, 2023', status: 'Operational' },
        { tooltip: '11 Nov, 2023', status: 'Operational' },
        { tooltip: '12 Nov, 2023', status: 'Operational' },
        { tooltip: '13 Nov, 2023', status: 'Operational' },
        { tooltip: '14 Nov, 2023', status: 'Operational' },
        { tooltip: '15 Nov, 2023', status: 'Operational' },
        { tooltip: '16 Nov, 2023', status: 'Operational' },
        { tooltip: '17 Nov, 2023', status: 'Operational' },
        { tooltip: '18 Nov, 2023', status: 'Operational' },
        { tooltip: '19 Nov, 2023', status: 'Operational' },
        { tooltip: '20 Nov, 2023', status: 'Operational' },
        { tooltip: '21 Nov, 2023', status: 'Operational' },
        { tooltip: '22 Nov, 2023', status: 'Operational' },
        { tooltip: '23 Nov, 2023', status: 'Operational' },
        { tooltip: '24 Nov, 2023', status: 'Downtime' },
        { tooltip: '25 Nov, 2023', status: 'Operational' },
        { tooltip: '26 Nov, 2023', status: 'Operational' },
        { tooltip: '27 Nov, 2023', status: 'Operational' },
        { tooltip: '28 Nov, 2023', status: 'Operational' },
        { tooltip: '29 Nov, 2023', status: 'Operational' },
        { tooltip: '30 Nov, 2023', status: 'Operational' },
        { tooltip: '1 Dec, 2023', status: 'Operational' },
        { tooltip: '2 Dec, 2023', status: 'Operational' },
        { tooltip: '3 Dec, 2023', status: 'Operational' },
        { tooltip: '4 Dec, 2023', status: 'Operational' },
        { tooltip: '5 Dec, 2023', status: 'Operational' },
        { tooltip: '6 Dec, 2023', status: 'Operational' },
        { tooltip: '7 Dec, 2023', status: 'Operational' },
        { tooltip: '8 Dec, 2023', status: 'Operational' },
        { tooltip: '9 Dec, 2023', status: 'Operational' },
        { tooltip: '10 Dec, 2023', status: 'Operational' },
        { tooltip: '11 Dec, 2023', status: 'Operational' },
        { tooltip: '12 Dec, 2023', status: 'Operational' },
        { tooltip: '13 Dec, 2023', status: 'Operational' },
        { tooltip: '14 Dec, 2023', status: 'Operational' },
        { tooltip: '15 Dec, 2023', status: 'Operational' },
        { tooltip: '16 Dec, 2023', status: 'Operational' },
        { tooltip: '17 Dec, 2023', status: 'Operational' },
        { tooltip: '18 Dec, 2023', status: 'Operational' },
        { tooltip: '19 Dec, 2023', status: 'Operational' },
        { tooltip: '20 Dec, 2023', status: 'Operational' },
        { tooltip: '21 Dec, 2023', status: 'Operational' },
        { tooltip: '22 Dec, 2023', status: 'Operational' },
        { tooltip: '23 Dec, 2023', status: 'Operational' },
        { tooltip: '24 Dec, 2023', status: 'Operational' },
        { tooltip: '25 Dec, 2023', status: 'Operational' },
        { tooltip: '26 Dec, 2023', status: 'Operational' },
        { tooltip: '27 Dec, 2023', status: 'Operational' },
    ];

    return (
        <Tracker01
            data={data}
            serviceName="Lena's Website"
            displayName="example.com"
            uptime="99.9%"
            status="Operational"
        />
    );
};

export const Tracker02Example = () => {
    const data: Tracker02DataItem[] = Array.from({ length: 90 }, (_, i) => {
        const downtimeDays = [6, 28, 58];
        return {
            tooltip: new Date(2023, 8, 23 + i).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: '2-digit',
            }),
            status: downtimeDays.includes(i) ? 'Downtime' : 'Operational',
        };
    });

    return (
        <Tracker02
            data={data}
            serviceName="NYSE Exchange Link"
            displayName="exchange.nyse.com"
            uptime="99.7%"
            status="Operational"
            detailsTitle="Atypical high request volume"
            detailsContent="Exchange connectivity experienced elevated latency during pre-market hours. All systems restored by 08:45 EST."
        />
    );
};

export const Tracker03Example = () => {
    const data: Tracker03DataItem[] = Array.from({ length: 90 }, (_, i) => {
        let status: Tracker03Status = 'Operational';
        if (i < 15) {
            status = 'Inactive';
        } else if (i >= 15 && i < 20) {
            status = 'Degraded';
        } else if (i === 22) {
            status = 'Downtime';
        }

        return {
            tooltip: new Date(2023, 8, 23 + i).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: '2-digit',
            }),
            status,
        };
    });

    return (
        <Tracker03
            data={data}
            headerLabel="Monitored feeds:"
            items={[
                { name: 'equities-feed' },
                { name: 'fx-rates' },
                { name: 'options-chain' },
                { name: 'risk-engine' },
            ]}
            runningLabel="Running"
            nextRunLabel="Next run: 1 hour and 2 minutes"
            viewMoreLabel="View more →"
        />
    );
};

export const Tracker04Example = () => {
    const data: Tracker04DataItem[] = Array.from({ length: 90 }, (_, i) => ({
        tooltip: new Date(2023, 8, 23 + i).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: '2-digit',
        }),
        status: i === 6 || i === 28 || i === 58 ? 'Downtime' : 'Operational',
    }));

    const incidents: TrackerIncident[] = [
        { date: '29 Sep, 2023', duration: 'Down for 1 min' },
        { date: '21 Oct, 2023', duration: 'Down for 2 min' },
        { date: '24 Nov, 2023', duration: 'Down for 1 min' },
    ];

    return (
        <Tracker04
            data={data}
            serviceName="Market Data Feed"
            uptime="99.9%"
            status="Operational"
            incidents={incidents}
        />
    );
};

export const Tracker05Example = () => {
    const data: Tracker04DataItem[] = Array.from({ length: 90 }, (_, i) => {
        const downtimeDays = [6, 28, 58];
        return {
            tooltip: new Date(2023, 8, 23 + i).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: '2-digit',
            }),
            status: downtimeDays.includes(i) ? 'Downtime' : 'Operational',
        };
    });

    const incidents: TrackerIncident[] = [
        { date: '29 Sep, 2023', duration: 'Down for 1 min' },
        { date: '21 Oct, 2023', duration: 'Down for 2 min' },
        { date: '24 Nov, 2023', duration: 'Down for 1 min' },
    ];

    return (
        <Tracker04
            data={data}
            serviceName="API Gateway"
            uptime="99.9%"
            status="Operational"
            incidents={incidents}
            collapsibleIncidents={true}
        />
    );
};
