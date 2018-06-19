#!/usr/bin/env python3
"""
Unit tests.
"""

from unit_test_common import execute_csv2_command, initialize_csv2_request
import sys

def main(gvar):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])

    execute_csv2_command(
        gvar, None, None, None,
        ['cloudscheduler', 'defaults', 'list', '-s', 'unit-test']
        )

    execute_csv2_command(
        gvar, None, None, None,
        ['cloudscheduler', 'user', 'delete', '-Y', '-un', 'utu1']
        )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized:',
        ['cloudscheduler', 'user', 'add', '-xx', 'yy']
        )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line:',
        ['cloudscheduler', 'user', 'add']
        )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line:',
        ['cloudscheduler', 'user', 'add', '-upw', 'x']
        )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line:',
        ['cloudscheduler', 'user', 'add', '-ucn', 'unit test user one', '-upw', 'x']
        )

    execute_csv2_command(
        gvar, 1, 'UV01', 'must be all lower case.',
        ['cloudscheduler', 'user', 'add', '-un', 'UTu1', '-upw', 'Abc123', '-ucn', 'unit test user one']
        )

if __name__ == "__main__":
    main(None)

