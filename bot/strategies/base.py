class BaseStrategy:
    def __init__(self, config):
        self.config = config

    def generate_signal(self, row):
        raise NotImplementedError

    def execute_trade(self, signal, row, balance):
        raise NotImplementedError
