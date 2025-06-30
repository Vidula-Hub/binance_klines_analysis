import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils.fetch_data import fetch_klines
from utils.db_handler import save_to_mongo
from utils.analysis import get_ohlc, detect_outliers
import datetime

st.set_page_config(page_title="Binance OHLC Dashboard", layout="wide")

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2c5aa0 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .sidebar-header {
        background: #2c5aa0;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>📈 Binance OHLC Analytics Dashboard</h1>
    <p>Advanced cryptocurrency market analysis with professional charting tools</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("<div class='sidebar-header'><h3>⚙️ Configuration Panel</h3></div>", unsafe_allow_html=True)

    symbols = ["BTCUSDT", "ETHUSDT"]
    selected_symbol = st.selectbox("Select Symbol", symbols)

    intervals = ["1h", "4h", "1d"]
    selected_interval = st.selectbox("Select Interval", intervals)

    st.subheader("📅 Time Range")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime.date(2025, 1, 1),
                                   min_value=datetime.date(2020, 1, 1), max_value=datetime.date.today())
    with col2:
        end_date = st.date_input("End Date", value=datetime.date.today(),
                                 min_value=start_date, max_value=datetime.date.today())

    thresholds = [1.0, 1.5, 2.0, 2.5, 3.0]
    selected_threshold = st.selectbox("Z-Score Threshold", thresholds)

    method = st.radio("Outlier Detection Method", ["Z-Score", "IQR"])

    chart_type = st.radio("Chart Type", ["Candlestick", "Renko"])

    if chart_type == "Renko":
        renko_mode = st.radio("Brick Size Method", ["Auto", "Manual"])
        if renko_mode == "Manual":
            brick_size = st.number_input("Brick Size", min_value=1.0, value=50.0, step=10.0)

# Timestamp conversion
start_ts = int(datetime.datetime.combine(start_date, datetime.time.min, tzinfo=datetime.timezone.utc).timestamp())
end_ts = int(datetime.datetime.combine(end_date, datetime.time.max, tzinfo=datetime.timezone.utc).timestamp())

# Chart Generation Logic
def calculate_optimal_brick_size(df):
    if len(df) < 2:
        return df["close"].std() * 0.01
    price_changes = df["close"].diff().abs().dropna()
    percentile_bricks = [price_changes.quantile(p) for p in [0.2, 0.3, 0.4, 0.5]]
    min_size = df["close"].mean() * 0.001
    brick_sizes = [b for b in percentile_bricks if b >= min_size]
    return np.median(brick_sizes) if brick_sizes else min_size * 10

def generate_renko_optimized(df, brick_size):
    prices = df["close"].values
    timestamps = df["Timestamp"].values
    bricks = []
    current_price = prices[0]
    for i, price in enumerate(prices[1:]):
        price_diff = price - current_price
        while abs(price_diff) >= brick_size:
            if price_diff > 0:
                new_price = current_price + brick_size
                bricks.append({
                    "open": current_price,
                    "close": new_price,
                    "direction": "Up",
                    "Timestamp": timestamps[i]
                })
            else:
                new_price = current_price - brick_size
                bricks.append({
                    "open": current_price,
                    "close": new_price,
                    "direction": "Down",
                    "Timestamp": timestamps[i]
                })
            current_price = new_price
            price_diff = price - current_price
    return pd.DataFrame(bricks)

# --- MAIN Execution ---
if st.button("Fetch and Analyze"):
    with st.spinner("Fetching and processing data..."):
        raw_data = fetch_klines(selected_symbol, interval=selected_interval,
                                start_time=start_ts, end_time=end_ts)

        if raw_data is None or len(raw_data) == 0:
            st.error("No data retrieved.")
        else:
            save_to_mongo(raw_data, db_name="binance_data", collection_name="klines")
            ohlc_data = get_ohlc()

            if ohlc_data.empty:
                st.error("MongoDB returned no data.")
            else:
                df = detect_outliers(ohlc_data, column="close", threshold=selected_threshold, method=method)

                # Fix 1970 bug: ensure milliseconds are used
                df["Timestamp"] = pd.to_datetime(df["open_time"].astype("int64"), unit="ms")

                st.subheader("OHLC Data")
                st.dataframe(df[["Timestamp", "open", "high", "low", "close"]])

                if chart_type == "Renko":
                    st.subheader("Renko Chart")
                    if renko_mode == "Auto":
                        brick_size = calculate_optimal_brick_size(df)
                    st.markdown(f"**Brick Size Used:** `{brick_size:.2f}`")

                    renko_df = generate_renko_optimized(df.copy(), brick_size)
                    renko_df["brick_index"] = range(len(renko_df))

                    if renko_df.empty:
                        st.warning("Renko chart generated no bricks.")
                    else:
                        fig = go.Figure()
                        up = renko_df[renko_df["direction"] == "Up"]
                        down = renko_df[renko_df["direction"] == "Down"]

                        if not up.empty:
                            fig.add_trace(go.Bar(
                                x=up["brick_index"], y=up["close"] - up["open"], base=up["open"],
                                name="Up Bricks", marker_color="green", width=0.8
                            ))
                        if not down.empty:
                            fig.add_trace(go.Bar(
                                x=down["brick_index"], y=down["open"] - down["close"], base=down["close"],
                                name="Down Bricks", marker_color="red", width=0.8
                            ))

                        fig.update_layout(title="Renko Chart", xaxis_title="Brick Index", yaxis_title="Price",
                                          barmode="overlay", height=500)
                        st.plotly_chart(fig, use_container_width=True)

                        st.subheader("Renko Stats")
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Total Bricks", len(renko_df))
                        col2.metric("Up Bricks", len(up))
                        col3.metric("Down Bricks", len(down))

                elif chart_type == "Candlestick":
                    st.subheader("Candlestick Characteristics")
                    st.dataframe(df[[
                        "date", "type", "type_two", "type_three",
                        "upper_wick_percentage", "lower_wick_percentage",
                        "moving_average", "is_bullish"
                    ]])

                    st.subheader("Close Prices with Outliers")
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df["Timestamp"], y=df["close"], mode="lines", name="Close"
                    ))
                    fig.add_hline(y=df["close"].mean(), line_color="green", line_dash="dot", annotation_text="Mean")

                    outliers = df[df["is_outlier"] == True]
                    if not outliers.empty:
                        fig.add_trace(go.Scatter(
                            x=outliers["Timestamp"], y=outliers["close"], mode="markers",
                            marker=dict(size=8, color="red"), name="Outliers"
                        ))

                    patterns = df[df["type"] != "-"]
                    if not patterns.empty:
                        fig.add_trace(go.Scatter(
                            x=patterns["Timestamp"], y=patterns["close"], mode="markers",
                            marker=dict(size=6, color="blue", symbol="diamond"), name="Candle Patterns"
                        ))

                    fig.update_layout(title=f"{selected_symbol} Close Prices", height=500)
                    st.plotly_chart(fig, use_container_width=True)
