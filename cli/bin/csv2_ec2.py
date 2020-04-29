from csv2_common import check_keys, requests, show_active_user_groups, show_table
from subprocess import Popen, PIPE

import os

# ----------------------------------------------------------------------------------------------------------------------

def get_form_data_and_update_count(gvar, mandatory, required, optional, key_map={}, query_keys=[]):
    form_data = check_keys(
        gvar,
        mandatory,
        required,
        optional,
        key_map=key_map)

    query_count = 0
    for key in query_keys:
        if key in form_data:
            query_count += 1

    return form_data, len(form_data)-query_count

# ----------------------------------------------------------------------------------------------------------------------

def images(gvar):
    """
    List EC2 images for the specified cloud.
    """

    mandatory = ['-cn']
    required = []
    optional = ['-CSEP', '-CSV', '-g', '-H', '-h', '-ia', '-il', '-inl', '-ioa', '-ioi', '-ios', '-NV', '-ok', '-r', '-s', '-V', '-VC', '-v', '-v', '-x509', '-xA', '-w']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    key_map = {
        '-cn':   'cloud_name',
        '-ia':   'architectures',
        '-il':   'like',
        '-inl':  'not_like',
        '-ioa':  'owner_aliases',
        '-ioi':  'owner_ids',
        '-ios':  'operating_systems',
        }

    # Check for missing arguments or help required.
    form_data, updates = get_form_data_and_update_count(
        gvar,
        mandatory,
        required,
        optional,
        key_map=key_map,
        query_keys=['cloud_name'])

    # Retrieve data (possibly after changing the filters).
    if updates > 0:
        response = requests(
            gvar,
            '/ec2/images/',
            form_data
            )
    else:
        response = requests(gvar, '/ec2/images/', query_data={'cloud_name': gvar['user_settings']['cloud-name']})
    
    if response['message']:
        print(response['message'])

    # Print report.
    show_active_user_groups(gvar, response)

    show_table(
        gvar,
        response['ec2_image_filters'],
        [
            'group_name/Group,k',
            'cloud_name/Cloud,k',
            'owner_aliases/Aliases/Owner',
            'owner_ids/IDs/Owner',
            'like/Like/Images',
            'not_like/Not Like/Images',
            'operating_systems/Operating Systems',
            'architectures/Architectures',   
        ],
        title="EC2 Image Filters",
        )

    show_table(
        gvar,
        response['architectures'],
        [
            'architecture/Architecture',
        ],
        title="Architecture Filter",
        optional=True,
        )

    show_table(
        gvar,
        response['operating_systems'],
        [
            'operating_system/Operating System',
        ],
        title="Operating System Filter",
        optional=True,
        )

    show_table(
        gvar,
        response['owner_aliases'],
        [
            'alias/Alias',
        ],
        title="Owner Alias Filter",
        optional=True,
        )

    show_table(
        gvar,
        response['ec2_images'],
        [
            'region/Region,k',
            'image_location/Location',
            'id/ID',
            'owner_alias/Alias/Owner',
            'owner_id/ID/Owner',
            'borrower_id/Borrower ID',
            'opsys/Operating System',
            'arch/Architecture',
            'disk_format/Disk Fromat',
            'size/Size',
            'visibility/Visibility',
            'last_updated/Last Updated',
        ],
        title="EC2 Images",
        )

# ----------------------------------------------------------------------------------------------------------------------

def instance_types(gvar):
    """
    List EC2 instance types for the specified cloud.
    """

    mandatory = ['-cn']
    required = []
    optional = ['-CSEP', '-CSV', '-g', '-H', '-h', '-itc', '-itf', '-itmn', '-itmx', '-itos', '-itp', '-itpm', '-NV', '-ok', '-r', '-s', '-V', '-VC', '-v', '-v', '-x509', '-xA', '-w']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    key_map = {
        '-cn':   'cloud_name',
        '-itc':  'cores',
        '-itf':  'families',
        '-itmn': 'memory_min_gigabytes_per_core',
        '-itmx': 'memory_max_gigabytes_per_core',
        '-itos': 'operating_systems',
        '-itp':  'processors',
        '-itpm': 'processor_manufacturers',
        }

    # Check for missing arguments or help required.
    form_data, updates = get_form_data_and_update_count(
        gvar,
        mandatory,
        required,
        optional,
        key_map=key_map,
        query_keys=['cloud_name'])

    # Retrieve data (possibly after changing the filters).
    if updates > 0:
        response = requests(
            gvar,
            '/ec2/instance-types/',
            form_data
            )
    else:
        response = requests(gvar, '/ec2/instance-types/', query_data={'cloud_name': gvar['user_settings']['cloud-name']})
    
    if response['message']:
        print(response['message'])

    # Print report.
    show_active_user_groups(gvar, response)

    show_table(
        gvar,
        response['ec2_instance_type_filters'],
        [
            'group_name/Group,k',
            'cloud_name/Cloud,k',
            'families/Families',
            'operating_systems/Operatings Systems',
            'processors/Processors',
            'processor_manufacturers/Processor Manufacturers',
            'cores/Cores',
            'memory_min_gigabytes_per_core/Min/Memory (GiB per core)',
            'memory_max_gigabytes_per_core/Max/Memory (GiB per core)',
#           'owner_aliases/Aliases/Owner',
#           'owner_ids/IDs/Owner',
#           'like/Like/Images',
#           'not_like/Not Like/Images',
#           'operating_systems/Operating Systems',
#           'architectures/Architectures',   
        ],
        title="EC2 Instance Type Filters",
        )

    show_table(
        gvar,
        response['families'],
        [
            'instance_family/Family',
        ],
        title="Family Filter",
        optional=True,
        )

    show_table(
        gvar,
        response['operating_systems'],
        [
            'operating_system/Operating System',
        ],
        title="Operating System Filter",
        optional=True,
        )

    show_table(
        gvar,
        response['processors'],
        [
            'processor/Processor',
        ],
        title="Processor Filter",
        optional=True,
        )

    show_table(
        gvar,
        response['manufacturers'],
        [
            'processor_manufacturer/Manufacturer',
        ],
        title="Manufacturer Filter",
        optional=True,
        )

    show_table(
        gvar,
        response['cores'],
        [
            'cores/Cores',
        ],
        title="Cores Filter",
        optional=True,
        )

    show_table(
        gvar,
        response['ec2_instance_types'],
        [
            'region/Region,k',
            'instance_type/Instance Type',
            'operating_system/Operating System',
            'instance_family/Family',
            'processor/Processor',
            'processor_manufacturer/Manufacturer',
            'cores/Cores',
            'memory/Memory',
            'memory_per_core/Memory per Core',
            'storage/Storage',
            'cost_per_hour/Cost per Hour',
        ],
        title="EC2 Instance Types",
        )

