# ZeroBot - Automated Trading Bot for Zerodha

ZeroBot is an automated intraday trading application that uses Zerodha's KiteConnect API to execute trades on NSE and BSE markets. The bot intelligently splits your capital across multiple trades to diversify risk and maximize potential returns.

## Features

- **Automated Trading**: Set up once and let the bot trade for you
- **Smart Capital Allocation**: Splits your capital across multiple trades
- **Real-time Analytics**: Track performance with beautiful, reactive dashboards
- **Risk Management**: Built-in stop-loss and target mechanisms
- **Strategy Customization**: Choose from multiple trading strategies or create your own
- **Secure Authentication**: Direct integration with Zerodha's KiteConnect API

## Installation

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure your Zerodha API credentials in the `.env` file
4. Run the application: `python app.py`

## Configuration

Before using the bot, you need to:

1. Create a Zerodha Kite developer account
2. Generate API keys from the Zerodha developer console
3. Add these credentials to the `.env` file

## Disclaimer

Trading in financial markets involves risk. This bot is provided for educational and informational purposes only. Always use proper risk management and never invest money you cannot afford to lose.

## License

MIT
