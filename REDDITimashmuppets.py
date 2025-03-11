import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


# Function to fetch SPY data
def get_spy_data():
    spy = yf.Ticker("SPY")
    hist = spy.history(period="2d", interval="1d")
    return hist


# Step 1: Market Sentiment Score (MS)
def market_sentiment_score(usm, gm, pm):
    return (usm + gm + pm) / 30


# Step 2: Previous Day’s Market Performance Score (MPF)
def previous_market_performance(hist):
    change = (hist["Close"].iloc[-1] - hist["Close"].iloc[-2]) / hist["Close"].iloc[-2] * 100
    if change > 1.5:
        return 0.05
    elif change < -1.5:
        return -0.05
    return 0


# Step 3: Technical Analysis Score (TAS) - Placeholder values
def technical_analysis_score(vw, rsi, sma, macd, vol):
    return (vw + rsi + sma + macd + vol) / 50


# Step 4: Options Market Analysis Score (OMA) - Placeholder values
def options_market_analysis(pc, iv, v, t, d, g, hv):
    return (pc + iv + v + t + d + g + hv) / 70  # Normalize to 0-1 scale


# Step 5: Historical Market Data Analysis (HDA) - Placeholder
def historical_data_analysis(trend, gap, impact):
    return (trend + gap + impact) / 30  # Normalize to 0-1 scale


# Step 6: Final Market Direction (FMD)
def final_market_direction(ms, mpf, tas, oma, hda):
    return (ms + mpf + tas + oma + hda) / 5  # Ensure values are normalized between 0-1


# Step 7: Strike Selection & Position Sizing
def strike_selection(fmd, current_price):
    if fmd >= 0.50:
        return [float(current_price + i) for i in range(2, 7)]  # Calls
    else:
        return [float(current_price - i) for i in range(2, 7)]  # Puts


# Step 9: Risk Management (Stop-loss and Profit targets)
def risk_management():
    return {
        "initial_stop_loss": "20%-25%",
        "breakeven_at": "30% profit",
        "profit_locking": {"40% profit": "tighten stop to 15%", "70% profit": "scale out"}
    }


# Main execution
def main():
    hist = get_spy_data()
    current_price = hist["Close"].iloc[-1]

    # Replace placeholder values with actual data sources
    ms = market_sentiment_score(7, 6, 5)  # Example values
    mpf = previous_market_performance(hist)
    tas = technical_analysis_score(8, 7, 6, 7, 8)
    oma = options_market_analysis(6, 7, 5, 6, 7, 6, 5)
    hda = historical_data_analysis(7, 6, 5)

    fmd = final_market_direction(ms, mpf, tas, oma, hda)
    strikes = strike_selection(fmd, current_price)
    risk = risk_management()

    # Output results in a readable format
    print("\n------------------ MARKET ANALYSIS RESULTS ------------------")
    print(f"Final Market Direction (FMD): {fmd:.3f}")

    if fmd >= 0.50:
        print(f"Trade Type: CALLS (Bullish)")
    else:
        print(f"Trade Type: PUTS (Bearish)")

    print("\nSuggested Strike Prices:")
    for strike in strikes:
        print(f"  - {strike:.2f}")

    print("\nRisk Management Guidelines:")
    print(f"  Initial Stop Loss: {risk['initial_stop_loss']}")
    print(f"  Breakeven: {risk['breakeven_at']}")
    print(f"  Profit Locking:")
    for profit, action in risk['profit_locking'].items():
        print(f"    - {profit}: {action}")

    print("\n------------------------------------------------------------")


if __name__ == "__main__":
    main()
