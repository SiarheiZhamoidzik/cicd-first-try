# if 'FOO' == 'foo'.upper():
#     print('Test Passed')
# else:
#     print('Test Failed')
    
# DB CONNECTION pymssql

import pymssql

pymssql_server = 'host.docker.internal'
pymssql_user = 'auto_test'
pymssql_password = 'auto_test'
pymssql_database = 'AdventureWorks2019'
    
cnx = pymssql.connect(server=pymssql_server, user=pymssql_user,
                      password=pymssql_password, database=pymssql_database)
                      
cursor = cnx.cursor()
sql = f"select top 10 * from Production.UnitMeasure"
cursor.execute(sql)
print([column for column in cursor.description])
