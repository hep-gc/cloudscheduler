#!/usr/bin/env python
"""
Write cross reference to stdout. Synopsis: utilities/schema_xref.py
"""

from subprocess import Popen, PIPE
from tempfile import mkdtemp
import getpass
import os
import sys

def scan_dir(gvar, path):
    """
    Recursive function to walk the file tree of the csv2 repository, and for each python
    source file (*.py) or view definition (view_*), report which tables and columns are
    referenced. References are returned in the gvar['tables'] variable when all files
    have been scanned.
    """
    for item in os.listdir(path):
        if item[0] == '.':
            continue

        current_path = '%s/%s' % (path, item)

        if os.path.isdir(current_path):
            if current_path[-7:] != '/backup' and current_path[-4:] != '/lib':
                scan_dir(gvar, current_path)

        elif os.path.getsize(current_path) > 0 and \
        (item[:5] == 'view_' or item[-3:] == '.py'):

            _fd = open(current_path)
            current_path_content = _fd.read()
            _fd.close()

            for table in gvar['tables']:
                if '\'%s\'' % table in current_path_content or \
                '"%s"' % table in current_path_content or \
                ' %s ' % table in current_path_content or \
                '[%s]' % table in current_path_content:
                    gvar['tables'][table]['paths'][current_path] = 0
                    lines = current_path_content.split('\n')
                    for column in gvar['tables'][table]['columns']:
                        if current_path not in gvar['tables'][table]['columns'][column]:
                            gvar['tables'][table]['columns'][column][current_path] = []

                        for _ix, _v in enumerate(lines):
                            if column in lines[_ix]:
                                gvar['tables'][table]['paths'][current_path] += 1
                                gvar['tables'][table]['columns'][column][current_path].append(_ix+1)

def main(args):
    """
    Retrieve the schema (table and column definitions) of the csv2 database and then
    call scan_dir to scan all source files for references. When the scan is complete,
    print the report.
    """
    gvar = {
        'backup_data': [
            'csv2_attribute_mapping',
            ],
        'cmd_path': os.path.abspath(args[0]),
        }

    gvar['path_info'] = gvar['cmd_path'].split('/')
    gvar['ix'] = gvar['path_info'].index('cloudscheduler')
    gvar['root_dir'] = '/'.join(gvar['path_info'][:gvar['ix']+1])
    gvar['temp_dir'] = mkdtemp()
    gvar['secrets_file'] = '%s/ansible-systems/heprc/staticvms/roles/csv2/vars/csv2_secrets.yaml' \
        % '/'.join(gvar['path_info'][:gvar['ix']])
    gvar['vp_file'] = '%s/.pw/staticvms' % '/'.join(gvar['path_info'][:3])

    if os.path.exists(gvar['secrets_file']) and os.path.exists(gvar['vp_file']):
        _p1 = Popen(
            [
                'ansible-vault',
                'view',
                gvar['secrets_file'],
                '--vault-password-file',
                gvar['vp_file']
                ],
            stdout=PIPE,
            stderr=PIPE
            )
        _p2 = Popen(
            [
                'awk',
                '/^mariadb_cloudscheduler:/ {print $2}'
                ],
            stdin=_p1.stdout,
            stdout=PIPE,
            stderr=PIPE
            )
        stdout, stderr = _p2.communicate()
        if stderr != '':
            print('Failed to retrieve DB password.')
            exit(1)

        gvar['pw'] = stdout.strip()
    else:
        gvar['pw'] = getpass.getpass('Enter MariaDB password for user csv2:')

    _p1 = Popen(
        [
            'mysql',
            '-ucsv2',
            '-p%s' % gvar['pw'],
            '-e',
            'show full tables;',
            'csv2'
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
    if stderr != '':
        print('Failed to retrieve table list.')
        exit(1)


    gvar['tables'] = {}
    tables = stdout.split('\n')
    for table in tables:
        if len(table) < 1:
            continue

        gvar['tables'][table] = {'columns': {}, 'paths': {}}

        _p1 = Popen(
            [
                'mysql',
                '-ucsv2',
                '-p%s' % gvar['pw'],
                '-e',
                'show columns from %s;' % table,
                'csv2'
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
        if stderr != '':
            print('Failed to retrieve columns for table "%s".' % table)
            exit(1)

        columns = stdout.split("\n")
        for _ix in range(1, len(columns)):
            _w = columns[_ix].split()
            if len(_w) > 3:
                gvar['tables'][table]['columns'][_w[0]] = {}

    scan_dir(gvar, gvar['root_dir'])

    for table in sorted(gvar['tables']):
        print('Table: %s' % table)
        print_header_table_no_columns = True
        print_header_table_with_columns = True
        for current_path in sorted(gvar['tables'][table]['paths']):
            if gvar['tables'][table]['paths'][current_path] < 1:
                if print_header_table_no_columns:
                    print(' This table but none of its\' columns were referenced \
                        in the following files:')
                    print_header_table_no_columns = False

                print('   %s' % current_path)

        for column in sorted(gvar['tables'][table]['columns']):
            if print_header_table_with_columns:
                print(' Columns:')
                print_header_table_with_columns = False

            print('   %s' % column)
            for current_path in sorted(gvar['tables'][table]['columns'][column]):
                if gvar['tables'][table]['columns'][column][current_path]:
                    print(
                        '              %s %s' % (
                            current_path,
                            gvar['tables'][table]['columns'][column][current_path]
                            )
                        )

if __name__ == "__main__":
    main(sys.argv)
