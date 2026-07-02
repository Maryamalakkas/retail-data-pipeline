import sqlite3
from datetime import datetime


def update_metadata():
    conn = sqlite3.connect("retail.db")

    # One row per table in the warehouse: what it is, where it came from,
    # what was done to it, and when it was last loaded
    conn.execute("""
    CREATE TABLE IF NOT EXISTS metadata (
        table_name      TEXT PRIMARY KEY,
        description     TEXT,
        source          TEXT,
        transformations TEXT,
        row_count       INTEGER,
        last_updated    TEXT
    )
    """)

    now = str(datetime.now())

    tables = [
        ("dim_customers",
         "One row per customer (customer register)",
         "data/raw/online_retail.csv -> data/processed/online_retail_clean.csv",
         "Deduplicated by CustomerID, ID converted float -> int -> string",
         "SELECT COUNT(*) FROM dim_customers"),

        ("dim_products",
         "One row per product (product catalog)",
         "data/raw/online_retail.csv -> data/processed/online_retail_clean.csv",
         "Deduplicated by StockCode, missing descriptions filled from same product",
         "SELECT COUNT(*) FROM dim_products"),

        ("fact_sales",
         "One row per sale line (center of the star schema)",
         "data/raw/online_retail.csv -> data/processed/online_retail_clean.csv",
         "Removed duplicates, missing CustomerID, quantity <= 0, price <= 0",
         "SELECT COUNT(*) FROM fact_sales"),
    ]

    for name, description, source, transformations, count_query in tables:
        row_count = conn.execute(count_query).fetchone()[0]
        conn.execute("""
        INSERT OR REPLACE INTO metadata VALUES (?, ?, ?, ?, ?, ?)
        """, (name, description, source, transformations, row_count, now))

    conn.commit()
    conn.close()
    print("Metadata updated for 3 tables")


if __name__ == "__main__":
    update_metadata()