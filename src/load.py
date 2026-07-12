"""
Description--

Handles loading transformed data into the PostgreSQL database (Neon) for
the Crypto ETL Pipeline.

Responsible for:
- Connecting securely to PostgreSQL using credentials from environment
  variables
- Inserting coin metadata into dim_coins and price snapshots into
  fact_coin_price_snapshot
- Preventing duplicate data on repeated runs using ON CONFLICT DO NOTHING
- Rolling back cleanly if either insert fails, without affecting
  already-committed data

This module does not fetch or clean data — it assumes it has already been
prepared correctly by extract.py and transform.py.
"""


import psycopg2 
import os
import sys
import dotenv

def load_data(dim_coins, fact_coin_price_snapshot ):
    '''
    Loads cleaned coin data into the PostgreSQL database.

    Inserts rows into dim_coins and fact_coin_price_snapshot using a single
    shared connection. Each table's insert is committed independently, so a
    failure in one does not roll back data already committed for the other.
    Duplicate coins or duplicate price snapshots (same coin_id and
    coin_price_time) are silently skipped rather than raised as errors.

    Args:
        dim_coins (pd.DataFrame): Coin metadata — coin_id, coin_symbol,
            coin_name.
        fact_coin_price_snapshot (pd.DataFrame): Price/market snapshot data,
            including coin_id and coin_price_time.

    Returns:
        None. Prints status messages indicating success or failure for
        each stage (connection, dim_coins insert, fact table insert).
    '''
    dotenv.load_dotenv()

    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')
    db_password = os.getenv('DB_PASSWORD')
    db_user = os.getenv('DB_USER')

    try:
        conn = psycopg2.connect(database= db_name, user= db_user, host= db_host, password= db_password)
        print('Database connected Successfully')

        try:
            cur = conn.cursor()
            for _,row in dim_coins.iterrows():
                cur.execute("INSERT INTO dim_coins(coin_id,coin_name,coin_symbol) VALUES(%s,%s,%s)\
                            ON CONFLICT (coin_id) DO NOTHING",
                            (row['coin_id'],row['coin_name'],row['coin_symbol']))
            conn.commit()
            cur.close()
            print('Data inserted in dim_coins successfully')
            
        except Exception as e:
            print(f"Error inserting data: {e}")
            conn.rollback()

        try:
            cur = conn.cursor()

            for _,row in fact_coin_price_snapshot.iterrows():
                cur.execute("INSERT INTO fact_coin_price_snapshot(coin_id,current_price,market_cap,\
                            market_cap_rank,high_24,low_24,price_change_24h,price_percent_change_24h,\
                            market_cap_change_24h,market_cap_change_percentage_24h,circulating_supply,\
                            all_time_high,coin_price_time,total_trading_volume)\
                            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)\
                            ON CONFLICT (coin_id, coin_price_time) DO NOTHING",
                            (row['coin_id'],
                            row['current_price'],
                            row['market_cap'],
                            row['market_cap_rank'],
                            row['high_24'],
                            row['low_24'],
                            row['price_change_24h'],
                            row['price_percent_change_24h'],
                            row['market_cap_change_24h'],
                            row['market_cap_change_percentage_24h'],
                            row['circulating_supply'],
                            row['all_time_high'],
                            row['coin_price_time'],
                            row['total_trading_volume']))
            conn.commit()
            print("Data insertes in fact_coin_price_snapshot Successfully")
            cur.close()


        except Exception as e:
            print(f"Error inserting data: {e}")
            conn.rollback()
        conn.close()
        print('Data inserted successfully')

    except Exception as e:
        print(f'Error While connecting Database {e}')


    return 