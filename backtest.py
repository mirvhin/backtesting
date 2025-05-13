import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def fetch_historical_data(ticker="GC=F", start_date="2022-01-01", end_date="2022-12-31"):
    """
    Fetch historical data for the given ticker using Yahoo Finance.
    """
    data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False)
    data.reset_index(inplace=True)
    # Convert Date to Asia/Manila (GMT+8)
    data['Date'] = pd.to_datetime(data['Date'])
    if data['Date'].dt.tz is None:
        # Localize to US/Eastern if not already tz-aware, then convert
        data['Date'] = data['Date'].dt.tz_localize('US/Eastern').dt.tz_convert('Asia/Manila')
    else:
        # If already tz-aware, just convert
        data['Date'] = data['Date'].dt.tz_convert('Asia/Manila')
    # Flatten multi-index columns if present
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [col[0] for col in data.columns]
    return data

def apply_strategy(data):
    """
    Apply breakout strategy based on daily close above previous high or below previous low.
    """
    required_cols = {'High', 'Low', 'Close'}
    if not required_cols.issubset(data.columns):
        raise ValueError(f"Data must contain columns: {required_cols}")

    data['Prev_High'] = data['High'].shift(1)
    data['Prev_Low'] = data['Low'].shift(1)
    data = data.dropna(subset=['Prev_High', 'Prev_Low'])
    data['Signal'] = 0  # 1 for long, -1 for short, 0 for no trade

    data.loc[data['Close'] > data['Prev_High'], 'Signal'] = 1
    data.loc[data['Close'] < data['Prev_Low'], 'Signal'] = -1

    return data

def backtest(data, initial_balance=10000):
    """
    Backtest the breakout strategy with 1:1 risk/reward and stop loss at previous high/low.
    Allows multiple simultaneous trades.
    """
    balance = initial_balance
    open_trades = []
    closed_trades = []

    for i in range(1, len(data)):
        signal = data['Signal'].iloc[i]
        date = data['Date'].iloc[i]
        close = data['Close'].iloc[i]
        prev_low = data['Prev_Low'].iloc[i]
        prev_high = data['Prev_High'].iloc[i]

        # Open new trades on signals
        if signal == 1:
            entry_price = close
            stop_loss = prev_low
            risk = entry_price - stop_loss
            take_profit = entry_price + risk
            open_trades.append({
                'direction': 1,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'entry_date': date
            })
            print(
                f"Day {i} ({date}): Long Entry at {entry_price}, Close: {close}, Prev High: {prev_high}, Prev Low: {prev_low}, SL {stop_loss}, TP {take_profit}"
            )
        elif signal == -1:
            entry_price = close
            stop_loss = prev_high
            risk = stop_loss - entry_price
            take_profit = entry_price - risk
            open_trades.append({
                'direction': -1,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'entry_date': date
            })
            print(
                f"Day {i} ({date}): Short Entry at {entry_price}, Close: {close}, Prev High: {prev_high}, Prev Low: {prev_low}, SL {stop_loss}, TP {take_profit}"
            )

        # Check all open trades for exit
        high = data['High'].iloc[i]
        low = data['Low'].iloc[i]
        closed_indices = []
        for idx, trade in enumerate(open_trades):
            if trade['direction'] == 1:
                # Long: check SL or TP
                if low <= trade['stop_loss']:
                    balance += (trade['stop_loss'] - trade['entry_price'])
                    print(f"Day {i} ({date}): Long Stopped Out at {trade['stop_loss']}, Balance: {balance}")
                    closed_trades.append({**trade, 'exit_date': date, 'exit_price': trade['stop_loss'], 'result': trade['stop_loss'] - trade['entry_price']})
                    closed_indices.append(idx)
                elif high >= trade['take_profit']:
                    balance += (trade['take_profit'] - trade['entry_price'])
                    print(f"Day {i} ({date}): Long Take Profit at {trade['take_profit']}, Balance: {balance}")
                    closed_trades.append({**trade, 'exit_date': date, 'exit_price': trade['take_profit'], 'result': trade['take_profit'] - trade['entry_price']})
                    closed_indices.append(idx)
            elif trade['direction'] == -1:
                # Short: check SL or TP
                if high >= trade['stop_loss']:
                    balance += (trade['entry_price'] - trade['stop_loss'])
                    print(f"Day {i} ({date}): Short Stopped Out at {trade['stop_loss']}, Balance: {balance}")
                    closed_trades.append({**trade, 'exit_date': date, 'exit_price': trade['stop_loss'], 'result': trade['entry_price'] - trade['stop_loss']})
                    closed_indices.append(idx)
                elif low <= trade['take_profit']:
                    balance += (trade['entry_price'] - trade['take_profit'])
                    print(f"Day {i} ({date}): Short Take Profit at {trade['take_profit']}, Balance: {balance}")
                    closed_trades.append({**trade, 'exit_date': date, 'exit_price': trade['take_profit'], 'result': trade['entry_price'] - trade['take_profit']})
                    closed_indices.append(idx)
        # Remove closed trades (from last to first to avoid index shift)
        for idx in sorted(closed_indices, reverse=True):
            del open_trades[idx]

    print(f"Final Balance: {balance}")
    return balance

def plot_results(data):
    """
    Plot the price and buy/sell signals.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(data['Date'], data['Close'], label='Close Price', alpha=0.7)
    buy_signals = data[data['Signal'] == 1]
    sell_signals = data[data['Signal'] == -1]
    plt.scatter(buy_signals['Date'], buy_signals['Close'], label='Buy Signal', marker='^', color='green')
    plt.scatter(sell_signals['Date'], sell_signals['Close'], label='Sell Signal', marker='v', color='red')
    plt.title('Backtesting Results')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.show()

def evaluate_performance(data, initial_balance=10000):
    """
    Evaluate the performance of the strategy.
    """
    final_balance = backtest(data, initial_balance)
    total_return = (final_balance - initial_balance) / initial_balance * 100
    print(f"Final Balance: ${final_balance:.2f}")
    print(f"Total Return: {total_return:.2f}%")

if __name__ == "__main__":
    data = fetch_historical_data("GC=F", "2022-01-01", "2022-12-31")
    data = apply_strategy(data)
    evaluate_performance(data)
    plot_results(data)