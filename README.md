# Backtesting Environment

This project provides a framework for backtesting trading strategies. It fetches historical data, applies a user-defined strategy, evaluates its performance, and visualizes the results.

## Features

- Fetch historical data using Yahoo Finance.
- Apply custom trading strategies.
- Backtest the strategy to calculate final balance and returns.
- Visualize the results with buy/sell signals.

## Requirements

- Python 3.7 or higher
- Required libraries:
  - `yfinance`
  - `pandas`
  - `matplotlib`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mirvhin/backtesting.git
   cd backtesting-env
   ```

2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Mac/Linux
   venv\Scripts\activate     # On Windows
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the script:
   ```bash
   python backtest.py
   ```

2. The script will:
   - Fetch historical data for the specified ticker (default: gold futures `GC=F`).
   - Apply the user-defined trading strategy.
   - Evaluate the strategy's performance.
   - Plot the results with buy/sell signals.

## Configuration

- **Ticker Symbol**: Change the `ticker` parameter in the `fetch_historical_data` function to backtest a different asset.
- **Date Range**: Modify the `start_date` and `end_date` parameters in the `fetch_historical_data` function.
- **Strategy Logic**: Customize the `apply_strategy` function to implement your own trading strategy.

## Example Output

- **Console**: Displays daily transactions, final balance, and total return.
- **Plot**: Shows the price chart with buy/sell signals.

## File Structure

```
backtesting-env/
├── backtest.py         # Main script for backtesting
├── .gitignore          # Git ignore file
├── README.md           # Project documentation
├── requirements.txt    # List of dependencies
└── venv/               # Virtual environment (ignored by Git)
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments

- [Yahoo Finance](https://finance.yahoo.com/) for providing historical data.
- [Matplotlib](https://matplotlib.org/) and [Pandas](https://pandas.pydata.org/) for data visualization and manipulation.