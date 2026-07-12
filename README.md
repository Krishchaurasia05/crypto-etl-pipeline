# Crypto ETL Pipeline

A fully working ETL pipeline that extracts live cryptocurrency market data from the CoinGecko API, transforms and validates it with pandas, and loads it into a cloud-hosted PostgreSQL database (Neon) — built end-to-end in Python.

## Business Problem

Manually checking and recording cryptocurrency prices doesn't scale. Analysts need a reliable system that automatically captures market data at regular intervals and stores it historically, enabling trend analysis, volatility tracking, and top gainers/losers reporting without manual effort.

## Architecture

```
CoinGecko API --> Extract (Python) --> Transform (pandas) --> Load (PostgreSQL on Neon)
                                                                      ^
                                                        Scheduled by GitHub Actions (planned)
```

The pipeline follows a strict Extract -> Transform -> Load separation, so each stage can be built, tested, and debugged independently:

- **`extract.py`** - Authenticates with the CoinGecko API and fetches paginated market data for the top 5,000 cryptocurrencies by market cap. Handles failed pages gracefully without halting the entire run.
- **`transform.py`** - Cleans raw API data using pandas: selects only relevant fields, renames them to match the database schema, converts timestamps to the correct type, and drops rows with incomplete 24h market data (logged, not silently discarded). Splits the result into two schema-ready DataFrames.
- **`load.py`** - Connects to PostgreSQL and inserts data into two tables, using `ON CONFLICT DO NOTHING` so the pipeline can safely re-run without creating duplicate data.
- **`main.py`** - Wires the three stages together into a single, runnable pipeline.

## Tech Stack

- **Python** - extraction, transformation, and loading logic
- **pandas** - data cleaning, validation, and reshaping
- **psycopg2** - PostgreSQL connectivity
- **PostgreSQL (Neon)** - cloud-hosted, serverless database
- **python-dotenv** - secure credential management (API keys and database credentials loaded from environment variables, never hardcoded)
- **CoinGecko API** - live market data source

## Dataset

Top 5,000 cryptocurrencies by market cap, refreshed via the CoinGecko `/coins/markets` endpoint (20 pages of 250 coins each).

## Database Schema

Two tables, following a dimension/fact design so coin metadata isn't repeated across every price snapshot:

- **`dim_coins`** - static coin metadata: `coin_id` (primary key), `coin_symbol`, `coin_name`, `coin_adding_date` (auto-filled on first insert)
- **`fact_coin_price_snapshot`** - time-series price data: current price, market cap, market cap rank, 24h high/low, 24h price and market cap change (absolute and percentage), circulating supply, all-time high, total trading volume, and the source timestamp (`coin_price_time`). A `UNIQUE(coin_id, coin_price_time)` constraint prevents duplicate snapshots.

See `sql/Table_creation.sql` and `sql/add_new_columns.sql` for the full schema.

## Installation

1. Clone this repository
2. Create and activate a virtual environment
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your own Neon database credentials and CoinGecko API key
5. Run the pipeline:
   ```
   python src/main.py
   ```

## Key Engineering Decisions

- **Capacity planning** - scope (top 5,000 coins, rather than all ~17,000) and refresh frequency were deliberately chosen based on the CoinGecko API's rate limits (100 calls/min, 10,000 calls/month), rather than arbitrarily.
- **Data quality over completeness** - rows with missing 24h market data (typically low-liquidity coins) are dropped and logged, rather than filled with misleading placeholder values.
- **Idempotent loads** - every insert uses `ON CONFLICT DO NOTHING`, so re-running the pipeline (including after a partial failure) never creates duplicate rows.
- **Separation of concerns** - extract, transform, and load are independent, individually testable functions with no hidden dependencies on each other's internals.

## Results

Verified end-to-end: ~4,640 coins successfully extracted, cleaned, and loaded into a live PostgreSQL database on Neon, with correct data types, referential integrity, and duplicate protection confirmed.

## Future Improvements

- Automate runs on a schedule using GitHub Actions
- Switch from row-by-row inserts to bulk inserts (`execute_values`) for significantly faster load times
- Add a lightweight dashboard on top of the accumulated historical data
- Add automated data quality checks and unit tests

## Author

Krish Chaurasia - [GitHub](https://github.com/Krishchaurasia05) | [LinkedIn](https://linkedin.com/in/krishchaurasia)
