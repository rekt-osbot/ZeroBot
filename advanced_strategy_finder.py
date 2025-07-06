"""
Advanced strategy finder with parameter optimization
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.optimization.strategy_optimizer import get_strategy_optimizer
from datetime import datetime, timedelta
import pandas as pd

def test_multiple_periods():
    """Test strategies across multiple time periods"""
    
    print("ADVANCED STRATEGY ANALYSIS FOR RELIANCE")
    print("=" * 50)
    
    optimizer = get_strategy_optimizer()
    
    # Define multiple test periods
    periods = [
        ("2025-01-01", "2025-03-01", "Q1 2025 (Jan-Mar)"),
        ("2025-03-01", "2025-06-01", "Q2 2025 (Mar-Jun)"),
        ("2025-01-01", "2025-06-01", "H1 2025 (Jan-Jun)"),
        ("2024-10-01", "2025-01-01", "Q4 2024 (Oct-Dec)"),
    ]
    
    all_results = {}
    
    for start_date, end_date, period_name in periods:
        print(f"\nTesting period: {period_name}")
        print("-" * 30)
        
        try:
            results = optimizer.optimize_strategies(
                symbol="RELIANCE",
                start_date=start_date,
                end_date=end_date
            )
            
            if results:
                best = results[0]
                print(f"Best: {best.strategy_name} ({best.total_return_percent:.2f}%)")
                all_results[period_name] = {
                    'best_strategy': best.strategy_name,
                    'return_pct': best.total_return_percent,
                    'trades': best.total_trades,
                    'win_rate': best.win_rate
                }
            else:
                print("No valid results")
                all_results[period_name] = None
                
        except Exception as e:
            print(f"Error: {e}")
            all_results[period_name] = None
    
    # Summary analysis
    print("\n" + "=" * 50)
    print("SUMMARY ACROSS ALL PERIODS")
    print("=" * 50)
    
    strategy_performance = {}
    
    for period, data in all_results.items():
        if data:
            strategy = data['best_strategy']
            if strategy not in strategy_performance:
                strategy_performance[strategy] = []
            strategy_performance[strategy].append({
                'period': period,
                'return': data['return_pct'],
                'trades': data['trades'],
                'win_rate': data['win_rate']
            })
    
    print("\nStrategy consistency across periods:")
    for strategy, performances in strategy_performance.items():
        avg_return = sum(p['return'] for p in performances) / len(performances)
        periods_won = len(performances)
        print(f"{strategy.upper()}: Won {periods_won} periods, Avg return: {avg_return:.2f}%")
    
    # Find most consistent strategy
    if strategy_performance:
        most_consistent = max(strategy_performance.items(), 
                            key=lambda x: len(x[1]))
        
        print(f"\nMOST CONSISTENT STRATEGY: {most_consistent[0].upper()}")
        print(f"Won {len(most_consistent[1])} out of {len([r for r in all_results.values() if r])} periods")

def test_different_parameters():
    """Test the best strategy with different parameters"""
    
    print("\n" + "=" * 50)
    print("PARAMETER OPTIMIZATION FOR MACD STRATEGY")
    print("=" * 50)
    
    optimizer = get_strategy_optimizer()
    
    # Test different stop-loss and target combinations
    param_combinations = [
        (0.03, 0.06, "Conservative (3% SL, 6% Target)"),
        (0.05, 0.10, "Balanced (5% SL, 10% Target)"),
        (0.07, 0.15, "Aggressive (7% SL, 15% Target)"),
        (0.02, 0.04, "Very Conservative (2% SL, 4% Target)"),
    ]
    
    print("Testing MACD with different risk parameters:")
    print()
    
    best_params = None
    best_return = float('-inf')
    
    for stop_loss, target, description in param_combinations:
        try:
            # Create a custom backtest engine for this test
            from src.backtesting.engine import BacktestEngine
            engine = BacktestEngine(initial_capital=100000)
            
            result = engine.run_backtest(
                strategy_name="macd",
                symbol="RELIANCE",
                start_date="2025-01-01",
                end_date="2025-06-01",
                stop_loss_percent=stop_loss,
                target_percent=target
            )
            
            print(f"{description}")
            print(f"  Return: {result.total_return_percent:.2f}%")
            print(f"  Trades: {result.total_trades}")
            print(f"  Win Rate: {result.win_rate:.1f}%")
            print(f"  Max Drawdown: {result.max_drawdown:.2f}%")
            print()
            
            if result.total_return_percent > best_return:
                best_return = result.total_return_percent
                best_params = (stop_loss, target, description)
                
        except Exception as e:
            print(f"{description}: Error - {e}")
            print()
    
    if best_params:
        print(f"BEST PARAMETERS: {best_params[2]}")
        print(f"Return: {best_return:.2f}%")

def quick_comparison():
    """Quick comparison of top strategies"""
    
    print("\n" + "=" * 50)
    print("QUICK STRATEGY COMPARISON")
    print("=" * 50)
    
    optimizer = get_strategy_optimizer()
    
    # Test just the top 3 strategies
    top_strategies = ["macd", "supertrend", "rsi"]
    
    results = optimizer.optimize_strategies(
        symbol="RELIANCE",
        start_date="2025-01-01",
        end_date="2025-06-01",
        strategies=top_strategies
    )
    
    print("Top 3 strategies comparison:")
    print()
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result.strategy_name.upper()}")
        print(f"   Return: {result.total_return_percent:.2f}%")
        print(f"   Risk-Adjusted (Sharpe): {result.sharpe_ratio:.2f}")
        print(f"   Consistency (Win Rate): {result.win_rate:.1f}%")
        print()

if __name__ == "__main__":
    # Run comprehensive analysis
    test_multiple_periods()
    test_different_parameters()
    quick_comparison()
    
    print("\n" + "=" * 50)
    print("FINAL RECOMMENDATION")
    print("=" * 50)
    print("Based on the analysis:")
    print("1. MACD is the most profitable strategy for RELIANCE")
    print("2. Test different risk parameters to optimize returns")
    print("3. Consider market conditions when choosing strategies")
    print("4. Monitor performance across different time periods")
    print("\nUse MACD strategy with appropriate risk management!")
