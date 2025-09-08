import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { AreaClosed, LinePath } from '@visx/shape';
import { scaleTime, scaleLinear } from '@visx/scale';
import { Group } from '@visx/group';
import { GridRows, GridColumns } from '@visx/grid';
import { AxisLeft, AxisBottom } from '@visx/axis';
import { ParentSize } from '@visx/responsive';

// Mock data - in real app would come from Alpaca APIs
const mockPortfolioHistory = [
  { date: new Date('2024-08-08'), equity: 98500, pnl: -1500 },
  { date: new Date('2024-08-09'), equity: 99200, pnl: -800 },
  { date: new Date('2024-08-12'), equity: 100800, pnl: 800 },
  { date: new Date('2024-08-13'), equity: 99500, pnl: -500 },
  { date: new Date('2024-08-14'), equity: 101200, pnl: 1200 },
  { date: new Date('2024-08-15'), equity: 102500, pnl: 2500 },
  { date: new Date('2024-08-16'), equity: 101800, pnl: 1800 },
  { date: new Date('2024-08-19'), equity: 103200, pnl: 3200 },
  { date: new Date('2024-08-20'), equity: 104100, pnl: 4100 },
  { date: new Date('2024-08-21'), equity: 102900, pnl: 2900 },
  { date: new Date('2024-08-22'), equity: 105200, pnl: 5200 },
  { date: new Date('2024-08-23'), equity: 104800, pnl: 4800 },
  { date: new Date('2024-08-26'), equity: 106500, pnl: 6500 },
  { date: new Date('2024-08-27'), equity: 105900, pnl: 5900 },
  { date: new Date('2024-08-28'), equity: 107200, pnl: 7200 },
  { date: new Date('2024-08-29'), equity: 106800, pnl: 6800 },
  { date: new Date('2024-08-30'), equity: 108500, pnl: 8500 },
  { date: new Date('2024-09-03'), equity: 107900, pnl: 7900 },
  { date: new Date('2024-09-04'), equity: 109200, pnl: 9200 },
  { date: new Date('2024-09-05'), equity: 108600, pnl: 8600 },
];

const mockPositions = [
  { symbol: 'AAPL', qty: 50, market_value: 8750, unrealized_pl: 450, unrealized_plpc: 0.0541 },
  { symbol: 'MSFT', qty: 25, market_value: 10500, unrealized_pl: -125, unrealized_plpc: -0.0117 },
  { symbol: 'GOOGL', qty: 15, market_value: 2250, unrealized_pl: 75, unrealized_plpc: 0.0345 },
  { symbol: 'TSLA', qty: 30, market_value: 6300, unrealized_pl: -180, unrealized_plpc: -0.0278 },
];

const mockActivities = [
  { id: '1', activity_type: 'FILL', symbol: 'AAPL', side: 'buy', qty: 10, price: 175.25, transaction_time: '2024-09-05T14:30:00Z' },
  { id: '2', activity_type: 'FILL', symbol: 'MSFT', side: 'sell', qty: 5, price: 420.50, transaction_time: '2024-09-04T10:15:00Z' },
  { id: '3', activity_type: 'DIV', symbol: 'AAPL', gross_amount: 23.50, transaction_time: '2024-09-03T09:00:00Z' },
  { id: '4', activity_type: 'FILL', symbol: 'GOOGL', side: 'buy', qty: 5, price: 150.75, transaction_time: '2024-09-02T15:45:00Z' },
];

const mockAccount = {
  portfolio_value: '108600.00',
  buying_power: '12450.00',
  cash: '4250.00',
  equity: '108600.00',
  last_equity: '100000.00'
};

// Accessor functions for visx
const getDate = (d: any) => d.date;
const getEquity = (d: any) => d.equity;

