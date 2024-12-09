import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
from datetime import datetime
from pandas import DataFrame, Series
import numpy as np 

class DB_Anomaly_Detector(db_interface):
    def __init__(self, conn_params: dict):
        """Initialization of the connection to the PostgreSQL database """
        conn_params = {
        "host":"localhost",
        "database":"TSdatabase",
        "user":"Anomdet",
        "password":"G5anomdet",
        "port":"8050"
       }
        try:
            self.conn = psycopg2.connect(**conn_params)
            self.conn.autocommit = True
            self.cursor = self.conn.cursor()
        except Exception as e:
            raise ConnectionError(f"Error connecting to PostgreSQL: {e}")
    
    

# a=("n":23)

    def create_table(self, table_name: str, columns: list[str]):
        columns_def = ", ".join([
            f"{name} {data_type}" 
            for name,data_type in [ 
              ("timestamp", "timestamp with time zone NOT NULL"), 
              ("load_1m"," double precision NOT NULL"),
              ("load_5m ","double precision NOT NULL" ),
              ("load_15m ","double precision NOT NULL" ),
              ("sys_mem_swap_total ","double precision NOT NULL"),
              ("sys_mem_swap_free ","double precision NOT NULL"),
              ("sys_mem_free ","double precision NOT NULl"),
              ("sys_mem_cache","double precision NOT NULL"),
              ("sys_mem_buffered ","double precision NOT NULL"),
              ("sys_mem_available","double precision NOT NULL"),
              ("sys_mem_total","double precision NOT NULL"),
              ("cpu_iowait ","double precision NOT NULL"),
              ("cpu_system ","double precision NOT NULL"),
              ("cpu_user ","double precision NOT NULL"),
              ("disk_io_time","double precision NOT NULL"),
              ("disk_bytes_read "," double precision NOT NULL"), ggggggggg
              ("disk_bytes_written ","double precision NOT NULL"),
              (" disk_io_read ","double precision NOT NULL"),
              ("disk_io_write ","double precision NOT NULL"),
              ("sys_fork_rate ","double precision NOT NULL"),
              ("sys_interrupt_rate","double precision NOT NULL"),
              ("sys_context_switch_rate ","double precision NOT NULL"),
              ("sys_thermal ","double precision NOT NULL"),
              ("server_up boolean NOT NULL",""),
            ]                                   
        ])
    create_query = f"""
        CREATE TABLE IF NOT EXISTS  performance_metrics(
             PRIMARY KEY(timestamp),
            {columns_def},
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    try:
        self.cursor.execute(create_query)
    except Exception as e:
        raise RuntimeError(f"Error creating table {performance_metrics}: {e}")
    print(f"Table ' {performance_metrics}' created.")
    print("Table is successfully created.")
    
    # Convert table to hypertable
    hypertable_query = f"SELECT create_hypertable('{performance_metrics}', '{timestamp}', if_not_exists => TRUE);"
    cursor.execute(hypertable_query)
    print(f"Hypertable {performance_metrics} created successfully.")
    except Exception as e:
        raise RuntimeError(f"Error creating hypertable {performance_metrics}: {e}")
    finally:
        cursor.close()
        conn.close()            

    def insert_data(self, table_name: str, data.frame):
        try:
            # Handle data based on whether it's a file path or a DataFrame
            if not os.path.isfile(data_source):
                # If it's not a file path, assume it's a DataFrame
                data = data_source
            else:
                # If it's a file path, read the CSV file
                data = pd.read_csv(data_source)

            # Insert data into PostgreSQL database
            data.to_sql(performance_metrics, self.conn, if_exists='replace', index=False)
            self.conn.commit()
            print(f"Data inserted successfully into {performance_metrics} table.")
        except Exception as e:
            print(f"Error inserting data: {e}")
