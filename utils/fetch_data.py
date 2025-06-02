import requests
import pandas as pd
import time
from pymongo import MongoClient
import os

# MongoDB setup
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(mongo_uri)
db = client["binance_data"]
collection = db["klines"]

def fetch_klines(symbol, interval, start_time=None, end_time=None):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": 1000
    }

    if start_time:
        params["startTime"] = int(start_time * 1000)
    if end_time:
        params["endTime"] = int(end_time * 1000)

    all_data = []
    while True:
        res = requests.get(url, params=params)
        res.raise_for_status()
        klines = res.json()

        if not klines:
            break

        all_data.extend(klines)
        last_close_time = klines[-1][6]
        if last_close_time >= params.get("endTime", float('inf')):
            break
        params["startTime"] = last_close_time + 1
        time.sleep(0.3)

    df = pd.DataFrame(all_data, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_vol", "taker_buy_quote_vol", "ignore"
    ])

    df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
    df[["open_time", "close_time"]] = df[["open_time", "close_time"]].astype("int64")
    
    return df[["open_time", "open", "high", "low", "close", "volume", "close_time"]]
