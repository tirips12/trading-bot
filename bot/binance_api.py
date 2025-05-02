import os
import yaml
from binance.client import Client
from dotenv import load_dotenv

class BinanceAPI:
    def __init__(self, config_path="config/config.yaml"):
        load_dotenv()
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        self.use_testnet = config["binance"].get("use_testnet", True)
        self.api_key = os.getenv("BINANCE_API_KEY", config["binance"]["api_key"])
        self.api_secret = os.getenv("BINANCE_API_SECRET", config["binance"]["api_secret"])
        self.client = self._init_client()

    def _init_client(self):
        client = Client(self.api_key, self.api_secret)
        if self.use_testnet:
            client.FUTURES_URL = 'https://testnet.binancefuture.com/fapi'
        return client

    def get_balance(self):
        return self.client.futures_account_balance()

    def get_positions(self):
        return self.client.futures_position_information()

    def place_order(self, symbol, side, quantity, order_type, **kwargs):
        return self.client.futures_create_order(
            symbol=symbol,
            side=side,
            type=order_type,
            quantity=quantity,
            **kwargs
        )

    def set_leverage(self, symbol, leverage):
        return self.client.futures_change_leverage(symbol=symbol, leverage=leverage)
