from pymongo import MongoClient
import os

from utils.candle_utils import (
    binanceArrayToCandleStickArray,
    updateCandlePattern,
    calculate_moving_average,
    analyze_hourly_data,
)


def save_to_mongo(data, db_name="binance_ohlc", collection_name="candlestick"):
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]
    collection.delete_many({})

    # CONVERT raw data to enriched candlestick objects
    candles = binanceArrayToCandleStickArray(data, SYMBOL="BTCUSDT", PERIOD="1h")
    candles = updateCandlePattern(candles)
    candles = calculate_moving_average(candles, period=5)

    for candle in candles:
        analysis = analyze_hourly_data([candle])
        if analysis:
            candle.isCrossed = analysis["isCrossed"]
            candle.is_high_formed_first = analysis["is_high_formed_first"]
            candle.high_time = analysis["high_time"]
            candle.low_time = analysis["low_time"]

        # Convert to dictionary before saving
        collection.insert_one(candle.to_dict())

