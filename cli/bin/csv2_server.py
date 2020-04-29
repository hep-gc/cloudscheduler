from csv2_common import check_keys, requests, show_active_user_groups, show_table

KEY_MAP = {
    '-cc':  'category',
    '-ckv': 'config_key_values',
    }

def config(gvar):
    """
    Modify the specified group defaults.
    """

    mandatory = []
    required = []
    optional = ['-cc', '-ckv', '-CSEP', '-CSV', '-g', '-H', '-h', '-NV', '-ok', '-r', '-s', '-V', '-VC', '-v', '-x509', '-xA']

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
        title="Server Configuration",
    )
