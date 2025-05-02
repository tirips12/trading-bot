class RiskControl:
    def __init__(self, stop_loss_pct, take_profit_pct):
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct

    def get_stop_loss(self, entry_price):
        return entry_price * (1 - self.stop_loss_pct / 100)

    def get_take_profit(self, entry_price):
        return entry_price * (1 + self.take_profit_pct / 100)
