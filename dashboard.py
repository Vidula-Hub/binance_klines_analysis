import streamlit as st
import pandas as pd
import plotly.express as px
from utils.fetch_data import fetch_klines
from utils.db_handler import save_to_mongo
from utils.analysis import get_ohlc, detect_outliers
import datetime
import time

st.title("Binance OHLC Dashboard")

symbols = ["BTCUSDT", "ETHUSDT"]
selected_symbol = st.selectbox("Select Symbol", symbols)

intervals = ["1h", "4h", "1d"]
selected_interval = st.selectbox("Select Interval", intervals)

st.subheader("Select Time Range")
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=datetime.date(2025, 1, 1), min_value=datetime.date(2020, 1, 1), max_value=datetime.date.today())
with col2:
    end_date = st.date_input("End Date", value=datetime.date.today(), min_value=start_date, max_value=datetime.date.today())

start_datetime = datetime.datetime.combine(start_date, datetime.time.min, tzinfo=datetime.timezone.utc)
end_datetime = datetime.datetime.combine(end_date, datetime.time.max, tzinfo=datetime.timezone.utc)
start_timestamp = int(start_datetime.timestamp())
end_timestamp = int(end_datetime.timestamp())

thresholds = [1.0, 1.5, 2.0, 2.5, 3.0]
selected_threshold = st.selectbox("Select Z-Score Threshold for Outlier Detection", thresholds)

if st.button("Fetch and Analyze"):
    with st.spinner("Fetching and analyzing data..."):
        df = fetch_klines(selected_symbol, interval=selected_interval, start_time=start_timestamp, end_time=end_timestamp)
        
        if df.empty:
            st.error("Failed to fetch data from Binance for the selected time range.")
        else:
            save_to_mongo(df, db_name="binance_data", collection_name="klines")
            ohlc_data = get_ohlc()
            
            if ohlc_data.empty:
                st.error("No data available in MongoDB for the selected symbol and time range.")
            else:
                df_with_outliers = detect_outliers(ohlc_data, column='close', threshold=selected_threshold)
                st.subheader("OHLC Data")
                df_display = df_with_outliers.rename(columns={"open_time": "Timestamp", 
                                                            "open": "Open", 
                                                            "high": "High", 
                                                            "low": "Low", 
                                                            "close": "Close"})
                st.dataframe(df_display[["Timestamp", "Open", "High", "Low", "Close"]])
                
                st.subheader("Close Prices with Outliers")
                fig = px.line(df_with_outliers, x="open_time", y="close", 
                            title=f"Close Prices for {selected_symbol} ({selected_interval} interval)")
                
                outlier_df = df_with_outliers[df_with_outliers["is_outlier"] == True]
                if not outlier_df.empty:
                    fig.add_scatter(x=outlier_df["open_time"], y=outlier_df["close"], 
                                  mode="markers", name="Outliers", 
                                  marker=dict(color="red", size=10))
                else:
                    st.warning("No outliers detected with the current threshold. Try lowering the threshold.")
                
                st.plotly_chart(fig)