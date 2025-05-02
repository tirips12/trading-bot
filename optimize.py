import itertools
import yaml
import copy
import pandas as pd
import numpy as np
from bot.strategies.scalping import ScalpingStrategy
from bot.backtest import BacktestEngine

PARAM_GRID = {
    'ema_fast': [7, 9, 12],
    'ema_slow': [20, 26, 30],
    'min_atr': [1.0, 1.5, 2.0],
    'sl_atr_mult': [1.0, 1.2, 1.5],
    'tp_atr_mult': [1.5, 2.0, 2.5],
    'rsi_buy': [50, 55, 60],
    'rsi_sell': [40, 45, 50],
    'order_size': [0.02, 0.05]
}

def run_grid_search(config_path, data_path):
    with open(config_path, 'r') as f:
        base_config = yaml.safe_load(f)
    keys, values = zip(*PARAM_GRID.items())
    results = []
    for param_set in itertools.product(*values):
        config = copy.deepcopy(base_config)
        # Set params
        config['strategy']['ema_fast'] = param_set[0]
        config['strategy']['ema_slow'] = param_set[1]
        config['strategy']['min_atr'] = param_set[2]
        config['strategy']['sl_atr_mult'] = param_set[3]
        config['strategy']['tp_atr_mult'] = param_set[4]
        config['strategy']['rsi_buy'] = param_set[5]
        config['strategy']['rsi_sell'] = param_set[6]
        config['trading']['order_size'] = param_set[7]
        strategy = ScalpingStrategy(config)
        bt = BacktestEngine(strategy, data_path, config)
        bt.run()
        trades = bt.trades
        final_balance = bt.balance
        win_rate = sum(1 for t in trades if t['pnl'] > 0) / len(trades) if trades else 0
        returns = [t['pnl']/config['backtest']['initial_balance'] for t in trades]
        sharpe = np.mean(returns)/(np.std(returns)+1e-9)*(252**0.5) if len(returns) > 1 else 0
        results.append({
            'ema_fast': param_set[0],
            'ema_slow': param_set[1],
            'min_atr': param_set[2],
            'sl_atr_mult': param_set[3],
            'tp_atr_mult': param_set[4],
            'rsi_buy': param_set[5],
            'rsi_sell': param_set[6],
            'order_size': param_set[7],
            'final_balance': final_balance,
            'win_rate': win_rate,
            'sharpe': sharpe,
            'num_trades': len(trades)
        })
        print(f"Tested: {param_set} | Final: {final_balance:.2f} | Sharpe: {sharpe:.2f} | WinRate: {win_rate:.2f}")
    pd.DataFrame(results).to_csv('grid_search_results.csv', index=False)
    print("Grid search complete. Results saved to grid_search_results.csv.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='config/config.yaml')
    parser.add_argument('--data', type=str, required=True)
    args = parser.parse_args()
    run_grid_search(args.config, args.data)
