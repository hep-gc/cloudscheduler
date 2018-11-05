from django.conf import settings
config = settings.CSV2_CONFIG

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import requires_csrf_token
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from django.contrib.auth.models import User #to get auth_user table
from .models import user as csv2_user

from .view_utils import \
    diff_lists, \
    getAuthUser, \
    getcsv2User, \
    getSuperUserStatus, \
    lno, \
    qt, \
    qt_filter_get, \
    render, \
    service_msg, \
    set_user_groups, \
    table_fields, \
    validate_by_filtered_table_entries, \
    validate_fields, \
    verifyUser
from collections import defaultdict
import bcrypt

from sqlalchemy import exists
from sqlalchemy.sql import select
from cloudscheduler.lib.schema import *
import sqlalchemy.exc
#import subprocess
import os
import psutil

#from silk.profiling.profiler import silk_profile as silkp

# lno: CV - error code identifier.

#-------------------------------------------------------------------------------

CLOUD_KEYS = {
    'auto_active_group': True,
    # Named argument formats (anything else is a string).
    'format': {
        'cloud_name':                           'lowerdash',
        'cloud_type':                           ('csv2_cloud_types', 'cloud_type'),
        'enabled':                              'dboolean',
        'cores_ctl':                            'integer',
        'metadata_name':                        'ignore',
        'metadata_option':                      ['add', 'delete'],
        'ram_ctl':                              'integer',
        'spot_price':                           'integer',
        'vm_keep_alive':                        'integer',

        'cores_slider':                         'ignore',
        'csrfmiddlewaretoken':                  'ignore',
        'group':                                'ignore',
        'ram_slider':                           'ignore',

        'server_meta_ctl':                      'reject',
        'instances_ctl':                        'reject',
        'personality_ctl':                      'reject',
        'image_meta_ctl':                       'reject',
        'personality_size_ctl':                 'reject',
        'server_groups_ctl':                    'reject',
        'security_group_rules_ctl':             'reject',
        'keypairs_ctl':                         'reject',
        'security_groups_ctl':                  'reject',
        'server_group_members_ctl':             'reject',
        'floating_ips_ctl':                     'reject',
        },
    'mandatory': [
        'cloud_name',
        ],
    'not_empty': [
        'authurl',
        'project',
        'username',
        'password',
        'region',
        ],
    }

METADATA_KEYS = {
    'auto_active_group': True,
    # Named argument formats (anything else is a string).
    'format': {
        'cloud_name':                           'lowerdash',
        'enabled':                              'dboolean',
        'priority':                             'integer',
        'metadata':                             'metadata',
        'metadata_name':                        'lowercase',
        'mime_type':                            ('csv2_mime_types', 'mime_type'),

        'csrfmiddlewaretoken':                  'ignore',
        'group':                                'ignore',
        },
    'mandatory': [
        'cloud_name',
        'metadata_name',
        ],
    }

IGNORE_METADATA_NAME = {
    'format': {
        'metadata_name':                         'ignore',
        },
    }

LIST_KEYS = {
    # Named argument formats (anything else is a string).
    'format': {
        'csrfmiddlewaretoken':                  'ignore',
        'group':                                'ignore',
        },
    }

METADATA_LIST_KEYS = {
    # Named argument formats (anything else is a string).
    'format': {
        'csrfmiddlewaretoken':                  'ignore',
        'group':                                'ignore',
        },
    }

#-------------------------------------------------------------------------------

#@silkp(name="Cloud Manage Metadata Exclusions")
def manage_group_metadata_exclusions(tables, active_group, cloud_name, metadata_names, option=None):
    """
    Ensure all the specified metadata exclusions (metadata_names) and only the specified
    metadata exclusions are defined for the specified cloud. The specified cloud and
    exclusions have all been pre-verified.
    """

    table = tables['csv2_group_metadata_exclusions']

    # if there is only one metadata_name, make it a list anyway
    if metadata_names:
        if isinstance(metadata_names, str):
            metadata_name_list = metadata_names.split(',')
        else:
            metadata_name_list = metadata_names
    else:
        metadata_name_list = []

    # Retrieve the list of metadata exclusions the cloud already has.
    exclusions=[]
    
    s = select([table]).where((table.c.group_name==active_group) & (table.c.cloud_name==cloud_name))
    exclusion_list = qt(config.db_connection.execute(s))

    for row in exclusion_list:
        exclusions.append(row['metadata_name'])

    if not option or option == 'add':
        # Get the list of metadata exclusions (metadata_names) specified that the cloud doesn't already have.
        add_exclusions = diff_lists(metadata_name_list, exclusions)

        # Add the missing exclusions.
        for metadata_name in add_exclusions:
            rc, msg = config.db_session_execute(table.insert().values(group_name=active_group, cloud_name=cloud_name, metadata_name=metadata_name))
            if rc != 0:
                return 1, msg

    if not option:
        # Get the list of metadata exclusions (metadata_names) that the cloud currently has but were not specified.
        remove_exclusions = diff_lists(exclusions, metadata_name_list)
        
        # Remove the extraneous exclusions.
        for metadata_name in remove_exclusions:
            rc, msg = config.db_session_execute(table.delete((table.c.group_name==active_group) & (table.c.cloud_name==cloud_name) & (table.c.metadata_name==metadata_name)))
            if rc != 0:
                return 1, msg

    elif option == 'delete':
        # Get the list of metadata exclusions (metadata_names) that the cloud currently has and were specified.
        remove_exclusions = diff_lists(metadata_name_list, exclusions, option='and')
        
        # Remove the extraneous exclusions.
        for metadata_name in remove_exclusions:
            rc, msg = config.db_session_execute(table.delete((table.c.group_name==active_group) & (table.c.cloud_name==cloud_name) & (table.c.metadata_name==metadata_name)))
            if rc != 0:
                return 1, msg

    return 0, None

