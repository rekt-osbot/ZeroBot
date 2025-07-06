"""
Backtesting engine for trading strategies
"""
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from src.data.providers import get_data_provider
from src.trading.strategies import STRATEGIES

logger = logging.getLogger(__name__)

@dataclass
class BacktestTrade:
    """Represents a trade in backtesting"""
    entry_date: datetime
    exit_date: Optional[datetime]
    symbol: str
    entry_price: float
    exit_price: Optional[float]
    quantity: int
    trade_type: str  # 'BUY' or 'SELL'
    pnl: Optional[float]
    pnl_percent: Optional[float]
    reason: str  # 'target', 'stop_loss', 'signal', 'end_of_period'
    
    def is_closed(self) -> bool:
        return self.exit_date is not None

@dataclass
class BacktestResults:
    """Results of a backtest"""
    start_date: str
    end_date: str
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_percent: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_profit: float
    avg_loss: float
    max_drawdown: float
    sharpe_ratio: float
    trades: List[BacktestTrade]
    equity_curve: pd.DataFrame
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'initial_capital': self.initial_capital,
            'final_capital': self.final_capital,
            'total_return': self.total_return,
            'total_return_percent': self.total_return_percent,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': self.win_rate,
            'avg_profit': self.avg_profit,
            'avg_loss': self.avg_loss,
            'max_drawdown': self.max_drawdown,
            'sharpe_ratio': self.sharpe_ratio,
            'trades': [
                {
                    'entry_date': trade.entry_date.isoformat(),
                    'exit_date': trade.exit_date.isoformat() if trade.exit_date else None,
                    'symbol': trade.symbol,
                    'entry_price': trade.entry_price,
                    'exit_price': trade.exit_price,
                    'quantity': trade.quantity,
                    'trade_type': trade.trade_type,
                    'pnl': trade.pnl,
                    'pnl_percent': trade.pnl_percent,
                    'reason': trade.reason
                }
                for trade in self.trades
            ],
            'equity_curve': self.equity_curve.to_dict('records') if not self.equity_curve.empty else []
        }

