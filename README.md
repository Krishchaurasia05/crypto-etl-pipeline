# Crypto ETL Pipeline

An automated ETL pipeline that ingests cryptocurrency market data from the CoinGecko API and loads it into a cloud-hosted PostgreSQL database (Neon) on a scheduled basis, using GitHub Actions.

## Business Problem

Manually checking and recording cryptocurrency prices doesn't scale — analysts need a reliable system that automatically captures market data at regular intervals and stores it historically, enabling trend analysis, volatility tracking, and top gainers/losers reporting without manual effort.

## Architecture

```
CoinGecko API --> Extract (Python) --> Transform (Python) --> Load (PostgreSQL on Neon)
                                                                      ^
                                                        Scheduled by GitHub Actions (every 6 hours)
```

## Tech Stack

- **Python** — extraction, transformation, and loading logic
- **PostgreSQL (Neon)** — cloud-hosted, serverless database
- **GitHub Actions** — scheduled automation, no local machine required
- **CoinGecko API** — free, public, no-auth-required market data source

## Dataset

Top 5,000 cryptocurrencies by market cap, refreshed every 6 hours via the CoinGecko `/coins/markets` endpoint.

## Database Schema

Two tables:

- **`dim_coins`** — static coin metadata (id, symbol, name, date first tracked)
- **`fact_coin_price_snapshot`** — time-series price data (price, market cap, volume, 24h high/low, % change, circulating supply, ATH), one row per coin per pipeline run

See `sql/create_tables.sql` for the full schema.

## Installation

1. Clone this repository
2. Create a virtual environment and activate it
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your own Neon database connection details
5. Run the pipeline:
   ```
   python src/main.py
   ```

## Project Workflow

1. **Extract** — fetch current market data for top coins from CoinGecko
2. **Transform** — clean and reshape the raw API response into the database's column structure
3. **Load** — insert new coins into `dim_coins`, insert price snapshots into `fact_coin_price_snapshot`, skipping duplicates via a unique constraint

## Results / Insights

*(To be added once the pipeline has been running and enough historical data has accumulated.)*

## Future Improvements

- Add automated data quality checks
- Add a lightweight dashboard on top of the historical data
- Expand to hourly refresh once usage patterns justify a higher API tier

## Author

Krish Chaurasia — [GitHub](https://github.com/Krishchaurasia05) | [LinkedIn](https://linkedin.com/in/krishchaurasia)