#-------------------------------------------------------------------------------

#@silkp(name="Cloud Manage Group Metadata Verification")
def manage_group_metadata_verification(tables, active_group, cloud_names, metadata_names):
    """
    Make sure the specified cloud, and metadata names exist.
    """

    if cloud_names:
        # if there is only one cloud, make it a list anyway
        if isinstance(cloud_names, str):
            cloud_name_list = cloud_names.split(',')
        else:
            cloud_name_list = cloud_names

        # Get the list of valid clouds.
        table = tables['csv2_group_resources']
        s = select([table]).where(table.c.group_name==active_group)
        cloud_list = qt(config.db_connection.execute(s))

        valid_clouds = {}
        for row in cloud_list:
            valid_clouds[row['cloud_name']] = False

        # Check the list of specified clouds.
        for cloud in cloud_name_list:
            if cloud not in valid_clouds:
                return 1, 'specified cloud "%s::%s" does not exist' % (active_group, cloud)
            elif valid_clouds[cloud]:
                return 1, 'cloud "%s" was specified twice' % cloud
            else:
                valid_clouds[cloud] = True

    if metadata_names:
        # if there is only one metadata name, make it a list anyway
        if isinstance(metadata_names, str):
            metadata_name_list = metadata_names.split(',')
        else:
            metadata_name_list = metadata_names

        # Get the list of valid metadata names.
        table = tables['csv2_group_metadata']
        s = select([table]).where(table.c.group_name==active_group)
        metadata_list = qt(config.db_connection.execute(s))

        valid_metadata = {}
        for row in metadata_list:
            valid_metadata[row['metadata_name']] = False

        # Check the list of specified metadata names.
        for metadata_name in metadata_name_list:
            if metadata_name not in valid_metadata:
                return 1, 'specified metadata_name "%s" does not exist' % metadata_name
            elif valid_metadata[metadata_name]:
                return 1, 'metadata name "%s" was specified twice' % metadata_name
            else:
                valid_metadata[metadata_name] = True

    return 0, None

#-------------------------------------------------------------------------------

