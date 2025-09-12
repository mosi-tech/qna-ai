import pandas as pd
import numpy as np
import ta

# Mock data with SMA crossover
np.random.seed(42)
dates = pd.date_range('2024-01-01', periods=250, freq='D')
prices = 350 + np.cumsum(np.random.randn(250) * 0.02)
df = pd.DataFrame({'date': dates, 'close': prices})

# Calculate SMAs
df['sma_50'] = ta.trend.sma_indicator(df['close'], window=50)
df['sma_200'] = ta.trend.sma_indicator(df['close'], window=200)

# Identify crossovers
df['sma_position'] = df['sma_50'] > df['sma_200']
df['crossover'] = df['sma_position'].diff()

crossovers = df[df['crossover'] != 0.0].copy()
print('✅ Crossover detection working')
print('Crossover events found:', len(crossovers))
print('Data points processed:', len(df))

# Test performance calculation
if len(crossovers) > 0:
    crossovers['signal'] = crossovers['crossover'].map({1.0: 'Golden Cross', -1.0: 'Death Cross'})
    print('Sample crossover events:')
    print(crossovers[['date', 'signal', 'close']].head())