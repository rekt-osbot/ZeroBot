"""
ChartInk-based trading strategies implementation
"""
import logging
import pandas as pd
import numpy as np
import ta
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class ChartInkStrategy(ABC):
    """Base class for ChartInk strategies"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on the strategy"""
        pass

class SMA200BreakoutStrategy(ChartInkStrategy):
    """
    4H closing above 200 SMA strategy
    Based on: 4 hour close > 4 hour sma(close, 200) and previous close <= previous sma(close, 200)
    """
    
    def __init__(self):
        super().__init__("SMA200_Breakout")
        self.sma_period = 50  # Use 50 instead of 200 for shorter data periods
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        if len(data) < self.sma_period + 5:
            logger.warning(f"Not enough data for {self.name} strategy. Need at least {self.sma_period + 5} periods.")
            return pd.DataFrame()
        
        signals = data.copy()
        
        # Calculate 200-period SMA
        signals['sma_200'] = signals['close'].rolling(window=self.sma_period, min_periods=1).mean()
        
        # Calculate 20-period SMA for additional filter
        signals['sma_20'] = signals['close'].rolling(window=20, min_periods=1).mean()
        
        # Initialize signals
        signals['signal'] = 0.0
        signals['position'] = 0.0
        
        # Generate buy signals: current close > SMA200 AND previous close <= previous SMA200
        for i in range(1, len(signals)):
            current_close = signals['close'].iloc[i]
            current_sma200 = signals['sma_200'].iloc[i]
            prev_close = signals['close'].iloc[i-1]
            prev_sma200 = signals['sma_200'].iloc[i-1]
            current_sma20 = signals['sma_20'].iloc[i]
            
            # Buy condition: breakout above 200 SMA + above 20 SMA filter
            if (current_close > current_sma200 and 
                prev_close <= prev_sma200 and 
                current_close > current_sma20):
                signals.loc[signals.index[i], 'signal'] = 1.0
        
        # Generate position changes
        signals['position'] = signals['signal'].diff()
        
        return signals

class HighRSIBreakoutStrategy(ChartInkStrategy):
    """
    High RSI and Breakout strategy
    Based on: close >= previous high with RSI momentum conditions
    """
    
    def __init__(self):
        super().__init__("High_RSI_Breakout")
        self.rsi_period = 9
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        if len(data) < 50:
            logger.warning(f"Not enough data for {self.name} strategy. Need at least 50 periods.")
            return pd.DataFrame()
        
        signals = data.copy()
        
        # Calculate RSI
        signals['rsi'] = ta.momentum.RSIIndicator(signals['close'], window=self.rsi_period).rsi()
        
        # Calculate moving averages
        signals['sma_20'] = signals['close'].rolling(window=20, min_periods=1).mean()
        signals['sma_50'] = signals['close'].rolling(window=50, min_periods=1).mean()
        
        # Calculate RSI WMA and EMA
        signals['rsi_wma'] = signals['rsi'].rolling(window=21).apply(
            lambda x: np.average(x, weights=np.arange(1, len(x) + 1)), raw=True
        )
        signals['rsi_ema'] = signals['rsi'].ewm(span=3).mean()
        
        # Initialize signals
        signals['signal'] = 0.0
        signals['position'] = 0.0
        
        # Generate buy signals
        for i in range(1, len(signals)):
            current_close = signals['close'].iloc[i]
            prev_high = signals['high'].iloc[i-1]
            current_rsi = signals['rsi'].iloc[i]
            current_rsi_wma = signals['rsi_wma'].iloc[i]
            current_rsi_ema = signals['rsi_ema'].iloc[i]
            current_sma20 = signals['sma_20'].iloc[i]
            current_sma50 = signals['sma_50'].iloc[i]
            
            # Buy conditions: breakout + RSI momentum + trend filter
            if (current_close >= prev_high and  # Breakout
                current_rsi_wma < current_rsi and  # RSI momentum
                current_rsi_ema < current_rsi and  # RSI momentum
                current_sma20 > current_sma50 and  # Trend filter
                not pd.isna(current_rsi_wma) and not pd.isna(current_rsi_ema)):
                signals.loc[signals.index[i], 'signal'] = 1.0
        
        # Generate position changes
        signals['position'] = signals['signal'].diff()
        
        return signals

