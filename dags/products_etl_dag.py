from airflow import DAG
from airflow.operators.python import PythonOperator
import logging
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine

DATA_PATH = "/opt/airflow/data/products.csv"  # CSV location

# Postgres connection string
POSTGRES_CONN = "postgresql+psycopg2://airflow:airflow@postgres:5432/airflow"

def extract():
    # Read CSV into pandas dataframe
    df = pd.read_csv(DATA_PATH, sep=r'\s+', skipinitialspace=True)
    return df


def transform(ti):
    # Pull data from extract task
    df = ti.xcom_pull(task_ids="extract")
    
    # Filter rows where price > 100
    filtered_df = df[df['price'] > 100]

    # Strip commas in name and category
    for col in ['name', 'category']:
        filtered_df[col] = filtered_df[col].str.strip(', ')

    # Push filtered data as dictionary to XCom
    ti.xcom_push(key='filtered_df', value=filtered_df.to_dict(orient='records'))


def load(ti):
    # Pull filtered data from transform task
    filtered_data = ti.xcom_pull(task_ids="transform", key='filtered_df')
    df = pd.DataFrame(filtered_data)

    # Write filtered dataframe to Postgres
    engine = create_engine(POSTGRES_CONN)
    df.to_sql("products_filtered", engine, if_exists="replace", index=False)  # creates table if missing

   # Calculate average price
    average_price = df['price'].mean()

    # Log average price and items using logging (better than print for Airflow)
    logging.info(f"Average price of items > 100: {average_price:.2f}")
    logging.info(f"Items with price > 100: {df['name'].tolist()}")

    # Optional: store average in a separate table for queries
    avg_df = pd.DataFrame([{"metric": "average_price", "value": average_price}])
    avg_df.to_sql("products_metrics", engine, if_exists="replace", index=False)

# Define DAG
with DAG(
    dag_id="products_etl_pipeline",
    start_date=datetime(2026, 1, 2),
    schedule="@daily",
    catchup=False,
    tags=["etl", "products"]
) as dag:

    extract_task = PythonOperator(task_id="extract", python_callable=extract)
    transform_task = PythonOperator(task_id="transform", python_callable=transform)
    load_task = PythonOperator(task_id="load", python_callable=load)

    extract_task >> transform_task >> load_task
