# DB CONNECTION

db_conn_driver = 'Driver={ODBC Driver 17 for SQL Server};'
server = 'Server=localhost;'
database = 'Database=AdventureWorks2019;'
trusted_Connection = 'Trusted_Connection=yes;'
conn_db_role = 'UID=<user_role>;'
conn_db_creds = 'PWD=<PWD>;'

# with Windows authentication
connection_params = db_conn_driver + server + database + trusted_Connection

# with password and role
# connection_params= db_conn_driver + server + database + conn_db_role + conn_db_creds


# DB CONNECTION pymssql
pymssql_server = 'host.docker.internal'
pymssql_user = 'auto_test'
pymssql_password = 'auto_test'
pymssql_database = 'AdventureWorks2019'
