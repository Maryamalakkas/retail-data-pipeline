import sqlite3


def create_indexes():
    conn = sqlite3.connect("retail.db")

    # Index on customer_id: speeds up "all sales of customer X" and joins
    conn.execute("""
    CREATE INDEX IF NOT EXISTS idx_sales_customer
    ON fact_sales (customer_id)
    """)

    # Index on stock_code: speeds up "all sales of product Y" and joins
    conn.execute("""
    CREATE INDEX IF NOT EXISTS idx_sales_product
    ON fact_sales (stock_code)
    """)

    # Index on invoice_date: speeds up date filters and monthly reports
    # (also our substitute for partitioning, which SQLite doesn't support)
    conn.execute("""
    CREATE INDEX IF NOT EXISTS idx_sales_date
    ON fact_sales (invoice_date)
    """)

    conn.commit()
    conn.close()
    print("Indexes created: customer_id, stock_code, invoice_date")


if __name__ == "__main__":
    create_indexes()




'''
With an index on customer_id, the database jumps straight to that customer's rows — no scanning. 
The trade-off (interview vocab alert): indexes cost a bit of disk space and slow down writes slightly
(every new row must also update the index page). 
Reads get faster, writes pay a small tax. 
In a warehouse, that trade is almost always worth it because warehouses are read-heavy.
'''