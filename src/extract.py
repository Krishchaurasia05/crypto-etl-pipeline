
import requests
import time 
import os
import dotenv

dotenv.load_dotenv()
coingecko_url = 'https://api.coingecko.com/api/v3/coins/markets'
api_key = os.getenv('COINGECKO_API_KEY')

def get_coin_data():
    '''
    Getting the coins data from CoinGecko
    250 per page 
    Total Number of pages - 20 
    Total coins - 5000
    '''
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
