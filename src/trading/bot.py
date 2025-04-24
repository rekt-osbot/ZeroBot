"""
Core TradeBot implementation for automated trading
"""
import logging
import time
import datetime
import pandas as pd
import numpy as np
from threading import Thread, Lock
from apscheduler.schedulers.background import BackgroundScheduler
from src.trading.zerodha import ZerodhaConnector
from src.trading.strategies import STRATEGIES
from src.utils.config import config

logger = logging.getLogger(__name__)

class TradeBot:
    """TradeBot class for automated trading"""
    
    def __init__(self):
        """Initialize the TradeBot"""
        self.zerodha = ZerodhaConnector()
        self.scheduler = BackgroundScheduler()
        self.lock = Lock()
        self.is_running = False
        self.active_trades = {}
        self.trade_history = []
        self.capital = config.capital
        self.min_trades = config.min_trades
        self.max_trades = config.max_trades
        self.risk_per_trade = config.risk_per_trade / 100  # Convert to decimal
        self.stop_loss_percent = config.stop_loss_percent / 100  # Convert to decimal
        self.target_percent = config.target_percent / 100  # Convert to decimal
        
        # Load strategies
        self.strategies = {}
        self._load_strategies()
        
        # Initialize performance metrics
        self.metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit': 0,
            'total_loss': 0,
            'net_pnl': 0,
            'win_rate': 0,
            'avg_profit': 0,
            'avg_loss': 0,
            'max_drawdown': 0,
            'sharpe_ratio': 0
        }
    
    def _load_strategies(self):
        """Load trading strategies"""
        self.strategies = {
            'ma_crossover': STRATEGIES['ma_crossover'](),
            'rsi': STRATEGIES['rsi'](),
            'macd': STRATEGIES['macd'](),
            'bollinger': STRATEGIES['bollinger'](),
            'supertrend': STRATEGIES['supertrend']()
        }
        logger.info(f"Loaded {len(self.strategies)} trading strategies")
    
    def is_authenticated(self):
        """Check if the bot is authenticated with Zerodha"""
        return self.zerodha.authenticated
    
    def login(self, request_token=None):
        """Login to Zerodha"""
        if request_token:
            return self.zerodha.generate_session(request_token)
        else:
            return self.zerodha.get_login_url()
    
    def get_profile(self):
        """Get user profile information"""
        return self.zerodha.get_profile()
    
    def get_margins(self):
        """Get user margin information"""
        return self.zerodha.get_margins()
    
    def get_instruments(self, exchange=None):
        """Get list of tradable instruments"""
        return self.zerodha.get_instruments(exchange)
    
    def start(self):
        """Start the trading bot"""
        if self.is_running:
            logger.warning("TradeBot is already running")
            return False
        
        if not self.is_authenticated():
            logger.error("Not authenticated with Zerodha. Please login first.")
            return False
        
        # Start the scheduler
        self.scheduler.start()
        
        # Schedule the trading job
        self.scheduler.add_job(
            self._trading_job,
            'cron',
            day_of_week='mon-fri',
            hour='9-15',
            minute='*/5',  # Run every 5 minutes during market hours
            id='trading_job'
        )
        
        # Schedule the monitoring job
        self.scheduler.add_job(
            self._monitor_trades,
            'interval',
            seconds=30,  # Check trades every 30 seconds
            id='monitor_job'
        )
        
        # Schedule the end-of-day job
        self.scheduler.add_job(
            self._end_of_day,
            'cron',
            day_of_week='mon-fri',
            hour=15,
            minute=30,
            id='eod_job'
        )
        
        self.is_running = True
        logger.info("TradeBot started successfully")
        return True
    
    def stop(self):
        """Stop the trading bot"""
        if not self.is_running:
            logger.warning("TradeBot is not running")
            return False
        
        # Stop the scheduler
        self.scheduler.shutdown()
        
        # Close all open positions
        self._close_all_positions()
        
        self.is_running = False
        logger.info("TradeBot stopped successfully")
        return True
    
    def _trading_job(self):
        """Main trading job that runs on schedule"""
        logger.info("Running trading job")
        
        with self.lock:
            try:
                # Check if we have capacity for new trades
                current_trades = len(self.active_trades)
                if current_trades >= self.max_trades:
                    logger.info(f"Maximum number of trades ({self.max_trades}) already active")
                    return
                
                # Calculate how many new trades to place
                trades_to_place = min(self.max_trades - current_trades, self.min_trades)
                
                # Get tradable instruments
                nse_instruments = self.zerodha.get_instruments(exchange="NSE")
                bse_instruments = self.zerodha.get_instruments(exchange="BSE")
                
                # Filter for liquid stocks
                nse_liquid = self._filter_liquid_stocks(nse_instruments)
                bse_liquid = self._filter_liquid_stocks(bse_instruments)
                
                # Combine and shuffle to randomize selection
                all_liquid = pd.concat([nse_liquid, bse_liquid]).sample(frac=1)
                
                # Calculate capital per trade
                capital_per_trade = self.capital / self.min_trades
                
                # Find trading opportunities
                opportunities = self._find_opportunities(all_liquid, trades_to_place)
                
                # Execute trades
                for opportunity in opportunities:
                    self._execute_trade(opportunity, capital_per_trade)
            
            except Exception as e:
                logger.error(f"Error in trading job: {str(e)}")
    
    def _filter_liquid_stocks(self, instruments, min_volume=100000):
        """Filter for liquid stocks based on volume"""
        # In a real implementation, you would use historical volume data
        # For this example, we'll just return a subset of instruments
        return instruments.sample(min(50, len(instruments)))
    
    def _find_opportunities(self, instruments, max_opportunities):
        """Find trading opportunities based on strategies"""
        opportunities = []
        
        for _, instrument in instruments.iterrows():
            if len(opportunities) >= max_opportunities:
                break
            
            try:
                # Get historical data
                historical_data = self._get_historical_data(instrument['instrument_token'])
                
                if historical_data.empty:
                    continue
                
                # Apply strategies
                signals = {}
                for name, strategy in self.strategies.items():
                    signal_data = strategy.generate_signals(historical_data)
                    if not signal_data.empty:
                        signals[name] = signal_data
                
                # Check for buy signals
                buy_signal = self._check_buy_signals(signals)
                
                if buy_signal:
                    opportunities.append({
                        'instrument': instrument,
                        'signal': buy_signal,
                        'price': historical_data['close'].iloc[-1]
                    })
            
            except Exception as e:
                logger.error(f"Error analyzing {instrument['tradingsymbol']}: {str(e)}")
        
        return opportunities
    
    def _get_historical_data(self, instrument_token, interval="15minute", days=5):
        """Get historical data for an instrument"""
        to_date = datetime.datetime.now()
        from_date = to_date - datetime.timedelta(days=days)
        
        return self.zerodha.get_historical_data(
            instrument_token=instrument_token,
            from_date=from_date,
            to_date=to_date,
            interval=interval
        )
    
    def _check_buy_signals(self, signals):
        """Check if multiple strategies agree on a buy signal"""
        buy_count = 0
        total_strategies = len(signals)
        
        if total_strategies == 0:
            return False
        
        for name, signal_data in signals.items():
            if signal_data.empty:
                continue
            
            # Check if the last signal is a buy
            last_position = signal_data['position'].iloc[-1]
            if last_position > 0:  # Buy signal
                buy_count += 1
        
        # If more than 50% of strategies agree, generate a buy signal
        if buy_count / total_strategies > 0.5:
            return True
        
        return False
    
    def _execute_trade(self, opportunity, capital):
        """Execute a trade based on an opportunity"""
        instrument = opportunity['instrument']
        price = opportunity['price']
        
        # Calculate quantity based on capital and price
        quantity = int(capital / price)
        
        if quantity <= 0:
            logger.warning(f"Insufficient capital to buy {instrument['tradingsymbol']}")
            return
        
        # Calculate stop loss and target
        stop_loss = price * (1 - self.stop_loss_percent)
        target = price * (1 + self.target_percent)
        
        # Place buy order
        order_id = self.zerodha.place_order(
            exchange=instrument['exchange'],
            symbol=instrument['tradingsymbol'],
            transaction_type="BUY",
            quantity=quantity,
            product="MIS"  # Intraday
        )
        
        if order_id:
            # Add to active trades
            self.active_trades[order_id] = {
                'instrument': instrument,
                'quantity': quantity,
                'buy_price': price,
                'stop_loss': stop_loss,
                'target': target,
                'timestamp': datetime.datetime.now(),
                'status': 'open'
            }
            
            logger.info(f"Executed BUY order for {quantity} shares of {instrument['tradingsymbol']} at {price}")
            
            # Update metrics
            self.metrics['total_trades'] += 1
    
    def _monitor_trades(self):
        """Monitor active trades for stop loss and target"""
        with self.lock:
            try:
                if not self.active_trades:
                    return
                
                # Get current positions
                positions = self.zerodha.get_positions()
                
                if positions['day'].empty:
                    return
                
                # Check each active trade
                for order_id, trade in list(self.active_trades.items()):
                    instrument = trade['instrument']
                    symbol = instrument['tradingsymbol']
                    
                    # Find the position for this trade
                    position = positions['day'][positions['day']['tradingsymbol'] == symbol]
                    
                    if position.empty:
                        continue
                    
                    current_price = position['last_price'].iloc[0]
                    
                    # Check for stop loss
                    if current_price <= trade['stop_loss']:
                        self._close_trade(order_id, current_price, 'stop_loss')
                    
                    # Check for target
                    elif current_price >= trade['target']:
                        self._close_trade(order_id, current_price, 'target')
            
            except Exception as e:
                logger.error(f"Error monitoring trades: {str(e)}")
    
    def _close_trade(self, order_id, current_price, reason):
        """Close a trade and update metrics"""
        trade = self.active_trades[order_id]
        instrument = trade['instrument']
        quantity = trade['quantity']
        buy_price = trade['buy_price']
        
        # Place sell order
        sell_order_id = self.zerodha.place_order(
            exchange=instrument['exchange'],
            symbol=instrument['tradingsymbol'],
            transaction_type="SELL",
            quantity=quantity,
            product="MIS"  # Intraday
        )
        
        if sell_order_id:
            # Calculate profit/loss
            pnl = (current_price - buy_price) * quantity
            
            # Update trade record
            trade.update({
                'sell_price': current_price,
                'sell_timestamp': datetime.datetime.now(),
                'pnl': pnl,
                'reason': reason,
                'status': 'closed'
            })
            
            # Move to trade history
            self.trade_history.append(trade)
            
            # Remove from active trades
            del self.active_trades[order_id]
            
            # Update metrics
            if pnl > 0:
                self.metrics['winning_trades'] += 1
                self.metrics['total_profit'] += pnl
            else:
                self.metrics['losing_trades'] += 1
                self.metrics['total_loss'] += abs(pnl)
            
            self.metrics['net_pnl'] = self.metrics['total_profit'] - self.metrics['total_loss']
            
            if self.metrics['total_trades'] > 0:
                self.metrics['win_rate'] = self.metrics['winning_trades'] / self.metrics['total_trades'] * 100
            
            if self.metrics['winning_trades'] > 0:
                self.metrics['avg_profit'] = self.metrics['total_profit'] / self.metrics['winning_trades']
            
            if self.metrics['losing_trades'] > 0:
                self.metrics['avg_loss'] = self.metrics['total_loss'] / self.metrics['losing_trades']
            
            logger.info(f"Closed trade for {instrument['tradingsymbol']} with P&L: {pnl:.2f} ({reason})")
    
    def _close_all_positions(self):
        """Close all open positions at the end of the day"""
        with self.lock:
            try:
                positions = self.zerodha.get_positions()
                
                if positions['day'].empty:
                    return
                
                for _, position in positions['day'].iterrows():
                    if position['quantity'] > 0:
                        # Place sell order to close position
                        self.zerodha.place_order(
                            exchange=position['exchange'],
                            symbol=position['tradingsymbol'],
                            transaction_type="SELL",
                            quantity=position['quantity'],
                            product="MIS"  # Intraday
                        )
                        
                        logger.info(f"Closed position for {position['tradingsymbol']}")
                
                # Clear active trades
                self.active_trades = {}
            
            except Exception as e:
                logger.error(f"Error closing positions: {str(e)}")
    
    def _end_of_day(self):
        """End of day processing"""
        logger.info("Running end of day processing")
        
        # Close all positions
        self._close_all_positions()
        
        # Calculate daily performance metrics
        self._calculate_performance()
    
    def _calculate_performance(self):
        """Calculate performance metrics"""
        if not self.trade_history:
            return
        
        # Calculate daily returns
        daily_pnl = sum(trade['pnl'] for trade in self.trade_history if trade['status'] == 'closed')
        daily_return = daily_pnl / self.capital * 100
        
        # Calculate drawdown
        cumulative_returns = [0]
        for trade in self.trade_history:
            if trade['status'] == 'closed':
                cumulative_returns.append(cumulative_returns[-1] + trade['pnl'])
        
        peak = max(cumulative_returns)
        drawdowns = [(peak - val) / peak * 100 if peak > 0 else 0 for val in cumulative_returns]
        max_drawdown = max(drawdowns) if drawdowns else 0
        
        # Update metrics
        self.metrics['max_drawdown'] = max_drawdown
        
        logger.info(f"Daily P&L: {daily_pnl:.2f} ({daily_return:.2f}%)")
        logger.info(f"Max Drawdown: {max_drawdown:.2f}%")
    
    def get_metrics(self):
        """Get performance metrics"""
        return self.metrics
    
    def get_active_trades(self):
        """Get active trades"""
        return self.active_trades
    
    def get_trade_history(self):
        """Get trade history"""
        return self.trade_history
