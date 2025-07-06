"""
Debug script to check data columns
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data.providers import YFinanceProvider
from datetime import datetime, timedelta

def debug_data():
    provider = YFinanceProvider()
    
    # Test getting historical data for RELIANCE
    symbol = "RELIANCE"
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    
    print(f"Getting historical data for {symbol} from {start_date} to {end_date}")
    data = provider.get_historical_data(symbol, start_date, end_date)
    
    if not data.empty:
        print(f"Retrieved {len(data)} data points")
        print(f"Columns: {list(data.columns)}")
        print(f"Data types: {data.dtypes}")
        print("\nFirst few rows:")
        print(data.head())
        print("\nLast few rows:")
        print(data.tail())
    else:
        print("No data retrieved")

if __name__ == "__main__":
    debug_data()
