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

    if start_time is not None:
        params["startTime"] = int(start_time * 1000)
    if end_time is not None:
        params["endTime"] = int(end_time * 1000)

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        if isinstance(data, dict) and "code" in data:
            print(f"❌ Binance API error: {data['msg']} (Code: {data['code']})")
            return []

        if not data:
            print("❌ No data fetched from Binance for the given time range.")
            return []

        return data  # ✅ return list of lists, not DataFrame

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch data from Binance: {str(e)}")
        return []
    except ValueError as e:
        print(f"❌ Failed to parse API response as JSON: {str(e)}")
        print(f"Response content: {response.text}")
        return []
