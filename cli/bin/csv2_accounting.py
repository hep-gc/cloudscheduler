from csv2_common import check_keys, requests, show_active_user_groups, show_table, verify_yaml_file
from subprocess import Popen, PIPE

import filecmp
import os

KEY_MAP = {
    '-a':  'all',
    '-g':   'group',
    '-lu':  'last_update',
    }

COMMAS_TO_NL = str.maketrans(',','\n')


def apel(gvar):
    """
    List aliases for the active group.
    """

    mandatory = []
    required = []
    optional = ['-a', '-CSEP', '-CSV', '-g', '-H', '-h', '-lu', '-ok', '-r', '-s', '-V', '-VC', '-NV', '-w', '-v', '-x509', '-xA']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    check_keys(gvar, mandatory, required, optional)

    # Check for missing arguments or help required.
    form_data = check_keys(
        gvar,
        mandatory,
        required,
        optional,
        key_map=KEY_MAP)

    # Retrieve data (possibly after changing the group).
#   response = requests(gvar, '/accounting/apel/')
    
    response = requests(
        gvar,
        '/accounting/apel/',
        form_data
        )
    if response['message']:
        print(response['message'])

    # Print report.
    show_active_user_groups(gvar, response)

    show_table(
        gvar,
        response['apel_accounting'],
        [
            'group_name/Group,k',
            'cloud_name/Cloud,k',
            'hostname/Hostname,k',
            'cloud_type/Type/Cloud',
            'region/Region/Cloud',
            'flavor_id/ID/Flavor',
            'flavor/Name/Flavor',
            'image_id/ID/Image',
            'image/Name/Image',
            'benchmark_type/Type/Benchmark',
            'benchmark/Score/Benchmark',
            'vmid/ID/VM',
            'cores/Cores/VM',
            'disk/Disk/VM',
            'ram/RAM/VM',
            'start_time/Started/VM',
            'end_time/Ended/VM',
            'cpu_time/CPU Time/VM',
            'network_type/Type/Network',
            'rx/Received (MBs)/Network',
            'tx/Sent (MBs)/Network',
            'last_update/Last Update'
            ],
        title="APEL Accounting",
        )

#   show_table(
#       gvar,
#       response['cloud_list'],
#       [
#           'group_name/Group,k',
#           'cloud_name/Alias,k',
#           ],
#       title="Clouds",
#       optional=True,
#       )

