import pandas as pd
from .base import BaseStrategy

class ScalpingStrategy(BaseStrategy):
    """
    Configurable EMA scalping with slippage, ATR, and time filter.
    """
    def __init__(self, config):
        super().__init__(config)
        self.ema_fast = config.get('strategy', {}).get('ema_fast', 5)
        self.ema_slow = config.get('strategy', {}).get('ema_slow', 20)
        self.min_atr = config.get('strategy', {}).get('min_atr', 0)
        self.start_hour = config.get('strategy', {}).get('trade_start_hour', 0)
        self.end_hour = config.get('strategy', {}).get('trade_end_hour', 24)
        self.slippage = config.get('trading', {}).get('slippage', 0.0)

    def generate_signal(self, row):
        # ATR filter
        if 'atr' in row and row['atr'] < self.min_atr:
            return None
        # Volume spike filter
        if 'volume' in row and 'volume_ma' in row:
            if row['volume'] < 1.2 * row['volume_ma']:
                return None
        # Time filter
        if 'timestamp' in row:
            import datetime
            ts = row['timestamp']
            if ts > 1e10:
                ts = ts / 1000
            hour = datetime.datetime.utcfromtimestamp(ts).hour
            if hour < self.start_hour or hour >= self.end_hour:
                return None
        # Configurable thresholds
        rsi_buy = getattr(self, 'rsi_buy', self.config.get('strategy', {}).get('rsi_buy', 55))
        rsi_sell = getattr(self, 'rsi_sell', self.config.get('strategy', {}).get('rsi_sell', 45))
        use_vwap = getattr(self, 'use_vwap_confluence', self.config.get('strategy', {}).get('use_vwap_confluence', True))

        # EMA + RSI + VWAP confluence
        if row['ema_fast'] > row['ema_slow'] and row['prev_ema_fast'] <= row['prev_ema_slow']:
            if 'rsi' in row and row['rsi'] > rsi_buy:
                if use_vwap and 'vwap' in row and row['close'] < row['vwap']:
                    return None
                return 'BUY'
        elif row['ema_fast'] < row['ema_slow'] and row['prev_ema_fast'] >= row['prev_ema_slow']:
            if 'rsi' in row and row['rsi'] < rsi_sell:
                if use_vwap and 'vwap' in row and row['close'] > row['vwap']:
                    return None
                return 'SELL'
        return None

    def execute_trade(self, signal, row, balance, df=None, idx=None):
        """
        Realistic trade simulation: after entry, scan future candles for SL/TP hit, exit at first hit, deduct trading fee from PnL.
        Applies slippage to entry and exit.
        """
        entry_price = row['close']
        slippage = self.slippage
        if signal == 'BUY':
            entry_price *= (1 + slippage)
        else:
            entry_price *= (1 - slippage)
        qty = balance * self.config['trading']['order_size'] / entry_price
        fee_rate = self.config['trading'].get('fee', 0.0004)
        leverage = self.config['trading']['leverage']
        # Use ATR for dynamic SL/TP
        atr = row.get('atr', 0)
        sl_atr_mult = 1.2
        tp_atr_mult = 2.0
        if signal == 'BUY':
            stop_loss = entry_price - sl_atr_mult * atr
            take_profit = entry_price + tp_atr_mult * atr
            direction = 1
        else:
            stop_loss = entry_price + sl_atr_mult * atr
            take_profit = entry_price - tp_atr_mult * atr
            direction = -1
        exit_price = entry_price
        exit_idx = idx
        reason = 'hold'
        # Scan future candles for SL/TP hit
        if df is not None and idx is not None:
            for i in range(idx+1, len(df)):
                high = df.loc[i, 'high']
                low = df.loc[i, 'low']
                # Apply slippage to exit
                if direction == 1:
                    if high >= take_profit:
                        exit_price = take_profit * (1 - slippage)
                        exit_idx = i
                        reason = 'tp'
                        break
                    if low <= stop_loss:
                        exit_price = stop_loss * (1 + slippage)
                        exit_idx = i
                        reason = 'sl'
                        break
                else:
                    if low <= take_profit:
                        exit_price = take_profit * (1 + slippage)
                        exit_idx = i
                        reason = 'tp'
                        break
                    if high >= stop_loss:
                        exit_price = stop_loss * (1 - slippage)
                        exit_idx = i
                        reason = 'sl'
                        break
            else:
                exit_price = df.iloc[-1]['close']
                # Apply slippage to market exit
                if direction == 1:
                    exit_price *= (1 - slippage)
                else:
                    exit_price *= (1 + slippage)
                exit_idx = len(df)-1
                reason = 'timeout'
        else:
            exit_price = take_profit
            reason = 'tp'
        gross_pnl = (exit_price - entry_price) * qty * direction * leverage
        fee = (entry_price + exit_price) * qty * fee_rate * leverage
        net_pnl = gross_pnl - fee
        return {
            'signal': signal,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'qty': qty,
            'pnl': net_pnl,
            'raw_pnl': gross_pnl,
            'fee': fee,
            'exit_idx': exit_idx,
            'reason': reason
        }
