

'''

About Dataset
InvoiceNo: Invoice number. Nominal, a 6-digit integral number uniquely assigned to each transaction. If this code starts with letter 'c', it indicates a cancellation.
StockCode: Product (item) code. Nominal, a 5-digit integral number uniquely assigned to each distinct product.
Description: Product (item) name. Nominal.
Quantity: The quantities of each product (item) per transaction. Numeric.
InvoiceDate: Invice Date and time. Numeric, the day and time when each transaction was generated.
UnitPrice: Unit price. Numeric, Product price per unit in sterling.
CustomerID: Customer number. Nominal, a 5-digit integral number uniquely assigned to each customer.
Country: Country name. Nominal, the name of the country where each customer resides.

'''
import pandas as pd

# 1. Load the CSV into a DataFrame
df = pd.read_csv("data/raw/online_retail.csv")

print("\n" + "-" * 50)
print("Dataset Size (rows, columns)")
print("-" * 50)
print(df.shape)

print("\n" + "-" * 50)
print("First 5 Rows of the Dataset")
print("-" * 50)
print(df.head())

print("\n" + "-" * 50)
print("Column Names")
print("-" * 50)
print(df.columns.tolist())

print("\n" + "-" * 50)
print("Missing Values Check")
print("-" * 50)
print(df.isnull().sum())


print("\n" + "-" * 50)
print("What to clean in the dataset")
print("-" * 50)
print("Negative or zero Quantity:", (df["Quantity"] <= 0).sum())
print("Negative or zero UnitPrice:", (df["UnitPrice"] <= 0).sum())
print("Exact duplicate rows:", df.duplicated().sum())
print("Cancelled invoices (start with C):", df["InvoiceNo"].str.startswith("C").sum())


'''

What explore.py found in the raw data:

Problem                         Count      What it means
------------------------------- ---------- --------------------------------------
Missing CustomerID              135,080    Sales with no known buyer
Missing Description             1,454      Product rows with no name
Quantity <= 0                   10,624     Mostly returns/cancellations
UnitPrice <= 0                  2,517      Free items or data errors
Exact duplicates                5,268      Same row entered twice
Cancelled invoices ("C")        9,288      Returns, overlap with negative Quantity

'''