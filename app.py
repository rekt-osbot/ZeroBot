"""
ZeroBot - Automated Trading Bot for Zerodha
Main application entry point
"""
import os
import logging
from dotenv import load_dotenv
from flask import Flask
from src.dashboard import create_dashboard
from src.trading.bot import TradeBot
from src.utils.logger import setup_logger

# Load environment variables
load_dotenv()

# Setup logging
setup_logger()
logger = logging.getLogger(__name__)

def main():
    """Main application entry point"""
    logger.info("Starting ZeroBot Trading Application")
    
    # Initialize the trading bot
    trade_bot = TradeBot()
    
    # Create the dashboard app
    app = create_dashboard(trade_bot)
    
    # Run the server
    app.run(debug=os.getenv("DEBUG", "False").lower() == "true", 
           host="0.0.0.0", 
           port=8000)

if __name__ == "__main__":
    main()
