from csv2_common import check_keys, requests, show_active_user_groups, show_table, verify_yaml_file
from subprocess import Popen, PIPE

import filecmp
import os

KEY_MAP = {
    '-in':  'image_name',
    '-ic':  'image_checksum',
    '-tc':  'cloud_name', #target cloud
    '-cl':  'cloud_list',
    '-df':  'disk_format',
    '-ip':  'image_path',
    '-id':  'image_date',
    '-ii':  'image_index',
    '-g':   'group_name',
    }

COMMAS_TO_NL = str.maketrans(',','\n')


def upload(gvar):
    """
    Upload Image to a list of clouds.
    Can provide a file OR a url
    Requires: Image file OR Image url, cloud_list, disk_format
    """

    disk_formats = ['ami', 'aki', 'ari', 'docker', 'iso', 'ova', 'qcow2', 'raw', 'vdi', 'vhd', 'vmdk']

    mandatory = []
    required = []
    optional = ['-g', '-s', '-v', '-x509', '-xA']

    """
    Will need to audit the disk format
    """

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    form_data = check_keys(
        gvar,
        mandatory,
        required,
        optional,
        key_map=KEY_MAP)

    #Upload Image, will likely need to change this request since we are uploading a file

    # NEED TO ISOLATE GROUP NAME FOR URL
    # group_name=??
    response = requests(
        gvar,
        '/images/upload_image/%s' % group_name,
        form_data
        )
    
    if response['message']:
        print(response['message'])

def transfer(gvar):
    """
    Transfers a target image to a target cloud
    Requrires: image_name, target_cloud, target_group
    Optional: image_checksum
    """

    mandatory = ['-tc']
    required = []
    optional = ['-ic', '-in', '-ii', '-g', '-s', '-v', '-x509', '-xA']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # need to build special form data, the image key is a composite of:
    # (image_name + '---' + image_checksum)
    #
    # Alternatively modify the server side code to handle the keys individually.
    #
    # Transfer needs to be extended to accept image_index and image_date (2 formats)

    # Check for missing arguments or help required.
    form_data = check_keys(
        gvar,
        mandatory,
        required,
        optional,
        key_map=KEY_MAP)

    # Send transfer request.
    response = requests(
        gvar,
        '/images/transfer/',
        form_data
    )
    
    if response['message']:
        print(response['message'])


def delete(gvar):
    """
    Deletes a target image from a target group.
    Requrires: image_name, target_cloud, target_group
    Optional: image_checksum
    """

    mandatory = []
    required = []
    optional = ['-v', '-x509', '-xA']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    form_data = check_keys(
        gvar,
        mandatory,
        required,
        optional,
        key_map=KEY_MAP)


    # Delete the image.
    response = requests(
        gvar,
        '/images/delete/',
        form_data
        )
    
    if response['message']:
        print(response['message'])

def list(gvar):
    """
    List images for the active or specified group (and optionlally cloud).
    """

    mandatory = []
    required = []
    optional = ['-g', '-s', '-cn', '-v', '-x509', '-xA']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    check_keys(
        gvar,   
        mandatory,
        required,
        optional)

    # Retrieve data (possibly after changing the group). 
    if "cloud_name" in gvar:
        qd= {
            "cloud_name": gvar["cloud-name"]
        }
        response = requests(gvar, '/images/image_list/', query_data=gvar)
    else:
        response = requests(gvar, '/images/image_list/')

    if response['message']:
        print(response['message'])

    # Filter response as requested (or not).
    image_list = response['image_list']

    # Print report. 
    show_active_user_groups(gvar, response)
    
    show_table(
        gvar,   
        image_list,
        [
            'rank,Image Number',
            'group_name/Group,k',
            'cloud_name/Cloud,k',
            'name/Name/Image Info',
            'created_at/Creation Date/Image Info',
            'checksum/Checksum/Image Info',
        ],

        title="Images",
    )       