#@silkp(name="Cloud Add")
@requires_csrf_token
def add(request):
    """
    This function should recieve a post request with a payload of cloud configuration
    to add a cloud to a given group.
    """

    if not verifyUser(request):
        raise PermissionDenied

    if request.method == 'POST':
        # open the database.
        config.db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(config, request)
        if rc != 0:
            config.db_close()
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('CV00'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(config, request, [CLOUD_KEYS], ['csv2_group_resources', 'csv2_group_metadata,n', 'csv2_group_metadata_exclusions,n'], active_user)
        if rc != 0: 
            config.db_close()
            return list(request, selector='-', response_code=1, message='%s cloud add %s' % (lno('CV01'), msg), active_user=active_user, user_groups=user_groups)

        if 'vm_flavor' in fields and fields['vm_flavor']:
            rc, msg = validate_by_filtered_table_entries(config, fields['vm_flavor'], 'vm_flavor', 'cloud_flavors', 'name', [['group_name', fields['group_name']], ['cloud_name', fields['cloud_name']]])
            if rc != 0:
                config.db_close()
                return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud add, "%s" failed - %s.' % (lno('CV96'), fields['cloud_name'], msg), active_user=active_user, user_groups=user_groups)

        if 'vm_image' in fields and fields['vm_image']:
            rc, msg = validate_by_filtered_table_entries(config, fields['vm_image'], 'vm_image', 'cloud_images', 'name', [['group_name', fields['group_name']], ['cloud_name', fields['cloud_name']]])
            if rc != 0:
                config.db_close()
                return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud add, "%s" failed - %s.' % (lno('CV97'), fields['cloud_name'], msg), active_user=active_user, user_groups=user_groups)

        if 'vm_keyname' in fields and fields['vm_keyname']:
            rc, msg = validate_by_filtered_table_entries(config, fields['vm_keyname'], 'vm_keyname', 'cloud_keypairs', 'name', [['group_name', fields['group_name']], ['cloud_name', fields['cloud_name']]])
            if rc != 0:
                config.db_close()
                return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud add, "%s" failed - %s.' % (lno('CV95'), fields['cloud_name'], msg), active_user=active_user, user_groups=user_groups)

        if 'vm_network' in fields and fields['vm_network']:
            rc, msg = validate_by_filtered_table_entries(config, fields['vm_network'], 'vm_network', 'cloud_networks', 'name', [['group_name', fields['group_name']], ['cloud_name', fields['cloud_name']]])
            if rc != 0:
                config.db_close()
                return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud add, "%s" failed - %s.' % (lno('CV95'), fields['cloud_name'], msg), active_user=active_user, user_groups=user_groups)

        # Validity check the specified metadata exclusions.
        if 'metadata_name' in fields:
            rc, msg = manage_group_metadata_verification(tables, fields['group_name'], None, fields['metadata_name']) 
            if rc != 0:
                config.db_close()
                return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud add, "%s" failed - %s.' % (lno('CV03'), fields['cloud_name'], msg), active_user=active_user, user_groups=user_groups)

        # Add the cloud.
        table = tables['csv2_group_resources']
        rc, msg = config.db_session_execute(table.insert().values(table_fields(fields, table, columns, 'insert')))
        if rc != 0:
            config.db_close()
            return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud add "%s::%s" failed - %s.' % (lno('CV02'), fields['group_name'], fields['cloud_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

        # Add the cloud's group metadata exclusions.
        if 'metadata_name' in fields:
            rc, msg = manage_group_metadata_exclusions(tables, fields['group_name'], fields['cloud_name'], fields['metadata_name'])

        if rc == 0:
            config.db_close(commit=True)
            return list(request, selector=fields['cloud_name'], response_code=0, message='cloud "%s::%s" successfully added.' % (fields['group_name'], fields['cloud_name']), active_user=active_user, user_groups=user_groups, attributes=columns)
        else:
            config.db_close()
            return list(request, selector=fields['cloud_name'], response_code=1, message='%s add group metadata exclusion for cloud "%s::%s" failed - %s.' % (lno('CV02'), fields['group_name'], fields['cloud_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)
                    
    ### Bad request.
    else:
        return list(request, response_code=1, message='%s cloud add, invalid method "%s" specified.' % (lno('CV03'), request.method))

#-------------------------------------------------------------------------------

#@silkp(name="Cloud Delete")
@requires_csrf_token
def delete(request):
    """
 function should recieve a post request with a payload of cloud name
    to be deleted.
    """

    if not verifyUser(request):
        raise PermissionDenied

    if request.method == 'POST':
        # open the database.
        config.db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(config, request)
        if rc != 0:
            config.db_close()
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('CV05'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(config, request, [CLOUD_KEYS, IGNORE_METADATA_NAME], ['csv2_group_resources', 'csv2_group_resource_metadata', 'csv2_group_metadata_exclusions'], active_user)
        if rc != 0:
            config.db_close()
            return list(request, selector='-', response_code=1, message='%s cloud delete %s' % (lno('CV06'), msg), active_user=active_user, user_groups=user_groups)

        # Delete any metadata files for the cloud.
        table = tables['csv2_group_resource_metadata']
        rc, msg = config.db_session_execute(table.delete((table.c.group_name==fields['group_name']) & (table.c.cloud_name==fields['cloud_name'])), allow_no_rows=True)
        if rc != 0:
            config.db_close()
            return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud metadata-delete "%s::%s.*" failed - %s.' % (lno('CV07'), fields['group_name'], fields['cloud_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

        # Delete any metadata exclusions files for the cloud.
        table = tables['csv2_group_metadata_exclusions']
        rc, msg = config.db_session_execute(table.delete((table.c.group_name==fields['group_name']) & (table.c.cloud_name==fields['cloud_name'])), allow_no_rows=True)
        if rc != 0:
            config.db_close()
            return list(request, selector=fields['cloud_name'], response_code=1, message='%s delete group metadata exclusion for cloud "%s::%s" failed - %s.' % (lno('CV07'), fields['group_name'], fields['cloud_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

        # Delete the cloud.
        table = tables['csv2_group_resources']
        rc, msg = config.db_session_execute(
            table.delete((table.c.group_name==fields['group_name']) & (table.c.cloud_name==fields['cloud_name']))
            )
        if rc == 0:
            config.db_close(commit=True)
            return list(request, selector=fields['cloud_name'], response_code=0, message='cloud "%s::%s" successfully deleted.' % (fields['group_name'], fields['cloud_name']), active_user=active_user, user_groups=user_groups, attributes=columns)
        else:
            config.db_close()
            return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud delete "%s::%s" failed - %s.' % (lno('CV08'), fields['group_name'], fields['cloud_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

    ### Bad request.
    else:
        return list(request, response_code=1, message='%s cloud delete, invalid method "%s" specified.' % (lno('CV09'), request.method))

#-------------------------------------------------------------------------------

#@silkp(name='Cloud List')
@requires_csrf_token
def list(
    request,
    selector=None,
    group_name=None,
    response_code=0,
    message=None,
    active_user=None,
    user_groups=None,
    attributes=None
    ):

    if not verifyUser(request):
        raise PermissionDenied

    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    if not active_user:
        rc, msg, active_user, user_groups = set_user_groups(config, request)
        if rc != 0:
            config.db_close()
            return render(request, 'csv2/clouds.html', {'response_code': 1, 'message': msg})

    # Validate input fields (should be none).
    if not message:
        rc, msg, fields, tables, columns = validate_fields(config, request, [LIST_KEYS], [], active_user)
        if rc != 0:
            config.db_close()
            return render(request, 'csv2/clouds.html', {'response_code': 1, 'message': '%s cloud list, %s' % (lno('CV11'), msg)})

    s = select([csv2_cloud_types])
    type_list = qt(config.db_connection.execute(s))

    # Retrieve cloud information.
    if request.META['HTTP_ACCEPT'] == 'application/json':
        s = select([view_group_resources_with_metadata_names]).where(view_group_resources_with_metadata_names.c.group_name == active_user.active_group)
        cloud_list = qt(config.db_connection.execute(s), prune=['password'])
        image_list = {}
        flavor_list = {}
        metadata_dict = {}
        keypairs_list = {}
        network_list = {}
    else:
        # Get all the images in group:
        s = select([cloud_images]).where(cloud_images.c.group_name==active_user.active_group)
        image_list = qt(config.db_connection.execute(s))

        # Get all the flavors in group:
        s = select([cloud_flavors]).where(cloud_flavors.c.group_name==active_user.active_group)
        flavor_list = qt(config.db_connection.execute(s))

        # Get all the keynames in group:
        s = select([cloud_keypairs]).where(cloud_keypairs.c.group_name==active_user.active_group)
        keypairs_list = qt(config.db_connection.execute(s))

        # Get all the networks in group:
        s = select([cloud_networks]).where(cloud_networks.c.group_name==active_user.active_group)
        network_list = qt(config.db_connection.execute(s))

        s = select([view_group_resources_with_metadata_info]).where(view_group_resources_with_metadata_info.c.group_name == active_user.active_group)
        cloud_list, metadata_dict = qt(
            config.db_connection.execute(s),
            keys = {
                'primary': [
                    'group_name',
                    'cloud_name'
                    ],
                'secondary': [
                    'metadata_name',
                    'metadata_enabled',
                    'metadata_priority',
                    'metadata_mime_type',
                    ]
                },
            prune=['password']    
            )

        config.db_close()

    # Position the page.
    obj_act_id = request.path.split('/')
    if selector:
        if selector == '-':
            current_cloud = ''
        else:
            current_cloud = selector
    elif len(obj_act_id) > 3 and len(obj_act_id[3]) > 0:
        current_cloud = str(obj_act_id[3])
    else:
        if len(cloud_list) > 0:
            current_cloud = str(cloud_list[0]['cloud_name'])
        else:
            current_cloud = ''

    # Render the page.
    context = {
            'active_user': active_user,
            'active_group': active_user.active_group,
            'attributes': attributes,
            'user_groups': user_groups,
            'cloud_list': cloud_list,
            'type_list': type_list,
            'metadata_dict': metadata_dict,
            'image_list': image_list,
            'flavor_list': flavor_list,
            'keypairs_list': keypairs_list,
            'network_list': network_list,
            'current_cloud': current_cloud,
            'response_code': response_code,
            'message': message,
            'enable_glint': config.enable_glint
        }

    return render(request, 'csv2/clouds.html', context)

#-------------------------------------------------------------------------------

#@silkp(name='Cloud Metadata Add')
@requires_csrf_token
def metadata_add(request):
    """
    This function should recieve a post request with a payload of metadata configuration
    to add to a given group/cloud.
    """

    if not verifyUser(request):
        raise PermissionDenied

    if request.method == 'POST':
        # open the database.
        config.db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(config, request)
        if rc != 0:
            config.db_close()
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('CV12'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(config, request, [METADATA_KEYS], ['csv2_group_resource_metadata', 'csv2_group_resources,n'], active_user)
        if rc != 0:
            config.db_close()
            return list(request, selector='-', response_code=1, message='%s cloud metadata-add %s' % (lno('CV13'), msg), active_user=active_user, user_groups=user_groups)

        # Check cloud already exists.
        table = tables['csv2_group_resources']
        s = select([csv2_group_resources]).where(csv2_group_resources.c.group_name == active_user.active_group)
        cloud_list = config.db_connection.execute(s)
        found = False
        for cloud in cloud_list:
            if active_user.active_group == cloud['group_name'] and fields['cloud_name'] == cloud['cloud_name']:
                found = True
                break

        if not found:
            return list(request, selector='-', response_code=1, message='%s cloud metadata-add failed, cloud name  "%s" does not exist.' % (lno('CV14'), fields['cloud_name']), active_user=active_user, user_groups=user_groups)

        # Add the cloud metadata file.
        table = tables['csv2_group_resource_metadata']
        rc, msg = config.db_session_execute(table.insert().values(table_fields(fields, table, columns, 'insert')))
        if rc == 0:
            config.db_close(commit=True)
            return list(request, selector=fields['cloud_name'], response_code=0, message='cloud metadata file "%s::%s::%s" successfully added.' % (fields['group_name'], fields['cloud_name'], fields['metadata_name']), active_user=active_user, user_groups=user_groups, attributes=columns)
        else:
            config.db_close()
            return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud metadata-add "%s::%s::%s" failed - %s.' % (lno('CV15'), fields['group_name'], fields['cloud_name'], fields['metadata_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

    ### Bad request.
    else:
        return list(request, response_code=1, message='%s cloud metadata_add, invalid method "%s" specified.' % (lno('CV16'), request.method))

#-------------------------------------------------------------------------------

#@silkp(name="Cloud Metadata Add")
@requires_csrf_token
def metadata_collation(request):

    if not verifyUser(request):
        raise PermissionDenied

    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user, user_groups = set_user_groups(config, request)
    if rc != 0:
        config.db_close()
        return render(request, 'csv2/clouds_metadata_list.html', {'response_code': 1, 'message': '%s cloud metadata-list, %s' % (lno('CV18'), msg)})

    # Validate input fields (should be none).
    rc, msg, fields, tables, columns = validate_fields(config, request, [METADATA_LIST_KEYS], [], active_user)
    if rc != 0:
        config.db_close()
        return render(request, 'csv2/clouds_metadata_list.html', {'response_code': 1, 'message': '%s cloud metadata-list, %s' % (lno('CV19'), msg)})

    # Retrieve cloud/metadata information.
    s = select([view_metadata_collation]).where(view_metadata_collation.c.group_name == active_user.active_group)
    cloud_metadata_list = qt(config.db_connection.execute(s))

    config.db_close()

    # Render the page.
    context = {
            'active_user': active_user,
            'active_group': active_user.active_group,
            'user_groups': user_groups,
            'cloud_metadata_list': cloud_metadata_list,
            'response_code': 0,
            'message': None,
            'enable_glint': config.enable_glint
        }

    return render(request, 'csv2/cloud_metadata_list.html', context)

#-------------------------------------------------------------------------------

#@silkp(name='Cloud Metadata Delete')
@requires_csrf_token
def metadata_delete(request):
    """
    This function should recieve a post request with a payload of metadata configuration
    to add to a given group/cloud.
    """

    if not verifyUser(request):
        raise PermissionDenied

    if request.method == 'POST':
        # open the database.
        config.db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(config, request)
        if rc != 0:
            config.db_close()
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('CV20'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(config, request, [METADATA_KEYS], ['csv2_group_resource_metadata'], active_user)
        if rc != 0:
            config.db_close()
            return list(request, selector='-', response_code=1, message='%s cloud metadata-delete %s' % (lno('CV21'), msg), active_user=active_user, user_groups=user_groups)

        # Delete the cloud metadata file.
        table = tables['csv2_group_resource_metadata']
        rc, msg = config.db_session_execute(
            table.delete( \
                (table.c.group_name==fields['group_name']) & \
                (table.c.cloud_name==fields['cloud_name']) & \
                (table.c.metadata_name==fields['metadata_name']) \
                )
            )
        if rc == 0:
            config.db_close(commit=True)
            return list(request, selector=fields['cloud_name'], response_code=0, message='cloud metadata file "%s::%s::%s" successfully deleted.' % (fields['group_name'], fields['cloud_name'], fields['metadata_name']), active_user=active_user, user_groups=user_groups, attributes=columns)
        else:
            config.db_close()
            return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud metadata-delete "%s::%s::%s" failed - %s.' % (lno('CV22'), fields['group_name'], fields['cloud_name'], fields['metadata_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

    ### Bad request.
    else:
        return list(request, response_code=1, message='%s cloud metadata_delete, invalid method "%s" specified.' % (lno('CV23'), request.method))

#-------------------------------------------------------------------------------

#@silkp(name="Cloud Metadata Fetch")
@requires_csrf_token
def metadata_fetch(request, selector=None):
    if not verifyUser(request):
        raise PermissionDenied

    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user, user_groups = set_user_groups(config, request)
    if rc != 0:
        config.db_close()
        return list(request, selector='-', response_code=1, message='%s %s' % (lno('CV25'), msg), active_user=active_user, user_groups=user_groups)

    # Get mime type list:
    s = select([csv2_mime_types])
    mime_types_list = qt(config.db_connection.execute(s))

    # Retrieve metadata file.
    obj_act_id = request.path.split('/') # /cloud/metadata_fetch/<group>.<cloud>.<metadata>
    if len(obj_act_id) > 3:
        id = obj_act_id[3]
        ids = id.split('::')
        if len(ids) == 2:
            METADATA = config.db_map.classes.csv2_group_resource_metadata
            METADATAobj = config.db_session.query(METADATA).filter((METADATA.group_name == active_user.active_group) & (METADATA.cloud_name==ids[0]) & (METADATA.metadata_name==ids[1]))
            if METADATAobj:
                for row in METADATAobj:
                    context = {
                        'group_name': row.group_name,
                        'cloud_name': row.cloud_name,
                        'metadata': row.metadata,
                        'metadata_enabled': row.enabled,
                        'metadata_priority': row.priority,
                        'metadata_mime_type': row.mime_type,
                        'metadata_name': row.metadata_name,
                        'mime_types_list': mime_types_list,
                        'response_code': 0,
                        'message': None,
                        'enable_glint': config.enable_glint
                        }

                    config.db_close()
                    return render(request, 'csv2/meta_editor.html', context)


    config.db_close()

    if id:
      return render(request, 'csv2/meta_editor.html', {'response_code': 1, 'message': 'cloud metadata_fetch, received an invalid metadata file id "%s::%s".' % (active_user.active_group, id)})
    else:
      return render(request, 'csv2/meta_editor.html', {'response_code': 1, 'message': 'cloud metadata_fetch, metadata file id omitted.'})

#-------------------------------------------------------------------------------

#@silkp(name="Cloud Metadata List")
@requires_csrf_token
def metadata_list(request):

    if not verifyUser(request):
        raise PermissionDenied

    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user, user_groups = set_user_groups(config, request)
    if rc != 0:
        config.db_close()
        return render(request, 'csv2/clouds_metadata_list.html', {'response_code': 1, 'message': '%s cloud metadata-list, %s' % (lno('CV26'), msg)})

    # Validate input fields (should be none).
    rc, msg, fields, tables, columns = validate_fields(config, request, [METADATA_LIST_KEYS], [], active_user)
    if rc != 0:
        config.db_close()
        return render(request, 'csv2/clouds_metadata_list.html', {'response_code': 1, 'message': '%s cloud metadata-list, %s' % (lno('CV27'), msg)})

    # Retrieve cloud/metadata information.
    s = select([csv2_group_resource_metadata]).where(csv2_group_resource_metadata.c.group_name == active_user.active_group)
    cloud_metadata_list = qt(config.db_connection.execute(s))
    


    # Retrieve group/metadata information.
    s = select([view_groups_with_metadata_names]).where(view_groups_with_metadata_names.c.group_name == active_user.active_group)
    group_metadata_names = qt(config.db_connection.execute(s))

    # Retrieve cloud/metadata information.
    s = select([view_group_resources_with_metadata_names]).where(view_group_resources_with_metadata_names.c.group_name == active_user.active_group)
    cloud_metadata_names = qt(config.db_connection.execute(s))

    config.db_close()

    # Render the page.
    context = {
            'active_user': active_user,
            'active_group': active_user.active_group,
            'user_groups': user_groups,
            'cloud_metadata_list': cloud_metadata_list,
            'group_metadata_names': group_metadata_names,
            'cloud_metadata_names': cloud_metadata_names,
            'response_code': 0,
            'message': None,
            'enable_glint': config.enable_glint
        }

    return render(request, 'csv2/metadata-list.html', context)

#-------------------------------------------------------------------------------
#@silkp(name="Cloud Metadata Fetch")
@requires_csrf_token
def metadata_new(request, selector=None):
    if not verifyUser(request):
        raise PermissionDenied

    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user, user_groups = set_user_groups(config, request)
    if rc != 0:
        config.db_close()
        return list(request, selector='-', response_code=1, message='%s %s' % (lno('CV25'), msg), active_user=active_user, user_groups=user_groups)

    # Get mime type list:
    s = select([csv2_mime_types])
    mime_types_list = qt(config.db_connection.execute(s))

    # Retrieve metadata file.
    obj_act_id = request.path.split('/') # /cloud/metadata_add/<group>.<cloud>.<metadata>
    if len(obj_act_id) > 3:
        cloud_name = obj_act_id[3]

        context = {
            'group_name': active_user.active_group,
            'cloud_name': cloud_name,
            'metadata': "",
            'metadata_enabled': 0,
            'metadata_priority': 0,
            'metadata_mime_type': "",
            'metadata_name': "",
            'mime_types_list': mime_types_list,
            'response_code': 0,
            'message': "new-cloud-metadata",
            'enable_glint': config.enable_glint
            }

        config.db_close()
        return render(request, 'csv2/meta_editor.html', context)


    config.db_close()

    return render(request, 'csv2/meta_editor.html', {'response_code': 1, 'message': 'cloud metadata_new, received an invalid request: "%s".' % obj_act_id })

#-------------------------------------------------------------------------------
#@silkp(name="Cloud Metadata Update")
@requires_csrf_token
def metadata_update(request):
    """
    This function should recieve a post request with a payload of metadata configuration
    to add to a given group/cloud.
    """

    if not verifyUser(request):
        raise PermissionDenied

    if request.method == 'POST':
        # open the database.
        config.db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(config, request)
        if rc != 0:
            config.db_close()
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('CV28'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(config, request, [METADATA_KEYS], ['csv2_group_resource_metadata'], active_user)
        if rc != 0:
            config.db_close()
            return list(request, selector='-', response_code=1, message='%s cloud metadata-update %s' % (lno('CV29'), msg), active_user=active_user, user_groups=user_groups)

        # Update the cloud metadata file.
        table = tables['csv2_group_resource_metadata']
        rc, msg = config.db_session_execute(table.update().where( \
            (table.c.group_name==fields['group_name']) & \
            (table.c.cloud_name==fields['cloud_name']) & \
            (table.c.metadata_name==fields['metadata_name']) \
            ).values(table_fields(fields, table, columns, 'update')))
        if rc == 0:
            if not 'metadata' in fields.keys():
                s = table.select(
                    (table.c.group_name==fields['group_name']) & \
                    (table.c.cloud_name==fields['cloud_name']) & \
                    (table.c.metadata_name==fields['metadata_name'])
                    )
                metadata_list = qt(config.db_connection.execute(s))
                if len(metadata_list) != 1:
                    return list(request, selector='-', response_code=1, message='%s cloud metadata-update could not retrieve metadata' % (lno('CV99')), active_user=active_user, user_groups=user_groups)
                metadata = metadata_list[0]
            else:
                metadata = fields['metadata']

            config.db_close(commit=True)

            message='cloud metadata file "%s::%s::%s" successfully  updated.' % (fields['group_name'], fields['cloud_name'], fields['metadata_name'])
            context = {
                    'group_name': fields['group_name'],
                    'cloud_name': fields['cloud_name'],
                    'metadata': metadata,
                    'response_code': 0,
                    'message': message,
                }

            return render(request, 'csv2/meta_editor.html', context)
        else:
            config.db_close()
            return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud metadata-update "%s::%s::%s" failed - %s.' % (lno('CV30'), fields['group_name'], fields['cloud_name'], fields['metadata_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

    ### Bad request.
    else:
        return list(request, response_code=1, message='%s cloud metadata_update, invalid method "%s" specified.' % (lno('CV31'), request.method))

#-------------------------------------------------------------------------------

#@silkp(name="Cloud Status")
@requires_csrf_token
def status(request, group_name=None):
    """
    This function generates a the status of a given groups operations
    VM status, job status, and machine status should all be available for a given group on this page
    """

    if not verifyUser(request):
        raise PermissionDenied

    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user, user_groups = set_user_groups(config, request)
    if rc != 0:
        config.db_close()
        return list(request, selector='-', response_code=1, message='%s %s' % (lno('CV33'), msg), active_user=active_user, user_groups=user_groups)

    # get cloud status per group
    s = select([view_cloud_status]).where(view_cloud_status.c.group_name == active_user.active_group)
    cloud_status_list = qt(config.db_connection.execute(s), filter='cols["enabled"] == 1 or cols["VMs"] > 0')

    # calculate the totals for all rows
    cloud_status_list_totals = qt(cloud_status_list, keys={
        'primary': ['group_name'],
        'sum': [
            'VMs',
            'VMs_unregistered',
            'VMs_running',
            'VMs_retiring',
            'VMs_manual',
            'VMs_in_error',
            'VMs_other',
            'Foreign_VMs',
            'cores_max',
            'cores_busy',
            'cores_foreign',
            'cores_idle',
            'cores_native',
                                'ram_max',
                                'ram_busy',
                                'ram_foreign',
                                'ram_idle',
                                'ram_native',
                                'slots_max',
            'slots_used'
            ]
        })

    cloud_total_list = cloud_status_list_totals[0]

    # find the actual cores limit in use
    cloud_total_list['cores_limit'] = 0
    n=0
    for cloud in cloud_status_list:
        if cloud['cores_ctl'] == -1:
            cloud_status_list[n]['cores_limit'] = cloud['cores_native']
        else:
            cloud_status_list[n]['cores_limit'] = cloud['cores_ctl']

        cloud_total_list['cores_limit'] += cloud_status_list[n]['cores_limit']
        n=n+1


    # get slots type counts
    s = select([view_cloud_status_slots]).where(view_cloud_status_slots.c.group_name == active_user.active_group)
    slot_list = qt(
        config.db_connection.execute(s),
        )

    slot_total_list = qt(slot_list, keys={
        'primary': ['group_name', 'slot_CPUs'],
        'sum': ['slot_count']
        })

    # get job status per group
    s = select([view_job_status]).where(view_job_status.c.group_name == active_user.active_group)
    job_status_list = qt(config.db_connection.execute(s))




    system_list = {}

    system_list["csv2_status_msg"] = service_msg("csv2-status")
    if 'running' in system_list["csv2_status_msg"]:
        system_list["csv2_status_status"] = 1
        # get system status
        s = select([csv2_system_status])
        system_list.update(qt(config.db_connection.execute(s))[0])

    else:
        system_list["csv2_status_status"] = 0

        # Determine the csv2 service statuses and put them in a list

        system_list["csv2_main_msg"] = service_msg("csv2-main")
        if 'running' in system_list["csv2_main_msg"]:
            system_list["csv2_main_status"] = 1
        else:
            system_list["csv2_main_status"] = 0

        system_list["csv2_openstack_msg"] = service_msg("csv2-openstack")
        if 'running' in system_list["csv2_openstack_msg"]:
            system_list["csv2_openstack_status"] = 1
        else:
            system_list["csv2_openstack_status"] = 0

        system_list["csv2_jobs_msg"] = service_msg("csv2-jobs")
        if 'running' in system_list["csv2_jobs_msg"]:
            system_list["csv2_jobs_status"] = 1
        else:
            system_list["csv2_jobs_status"] = 0

        system_list["csv2_machines_msg"] = service_msg("csv2-machines")
        if 'running' in system_list["csv2_machines_msg"]:
            system_list["csv2_machines_status"] = 1
        else:
            system_list["csv2_machines_status"] = 0

        system_list["mariadb_msg"] = service_msg("mariadb")
        if 'running' in system_list["mariadb_msg"]:
            system_list["mariadb_status"] = 1
        else:
            system_list["mariadb_status"] = 0

        system_list["condor_msg"] = service_msg("condor")
        if 'running' in system_list["condor_msg"]:
            system_list["condor_status"] = 1
        else:
            system_list["condor_status"] = 0

        # Determine the system load, RAM and disk usage

        system_list["load"] = round(100*( os.getloadavg()[0] / os.cpu_count() ),1)

        system_list["ram"] = psutil.virtual_memory().percent
        system_list["ram_size"] = round(psutil.virtual_memory().total/1000000000 , 1)
        system_list["ram_used"] = round(psutil.virtual_memory().used/1000000000 , 1)

        system_list["swap"] = psutil.swap_memory().percent
        system_list["swap_size"] = round(psutil.swap_memory().total/1000000000 , 1)
        system_list["swap_used"] = round(psutil.swap_memory().used/1000000000 , 1)


        system_list["disk"] = round(100*(psutil.disk_usage('/').used / psutil.disk_usage('/').total),1)
        system_list["disk_size"] = round(psutil.disk_usage('/').total/1000000000 , 1)
        system_list["disk_used"] = round(psutil.disk_usage('/').used/1000000000 , 1)







    config.db_close()


    context = {
            'active_user': active_user,
            'active_group': active_user.active_group,
            'user_groups': user_groups,
            'cloud_status_list': cloud_status_list,
            'cloud_total_list': cloud_total_list,
            'job_status_list': job_status_list,
            'system_list' : system_list,
            'slot_list' : slot_list,
            'slot_total_list': slot_total_list,
            'response_code': 0,
            'message': None,
            'enable_glint': config.enable_glint
        }

    return render(request, 'csv2/status.html', context)


#-------------------------------------------------------------------------------

#@silkp(name="Cloud Update")
@requires_csrf_token
def update(request):
    """
    This function should recieve a post request with a payload of cloud configuration
    to update a given cloud.
    """

    if not verifyUser(request):
        raise PermissionDenied

    if request.method == 'POST':

        # if the password is blank, remove the password field.
        if request.META['HTTP_ACCEPT'] != 'application/json' and len(request.POST['password']) == 0:
            # create a copy of the dict to make it mutable.
            request.POST = request.POST.copy()

            # remove the password field.
            del request.POST['password']

        # open the database.
        config.db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(config, request)
        if rc != 0:
            config.db_close()
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('CV34'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(config, request, [CLOUD_KEYS], ['csv2_group_resources', 'csv2_group_metadata,n', 'csv2_group_metadata_exclusions,n'], active_user)
        if rc != 0:
            config.db_close()
            return list(request, selector='-', response_code=1, message='%s cloud update %s' % (lno('CV35'), msg), active_user=active_user, user_groups=user_groups)

        if 'vm_flavor' in fields and fields['vm_flavor']:
            rc, msg = validate_by_filtered_table_entries(config, fields['vm_flavor'], 'vm_flavor', 'cloud_flavors', 'name', [['group_name', fields['group_name']], ['cloud_name', fields['cloud_name']]])
            if rc != 0:
                config.db_close()
                return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud update, "%s" failed - %s.' % (lno('CV98'), fields['cloud_name'], msg), active_user=active_user, user_groups=user_groups)

        if 'vm_image' in fields and fields['vm_image']:
            rc, msg = validate_by_filtered_table_entries(config, fields['vm_image'], 'vm_image', 'cloud_images', 'name', [['group_name', fields['group_name']], ['cloud_name', fields['cloud_name']]])
            if rc != 0:
                config.db_close()
                return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud update, "%s" failed - %s.' % (lno('CV99'), fields['cloud_name'], msg), active_user=active_user, user_groups=user_groups)

        if 'vm_keyname' in fields and fields['vm_keyname']:
            rc, msg = validate_by_filtered_table_entries(config, fields['vm_keyname'], 'vm_keyname', 'cloud_keypairs', 'name', [['group_name', fields['group_name']], ['cloud_name', fields['cloud_name']]])
            if rc != 0:
                config.db_close()
                return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud update, "%s" failed - %s.' % (lno('CV94'), fields['cloud_name'], msg), active_user=active_user, user_groups=user_groups)

        if 'vm_network' in fields and fields['vm_network']:
            rc, msg = validate_by_filtered_table_entries(config, fields['vm_network'], 'vm_network', 'cloud_networks', 'name', [['group_name', fields['group_name']], ['cloud_name', fields['cloud_name']]])
            if rc != 0:
                config.db_close()
                return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud update, "%s" failed - %s.' % (lno('CV94'), fields['cloud_name'], msg), active_user=active_user, user_groups=user_groups)

        # Validity check the specified metadata exclusions.
        if 'metadata_name' in fields:
            rc, msg = manage_group_metadata_verification(tables, fields['group_name'], fields['cloud_name'], fields['metadata_name']) 
            if rc != 0:
                config.db_close()
                return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud update, "%s" failed - %s.' % (lno('CV03'), fields['cloud_name'], msg), active_user=active_user, user_groups=user_groups)

        # update the cloud.
        table = tables['csv2_group_resources']
        cloud_updates = table_fields(fields, table, columns, 'update')
        if len(cloud_updates) > 0:
            rc, msg = config.db_session_execute(table.update().where((table.c.group_name==fields['group_name']) & (table.c.cloud_name==fields['cloud_name'])).values(cloud_updates))
            if rc != 0:
                config.db_close()
                return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud update "%s::%s" failed - %s.' % (lno('CV36'), fields['group_name'], fields['cloud_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)
        else:
            if 'metadata_name' not in fields:
                config.db_close()
                return list(request, selector=fields['cloud_name'], response_code=1, message='%s cloud update must specify at least one field to update.' % lno('CV23'), active_user=active_user, user_groups=user_groups)

        # Update the cloud's group metadata exclusions.
        if request.META['HTTP_ACCEPT'] == 'application/json':
            if 'metadata_name' in fields:
                if 'metadata_option' in fields and fields['metadata_option'] == 'delete':
                    rc, msg = manage_group_metadata_exclusions(tables, fields['group_name'], fields['cloud_name'], fields['metadata_name'], option='delete')
                else:
                    rc, msg = manage_group_metadata_exclusions(tables, fields['group_name'], fields['cloud_name'], fields['metadata_name'], option='add')

        else:
            if 'metadata_name' in fields:
                rc, msg = manage_group_metadata_exclusions(tables, fields['group_name'], fields['cloud_name'], fields['metadata_name'])
            else:
                rc, msg = manage_group_metadata_exclusions(tables, fields['group_name'], fields['cloud_name'], None)

        if rc == 0:
            config.db_close(commit=True)
            return list(request, selector=fields['cloud_name'], response_code=0, message='cloud "%s::%s" successfully updated.' % (fields['group_name'], fields['cloud_name']), active_user=active_user, user_groups=user_groups, attributes=columns)
        else:
            config.db_close()
            return list(request, selector=fields['cloud_name'], response_code=1, message='%s update group metadata exclusion for cloud "%s::%s" failed - %s.' % (lno('CV99'), fields['group_name'], fields['cloud_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

    ### Bad request.
    else:
        return list(request, response_code=1, message='%s cloud update, invalid method "%s" specified.' % (lno('CV37'), request.method))

