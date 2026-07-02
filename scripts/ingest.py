import sqlite3
import pandas as pd


def ingest():
    # Load the cleaned data (never the raw file)
    df = pd.read_csv("data/processed/online_retail_clean.csv")

    # Connect to the database
    # (this creates the file retail.db the first time we run it)
    conn = sqlite3.connect("retail.db")

    # Create the three tables of the star schema
    # dim_customers: one row per customer (the customer register)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS dim_customers (
        customer_id TEXT PRIMARY KEY,
        country     TEXT
    )
    """)

    # dim_products: one row per product (the product catalog)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS dim_products (
        stock_code  TEXT PRIMARY KEY,
        description TEXT,
        unit_price  REAL
    )
    """)

    # fact_sales: one row per sale line (the events notebook)
    # customer_id and stock_code are links to the two tables above
    conn.execute("""
    CREATE TABLE IF NOT EXISTS fact_sales (
        invoice_no   TEXT,
        invoice_date TEXT,
        customer_id  TEXT REFERENCES dim_customers(customer_id),
        stock_code   TEXT REFERENCES dim_products(stock_code),
        quantity     INTEGER,
        unit_price   REAL
    )
    """)

    print("\n" + "-" * 50)
    print("Ingestion Receipt")
    print("-" * 50)

    # Build dim_customers: keep one row per customer
    customers = df[["CustomerID", "Country"]].drop_duplicates(subset=["CustomerID"])
    customers.columns = ["customer_id", "country"]
    customers.to_sql("dim_customers", conn, if_exists="replace", index=False)
    print("Customers loaded:", len(customers))

    # Build dim_products: keep one row per product
    products = df[["StockCode", "Description", "UnitPrice"]].drop_duplicates(subset=["StockCode"])
    products.columns = ["stock_code", "description", "unit_price"]
    products.to_sql("dim_products", conn, if_exists="replace", index=False)
    print("Products loaded:", len(products))

    # Build fact_sales: every sale line, with links to the two catalogs
    sales = df[["InvoiceNo", "InvoiceDate", "CustomerID", "StockCode", "Quantity", "UnitPrice"]]
    sales.columns = ["invoice_no", "invoice_date", "customer_id", "stock_code", "quantity", "unit_price"]
    sales.to_sql("fact_sales", conn, if_exists="replace", index=False)
    print("Sales loaded:", len(sales))

    conn.close()
    print("\nDone, database saved as retail.db")


if __name__ == "__main__":
    ingest()