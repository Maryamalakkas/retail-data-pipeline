import pandas as pd

# What explore.py found in the raw data:
#
# Problem                         Count      What it means
# ------------------------------- ---------- --------------------------------------
# Missing CustomerID              135,080    Sales with no known buyer
# Missing Description             1,454      Product rows with no name
# Quantity <= 0                   10,624     Mostly returns/cancellations
# UnitPrice <= 0                  2,517      Free items or data errors
# Exact duplicates                5,268      Same row entered twice
# Cancelled invoices ("C")        9,288      Returns, overlap with negative Quantity


def clean():
    # Load the raw data
    df = pd.read_csv("data/raw/online_retail.csv")

    print("\n" + "-" * 50)
    print("Cleaning Receipt")
    print("-" * 50)
    print("Rows at start:", len(df))

    # remove exact duplicate rows
    df = df.drop_duplicates()
    print("After removing duplicates:", len(df))

    # remove rows with no CustomerID
    # the warehouse links every sale to a customer, so these rows can't be used
    df = df.dropna(subset=["CustomerID"])
    print("After removing missing CustomerID:", len(df))

    # keep only real sales (removing returns/cancellations )
    df = df[df["Quantity"] > 0]
    print("After removing Quantity <= 0:", len(df))

    # keep only rows with a real price (removing data errors as not a single product is free)
    df = df[df["UnitPrice"] > 0]
    print("After removing UnitPrice <= 0:", len(df))

    # fix data types
    # InvoiceDate is stored as text need to be converted to a real datetime
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

    # CustomerID is a label not a number that needs math, so make it a string
    # float -> int first to remove .0 in the float format-> then a string
    df["CustomerID"] = df["CustomerID"].astype(int).astype(str)

    # fill missing Descriptions using other rows of the same product
    # if StockCode = same product = same description
    df["Description"] = df.groupby("StockCode")["Description"].transform(
        lambda x: x.fillna(x.mode()[0]) if not x.mode().empty else x
    )
    print("Missing Descriptions left:", df["Description"].isnull().sum())

    # save the cleaned dataset to a new file
    df.to_csv("data/processed/online_retail_clean.csv", index=False)
    print("\nSaved to data/processed/online_retail_clean.csv")
    print("Final rows:", len(df))


'''
Note
pipeline run in this order: duplicates -> missing IDs -> invalid values.
'''

if __name__ == "__main__":
    clean()