"""
Test ChartInk strategies against RELIANCE data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.optimization.strategy_optimizer import get_strategy_optimizer
from src.trading.strategies import STRATEGIES

def test_all_strategies():
    """Test all strategies including new ChartInk ones"""
    
    print("🚀 TESTING ALL STRATEGIES INCLUDING CHARTINK SCANS")
    print("=" * 60)
    print("Symbol: RELIANCE")
    print("Period: January 1, 2025 to June 1, 2025")
    print("Initial Capital: ₹1,00,000")
    print("")
    
    # Show all available strategies
    print("📊 Available strategies:")
    for i, strategy_name in enumerate(STRATEGIES.keys(), 1):
        strategy_type = "ChartInk" if strategy_name in ['sma200_breakout', 'high_rsi_breakout', 'bull_gap', 'morning_star'] else "Original"
        print(f"  {i:2d}. {strategy_name:<20} ({strategy_type})")
    print("")
    
    optimizer = get_strategy_optimizer()
    
    print("🔍 Running comprehensive strategy optimization...")
    print("-" * 50)
    
    try:
        # Test all strategies
        results = optimizer.optimize_strategies(
            symbol="RELIANCE",
            start_date="2025-01-01",
            end_date="2025-06-01"
        )
        
        if not results:
            print("❌ No valid results found!")
            return
        
        print(f"✅ Optimization completed! Tested {len(results)} strategies.")
        print("")
        
        # Separate original and ChartInk strategies
        original_strategies = []
        chartink_strategies = []
        
        for result in results:
            if result.strategy_name in ['sma200_breakout', 'high_rsi_breakout', 'bull_gap', 'morning_star']:
                chartink_strategies.append(result)
            else:
                original_strategies.append(result)
        
        # Display results
        print("📈 COMPLETE STRATEGY PERFORMANCE RANKING:")
        print("=" * 85)
        print(f"{'Rank':<4} {'Strategy':<20} {'Type':<10} {'Return %':<10} {'Return ₹':<12} {'Trades':<7} {'Win %':<7}")
        print("-" * 85)
        
        for i, result in enumerate(results, 1):
            strategy_type = "ChartInk" if result.strategy_name in ['sma200_breakout', 'high_rsi_breakout', 'bull_gap', 'morning_star'] else "Original"
            return_color = "🟢" if result.total_return_percent > 0 else "🔴" if result.total_return_percent < 0 else "⚪"
            
            print(
                f"{i:<4} {result.strategy_name:<20} {strategy_type:<10} "
                f"{return_color} {result.total_return_percent:>6.2f}% "
                f"₹{result.total_return:>9,.0f} "
                f"{result.total_trades:>5} "
                f"{result.win_rate:>5.1f}%"
            )
        
        print("-" * 85)
        
        # Analysis by type
        print("")
        print("📊 ANALYSIS BY STRATEGY TYPE:")
        print("=" * 40)
        
        if original_strategies:
            print("\n🔵 ORIGINAL STRATEGIES:")
            best_original = max(original_strategies, key=lambda x: x.total_return_percent)
            avg_return_original = sum(s.total_return_percent for s in original_strategies) / len(original_strategies)
            profitable_original = len([s for s in original_strategies if s.total_return_percent > 0])
            
            print(f"  Best: {best_original.strategy_name} ({best_original.total_return_percent:.2f}%)")
            print(f"  Average return: {avg_return_original:.2f}%")
            print(f"  Profitable: {profitable_original}/{len(original_strategies)}")
        
        if chartink_strategies:
            print("\n🟡 CHARTINK STRATEGIES:")
            best_chartink = max(chartink_strategies, key=lambda x: x.total_return_percent)
            avg_return_chartink = sum(s.total_return_percent for s in chartink_strategies) / len(chartink_strategies)
            profitable_chartink = len([s for s in chartink_strategies if s.total_return_percent > 0])
            
            print(f"  Best: {best_chartink.strategy_name} ({best_chartink.total_return_percent:.2f}%)")
            print(f"  Average return: {avg_return_chartink:.2f}%")
            print(f"  Profitable: {profitable_chartink}/{len(chartink_strategies)}")
        
        # Overall winner
        best_overall = results[0]
        print("")
        print("🏆 OVERALL WINNER:")
        print("=" * 30)
        strategy_type = "ChartInk" if best_overall.strategy_name in ['sma200_breakout', 'high_rsi_breakout', 'bull_gap', 'morning_star'] else "Original"
        print(f"🎯 Strategy: {best_overall.strategy_name.upper()} ({strategy_type})")
        print(f"💰 Total Return: ₹{best_overall.total_return:,.2f}")
        print(f"📊 Return Percentage: {best_overall.total_return_percent:.2f}%")
        print(f"🔄 Total Trades: {best_overall.total_trades}")
        print(f"🎯 Win Rate: {best_overall.win_rate:.1f}%")
        print(f"📊 Sharpe Ratio: {best_overall.sharpe_ratio:.2f}")
        
        # Comparison insights
        print("")
        print("💡 KEY INSIGHTS:")
        print("-" * 20)
        
        if chartink_strategies and original_strategies:
            chartink_avg = sum(s.total_return_percent for s in chartink_strategies) / len(chartink_strategies)
            original_avg = sum(s.total_return_percent for s in original_strategies) / len(original_strategies)
            
            if chartink_avg > original_avg:
                print(f"✨ ChartInk strategies outperformed on average ({chartink_avg:.2f}% vs {original_avg:.2f}%)")
            else:
                print(f"📈 Original strategies outperformed on average ({original_avg:.2f}% vs {chartink_avg:.2f}%)")
        
        # Top 3 strategies
        print("")
        print("🥇 TOP 3 STRATEGIES:")
        for i, result in enumerate(results[:3], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            strategy_type = "ChartInk" if result.strategy_name in ['sma200_breakout', 'high_rsi_breakout', 'bull_gap', 'morning_star'] else "Original"
            print(f"  {medal} {result.strategy_name} ({strategy_type}): {result.total_return_percent:.2f}%")
        
        print("")
        print("🎉 Analysis complete! ChartInk strategies have been successfully tested.")
        
    except Exception as e:
        print(f"❌ Error during optimization: {e}")
        import traceback
        traceback.print_exc()

def test_specific_chartink_strategy():
    """Test a specific ChartInk strategy in detail"""
    
    print("\n" + "=" * 60)
    print("🔍 DETAILED CHARTINK STRATEGY ANALYSIS")
    print("=" * 60)
    
    # Test the SMA200 breakout strategy specifically
    optimizer = get_strategy_optimizer()
    
    try:
        results = optimizer.optimize_strategies(
            symbol="RELIANCE",
            start_date="2025-01-01",
            end_date="2025-06-01",
            strategies=['sma200_breakout']  # Test just this one
        )
        
        if results:
            result = results[0]
            print("📊 SMA200 BREAKOUT STRATEGY DETAILS:")
            print("-" * 40)
            print(f"Strategy: {result.strategy_name}")
            print(f"Description: 4H closing above 200 SMA breakout")
            print(f"Return: {result.total_return_percent:.2f}% (₹{result.total_return:,.2f})")
            print(f"Trades: {result.total_trades}")
            print(f"Win Rate: {result.win_rate:.1f}%")
            print(f"Avg Profit: ₹{result.avg_profit:.2f}")
            print(f"Avg Loss: ₹{abs(result.avg_loss):.2f}")
            print(f"Max Drawdown: {result.max_drawdown:.2f}%")
            print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
            
            if result.total_return_percent > 0:
                print("✅ This ChartInk strategy is profitable!")
            else:
                print("⚠️ This strategy needs optimization for current market conditions.")
        else:
            print("❌ No results for SMA200 breakout strategy")
            
    except Exception as e:
        print(f"❌ Error testing specific strategy: {e}")

if __name__ == "__main__":
    test_all_strategies()
    test_specific_chartink_strategy()
