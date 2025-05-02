import pandas as pd
import numpy as np

class BacktestEngine:
    def __init__(self, strategy, data_path, config):
        self.strategy = strategy
        self.data_path = data_path
        self.config = config
        self.initial_balance = config['backtest']['initial_balance']
        self.balance = self.initial_balance
        self.trades = []

    def load_data(self):
        df = pd.read_csv(self.data_path)
        # Expect columns: open, high, low, close, volume, timestamp
        # EMA periods from config
        ema_fast = self.config.get('strategy', {}).get('ema_fast', 5)
        ema_slow = self.config.get('strategy', {}).get('ema_slow', 20)
        df['ema_fast'] = df['close'].ewm(span=ema_fast, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=ema_slow, adjust=False).mean()
        df['prev_ema_fast'] = df['ema_fast'].shift(1)
        df['prev_ema_slow'] = df['ema_slow'].shift(1)
        # ATR calculation
        df['tr0'] = abs(df['high'] - df['low'])
        df['tr1'] = abs(df['high'] - df['close'].shift(1))
        df['tr2'] = abs(df['low'] - df['close'].shift(1))
        df['tr'] = df[['tr0', 'tr1', 'tr2']].max(axis=1)
        df['atr'] = df['tr'].rolling(window=14).mean()
        # Volume moving average for volume spike filter
        df['volume_ma'] = df['volume'].rolling(window=20).mean()
        # RSI calculation (14-period)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-9)
        df['rsi'] = 100 - (100 / (1 + rs))
        # VWAP calculation
        cum_vol = df['volume'].cumsum()
        cum_vol_price = (df['close'] * df['volume']).cumsum()
        df['vwap'] = cum_vol_price / cum_vol
        df = df.dropna().reset_index(drop=True)
        return df

    def run(self):
        df = self.load_data()
        for idx, row in df.iterrows():
            signal = self.strategy.generate_signal(row)
            if signal:
                trade = self.strategy.execute_trade(signal, row, self.balance, df, idx)
                self.trades.append(trade)
                self.balance += trade['pnl']
        return self.trades, self.balance

    def print_summary(self):
        print(f"Initial balance: {self.initial_balance}")
        print(f"Final balance: {self.balance:.2f}")
        print(f"Total trades: {len(self.trades)}")
        if self.trades:
            win_trades = [t for t in self.trades if t['pnl'] > 0]
            loss_trades = [t for t in self.trades if t['pnl'] <= 0]
            print(f"Winning trades: {len(win_trades)}")
            print(f"Losing trades: {len(loss_trades)}")
            print(f"Win rate: {len(win_trades) / len(self.trades) * 100:.1f}%")
            total_fee = sum(t['fee'] for t in self.trades)
            print(f"Total fees paid: {total_fee:.2f}")
            # Advanced metrics
            returns = [t['pnl']/self.initial_balance for t in self.trades]
            if len(returns) > 1:
                import numpy as np
                sharpe = np.mean(returns) / (np.std(returns) + 1e-9) * (252 ** 0.5)  # annualized
                # Equity curve
                equity = np.array([self.initial_balance] + [self.initial_balance + sum(t['pnl'] for t in self.trades[:i+1]) for i in range(len(self.trades))])
                drawdown = (equity - np.maximum.accumulate(equity))
                max_dd = drawdown.min()
                print(f"Sharpe ratio: {sharpe:.2f}")
                print(f"Max drawdown: {max_dd:.2f}")
                # Save equity curve
                import pandas as pd
                pd.DataFrame({'equity': equity}).to_csv('equity_curve.csv', index=False)
            # Save trade log
            pd.DataFrame(self.trades).to_csv('trade_log.csv', index=False)
            print("Sample trade outcomes:")
            for t in self.trades[:3]:
                print(f"  {t['signal']} entry {t['entry_price']:.2f} exit {t['exit_price']:.2f} pnl {t['pnl']:.2f} fee {t['fee']:.2f} reason {t['reason']}")
            print("Trade log saved to trade_log.csv. Equity curve saved to equity_curve.csv.")
        else:
            print("No trades executed.")
