import yfinance as yf
import pandas as pd


def fetch_data(symbol='GBPUSD=X', period='1d', interval='5m'):
    forex = yf.Ticker(symbol)
    data = forex.history(period=period, interval=interval)
    if data.empty:
        print(f"Failed to fetch data for {symbol}.")
        return pd.DataFrame()
    return data


def calculate_macd(data, short_period=12, long_period=26, signal_period=9):
    data['EMA_short'] = data['Close'].ewm(span=short_period, adjust=False).mean()
    data['EMA_long'] = data['Close'].ewm(span=long_period, adjust=False).mean()
    data['MACD'] = data['EMA_short'] - data['EMA_long']
    data['Signal'] = data['MACD'].ewm(span=signal_period, adjust=False).mean()
    data['Histogram'] = data['MACD'] - data['Signal']
    print(data[['Close', 'EMA_short', 'EMA_long', 'MACD', 'Signal', 'Histogram']].tail())
    last_macd = data['MACD'].iloc[-1]
    last_signal = data['Signal'].iloc[-1]
    last_histogram = data['Histogram'].iloc[-1]
    print(f"\nLast MACD: {last_macd}, Signal: {last_signal}, Histogram: {last_histogram}\n")
    return data, last_macd, last_signal, last_histogram


def calculate_atr(data, period=14):
    data['H-L'] = data['High'] - data['Low']
    data['H-PC'] = abs(data['High'] - data['Close'].shift(1))
    data['L-PC'] = abs(data['Low'] - data['Close'].shift(1))
    data['TR'] = data[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    data['ATR'] = data['TR'].rolling(window=period).mean()
    return data['ATR'].iloc[-1]


def identify_trade_levels(data, last_macd, last_signal, last_histogram):
    last_close = data['Close'].iloc[-1]
    last_atr = calculate_atr(data)
    print(f"Last Close: {last_close}, MACD: {last_macd}, Signal: {last_signal}, ATR: {last_atr}\n")

    entry = last_close
    trade_type = "None"
    stop_loss = last_close
    target = last_close

    if last_atr < 0.00015:
        print("ATR too low for reliable trade signal.")
    elif (last_macd > last_signal and last_histogram > 0 and
          data['MACD'].iloc[-2] > data['Signal'].iloc[-2]):
        trade_type = "Buy"
        stop_loss = last_close - (last_atr * 5)
        target = last_close + (last_atr * 6)
        print("Bullish Trend Confirmed with 2-candle persistence")
    elif (last_macd < last_signal and last_histogram < 0 and
          data['MACD'].iloc[-2] < data['Signal'].iloc[-2]):
        trade_type = "Sell"
        stop_loss = last_close + (last_atr * 5)
        target = last_close - (last_atr * 6)
        print("Bearish Trend Confirmed with 2-candle persistence")
    else:
        stop_loss = last_close - (last_atr * 5)
        target = last_close + (last_atr * 6)

    return {'Entry': entry, 'Stop Loss': stop_loss, 'Target': target, 'Trade Type': trade_type, 'ATR': last_atr}


def execute_trade(symbol, trade_type, amount, stop_loss, target):
    if trade_type == "None":
        print("\nNo trade signal detected.\n")
    else:
        print(f"\nExecuting {trade_type} trade for {symbol}:")
        print(f"Amount: {amount}")
        print(f"Stop Loss: {stop_loss}")
        print(f"Target: {target}\n")


def main():
    symbol = 'GBPUSD=X'
    try:
        data = fetch_data(symbol)
        if not data.empty:
            data, last_macd, last_signal, last_histogram = calculate_macd(data)
            trade_levels = identify_trade_levels(data, last_macd, last_signal, last_histogram)
            print("\nTrade Setup for GBP/USD CFD:\n")
            for key, value in trade_levels.items():
                print(f"{key}: {value}")
            execute_trade(symbol, trade_levels['Trade Type'], 1, trade_levels['Stop Loss'], trade_levels['Target'])
        else:
            print("No data to process. Exiting.\n")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()