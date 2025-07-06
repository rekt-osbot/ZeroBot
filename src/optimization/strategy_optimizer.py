"""
Strategy optimization engine to find the best performing strategy
"""
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from src.data.providers import get_data_provider
from src.backtesting.engine import BacktestEngine, BacktestResults
from src.trading.strategies import STRATEGIES

logger = logging.getLogger(__name__)

@dataclass
class StrategyPerformance:
    """Performance metrics for a strategy"""
    strategy_name: str
    total_return: float
    total_return_percent: float
    total_trades: int
    win_rate: float
    avg_profit: float
    avg_loss: float
    max_drawdown: float
    sharpe_ratio: float
    final_capital: float
    
    def __str__(self):
        return f"{self.strategy_name}: {self.total_return_percent:.2f}% return, {self.win_rate:.1f}% win rate, {self.total_trades} trades"

class StrategyOptimizer:
    """Optimize strategies to find the best performer"""
    
    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.data_provider = get_data_provider(simulation_mode=False)
        self.backtest_engine = BacktestEngine(initial_capital)
        
    def optimize_strategies(self, 
                          symbol: str,
                          start_date: str,
                          end_date: str,
                          strategies: Optional[List[str]] = None,
                          stop_loss_percent: float = 0.05,
                          target_percent: float = 0.10,
                          position_size_percent: float = 0.10) -> List[StrategyPerformance]:
        """
        Test all strategies and return performance ranking
        
        Args:
            symbol: Stock symbol to test
            start_date: Start date for backtesting (YYYY-MM-DD)
            end_date: End date for backtesting (YYYY-MM-DD)
            strategies: List of strategy names to test (None = all strategies)
            stop_loss_percent: Stop loss percentage (0.05 = 5%)
            target_percent: Target profit percentage (0.10 = 10%)
            position_size_percent: Position size as percentage of capital (0.10 = 10%)
            
        Returns:
            List of StrategyPerformance objects sorted by total return
        """
        
        logger.info(f"Optimizing strategies for {symbol} from {start_date} to {end_date}")
        
        # Get historical data once
        historical_data = self.data_provider.get_historical_data(symbol, start_date, end_date)
        
        if historical_data.empty:
            logger.error(f"No historical data found for {symbol}")
            return []
        
        logger.info(f"Retrieved {len(historical_data)} data points for {symbol}")
        
        # Use all strategies if none specified
        if strategies is None:
            strategies = list(STRATEGIES.keys())
        
        results = []
        
        for strategy_name in strategies:
            logger.info(f"Testing strategy: {strategy_name}")
            
            try:
                # Run backtest for this strategy
                backtest_result = self.backtest_engine.run_backtest(
                    strategy_name=strategy_name,
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date,
                    stop_loss_percent=stop_loss_percent,
                    target_percent=target_percent,
                    position_size_percent=position_size_percent
                )
                
                # Convert to StrategyPerformance
                performance = StrategyPerformance(
                    strategy_name=strategy_name,
                    total_return=backtest_result.total_return,
                    total_return_percent=backtest_result.total_return_percent,
                    total_trades=backtest_result.total_trades,
                    win_rate=backtest_result.win_rate,
                    avg_profit=backtest_result.avg_profit,
                    avg_loss=backtest_result.avg_loss,
                    max_drawdown=backtest_result.max_drawdown,
                    sharpe_ratio=backtest_result.sharpe_ratio,
                    final_capital=backtest_result.final_capital
                )
                
                results.append(performance)
                logger.info(f"✓ {strategy_name}: {performance.total_return_percent:.2f}% return")
                
            except Exception as e:
                logger.error(f"✗ {strategy_name} failed: {e}")
                continue
        
        # Sort by total return percentage (descending)
        results.sort(key=lambda x: x.total_return_percent, reverse=True)
        
        return results
    
    def find_best_strategy(self, 
                          symbol: str,
                          start_date: str,
                          end_date: str,
                          min_trades: int = 1) -> Optional[StrategyPerformance]:
        """
        Find the single best performing strategy
        
        Args:
            symbol: Stock symbol to test
            start_date: Start date for backtesting
            end_date: End date for backtesting
            min_trades: Minimum number of trades required
            
        Returns:
            Best performing StrategyPerformance or None
        """
        
        results = self.optimize_strategies(symbol, start_date, end_date)
        
        # Filter by minimum trades
        valid_results = [r for r in results if r.total_trades >= min_trades]
        
        if not valid_results:
            logger.warning(f"No strategies with at least {min_trades} trades found")
            return None
        
        return valid_results[0]
    
    def generate_optimization_report(self, 
                                   symbol: str,
                                   start_date: str,
                                   end_date: str) -> str:
        """
        Generate a comprehensive optimization report
        
        Returns:
            Formatted report string
        """
        
        results = self.optimize_strategies(symbol, start_date, end_date)
        
        if not results:
            return f"No valid results found for {symbol}"
        
        report = []
        report.append("=" * 80)
        report.append(f"STRATEGY OPTIMIZATION REPORT")
        report.append("=" * 80)
        report.append(f"Symbol: {symbol}")
        report.append(f"Period: {start_date} to {end_date}")
        report.append(f"Initial Capital: ₹{self.initial_capital:,.2f}")
        report.append("")
        
        # Summary table
        report.append("PERFORMANCE RANKING:")
        report.append("-" * 80)
        report.append(f"{'Rank':<4} {'Strategy':<15} {'Return %':<10} {'Return ₹':<12} {'Trades':<7} {'Win %':<7} {'Sharpe':<8}")
        report.append("-" * 80)
        
        for i, result in enumerate(results, 1):
            report.append(
                f"{i:<4} {result.strategy_name:<15} "
                f"{result.total_return_percent:>8.2f}% "
                f"₹{result.total_return:>9,.0f} "
                f"{result.total_trades:>5} "
                f"{result.win_rate:>5.1f}% "
                f"{result.sharpe_ratio:>6.2f}"
            )
        
        report.append("-" * 80)
        
        # Best strategy details
        if results:
            best = results[0]
            report.append("")
            report.append("BEST STRATEGY DETAILS:")
            report.append("-" * 40)
            report.append(f"Strategy: {best.strategy_name}")
            report.append(f"Total Return: ₹{best.total_return:,.2f} ({best.total_return_percent:.2f}%)")
            report.append(f"Final Capital: ₹{best.final_capital:,.2f}")
            report.append(f"Total Trades: {best.total_trades}")
            report.append(f"Win Rate: {best.win_rate:.1f}%")
            report.append(f"Average Profit: ₹{best.avg_profit:.2f}")
            report.append(f"Average Loss: ₹{abs(best.avg_loss):.2f}")
            report.append(f"Max Drawdown: {best.max_drawdown:.2f}%")
            report.append(f"Sharpe Ratio: {best.sharpe_ratio:.2f}")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def compare_strategies(self, 
                          symbol: str,
                          start_date: str,
                          end_date: str,
                          strategy_names: List[str]) -> pd.DataFrame:
        """
        Compare specific strategies and return as DataFrame
        
        Returns:
            DataFrame with strategy comparison
        """
        
        results = self.optimize_strategies(symbol, start_date, end_date, strategy_names)
        
        if not results:
            return pd.DataFrame()
        
        data = []
        for result in results:
            data.append({
                'Strategy': result.strategy_name,
                'Return %': result.total_return_percent,
                'Return ₹': result.total_return,
                'Final Capital': result.final_capital,
                'Total Trades': result.total_trades,
                'Win Rate %': result.win_rate,
                'Avg Profit': result.avg_profit,
                'Avg Loss': abs(result.avg_loss),
                'Max Drawdown %': result.max_drawdown,
                'Sharpe Ratio': result.sharpe_ratio
            })
        
        df = pd.DataFrame(data)
        return df.sort_values('Return %', ascending=False)

# Global optimizer instance
_strategy_optimizer = None

def get_strategy_optimizer() -> StrategyOptimizer:
    """Get the global strategy optimizer"""
    global _strategy_optimizer
    if _strategy_optimizer is None:
        _strategy_optimizer = StrategyOptimizer()
    return _strategy_optimizer
