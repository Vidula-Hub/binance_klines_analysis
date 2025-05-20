from pymongo import MongoClient
import pandas as pd

client = MongoClient("mongodb://localhost:27017/")
db = client["binance_data"]
collection = db["klines"]

def get_ohlc():
    """
    Fetch documents with 'open_time' and OHLC data from MongoDB and return a clean DataFrame.
    """
    data = list(collection.find({"open_time": {"$exists": True}}))
    if not data:
        print("❌ No data with 'open_time' found in the 'klines' collection.")
        return pd.DataFrame()
    
    df = pd.DataFrame(data)
    df['open_time'] = pd.to_datetime(df['open_time'])
    
    return df[['open_time', 'open', 'high', 'low', 'close']]

def detect_outliers(df, column='close', threshold=3):
    """
    Simple outlier detection using z-score method on a given column.
    Returns the DataFrame with an added boolean column 'is_outlier'.
    """
    if df.empty:
        print("❌ DataFrame is empty, cannot detect outliers.")
        return df

    from scipy import stats
    import numpy as np

    df = df.copy()
    df['z_score'] = stats.zscore(df[column].astype(float))
    df['is_outlier'] = np.abs(df['z_score']) > threshold

    df.drop(columns=['z_score'], inplace=True)
    return df
