#!/usr/bin/env python3
"""
Synopsis: utilities/generate_schema.py > lib/schema.py

This routine pulls the current table definitions from the csv2 database and writes the
schema to stdout. To use the schema definitions:

            from lib.schema import <view_or_table_name_1>, <view_or_table_name_2>, ...
"""

from subprocess import Popen, PIPE
from tempfile import mkdtemp
import json
import os
import sys
import yaml

REMOVE_BRACKETS = str.maketrans('()', '  ')

def main(args):
    """
    This does everything:
    o Writes the schema header to stdout.
    o Retrieves the list of tables from the csv2 database.
    o Then for each table:
      - Resets the variable _stdout to just the table header.
      - Retrieves the column list for the table.
      - Then for each column:
        + Appends the column definition to _stdout.-
      - Appends the table footer to _stdout.
      - Writes the table definition to stdout.
    """

    gvar = {}

    fd = open('/etc/cloudscheduler/cloudscheduler.yaml')
    gvar['csv2_config'] = yaml.full_load(fd.read())
    fd.close()
    
    gvar['cmd_path'] = os.path.abspath(args[0])
    gvar['cmd_path_stat'] = os.stat(gvar['cmd_path'])
    gvar['path_info'] = gvar['cmd_path'].split('/')
    gvar['ix'] = gvar['path_info'].index('cloudscheduler')
    gvar['schema_path'] = '%s/lib/schema.py' % '/'.join(gvar['path_info'][:gvar['ix']+1])
    gvar['schema_na_path'] = '%s/lib/schema_na.py' % '/'.join(gvar['path_info'][:gvar['ix']+1])
    gvar['fd'] = open(gvar['schema_path'], 'w')
    gvar['schema_na'] = {}

    _p1 = Popen(
        [
            'mysql',
            '-u%s' % gvar['csv2_config']['database']['db_user'],
            '-p%s' % gvar['csv2_config']['database']['db_password'],
            '-h%s' % gvar['csv2_config']['database']['db_host'],
            '-e',
            'show tables;',
            gvar['csv2_config']['database']['db_name']
            ],
        stdout=PIPE,
        stderr=PIPE
        )
    _p2 = Popen(
        [
            'awk',
            '!/Tables_in_csv2/ {print $1}'
            ],
        stdin=_p1.stdout,
        stdout=PIPE,
        stderr=PIPE
        )
    stdout, stderr = _p2.communicate()
    if _p2.returncode != 0:
        print('Failed to retrieve table list.')
        exit(1)

    gvar['fd'].write(
        "if 'Table' not in locals() and 'Table' not in globals():\n" + \
        "  from sqlalchemy import Table, Column, Float, Integer, String, MetaData, ForeignKey\n" + \
        "  metadata = MetaData()\n\n"
        )


    tables = stdout.decode('ascii').split()
    for table in tables:
        _stdout = ["%s = Table('%s', metadata,\n" % (table, table)]
        gvar['schema_na'][table] = {'keys': [], 'columns': {}}

        _p1 = Popen(
            [
                'mysql',
                '-u%s' % gvar['csv2_config']['database']['db_user'],
                '-p%s' % gvar['csv2_config']['database']['db_password'],
                '-h%s' % gvar['csv2_config']['database']['db_host'],
                '-e',
                'show columns from %s;' % table,
                gvar['csv2_config']['database']['db_name']
                ],
            stdout=PIPE,
            stderr=PIPE
            )
        _p2 = Popen(
            [
                'awk',
                '!/^+/'
                ],
            stdin=_p1.stdout,
            stdout=PIPE,
            stderr=PIPE
            )
        stdout, stderr = _p2.communicate()
        if _p2.returncode != 0:
            print('Failed to retrieve table columns.')
            exit(1)

        columns = stdout.decode('ascii').split("\n")
        for _ix in range(1, len(columns)):
            _w = columns[_ix].split()
            if len(_w) > 2:
                _stdout.append("  Column('%s'," % _w[0])
#               gvar['schema_na'][table]['columns'][_w[0]] = []

                if _w[1][:5] == 'char(' or \
                    _w[1][:8] == 'varchar(':
                    _w2 = _w[1].translate(REMOVE_BRACKETS).split()
                    _stdout.append(" String(%s)" % _w2[1])
                    gvar['schema_na'][table]['columns'][_w[0]] = {'type': 'str', 'len': _w2[1], 'nulls': _w[2]}

                elif _w[1][:4] == 'int(' or \
                _w[1][:6] == 'bigint' or \
                _w[1][:7] == 'decimal' or \
                _w[1][:8] == 'smallint' or \
                _w[1][:7] == 'tinyint':
                    _stdout.append(" Integer")
                    gvar['schema_na'][table]['columns'][_w[0]] = {'type': 'int'}

                elif _w[1] == 'text' or \
                _w[1][:4] == 'date' or \
                _w[1][:8] == 'datetime' or \
                _w[1][:4] == 'time' or \
                _w[1][:9] == 'timestamp' or \
                _w[1] == 'tinytext' or \
                _w[1] == 'longtext' or \
                _w[1] == 'mediumtext':
                    _stdout.append(" String")
                    gvar['schema_na'][table]['columns'][_w[0]] = {'type': 'str', 'nulls': _w[2]}

                elif _w[1][:7] == 'double' or \
                _w[1][:5] == 'float':
                    _stdout.append(" Float")
                    gvar['schema_na'][table]['columns'][_w[0]] = {'type': 'float'}

                else:
                    print('Table %s, unknown data type for column: %s' % (table, columns[_ix]))
                    exit(1)

                if len(_w) > 3 and _w[3] == 'PRI':
                    _stdout.append(", primary_key=True")
                    gvar['schema_na'][table]['keys'].append(_w[0])

                if _ix < len(columns) - 2:
                    _stdout.append("),\n")
                else:
                    _stdout.append(")\n  )\n")

        gvar['fd'].write('%s\n' % ''.join(_stdout))

    gvar['fd'].close()

    gvar['fd'] = open(gvar['schema_na_path'], 'w')
    gvar['fd'].write('schema = {\n')
    tix = 0
    for table in sorted(gvar['schema_na']):
        gvar['fd'].write('    "%s": {\n        "keys": [\n' % table)
        ix = 0
        for key in gvar['schema_na'][table]['keys']:
            if ix < len(gvar['schema_na'][table]['keys'])-1:
              gvar['fd'].write('            "%s",\n' % key)
            else:
              gvar['fd'].write('            "%s"\n' % key)
            ix += 1
        gvar['fd'].write('            ],\n        "columns": {\n')
        ix = 0
        for column in gvar['schema_na'][table]['columns']:
            if ix < len(gvar['schema_na'][table]['columns'])-1:
                gvar['fd'].write('            "%s": %s,\n' % (column, json.dumps(gvar['schema_na'][table]['columns'][column])))
            else:
                gvar['fd'].write('            "%s": %s\n' % (column, json.dumps(gvar['schema_na'][table]['columns'][column])))
            ix += 1

        if tix < len(gvar['schema_na'])-1:
            gvar['fd'].write('            }\n        },\n')
        else:
            gvar['fd'].write('            }\n        }\n    }\n')

        tix += 1

    gvar['fd'].close()

    _p1 = Popen(
        [
            'chown',
            '%s.%s' % (gvar['cmd_path_stat'].st_uid, gvar['cmd_path_stat'].st_gid),
            gvar['schema_path']
            ]
        )
    _p1.communicate()

if __name__ == "__main__":
    main(sys.argv)
