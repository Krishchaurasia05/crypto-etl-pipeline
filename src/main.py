from extract import get_coin_data
from transform import transform_raw_data
from load import load_data

raw_data = get_coin_data()

dim_coins, fact_coin_price_snapshot = transform_raw_data(raw_data= raw_data)

load_data(dim_coins=dim_coins,fact_coin_price_snapshot=fact_coin_price_snapshot)
