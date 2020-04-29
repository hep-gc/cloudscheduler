
from csv2_common import check_keys, requests
import traceback
import os

def base_metadata_save(gvar, context=None):
    """
    Save the specified cloud or cloud metadata file.
    """

    if context is None:
        print('Error: This code should not have been called without a context')
        traceback.print_tb()
        return

    if context =='cloud':
        mandatory = ['-cn', '-mn', '-f']
    else:
        mandatory = ['-mn', '-f']
    required = []
    optional = ['-F', '-g', '-H', '-h', '-s', '-v', '-x509', '-xA']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    check_keys(gvar, mandatory, required, optional)
    
    # Retrieve data (possibly after changing the group).
    if context == 'cloud':
        response = requests(gvar, '/cloud/metadata-fetch/', query_data={'cloud_name': gvar['user_settings']['cloud-name'], 'metadata_name': gvar['user_settings']['metadata-name']})
    else:
        response = requests(gvar, '/group/metadata-fetch/', query_data={'metadata_name': gvar['user_settings']['metadata-name']})
    
    if os.path.exists(gvar['user_settings']['file-path']) and not gvar['user_settings']['force']:
        print('Error: The specified metadata file "%s" already exists, use -F to overwrite .' % gvar['user_settings']['file-path'])
        exit(1)
    
    # Write the reference copy.
    fd = open(gvar['user_settings']['file-path'], 'w')
    
    fd.write(response['metadata'])
    fd.close()
