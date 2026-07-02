import sqlite3


def build_cache():
    conn = sqlite3.connect("retail.db")

    # Precompute answers to frequent questions so dashboards read a tiny
    # summary table instead of aggregating 392k rows on every request.
    # Rebuilt on every pipeline run, so the cache is never stale.

    # Cache 1: sales summary by country
    conn.execute("DROP TABLE IF EXISTS cache_sales_by_country")
    conn.execute("""
    CREATE TABLE cache_sales_by_country AS
    SELECT
        c.country,
        COUNT(*)                        AS num_sales,
        SUM(f.quantity)                 AS total_items,
        ROUND(SUM(f.quantity * f.unit_price), 2) AS total_revenue
    FROM fact_sales f
    JOIN dim_customers c ON f.customer_id = c.customer_id
    GROUP BY c.country
    """)

    # Cache 2: sales summary by month
    conn.execute("DROP TABLE IF EXISTS cache_sales_by_month")
    conn.execute("""
    CREATE TABLE cache_sales_by_month AS
    SELECT
        strftime('%Y-%m', invoice_date) AS month,
        COUNT(*)                        AS num_sales,
        SUM(quantity)                   AS total_items,
        ROUND(SUM(quantity * unit_price), 2) AS total_revenue
    FROM fact_sales
    GROUP BY month
    """)

    countries = conn.execute("SELECT COUNT(*) FROM cache_sales_by_country").fetchone()[0]
    months = conn.execute("SELECT COUNT(*) FROM cache_sales_by_month").fetchone()[0]

    conn.commit()
    conn.close()
    print(f"Cache built: sales by country ({countries} rows), sales by month ({months} rows)")


if __name__ == "__main__":
    build_cache()