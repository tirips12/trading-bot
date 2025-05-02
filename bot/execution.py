from bot.risk.risk_control import RiskControl

class TradeExecutor:
    def __init__(self, api, config):
        self.api = api
        self.config = config
        self.risk = RiskControl(
            stop_loss_pct=config['trading']['stop_loss_pct'],
            take_profit_pct=config['trading']['take_profit_pct']
        )
        self.leverage = config['trading']['leverage']

    def open_position(self, symbol, side, quantity, entry_price):
        # Set leverage
        self.api.set_leverage(symbol, self.leverage)
        # Place order
        order = self.api.place_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type='MARKET'
        )
        # Calculate SL/TP
        stop_loss = self.risk.get_stop_loss(entry_price)
        take_profit = self.risk.get_take_profit(entry_price)
        # Place stop loss and take profit orders
        # (Pseudo-code, should use Binance OCO or separate orders)
        # self.api.place_order(symbol, 'SELL' if side == 'BUY' else 'BUY', quantity, 'STOP_MARKET', stopPrice=stop_loss)
        # self.api.place_order(symbol, 'SELL' if side == 'BUY' else 'BUY', quantity, 'TAKE_PROFIT_MARKET', stopPrice=take_profit)
        return order, stop_loss, take_profit
