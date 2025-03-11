import yfinance as yf
import numpy as np
import pandas as pd


def get_spy_data():
    spy = yf.Ticker("SPY")
    return spy.history(period="50d", interval="1d")


def market_sentiment_score(hist):
    usm = min(max(5 + int((hist["Close"].iloc[-1] - hist["Close"].iloc[-5]) / hist["Close"].iloc[-5] * 100 * 2), 1), 10)
    nikkei = yf.Ticker("^N225").history(period="2d")["Close"]
    gm = min(max(5 + int((nikkei.iloc[-1] - nikkei.iloc[-2]) / nikkei.iloc[-2] * 100 * 2), 1), 10)
    futures = yf.Ticker("ES=F").history(period="1d", interval="1m")
    pm = min(max(5 + int((futures["Close"].iloc[-1] - futures["Close"].iloc[0]) / futures["Close"].iloc[0] * 100 * 2), 1), 10)
    return (usm + gm + pm) / 30


def previous_market_performance(hist):
    change = (hist["Close"].iloc[-1] - hist["Close"].iloc[-2]) / hist["Close"].iloc[-2] * 100
    return 0.05 if change > 1.5 else -0.05 if change < -1.5 else 0


def technical_analysis_score(hist):
    closes = hist["Close"].tail(15)
    gains = np.where(closes.diff() > 0, closes.diff(), 0)
    losses = np.where(closes.diff() < 0, -closes.diff(), 0)
    avg_gain = gains[-14:].mean()
    avg_loss = losses[-14:].mean()
    rs = avg_gain / avg_loss if avg_loss != 0 else 10
    rsi = 100 - (100 / (1 + rs)) if avg_loss != 0 else 100
    rsi_score = min(max(int(rsi / 10), 1), 10)  # Gradient 1-10

    sma = hist["Close"].tail(50).mean()
    sma_diff = (hist["Close"].iloc[-1] - sma) / sma * 100
    sma_score = min(max(5 + int(sma_diff * 2), 1), 10)  # Gradient based on % deviation

    ema12 = hist["Close"].ewm(span=12, adjust=False).mean().iloc[-1]
    ema26 = hist["Close"].ewm(span=26, adjust=False).mean().iloc[-1]
    macd = ema12 - ema26
    macd_score = min(max(5 + int(macd / abs(macd) * 5) if macd != 0 else 5, 1), 10)  # Simplified gradient

    vol = min(max(int(hist["Volume"].iloc[-1] / hist["Volume"].mean() * 5), 1), 10)
    vw = 5  # Static VWAP proxy (yfinance limitation)

    return (vw + rsi_score + sma_score + macd_score + vol) / 50


def options_market_analysis():
    vix = yf.Ticker("^VIX").history(period="1d")["Close"].iloc[-1]
    iv_score = min(max(int(vix / 5), 1), 10)  # Implied Volatility proxy
    hv = yf.Ticker("SPY").history(period="20d")["Close"].pct_change().std() * np.sqrt(252) * 100
    hv_score = min(max(int(hv / 5), 1), 10)  # Historical Volatility
    # Put/Call, Vega, Theta, Delta, Gamma not directly available in yfinance; using proxies
    pc_score = 5  # Neutral placeholder
    return (iv_score + hv_score + pc_score + 5 + 5 + 5 + 5) / 70  # Adjusted to 0-1 scale


def historical_data_analysis(hist):
    trend = min(max(5 + int((hist["Close"].iloc[-1] - hist["Close"].iloc[-5]) / hist["Close"].iloc[-5] * 100 * 2), 1), 10)
    gap = min(max(5 + int((hist["Open"].iloc[-1] - hist["Close"].iloc[-2]) / hist["Close"].iloc[-2] * 100 * 2), 1), 10)
    vix = yf.Ticker("^VIX").history(period="1d")["Close"].iloc[-1]
    impact = min(max(int(vix / 5), 1), 10)
    return (trend + gap + impact) / 30


def final_market_direction(ms, mpf, tas, oma, hda):
    return (ms + mpf + tas + oma + hda) / 5


def strike_selection(fmd, current_price):
    return [float(current_price + i) for i in range(2, 7)] if fmd >= 0.50 else [float(current_price - i) for i in range(2, 7)]


def risk_management():
    return {
        "initial_stop_loss": "20%-25%",
        "breakeven_at": "30% profit, adjust stop to 5% breakeven",
        "profit_locking": {"40% profit": "tighten stop to 15%", "70% profit": "scale out"}
    }


def position_sizing(capital, previous_loss=None):
    if previous_loss and previous_loss >= 0.05 * capital:  # 5%+ loss
        max_capital = capital * 0.80  # 80% of remaining after loss
    else:
        max_capital = capital
    return {
        "initial_position": f"30% of ${max_capital:.2f} = ${max_capital * 0.30:.2f}",
        "remaining": f"70% of ${max_capital:.2f} = ${max_capital * 0.70:.2f}"
    }


def main():
    hist = get_spy_data()
    current_price = hist["Close"].iloc[-1]
    ms = market_sentiment_score(hist)
    mpf = previous_market_performance(hist)
    tas = technical_analysis_score(hist)
    oma = options_market_analysis()
    hda = historical_data_analysis(hist)
    fmd = final_market_direction(ms, mpf, tas, oma, hda)
    strikes = strike_selection(fmd, current_price)
    risk = risk_management()
    capital = 10000  # Example capital; adjust as needed
    sizing = position_sizing(capital)  # No previous loss assumed

    print(f"SPY Close: {current_price:.2f}")
    print(f"MS: {ms:.3f}, MPF: {mpf:.3f}, TAS: {tas:.3f}, OMA: {oma:.3f}, HDA: {hda:.3f}")
    print("\n------------------ MARKET ANALYSIS RESULTS ------------------")
    print(f"Final Market Direction (FMD): {fmd:.3f}")
    print(f"Trade Type: {'CALLS (Bullish)' if fmd >= 0.50 else 'PUTS (Bearish)'}")
    print("\nSuggested Strike Prices:")
    for strike in strikes:
        print(f"  - {strike:.2f}")
    print(f"\nPosition Sizing (Capital: ${capital}):")  # Fixed formatting
    for key, value in sizing.items():
        print(f"  {key.capitalize()}: {value}")
    print("\nRisk Management Guidelines:")
    print(f"  Initial Stop Loss: {risk['initial_stop_loss']}")
    print(f"  Breakeven: {risk['breakeven_at']}")
    print(f"  Profit Locking:")
    for profit, action in risk['profit_locking'].items():
        print(f"    - {profit}: {action}")
    print("\n------------------------------------------------------------")


if __name__ == "__main__":
    main()
