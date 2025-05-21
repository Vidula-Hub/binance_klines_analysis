from pymongo import MongoClient
import os

def save_to_mongo(dataframe, db_name="binance_data", collection_name="btc_klines"):
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]  # Use the collection_name param here
    collection.delete_many({})
    collection.insert_many(dataframe.to_dict("records"))