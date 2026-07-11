import pandas as pd
import os
import json

def transform_raw_data(raw_data):

    '''
    ===================================================================================================
        Converting it into Dataframe to transform
    ===================================================================================================
    '''

    raw_data = pd.DataFrame(raw_data)

    '''
    ===================================================================================================
        Filtering out columns
    ===================================================================================================
    '''

    filetr_columns = ['id','symbol','name','current_price','market_cap','market_cap_rank','high_24h',
                    'low_24h','price_change_24h','price_change_percentage_24h','market_cap_change_24h',
                    'market_cap_change_percentage_24h','circulating_supply','ath','last_updated',
                    'total_volume']

    usefull_data = raw_data[filetr_columns].copy()

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
        'last_updated': 'coin_price_time',
        'price_change_percentage_24h':'price_percent_change_24h',
        'total_volume':'total_trading_volume'
    }

    usefull_data.rename(columns=rename_columns,inplace=True)

    '''
    ===================================================================================================
        Changing Data type
    ===================================================================================================
    '''
    usefull_data['coin_price_time'] = pd.to_datetime(usefull_data['coin_price_time'])
    usefull_data['coin_price_time'] = usefull_data['coin_price_time'].dt.tz_localize(None)

    '''
    ===================================================================================================
        Handling Null values 
    ===================================================================================================
    '''
    
    missing_values_columns = ['high_24','low_24','price_change_24h','price_percent_change_24h',
                            'market_cap_change_24h','market_cap_change_percentage_24h',
                            'total_trading_volume']
    missing_value_count = usefull_data[missing_values_columns].isnull().any(axis=1).sum()

    usefull_data = usefull_data.dropna(subset=missing_values_columns).copy()

    print(f'Dropping {missing_value_count} rows due to 24h missing data')
    print(f"Remaining rows: {len(usefull_data)}")

    '''
    ===================================================================================================
        Creating two dataframes as requied
    ===================================================================================================
    '''
    dim_coins_columns = ['coin_id','coin_name','coin_symbol']
    dim_coins = usefull_data[dim_coins_columns].copy()

    fact_coin_columns = ['coin_id','current_price','market_cap','market_cap_rank','high_24','low_24',
                        'price_change_24h','price_percent_change_24h','market_cap_change_24h',
                        'market_cap_change_percentage_24h','circulating_supply','all_time_high',
                        'coin_price_time','total_trading_volume']

    fact_coin_price_snapshot = usefull_data[fact_coin_columns].copy()

    return dim_coins, fact_coin_price_snapshot
