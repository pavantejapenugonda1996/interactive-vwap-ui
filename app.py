import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(layout="wide", page_title="Interactive VWAP Chart")
st.title("📈 Interactive VWAP (HLC) Chart with Timeframe Selector")

# Upload file
uploaded_file = st.file_uploader("Upload CSV or Excel file (no header needed)", type=["csv", "xlsx"])

# Select timeframe
timeframe = st.selectbox(
    "Select timeframe",
    options=["1 min", "5 min", "10 min", "15 min", "1 hour"]
)

# Map selectbox to pandas resample rule
resample_map = {
    "1 min": "1T",
    "5 min": "5T",
    "10 min": "10T",
    "15 min": "15T",
    "1 hour": "1H"
}

def load_file(file):
    if file.name.endswith(".csv"):
        df = pd.read_csv(file, header=None)
    else:
        df = pd.read_excel(file, header=None)
    # Assign standard columns
    df.columns = ["date", "timestamp", "o", "h", "l", "c","volume","other1"]
    return df

def compute_vwap(df):
    """VWAP using provided volume, defaulting to unit volume when missing."""
    tp = (df["high"] + df["low"] + df["close"]) / 3
    vol = df.get("volume", pd.Series(1, index=df.index))
    vol = vol.fillna(0)
    return (tp * vol).cumsum() / vol.cumsum()


if uploaded_file:
    df = load_file(uploaded_file)

    # Combine date + timestamp
    df["datetime"] = pd.to_datetime(df["date"].astype(str) + " " + df["timestamp"].astype(str))

    # Select a single trading date to plot
    available_dates = sorted(df["datetime"].dt.date.unique())
    if not available_dates:
        st.error("No valid dates found in the file.")
        st.stop()

    selected_date = st.selectbox(
        "Select trading date",
        options=available_dates,
        format_func=lambda d: d.strftime("%Y-%m-%d")
    )

    df = df[df["datetime"].dt.date == selected_date]
    if df.empty:
        st.warning("No data for the selected date.")
        st.stop()

    # Map OHLC
    df["open"] = df["o"]
    df["high"] = df["h"]
    df["low"] = df["l"]
    df["close"] = df["c"]
    # Ensure volume is numeric and gap-free so the dotted line stays continuous
    df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0)
    df.set_index("datetime", inplace=True)
    df.sort_index(inplace=True)

    # --- Resample based on selected timeframe ---
    rule = resample_map[timeframe]

    df_resampled = pd.DataFrame()
    df_resampled["open"] = df["open"].resample(rule).first()
    df_resampled["high"] = df["high"].resample(rule).max()
    df_resampled["low"] = df["low"].resample(rule).min()
    df_resampled["close"] = df["close"].resample(rule).last()
    df_resampled["volume"] = df["volume"].resample(rule).sum()

    df_resampled.dropna(inplace=True)  # remove periods with no data

    df_resampled["vwap"] = compute_vwap(df_resampled)
    df_resampled.reset_index(inplace=True)

    # Align colors between candles and volume bars using the same up/down palette
    up_color = "#2ca02c"
    down_color = "#d62728"
    volume_colors = [up_color if c >= o else down_color for o, c in zip(df_resampled["open"], df_resampled["close"])]

    # --- Plotting ---
    fig = make_subplots(rows=1, cols=1, specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Candlestick(
            x=df_resampled["datetime"],
            open=df_resampled["open"],
            high=df_resampled["high"],
            low=df_resampled["low"],
            close=df_resampled["close"],
            name="Price",
            increasing_line_color=up_color,
            increasing_fillcolor=up_color,
            decreasing_line_color=down_color,
            decreasing_fillcolor=down_color,
            hovertemplate="<b>%{x}</b><br>Open: %{open}<br>High: %{high}<br>Low: %{low}<br>Close: %{close}<extra></extra>"
        ),
        row=1,
        col=1,
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=df_resampled["datetime"],
            y=df_resampled["vwap"],
            mode="lines",
            name="VWAP (HLC)",
            line=dict(width=2),
            hovertemplate="<b>%{x}</b><br>VWAP: %{y:.2f}<extra></extra>"
        ),
        row=1,
        col=1,
        secondary_y=False
    )

    fig.add_trace(
        go.Bar(
            x=df_resampled["datetime"],
            y=df_resampled["volume"],
            name="Volume",
            marker_color=volume_colors,
            showlegend=False,
            opacity=0.35
        ),
        row=1,
        col=1,
        secondary_y=True
    )

    fig.update_yaxes(
        title_text="Price",
        tickformat=",.2f",
        separatethousands=True,
        secondary_y=False
    )
    fig.update_yaxes(
        title_text="Volume",
        tickformat=".3s",
        separatethousands=True,
        rangemode="tozero",
        showgrid=False,
        secondary_y=True
    )
    fig.update_xaxes(title_text="Time", tickformat="%H:%M", dtick=15 * 60 * 1000)

    fig.update_layout(
        height=750,
        bargap=0,
        hovermode="x unified",
        legend=dict(orientation="h", y=1.02, x=1, xanchor="right"),
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("⬆ Upload your CSV or Excel file (no headers is fine) to view the chart")
