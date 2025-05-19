Binance OHLC Analysis Dashboard

This project fetches daily Binance Kline data (OHLC: Open, High, Low, Close) for cryptocurrencies like BTCUSDT and ETHUSDT, stores it in MongoDB, performs outlier analysis on closing prices, and displays the results in an interactive Streamlit dashboard.

Features
Fetches daily OHLC data from Binance.
Stores data in MongoDB.
Detects outliers in closing prices using the z-score method.
Displays an interactive dashboard with a dropdown for symbol selection, a threshold selector for outlier detection, an OHLC table, and a chart showing close prices with outliers marked in red.

Prerequisites
Python 3.7 or higher.
MongoDB installed and running on localhost:27017.
Internet connection to fetch data from Binance API.

Setup
Clone the repository:
git clone https://github.com/<your-username>/binance_klines_analysis.git
cd binance_klines_analysis

Install dependencies:
pip install -r requirements.txt

Start MongoDB (if not already running):
mongod

Run the dashboard:
streamlit run dashboard.py

Usage
Open the dashboard in your browser (Streamlit will provide the URL).
Select a symbol (e.g., BTCUSDT or ETHUSDT) from the dropdown.
Choose a z-score threshold for outlier detection.
Click "Fetch and Analyze" to fetch data, detect outliers, and display the OHLC table and chart.