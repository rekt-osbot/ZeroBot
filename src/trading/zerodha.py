"""
Zerodha KiteConnect API integration module
"""
import logging
import pandas as pd
import random
import datetime
import numpy as np
from kiteconnect import KiteConnect
from src.utils.config import config
from src.data.providers import get_data_provider
from src.simulation.engine import get_simulation_engine

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

        # Initialize data provider and simulation engine for demo mode
        if self.demo_mode:
            self.data_provider = get_data_provider(simulation_mode=True)
            self.simulation_engine = get_simulation_engine()
    
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
            # Use real data provider for instruments
            return self.data_provider.get_instruments(exchange)
        
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
            # Convert instrument_token to symbol (simplified mapping)
            symbol_map = {
                100000: "RELIANCE", 100001: "TCS", 100002: "INFY", 100003: "HDFCBANK",
                100004: "ICICIBANK", 100005: "SBIN", 100006: "BHARTIARTL",
                100007: "ITC", 100008: "HINDUNILVR", 100009: "KOTAKBANK"
            }

            symbol = symbol_map.get(instrument_token, "RELIANCE")

            # Use real data provider
            return self.data_provider.get_historical_data(
                symbol=symbol,
                start_date=from_date.strftime("%Y-%m-%d") if isinstance(from_date, datetime.datetime) else from_date,
                end_date=to_date.strftime("%Y-%m-%d") if isinstance(to_date, datetime.datetime) else to_date,
                interval="1d"  # Simplify to daily data for now
            )
        
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
            # Use simulation engine to place order
            return self.simulation_engine.place_order(
                symbol=symbol,
                exchange=exchange,
                transaction_type=transaction_type,
                quantity=quantity,
                price=price,
                order_type=order_type
            )
        
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
            # Use simulation engine to get positions
            return self.simulation_engine.get_positions()
        
        try:
            positions = self.kite.positions()
            return {
                "net": pd.DataFrame(positions["net"]),
                "day": pd.DataFrame(positions["day"])
            }
        except Exception as e:
            logger.error(f"Failed to get positions: {str(e)}")
            return {"net": pd.DataFrame(), "day": pd.DataFrame()}
