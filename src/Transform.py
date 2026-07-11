import pandas as pd
import os
import sys
import json
'''
===================================================================================================
    Changing Path to load data
===================================================================================================
'''
src_folder = os.path.dirname(__file__)
project_root = os.path.dirname(src_folder)
test_folder = os.path.join(project_root,'tests')
sample_data = os.path.join(test_folder,'sample_data.json')
sys.path.append(sample_data)
'''
===================================================================================================
    Loading Data
===================================================================================================
'''
#
with open(sample_data) as file:
    data = json.load(file)

'''
===================================================================================================
    Converting it into Dataframe to transform
===================================================================================================
'''

data = pd.DataFrame(data)

'''
===================================================================================================
    Filtering out columns
===================================================================================================
'''

filetr_columns = ['id','symbol','name','current_price','market_cap','market_cap_rank','high_24h',
                  'low_24h','price_change_24h','price_change_percentage_24h','market_cap_change_24h',
                  'market_cap_change_percentage_24h','circulating_supply','ath','last_updated']

usefull_data = data[filetr_columns]

'''
===================================================================================================
    Changing Column names as per our schema 
===================================================================================================
'''


rename_columns = {
    'id': 'coin_id',
    'symbol': 'coin_symbol',
    'name' : 'coin_name',
    'ath' : 'all_time_high',
    'high_24h': 'high_24',
    'low_24h': 'low_24',
    'last_updated': 'coin_price_time'
}

usefull_data.rename(columns=rename_columns,inplace=True)

'''
===================================================================================================
    Handling Null values 
===================================================================================================
'''
 
missing_values_columns = ['high_24','low_24','price_change_24h','price_change_percentage_24h',
                          'market_cap_change_24h','market_cap_change_percentage_24h']

usefull_data = usefull_data.dropna(subset=missing_values_columns)

