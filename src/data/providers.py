"""
Data providers for historical and real-time market data
"""
import logging
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time
import os
import pickle

logger = logging.getLogger(__name__)

class DataProvider:
    """Base class for data providers"""
    
    def get_historical_data(self, symbol: str, start_date: str, end_date: str, interval: str = "1d") -> pd.DataFrame:
        """Get historical data for a symbol"""
        raise NotImplementedError
    
    def get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        raise NotImplementedError
    
    def get_instruments(self, exchange: str = None) -> pd.DataFrame:
        """Get list of available instruments"""
        raise NotImplementedError

class YFinanceProvider(DataProvider):
    """Yahoo Finance data provider for Indian stocks"""
    
    def __init__(self):
        self.cache_dir = "data_cache"
        self.cache_duration = 3600  # 1 hour cache
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Common Indian stock symbols with .NS (NSE) and .BO (BSE) suffixes
        self.nse_symbols = [
            "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
            "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "HINDUNILVR.NS", "KOTAKBANK.NS",
            "LT.NS", "ASIANPAINT.NS", "MARUTI.NS", "BAJFINANCE.NS", "HCLTECH.NS",
            "WIPRO.NS", "ULTRACEMCO.NS", "TITAN.NS", "NESTLEIND.NS", "POWERGRID.NS",
            "NTPC.NS", "ONGC.NS", "TATAMOTORS.NS", "TECHM.NS", "SUNPHARMA.NS",
            "JSWSTEEL.NS", "TATASTEEL.NS", "INDUSINDBK.NS", "BAJAJFINSV.NS", "DRREDDY.NS"
        ]
        
        self.bse_symbols = [
            "RELIANCE.BO", "TCS.BO", "INFY.BO", "HDFCBANK.BO", "ICICIBANK.BO",
            "SBIN.BO", "BHARTIARTL.BO", "ITC.BO", "HINDUNILVR.BO", "KOTAKBANK.BO"
        ]
    
    def _get_cache_path(self, symbol: str, start_date: str, end_date: str, interval: str) -> str:
        """Get cache file path for data"""
        cache_key = f"{symbol}_{start_date}_{end_date}_{interval}"
        return os.path.join(self.cache_dir, f"{cache_key}.pkl")
    
    def _is_cache_valid(self, cache_path: str) -> bool:
        """Check if cache file is valid (not expired)"""
        if not os.path.exists(cache_path):
            return False
        
        cache_time = os.path.getmtime(cache_path)
        current_time = time.time()
        return (current_time - cache_time) < self.cache_duration
    
    def get_historical_data(self, symbol: str, start_date: str, end_date: str, interval: str = "1d") -> pd.DataFrame:
        """Get historical data from Yahoo Finance with caching"""
        try:
            # Convert symbol format if needed
            if not symbol.endswith(('.NS', '.BO')):
                symbol = f"{symbol}.NS"  # Default to NSE
            
            cache_path = self._get_cache_path(symbol, start_date, end_date, interval)
            
            # Check cache first
            if self._is_cache_valid(cache_path):
                try:
                    with open(cache_path, 'rb') as f:
                        data = pickle.load(f)
                    logger.info(f"Loaded cached data for {symbol}")
                    return data
                except Exception as e:
                    logger.warning(f"Failed to load cache for {symbol}: {e}")
            
            # Fetch from Yahoo Finance
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date, interval=interval)
            
            if data.empty:
                logger.warning(f"No data found for {symbol}")
                return pd.DataFrame()
            
            # Reset index to get date as a column
            data.reset_index(inplace=True)

            # Standardize column names
            column_mapping = {
                'Date': 'date',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            }

            # Rename columns
            data.rename(columns=column_mapping, inplace=True)

            # Convert to lowercase if not already
            data.columns = [col.lower() for col in data.columns]

            # Ensure we have the required columns
            required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
            if not all(col in data.columns for col in required_columns):
                logger.error(f"Missing required columns for {symbol}. Available: {list(data.columns)}")
                return pd.DataFrame()
            
            # Cache the data
            try:
                with open(cache_path, 'wb') as f:
                    pickle.dump(data, f)
                logger.info(f"Cached data for {symbol}")
            except Exception as e:
                logger.warning(f"Failed to cache data for {symbol}: {e}")
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to get historical data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_current_price(self, symbol: str) -> float:
        """Get current price from Yahoo Finance"""
        try:
            if not symbol.endswith(('.NS', '.BO')):
                symbol = f"{symbol}.NS"
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Try different price fields
            price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
            
            if price is None:
                # Fallback to recent historical data
                data = ticker.history(period="1d")
                if not data.empty:
                    price = data['Close'].iloc[-1]
            
            return float(price) if price else 0.0
            
        except Exception as e:
            logger.error(f"Failed to get current price for {symbol}: {e}")
            return 0.0
    
    def get_instruments(self, exchange: str = None) -> pd.DataFrame:
        """Get list of available instruments"""
        instruments = []
        
        symbols = []
        if exchange is None or exchange.upper() == "NSE":
            symbols.extend(self.nse_symbols)
        if exchange is None or exchange.upper() == "BSE":
            symbols.extend(self.bse_symbols)
        
        for i, symbol in enumerate(symbols):
            # Extract base symbol and exchange
            base_symbol = symbol.split('.')[0]
            exchange_suffix = symbol.split('.')[1]
            exchange_name = "NSE" if exchange_suffix == "NS" else "BSE"
            
            instruments.append({
                "instrument_token": 100000 + i,
                "exchange_token": 10000 + i,
                "tradingsymbol": base_symbol,
                "name": f"{base_symbol}",
                "last_price": self.get_current_price(symbol),
                "expiry": "",
                "strike": 0,
                "tick_size": 0.05,
                "lot_size": 1,
                "instrument_type": "EQ",
                "segment": exchange_name,
                "exchange": exchange_name,
                "yf_symbol": symbol  # Store the Yahoo Finance symbol for later use
            })
        
        return pd.DataFrame(instruments)