class BacktestEngine:
    """Backtesting engine for trading strategies"""
    
    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.data_provider = get_data_provider(simulation_mode=False)
        
    def run_backtest(self, 
                    strategy_name: str,
                    symbol: str,
                    start_date: str,
                    end_date: str,
                    stop_loss_percent: float = 0.05,
                    target_percent: float = 0.10,
                    position_size_percent: float = 0.10) -> BacktestResults:
        """Run a backtest for a given strategy and symbol"""
        
        logger.info(f"Starting backtest: {strategy_name} on {symbol} from {start_date} to {end_date}")
        
        # Get historical data
        historical_data = self.data_provider.get_historical_data(symbol, start_date, end_date)
        
        if historical_data.empty:
            logger.error(f"No historical data found for {symbol}")
            return self._empty_results(start_date, end_date)
        
        # Initialize strategy
        if strategy_name not in STRATEGIES:
            logger.error(f"Strategy {strategy_name} not found")
            return self._empty_results(start_date, end_date)
        
        strategy = STRATEGIES[strategy_name]()
        
        # Generate signals
        try:
            signals = strategy.generate_signals(historical_data)
        except Exception as e:
            logger.error(f"Error generating signals for {strategy_name} on {symbol}: {e}")
            logger.error(f"Available columns: {list(historical_data.columns)}")
            return self._empty_results(start_date, end_date)

        if signals.empty:
            logger.warning(f"No signals generated for {strategy_name} on {symbol}")
            return self._empty_results(start_date, end_date)
        
        # Run simulation
        return self._simulate_trades(
            historical_data, signals, symbol, start_date, end_date,
            stop_loss_percent, target_percent, position_size_percent
        )
    
    def _simulate_trades(self, 
                        data: pd.DataFrame, 
                        signals: pd.DataFrame,
                        symbol: str,
                        start_date: str,
                        end_date: str,
                        stop_loss_percent: float,
                        target_percent: float,
                        position_size_percent: float) -> BacktestResults:
        """Simulate trades based on signals"""
        
        capital = self.initial_capital
        trades = []
        open_trades = []
        equity_curve = []
        
        # Use signals directly since it already contains all the data
        combined = signals.copy()
        combined = combined.fillna(0)  # Fill NaN signals with 0
        
        for idx, row in combined.iterrows():
            current_date = row['date']
            current_price = row['close']
            
            # Check for exit conditions on open trades
            for trade in open_trades[:]:  # Use slice to avoid modification during iteration
                # Check stop loss
                if current_price <= trade.entry_price * (1 - stop_loss_percent):
                    trade.exit_date = current_date
                    trade.exit_price = current_price
                    trade.pnl = (trade.exit_price - trade.entry_price) * trade.quantity
                    trade.pnl_percent = (trade.pnl / (trade.entry_price * trade.quantity)) * 100
                    trade.reason = 'stop_loss'
                    capital += trade.exit_price * trade.quantity
                    trades.append(trade)
                    open_trades.remove(trade)
                    continue
                
                # Check target
                if current_price >= trade.entry_price * (1 + target_percent):
                    trade.exit_date = current_date
                    trade.exit_price = current_price
                    trade.pnl = (trade.exit_price - trade.entry_price) * trade.quantity
                    trade.pnl_percent = (trade.pnl / (trade.entry_price * trade.quantity)) * 100
                    trade.reason = 'target'
                    capital += trade.exit_price * trade.quantity
                    trades.append(trade)
                    open_trades.remove(trade)
                    continue
            
            # Check for new buy signals (position change from 0 to 1)
            if hasattr(row, 'position') and row.position == 1 and len(open_trades) == 0:
                # Calculate position size
                position_value = capital * position_size_percent
                quantity = int(position_value / current_price)
                
                if quantity > 0:
                    trade = BacktestTrade(
                        entry_date=current_date,
                        exit_date=None,
                        symbol=symbol,
                        entry_price=current_price,
                        exit_price=None,
                        quantity=quantity,
                        trade_type='BUY',
                        pnl=None,
                        pnl_percent=None,
                        reason=''
                    )
                    
                    capital -= current_price * quantity
                    open_trades.append(trade)
            
            # Check for sell signals to close positions (position change from 1 to 0)
            if hasattr(row, 'position') and row.position == -1:
                for trade in open_trades[:]:
                    trade.exit_date = current_date
                    trade.exit_price = current_price
                    trade.pnl = (trade.exit_price - trade.entry_price) * trade.quantity
                    trade.pnl_percent = (trade.pnl / (trade.entry_price * trade.quantity)) * 100
                    trade.reason = 'signal'
                    capital += trade.exit_price * trade.quantity
                    trades.append(trade)
                    open_trades.remove(trade)
            
            # Calculate current portfolio value
            portfolio_value = capital
            for trade in open_trades:
                portfolio_value += current_price * trade.quantity
            
            equity_curve.append({
                'date': current_date,
                'portfolio_value': portfolio_value,
                'capital': capital,
                'positions_value': portfolio_value - capital
            })
        
        # Close any remaining open trades at the end
        if open_trades:
            final_price = combined.iloc[-1]['close']
            final_date = combined.iloc[-1]['date']
            
            for trade in open_trades:
                trade.exit_date = final_date
                trade.exit_price = final_price
                trade.pnl = (trade.exit_price - trade.entry_price) * trade.quantity
                trade.pnl_percent = (trade.pnl / (trade.entry_price * trade.quantity)) * 100
                trade.reason = 'end_of_period'
                capital += trade.exit_price * trade.quantity
                trades.append(trade)
        
        # Calculate metrics
        return self._calculate_metrics(trades, equity_curve, start_date, end_date)
    
    def _calculate_metrics(self, trades: List[BacktestTrade], equity_curve: List[Dict], 
                          start_date: str, end_date: str) -> BacktestResults:
        """Calculate backtest metrics"""
        
        if not trades:
            return self._empty_results(start_date, end_date)
        
        # Basic metrics
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t.pnl > 0])
        losing_trades = len([t for t in trades if t.pnl < 0])
        
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        profits = [t.pnl for t in trades if t.pnl > 0]
        losses = [t.pnl for t in trades if t.pnl < 0]
        
        avg_profit = np.mean(profits) if profits else 0
        avg_loss = np.mean(losses) if losses else 0
        
        total_pnl = sum(t.pnl for t in trades)
        final_capital = self.initial_capital + total_pnl
        total_return_percent = (total_pnl / self.initial_capital) * 100
        
        # Calculate max drawdown
        equity_df = pd.DataFrame(equity_curve)
        if not equity_df.empty:
            equity_df['peak'] = equity_df['portfolio_value'].cummax()
            equity_df['drawdown'] = (equity_df['portfolio_value'] - equity_df['peak']) / equity_df['peak']
            max_drawdown = equity_df['drawdown'].min() * 100
        else:
            max_drawdown = 0
        
        # Calculate Sharpe ratio (simplified)
        if not equity_df.empty and len(equity_df) > 1:
            returns = equity_df['portfolio_value'].pct_change().dropna()
            if returns.std() > 0:
                sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252)  # Annualized
            else:
                sharpe_ratio = 0
        else:
            sharpe_ratio = 0
        
        return BacktestResults(
            start_date=start_date,
            end_date=end_date,
            initial_capital=self.initial_capital,
            final_capital=final_capital,
            total_return=total_pnl,
            total_return_percent=total_return_percent,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            avg_profit=avg_profit,
            avg_loss=avg_loss,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            trades=trades,
            equity_curve=equity_df if not equity_df.empty else pd.DataFrame()
        )
    
    def _empty_results(self, start_date: str, end_date: str) -> BacktestResults:
        """Return empty results for failed backtests"""
        return BacktestResults(
            start_date=start_date,
            end_date=end_date,
            initial_capital=self.initial_capital,
            final_capital=self.initial_capital,
            total_return=0,
            total_return_percent=0,
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            win_rate=0,
            avg_profit=0,
            avg_loss=0,
            max_drawdown=0,
            sharpe_ratio=0,
            trades=[],
            equity_curve=pd.DataFrame()
        )

# Global backtest engine instance
_backtest_engine = None

def get_backtest_engine() -> BacktestEngine:
    """Get the global backtest engine"""
    global _backtest_engine
    if _backtest_engine is None:
        _backtest_engine = BacktestEngine()
    return _backtest_engine
