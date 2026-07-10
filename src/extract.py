"""
Description ---

This file handles data extraction from the CoinGecko API for the Crypto ETL Pipeline.

Responsible for:
- Authenticating requests using an API key loaded from environment variables
- Fetching paginated market data for the top 5,000 cryptocurrencies by market cap
- Gracefully handling failed page requests without halting the entire extraction

This module only retrieves raw data — no cleaning, transformation, or database
logic happens here. See transform.py and load.py for those responsibilities.
"""


import requests
import time 
import os
import dotenv

dotenv.load_dotenv()
coingecko_url = 'https://api.coingecko.com/api/v3/coins/markets'
api_key = os.getenv('COINGECKO_API_KEY')

def get_coin_data():
    """
    Fetches market data for the top 5,000 cryptocurrencies from the CoinGecko,
    paginated across 20 pages of 250 coins each.

    Returns:
        list[dict]: A flat list of coin data dictionaries, one per coin.
        If a specific page fails to fetch, it is skipped and logged;
        the function still returns all successfully retrieved coins.
    """
    all_coins = []
    for page in range(1,21):
        parameters ={ 
        'vs_currency' : 'usd',
        'order' : 'market_cap_desc',
        'per_page' : '250',
        'page' : F'{page}',
        'x_cg_demo_api_key' : api_key
        }

        responce = requests.get(coingecko_url, params= parameters)
        if responce.status_code == 200:
            all_coins.extend(responce.json())
        else:
            print(f"Something went wrong on page {page}")
            continue
        time.sleep(1)
    return all_coins
