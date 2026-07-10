# Extract coins data and save it as a json file for transfroming 
import sys
import os
path = os.path.dirname(__file__)
full_path = os.path.join(path, 'sample_data.json')
sys.path.append('C:/Users/krish/OneDrive/Projects/crypto-etl-pipeline/src')
from extract import get_coin_data
import json

coins = get_coin_data()
with open(full_path, 'w') as file:
    json.dump(coins,file,indent=4)