import sqlite3
from datetime import datetime

# Each check is a question to the database that should return 0
# if the answer is not 0, something broke our rules after cleaning
CHECKS = {
    "Missing customer_id in fact_sales":
        "SELECT COUNT(*) FROM fact_sales WHERE customer_id IS NULL",

    "Missing stock_code in fact_sales":
        "SELECT COUNT(*) FROM fact_sales WHERE stock_code IS NULL",

    "Quantity zero or negative":
        "SELECT COUNT(*) FROM fact_sales WHERE quantity <= 0",

    "Price zero or negative":
        "SELECT COUNT(*) FROM fact_sales WHERE unit_price <= 0",

    "Sales linked to unknown customer":
        """SELECT COUNT(*) FROM fact_sales
           WHERE customer_id NOT IN (SELECT customer_id FROM dim_customers)""",

    "Sales linked to unknown product":
        """SELECT COUNT(*) FROM fact_sales
           WHERE stock_code NOT IN (SELECT stock_code FROM dim_products)""",

    "Duplicate customers in dim_customers":
        """SELECT COUNT(*) - COUNT(DISTINCT customer_id) FROM dim_customers""",
}


def quality_check():
    conn = sqlite3.connect("retail.db")

    print("\n" + "-" * 50)
    print("Data Quality Report")
    print("-" * 50)

    # Row count sanity check first: an empty or tiny table means the load failed
    total_rows = conn.execute("SELECT COUNT(*) FROM fact_sales").fetchone()[0]
    print("Rows in fact_sales:", total_rows)

    all_passed = True
    log_lines = [f"\n--- Quality check run at {datetime.now()} ---"]
    log_lines.append(f"Rows in fact_sales: {total_rows}")

    for name, query in CHECKS.items():
        bad_rows = conn.execute(query).fetchone()[0]
        status = "Pass" if bad_rows == 0 else f"Fail ({bad_rows} rows affected)"
        print(f"{name}: {status}")
        log_lines.append(f"{name}: {status}")
        if bad_rows != 0:
            all_passed = False

    conn.close()

    # Append this run to the log file so quality is tracked over time
    with open("docs/quality_log.txt", "a") as log:
        log.write("\n".join(log_lines) + "\n")

    if all_passed:
        print("\nAll checks passed")
    else:
        print("\nAlert: some checks failed, see docs/quality_log.txt")


if __name__ == "__main__":
    quality_check()



'''

Quality monitoring = an inspector standing at the end of the pipeline.
Each check ends in PASS or FAIL, printed and saved with a timestamp — so quality is tracked over time
cleaning is a promise, monitoring is verification
That's what turns panic into a fixable incident.

'''