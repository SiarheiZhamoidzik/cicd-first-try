# if 'FOO' == 'foo'.upper():
#     print('Test Passed')
# else:
#     print('Test Failed')
    
# DB CONNECTION pymssql

import pymssql

pymssql_server = 'localhost'
pymssql_user = 'auto_test'
pymssql_password = 'auto_test'
pymssql_database = 'AdventureWorks2019'
    
cnx = pymssql.connect(server=pymssql_server, user=pymssql_user,
                      password=pymssql_password, database=pymssql_database)