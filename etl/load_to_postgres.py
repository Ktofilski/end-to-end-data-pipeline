import os
import pandas as pd
from pymongo import MongoClient
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

#configuration

load_dotenv()

PG_HOST = os.getenv("POSTGRES_HOST")
PG_PORT = os.getenv("POSTGRES_PORT")
PG_DB = os.getenv("POSTGRES_DB")
PG_USER = os.getenv("POSTGRES_USER")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

# connect to mongodb

mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["crypto_db"]
collection = mongo_db["market_data"]

#extract from mongodb

documents = list(collection.find())

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

print(f"Prepared {len(df)} records from MongoDB")

#connect to postgresql

DATABASE_URL = (
    f"postgresql://{PG_USER}:{PG_PASSWORD}"
    f"@{PG_HOST}:{PG_PORT}/{PG_DB}"
)

engine = create_engine(DATABASE_URL)

# LOAD TO POSTGRESQL load to postgresql

insert_sql = text("""
    INSERT INTO crypto_market_snapshot (
        coin_id,
        symbol,
        name,
        current_price,
        market_cap,
        market_cap_rank,
        total_volume,
        price_change_percentage_24h,
        ingestion_time
    )
    VALUES (
        :coin_id,
        :symbol,
        :name,
        :current_price,
        :market_cap,
        :market_cap_rank,
        :total_volume,
        :price_change_percentage_24h,
        :ingestion_time
    )
    ON CONFLICT (coin_id, ingestion_time)
    DO NOTHING
""")

inserted_rows = 0

with engine.begin() as connection:

    for _, row in df.iterrows():

        result = connection.execute(
            insert_sql,
            row.to_dict()
        )

        inserted_rows += result.rowcount

print(f"Inserted {inserted_rows} new records into PostgreSQL")
print("Load completed successfully")