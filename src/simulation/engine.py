"""
Simulation engine for consistent trading simulation
"""
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import uuid
from dataclasses import dataclass, asdict
from src.data.providers import get_data_provider

logger = logging.getLogger(__name__)

@dataclass
class Position:
    """Represents a trading position"""
    symbol: str
    exchange: str
    quantity: int
    average_price: float
    current_price: float
    pnl: float
    pnl_percent: float
    timestamp: datetime
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)

@dataclass
class Order:
    """Represents a trading order"""
    order_id: str
    symbol: str
    exchange: str
    transaction_type: str  # BUY/SELL
    quantity: int
    price: float
    order_type: str  # MARKET/LIMIT
    status: str  # PENDING/EXECUTED/CANCELLED
    timestamp: datetime
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)

@dataclass
class Trade:
    """Represents a completed trade"""
    trade_id: str
    order_id: str
    symbol: str
    exchange: str
    transaction_type: str
    quantity: int
    price: float
    timestamp: datetime
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)

class SimulationEngine:
    """Simulation engine that maintains consistent state"""
    
    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions: Dict[str, Position] = {}
        self.orders: Dict[str, Order] = {}
        self.trades: List[Trade] = []
        self.data_provider = get_data_provider(simulation_mode=True)
        
        # Performance tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_profit = 0.0
        self.total_loss = 0.0
        
        logger.info(f"Simulation engine initialized with capital: ₹{initial_capital:,.2f}")
    
    def place_order(self, symbol: str, exchange: str, transaction_type: str, 
                   quantity: int, price: Optional[float] = None, 
                   order_type: str = "MARKET") -> str:
        """Place an order in the simulation"""
        order_id = str(uuid.uuid4())
        
        # Get current price if not specified
        if price is None:
            price = self.data_provider.get_current_price(symbol)
        
        if price <= 0:
            logger.error(f"Invalid price for {symbol}: {price}")
            return None
        
        # Check if we have enough capital for buy orders
        if transaction_type == "BUY":
            required_capital = price * quantity
            if required_capital > self.current_capital:
                logger.error(f"Insufficient capital. Required: ₹{required_capital:,.2f}, Available: ₹{self.current_capital:,.2f}")
                return None
        
        # Check if we have enough quantity for sell orders
        if transaction_type == "SELL":
            position_key = f"{exchange}:{symbol}"
            if position_key not in self.positions:
                logger.error(f"No position found for {symbol} to sell")
                return None
            
            if self.positions[position_key].quantity < quantity:
                logger.error(f"Insufficient quantity. Available: {self.positions[position_key].quantity}, Required: {quantity}")
                return None
        
        # Create order
        order = Order(
            order_id=order_id,
            symbol=symbol,
            exchange=exchange,
            transaction_type=transaction_type,
            quantity=quantity,
            price=price,
            order_type=order_type,
            status="PENDING",
            timestamp=datetime.now()
        )
        
        self.orders[order_id] = order
        
        # Execute order immediately (market order simulation)
        if order_type == "MARKET":
            self._execute_order(order_id)
        
        logger.info(f"Order placed: {transaction_type} {quantity} {symbol} at ₹{price:.2f}")
        return order_id
    
    def _execute_order(self, order_id: str) -> bool:
        """Execute a pending order"""
        if order_id not in self.orders:
            logger.error(f"Order {order_id} not found")
            return False
        
        order = self.orders[order_id]
        if order.status != "PENDING":
            logger.warning(f"Order {order_id} is not pending")
            return False
        
        # Create trade
        trade = Trade(
            trade_id=str(uuid.uuid4()),
            order_id=order_id,
            symbol=order.symbol,
            exchange=order.exchange,
            transaction_type=order.transaction_type,
            quantity=order.quantity,
            price=order.price,
            timestamp=datetime.now()
        )
        
        self.trades.append(trade)
        
        # Update positions and capital
        position_key = f"{order.exchange}:{order.symbol}"
        
        if order.transaction_type == "BUY":
            self._handle_buy_trade(trade, position_key)
        else:
            self._handle_sell_trade(trade, position_key)
        
        # Update order status
        order.status = "EXECUTED"
        
        logger.info(f"Order executed: {trade.transaction_type} {trade.quantity} {trade.symbol} at ₹{trade.price:.2f}")
        return True
    
    def _handle_buy_trade(self, trade: Trade, position_key: str):
        """Handle a buy trade"""
        cost = trade.price * trade.quantity
        self.current_capital -= cost
        
        if position_key in self.positions:
            # Add to existing position
            position = self.positions[position_key]
            total_quantity = position.quantity + trade.quantity
            total_cost = (position.average_price * position.quantity) + cost
            new_average_price = total_cost / total_quantity
            
            position.quantity = total_quantity
            position.average_price = new_average_price
        else:
            # Create new position
            position = Position(
                symbol=trade.symbol,
                exchange=trade.exchange,
                quantity=trade.quantity,
                average_price=trade.price,
                current_price=trade.price,
                pnl=0.0,
                pnl_percent=0.0,
                timestamp=trade.timestamp
            )
            self.positions[position_key] = position
    
    def _handle_sell_trade(self, trade: Trade, position_key: str):
        """Handle a sell trade"""
        revenue = trade.price * trade.quantity
        self.current_capital += revenue
        
        if position_key in self.positions:
            position = self.positions[position_key]
            
            # Calculate P&L for this trade
            cost_basis = position.average_price * trade.quantity
            pnl = revenue - cost_basis
            
            if pnl > 0:
                self.winning_trades += 1
                self.total_profit += pnl
            else:
                self.losing_trades += 1
                self.total_loss += abs(pnl)
            
            self.total_trades += 1
            
            # Update position
            position.quantity -= trade.quantity
            
            # Remove position if quantity is zero
            if position.quantity <= 0:
                del self.positions[position_key]
    
    def update_positions(self):
        """Update current prices and P&L for all positions"""
        for position_key, position in self.positions.items():
            current_price = self.data_provider.get_current_price(position.symbol)
            if current_price > 0:
                position.current_price = current_price
                position.pnl = (current_price - position.average_price) * position.quantity
                position.pnl_percent = (position.pnl / (position.average_price * position.quantity)) * 100
    
    def get_positions(self) -> Dict[str, List[Dict]]:
        """Get current positions in Zerodha format"""
        self.update_positions()
        
        day_positions = []
        net_positions = []
        
        for position in self.positions.values():
            pos_dict = {
                'tradingsymbol': position.symbol,
                'exchange': position.exchange,
                'quantity': position.quantity,
                'average_price': position.average_price,
                'last_price': position.current_price,
                'pnl': position.pnl,
                'product': 'MIS',
                'instrument_token': 0  # Placeholder
            }
            day_positions.append(pos_dict)
            net_positions.append(pos_dict)
        
        return {
            'day': pd.DataFrame(day_positions),
            'net': pd.DataFrame(net_positions)
        }
    
    def get_order_history(self, order_id: Optional[str] = None) -> pd.DataFrame:
        """Get order history"""
        if order_id:
            if order_id in self.orders:
                return pd.DataFrame([self.orders[order_id].to_dict()])
            else:
                return pd.DataFrame()
        
        orders_data = [order.to_dict() for order in self.orders.values()]
        return pd.DataFrame(orders_data)
    
    def get_trade_history(self) -> List[Dict]:
        """Get trade history"""
        return [trade.to_dict() for trade in self.trades]
    
    def get_portfolio_value(self) -> float:
        """Get total portfolio value"""
        self.update_positions()
        
        position_value = sum(
            position.current_price * position.quantity 
            for position in self.positions.values()
        )
        
        return self.current_capital + position_value
    
    def get_performance_metrics(self) -> Dict:
        """Get performance metrics"""
        portfolio_value = self.get_portfolio_value()
        total_return = portfolio_value - self.initial_capital
        total_return_percent = (total_return / self.initial_capital) * 100
        
        win_rate = (self.winning_trades / max(self.total_trades, 1)) * 100
        avg_profit = self.total_profit / max(self.winning_trades, 1)
        avg_loss = self.total_loss / max(self.losing_trades, 1)
        
        return {
            'initial_capital': self.initial_capital,
            'current_capital': self.current_capital,
            'portfolio_value': portfolio_value,
            'total_return': total_return,
            'total_return_percent': total_return_percent,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': win_rate,
            'total_profit': self.total_profit,
            'total_loss': self.total_loss,
            'avg_profit': avg_profit,
            'avg_loss': avg_loss
        }
    
    def reset(self):
        """Reset simulation to initial state"""
        self.current_capital = self.initial_capital
        self.positions.clear()
        self.orders.clear()
        self.trades.clear()
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_profit = 0.0
        self.total_loss = 0.0
        
        logger.info("Simulation engine reset")

# Global simulation engine instance
_simulation_engine = None

def get_simulation_engine() -> SimulationEngine:
    """Get the global simulation engine"""
    global _simulation_engine
    if _simulation_engine is None:
        _simulation_engine = SimulationEngine()
    return _simulation_engine

def set_simulation_engine(engine: SimulationEngine):
    """Set the global simulation engine"""
    global _simulation_engine
    _simulation_engine = engine
