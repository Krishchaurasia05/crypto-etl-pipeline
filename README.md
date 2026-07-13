# Crypto ETL Pipeline

A fully automated ETL pipeline that extracts live cryptocurrency market data from the CoinGecko API, cleans and validates it with pandas, and loads it into a cloud-hosted PostgreSQL database (Neon) — running on a schedule via GitHub Actions, with zero manual intervention.

![Status](https://img.shields.io/badge/status-complete-brightgreen) ![Python](https://img.shields.io/badge/python-3.12-blue) ![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-336791) ![Automation](https://img.shields.io/badge/automation-GitHub%20Actions-2088FF)

---

## Table of Contents

- [Overview](#overview)
- [Business Problem](#business-problem)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Dataset](#dataset)
- [Database Schema](#database-schema)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Automation](#automation)
- [Key Engineering Decisions](#key-engineering-decisions)
- [Results](#results)
- [Future Improvements](#future-improvements)
- [Author](#author)

---

## Overview

This project ingests market data for the top 5,000 cryptocurrencies on a recurring schedule, storing historical snapshots in a normalized PostgreSQL database. It follows a strict **Extract → Transform → Load** design, where each stage is an independently testable Python module with a single, well-defined responsibility.

The pipeline runs entirely unattended: GitHub Actions triggers it every 6 hours on a fresh virtual machine, authenticates securely using encrypted repository secrets, and writes to a cloud database — no local machine required.

## Business Problem

Manually checking and recording cryptocurrency prices doesn't scale. A reliable system needs to automatically capture market state at regular intervals and store it historically — the foundation for trend analysis, volatility tracking, and top gainers/losers reporting, without any manual effort.

## Architecture

```
CoinGecko API
      │
      ▼
 extract.py    — paginated fetch, per-page error handling, API key from .env
      │
      ▼
 transform.py  — pandas cleaning, type fixes, null handling, schema mapping
      │
      ▼
 load.py       — PostgreSQL inserts, ON CONFLICT DO NOTHING (idempotent)
      │
      ▼
 PostgreSQL (Neon)
      │
      ├── dim_coins                  (coin metadata)
      └── fact_coin_price_snapshot   (time-series price data)

Triggered every 6 hours by GitHub Actions (cron + workflow_dispatch)
Credentials injected via encrypted GitHub repository secrets
```

`main.py` orchestrates all three stages in sequence, and is the single entry point both for local runs and for the GitHub Actions workflow.

## Tech Stack

| Category | Tools |
|---|---|
| Language | Python 3.12 |
| Data processing | pandas |
| Database driver | psycopg2 |
| Database | PostgreSQL (hosted on Neon — serverless, free-tier) |
| Secrets management | python-dotenv (local), GitHub Actions repository secrets (CI/CD) |
| Automation | GitHub Actions (scheduled + manual triggers) |
| Data source | CoinGecko API (REST, Demo tier) |

## Dataset

Top 5,000 cryptocurrencies by market cap, fetched via the CoinGecko `/coins/markets` endpoint across 20 paginated requests (250 coins per page).

## Database Schema

A dimension/fact design, so coin metadata is never repeated across every price snapshot:

**`dim_coins`** — static coin metadata, one row per coin
| Column | Type | Notes |
|---|---|---|
| `coin_id` | `VARCHAR(50)` | Primary key |
| `coin_symbol` | `VARCHAR(50)` | e.g. `btc` |
| `coin_name` | `VARCHAR(50)` | e.g. `Bitcoin` |
| `coin_adding_date` | `TIMESTAMP` | Auto-filled (`DEFAULT NOW()`) on first insert |

**`fact_coin_price_snapshot`** — time-series price data, grows every run
| Column | Type | Notes |
|---|---|---|
| `cp_id` | `SERIAL` | Primary key |
| `coin_id` | `VARCHAR(50)` | Foreign key → `dim_coins(coin_id)` |
| `coin_price_time` | `TIMESTAMP` | Source timestamp from CoinGecko (`last_updated`) |
| `current_price`, `market_cap`, `market_cap_rank`, `total_trading_volume`, `high_24`, `low_24`, `price_change_24h`, `price_percent_change_24h`, `market_cap_change_24h`, `market_cap_change_percentage_24h`, `circulating_supply`, `all_time_high` | `FLOAT` / `INT` | Market data fields |
| `saved_date_time` | `TIMESTAMP` | Auto-filled with pipeline run time (`DEFAULT NOW()`) |

A `UNIQUE(coin_id, coin_price_time)` constraint on the fact table prevents duplicate snapshots on repeated or retried runs.

Full DDL: [`sql/Table_creation.sql`](sql/Table_creation.sql), [`sql/add_new_columns.sql`](sql/add_new_columns.sql)

## Project Structure

```
crypto-etl-pipeline/
├── .github/
│   └── workflows/
│       └── pipeline.yml       # GitHub Actions schedule + manual trigger
├── sql/
│   ├── Table_creation.sql
│   └── add_new_columns.sql
├── src/
│   ├── extract.py             # CoinGecko API extraction
│   ├── transform.py           # pandas cleaning + schema mapping
│   ├── load.py                # PostgreSQL loading
│   └── main.py                # Pipeline orchestration (entry point)
├── tests/
│   └── save_sample_data.py    # Dev helper — saves a sample API response for offline transform testing
├── .env.example                # Template for required environment variables
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/Krishchaurasia05/crypto-etl-pipeline.git
   cd crypto-etl-pipeline
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # macOS/Linux
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your own credentials:
   ```
   DB_HOST=your-neon-host
   DB_NAME=your-database-name
   DB_USER=your-username
   DB_PASSWORD=your-password
   COINGECKO_API_KEY=your-coingecko-demo-api-key
   ```

## Usage

Run the full pipeline locally:
```bash
python src/main.py
```

This executes Extract → Transform → Load in sequence, printing status at each stage and inserting/updating data in your configured PostgreSQL database.

## Automation

The pipeline runs automatically via **GitHub Actions**, defined in [`.github/workflows/pipeline.yml`](.github/workflows/pipeline.yml):

- **Schedule:** every 6 hours (`cron: '0 */6 * * *'`)
- **Manual trigger:** available on-demand via the Actions tab (`workflow_dispatch`)
- **Environment:** a fresh Ubuntu runner each time — checks out the repo, installs Python and dependencies, then runs `python src/main.py`
- **Secrets:** database credentials and the API key are stored as encrypted GitHub repository secrets and injected as environment variables at runtime — never exposed in code or logs

**An interesting finding from testing this:** the identical pipeline took ~45 minutes to run on a local machine, but only ~4 minutes on GitHub Actions' runners. The most likely explanation is network proximity — GitHub's infrastructure and the Neon database both sit in well-connected cloud environments, while a home connection reaching a US-hosted database over thousands of individual insert round-trips adds significant cumulative latency.

## Key Engineering Decisions

- **Capacity planning, not guesswork** — the scope (top 5,000 coins, 6-hour refresh) was chosen by calculating actual API call usage against CoinGecko's rate limits (100 calls/min, 10,000 calls/month), rather than picking arbitrary numbers.
- **Data quality over blind completeness** — rows with missing 24h market data (typically low-liquidity coins) are dropped and logged with a count, rather than filled with misleading placeholder values like `0`.
- **Idempotent by design** — every insert uses `ON CONFLICT DO NOTHING`, so the pipeline can be safely re-run, retried, or scheduled repeatedly without ever creating duplicate rows.
- **Separation of concerns** — extract, transform, and load are independent, single-responsibility functions with no hidden dependencies on each other's internals, making each one independently testable.
- **Secrets never touch source control** — API keys and database credentials are loaded from environment variables locally (`.env`, git-ignored) and from encrypted secrets in CI (GitHub Actions), with zero credentials ever committed to the repository.

## Results

Verified end-to-end in production: ~4,640 coins successfully extracted, validated, and loaded into a live PostgreSQL database on Neon on a recurring automated schedule, with correct data types, referential integrity, and duplicate protection confirmed across multiple runs.

## Future Improvements

- Replace row-by-row inserts with bulk inserts (`psycopg2.extras.execute_values`) to significantly reduce load time
- Add a lightweight dashboard on top of the accumulated historical data
- Add automated data quality checks and unit tests
- Add failure alerting for scheduled runs (e.g., notification on workflow failure)

## Author

**Krish Chaurasia**
[GitHub](https://github.com/Krishchaurasia05) · [LinkedIn](https://linkedin.com/in/krishchaurasia)