export default function TradingPerformanceDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  
  const totalReturn = parseFloat(mockAccount.portfolio_value) - parseFloat(mockAccount.last_equity);
  const returnPercentage = (totalReturn / parseFloat(mockAccount.last_equity)) * 100;
  
  const winningTrades = mockActivities.filter(a => a.activity_type === 'FILL').length;
  const dividendIncome = mockActivities.filter(a => a.activity_type === 'DIV')
    .reduce((sum, a) => sum + (a.gross_amount || 0), 0);

  const totalMarketValue = mockPositions.reduce((sum, pos) => sum + pos.market_value, 0);

  return (
    <div style={{ padding: '16px', maxHeight: '100vh', overflow: 'hidden' }}>
      {/* Header Stats Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '16px' }}>
        <Card style={{ padding: '12px' }}>
          <CardHeader style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingBottom: '8px', padding: 0 }}>
            <CardTitle style={{ fontSize: '14px', fontWeight: '500' }}>Portfolio Value</CardTitle>
            <svg style={{ height: '16px', width: '16px', opacity: 0.6 }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
            </svg>
          </CardHeader>
          <CardContent style={{ padding: 0 }}>
            <div style={{ fontSize: '20px', fontWeight: 'bold' }}>${parseFloat(mockAccount.portfolio_value).toLocaleString()}</div>
            <p style={{ fontSize: '12px', color: returnPercentage >= 0 ? '#16a34a' : '#dc2626' }}>
              {returnPercentage >= 0 ? '+' : ''}${totalReturn.toLocaleString()} 
              ({returnPercentage >= 0 ? '+' : ''}{returnPercentage.toFixed(2)}%)
            </p>
          </CardContent>
        </Card>
        
        <Card style={{ padding: '12px' }}>
          <CardHeader style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingBottom: '8px', padding: 0 }}>
            <CardTitle style={{ fontSize: '14px', fontWeight: '500' }}>Buying Power</CardTitle>
            <svg style={{ height: '16px', width: '16px', opacity: 0.6 }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
            </svg>
          </CardHeader>
          <CardContent style={{ padding: 0 }}>
            <div style={{ fontSize: '20px', fontWeight: 'bold' }}>${parseFloat(mockAccount.buying_power).toLocaleString()}</div>
            <p style={{ fontSize: '12px', opacity: 0.6 }}>Available to trade</p>
          </CardContent>
        </Card>
        
        <Card style={{ padding: '12px' }}>
          <CardHeader style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingBottom: '8px', padding: 0 }}>
            <CardTitle style={{ fontSize: '14px', fontWeight: '500' }}>Cash Balance</CardTitle>
            <svg style={{ height: '16px', width: '16px', opacity: 0.6 }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </CardHeader>
          <CardContent style={{ padding: 0 }}>
            <div style={{ fontSize: '20px', fontWeight: 'bold' }}>${parseFloat(mockAccount.cash).toLocaleString()}</div>
            <p style={{ fontSize: '12px', opacity: 0.6 }}>Uninvested cash</p>
          </CardContent>
        </Card>
        
        <Card style={{ padding: '12px' }}>
          <CardHeader style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingBottom: '8px', padding: 0 }}>
            <CardTitle style={{ fontSize: '14px', fontWeight: '500' }}>Total Trades</CardTitle>
            <svg style={{ height: '16px', width: '16px', opacity: 0.6 }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          </CardHeader>
          <CardContent style={{ padding: 0 }}>
            <div style={{ fontSize: '20px', fontWeight: 'bold' }}>{winningTrades}</div>
            <p style={{ fontSize: '12px', color: '#16a34a' }}>+${dividendIncome.toFixed(2)} dividends</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Dashboard Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <TabsList style={{ display: 'grid', width: '100%', gridTemplateColumns: 'repeat(3, 1fr)' }}>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="positions">Positions</TabsTrigger>
          <TabsTrigger value="activity">Activity</TabsTrigger>
        </TabsList>
        
        <TabsContent value="overview" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', height: '320px' }}>
            {/* Portfolio Performance Chart */}
            <Card>
              <CardHeader>
                <CardTitle style={{ fontSize: '16px' }}>Portfolio Performance (30 Days)</CardTitle>
              </CardHeader>
              <CardContent style={{ height: '256px' }}>
                <ParentSize>
                  {({ width, height }) => {
                    const margin = { top: 10, right: 10, bottom: 30, left: 50 };
                    const innerWidth = width - margin.left - margin.right;
                    const innerHeight = height - margin.top - margin.bottom;
                    
                    const xScale = scaleTime({
                      range: [0, innerWidth],
                      domain: [Math.min(...mockPortfolioHistory.map(getDate)), Math.max(...mockPortfolioHistory.map(getDate))],
                    });
                    
                    const yScale = scaleLinear({
                      range: [innerHeight, 0],
                      domain: [Math.min(...mockPortfolioHistory.map(getEquity)), Math.max(...mockPortfolioHistory.map(getEquity))],
                    });
                    
                    return (
                      <svg width={width} height={height}>
                        <Group left={margin.left} top={margin.top}>
                          <GridRows scale={yScale} width={innerWidth} strokeDasharray="2,2" stroke="#e2e8f0" />
                          <GridColumns scale={xScale} height={innerHeight} strokeDasharray="2,2" stroke="#e2e8f0" />
                          <AreaClosed
                            data={mockPortfolioHistory}
                            x={(d) => xScale(getDate(d)) ?? 0}
                            y={(d) => yScale(getEquity(d)) ?? 0}
                            yScale={yScale}
                            strokeWidth={2}
                            stroke="#3b82f6"
                            fill="#3b82f6"
                            fillOpacity={0.1}
                          />
                          <LinePath
                            data={mockPortfolioHistory}
                            x={(d) => xScale(getDate(d)) ?? 0}
                            y={(d) => yScale(getEquity(d)) ?? 0}
                            stroke="#3b82f6"
                            strokeWidth={2}
                          />
                          <AxisLeft
                            scale={yScale}
                            tickFormat={(value) => `$${(Number(value)/1000).toFixed(0)}k`}
                            tickLabelProps={{ fontSize: 10, fill: '#64748b' }}
                          />
                          <AxisBottom
                            top={innerHeight}
                            scale={xScale}
                            tickFormat={(value) => new Date(Number(value)).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                            tickLabelProps={{ fontSize: 10, fill: '#64748b' }}
                          />
                        </Group>
                      </svg>
                    );
                  }}
                </ParentSize>
              </CardContent>
            </Card>

            {/* Position Allocation */}
            <Card>
              <CardHeader>
                <CardTitle style={{ fontSize: '16px' }}>Position Allocation</CardTitle>
              </CardHeader>
              <CardContent style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {mockPositions.map((position) => {
                  const percentage = (position.market_value / totalMarketValue) * 100;
                  const isPositive = position.unrealized_pl >= 0;
                  return (
                    <div key={position.symbol} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontWeight: '500', fontSize: '14px' }}>{position.symbol}</span>
                        <div style={{ textAlign: 'right' }}>
                          <div style={{ fontSize: '14px', fontWeight: '500' }}>${position.market_value.toLocaleString()}</div>
                          <div style={{ fontSize: '12px', color: isPositive ? '#16a34a' : '#dc2626' }}>
                            {isPositive ? '+' : ''}${position.unrealized_pl} ({percentage.toFixed(1)}%)
                          </div>
                        </div>
                      </div>
                      <Progress value={percentage} style={{ height: '8px' }} />
                    </div>
                  );
                })}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="positions" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <Card>
            <CardHeader>
              <CardTitle style={{ fontSize: '16px' }}>Current Positions</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Symbol</TableHead>
                    <TableHead>Shares</TableHead>
                    <TableHead>Market Value</TableHead>
                    <TableHead>Unrealized P&L</TableHead>
                    <TableHead>% Change</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockPositions.map((position) => (
                    <TableRow key={position.symbol}>
                      <TableCell style={{ fontWeight: '500' }}>{position.symbol}</TableCell>
                      <TableCell>{position.qty}</TableCell>
                      <TableCell>${position.market_value.toLocaleString()}</TableCell>
                      <TableCell style={{ color: position.unrealized_pl >= 0 ? '#16a34a' : '#dc2626' }}>
                        {position.unrealized_pl >= 0 ? '+' : ''}${position.unrealized_pl.toLocaleString()}
                      </TableCell>
                      <TableCell style={{ color: position.unrealized_plpc >= 0 ? '#16a34a' : '#dc2626' }}>
                        {position.unrealized_plpc >= 0 ? '+' : ''}{(position.unrealized_plpc * 100).toFixed(2)}%
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="activity" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <Card>
            <CardHeader>
              <CardTitle style={{ fontSize: '16px' }}>Recent Activity (30 Days)</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Date</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Symbol</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead>Amount</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockActivities.map((activity) => (
                    <TableRow key={activity.id}>
                      <TableCell>
                        {new Date(activity.transaction_time).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <Badge 
                          variant={
                            activity.activity_type === 'FILL' ? 'default' :
                            activity.activity_type === 'DIV' ? 'secondary' :
                            'outline'
                          }
                        >
                          {activity.activity_type}
                        </Badge>
                      </TableCell>
                      <TableCell style={{ fontWeight: '500' }}>{activity.symbol}</TableCell>
                      <TableCell>
                        {activity.activity_type === 'FILL' 
                          ? `${activity.side?.toUpperCase()} ${activity.qty} shares @ $${activity.price}`
                          : 'Dividend payment'
                        }
                      </TableCell>
                      <TableCell>
                        {activity.activity_type === 'FILL' 
                          ? `$${(activity.qty * activity.price).toLocaleString()}`
                          : `$${activity.gross_amount?.toLocaleString()}`
                        }
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}