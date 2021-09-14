import pandas as pd
import sqlalchemy as sql

conn = "mysql+pymysql://headwall:photonics@192.168.77.37/gratingsdb"  # database connection string
db_connection = sql.create_engine(conn)

query = 'select * from rejectiondata'

results = pd.read_sql(query, db_connection)
results.to_csv("rejectiondata.csv", index=False)