class SimulationDataProvider(DataProvider):
    """Data provider for simulation mode with real historical data"""
    
    def __init__(self):
        self.yf_provider = YFinanceProvider()
        self.current_date = datetime.now()
        self.simulation_speed = 1  # 1 = real time, higher = faster
        
    def set_simulation_date(self, date: datetime):
        """Set the current simulation date"""
        self.current_date = date
    
    def advance_simulation(self, days: int = 1):
        """Advance simulation by specified days"""
        self.current_date += timedelta(days=days)
    
    def get_historical_data(self, symbol: str, start_date: str, end_date: str, interval: str = "1d") -> pd.DataFrame:
        """Get historical data up to simulation date"""
        # Ensure we don't get future data in simulation
        sim_date_str = self.current_date.strftime("%Y-%m-%d")
        if end_date > sim_date_str:
            end_date = sim_date_str
        
        return self.yf_provider.get_historical_data(symbol, start_date, end_date, interval)
    
    def get_current_price(self, symbol: str) -> float:
        """Get price at current simulation date"""
        # Get historical data up to simulation date
        end_date = self.current_date.strftime("%Y-%m-%d")
        start_date = (self.current_date - timedelta(days=5)).strftime("%Y-%m-%d")
        
        data = self.get_historical_data(symbol, start_date, end_date)
        if not data.empty:
            return float(data['close'].iloc[-1])
        
        return 0.0
    
    def get_instruments(self, exchange: str = None) -> pd.DataFrame:
        """Get instruments with prices at simulation date"""
        instruments = self.yf_provider.get_instruments(exchange)
        
        # Update prices to simulation date
        for idx, row in instruments.iterrows():
            symbol = row['yf_symbol']
            price = self.get_current_price(symbol)
            instruments.at[idx, 'last_price'] = price
        
        return instruments

# Global data provider instance
_data_provider = None

def get_data_provider(simulation_mode: bool = True) -> DataProvider:
    """Get the appropriate data provider"""
    global _data_provider
    
    if _data_provider is None:
        if simulation_mode:
            _data_provider = SimulationDataProvider()
        else:
            _data_provider = YFinanceProvider()
    
    return _data_provider

def set_data_provider(provider: DataProvider):
    """Set the global data provider"""
    global _data_provider
    _data_provider = provider
