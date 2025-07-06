"""
Comprehensive test suite for ZeroBot implementation
"""
import sys
import os
import pytest
import pandas as pd
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data.providers import YFinanceProvider, SimulationDataProvider
from src.simulation.engine import SimulationEngine
from src.backtesting.engine import BacktestEngine
from src.trading.strategies import STRATEGIES

class TestDataProviders:
    """Test data provider functionality"""
    
    def test_yfinance_provider_instruments(self):
        """Test getting instruments from YFinance provider"""
        provider = YFinanceProvider()
        instruments = provider.get_instruments("NSE")
        
        assert not instruments.empty, "Should return instruments"
        assert len(instruments) > 0, "Should have at least one instrument"
        assert 'tradingsymbol' in instruments.columns, "Should have tradingsymbol column"
        assert 'exchange' in instruments.columns, "Should have exchange column"
    
    def test_yfinance_provider_historical_data(self):
        """Test getting historical data"""
        provider = YFinanceProvider()
        
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        data = provider.get_historical_data("RELIANCE", start_date, end_date)
        
        if not data.empty:  # Only test if data is available
            assert 'date' in data.columns, "Should have date column"
            assert 'close' in data.columns, "Should have close column"
            assert 'open' in data.columns, "Should have open column"
            assert 'high' in data.columns, "Should have high column"
            assert 'low' in data.columns, "Should have low column"
            assert 'volume' in data.columns, "Should have volume column"
    
    def test_yfinance_provider_current_price(self):
        """Test getting current price"""
        provider = YFinanceProvider()
        price = provider.get_current_price("RELIANCE")
        
        assert isinstance(price, float), "Price should be a float"
        assert price >= 0, "Price should be non-negative"

class TestSimulationEngine:
    """Test simulation engine functionality"""
    
    def test_simulation_engine_initialization(self):
        """Test simulation engine initialization"""
        engine = SimulationEngine(initial_capital=100000)
        
        assert engine.initial_capital == 100000, "Should set initial capital"
        assert engine.current_capital == 100000, "Should start with full capital"
        assert len(engine.positions) == 0, "Should start with no positions"
        assert len(engine.trades) == 0, "Should start with no trades"
    
    def test_simulation_engine_place_order(self):
        """Test placing orders"""
        engine = SimulationEngine(initial_capital=100000)
        
        # Test buy order
        order_id = engine.place_order(
            symbol="RELIANCE",
            exchange="NSE",
            transaction_type="BUY",
            quantity=10,
            price=2500.0
        )
        
        assert order_id is not None, "Should return order ID"
        assert len(engine.positions) == 1, "Should create a position"
        assert engine.current_capital < 100000, "Should reduce capital"
    
    def test_simulation_engine_insufficient_capital(self):
        """Test handling insufficient capital"""
        engine = SimulationEngine(initial_capital=1000)
        
        # Try to buy expensive stock
        order_id = engine.place_order(
            symbol="RELIANCE",
            exchange="NSE",
            transaction_type="BUY",
            quantity=100,
            price=2500.0  # Total: 250,000 > 1,000 capital
        )
        
        assert order_id is None, "Should reject order with insufficient capital"
        assert len(engine.positions) == 0, "Should not create position"
        assert engine.current_capital == 1000, "Should not change capital"
    
    def test_simulation_engine_performance_metrics(self):
        """Test performance metrics calculation"""
        engine = SimulationEngine(initial_capital=100000)
        
        # Place a trade
        engine.place_order(
            symbol="RELIANCE",
            exchange="NSE",
            transaction_type="BUY",
            quantity=10,
            price=2500.0
        )
        
        metrics = engine.get_performance_metrics()
        
        assert 'initial_capital' in metrics, "Should have initial capital"
        assert 'current_capital' in metrics, "Should have current capital"
        assert 'portfolio_value' in metrics, "Should have portfolio value"
        assert metrics['initial_capital'] == 100000, "Should track initial capital"

class TestBacktestingEngine:
    """Test backtesting engine functionality"""
    
    def test_backtesting_engine_initialization(self):
        """Test backtesting engine initialization"""
        engine = BacktestEngine(initial_capital=100000)
        
        assert engine.initial_capital == 100000, "Should set initial capital"
    
    def test_backtesting_engine_empty_results(self):
        """Test handling of empty results"""
        engine = BacktestEngine(initial_capital=100000)
        
        # Test with invalid strategy
        results = engine.run_backtest(
            strategy_name="invalid_strategy",
            symbol="RELIANCE",
            start_date="2024-01-01",
            end_date="2024-01-31"
        )
        
        assert results.total_trades == 0, "Should have no trades for invalid strategy"
        assert results.final_capital == 100000, "Should maintain initial capital"
    
    def test_backtesting_engine_valid_strategy(self):
        """Test backtesting with valid strategy"""
        engine = BacktestEngine(initial_capital=100000)
        
        # Test with valid strategy and longer period
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        
        results = engine.run_backtest(
            strategy_name="ma_crossover",
            symbol="RELIANCE",
            start_date=start_date,
            end_date=end_date
        )
        
        assert isinstance(results.total_trades, int), "Should return integer trade count"
        assert isinstance(results.win_rate, float), "Should return float win rate"
        assert isinstance(results.total_return, float), "Should return float total return"
        assert results.initial_capital == 100000, "Should track initial capital"

class TestTradingStrategies:
    """Test trading strategies"""
    
    def test_ma_crossover_strategy(self):
        """Test Moving Average Crossover strategy"""
        strategy = STRATEGIES['ma_crossover']()
        
        # Create sample data
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        data = pd.DataFrame({
            'date': dates,
            'open': 1000 + (dates - dates[0]).days * 0.1,
            'high': 1010 + (dates - dates[0]).days * 0.1,
            'low': 990 + (dates - dates[0]).days * 0.1,
            'close': 1000 + (dates - dates[0]).days * 0.1,
            'volume': 100000
        })
        
        signals = strategy.generate_signals(data)
        
        assert not signals.empty, "Should generate signals"
        assert 'signal' in signals.columns, "Should have signal column"
        assert 'position' in signals.columns, "Should have position column"
        assert 'short_ma' in signals.columns, "Should have short MA column"
        assert 'long_ma' in signals.columns, "Should have long MA column"

class TestIntegration:
    """Integration tests"""
    
    def test_end_to_end_simulation(self):
        """Test complete simulation workflow"""
        # Initialize components
        engine = SimulationEngine(initial_capital=100000)
        
        # Place some trades
        order1 = engine.place_order("RELIANCE", "NSE", "BUY", 10, 2500.0)
        order2 = engine.place_order("TCS", "NSE", "BUY", 5, 3000.0)
        
        assert order1 is not None, "Should place first order"
        assert order2 is not None, "Should place second order"
        
        # Check positions
        positions = engine.get_positions()
        assert len(positions['day']) == 2, "Should have 2 positions"
        
        # Check metrics
        metrics = engine.get_performance_metrics()
        assert metrics['portfolio_value'] > 0, "Should have positive portfolio value"
    
    def test_data_provider_integration(self):
        """Test data provider integration with simulation"""
        provider = YFinanceProvider()
        engine = SimulationEngine(initial_capital=100000)
        
        # Get real price
        price = provider.get_current_price("RELIANCE")
        
        if price > 0:  # Only test if we got a valid price
            # Place order with real price
            order_id = engine.place_order("RELIANCE", "NSE", "BUY", 1, price)
            
            assert order_id is not None, "Should place order with real price"
            
            # Update positions (this would use real current prices)
            engine.update_positions()
            
            positions = engine.get_positions()
            assert not positions['day'].empty, "Should have positions"

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
