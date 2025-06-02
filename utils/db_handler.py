from pymongo import MongoClient
import os
from utils.candle_utils import (
    binanceArrayToCandleStickArray,
    updateCandlePattern,
    calculate_moving_average,
    analyze_hourly_data,
)

def save_to_mongo(data, db_name="binance_data", collection_name="klines"):
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]
    collection.delete_many({})

    # Make sure time columns are in milliseconds
    raw_array = data[["open_time", "open", "high", "low", "close", "volume", "close_time"]].values.tolist()

    candles = binanceArrayToCandleStickArray(raw_array, SYMBOL="BTCUSDT", PERIOD="1h")
    candles = updateCandlePattern(candles)
    candles = calculate_moving_average(candles, period=5)

    for candle in candles:
        analysis = analyze_hourly_data([candle])
        if analysis:
            candle.isCrossed = analysis["isCrossed"]
            candle.is_high_formed_first = analysis["is_high_formed_first"]
            candle.high_time = analysis["high_time"]
            candle.low_time = analysis["low_time"]

        collection.insert_one(candle.to_dict())
