"""
bash ignite.sh ../examples/config/example-ignite.xml
"""

from pyignite import Client, GenericObjectMeta
from pyignite.datatypes import *
from pyignite.datatypes.prop_codes import *
import csv


# Open a connection to the Ignite cluster
client = Client(compact_footer=False)
client.connect('127.0.0.1', 10800)

cache = client.create_cache({
    PROP_NAME: 'SQL_SRM',
    PROP_SQL_SCHEMA: 'PUBLIC',
    PROP_QUERY_ENTITIES: [
        {
            'table_name': 'SRM',
            'key_field_name': None,
            'key_type_name': 'CELLID',
            'field_name_aliases': [],
            'query_fields': [
                # Define each field of the composite key CellId
                {'name': 'EXECUTIONID', 'type_name': 'java.lang.String', 'is_key_field': True, 'is_notnull_constraint_field': True,},
                {'name': 'ABSTRACTIONID', 'type_name': 'java.lang.String', 'is_key_field': True, 'is_notnull_constraint_field': True,},
                {'name': 'ACTIONID', 'type_name': 'java.lang.String', 'is_key_field': True, 'is_notnull_constraint_field': True,},
                {'name': 'ARENAID', 'type_name': 'java.lang.String', 'is_key_field': True, 'is_notnull_constraint_field': True,},
                {'name': 'SHEETID', 'type_name': 'java.lang.String', 'is_key_field': True, 'is_notnull_constraint_field': True,},
                {'name': 'SYSTEMID', 'type_name': 'java.lang.String', 'is_key_field': True, 'is_notnull_constraint_field': True,},
                {'name': 'VARIANTID', 'type_name': 'java.lang.String', 'is_key_field': True, 'is_notnull_constraint_field': True,},
                {'name': 'ADAPTERID', 'type_name': 'java.lang.String', 'is_key_field': True, 'is_notnull_constraint_field': True,},
                {'name': 'X', 'type_name': 'java.lang.Integer', 'is_key_field': True, 'is_notnull_constraint_field': True,},
                {'name': 'X', 'type_name': 'java.lang.Integer', 'is_key_field': True, 'is_notnull_constraint_field': True,},
                {'name': 'TYPE', 'type_name': 'java.lang.String', 'is_key_field': True, 'is_notnull_constraint_field': True,},

                # Define the fields from the CellValue object
                {
                    'name': 'VALUE',
                    'type_name': 'java.lang.Integer',
                },
                {
                    'name': 'RAWVALUE',
                    'type_name': 'java.lang.Integer',
                },
                {
                    'name': 'VALUETYPE',
                    'type_name': 'java.lang.Integer',
                },
                {
                    'name': 'LASTMODIFIED',
                    'type_name': 'java.lang.Integer',
                },
                {
                    'name': 'EXECUTIONTIME',
                    'type_name': 'java.lang.Integer',
                },
            ],
            'query_indexes': [],
            'value_type_name': 'CELLVALUE',
            'value_field_name': None,
        },
    ],
})

class CellValue(
    metaclass=GenericObjectMeta,
    type_name='CELLVALUE',
    schema={'VALUE': IntObject, 'RAWVALUE': IntObject, 'VALUETYPE': IntObject, 'LASTMODIFIED': IntObject, 'EXECUTIONTIME': IntObject}
):
    pass

class CellId(
    metaclass=GenericObjectMeta,
    type_name='CELLID',
    schema={'EXECUTIONID': String, 'ABSTRACTIONID': String, 'ACTIONID': String, 'ARENAID': String, 'SHEETID': String, 'SYSTEMID': String, 'VARIANTID': String, 'ADAPTERID': String, 'X': IntObject, 'Y': IntObject, 'TYPE': String}
):
    pass

cache.put(
    CellId(EXECUTIONID='1', ABSTRACTIONID='101', ACTIONID='201', ARENAID='301', SHEETID='401', SYSTEMID='501', VARIANTID='601', ADAPTERID='701', X=801, Y=901, TYPE='1'),
    CellValue(VALUE=1, RAWVALUE=1, VALUETYPE=1, LASTMODIFIED=1, EXECUTIONTIME=1)
)

with client.sql(r'SELECT * FROM SRM', include_field_names=True) as cursor:
    print(next(cursor))
    print(*cursor)

result = cache.get(CellId(EXECUTIONID='1', ABSTRACTIONID='101', ACTIONID='201', ARENAID='301', SHEETID='401', SYSTEMID='501', VARIANTID='601', ADAPTERID='701', X=801, Y=901, TYPE='1'))
print(result)

# Destroy the cache and close the connection
cache.destroy()
client.close()