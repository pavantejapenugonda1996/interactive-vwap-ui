import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Interactive VWAP Chart")
st.title("📈 Interactive VWAP (HLC) Chart")

uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

def load_file(file):
    if file.name.endswith(".csv"):
        # No headers in CSV
        df = pd.read_csv(file, header=None)
    else:
        # No headers in Excel
        df = pd.read_excel(file, header=None)
    # Assign standard column names
    df.columns = ["date", "timestamp", "o", "h", "l", "c","volume","other1"]
    return df

def compute_vwap(df):
    tp = (df["h"] + df["l"] + df["c"]) / 3
    vol = df["volume"]
    return (tp * vol).cumsum() / vol.cumsum()

if uploaded_file:
    df = load_file(uploaded_file)

    # Combine date + timestamp into datetime
    df["datetime"] = pd.to_datetime(df["date"].astype(str) + " " + df["timestamp"].astype(str))
    
    # Map OHLC
    df["open"] = df["o"]
    df["high"] = df["h"]
    df["low"] = df["l"]
    df["close"] = df["c"]

    df.sort_values("datetime", inplace=True)
    df["vwap"] = compute_vwap(df)

    fig = go.Figure()
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df["datetime"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="Price",
        hovertemplate="<b>%{x}</b><br>Open: %{open}<br>High: %{high}<br>Low: %{low}<br>Close: %{close}<extra></extra>"
    ))
    # VWAP
    fig.add_trace(go.Scatter(
        x=df["datetime"],
        y=df["vwap"],
        mode="lines",
        name="VWAP (HLC)",
        line=dict(width=2)
    ))

    fig.update_layout(
        height=750,
        xaxis=dict(
            title="Time",
            tickformat="%H:%M",
            dtick=5 * 60 * 1000,
            rangeslider=dict(visible=False)
        ),
        yaxis=dict(title="Price"),
        hovermode="x unified",
        legend=dict(orientation="h", y=1.02, x=1, xanchor="right")
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("⬆ Upload your CSV or Excel file (no headers is fine) to view the chart")