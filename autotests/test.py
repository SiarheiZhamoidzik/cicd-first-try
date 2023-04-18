import Utils
import pytest
import logging

my_logger = logging.getLogger()
my_logger.setLevel(logging.INFO)

metadata_for_tests_execution = \
    {'Person.Address': {'sch': 'Person',  # schema in MSS
                        'tbl': 'Address',  # table in MSS
                        'unq_columns': ['AddressID'],  # table in MSS
                        'nn_columns': ['AddressLine1'],  # columns which should not contain nulls
                        'columns_to_check_values': ['City'],
                        # columns which will be checked for containing specified values
                        'values': ['Hannover', 'Alhambra', 'Bendigo', 'Dunkerque', 'Verrieres Le Buisson'],
                        # values which will be checked in prev. columns
                        'allowed_percent_of_values_difference': 99,
                        # max allowed percent of rows with nulls in nn_columns to consider test passed
                        'columns_to_check_with_regex': ['AddressLine1'],
                        # columns which will be checked for matching regex
                        'regex_pattern': '^[0-9][0-9][0-9][0-9]\s',
                        # regex to match: pattern to find 4 digits and blank space in this example
                        'allowed_percent_of_regex_difference': 30
                        # max allowed percent of rows which do not match regex to consider test passed
                        },
     'Production.Document': {'sch': 'Production',
                             'tbl': 'Document',
                             'unq_columns': ['Title'],
                             'nn_columns': ['DocumentLevel', 'DocumentNode', 'Title'],
                             'columns_to_check_values': ['DocumentLevel'],
                             'values': [0, 1, 2],
                             'allowed_percent_of_values_difference': 7,
                             'columns_to_check_with_regex': ['FileExtension'],
                             'regex_pattern': '.doc',
                             'allowed_percent_of_regex_difference': 40
                             },
     'Production.UnitMeasure': {'sch': 'Production',
                                'tbl': 'UnitMeasure',
                                'unq_columns': ['Name'],
                                'nn_columns': ['Name', 'UnitMeasureCode', 'ModifiedDate'],
                                'columns_to_check_values': ['ModifiedDate'],
                                'values': ['2008-04-30 00:00:00.000'],
                                'allowed_percent_of_values_difference': 7,
                                'columns_to_check_with_regex': ['UnitMeasureCode'],
                                'regex_pattern': '^[A-Z]+$',  # pattern to find only uppercase letters
                                'allowed_percent_of_regex_difference': 70
                                }
     }


# Verifies whether selected columns uniquely define records in table. AssertionError returns count of duplicated rows
@pytest.mark.parametrize('chosen_table', [tbl for tbl in metadata_for_tests_execution.keys()])
def test_uniqueness(chosen_table):
    metadata_for_test = metadata_for_tests_execution.get(chosen_table)
    my_logger.info(f"Verifying uniqueness for {metadata_for_test.get('sch')}.{metadata_for_test.get('tbl')} "
                   f"by {', '.join(str(col) for col in metadata_for_test.get('unq_columns'))}")
    expected_result = 0
    actual_result = Utils.check_uniqueness(sch=metadata_for_test.get('sch'), tbl=metadata_for_test.get('tbl'),
                                           unq_columns=metadata_for_test.get('unq_columns'))
    assert actual_result == expected_result, f"{actual_result} duplicated rows were found"


# Verifies whether there are nulls in provided list of columns. AssertionError returns count of rows
# with nulls in any of columns from the list
@pytest.mark.parametrize('chosen_table', [tbl for tbl in metadata_for_tests_execution.keys()])
def test_nulls(chosen_table):
    metadata_for_test = metadata_for_tests_execution.get(chosen_table)
    my_logger.info(
        f"Verifying if there are nulls in table {metadata_for_test.get('sch')}.{metadata_for_test.get('tbl')} "
        f"in columns {', '.join(str(col) for col in metadata_for_test.get('nn_columns'))}")
    expected_result = 0
    actual_result = Utils.check_nulls(sch=metadata_for_test.get('sch'), tbl=metadata_for_test.get('tbl'),
                                      nn_columns=metadata_for_test.get('nn_columns'))
    assert actual_result == expected_result, f"{actual_result} rows with forbidden nulls"


