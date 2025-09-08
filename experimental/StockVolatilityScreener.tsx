import React, { useState } from 'react';

interface VolatilityData {
  symbol: string;
  name: string;
  currentPrice: number;
  volatility: number;
  averageVolume: number;
  priceChange: number;
  priceChangePercent: number;
  riskLevel: 'Low' | 'Medium' | 'High' | 'Extreme';
}

const StockVolatilityScreener: React.FC = () => {
  const [sortBy, setSortBy] = useState<'volatility' | 'price' | 'volume'>('volatility');
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [itemsPerPage, setItemsPerPage] = useState<number>(5);
  const [topN, setTopN] = useState<number>(8); // Top N stocks to analyze

  const volatilityData: VolatilityData[] = [
    {
      symbol: 'NVDA',
      name: 'NVIDIA Corp',
      currentPrice: 442.50,
      volatility: 62.5,
      averageVolume: 45200000,
      priceChange: -8.25,
      priceChangePercent: -1.83,
      riskLevel: 'Extreme'
    },
    {
      symbol: 'TSLA',
      name: 'Tesla Inc',
      currentPrice: 248.42,
      volatility: 58.2,
      averageVolume: 82100000,
      priceChange: 12.15,
      priceChangePercent: 5.14,
      riskLevel: 'Extreme'
    },
    {
      symbol: 'AMD',
      name: 'Advanced Micro Devices',
      currentPrice: 142.18,
      volatility: 54.7,
      averageVolume: 51300000,
      priceChange: -2.82,
      priceChangePercent: -1.94,
      riskLevel: 'High'
    },
    {
      symbol: 'META',
      name: 'Meta Platforms Inc',
      currentPrice: 502.34,
      volatility: 47.3,
      averageVolume: 18600000,
      priceChange: 15.67,
      priceChangePercent: 3.22,
      riskLevel: 'High'
    },
    {
      symbol: 'AAPL',
      name: 'Apple Inc',
      currentPrice: 220.85,
      volatility: 35.1,
      averageVolume: 45800000,
      priceChange: 2.45,
      priceChangePercent: 1.12,
      riskLevel: 'Medium'
    },
    {
      symbol: 'MSFT',
      name: 'Microsoft Corp',
      currentPrice: 420.15,
      volatility: 28.9,
      averageVolume: 25100000,
      priceChange: 5.82,
      priceChangePercent: 1.40,
      riskLevel: 'Medium'
    },
    {
      symbol: 'JNJ',
      name: 'Johnson & Johnson',
      currentPrice: 165.42,
      volatility: 18.7,
      averageVolume: 8200000,
      priceChange: 0.85,
      priceChangePercent: 0.52,
      riskLevel: 'Low'
    },
    {
      symbol: 'KO',
      name: 'Coca-Cola Co',
      currentPrice: 62.88,
      volatility: 15.2,
      averageVolume: 12500000,
      priceChange: -0.12,
      priceChangePercent: -0.19,
      riskLevel: 'Low'
    }
  ];

  const formatPrice = (price: number) => `$${price.toFixed(2)}`;
  const formatVolume = (volume: number) => {
    if (volume >= 1000000) return `${(volume / 1000000).toFixed(1)}M`;
    if (volume >= 1000) return `${(volume / 1000).toFixed(0)}K`;
    return volume.toString();
  };

  const getSortedData = () => {
    return [...volatilityData].sort((a, b) => {
      switch (sortBy) {
        case 'volatility': return b.volatility - a.volatility;
        case 'price': return b.currentPrice - a.currentPrice;
        case 'volume': return b.averageVolume - a.averageVolume;
        default: return 0;
      }
    });
  };

  const getTopNData = () => {
    const sortedData = getSortedData();
    return sortedData.slice(0, Math.min(topN, sortedData.length));
  };

  const getPaginatedData = () => {
    const topNData = getTopNData();
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return topNData.slice(startIndex, endIndex);
  };

  const totalPages = Math.ceil(Math.min(topN, volatilityData.length) / itemsPerPage);

  const riskCounts = {
    extreme: volatilityData.filter(s => s.riskLevel === 'Extreme').length,
    high: volatilityData.filter(s => s.riskLevel === 'High').length,
    medium: volatilityData.filter(s => s.riskLevel === 'Medium').length,
    low: volatilityData.filter(s => s.riskLevel === 'Low').length
  };

  const avgVolatility = volatilityData.reduce((sum, s) => sum + s.volatility, 0) / volatilityData.length;

  const styles = {
    container: {
      padding: '16px',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      backgroundColor: '#fff',
      height: 'auto',
      maxHeight: '100vh',
      overflow: 'hidden'
    },
    header: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: '16px',
      paddingBottom: '12px',
      borderBottom: '1px solid #e5e5e5'
    },
    title: {
      fontSize: '24px',
      fontWeight: '600',
      color: '#1a1a1a',
      margin: '0'
    },
    stats: {
      display: 'grid',
      gridTemplateColumns: 'repeat(4, 1fr)',
      gap: '12px',
      marginBottom: '16px'
    },
    statCard: {
      backgroundColor: '#f8f9fa',
      border: '1px solid #e9ecef',
      borderRadius: '8px',
      padding: '12px',
      textAlign: 'center' as const
    },
    statLabel: {
      fontSize: '11px',
      color: '#666',
      fontWeight: '500',
      marginBottom: '4px'
    },
    statValue: {
      fontSize: '20px',
      fontWeight: '600',
      color: '#1a1a1a'
    },
    controls: {
      display: 'flex',
      gap: '12px',
      alignItems: 'center',
      marginBottom: '16px'
    },
    select: {
      padding: '6px 10px',
      border: '1px solid #d1d1d1',
      borderRadius: '6px',
      backgroundColor: '#fff',
      fontSize: '12px',
      fontWeight: '500',
      cursor: 'pointer',
      outline: 'none'
    },
    table: {
      border: '1px solid #e5e5e5',
      borderRadius: '8px',
      overflow: 'hidden',
      maxHeight: '400px',
      overflowY: 'auto' as const
    },
    th: {
      padding: '10px 12px',
      textAlign: 'left' as const,
      fontSize: '12px',
      fontWeight: '600',
      color: '#666'
    },
    td: {
      padding: '10px 12px',
      borderBottom: '1px solid #f0f0f0',
      fontSize: '12px'
    },
    symbol: {
      fontWeight: '600',
      fontSize: '13px',
      color: '#1a1a1a',
      marginBottom: '1px'
    },
    company: {
      fontSize: '10px',
      color: '#666',
      fontWeight: '400'
    },
    price: {
      fontWeight: '600',
      fontSize: '13px',
      color: '#1a1a1a'
    },
    change: {
      fontWeight: '600',
      fontSize: '12px'
    },
    positive: {
      color: '#16a34a'
    },
    negative: {
      color: '#dc2626'
    },
    volatilityBar: {
      width: '100%',
      height: '4px',
      backgroundColor: '#f0f0f0',
      borderRadius: '2px',
      overflow: 'hidden',
      marginTop: '3px'
    },
    volatilityFill: {
      height: '100%',
      backgroundColor: '#3b82f6',
      borderRadius: '2px',
      transition: 'width 0.3s ease'
    },
    badge: {
      padding: '2px 6px',
      borderRadius: '4px',
      fontSize: '10px',
      fontWeight: '600',
      display: 'inline-block'
    },
    extremeBadge: {
      backgroundColor: '#fee2e2',
      color: '#991b1b'
    },
    highBadge: {
      backgroundColor: '#fef3c7',
      color: '#92400e'
    },
    mediumBadge: {
      backgroundColor: '#dbeafe',
      color: '#1e40af'
    },
    lowBadge: {
      backgroundColor: '#dcfce7',
      color: '#166534'
    }
  };

  const getRiskBadgeStyle = (riskLevel: string) => {
    switch (riskLevel) {
      case 'Extreme': return { ...styles.badge, ...styles.extremeBadge };
      case 'High': return { ...styles.badge, ...styles.highBadge };
      case 'Medium': return { ...styles.badge, ...styles.mediumBadge };
      case 'Low': return { ...styles.badge, ...styles.lowBadge };
      default: return styles.badge;
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Stock Volatility Screener</h1>
        <div style={styles.controls}>
          <label style={{ fontSize: '12px', fontWeight: '500', color: '#666' }}>
            Analyze:
          </label>
          <select
            value={topN}
            onChange={(e) => {
              setTopN(Number(e.target.value));
              setCurrentPage(1); // Reset to first page
            }}
            style={styles.select}
          >
            <option value="3">Top 3</option>
            <option value="5">Top 5</option>
            <option value="8">Top 8</option>
            <option value="10">Top 10</option>
            <option value="20">Top 20</option>
            <option value="50">Top 50</option>
            <option value="100">Top 100</option>
          </select>
          
          <label style={{ fontSize: '12px', fontWeight: '500', color: '#666', marginLeft: '16px' }}>
            Sort by:
          </label>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            style={styles.select}
          >
            <option value="volatility">Volatility</option>
            <option value="price">Price</option>
            <option value="volume">Volume</option>
          </select>
        </div>
      </div>

      <div style={styles.stats}>
        <div style={styles.statCard}>
          <div style={styles.statLabel}>Extreme Risk</div>
          <div style={styles.statValue}>{riskCounts.extreme}</div>
        </div>
        <div style={styles.statCard}>
          <div style={styles.statLabel}>High Risk</div>
          <div style={styles.statValue}>{riskCounts.high}</div>
        </div>
        <div style={styles.statCard}>
          <div style={styles.statLabel}>Medium Risk</div>
          <div style={styles.statValue}>{riskCounts.medium}</div>
        </div>
        <div style={styles.statCard}>
          <div style={styles.statLabel}>Average Volatility</div>
          <div style={styles.statValue}>{avgVolatility.toFixed(1)}%</div>
        </div>
      </div>

      <div style={styles.table}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#f8f9fa', borderBottom: '1px solid #e5e5e5' }}>
              <th style={styles.th}>Stock</th>
              <th style={styles.th}>Price / Change</th>
              <th style={styles.th}>Volatility</th>
              <th style={styles.th}>Volume</th>
              <th style={styles.th}>Risk</th>
            </tr>
          </thead>
          <tbody>
            {getPaginatedData().map((stock) => {
              const maxVolatility = Math.max(...volatilityData.map(s => s.volatility));
              const volatilityWidth = (stock.volatility / maxVolatility) * 100;
              const isPositive = stock.priceChangePercent >= 0;

              return (
                <tr key={stock.symbol}>
                  <td style={styles.td}>
                    <div style={styles.symbol}>{stock.symbol}</div>
                    <div style={styles.company}>{stock.name}</div>
                  </td>
                  <td style={styles.td}>
                    <div style={styles.price}>{formatPrice(stock.currentPrice)}</div>
                    <div style={{
                      ...styles.change,
                      ...(isPositive ? styles.positive : styles.negative)
                    }}>
                      {isPositive ? '+' : ''}{stock.priceChangePercent.toFixed(2)}% ({isPositive ? '+' : ''}{formatPrice(stock.priceChange)})
                    </div>
                  </td>
                  <td style={styles.td}>
                    <div style={{ fontWeight: '600', marginBottom: '2px' }}>
                      {stock.volatility.toFixed(1)}%
                    </div>
                    <div style={styles.volatilityBar}>
                      <div 
                        style={{
                          ...styles.volatilityFill,
                          width: `${volatilityWidth}%`
                        }}
                      />
                    </div>
                  </td>
                  <td style={styles.td}>
                    <div style={{ fontWeight: '500' }}>
                      {formatVolume(stock.averageVolume)}
                    </div>
                  </td>
                  <td style={styles.td}>
                    <span style={getRiskBadgeStyle(stock.riskLevel)}>
                      {stock.riskLevel}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginTop: '16px',
          padding: '0 8px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <label style={{ fontSize: '12px', fontWeight: '500', color: '#666' }}>
              Per page:
            </label>
            <select
              value={itemsPerPage}
              onChange={(e) => {
                setItemsPerPage(Number(e.target.value));
                setCurrentPage(1); // Reset to first page
              }}
              style={styles.select}
            >
              <option value="3">3</option>
              <option value="5">5</option>
              <option value="8">8</option>
            </select>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              style={{
                padding: '6px 12px',
                border: '1px solid #d1d1d1',
                borderRadius: '6px',
                backgroundColor: currentPage === 1 ? '#f5f5f5' : '#fff',
                color: currentPage === 1 ? '#999' : '#333',
                fontSize: '12px',
                cursor: currentPage === 1 ? 'not-allowed' : 'pointer'
              }}
            >
              Previous
            </button>
            
            <span style={{ fontSize: '12px', color: '#666', margin: '0 8px' }}>
              Page {currentPage} of {totalPages}
            </span>
            
            <button
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
              style={{
                padding: '6px 12px',
                border: '1px solid #d1d1d1',
                borderRadius: '6px',
                backgroundColor: currentPage === totalPages ? '#f5f5f5' : '#fff',
                color: currentPage === totalPages ? '#999' : '#333',
                fontSize: '12px',
                cursor: currentPage === totalPages ? 'not-allowed' : 'pointer'
              }}
            >
              Next
            </button>
          </div>
          
          <div style={{ fontSize: '12px', color: '#666' }}>
            Showing top {Math.min(topN, volatilityData.length)} stocks
          </div>
        </div>
      )}
    </div>
  );
};

export default StockVolatilityScreener;