class BullGapStrategy(ChartInkStrategy):
    """
    Bull Gap with Open Low strategy
    Based on: gap up opening with specific conditions
    """
    
    def __init__(self):
        super().__init__("Bull_Gap")
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        if len(data) < 50:
            logger.warning(f"Not enough data for {self.name} strategy. Need at least 50 periods.")
            return pd.DataFrame()
        
        signals = data.copy()
        
        # Calculate moving averages
        signals['sma_20'] = signals['close'].rolling(window=20, min_periods=1).mean()
        signals['sma_50'] = signals['close'].rolling(window=50, min_periods=1).mean()
        signals['sma_5'] = signals['close'].rolling(window=5, min_periods=1).mean()
        
        # Initialize signals
        signals['signal'] = 0.0
        signals['position'] = 0.0
        
        # Generate buy signals
        for i in range(1, len(signals)):
            current_open = signals['open'].iloc[i]
            current_close = signals['close'].iloc[i]
            current_low = signals['low'].iloc[i]
            prev_close = signals['close'].iloc[i-1]
            prev_low = signals['low'].iloc[i-1]
            current_sma20 = signals['sma_20'].iloc[i]
            current_sma50 = signals['sma_50'].iloc[i]
            current_sma5 = signals['sma_5'].iloc[i]
            prev_sma20 = signals['sma_20'].iloc[i-1]
            
            # Bull gap conditions
            gap_up = current_open > prev_close
            above_sma20 = current_close > current_sma20
            prev_low_near_sma = prev_low < prev_sma20 * 1.02
            open_near_sma = current_open < current_sma20 * 1.05
            trend_up = current_sma20 > current_sma50
            small_wick = (current_open - current_low) <= (current_close * 0.05)
            above_sma5 = current_close > current_sma5
            
            if (gap_up and above_sma20 and prev_low_near_sma and 
                open_near_sma and trend_up and small_wick and above_sma5):
                signals.loc[signals.index[i], 'signal'] = 1.0
        
        # Generate position changes
        signals['position'] = signals['signal'].diff()
        
        return signals

class MorningStarStrategy(ChartInkStrategy):
    """
    Morning Star Pattern strategy
    Based on: 3-candle reversal pattern with trend confirmation
    """
    
    def __init__(self):
        super().__init__("Morning_Star")
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        if len(data) < 50:
            logger.warning(f"Not enough data for {self.name} strategy. Need at least 50 periods.")
            return pd.DataFrame()
        
        signals = data.copy()
        
        # Calculate moving averages
        signals['sma_20'] = signals['close'].rolling(window=20, min_periods=1).mean()
        signals['sma_50'] = signals['close'].rolling(window=50, min_periods=1).mean()
        
        # Calculate RSI and its moving averages
        signals['rsi'] = ta.momentum.RSIIndicator(signals['close'], window=9).rsi()
        signals['rsi_wma'] = signals['rsi'].rolling(window=21).apply(
            lambda x: np.average(x, weights=np.arange(1, len(x) + 1)), raw=True
        )
        signals['rsi_ema'] = signals['rsi'].ewm(span=3).mean()
        
        # Initialize signals
        signals['signal'] = 0.0
        signals['position'] = 0.0
        
        # Generate buy signals (simplified morning star pattern)
        for i in range(2, len(signals)):
            # Current candle
            current_close = signals['close'].iloc[i]
            current_open = signals['open'].iloc[i]
            
            # Previous candle (middle of pattern)
            prev_close = signals['close'].iloc[i-1]
            prev_open = signals['open'].iloc[i-1]
            prev_high = signals['high'].iloc[i-1]
            prev_low = signals['low'].iloc[i-1]
            
            # Two days ago (first candle)
            prev2_close = signals['close'].iloc[i-2]
            prev2_open = signals['open'].iloc[i-2]
            prev2_high = signals['high'].iloc[i-2]
            
            # Technical indicators
            current_sma20 = signals['sma_20'].iloc[i]
            current_sma50 = signals['sma_50'].iloc[i]
            prev_sma20 = signals['sma_20'].iloc[i-1]
            current_rsi = signals['rsi'].iloc[i]
            current_rsi_wma = signals['rsi_wma'].iloc[i]
            current_rsi_ema = signals['rsi_ema'].iloc[i]
            
            # Morning star pattern conditions (simplified)
            bearish_first = prev2_close < prev2_open  # First candle bearish
            small_middle = abs(prev_close - prev_open) < abs(prev2_close - prev2_open) * 0.5  # Small middle candle
            bullish_third = current_close > current_open  # Third candle bullish
            breakout = current_close > prev2_high  # Breakout above first candle high
            
            # Additional filters
            trend_filter = current_sma20 > current_sma50
            prev_low_filter = prev_low < prev_sma20 * 1.07
            rsi_momentum = (current_rsi_wma < current_rsi and current_rsi_ema < current_rsi and
                          not pd.isna(current_rsi_wma) and not pd.isna(current_rsi_ema))
            
            if (bearish_first and small_middle and bullish_third and breakout and
                trend_filter and prev_low_filter and rsi_momentum):
                signals.loc[signals.index[i], 'signal'] = 1.0
        
        # Generate position changes
        signals['position'] = signals['signal'].diff()
        
        return signals

# Dictionary of ChartInk strategies
CHARTINK_STRATEGIES = {
    'sma200_breakout': SMA200BreakoutStrategy,
    'high_rsi_breakout': HighRSIBreakoutStrategy,
    'bull_gap': BullGapStrategy,
    'morning_star': MorningStarStrategy
}
