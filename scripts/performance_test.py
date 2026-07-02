import sqlite3
import time


def time_query(conn, label):
    # The test question: total items bought by one customer
    query = """
    SELECT SUM(quantity)
    FROM fact_sales
    WHERE customer_id = '17850'
    """

    # Ask the database HOW it plans to answer (scan vs index)
    plan = conn.execute("EXPLAIN QUERY PLAN " + query).fetchall()
    print("Plan:", plan[0][3])

    # Stopwatch: run the query 100 times and measure the total
    start = time.perf_counter()
    for _ in range(100):
        conn.execute(query).fetchone()
    elapsed = time.perf_counter() - start
    print(label, "->", round(elapsed * 1000, 1), "ms for 100 runs\n")


def run_test():
    conn = sqlite3.connect("retail.db")

    print("\n" + "-" * 50)
    print("Performance Test: query with vs without index")
    print("-" * 50 + "\n")

    # Round 1: indexes exist (created by optimize.py)
    time_query(conn, "With index")

    # Round 2: drop the customer index and ask the same question
    conn.execute("DROP INDEX IF EXISTS idx_sales_customer")
    conn.commit()
    conn.close()

    # Fresh connection so the query plan is re-evaluated honestly
    conn = sqlite3.connect("retail.db")
    time_query(conn, "Without index")

    # Put the index back so the database stays optimized
    conn.execute("""
    CREATE INDEX IF NOT EXISTS idx_sales_customer
    ON fact_sales (customer_id)
    """)
    conn.commit()
    conn.close()
    print("Index restored, database back to optimized state")


if __name__ == "__main__":
    run_test()