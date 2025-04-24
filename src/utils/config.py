"""
Configuration utilities for the ZeroBot application
"""
import os
from dotenv import load_dotenv

class Config:
    """Configuration class for the ZeroBot application"""
    
    def __init__(self):
        """Initialize configuration from environment variables"""
        load_dotenv()
        
        # API credentials
        self.api_key = os.getenv("API_KEY")
        self.api_secret = os.getenv("API_SECRET")
        self.redirect_url = os.getenv("REDIRECT_URL", "http://localhost:8000/login/callback")
        
        # Trading parameters
        self.capital = float(os.getenv("CAPITAL", "5000"))
        self.min_trades = int(os.getenv("MIN_TRADES", "3"))
        self.max_trades = int(os.getenv("MAX_TRADES", "5"))
        self.risk_per_trade = float(os.getenv("RISK_PER_TRADE", "2"))
        self.stop_loss_percent = float(os.getenv("STOP_LOSS_PERCENT", "1.5"))
        self.target_percent = float(os.getenv("TARGET_PERCENT", "3.0"))
        
        # Application settings
        self.debug = os.getenv("DEBUG", "False").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
    
    def validate(self):
        """Validate the configuration"""
        if not self.api_key or not self.api_secret:
            raise ValueError("API_KEY and API_SECRET must be set in .env file")
        
        if self.capital <= 0:
            raise ValueError("CAPITAL must be greater than 0")
        
        if self.min_trades <= 0 or self.max_trades <= 0:
            raise ValueError("MIN_TRADES and MAX_TRADES must be greater than 0")
        
        if self.min_trades > self.max_trades:
            raise ValueError("MIN_TRADES cannot be greater than MAX_TRADES")
        
        if self.risk_per_trade <= 0:
            raise ValueError("RISK_PER_TRADE must be greater than 0")
        
        if self.stop_loss_percent <= 0 or self.target_percent <= 0:
            raise ValueError("STOP_LOSS_PERCENT and TARGET_PERCENT must be greater than 0")
        
        return True

config = Config()
