"""
Zerodha KiteConnect API integration module
"""
import logging
import pandas as pd
import random
import datetime
from kiteconnect import KiteConnect
from src.utils.config import config

logger = logging.getLogger(__name__)

class ZerodhaConnector:
    """Connector class for Zerodha KiteConnect API"""
    
    def __init__(self):
        """Initialize the Zerodha connector"""
        self.api_key = config.api_key
        self.api_secret = config.api_secret
        self.redirect_url = config.redirect_url
        self.demo_mode = not self.api_key or self.api_key == "your_api_key_here"
        
        if not self.demo_mode:
            self.kite = KiteConnect(api_key=self.api_key)
        else:
            self.kite = None
            logger.info("Running in demo mode (no API key provided)")
            
        self.access_token = None
        self.authenticated = self.demo_mode  # Auto-authenticate in demo mode
    
    def get_login_url(self):
        """Get the login URL for Zerodha authentication"""
        if self.demo_mode:
            # In demo mode, return a dummy callback URL that will trigger our demo login
            return f"/login/demo-callback"
        return self.kite.login_url()
    
    def generate_session(self, request_token):
        """Generate a session using the request token"""
        if self.demo_mode:
            # In demo mode, just set authenticated to True
            self.authenticated = True
            logger.info("Demo mode: Successfully authenticated with Zerodha")
            return True
            
        try:
            data = self.kite.generate_session(
                request_token=request_token,
                api_secret=self.api_secret
            )
            self.access_token = data["access_token"]
            self.kite.set_access_token(self.access_token)
            self.authenticated = True
            logger.info("Successfully authenticated with Zerodha")
            return True
        except Exception as e:
            logger.error(f"Failed to authenticate with Zerodha: {str(e)}")
            return False
    
    def get_profile(self):
        """Get user profile information"""
        if not self.authenticated:
            logger.error("Not authenticated with Zerodha")
            return None
        
        if self.demo_mode:
            # Return demo profile data
            return {
                "user_id": "DM0001",
                "user_name": "Demo User",
                "email": "demo@example.com",
                "user_type": "individual",
                "broker": "ZERODHA",
                "exchanges": ["NSE", "BSE"],
                "products": ["CNC", "MIS", "NRML"],
                "order_types": ["MARKET", "LIMIT", "SL", "SL-M"],
                "avatar_url": None
            }
        
        try:
            return self.kite.profile()
        except Exception as e:
            logger.error(f"Failed to get profile: {str(e)}")
            return None
    
    def get_margins(self):
        """Get user margin information"""
        if not self.authenticated:
            logger.error("Not authenticated with Zerodha")
            return None
        
        if self.demo_mode:
            # Return demo margin data
            return {
                "equity": {
                    "enabled": True,
                    "net": 50000.0,
                    "available": {
                        "adhoc_margin": 0,
                        "cash": 50000.0,
                        "collateral": 0,
                        "intraday_payin": 0
                    },
                    "utilised": {
                        "debits": 0,
                        "exposure": 0,
                        "m2m_realised": 0,
                        "m2m_unrealised": 0,
                        "option_premium": 0,
                        "payout": 0,
                        "span": 0,
                        "holding_sales": 0,
                        "turnover": 0
                    }
                }
            }
        
        try:
            return self.kite.margins()
        except Exception as e:
            logger.error(f"Failed to get margins: {str(e)}")
            return None
    
    def get_instruments(self, exchange=None):
        """Get list of tradable instruments"""
        if self.demo_mode:
            # Return demo instruments
            instruments = []
            
            if exchange in [None, "NSE"]:
                # Add some NSE instruments
                nse_symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", 
                              "SBIN", "BHARTIARTL", "ITC", "HINDUNILVR", "KOTAKBANK"]
                for i, symbol in enumerate(nse_symbols):
                    instruments.append({
                        "instrument_token": 100000 + i,
                        "exchange_token": 10000 + i,
                        "tradingsymbol": symbol,
                        "name": f"{symbol} Demo",
                        "last_price": random.uniform(500, 3000),
                        "expiry": "",
                        "strike": 0,
                        "tick_size": 0.05,
                        "lot_size": 1,
                        "instrument_type": "EQ",
                        "segment": "NSE",
                        "exchange": "NSE"
                    })
            
            if exchange in [None, "BSE"]:
                # Add some BSE instruments
                bse_symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]
                for i, symbol in enumerate(bse_symbols):
                    instruments.append({
                        "instrument_token": 200000 + i,
                        "exchange_token": 20000 + i,
                        "tradingsymbol": symbol,
                        "name": f"{symbol} Demo",
                        "last_price": random.uniform(500, 3000),
                        "expiry": "",
                        "strike": 0,
                        "tick_size": 0.05,
                        "lot_size": 1,
                        "instrument_type": "EQ",
                        "segment": "BSE",
                        "exchange": "BSE"
                    })
            
            return pd.DataFrame(instruments)
        
        try:
            instruments = self.kite.instruments(exchange=exchange)
            return pd.DataFrame(instruments)
        except Exception as e:
            logger.error(f"Failed to get instruments: {str(e)}")
            return pd.DataFrame()
    
    def get_historical_data(self, instrument_token, from_date, to_date, interval, continuous=False):
        """Get historical data for an instrument"""
        if not self.authenticated:
            logger.error("Not authenticated with Zerodha")
            return pd.DataFrame()
        
        if self.demo_mode:
            # Generate demo historical data
            start_date = from_date
            end_date = to_date
            
            if isinstance(start_date, str):
                start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            if isinstance(end_date, str):
                end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            
            # Determine time delta based on interval
            if interval == "minute":
                delta = datetime.timedelta(minutes=1)
            elif interval == "3minute":
                delta = datetime.timedelta(minutes=3)
            elif interval == "5minute":
                delta = datetime.timedelta(minutes=5)
            elif interval == "10minute":
                delta = datetime.timedelta(minutes=10)
            elif interval == "15minute":
                delta = datetime.timedelta(minutes=15)
            elif interval == "30minute":
                delta = datetime.timedelta(minutes=30)
            elif interval == "60minute":
                delta = datetime.timedelta(hours=1)
            else:  # day
                delta = datetime.timedelta(days=1)
            
            # Generate dates
            dates = []
            current_date = start_date
            while current_date <= end_date:
                # Only include weekdays and trading hours
                if current_date.weekday() < 5:  # Monday to Friday
                    if interval == "day" or (9 <= current_date.hour < 16):
                        dates.append(current_date)
                current_date += delta
            
            # Generate random price data
            base_price = 1000.0
            price_data = []
            
            for i, date in enumerate(dates):
                # Create a random walk
                if i == 0:
                    open_price = base_price
                else:
                    open_price = price_data[-1]["close"]
                
                # Random price movements
                price_change = random.uniform(-20, 20)
                close_price = max(0.1, open_price + price_change)
                high_price = max(open_price, close_price) + random.uniform(0, 10)
                low_price = min(open_price, close_price) - random.uniform(0, 10)
                
                # Ensure low <= open, close <= high
                low_price = max(0.1, min(low_price, open_price, close_price))
                high_price = max(high_price, open_price, close_price)
                
                # Volume
                volume = int(random.uniform(10000, 1000000))
                
                price_data.append({
                    "date": date,
                    "open": open_price,
                    "high": high_price,
                    "low": low_price,
                    "close": close_price,
                    "volume": volume
                })
            
            return pd.DataFrame(price_data)
        
        try:
            data = self.kite.historical_data(
                instrument_token=instrument_token,
                from_date=from_date,
                to_date=to_date,
                interval=interval,
                continuous=continuous
            )
            return pd.DataFrame(data)
        except Exception as e:
            logger.error(f"Failed to get historical data: {str(e)}")
            return pd.DataFrame()
    
    def place_order(self, exchange, symbol, transaction_type, quantity, price=None, product="MIS", order_type="MARKET"):
        """Place an order on Zerodha"""
        if not self.authenticated:
            logger.error("Not authenticated with Zerodha")
            return None
        
        if self.demo_mode:
            # Generate a random order ID
            order_id = f"demo_{random.randint(100000, 999999)}"
            logger.info(f"Demo mode: Placed order {order_id} for {symbol} on {exchange}")
            return order_id
        
        try:
            order_params = {
                "exchange": exchange,
                "tradingsymbol": symbol,
                "transaction_type": transaction_type,
                "quantity": quantity,
                "product": product,
                "order_type": order_type
            }
            
            if price and order_type != "MARKET":
                order_params["price"] = price
            
            order_id = self.kite.place_order(variety="regular", **order_params)
            logger.info(f"Placed order {order_id} for {symbol} on {exchange}")
            return order_id
        except Exception as e:
            logger.error(f"Failed to place order: {str(e)}")
            return None
    
    def modify_order(self, order_id, price=None, quantity=None, order_type=None, trigger_price=None):
        """Modify an existing order"""
        if not self.authenticated:
            logger.error("Not authenticated with Zerodha")
            return False
        
        if self.demo_mode:
            logger.info(f"Demo mode: Modified order {order_id}")
            return True
        
        try:
            params = {}
            if price:
                params["price"] = price
            if quantity:
                params["quantity"] = quantity
            if order_type:
                params["order_type"] = order_type
            if trigger_price:
                params["trigger_price"] = trigger_price
            
            self.kite.modify_order(variety="regular", order_id=order_id, **params)
            logger.info(f"Modified order {order_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to modify order: {str(e)}")
            return False
    
    def cancel_order(self, order_id):
        """Cancel an order"""
        if not self.authenticated:
            logger.error("Not authenticated with Zerodha")
            return False
        
        if self.demo_mode:
            logger.info(f"Demo mode: Cancelled order {order_id}")
            return True
        
        try:
            self.kite.cancel_order(variety="regular", order_id=order_id)
            logger.info(f"Cancelled order {order_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel order: {str(e)}")
            return False
    
    def get_order_history(self, order_id=None):
        """Get order history"""
        if not self.authenticated:
            logger.error("Not authenticated with Zerodha")
            return pd.DataFrame()
        
        if self.demo_mode:
            # Generate demo order history
            orders = []
            
            # If a specific order ID is requested
            if order_id:
                orders.append({
                    "order_id": order_id,
                    "exchange_order_id": f"X{order_id[5:]}",
                    "parent_order_id": None,
                    "status": "COMPLETE",
                    "exchange": "NSE",
                    "tradingsymbol": "RELIANCE",
                    "order_type": "MARKET",
                    "transaction_type": "BUY",
                    "quantity": 10,
                    "price": 2500,
                    "average_price": 2500,
                    "product": "MIS",
                    "placement_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "trigger_price": 0,
                    "exchange_timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            else:
                # Generate a few random orders
                symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]
                for i in range(5):
                    symbol = random.choice(symbols)
                    quantity = random.randint(1, 20)
                    price = random.uniform(500, 3000)
                    
                    orders.append({
                        "order_id": f"demo_{random.randint(100000, 999999)}",
                        "exchange_order_id": f"X{random.randint(100000, 999999)}",
                        "parent_order_id": None,
                        "status": random.choice(["COMPLETE", "REJECTED", "CANCELLED"]),
                        "exchange": random.choice(["NSE", "BSE"]),
                        "tradingsymbol": symbol,
                        "order_type": random.choice(["MARKET", "LIMIT"]),
                        "transaction_type": random.choice(["BUY", "SELL"]),
                        "quantity": quantity,
                        "price": price,
                        "average_price": price,
                        "product": "MIS",
                        "placement_date": (datetime.datetime.now() - datetime.timedelta(hours=random.randint(1, 24))).strftime("%Y-%m-%d %H:%M:%S"),
                        "trigger_price": 0,
                        "exchange_timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
            
            return pd.DataFrame(orders)
        
        try:
            if order_id:
                orders = self.kite.order_history(order_id=order_id)
            else:
                orders = self.kite.orders()
            return pd.DataFrame(orders)
        except Exception as e:
            logger.error(f"Failed to get order history: {str(e)}")
            return pd.DataFrame()
    
    def get_positions(self):
        """Get current positions"""
        if not self.authenticated:
            logger.error("Not authenticated with Zerodha")
            return {"net": pd.DataFrame(), "day": pd.DataFrame()}
        
        if self.demo_mode:
            # Generate demo positions
            positions = []
            
            # Generate a few random positions
            symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]
            for i in range(3):
                symbol = symbols[i]
                quantity = random.randint(1, 20)
                buy_price = random.uniform(500, 3000)
                current_price = buy_price * random.uniform(0.9, 1.1)
                
                positions.append({
                    "tradingsymbol": symbol,
                    "exchange": "NSE",
                    "instrument_token": 100000 + i,
                    "product": "MIS",
                    "quantity": quantity,
                    "overnight_quantity": 0,
                    "multiplier": 1,
                    "average_price": buy_price,
                    "close_price": 0,
                    "last_price": current_price,
                    "value": quantity * current_price,
                    "pnl": quantity * (current_price - buy_price),
                    "m2m": quantity * (current_price - buy_price),
                    "unrealised": quantity * (current_price - buy_price),
                    "realised": 0,
                    "buy_quantity": quantity,
                    "buy_price": buy_price,
                    "buy_value": quantity * buy_price,
                    "sell_quantity": 0,
                    "sell_price": 0,
                    "sell_value": 0
                })
            
            return {
                "net": pd.DataFrame(positions),
                "day": pd.DataFrame(positions)
            }
        
        try:
            positions = self.kite.positions()
            return {
                "net": pd.DataFrame(positions["net"]),
                "day": pd.DataFrame(positions["day"])
            }
        except Exception as e:
            logger.error(f"Failed to get positions: {str(e)}")
            return {"net": pd.DataFrame(), "day": pd.DataFrame()}
