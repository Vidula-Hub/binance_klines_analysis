import requests
import pandas as pd
import time
from pymongo import MongoClient
import os

# MongoDB setup
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")  # Fallback to local for development
client = MongoClient(mongo_uri)
db = client["binance_data"]
collection = db["klines"]

# Binance API setup
symbol = "BTCUSDT"
interval = "1h"
limit = 1000

def fetch_klines(symbol, interval, start_time=None, end_time=None):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval
    }
    
    # Add startTime and endTime to the parameters if provided
    if start_time is not None:
        params["startTime"] = int(start_time * 1000)  # Convert to milliseconds
    if end_time is not None:
        params["endTime"] = int(end_time * 1000)      # Convert to milliseconds
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors (e.g., 400, 429)

        data = response.json()

        # Check if the response is a list (valid Kline data) or a dict (error response)
        if isinstance(data, dict) and "code" in data:
            print(f"❌ Binance API error: {data['msg']} (Code: {data['code']})")
            return pd.DataFrame()  # Return empty DataFrame on error

        if not data:
            print("❌ No data fetched from Binance for the given time range.")
            return pd.DataFrame()

        df = pd.DataFrame(data, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base_vol", "taker_buy_quote_vol", "ignore"
        ])

        # Convert time and price columns
        df["open_time"] = pd.to_datetime(df["open_time"], unit='ms')
        df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].astype(float)

        return df[["open_time", "open", "high", "low", "close"]]

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch data from Binance: {str(e)}")
        return pd.DataFrame()
    except ValueError as e:
        print(f"❌ Failed to parse API response as JSON: {str(e)}")
        print(f"Response content: {response.text}")
        return pd.DataFrame()

def store_to_mongo(df):
    records = df.to_dict(orient='records')
    collection.insert_many(records)
    print(f"Inserted {len(records)} records into MongoDB.")

if __name__ == "__main__":
    df = fetch_klines(symbol, interval, limit)
    print(df.head())  # Optional: see sample data
    store_to_mongo(df)