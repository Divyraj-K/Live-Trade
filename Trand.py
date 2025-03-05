import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import time

st.title("📊 Live Crypto Candlestick Chart with Moving Averages")

# Select cryptocurrency pair
crypto_pair = st.selectbox("Select Cryptocurrency", ["BTCUSDT", "ETHUSDT", "BNBUSDT"])

# Select refresh interval
refresh_interval = st.selectbox("Select Refresh Interval (seconds)", [10, 30, 60], index=1)

# Select moving averages
sma_period = st.slider("SMA Period", 5, 50, 20)
ema_period = st.slider("EMA Period", 5, 50, 10)


# Function to fetch live crypto data from Binance API
def fetch_binance_data(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=50"
    response = requests.get(url)
    if response.status_code != 200:
        st.error("⚠️ Error fetching data from Binance API")
        return None

    data = response.json()
    df = pd.DataFrame(data, columns=[
        "Time", "Open", "High", "Low", "Close", "Volume", "CloseTime",
        "QuoteAssetVolume", "NumberOfTrades", "TakerBuyBaseAssetVolume",
        "TakerBuyQuoteAssetVolume", "Ignore"
    ])

    df["Time"] = pd.to_datetime(df["Time"], unit="ms")
    df[["Open", "High", "Low", "Close"]] = df[["Open", "High", "Low", "Close"]].astype(float)

    df["SMA"] = df["Close"].rolling(window=sma_period).mean()
    df["EMA"] = df["Close"].ewm(span=ema_period, adjust=False).mean()

    return df


# Fetch data
df = fetch_binance_data(crypto_pair)

# Check if data is available
if df is not None and not df.empty:
    # Plot candlestick chart
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df["Time"],
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Candles"
    ))

    fig.add_trace(go.Scatter(
        x=df["Time"], y=df["SMA"], mode="lines", name=f"SMA-{sma_period}", line=dict(color='blue', width=1)
    ))

    fig.add_trace(go.Scatter(
        x=df["Time"], y=df["EMA"], mode="lines", name=f"EMA-{ema_period}", line=dict(color='orange', width=1)
    ))

    fig.update_layout(title=f"{crypto_pair} - 1 Min Candlestick Chart", xaxis_rangeslider_visible=False)

    st.plotly_chart(fig, use_container_width=True)

    # Refresh logic (without breaking Streamlit Cloud)
    time.sleep(refresh_interval)
    st.experimental_rerun()
else:
    st.warning("⚠️ No data available. Try again later.")

