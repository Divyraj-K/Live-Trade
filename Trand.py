import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import time

st.title("📊 Live Crypto Candlestick Chart with Moving Averages")

col1, col2 = st.columns([1,1])
# Select cryptocurrency pair
crypto_pair = col1.selectbox("Select Cryptocurrency", ["BTCUSDT", "ETHUSDT", "BNBUSDT"])

# Select refresh interval
refresh_interval = col2.selectbox("Select Refresh Interval", [10, 30, 60], index=1)  # Default 30s

# Select moving averages
sma_period = st.sidebar.slider("SMA Period", 5, 50, 20)  # Default 20
ema_period = st.sidebar.slider("EMA Period", 5, 50, 10)  # Default 10


# Function to fetch live crypto data from Binance API
def fetch_binance_data(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=100"
    response = requests.get(url)
    data = response.json()

    df = pd.DataFrame(data, columns=[
        "Time", "Open", "High", "Low", "Close", "Volume", "CloseTime",
        "QuoteAssetVolume", "NumberOfTrades", "TakerBuyBaseAssetVolume",
        "TakerBuyQuoteAssetVolume", "Ignore"
    ])

    df["Time"] = pd.to_datetime(df["Time"], unit="ms")  # Convert timestamp
    df[["Open", "High", "Low", "Close"]] = df[["Open", "High", "Low", "Close"]].astype(float)

    # Calculate Moving Averages
    df["SMA"] = df["Close"].rolling(window=sma_period).mean()
    df["EMA"] = df["Close"].ewm(span=ema_period, adjust=False).mean()

    return df


# Auto-refresh logic using session state
if "last_update" not in st.session_state:
    st.session_state.last_update = time.time()

df = fetch_binance_data(crypto_pair)

# Plot candlestick chart with moving averages
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

# Auto-refresh every user-selected seconds
if time.time() - st.session_state.last_update > refresh_interval:
    st.session_state.last_update = time.time()
    st.rerun()
