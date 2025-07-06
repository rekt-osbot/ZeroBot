"""
Backtesting module for trading strategies
"""
from .engine import BacktestEngine, BacktestResults, BacktestTrade, get_backtest_engine

__all__ = ['BacktestEngine', 'BacktestResults', 'BacktestTrade', 'get_backtest_engine']
