"""
Use Apache Ignite with Docker:
    1. docker pull apacheignite/ignite:2.16.0
    2. docker run -d -p 10800:10800 apacheignite/ignite:2.16.0

Alternatively, use Apache Ignite as a local installation:
    1. download Apache Ignite binaries (NOT SOURCE FILES) version 2.16.0 from https://ignite.apache.org/download.cgi#binaries
    2. unzip the zip archive
    3. navigate to the bin folder in the unzipped folder
    4. run ignite.bat (Windows) or ignite.sh (Unix) via the command line
"""

from pyignite import Client, GenericObjectMeta
from pyignite.datatypes import *
from pyignite.datatypes.prop_codes import *
import pandas as pd
import sys
import git
repo = git.Repo(search_parent_directories=True)
sys.path.insert(0, repo.working_tree_dir)


class LassoIgniteClient:
    def __init__(self) -> None:
        self.client = Client(compact_footer=False)
        self.client.connect("localhost", 10800)

        self.cache = self.client.get_or_create_cache(
            {
                PROP_NAME: "SQL_SRM",
                PROP_SQL_SCHEMA: "PUBLIC",
                PROP_QUERY_ENTITIES: [
                    {
                        "table_name": "PYTHON_SRM",
                        "key_field_name": None,
                        "key_type_name": "CELLID",
                        "field_name_aliases": [],
                        "query_fields": [
                            # Define each field of the composite key CellId
                            {
                                "name": "EXECUTIONID",
                                "type_name": "java.lang.String",
                                "is_key_field": True,
                                "is_notnull_constraint_field": True,
                            },
                            {
                                "name": "ABSTRACTIONID",
                                "type_name": "java.lang.String",
                                "is_key_field": True,
                                "is_notnull_constraint_field": True,
                            },
                            {
                                "name": "ACTIONID",
                                "type_name": "java.lang.String",
                                "is_key_field": True,
                                "is_notnull_constraint_field": True,
                            },
                            {
                                "name": "ARENAID",
                                "type_name": "java.lang.String",
                                "is_key_field": True,
                                "is_notnull_constraint_field": True,
                            },
                            {
                                "name": "SHEETID",
                                "type_name": "java.lang.String",
                                "is_key_field": True,
                                "is_notnull_constraint_field": True,
                            },
                            {
                                "name": "SYSTEMID",
                                "type_name": "java.lang.String",
                                "is_key_field": True,
                                "is_notnull_constraint_field": True,
                            },
                            {
                                "name": "VARIANTID",
                                "type_name": "java.lang.String",
                                "is_key_field": True,
                                "is_notnull_constraint_field": True,
                            },
                            {
                                "name": "ADAPTERID",
                                "type_name": "java.lang.String",
                                "is_key_field": True,
                                "is_notnull_constraint_field": True,
                            },
                            {
                                "name": "X",
                                "type_name": "java.lang.Integer",
                                "is_key_field": True,
                                "is_notnull_constraint_field": True,
                            },
                            {
                                "name": "Y",
                                "type_name": "java.lang.Integer",
                                "is_key_field": True,
                                "is_notnull_constraint_field": True,
                            },
                            {
                                "name": "TYPE",
                                "type_name": "java.lang.String",
                                "is_key_field": True,
                                "is_notnull_constraint_field": True,
                            },
                            
                            # Define the fields from the CellValue object
                            {
                                "name": "VALUE",
                                "type_name": "java.lang.String",
                            },
                            {
                                "name": "RAWVALUE",
                                "type_name": "java.lang.String",
                            },
                            {
                                "name": "VALUETYPE",
                                "type_name": "java.lang.String",
                            },
                            {
                                "name": "LASTMODIFIED",
                                "type_name": "java.sql.Timestamp",
                            },
                            {
                                "name": "EXECUTIONTIME",
                                "type_name": "java.lang.Long",
                            },
                        ],
                        "query_indexes": [],
                        "value_type_name": "CELLVALUE",
                        "value_field_name": None,
                    },
                ],
            }
        )


    def putAll(self, cells: list) -> bool:
        """
        Put all cells into the cache

        Returns: True if successful, False otherwise
        """
        try:
            for cell in cells:
                cellId, cellValue = cell
                self.cache.put(cellId, cellValue)
        except Exception as e:
            print(f"Error while putting cells into cache: {e}")
            return False
        else:
            return True

    def getDataFrame(self) -> pd.DataFrame:
        """
        Returns: A DataFrame that holds all data from the SRM cache
        """
        cursor = self.client.sql(r"SELECT * FROM PYTHON_SRM", include_field_names=True)
        column_headers = next(cursor)
        rows = list(cursor)
        df = pd.DataFrame(rows, columns=column_headers)
        return df


class CellId(
    metaclass=GenericObjectMeta,
    type_name="CELLID",
    schema={
        "EXECUTIONID": String,
        "ABSTRACTIONID": String,
        "ACTIONID": String,
        "ARENAID": String,
        "SHEETID": String,
        "SYSTEMID": String,
        "VARIANTID": String,
        "ADAPTERID": String,
        "X": IntObject,
        "Y": IntObject,
        "TYPE": String,
    },
):
    """
    Pythonic representation of the BinaryObject Ignite data type.
    """
    pass


class CellValue(
    metaclass=GenericObjectMeta,
    type_name="CELLVALUE",
    schema={
        "VALUE": String,
        "RAWVALUE": String,
        "VALUETYPE": String,
        "LASTMODIFIED": DateObject,
        "EXECUTIONTIME": LongObject,
    },
):
    pass
    """
    Pythonic representation of the BinaryObject Ignite data type.
    """
