import cnx_settings
# import pyodbc
import pymssql
import pandas as pd
import numpy as np
import re

# Connection to DB
# cnx_ = pyodbc.connect(cnx_settings.connection_params)
cnx = pymssql.connect(server=cnx_settings.pymssql_server, user=cnx_settings.pymssql_user,
                      password=cnx_settings.pymssql_password, database=cnx_settings.pymssql_database)


def tbl_to_dataframe(sch, tbl, columns: list) -> pd.DataFrame:
    """
    Transforms data from DB into pandas dataframe
    :param sch: name of scheme in DB
    :param tbl: name of table in DB
    :param columns: columns to retrieve from table
    :return: pandas dataframe
    """
    cursor = cnx.cursor()
    sql = f"SELECT {', '.join(str(col) for col in columns)} " \
          f"FROM {sch}.{tbl}"
    cursor.execute(sql)
    columns = [column[0] for column in cursor.description]
    dataframe = pd.DataFrame.from_records(cursor.fetchall(), columns=columns)
    return dataframe


def get_result_by_percentage(corrupted_records_amount: int, overall_records_amount: int):
    """
    Returns percentage of one value in another
    :param corrupted_records_amount: numerator
    :param overall_records_amount: denominator
    :return: decimal
    """
    return round(corrupted_records_amount / overall_records_amount * 100, 2)


def check_uniqueness(sch, tbl, unq_columns: list):
    """
    Verifies whether set of columns uniquely identify the records of the table
    :param sch: name of scheme in DB
    :param tbl: name of table in DB
    :param unq_columns: columns, which should define uniqueness
    :return: count of duplicated rows by unq_columns
    """
    cursor = cnx.cursor()
    sql = f"SELECT {', '.join(str(col) for col in unq_columns)}, COUNT(*) AS CNT " \
          f"FROM {sch}.{tbl} " \
          f"GROUP BY {', '.join(str(col) for col in unq_columns)} " \
          f"HAVING COUNT(*) > 1"
    cursor.execute(sql)
    columns = [column[0] for column in cursor.description]
    dataframe = pd.DataFrame.from_records(cursor.fetchall(), columns=columns)
    return dataframe.shape[0]


def check_nulls(sch, tbl, nn_columns: list):
    """
    Verified whether there are nulls in specific columns
    :param sch: name of scheme in DB
    :param tbl: name of table in DB
    :param nn_columns: columns, which should not contain nulls
    :return: count of rows with nulls in nn_columns
    """
    cursor = cnx.cursor()
    sql = f"SELECT {', '.join(str(col) for col in nn_columns)} " \
          f"FROM {sch}.{tbl} " \
          f"WHERE {' OR '.join(str(col + ' IS NULL') for col in nn_columns)} "
    cursor.execute(sql)
    columns = [column[0] for column in cursor.description]
    dataframe = pd.DataFrame.from_records(cursor.fetchall(), columns=columns)
    return dataframe.shape[0]


def check_metadata(sch, tbl):
    """
    Compare table metadata with metadata in file
    :param sch: name of scheme in DB
    :param tbl: name of table in DB
    :return: empty string for passed test. String with description for failed
    """
    cursor = cnx.cursor()
    sql_meta = f"SELECT DISTINCT COLS.TABLE_SCHEMA AS SCH, COLS.TABLE_NAME AS TAB, COLS.COLUMN_NAME AS COL, " \
               f"   COLS.DATA_TYPE,COLS.CHARACTER_MAXIMUM_LENGTH, COLS.NUMERIC_PRECISION, COLS.NUMERIC_SCALE " \
               f"FROM INFORMATION_SCHEMA.COLUMNS COLS " \
               f"WHERE COLS.TABLE_SCHEMA = '{sch}' AND COLS.TABLE_NAME = '{tbl}' ;"
    cursor.execute(sql_meta)
    columns = [column[0] for column in cursor.description]
    actual_meta = pd.DataFrame.from_records(cursor.fetchall(), columns=columns)
    # dataframe.to_excel("output.xlsx", sheet_name='Sheet_name_1')
    target_meta = pd.read_excel(io='metadata/metadata.xlsx',
                                sheet_name='production').query(f"SCH=='{sch}' and TAB=='{tbl}'")
    joined = actual_meta.merge(target_meta, on=['SCH', 'TAB', 'COL'],
                               how='outer', suffixes=('_actual', '_target'), indicator=True).replace(np.nan, -999)
    columns_in_target_only = joined.query('_merge == "right_only"')
    columns_in_actual_only = joined.query('_merge == "left_only"')
    metadata_differ = joined.query('DATA_TYPE_actual != DATA_TYPE_target or '
                                   'CHARACTER_MAXIMUM_LENGTH_actual != CHARACTER_MAXIMUM_LENGTH_target or '
                                   'NUMERIC_PRECISION_actual != NUMERIC_PRECISION_target or '
                                   'NUMERIC_SCALE_actual != NUMERIC_SCALE_target')
    error = ''
    if columns_in_target_only.shape[0] != 0:
        error = error + f"""{columns_in_target_only.shape[0]} columns are absent in table, while exist in metadata. 
        Columns are {columns_in_target_only['COL'].tolist()}.\n"""
    if columns_in_actual_only.shape[0] != 0:
        error = error + f"""{columns_in_actual_only.shape[0]} columns are absent in metadata, while exist in table.
        Columns are {columns_in_actual_only['COL'].tolist()}.\n"""
    if metadata_differ.shape[0] != 0:
        error = error + f"For {metadata_differ.shape[0]} rows actual metadata differs from required. " \
                        f"Columns are {metadata_differ['COL'].tolist()}"
    return error


