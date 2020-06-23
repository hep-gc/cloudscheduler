from csv2_common import check_keys, requests, show_active_user_groups, show_table, verify_yaml_file, prepare_file
from subprocess import Popen, PIPE

import filecmp
import os

KEY_MAP = {
    '-in':  'image_name',
    '-ic':  'image_checksum',
    '-tc':  'cloud_name', #target cloud
    '-cl':  'clouds',
    '-df':  'disk_format',
    '-ip':  'image-path',
    '-id':  'image-date',
    '-ii':  'image-index',
    '-g':   'group-name',
    '-cn':  'cloud-name', 
    }

COMMAS_TO_NL = str.maketrans(',','\n')


def upload(gvar):
    """
    Upload Image to a list of clouds.
    Can provide a file OR a url
    Requires: Image file OR Image url, cloud_list, disk_format
    """

    # disk formats will be checked on server side, remember to add these to the manpage
    #disk_formats = ['ami', 'aki', 'ari', 'docker', 'iso', 'ova', 'qcow2', 'raw', 'vdi', 'vhd', 'vmdk']

    mandatory = ['-cl', '-ip', '-df']
    required = []
    optional = ['-g', '-H', '-h', '-s', '-v', '-x509', '-xA']

    """
    Will need to audit the disk format
    """

    if gvar['retrieve_options']:
        return mandatory + required + optional

    #Process cloud list:
    #### MAY HAVE TO DO THIS SERVER SIDE
    #if 'cloud-list' in gvar['user_settings'].keys():
    #    gvar['user_settings']['cloud-list'] = gvar['user_settings']['cloud-list'].replace(" ", "").split(",")

    # Check for missing arguments or help required.
    form_data = check_keys(
        gvar,
        mandatory,
        required,
        optional,
        key_map=KEY_MAP)

    #Upload Image, will likely need to change this request since we are uploading a file

    url_command = '/images/upload_image/'
    prepare_dict = prepare_file(gvar['user_settings']['image-path'])
    if prepare_dict.get("streaming_upload"):
        prepare_dict.pop("streaming_upload")
        response = requests(
            gvar,   
            url_command,
            {       
                **form_data,
                **prepare_dict
            },       
            streaming_upload=True
            )    
    else:
        response = requests(
            gvar,   
            url_command,
            {       
                **form_data,
                **prepare_dict
            })
        
    
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
    optional = ['-ic', '-in', '-ii', '-g', '-H', '-h', '-s', '-v', '-x509', '-xA']

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
    optional = ['-cn', '-ic', '-in', '-ii', '-g', '-H', '-h', '-s', '-v', '-x509', '-xA']

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
    optional = ['-g', '-H', '-h', '-s', '-cn', '-v', '-x509', '-xA']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    form_data = check_keys(
        gvar,   
        mandatory,
        required,
        optional,
        key_map=KEY_MAP)

    response = requests(gvar, '/images/image_list/', form_data)

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
            'rank/Image Index',
            'group_name/Group,k',
            'cloud_name/Cloud,k',
            'name/Name/Image Info',
            'created_at/Creation Date/Image Info',
            'checksum/Checksum/Image Info',
        ],

        title="Images",
    )       

