# Online Retail Sales Data Engineering

An end-to-end data pipeline built for a data engineering assessment.
It takes a raw online retail dataset and turns it into a small data
warehouse with automated cleaning, loading, quality checks, versioning
and metadata.

Built with Python, pandas and SQLite.

## How to run

1. Create and activate a virtual environment:

       python3 -m venv venv
       source venv/bin/activate

2. Install the dependencies:

       pip install -r requirements.txt

3. Run the full pipeline:

       python scripts/etl_pipeline.py

The dataset is included in data/raw/ so the project runs out of the
box. In a real production project, data files would live outside git
(in object storage or a database). They are included here so the
reviewer can run everything without downloading anything.

## Project structure
'

    Nesma_2/
    ├── data/
    │   ├── raw/                  original dataset, never modified
    │   ├── processed/            cleaned output of the pipeline
    │   └── archive/              timestamped snapshots (created by the pipeline)
    ├── scripts/
    │   ├── explore.py            investigation tool (not part of the pipeline)
    │   ├── performance_test.py   proves the index speedup (not part of the pipeline)
    │   ├── clean.py              extract + transform
    │   ├── ingest.py             load into the warehouse
    │   ├── optimize.py           indexes
    │   ├── quality_check.py      data quality checks
    │   ├── versioning.py         dataset snapshots
    │   ├── metadata.py           metadata table refresh
    │   ├── caching.py            cached summary tables for frequent queries
    │   └── etl_pipeline.py       runs all pipeline steps in order
    ├── docs/
    │   ├── scheduling.md         how the pipeline is scheduled with cron
    │   └── quality_log.txt       history of quality check runs
    ├── requirements.txt
    └── README.md

'
explore.py and performance_test.py are tools a human runs once to
investigate and to measure. The other scripts are the pipeline itself.

## The data and how it was cleaned

Source: an online retail transactions dataset with 541,909 rows and
8 columns (invoices, products, quantities, prices, customers,
countries).

I explored the data first (explore.py) to measure the problems before
deciding how to fix them. The cleaning then runs in this order:

| Step | Rows removed | Reason |
|------|--------------|--------|
| Exact duplicates | 5,268 | Same row entered twice |
| Missing CustomerID | 135,037 | The warehouse links every sale to a customer, so rows without one cannot be used |
| Quantity <= 0 | 8,872 | Returns and cancellations, out of scope for a sales warehouse |
| UnitPrice <= 0 | 40 | Data errors, a sale with no price adds nothing to revenue analysis |

Final result: 392,692 clean rows.

The order of the steps matters. Some rows have more than one problem,
so a different order gives different counts. The pipeline fixes the
order: duplicates first, then missing IDs, then invalid values.

Type fixes:
- InvoiceDate was stored as text and is converted to a real datetime,
  so the warehouse can filter and group by time.
- CustomerID was a float (17850.0). An ID is a label, not a number
  used for math, so it is converted float to int to string.
- Missing product descriptions are filled from other rows with the
  same StockCode (same product, same description).

The raw file is never modified. The cleaned data is saved as a new
file in data/processed/.

## Warehouse design: star schema

The clean data is loaded into SQLite (retail.db) as a star schema:
two dimension tables that describe things, and one fact table that
records events.

    dim_customers                dim_products
    ├── customer_id (PK)         ├── stock_code (PK)
    └── country                  ├── description
              \                  └── unit_price
               \                /
                fact_sales
                ├── invoice_no
                ├── invoice_date
                ├── customer_id (FK)
                ├── stock_code (FK)
                ├── quantity
                └── unit_price

Loaded counts: 4,338 customers, 3,665 products, 392,692 sales rows.

unit_price appears in both dim_products and fact_sales on purpose.
The product table holds the current catalog price, while the fact row
freezes the price at the moment of sale. If prices change later, the
sales history stays correct.

## ETL pipeline

One command runs the whole chain:

    clean -> ingest -> indexes -> quality check -> archive -> metadata -> cache

Each step prints a receipt with row counts, so every run can be
audited. Scheduling is documented in docs/scheduling.md (cron, daily
at 02:00, with all output appended to a log file).

## Partitioning and indexing

fact_sales has indexes on customer_id, stock_code and invoice_date.
These are the columns used for filtering and joins, so they are the
ones that benefit from an index.

I measured the effect with performance_test.py, using EXPLAIN QUERY
PLAN and timing the same query 100 times with and without the index:

    With index:    SEARCH fact_sales USING INDEX   ->    8.3 ms
    Without index: SCAN fact_sales                 -> 2784.4 ms

That is roughly a 335x speedup from one index.

SQLite does not support table partitioning. In production (for
example PostgreSQL) fact_sales would be partitioned by month on
invoice_date. The index on invoice_date serves that purpose here.

## Caching

Some questions get asked constantly, like sales by country or revenue
per month. Answering them directly means scanning and aggregating all
392,692 fact rows every time, even though the answer only changes when
new data is loaded.

caching.py precomputes these answers once per pipeline run and stores
them as small summary tables:

    cache_sales_by_country    one row per country (sales, items, revenue)
    cache_sales_by_month      one row per month (sales, items, revenue)

A dashboard reads a table of a few dozen rows instead of aggregating
392k. The cache is rebuilt at the end of every pipeline run, so it can
never go stale: the underlying data only changes when the pipeline
runs. This is the same idea as a materialized view in a production
warehouse.

The trade-off of any cache is freshness against speed. Here the
refresh is tied to the load, which removes the staleness problem
entirely.

## Data quality monitoring

quality_check.py runs 7 checks against the database after every load:
missing keys, invalid quantities and prices, sales linked to unknown
customers or products, and duplicate rows in the dimensions.

Results are printed and appended with a timestamp to
docs/quality_log.txt, so quality is tracked over time. The checks run
against the database, not the CSV, because data can change after
cleaning. Cleaning is a promise, monitoring verifies it.

In production, a failed check would send an alert (email or Slack)
instead of a log line.

## Data versioning

Every pipeline run copies the cleaned dataset into data/archive/ with
a timestamp in the filename, for example:

    online_retail_clean_2026-07-02_12-32.csv

Old versions are never overwritten, so it is always possible to see
what the data looked like on a given day. The archive folder is not
pushed to git because it grows with every run.

## Metadata management

The warehouse contains a metadata table that documents every other
table: description, source, transformations applied, row count and
last update time. It is refreshed by the pipeline on every run, so
the database documents itself. This records the lineage from raw CSV
to warehouse.

## Possible improvements

- Move to PostgreSQL for real partitioning and concurrent access
- Replace cron with Airflow for retries and alerts on failure
- Load new data incrementally instead of replacing the tables
- Send quality alerts to email or Slack instead of a log file
- Add unit tests for the cleaning rules
