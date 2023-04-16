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
    
cnx = pymssql.connect(server=cnx_settings.pymssql_server, user=cnx_settings.pymssql_user,
                      password=cnx_settings.pymssql_password, database=cnx_settings.pymssql_database)