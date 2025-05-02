import pandas as pd
import matplotlib.pyplot as plt

def plot_equity_curve(csv_path='equity_curve.csv'):
    df = pd.read_csv(csv_path)
    plt.figure(figsize=(10, 5))
    plt.plot(df['equity'], label='Equity Curve')
    plt.xlabel('Trade #')
    plt.ylabel('Equity ($)')
    plt.title('Trading Bot Equity Curve')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', type=str, default='equity_curve.csv')
    args = parser.parse_args()
    plot_equity_curve(args.csv)
