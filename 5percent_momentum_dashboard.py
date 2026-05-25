import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="5% Daily Scanner", layout="wide")
st.title("🚀 My 5% Daily Momentum Scanner")
st.write("**NYSE Stocks for TradeRepublic** • Updated every time you click Refresh")

# 10 Strong NYSE Stocks
stocks = {
    "NVIDIA": "NVDA", "Tesla": "TSLA", "Apple": "AAPL",
    "Microsoft": "MSFT", "Amazon": "AMZN", "Meta": "META",
    "Palantir": "PLTR", "Alphabet": "GOOGL", "Super Micro": "SMCI",
    "Eli Lilly": "LLY"
}

st.sidebar.header("Filters")
min_change = st.sidebar.slider("Minimum % Change", 0.0, 10.0, 1.0)
min_volume = st.sidebar.slider("Minimum Volume Ratio", 1.0, 5.0, 1.5)

if st.button("🔄 Refresh Data Now"):
    st.rerun()

data = []
for name, ticker in stocks.items():
    try:
        df = yf.download(ticker, period="3d", interval="15m", progress=False)
        if len(df) < 5:
            continue

        price = float(df['Close'].iloc[-1])
        change = (price - float(df['Close'].iloc[-2])) / float(df['Close'].iloc[-2]) * 100
        vol_ratio = float(df['Volume'].iloc[-1] / df['Volume'].mean())

        # Simple RSI Calculation (without extra libraries)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = float(rsi.iloc[-1])

        data.append({
            "Stock": name,
            "Ticker": ticker,
            "Price": round(price, 2),
            "% Change": round(change, 2),
            "Volume Ratio": round(vol_ratio, 2),
            "RSI": round(current_rsi, 1)
        })
    except:
        pass

df_results = pd.DataFrame(data)

filtered = df_results[
    (df_results["% Change"] >= min_change) & 
    (df_results["Volume Ratio"] >= min_volume)
].sort_values("% Change", ascending=False)

# Color function
def highlight(val):
    if val >= 3.0:
        return 'background-color: #90EE90'
    elif val >= 1.5:
        return 'background-color: #D4EDDA'
    return ''

st.subheader("🔥 Top Momentum Stocks Right Now")
styled_df = filtered.style.applymap(highlight, subset=['% Change'])
st.dataframe(styled_df, use_container_width=True, height=420)

if not filtered.empty:
    selected = st.selectbox("Select a stock to see chart", filtered["Stock"])
    ticker = next(t for n, t in stocks.items() if n == selected)
    
    hist = yf.download(ticker, period="5d", interval="15m")
    fig = go.Figure(data=[go.Candlestick(x=hist.index,
                    open=hist['Open'], high=hist['High'],
                    low=hist['Low'], close=hist['Close'])])
    fig.update_layout(title=f"{selected} - 15min Chart", height=650)
    st.plotly_chart(fig, use_container_width=True)

st.info("**Strategy**: Focus on green rows with high volume. Take 3-5% profit when possible.")
st.warning("⚠️ Remember: 5% daily is very hard and risky. Trade small.")

st.caption("Data from yfinance • Not financial advice")
