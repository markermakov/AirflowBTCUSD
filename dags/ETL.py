try:
    from airflow import DAG
    from airflow.operators.python_operator import PythonOperator
    from airflow.operators.dummy_operator import DummyOperator
    from datetime import date, datetime, timedelta
    from dotenv import dotenv_values
    from sqlalchemy import create_engine, inspect
    from time import sleep
    import requests
    import os
    import pandas as pd
    import json
    import psycopg2
    print("All modules were imported successfully")

except Exception as e:
    print("Error {} ".format(e))

def fill_table(table_name, engine, listToPg):
    if table_name in inspect(engine).get_table_names():
        print(f"{table_name!r} exists in the DB!")
        engine.execute(f"INSERT into {table_name} (currency_pair, created_on, current_rate) VALUES (%s, %s, %s)", listToPg)
        my_table = pd.read_sql(f"select * from {table_name}", engine)
        table_pg = my_table.tail(5)
        print(f"""DATASET:\n{table_pg}""")
    else:
        print(f"{table_name} does not exist in the DB! Creating new table...")
        engine.execute(f"CREATE TABLE {table_name} (currency_pair VARCHAR NOT NULL,    created_on TIMESTAMP NOT NULL, current_rate decimal not null );")
        engine.execute(f"INSERT into {table_name}(currency_pair, created_on, current_rate) VALUES (%s, %s, %s)", listToPg)
        my_table = pd.read_sql(f"select * from {table_name}", engine)
        table_pg = my_table.tail(5)
        print(f"""DATASET:\n{table_pg}""")

def main():

    CONFIG = dotenv_values('env.env')

    if not CONFIG:
        CONFIG = os.environ

    connection_uri = "postgresql+psycopg2://{}:{}@{}:{}".format(
        CONFIG["POSTGRES_USER"],
        CONFIG["POSTGRES_PASSWORD"],
        CONFIG['POSTGRES_HOST'],
        CONFIG["POSTGRES_PORT"],
    )

    engine = create_engine(connection_uri, pool_pre_ping=True)
    engine.connect()

    today = str(date.today())
    hours = datetime.now().strftime("%H:%M:%S")
    url = "https://api.exchangerate.host/convert?from=BTC&to=USD"
    response = requests.get(url)
    data = response.json()
    listToPg = ["BTC/USD", today + ' ' + hours, round(data['info'].get("rate"), 2)]
    print(listToPg)

    fill_table("etl", engine, listToPg)

with DAG (
    dag_id="ETL",
    schedule_interval="0 */3 * * *",
    default_args={
        "owner": "airflow",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "start_date": datetime(2023, 2, 18)
    },
    catchup=False
) as f:

    main = PythonOperator(
        task_id="load_and_export_metrics_to_pg",
        python_callable=main,
    )