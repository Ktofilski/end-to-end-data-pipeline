import os
from pymongo import MongoClient
from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

PG_HOST = os.getenv("POSTGRES_HOST")
PG_PORT = os.getenv("POSTGRES_PORT")
PG_DB = os.getenv("POSTGRES_DB")
PG_USER = os.getenv("POSTGRES_USER")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

# Connect to MongoDB
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["crypto_db"]
collection = mongo_db["market_data"]

# Retrieve raw market data
documents = list(collection.find())

# Build an analytical dataset
records = []

for doc in documents:
    records.append({
        "coin_id": doc.get("id"),
        "symbol": doc.get("symbol"),
        "name": doc.get("name"),
        "current_price": doc.get("current_price"),
        "market_cap": doc.get("market_cap"),
        "market_cap_rank": doc.get("market_cap_rank"),
        "total_volume": doc.get("total_volume"),
        "price_change_percentage_24h": doc.get("price_change_percentage_24h"),
        "ingestion_time": doc.get("ingestion_time")
    })

df = pd.DataFrame(records)

print(f"Prepared {len(df)} records for loading.")

# Connect to PostgreSQL
DATABASE_URL = (
    f"postgresql://{PG_USER}:{PG_PASSWORD}"
    f"@{PG_HOST}:{PG_PORT}/{PG_DB}"
)

engine = create_engine(DATABASE_URL)

# Load data into the analytics layer
df.to_sql(
    "crypto_market_snapshot",
    engine,
    if_exists="append",
    index=False
)

print("Data successfully loaded into PostgreSQL.")