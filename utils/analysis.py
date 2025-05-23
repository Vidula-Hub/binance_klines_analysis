from pymongo import MongoClient
import pandas as pd
import os

# Connect to MongoDB
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(mongo_uri)
db = client["binance_data"]
collection = db["klines"]

def get_ohlc():
    """
    Fetch documents with 'open_time' and OHLC data from MongoDB and return a clean DataFrame.
    """
    data = list(collection.find({"open_time": {"$exists": True}}))
    if not data:
        print(" No data with 'open_time' found in the 'klines' collection.")
        return pd.DataFrame()  # Return empty DataFrame
    
    df = pd.DataFrame(data)
    df['open_time'] = pd.to_datetime(df['open_time'])
    
    # Select only relevant columns for OHLC
    return df

def detect_outliers(df, column='close', threshold=3, method='Z-Score'):
    """
    Detect outliers using Z-score or IQR method on a given column.
    Returns the DataFrame with an added boolean column 'is_outlier'.
    """
    if df.empty:
        print("DataFrame is empty, cannot detect outliers.")
        return df

    import numpy as np

    df = df.copy()

    if method == "Z-Score":
        from scipy import stats
        df['z_score'] = stats.zscore(df[column].astype(float))
        df['is_outlier'] = np.abs(df['z_score']) > threshold
        df.drop(columns=['z_score'], inplace=True)

    elif method == "IQR":
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        df['is_outlier'] = (df[column] < lower_bound) | (df[column] > upper_bound)

    else:
        print(f"Unsupported outlier detection method: {method}. Defaulting to no outliers.")
        df['is_outlier'] = False

    return df
