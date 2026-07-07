CREATE TABLE IF NOT EXISTS dim_coins(
  coin_id VARCHAR(50) PRIMARY KEY,
  coin_symbol VARCHAR(50) NOT NULL,
  coin_name VARCHAR(50) NOT NULL,
  coin_adding_date TIMESTAMP NOT NULL DEFAULT NOW()
  );

CREATE TABLE IF NOT EXISTS fact_coin_price_snapshot(
  cp_id SERIAL PRIMARY KEY,
  coin_id VARCHAR(50) NOT NULL REFERENCES dim_coins(coin_id),
  coin_price_time TIMESTAMP NOT NULL,
  current_price FLOAT NOT NULL,
  market_cap FLOAT NOT NULL,
  market_cap_rank INT NOT NULL,
  total_trading_volume FLOAT NOT NULL,
  high_24 FLOAT NOT NULL,
  low_24 FLOAT NOT NULL,
  percent_change_24h FLOAT NOT NULL,
  all_time_high FLOAT NOT NULL,
  saved_date_time TIMESTAMP NOT NULL DEFAULT NOW(),
  circulating_supply FLOAT NOT NULL,
  UNIQUE (coin_id, coin_price_time)
  );

COMMENT ON TABLE dim_coins IS 'Basic coin details — one row per coin, rarely changes';
COMMENT ON TABLE fact_coin_price_snapshot IS 'Historical price snapshots, one row per coin per pipeline run';
