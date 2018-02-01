#!/usr/bin/env python
#
# Synopsis: utilities/generate_schema.py > lib/schema.py
#
# This routine pulls the current table definitions from the CSv2 database and writes the schema to stdout. To use the
# schema definitions:
#
# from lib.schema import <view_or_table_name_1>, <view_or_table_name_2>, ...
#
from subprocess import Popen, PIPE
from tempfile import mkdtemp
import os
import string
import sys

remove_brackets = string.maketrans('()', '  ')

def main(args):
  gvar = {'backup_data': [
    'csv2_attribute_mapping',
    ],
    'cmd_path': os.path.abspath(args[0]),
    }

  gvar['path_info'] = gvar['cmd_path'].split('/')
  gvar['ix'] = gvar['path_info'].index('cloudscheduler')
  gvar['temp_dir'] = mkdtemp()
  gvar['secrets_file'] = '%s/ansible-systems/heprc/staticvms/roles/csv2/vars/csv2_secrets.yaml' % '/'.join(gvar['path_info'][:gvar['ix']])
  gvar['vp_file'] = '%s/.pw/staticvms' % '/'.join(gvar['path_info'][:3])

  p1 = Popen(['ansible-vault', 'view', gvar['secrets_file'], '--vault-password-file', gvar['vp_file']], stdout=PIPE, stderr=PIPE)
  p2 = Popen(['awk', '/^mariadb_root:/ {print $2}'], stdin=p1.stdout, stdout=PIPE, stderr=PIPE)
  stdout, stderr = p2.communicate()
  if stderr != '':
    'Failed to retrieve DB password.'
    exit(1)

  gvar['pw'] = stdout.strip()

  p1 = Popen(['mysql', '-uroot', '-p%s' % gvar['pw'], '-e', 'show tables;', 'csv2'], stdout=PIPE, stderr=PIPE)
  p2 = Popen(['awk', '!/Tables_in_csv2/ {print $1}'], stdin=p1.stdout, stdout=PIPE, stderr=PIPE)
  stdout, stderr = p2.communicate()
  if stderr != '':
    'Failed to retrieve table list.'
    exit(1)

  print "if 'Table' not in locals() and 'Table' not in globals():\n  from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey\n  metadata = MetaData()\n"


  tables = stdout.split()
  for table in tables:
    td = [  "%s = Table('%s', metadata,\n" % (table, table) ]

    p1 = Popen(['mysql', '-uroot', '-p%s' % gvar['pw'], '-e', 'show columns from %s;' % table, 'csv2'], stdout=PIPE, stderr=PIPE)
    p2 = Popen(['awk', '!/^+/'], stdin=p1.stdout, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p2.communicate()
    if stderr != '':
      'Failed to retrieve table list.'
      exit(1)

    columns = stdout.split("\n")
    for ix in range(1, len(columns)):
      w = columns[ix].split()
      if len(w) > 3:
        td.append("  Column('%s'," % w[0])
        if w[1][:8] == 'varchar(':
          w2 = w[1].translate(remove_brackets).split()
          td.append(" String(%s)" % w2[1])
        elif w[1][:4] == 'int(' or w[1][:6] == 'bigint' or w[1] == 'date' or w[1] == 'datetime' or w[1][:7] == 'decimal' or w[1][:8] == 'smallint' or w[1][:7] == 'tinyint':
          td.append(" Integer")
        elif w[1] == 'text' or w[1] == 'longtext' or w[1] == 'mediumtext':
          td.append(" String")
        else:
          print '????????????????????????????????', columns[ix]
          0/0

        if w[3] == 'PRI':
          td.append(", primary_key=True")

        if ix < len(columns) - 2:
          td.append("),\n")
        else:
          td.append(")\n  )\n")
          
    print ''.join(td)

if __name__ == "__main__":
  main(sys.argv)
