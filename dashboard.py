import streamlit as st
import pandas as pd
import plotly.express as px
from utils.fetch_data import fetch_klines
from utils.db_handler import save_to_mongo
from utils.analysis import get_ohlc, detect_outliers

# Streamlit app setup
st.title("Binance OHLC Dashboard")

# Dropdown for symbol selection
symbols = ["BTCUSDT", "ETHUSDT"]
selected_symbol = st.selectbox("Select Symbol", symbols)

# Dropdown for z-score threshold selection
thresholds = [1.0, 1.5, 2.0, 2.5, 3.0]
selected_threshold = st.selectbox("Select Z-Score Threshold for Outlier Detection", thresholds)

# Button to fetch and analyze data
if st.button("Fetch and Analyze"):
    with st.spinner("Fetching and analyzing data..."):
        # Fetch data from Binance
        df = fetch_klines(selected_symbol, interval="1d", limit=100)
        
        if df.empty:
            st.error("Failed to fetch data from Binance.")
        else:
            # Save to MongoDB (using the same collection as in fetch_data.py)
            save_to_mongo(df, db_name="binance_data", collection_name="klines")
            
            # Retrieve data from MongoDB
            ohlc_data = get_ohlc()
            
            if ohlc_data.empty:
                st.error("No data available in MongoDB for the selected symbol.")
            else:
                # Detect outliers on the 'close' column with the user-selected threshold
                df_with_outliers = detect_outliers(ohlc_data, column='close', threshold=selected_threshold)
                
                # Display OHLC table
                st.subheader("OHLC Data")
                df_display = df_with_outliers.rename(columns={"open_time": "Timestamp", 
                                                            "open": "Open", 
                                                            "high": "High", 
                                                            "low": "Low", 
                                                            "close": "Close"})
                st.dataframe(df_display[["Timestamp", "Open", "High", "Low", "Close"]])
                
                # Plot close prices with outliers
                st.subheader("Close Prices with Outliers")
                fig = px.line(df_with_outliers, x="open_time", y="close", 
                            title=f"Close Prices for {selected_symbol}")
                
                # Add scatter for outliers
                outlier_df = df_with_outliers[df_with_outliers["is_outlier"] == True]
                if not outlier_df.empty:
                    fig.add_scatter(x=outlier_df["open_time"], y=outlier_df["close"], 
                                  mode="markers", name="Outliers", 
                                  marker=dict(color="red", size=10))
                else:
                    st.warning("No outliers detected with the current threshold. Try lowering the threshold.")
                
                st.plotly_chart(fig)