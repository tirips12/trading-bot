import csv
from binance.client import Client
from datetime import datetime
import os
import sys

# Read API keys from .env
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

if not API_KEY or not API_SECRET:
    print("Error: API key/secret not found in .env")
    sys.exit(1)

client = Client(API_KEY, API_SECRET)

def fetch_klines(symbol, interval, start_str, end_str=None, limit=1000):
    return client.get_historical_klines(symbol, interval, start_str, end_str, limit=limit)

def save_to_csv(klines, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['open', 'high', 'low', 'close', 'volume', 'timestamp'])
        for k in klines:
            # kline: [open_time, open, high, low, close, volume, close_time, ...]
            writer.writerow([
                k[1],  # open
                k[2],  # high
                k[3],  # low
                k[4],  # close
                k[5],  # volume
                k[0]   # timestamp (open_time)
            ])

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Fetch Binance klines and save to CSV.')
    parser.add_argument('--symbol', type=str, required=True, help='Symbol, e.g. BTCUSDT')
    parser.add_argument('--interval', type=str, default='1m', help='Kline interval, e.g. 1m, 5m, 1h, 1d')
    parser.add_argument('--start', type=str, required=True, help='Start date, e.g. 2024-01-01')
    parser.add_argument('--end', type=str, default=None, help='End date, e.g. 2024-01-31')
    parser.add_argument('--output', type=str, default='historical_data.csv', help='Output CSV file name')
    args = parser.parse_args()

    print(f"Fetching {args.symbol} klines from {args.start} to {args.end or 'now'} at {args.interval} interval...")
    klines = fetch_klines(args.symbol, args.interval, args.start, args.end)
    print(f"Fetched {len(klines)} rows. Saving to {args.output}...")
    save_to_csv(klines, args.output)
    print(f"Done. File saved: {args.output}")
