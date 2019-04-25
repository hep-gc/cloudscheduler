#!/usr/bin/env python3
from cloudscheduler.lib.db_config import Config
from cloudscheduler.lib.html_tables_to_dictionary import get_html_tables
import logging
import os
import sys

config = Config('/etc/cloudscheduler/cloudscheduler.yaml', os.path.basename(sys.argv[0]), pool_size=8)

tables = get_html_tables(config.ec2_regions_and_endpoints_url)
print(tables)

if config.ec2_regions_and_endpoints_table not in tables:
    0/0

for table in [config.ec2_regions_and_endpoints_table]:
    print(table)
    if 'heads' in tables[table]:
        print('   ', '%-48s' * len(tables[table]['heads']) % tuple(tables[table]['heads']))
        for row in tables[table]['rows']:
            print('   ', '%-48s' * len(row) % tuple(row))
