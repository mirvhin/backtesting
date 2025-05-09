import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def fetch_historical_data(ticker="GC=F", start_date="2020-01-01", end_date="2023-01-01"):
    """
    Fetch historical data for the given ticker using Yahoo Finance.
    """
    data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False)
    data.reset_index(inplace=True)
    return data

def apply_strategy(data, short_window=9, long_window=21):
    """
    Apply a moving average crossover strategy.
    """
    data['SMA_short'] = data['Close'].rolling(window=short_window).mean()
    data['SMA_long'] = data['Close'].rolling(window=long_window).mean()
    data['Signal'] = 0
    data.loc[data['SMA_short'] > data['SMA_long'], 'Signal'] = 1  # Buy signal
    data.loc[data['SMA_short'] <= data['SMA_long'], 'Signal'] = -1  # Sell signal
    return data

def backtest(data, initial_balance=10000):
    """
    Backtest the strategy and calculate the final balance.
    """
    balance = initial_balance
    position = 0  # Number of shares held

    for i in range(1, len(data)):
        # Debugging: Print current balance and position
        print(f"Day {i}: Balance = {balance}, Position = {position}, Close = {data['Close'].iloc[i]}")

        # Ensure `data['Signal'].iloc[i]` is treated as a scalar
        signal = data['Signal'].iloc[i]

        if signal == 1 and position == 0:  # Buy signal
            position = balance / data['Close'].iloc[i].item()  # Ensure scalar value
            balance = 0
            print(f"  Buy: Bought at {data['Close'].iloc[i].item()}, Position = {position}")
        elif signal == -1 and position > 0:  # Sell signal
            balance = position * data['Close'].iloc[i].item()  # Ensure scalar value
            position = 0
            print(f"  Sell: Sold at {data['Close'].iloc[i].item()}, Balance = {balance}")

    # Final balance includes the value of any open position
    final_balance = balance + (position * data['Close'].iloc[-1].item())  # Ensure scalar value
    print(f"Final Balance: {final_balance}")
    return final_balance

def plot_results(data):
    """
    Plot the price, moving averages, and buy/sell signals.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(data['Date'], data['Close'], label='Close Price', alpha=0.5)
    plt.plot(data['Date'], data['SMA_short'], label='Short SMA', alpha=0.75)
    plt.plot(data['Date'], data['SMA_long'], label='Long SMA', alpha=0.75)

    # Plot buy and sell signals
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
    data = fetch_historical_data("GC=F", "2020-01-01", "2023-01-01")
    data = apply_strategy(data)
    evaluate_performance(data)
    plot_results(data)