import argparse
from bot.binance_api import BinanceAPI
import yaml
from bot.strategies.scalping import ScalpingStrategy
from bot.backtest import BacktestEngine
import os


def main():
    parser = argparse.ArgumentParser(description="Crypto Trading Bot CLI")
    parser.add_argument('--balance', action='store_true', help='Show futures account balance')
    parser.add_argument('--positions', action='store_true', help='Show open futures positions')
    parser.add_argument('--backtest', type=str, help='Run backtest on CSV file (provide path)')
    args = parser.parse_args()

    if args.balance or args.positions:
        api = BinanceAPI()
        if args.balance:
            balance = api.get_balance()
            print("Futures Balance:", balance)
        if args.positions:
            positions = api.get_positions()
            print("Open Positions:", positions)

    if args.backtest:
        # Load config
        config_path = os.path.join('config', 'config.yaml')
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        # Init strategy
        strategy = ScalpingStrategy(config)
        # Run backtest
        bt = BacktestEngine(strategy, args.backtest, config)
        bt.run()
        bt.print_summary()

if __name__ == "__main__":
    main()
