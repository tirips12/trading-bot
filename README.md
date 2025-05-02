# Crypto Trading Bot (Binance Futures)

A modular, risk-controlled crypto trading bot for Binance Futures. Features:
- Multiple strategies: trend following, mean reversion, arbitrage, scalping
- High leverage (20x), automatic stop loss/take profit
- Backtesting & live trading support
- CLI interface (web dashboard coming soon)

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Configure your API keys and settings in `config/config.yaml` and `.env`
3. Run the CLI: `python cli/main.py`

## Structure
- `bot/` - Core trading logic and strategies
- `cli/` - Command-line interface
- `dashboard/` - (coming soon) Web dashboard
- `config/` - Config files

## Notes
- Start with testnet keys for safety
- For questions or improvements, open an issue or PR
