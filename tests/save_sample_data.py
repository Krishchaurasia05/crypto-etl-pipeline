# Extract coins data and save it as a json file for transfroming 
import sys
sys.path.append('C:/Users/krish/Music/crypto-etl-pipeline/src')
from extract import get_coin_data
import json

coins = get_coin_data()
with open('sample_data.json', 'w') as file:
    json.dump(coins,file,indent=4)