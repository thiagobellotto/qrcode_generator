import psycopg2
import os


def insert_to_table_dataset(db_schema="airpoon", values=None):
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DATABASE"),
    )

    if values is None:
        raise ValueError("You need to pass the values to be inserted.")

    cur = conn.cursor()
    print(f"Connected to PostgreSQL.")
    conn.set_session(autocommit=True)

    query = f"""INSERT INTO {db_schema}.ml_dataset (user_id, company, file_type, file_name, bucket, connection_type, file_size, 
            rows_count, columns_count, list_of_columns, list_of_columns_types, list_of_columns_size, nan_count, 
            empty_cells_count) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    cur.execute(query, values)

    cur.close()
    conn.close()

    print(f"Disconnected from PostgreSQL.")
