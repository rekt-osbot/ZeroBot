"""
Quick strategy optimization for RELIANCE - simplified version
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.optimization.strategy_optimizer import get_strategy_optimizer

def quick_test():
    """Quick test to confirm the results"""
    
    print("RELIANCE Strategy Optimization Results (Jan 1 - June 1, 2025)")
    print("=" * 65)
    
    optimizer = get_strategy_optimizer()
    
    results = optimizer.optimize_strategies(
        symbol="RELIANCE",
        start_date="2025-01-01", 
        end_date="2025-06-01"
    )
    
    print(f"Tested {len(results)} strategies:")
    print()
    
    for i, result in enumerate(results, 1):
        status = "PROFIT" if result.total_return_percent > 0 else "LOSS"
        print(f"{i}. {result.strategy_name.upper()}")
        print(f"   Return: {result.total_return_percent:.2f}% ({status})")
        print(f"   Trades: {result.total_trades}, Win Rate: {result.win_rate:.1f}%")
        print(f"   Sharpe: {result.sharpe_ratio:.2f}")
        print()
    
    best = results[0]
    print("WINNER: " + best.strategy_name.upper())
    print(f"Best return: {best.total_return_percent:.2f}%")
    print(f"Final capital: Rs {best.final_capital:,.0f}")

if __name__ == "__main__":
    quick_test()
