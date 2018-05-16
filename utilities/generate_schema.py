#!/usr/bin/env python3
"""
Synopsis: utilities/generate_schema.py > lib/schema.py

This routine pulls the current table definitions from the csv2 database and writes the
schema to stdout. To use the schema definitions:

            from lib.schema import <view_or_table_name_1>, <view_or_table_name_2>, ...
"""

from subprocess import Popen, PIPE
from tempfile import mkdtemp
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
    gvar['csv2_config'] = yaml.load(fd.read())
    fd.close()
    
    gvar['cmd_path'] = os.path.abspath(args[0])
    gvar['cmd_path_stat'] = os.stat(gvar['cmd_path'])
    gvar['path_info'] = gvar['cmd_path'].split('/')
    gvar['ix'] = gvar['path_info'].index('cloudscheduler')
    gvar['schema_path'] = '%s/lib/schema.py' % '/'.join(gvar['path_info'][:gvar['ix']+1])
    gvar['fd'] = open(gvar['schema_path'], 'w')

    _p1 = Popen(
        [
            'mysql',
            '-u%s' % gvar['csv2_config']['database']['db_user'],
            '-p%s' % gvar['csv2_config']['database']['db_password'],
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
        "  from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey\n" + \
        "  metadata = MetaData()\n\n"
        )


    tables = stdout.decode('ascii').split()
    for table in tables:
        _stdout = ["%s = Table('%s', metadata,\n" % (table, table)]

        _p1 = Popen(
            [
                'mysql',
                '-u%s' % gvar['csv2_config']['database']['db_user'],
                '-p%s' % gvar['csv2_config']['database']['db_password'],
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
                if _w[1][:8] == 'varchar(':
                    _w2 = _w[1].translate(REMOVE_BRACKETS).split()
                    _stdout.append(" String(%s)" % _w2[1])

                elif _w[1][:4] == 'int(' or \
                _w[1][:6] == 'bigint' or \
                _w[1] == 'date' or \
                _w[1] == 'datetime' or \
                _w[1][:7] == 'decimal' or \
                _w[1][:8] == 'smallint' or \
                _w[1][:7] == 'tinyint':
                    _stdout.append(" Integer")

                elif _w[1] == 'text' or \
                _w[1] == 'longtext' or \
                _w[1] == 'mediumtext':
                    _stdout.append(" String")

                else:
                    print('Unknown data type for column: %s' % columns[_ix])
                    exit(1)

                if len(_w) > 3 and _w[3] == 'PRI':
                    _stdout.append(", primary_key=True")

                if _ix < len(columns) - 2:
                    _stdout.append("),\n")
                else:
                    _stdout.append(")\n  )\n")

        gvar['fd'].write('%s\n' % ''.join(_stdout))

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
