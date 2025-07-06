"""
Find the best trading strategy for RELIANCE from Jan 1st to June 1st, 2025
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.optimization.strategy_optimizer import get_strategy_optimizer
from src.trading.strategies import STRATEGIES
import pandas as pd

def find_best_strategy_for_reliance():
    """Find the best strategy for RELIANCE in the specified period"""
    
    print("🔍 FINDING BEST STRATEGY FOR RELIANCE")
    print("=" * 60)
    print("Period: January 1, 2025 to June 1, 2025")
    print("Symbol: RELIANCE")
    print("Initial Capital: ₹1,00,000")
    print("")
    
    # Initialize optimizer
    optimizer = get_strategy_optimizer()
    
    # Define the period
    start_date = "2025-01-01"
    end_date = "2025-06-01"
    symbol = "RELIANCE"
    
    print("📊 Available strategies to test:")
    for i, strategy_name in enumerate(STRATEGIES.keys(), 1):
        print(f"  {i}. {strategy_name}")
    print("")
    
    print("🚀 Starting optimization...")
    print("-" * 40)
    
    try:
        # Run optimization
        results = optimizer.optimize_strategies(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )
        
        if not results:
            print("❌ No valid results found!")
            return
        
        print(f"✅ Optimization completed! Tested {len(results)} strategies.")
        print("")
        
        # Display results
        print("📈 STRATEGY PERFORMANCE RANKING:")
        print("=" * 80)
        print(f"{'Rank':<4} {'Strategy':<15} {'Return %':<10} {'Return ₹':<12} {'Trades':<7} {'Win %':<7} {'Sharpe':<8}")
        print("-" * 80)
        
        for i, result in enumerate(results, 1):
            return_color = "🟢" if result.total_return_percent > 0 else "🔴" if result.total_return_percent < 0 else "⚪"
            print(
                f"{i:<4} {result.strategy_name:<15} "
                f"{return_color} {result.total_return_percent:>6.2f}% "
                f"₹{result.total_return:>9,.0f} "
                f"{result.total_trades:>5} "
                f"{result.win_rate:>5.1f}% "
                f"{result.sharpe_ratio:>6.2f}"
            )
        
        print("-" * 80)
        
        # Highlight the best strategy
        best_strategy = results[0]
        print("")
        print("🏆 BEST STRATEGY FOUND:")
        print("=" * 40)
        print(f"🎯 Strategy: {best_strategy.strategy_name.upper()}")
        print(f"💰 Total Return: ₹{best_strategy.total_return:,.2f}")
        print(f"📊 Return Percentage: {best_strategy.total_return_percent:.2f}%")
        print(f"💵 Final Capital: ₹{best_strategy.final_capital:,.2f}")
        print(f"🔄 Total Trades: {best_strategy.total_trades}")
        print(f"🎯 Win Rate: {best_strategy.win_rate:.1f}%")
        print(f"📈 Average Profit: ₹{best_strategy.avg_profit:.2f}")
        print(f"📉 Average Loss: ₹{abs(best_strategy.avg_loss):.2f}")
        print(f"⬇️  Max Drawdown: {best_strategy.max_drawdown:.2f}%")
        print(f"📊 Sharpe Ratio: {best_strategy.sharpe_ratio:.2f}")
        
        # Performance analysis
        print("")
        print("📋 PERFORMANCE ANALYSIS:")
        print("-" * 30)
        
        if best_strategy.total_return_percent > 5:
            print("🟢 Excellent performance! Strategy significantly outperformed.")
        elif best_strategy.total_return_percent > 0:
            print("🟡 Positive performance. Strategy generated profits.")
        elif best_strategy.total_return_percent > -5:
            print("🟠 Modest losses. Strategy performed close to break-even.")
        else:
            print("🔴 Poor performance. Strategy generated significant losses.")
        
        if best_strategy.win_rate > 60:
            print("🎯 High win rate indicates good signal quality.")
        elif best_strategy.win_rate > 40:
            print("⚖️  Moderate win rate. Risk management is important.")
        else:
            print("⚠️  Low win rate. Strategy may need refinement.")
        
        if best_strategy.total_trades < 5:
            print("⚠️  Low trade frequency. Consider longer testing period.")
        elif best_strategy.total_trades > 20:
            print("🔄 High trade frequency. Good for active trading.")
        else:
            print("✅ Moderate trade frequency. Balanced approach.")
        
        # Comparison with other strategies
        profitable_strategies = [r for r in results if r.total_return_percent > 0]
        print("")
        print(f"📊 SUMMARY:")
        print(f"   • {len(profitable_strategies)}/{len(results)} strategies were profitable")
        print(f"   • Best return: {best_strategy.total_return_percent:.2f}%")
        print(f"   • Worst return: {results[-1].total_return_percent:.2f}%")
        
        if len(profitable_strategies) > 1:
            second_best = profitable_strategies[1] if len(profitable_strategies) > 1 else None
            if second_best:
                print(f"   • Second best: {second_best.strategy_name} ({second_best.total_return_percent:.2f}%)")
        
        print("")
        print("🎉 Analysis complete! Use the best strategy for your trading.")
        
        # Save detailed report
        report = optimizer.generate_optimization_report(symbol, start_date, end_date)
        with open("strategy_optimization_report.txt", "w") as f:
            f.write(report)
        print("📄 Detailed report saved to 'strategy_optimization_report.txt'")
        
    except Exception as e:
        print(f"❌ Error during optimization: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_best_strategy_for_reliance()
