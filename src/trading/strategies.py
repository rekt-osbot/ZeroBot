"""
Trading strategies for the ZeroBot application
"""
import logging
import pandas as pd
import numpy as np
import ta
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class Strategy(ABC):
    """Abstract base class for trading strategies"""
    
    def __init__(self, name):
        """Initialize the strategy"""
        self.name = name
    
    @abstractmethod
    def generate_signals(self, data):
        """Generate trading signals from data"""
        pass
    
    def __str__(self):
        """String representation of the strategy"""
        return self.name


class MovingAverageCrossover(Strategy):
    """Moving Average Crossover strategy"""
    
    def __init__(self, short_window=20, long_window=50):
        """Initialize the strategy with window sizes"""
        super().__init__("Moving Average Crossover")
        self.short_window = short_window
        self.long_window = long_window
    
    def generate_signals(self, data):
        """Generate trading signals based on moving average crossover"""
        if len(data) < self.long_window:
            logger.warning(f"Not enough data for {self.name} strategy. Need at least {self.long_window} periods.")
            return pd.DataFrame()
        
        # Make a copy of the data
        signals = data.copy()
        
        # Create short and long moving averages
        signals['short_ma'] = signals['close'].rolling(window=self.short_window, min_periods=1).mean()
        signals['long_ma'] = signals['close'].rolling(window=self.long_window, min_periods=1).mean()
        
        # Create signals
        signals['signal'] = 0.0
        signals.loc[self.short_window:, 'signal'] = np.where(
            signals['short_ma'][self.short_window:] > signals['long_ma'][self.short_window:], 1.0, 0.0
        )
        
        # Generate trading orders
        signals['position'] = signals['signal'].diff()
        
        return signals


class RSIStrategy(Strategy):
    """Relative Strength Index (RSI) strategy"""
    
    def __init__(self, window=14, oversold=30, overbought=70):
        """Initialize the strategy with RSI parameters"""
        super().__init__("RSI Strategy")
        self.window = window
        self.oversold = oversold
        self.overbought = overbought
    
    def generate_signals(self, data):
        """Generate trading signals based on RSI indicator"""
        if len(data) < self.window:
            logger.warning(f"Not enough data for {self.name} strategy. Need at least {self.window} periods.")
            return pd.DataFrame()
        
        # Make a copy of the data
        signals = data.copy()
        
        # Calculate RSI
        rsi = ta.momentum.RSIIndicator(close=signals['close'], window=self.window)
        signals['rsi'] = rsi.rsi()
        
        # Create signals
        signals['signal'] = 0.0
        signals['signal'] = np.where(signals['rsi'] < self.oversold, 1.0, 0.0)
        signals['signal'] = np.where(signals['rsi'] > self.overbought, -1.0, signals['signal'])
        
        # Generate trading orders
        signals['position'] = signals['signal'].diff()
        
        return signals


class MACDStrategy(Strategy):
    """Moving Average Convergence Divergence (MACD) strategy"""
    
    def __init__(self, fast=12, slow=26, signal=9):
        """Initialize the strategy with MACD parameters"""
        super().__init__("MACD Strategy")
        self.fast = fast
        self.slow = slow
        self.signal = signal
    
    def generate_signals(self, data):
        """Generate trading signals based on MACD indicator"""
        if len(data) < self.slow + self.signal:
            logger.warning(f"Not enough data for {self.name} strategy. Need at least {self.slow + self.signal} periods.")
            return pd.DataFrame()
        
        # Make a copy of the data
        signals = data.copy()
        
        # Calculate MACD
        macd = ta.trend.MACD(
            close=signals['close'],
            window_fast=self.fast,
            window_slow=self.slow,
            window_sign=self.signal
        )
        signals['macd'] = macd.macd()
        signals['macd_signal'] = macd.macd_signal()
        signals['macd_diff'] = macd.macd_diff()
        
        # Create signals
        signals['signal'] = 0.0
        signals['signal'] = np.where(signals['macd'] > signals['macd_signal'], 1.0, 0.0)
        
        # Generate trading orders
        signals['position'] = signals['signal'].diff()
        
        return signals


