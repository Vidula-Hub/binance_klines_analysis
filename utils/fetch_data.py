import requests
import pandas as pd
import time
from pymongo import MongoClient

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["binance_data"]
collection = db["klines"]

# Binance API setup
symbol = "BTCUSDT"
interval = "1h"
limit = 1000

def fetch_klines(symbol, interval, limit):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    response = requests.get(url, params=params)
    data = response.json()

    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_vol", "taker_buy_quote_vol", "ignore"
    ])

    # Convert time and price columns
    df["open_time"] = pd.to_datetime(df["open_time"], unit='ms')
    df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].astype(float)

    return df[["open_time", "open", "high", "low", "close"]]

def store_to_mongo(df):
    records = df.to_dict(orient='records')
    collection.insert_many(records)
    print(f"Inserted {len(records)} records into MongoDB.")

if __name__ == "__main__":
    df = fetch_klines(symbol, interval, limit)
    print(df.head())  # Optional: see sample data
    store_to_mongo(df)
