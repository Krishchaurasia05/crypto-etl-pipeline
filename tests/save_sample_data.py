# Extract coins data and save it as a json file for transfroming 
import sys
import os


path = os.path.dirname(__file__)
full_path = os.path.join(path, 'sample_data.json')
project_root = os.path.dirname(path)
src_path = os.path.join(project_root, 'src')
sys.path.append(src_path)

from extract import get_coin_data
import json

coins = get_coin_data()
with open(full_path, 'w') as file:
    json.dump(coins,file,indent=4)