def check_allowed_vales(sch, tbl, columns_to_check: list, values: list):
    """
    Finds percentage of values in columns which are not in the list of provided values
    :param sch: name of scheme in DB
    :param tbl: name of table in DB
    :param columns_to_check: columns, data from which should be checked
    :param values: expected data
    :return: float - percentage
    """
    dataframe = tbl_to_dataframe(sch, tbl, columns_to_check)
    concated_values = ", ".join(f"'{val}'" if isinstance(val, str) else str(val) for val in values)
    if len(values) > 1:
        query_string = ' or '.join(str(col + f' not in ({concated_values})') for col in columns_to_check)
    else:
        query_string = ' or '.join(str(col + f' != {concated_values}') for col in columns_to_check)
    return get_result_by_percentage(dataframe.query(query_string).shape[0], dataframe.shape[0])


def check_regex_format(sch, tbl, columns_to_check: list, pattern: str):
    """
    Finds percentage of values in columns, values in which does not correspond with regular expression
    :param sch: name of scheme in DB
    :param tbl: name of table in DB
    :param columns_to_check: columns, data from which should be checked
    :param pattern: regex pattern
    :return: float - percentage
    """
    dataframe = tbl_to_dataframe(sch, tbl, columns_to_check)
    processed = dataframe.applymap(lambda x: True if re.search(pattern, str(x)) else False)
    query_string = ' or '.join(str(col + f' != True') for col in columns_to_check)
    return get_result_by_percentage(processed.query(query_string).shape[0], dataframe.shape[0])


def check_pk(sch, tbl):
    """
    Check whether PK for table is defined as in metadata file
    :param sch: name of scheme in DB
    :param tbl: name of table in DB
    :return: empty string for passed test. String with description for failed
    """
    cursor = cnx.cursor()
    sql = f"SELECT schema_name(tab.schema_id) AS SCH, " \
          f"    tab.[name] AS TAB, col.[name] AS COL " \
          f"FROM sys.tables tab " \
          f"INNER JOIN sys.indexes pk " \
          f"    ON tab.object_id = pk.object_id AND pk.is_primary_key = 1 " \
          f"INNER JOIN sys.index_columns ic " \
          f"    ON ic.object_id = pk.object_id AND ic.index_id = pk.index_id " \
          f"INNER JOIN sys.columns col " \
          f"    ON pk.object_id = col.object_id AND col.column_id = ic.column_id " \
          f"WHERE schema_name(tab.schema_id) = '{sch}' AND tab.[name] = '{tbl}'"
    cursor.execute(sql)
    columns = [column[0] for column in cursor.description]
    actual_pk = pd.DataFrame.from_records(cursor.fetchall(), columns=columns)
    target_pk = pd.read_excel(io='metadata/metadata.xlsx',
                              sheet_name='production').query(f"PK == 1 & SCH == '{sch}' & TAB == '{tbl}'")
    joined = actual_pk.merge(target_pk, on=['SCH', 'TAB', 'COL'],
                             how='outer', suffixes=('_actual', '_target'), indicator=True).replace(np.nan, -999)
    absent_pk = joined.query('_merge == "right_only"')['COL'].tolist()
    redundant_pk = joined.query('_merge == "left_only"')['COL'].tolist()
    error = ''
    if len(redundant_pk) != 0:
        error = error + f"""{', '.join(str(col) for col in redundant_pk)} PK are redundant.\n"""
    if len(absent_pk) != 0:
        error = error + f"""{', '.join(str(col) for col in absent_pk)} PK are absent.\n"""
    return error
