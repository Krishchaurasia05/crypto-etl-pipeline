"""
Description --

Entry point for the Crypto ETL Pipeline.

Runs the full pipeline in sequence:
1. Extract — fetches live market data for the top 5,000 cryptocurrencies
   from the CoinGecko API
2. Transform — cleans, validates, and reshapes the data into
   database-ready structures
3. Load — inserts the transformed data into PostgreSQL (Neon), safely
   handling duplicates on repeated runs

Run with: python src/main.py
"""



from extract import get_coin_data
from transform import transform_raw_data
from load import load_data

raw_data = get_coin_data()
print('Data extracted successfully')
dim_coins, fact_coin_price_snapshot = transform_raw_data(raw_data= raw_data)
print("Data Transformed successfully")
load_data(dim_coins=dim_coins,fact_coin_price_snapshot=fact_coin_price_snapshot)
print("Data Loaded successfully")