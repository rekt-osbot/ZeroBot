"""
Debug script to check strategy
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data.providers import YFinanceProvider
from src.trading.strategies import STRATEGIES
from datetime import datetime, timedelta

def debug_strategy():
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
        
        # Test strategy
        strategy = STRATEGIES['ma_crossover']()
        print(f"\nTesting {strategy.name} strategy...")
        
        try:
            signals = strategy.generate_signals(data)
            print(f"Generated signals with columns: {list(signals.columns)}")
            print(f"Signal data shape: {signals.shape}")
            
            # Check for buy/sell signals
            buy_signals = signals[signals['position'] == 1]
            sell_signals = signals[signals['position'] == -1]
            
            print(f"Buy signals: {len(buy_signals)}")
            print(f"Sell signals: {len(sell_signals)}")
            
            if len(buy_signals) > 0:
                print("\nFirst few buy signals:")
                print(buy_signals[['date', 'close', 'short_ma', 'long_ma', 'position']].head())
                
        except Exception as e:
            print(f"Strategy failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("No data retrieved")

if __name__ == "__main__":
    debug_strategy()
