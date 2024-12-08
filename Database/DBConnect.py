#!C:\Users\LENOVO\Desktop\VavaAnomaly\AnomDet\Database\DBConnet.py
#Libraries imported which will facilate to communicate with database
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
    # Your code here
except Exception as e:
    print(f"Error occurred: {e}")

      """ print("Successfully Connected.");     
       self.conn = psycopg2.connect(**conn_params)
       self.cursor = self.conn.cursor()"""