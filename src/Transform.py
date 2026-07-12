"""
Description --

Handles data transformation for the Crypto ETL Pipeline.

Responsible for:
- Cleaning raw CoinGecko API data (selecting relevant fields, dropping
  incomplete rows, fixing data types)
- Renaming fields to match the PostgreSQL database schema
- Splitting cleaned data into two structures: dim_coins (coin metadata)
  and fact_coin_price_snapshot (time-series price/market data)

This module does not call the API or interact with the database directly.
See extract.py for data retrieval and load.py for database insertion.
"""



import pandas as pd
import os
import json

def transform_raw_data(raw_data):
    """
    Cleans and reshapes raw coin market data into two schema-ready DataFrames.

    Steps performed:
    - Selects only the fields required by the database schema
    - Renames fields to match column names in dim_coins and
      fact_coin_price_snapshot
    - Converts coin_price_time to a timezone-naive datetime
    - Drops rows with missing 24h market data (logged, not silently discarded)
    - Splits the cleaned data into coin metadata vs. price snapshot data

    Args:
        raw_data (list[dict]): Raw coin data, as returned by
            extract.get_coin_data().

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: (dim_coins, fact_coin_price_snapshot)
    """
    
    '''
    ===================================================================================================
        Converting it into Dataframe to transform
    ===================================================================================================
    '''

    full_raw_data = pd.DataFrame(raw_data)

    '''
    ===================================================================================================
        Filtering out columns
    ===================================================================================================
    '''

    filetr_columns = ['id','symbol','name','current_price','market_cap','market_cap_rank','high_24h',
                    'low_24h','price_change_24h','price_change_percentage_24h','market_cap_change_24h',
                    'market_cap_change_percentage_24h','circulating_supply','ath','last_updated',
                    'total_volume']

    usefull_data = full_raw_data[filetr_columns].copy()

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
