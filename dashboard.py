import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils.fetch_data import fetch_klines
from utils.db_handler import save_to_mongo
from utils.analysis import get_ohlc, detect_outliers
import datetime

st.title("Binance OHLC Dashboard")

# --- UI Controls ---
symbols = ["BTCUSDT", "ETHUSDT"]
selected_symbol = st.selectbox("Select Symbol", symbols)

intervals = ["1h", "4h", "1d"]
selected_interval = st.selectbox("Select Interval", intervals)

st.subheader("Select Time Range")
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=datetime.date(2025, 1, 1),
                               min_value=datetime.date(2020, 1, 1), max_value=datetime.date.today())
with col2:
    end_date = st.date_input("End Date", value=datetime.date.today(),
                             min_value=start_date, max_value=datetime.date.today())

# Convert to timestamps in seconds
start_timestamp = int(datetime.datetime.combine(start_date, datetime.time.min, tzinfo=datetime.timezone.utc).timestamp())
end_timestamp = int(datetime.datetime.combine(end_date, datetime.time.max, tzinfo=datetime.timezone.utc).timestamp())

thresholds = [1.0, 1.5, 2.0, 2.5, 3.0]
selected_threshold = st.selectbox("Select Z-Score Threshold for Outlier Detection", thresholds)

method = st.radio("Outlier Detection Method", options=["Z-Score", "IQR"])
chart_type = st.radio("Select Chart Type", ["Candlestick", "Renko"])

# Renko only input
if chart_type == "Renko":
    brick_size = st.number_input("Brick Size", min_value=1.0, value=50.0, step=10.0)

# --- Main Execution ---
if st.button("Fetch and Analyze"):
    with st.spinner("Fetching and analyzing data..."):
        raw_data = fetch_klines(selected_symbol, interval=selected_interval,
                                start_time=start_timestamp, end_time=end_timestamp)
        if raw_data is None or len(raw_data) == 0:
            st.error("Failed to fetch data from Binance.")
        else:
            save_to_mongo(raw_data, db_name="binance_data", collection_name="klines")
            ohlc_data = get_ohlc()

            if ohlc_data.empty:
                st.error("No data available in MongoDB.")
            else:
                df_with_outliers = detect_outliers(ohlc_data, column="close", threshold=selected_threshold, method=method)

                # Ensure timestamp is in correct format
                df_with_outliers["Timestamp"] = pd.to_datetime(df_with_outliers["open_time"].astype("int64"), unit="ms")

                # COMMON OUTPUTS
                st.subheader("OHLC Data")
                df_display = df_with_outliers.rename(columns={
                    "open": "Open", "high": "High", "low": "Low", "close": "Close"
                })
                st.dataframe(df_display[["Timestamp", "Open", "High", "Low", "Close"]])

                # RENKO CHART
                if chart_type == "Renko":
                    def generate_renko(df, brick_size):
                        prices = df["close"].values
                        bricks = []
                        last_price = prices[0]
                        for price in prices:
                            diff = price - last_price
                            if abs(diff) >= brick_size:
                                direction = "Up" if diff > 0 else "Down"
                                brick = {
                                    "close": last_price + brick_size if diff > 0 else last_price - brick_size,
                                    "direction": direction
                                }
                                bricks.append(brick)
                                last_price = brick["close"]
                        return pd.DataFrame(bricks)

                    renko_df = generate_renko(ohlc_data.copy(), brick_size)
                    renko_df["brick_index"] = np.arange(len(renko_df))

                    st.subheader("Renko Chart")
                    st.markdown("**Renko Chart (No Time Dependency)**")

                    fig = go.Figure()

                    # Color-coded bricks
                    fig.add_trace(go.Scatter(
                        x=renko_df["brick_index"],
                        y=renko_df["close"],
                        mode="lines+markers",
                        line=dict(color="green"),
                        name="Up",
                        showlegend=True,
                        marker=dict(color=np.where(renko_df["direction"] == "Up", "green", "red"))
                    ))

                    fig.update_layout(title="Renko Chart (No Date Axis)", xaxis_title="Brick Index", yaxis_title="Price")
                    st.plotly_chart(fig)

                # CANDLESTICK-ONLY FEATURES
                if chart_type == "Candlestick":
                    st.subheader("Candlestick Characteristics")
                    st.dataframe(df_with_outliers[[ 
                        "date", "type", "type_two", "type_three",
                        "upper_wick_percentage", "lower_wick_percentage",
                        "moving_average", "is_bullish"
                    ]])

                    st.subheader("Close Prices with Outliers")
                    fig = px.line(df_with_outliers, x="Timestamp", y="close",
                                  title=f"{selected_symbol} Close Price ({selected_interval})")

                    fig.add_hline(y=df_with_outliers["close"].mean(), line_dash="dot",
                                  line_color="green", annotation_text="Mean Price")

                    outliers = df_with_outliers[df_with_outliers["is_outlier"] == True]
                    if not outliers.empty:
                        fig.add_scatter(x=outliers["Timestamp"], y=outliers["close"],
                                        mode="markers", name="Outliers",
                                        marker=dict(color="red", size=10))

                    patterns = df_with_outliers[df_with_outliers["type"] != "-"]
                    if not patterns.empty:
                        fig.add_scatter(x=patterns["Timestamp"], y=patterns["close"],
                                        mode="markers", name="Candle Pattern",
                                        marker=dict(color="blue", size=6, symbol="diamond"))

                    st.plotly_chart(fig)