# Compare metadata about table from MSS sys table with metadata in Metadata.xlsx file. AssertionError
# returns string with discrepancy description
@pytest.mark.parametrize('chosen_table', [tbl for tbl in metadata_for_tests_execution.keys()])
def test_metadata(chosen_table):
    metadata_for_test = metadata_for_tests_execution.get(chosen_table)
    my_logger.info(f"Verifying metadata for {metadata_for_test.get('sch')}.{metadata_for_test.get('tbl')}")
    expected_result = ''
    actual_result = Utils.check_metadata(metadata_for_test.get('sch'), metadata_for_test.get('tbl'))
    assert actual_result == expected_result, f"{actual_result}"


# Find percentage of rows in which defined columns do not contain provided values and compares with provided value.
# AssertionError returns results of comparison
@pytest.mark.parametrize('chosen_table', [tbl for tbl in metadata_for_tests_execution.keys()])
def test_allowed_vales(chosen_table):
    metadata_for_test = metadata_for_tests_execution.get(chosen_table)
    my_logger.info(f"Verifying allowed values for {metadata_for_test.get('sch')}.{metadata_for_test.get('tbl')} "
                   f"in columns {', '.join(str(col) for col in metadata_for_test.get('columns_to_check_values'))}")
    max_allowed_percent = metadata_for_test.get('allowed_percent_of_values_difference')
    actual_percent = Utils.check_allowed_vales(metadata_for_test.get('sch'),
                                               metadata_for_test.get('tbl'),
                                               metadata_for_test.get('columns_to_check_values'),
                                               metadata_for_test.get('values'))
    assert max_allowed_percent >= actual_percent, f"Actual percent of bad values is higher " \
                                                  f"then max allowed. {max_allowed_percent} < {actual_percent}."


# Find percentage of rows in which defined columns do not contain values, which are matched with provided regular
# expression and compares this percentage with provided values. AssertionError returns results of comparison
@pytest.mark.parametrize('chosen_table', [tbl for tbl in metadata_for_tests_execution.keys()])
def test_col_with_regex(chosen_table):
    metadata_for_test = metadata_for_tests_execution.get(chosen_table)
    my_logger.info(
        f"Verifying columns {', '.join(str(col) for col in metadata_for_test.get('columns_to_check_with_regex'))} "
        f"with regex for {metadata_for_test.get('sch')}.{metadata_for_test.get('tbl')}")
    max_allowed_percent = metadata_for_test.get('allowed_percent_of_regex_difference')
    actual_percent = Utils.check_regex_format(metadata_for_test.get('sch'),
                                              metadata_for_test.get('tbl'),
                                              metadata_for_test.get('columns_to_check_with_regex'),
                                              metadata_for_test.get('regex_pattern'))
    assert max_allowed_percent >= actual_percent, f"Actual percent of rows with not valid values be regex is higher " \
                                                  f"then max allowed. {max_allowed_percent} < {actual_percent}."


# Checks PKs for table from MSS sys tables and compares this result with data from Metadata.xlsx file.
# AssertionError returns string with description
@pytest.mark.parametrize('chosen_table', [tbl for tbl in metadata_for_tests_execution.keys()])
def test_pks(chosen_table):
    metadata_for_test = metadata_for_tests_execution.get(chosen_table)
    my_logger.info(f"Comparing actual PKs for {metadata_for_test.get('sch')}."
                   f"{metadata_for_test.get('tbl')} with metadata")
    expected_result = ''
    actual_result = Utils.check_pk(metadata_for_test.get('sch'), metadata_for_test.get('tbl'))
    assert expected_result == actual_result, f"PKs for {metadata_for_test.get('sch')}.{metadata_for_test.get('tbl')} " \
                                             f"are not aligned with metadata"
