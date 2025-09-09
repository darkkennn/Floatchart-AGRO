import psycopg2
import streamlit as st
import pandas as pd
from pandas import DataFrame

def ensure_table_exists():
    db_params = st.secrets["database"]
    conn = None
    try:
        conn = psycopg2.connect(db_params["connection_string"])
        cur = conn.cursor()
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS argo_floats (
            id SERIAL PRIMARY KEY,
            latitude DOUBLE PRECISION,
            longitude DOUBLE PRECISION,
            timestamp TIMESTAMP
        );
        """
        cur.execute(create_table_sql)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        st.error(f"Database error during table creation: {error}")
    finally:
        if conn is not None:
            conn.close()

def insert_data(df: DataFrame):
    if df.empty:
        st.warning("Dataframe is empty. Nothing to insert.")
        return

    db_params = st.secrets["database"]
    conn = None
    try:
        df = df[['latitude', 'longitude', 'time']]
        conn = psycopg2.connect(db_params["connection_string"])
        cur = conn.cursor()
        
        tuples = [tuple(x) for x in df.itertuples(index=False, name=None)]
        cols = 'latitude, longitude, timestamp'
        
        psycopg2.extras.execute_values(cur, f"INSERT INTO argo_floats ({cols}) VALUES %s", tuples, page_size=1000)
        conn.commit()
        st.success("Data successfully uploaded to PostgreSQL.")

    except (Exception, psycopg2.DatabaseError) as error:
        st.error(f"Database error during data insertion: {error}")
    finally:
        if conn is not None:
            conn.close()

def get_all_argo_data():
    db_params = st.secrets["database"]
    conn = None
    try:
        conn = psycopg2.connect(db_params["connection_string"])
        sql_query = "SELECT id, latitude, longitude, timestamp FROM argo_floats;"
        df = pd.read_sql_query(sql_query, conn)
        return df
    except (Exception, psycopg2.DatabaseError) as error:
        st.error(f"Database error while fetching data: {error}")
        return pd.DataFrame(columns=['id', 'latitude', 'longitude', 'timestamp'])
    finally:
        if conn is not None:
            conn.close()
            
def is_data_present():
    db_params = st.secrets["database"]
    conn = None
    try:
        conn = psycopg2.connect(db_params["connection_string"])
        cur = conn.cursor()
        cur.execute("SELECT EXISTS(SELECT 1 FROM argo_floats LIMIT 1);")
        return cur.fetchone()[0]
    except (Exception, psycopg2.DatabaseError) as error:
        st.error(f"Database connection check failed: {error}")
        return False
    finally:
        if conn is not None:
            conn.close()