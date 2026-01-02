"""
Manual integration test to validate ETL logic outside Airflow
"""

from etl.extract import extract_products
from etl.transform import filter_expensive_products
from etl.load import save_to_csv

DATA_PATH = "data/products.csv"
OUTPUT_PATH = "data/filtered_products.csv"

df = extract_products(DATA_PATH)
filtered = filter_expensive_products(df)

print(filtered)
save_to_csv(filtered, OUTPUT_PATH)
print("Test completed successfully")