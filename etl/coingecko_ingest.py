import os
import requests
import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime, timezone

#load env variables

load_dotenv()

API_KEY = os.getenv("COINGECKO_API_KEY")

if not API_KEY:
    raise ValueError("Missing COINGECKO_API_KEY in .env file")


#api config

url = "https://api.coingecko.com/api/v3/coins/markets"

headers = {
    "x-cg-demo-api-key": API_KEY
}

params = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 50,
    "page": 1,
    "sparkline": False
}

#extract data

response = requests.get(url, params=params, headers=headers)

if response.status_code != 200:
    raise Exception(f"API request failed: {response.status_code} - {response.text}")

data = response.json()


#transform data

df = pd.DataFrame(data)

# remove problematic nested columns
df = df.drop(columns=["roi"], errors="ignore")

# remove duplicates
df = df.drop_duplicates(subset=["id"])

# add ingestion timestamp
df["ingestion_time"] = datetime.now(timezone.utc)

print(f"Fetched {len(df)} records")

#load to mongodb
client = MongoClient("mongodb://localhost:27017/")

db = client["crypto_db"]
collection = db["market_data"]

records = df.to_dict(orient="records")

if records:
    collection.insert_many(records)
    print("Data successfully inserted into MongoDB 🚀")
else:
    print("No data to insert")