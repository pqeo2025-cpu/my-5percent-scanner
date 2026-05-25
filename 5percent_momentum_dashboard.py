import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import pandas_ta as ta
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="My 5% Daily Scanner", layout="wide")
st.title("🚀 My 5% Daily Profit Momentum Scanner")
st.write("**NYSE Stocks for TradeRepublic** • Auto updates every 60 seconds • Pre-EU Open")

st_autorefresh(interval=60*1000, limit=1000, key="datarefresh")

# 10 High-Momentum NYSE Stocks (tradable on TradeRepublic)
stocks = {
    "NVIDIA": "NVDA", "Tesla": "TSLA", "Apple": "AAPL",
    "Microsoft": "MSFT", "Amazon": "AMZN", "Meta": "META",
    "Palantir": "PLTR", "Alphabet": "GOOGL", "Super Micro": "SMCI",
    "Eli Lilly": "LLY"
}

st.sidebar.header("🎛️ My Filters (Advisor Style)")
min_change = st.sidebar.slider("Minimum % Change (for big moves)", 0.0, 10.0, 1.0)
min_volume = st.sidebar.slider("Minimum Volume Ratio", 1.0, 5.0, 1.5)
rsi_max = st.sidebar.slider("Max RSI (avoid overbought)", 30, 80, 70)

data = []
for name, ticker in stocks.items():
    try:
        df = yf.download(ticker, period="3d", interval="15m", progress=False)
        if len(df) < 5: 
            continue
            
        price = float(df['Close'].iloc[-1])
        change = (price - float(df['Close'].iloc[-2])) / float(df['Close'].iloc[-2]) * 100
        vol_ratio = float(df['Volume'].iloc[-1] / df['Volume'].mean())

        df['RSI'] = ta.rsi(df['Close'])
        rsi = float(df['RSI'].iloc[-1])

        data.append({
            "Stock": name,
            "Ticker": ticker,
            "Price": round(price, 2),
            "% Change": round(change, 2),
            "Volume Ratio": round(vol_ratio, 2),
            "RSI": round(rsi, 1)
        })
    except:
        pass

df_results = pd.DataFrame(data)

filtered = df_results[
    (df_results["% Change"] >= min_change) & 
    (df_results["Volume Ratio"] >= min_volume) &
    (df_results["RSI"] <= rsi_max)
].sort_values("% Change", ascending=False)

def color_row(val):
    if val >= 3.0: return 'background-color: #90EE90; color: black'
    elif val >= 1.5: return 'background-color: #D4EDDA; color: black'
    return ''

st.subheader("🔥 Top Momentum Stocks Right Now (Advisor Style)")
styled = filtered.style.applymap(color_row, subset=['% Change'])
st.dataframe(styled, use_container_width=True, height=420)

if not filtered.empty:
    st.success(f"**{len(filtered)} good momentum stocks** found! Green rows = strongest for quick moves.")
    
    selected = st.selectbox("👉 Click any stock to see chart", filtered["Stock"])
    ticker = next(t for n, t in stocks.items() if n == selected)
    
    hist = yf.download(ticker, period="5d", interval="15m")
    fig = go.Figure(data=[go.Candlestick(x=hist.index,
                    open=hist['Open'], high=hist['High'],
                    low=hist['Low'], close=hist['Close'])])
    fig.update_layout(title=f"{selected} - 15min Chart", height=650)
    st.plotly_chart(fig, use_container_width=True)

st.info("**Strategy Tips (from stock advisors)**: Focus on green stocks with high volume. Buy on strong upward move. Set stop-loss 1-2% below. Take profit at 3-5%. Trade only during active hours.")
st.warning("⚠️ 5% daily is very difficult. Use small money only. This is just a helper tool.")

st.caption("Data: yfinance • Not financial advice • High risk")
