#!/usr/bin/env python3
"""
Synopsis: utilities/generate_schema.py > lib/schema.py

This routine pulls the current table definitions from the csv2 database and writes the
schema to the project's library directory. To use the schema definitions:

    from <project>.lib.schema import <view_or_table_name_1>, <view_or_table_name_2>, ...
"""

from cloudscheduler.lib.db_config import Config
from subprocess import Popen, PIPE
from tempfile import mkdtemp
import json
import os
import sys
import yaml

REMOVE_BRACKETS = str.maketrans('()', '  ')

def main(args):
    def add_column_entry(schema, table, column, type):
        schema[table]['columns'][column['Field']] = {'type': type, 'len': column_type[1], 'nulls': column['Null'], 'extra': column['Extra']}

        if column['Default']:
            schema[table]['columns'][column['Field']]['default'] = column['Default']

        if column['Key'] == 'PRI':
            schema[table]['keys'].append(column['Field'])

    cmd_path = os.path.abspath(args[0])
    cmd_path_stat = os.stat(cmd_path)
    path_info = cmd_path.split('/')
    schema_path = '%s/lib/schema.py' % '/'.join(path_info[:path_info.index('cloudscheduler')+1])

    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', [])
    config.db_open()

    db = config.db_query('select database() as db;')

    schema = {}
    table_name = 'Tables_in_%s' % db[0]['db']
    tables = config.db_query('show tables;')
    for table in tables:
        schema[table[table_name]] = {'keys': [], 'columns': {}}
        columns = config.db_query('show full columns from %s;' % table[table_name])
        for column in columns:
            column_type = column['Type'].translate(REMOVE_BRACKETS).split()
            if len(column_type) < 2:
                column_type.append(-1)

            if not column['Default']:
                column['Default'] == None


            if column_type[0] == 'char' or \
                column_type[0] == 'varchar' or \
                column_type[0] == 'text' or \
                column_type[0] == 'date' or \
                column_type[0] == 'datetime' or \
                column_type[0] == 'time' or \
                column_type[0] == 'timestamp' or \
                column_type[0] == 'longtext' or \
                column_type[0] == 'mediumtext' or \
                column_type[0] == 'set' or \
                column_type[0] == 'enum':
                add_column_entry(schema, table[table_name], column, 'str')

            elif column_type[0] == 'int' or \
                column_type[0] == 'bigint' or \
                column_type[0] == 'decimal' or \
                column_type[0] == 'smallint' or \
                column_type[0] == 'tinyint':
                add_column_entry(schema, table[table_name], column, 'int')

            elif column_type[0] == 'double' or \
                column_type[0] == 'float':
                add_column_entry(schema, table[table_name], column, 'float')

            else:
                print("Don't know how to deal with column: %s" % column)
                exit(1)

    fd = open(schema_path, 'w')
    fd.write('schema = {\n')
    tix = 0
    for table in sorted(schema):
        fd.write('    "%s": {\n        "keys": [\n' % table)
        ix = 0
        for key in schema[table]['keys']:
            if ix < len(schema[table]['keys'])-1:
              fd.write('            "%s",\n' % key)
            else:
              fd.write('            "%s"\n' % key)
            ix += 1
        fd.write('            ],\n        "columns": {\n')
        ix = 0
        for column in schema[table]['columns']:
            if ix < len(schema[table]['columns'])-1:
                fd.write('            "%s": %s,\n' % (column, json.dumps(schema[table]['columns'][column])))
            else:
                fd.write('            "%s": %s\n' % (column, json.dumps(schema[table]['columns'][column])))
            ix += 1

        if tix < len(schema)-1:
            fd.write('            }\n        },\n')
        else:
            fd.write('            }\n        }\n    }\n')

        tix += 1

    fd.close()

    p1 = Popen(
        [
            'chown',
            '%s.%s' % (cmd_path_stat.st_uid, cmd_path_stat.st_gid),
            schema_path
            ]
        )
    p1.communicate()

if __name__ == "__main__":
    main(sys.argv)