class BollingerBandsStrategy(Strategy):
    """Bollinger Bands strategy"""
    
    def __init__(self, window=20, num_std=2):
        """Initialize the strategy with Bollinger Bands parameters"""
        super().__init__("Bollinger Bands Strategy")
        self.window = window
        self.num_std = num_std
    
    def generate_signals(self, data):
        """Generate trading signals based on Bollinger Bands indicator"""
        if len(data) < self.window:
            logger.warning(f"Not enough data for {self.name} strategy. Need at least {self.window} periods.")
            return pd.DataFrame()
        
        # Make a copy of the data
        signals = data.copy()
        
        # Calculate Bollinger Bands
        bollinger = ta.volatility.BollingerBands(
            close=signals['close'],
            window=self.window,
            window_dev=self.num_std
        )
        signals['bollinger_mavg'] = bollinger.bollinger_mavg()
        signals['bollinger_hband'] = bollinger.bollinger_hband()
        signals['bollinger_lband'] = bollinger.bollinger_lband()
        
        # Create signals
        signals['signal'] = 0.0
        signals['signal'] = np.where(signals['close'] < signals['bollinger_lband'], 1.0, 0.0)
        signals['signal'] = np.where(signals['close'] > signals['bollinger_hband'], -1.0, signals['signal'])
        
        # Generate trading orders
        signals['position'] = signals['signal'].diff()
        
        return signals


class SupertrendStrategy(Strategy):
    """Supertrend strategy"""
    
    def __init__(self, atr_period=10, multiplier=3):
        """Initialize the strategy with Supertrend parameters"""
        super().__init__("Supertrend Strategy")
        self.atr_period = atr_period
        self.multiplier = multiplier
    
    def generate_signals(self, data):
        """Generate trading signals based on Supertrend indicator"""
        if len(data) < self.atr_period:
            logger.warning(f"Not enough data for {self.name} strategy. Need at least {self.atr_period} periods.")
            return pd.DataFrame()
        
        # Make a copy of the data
        signals = data.copy()
        
        # Calculate ATR
        atr = ta.volatility.AverageTrueRange(
            high=signals['high'],
            low=signals['low'],
            close=signals['close'],
            window=self.atr_period
        ).average_true_range()
        
        # Calculate Supertrend
        hl2 = (signals['high'] + signals['low']) / 2
        
        # Upper band
        signals['upperband'] = hl2 + (self.multiplier * atr)
        signals['prevupperband'] = signals['upperband'].shift(1)
        
        # Lower band
        signals['lowerband'] = hl2 - (self.multiplier * atr)
        signals['prevlowerband'] = signals['lowerband'].shift(1)
        
        # Initialize Supertrend
        signals['supertrend'] = 0.0
        signals['prevclose'] = signals['close'].shift(1)
        
        # Calculate Supertrend
        for i in range(1, len(signals)):
            if signals['close'].iloc[i] <= signals['upperband'].iloc[i]:
                signals['supertrend'].iloc[i] = signals['upperband'].iloc[i]
            else:
                signals['supertrend'].iloc[i] = signals['lowerband'].iloc[i]
        
        # Create signals
        signals['signal'] = 0.0
        signals['signal'] = np.where(signals['close'] > signals['supertrend'], 1.0, 0.0)
        
        # Generate trading orders
        signals['position'] = signals['signal'].diff()
        
        return signals


# Import ChartInk strategies
from .chartink_strategies import CHARTINK_STRATEGIES

# Dictionary of available strategies
STRATEGIES = {
    'ma_crossover': MovingAverageCrossover,
    'rsi': RSIStrategy,
    'macd': MACDStrategy,
    'bollinger': BollingerBandsStrategy,
    'supertrend': SupertrendStrategy,
    **CHARTINK_STRATEGIES  # Add ChartInk strategies
}
