from csv2_common import check_keys, requests, show_active_user_groups, show_table

KEY_MAP = {
    '-cc':  'category',
    '-dci': 'delete_cycle_interval',
    '-djg': 'default_job_group',
    '-eg':  'enable_glint',
    '-lf':  'log_file',
    '-ll':  'log_level',
    '-nld': 'no_limit_default',
    '-c':  'cacerts',
    '-sic': 'sleep_interval_cleanup',
    '-siC': 'sleep_interval_command',
    '-sif': 'sleep_interval_flavor',
    '-sii': 'sleep_interval_image',
    '-sij': 'sleep_interval_job',
    '-sik': 'sleep_interval_keypair',
    '-sil': 'sleep_interval_limit',
    '-sim': 'sleep_interval_machine',
    '-sin': 'sleep_interval_network',
    '-siv': 'sleep_interval_vm',
    '-sml': 'sleep_interval_main_long',
    '-sms': 'sleep_interval_main_short',
    }

def config(gvar):
    """
    Modify the specified group defaults.
    """

    mandatory = []
    required = []
    optional = ['-c', '-cc', '-dci', '-djg', '-eg', '-g', '-H', '-h', '-lf', '-ll', '-nld', '-NV', '-ok', '-r', '-s', '-sic', '-siC', '-sif', '-sii', '-sij', '-sik', '-sil', '-sim', '-sin', '-siv', '-sml', '-sms', '-V', '-VC', '-xA']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    form_data = check_keys(
        gvar,
        mandatory,
        required,
        optional,
        key_map=KEY_MAP)

    # List the current defaults. If the form_data contains any optional fields,
    # those values will be updated before the list is retrieved.
    response = requests(
        gvar,
        '/server/config/',
        form_data
        )
    
    if response['message']:
        print(response['message'])

    # Print report
    show_active_user_groups(gvar, response)

    show_table(
        gvar,
        response['config_list'],
        [
            'category/Category,k',
            'config_key/Config Key,k',
            'config_type/Type',
            'config_value/Value',
        ],
        title="Server Configuration:",
    )
