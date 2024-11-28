import psycopg2
import pandas as pd

# Assuming the docker container is started, connect to the database
CONNECTION = "postgres://Anomdet:G5anomdet@localhost:5432/mytimescaleDB"
conn = psycopg2.connect(CONNECTION)
cursor = conn.cursor()

query = "SELECT * FROM Electric_Production;"
cursor.execute(query)
for row in cursor.fetchall():
    print(row)
cursor.close()