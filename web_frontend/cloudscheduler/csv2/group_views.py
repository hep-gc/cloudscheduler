from django.conf import settings
config = settings.CSV2_CONFIG

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import requires_csrf_token
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from django.contrib.auth.models import User #to get auth_user table
from .models import user as csv2_user

from .view_utils import \
    getAuthUser, \
    getcsv2User, \
    getSuperUserStatus, \
    lno,  \
    manage_group_users, \
    manage_user_group_verification, \
    qt, \
    render, \
    set_user_groups, \
    table_fields, \
    validate_by_filtered_table_entries, \
    validate_fields, \
    verifyUser
#from glintwebui.utils import set_defaults_changed
from collections import defaultdict
import bcrypt

from sqlalchemy import exists
from sqlalchemy.sql import select
from cloudscheduler.lib.schema import *
import sqlalchemy.exc

#from cloudscheduler.lib.web_profiler import silk_profile as silkp

# lno: GV - error code identifier.

#-------------------------------------------------------------------------------

GROUP_KEYS = {
    'auto_active_group': False,
    # Named argument formats (anything else is a string).
    'format': {
        'group_name':                                 'lowerdash',
        'csrfmiddlewaretoken':                        'ignore',
        'group':                                      'ignore',
        'username':                                   'ignore',
        'user_option':                                ['add', 'delete'],
        'server_meta_ctl':                            'reject',
        'instances_ctl':                              'reject',
        'personality_ctl':                            'reject',
        'image_meta_ctl':                             'reject',
        'job_scratch':                                'reject',
        'personality_size_ctl':                       'reject',
        'server_groups_ctl':                          'reject',
        'security_group_rules_ctl':                   'reject',
        'keypairs_ctl':                               'reject',
        'security_groups_ctl':                        'reject',
        'server_group_members_ctl':                   'reject',
        'floating_ips_ctl':                           'reject',
        },
    'not_empty': [
        'condor_central_manager',
        ],
    }

GROUP_KEYS_ADD = {
    'auto_active_group': False,
    # Named argument formats (anything else is a string).
    'mandatory': [
        'condor_central_manager',
        ],
    }

GROUP_DEFAULTS_KEYS = {
    'auto_active_group': True,
    # Named argument formats (anything else is a string).
    'format': {
        'csrfmiddlewaretoken':                        'ignore',
        'group':                                      'ignore',
        'job_cpus':                                   'integer',
        'job_disk':                                   'integer',
        'job_ram':                                    'integer',
        'job_swap':                                   'integer',
        'vm_keep_alive':                              'integer',

        'job_scratch':                                'reject',
        },
    }

METADATA_KEYS = {
    # Should the active_group be automatically inserted into the primary keys.
    'auto_active_group': True,
    'format': {
        'enabled':                                    'dboolean',
        'priority':                                   'integer',
        'metadata':                                   'metadata',
        'metadata_name':                              'lowercase',
        'mime_type':                                  ('csv2_mime_types', 'mime_type'),

        'csrfmiddlewaretoken':                        'ignore',
        'group':                                      'ignore',
        },
    'mandatory': [
        'metadata_name',
        ],
    }

IGNORE_METADATA_NAME = {
    'format': {
        'metadata_name':                              'ignore',
        },
    }

IGNORE_KEYS = {
    'format': {
        'cloud_name':                                 'ignore',
        'fingerprint':                                'ignore',
        'id':                                         'ignore',
        'key_name':                                   'ignore',
        'name':                                       'ignore',
        'username':                                   'ignore',
        'vmid':                                       'ignore',
        },
    }

LIST_KEYS = {
    # Named argument formats (anything else is a string).
    'format': {
        'csrfmiddlewaretoken':                        'ignore',
        'group':                                      'ignore',
        },
    }

#-------------------------------------------------------------------------------

#@silkp(name='Group Add')
def add(request):
    """
    This function should receive a post request with a payload of group configuration
    to add the specified group.
    """

    if not verifyUser(request):
        raise PermissionDenied
    if not getSuperUserStatus(request):
        raise PermissionDenied

    if request.method == 'POST':
        # open the database.
        config.db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(config, request)
        if rc != 0:
            config.db_close()
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('GV00'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(config, request, [GROUP_KEYS, GROUP_KEYS_ADD], ['csv2_groups', 'csv2_group_defaults', 'csv2_user_groups', 'csv2_user,n'], active_user)
        if rc != 0:
            config.db_close()
            return list(request, selector='-', response_code=1, message='%s group add %s' % (lno('GV01'), msg), active_user=active_user, user_groups=user_groups)

        if 'vm_flavor' in fields and fields['vm_flavor']:
            rc, msg = validate_by_filtered_table_entries(config, fields['vm_flavor'], 'vm_flavor', 'cloud_flavors', 'name', [['group_name', fields['group_name']]])
            if rc != 0:
                config.db_close()
                return list(request, selector='-', response_code=1, message='%s group add, "%s" failed - %s.' % (lno('GV96'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups)

        if 'vm_image' in fields and fields['vm_image']:
            rc, msg = validate_by_filtered_table_entries(config, fields['vm_image'], 'vm_image', 'cloud_images', 'name', [['group_name', fields['group_name']]])
            if rc != 0:
                config.db_close()
                return list(request, selector='-', response_code=1, message='%s group add, "%s" failed - %s.' % (lno('GV97'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups)

        if 'vm_keyname' in fields and fields['vm_keyname']:
            rc, msg = validate_by_filtered_table_entries(config, fields['vm_keyname'], 'vm_keyname', 'cloud_keypairs', 'name', [['group_name', fields['group_name']]])
            if rc != 0:
                config.db_close()
                return list(request, selector='-', response_code=1, message='%s group add, "%s" failed - %s.' % (lno('GV95'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups)

        if 'vm_network' in fields and fields['vm_network']:
            rc, msg = validate_by_filtered_table_entries(config, fields['vm_network'], 'vm_network', 'cloud_networks', 'name', [['group_name', fields['group_name']]])
            if rc != 0:
                config.db_close()
                return list(request, selector='-', response_code=1, message='%s group add, "%s" failed - %s.' % (lno('GV95'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups)

        # Validity check the specified users.
        if 'username' in fields:
            rc, msg = manage_user_group_verification(config, tables, fields['username'], None) 
            if rc != 0:
                config.db_close()
                return list(request, selector=fields['group_name'], response_code=1, message='%s group add, "%s" failed - %s.' % (lno('GV02'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups)

        # Add the group.
        table = tables['csv2_groups']
        rc, msg = config.db_session_execute(table.insert().values(table_fields(fields, table, columns, 'insert')))
        if rc != 0:
            config.db_close()
            return list(request, selector=fields['group_name'], response_code=1, message='%s group add "%s" failed - %s.' % (lno('GV03'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

        # Add user_groups.
        if 'username' in fields:
            rc, msg = manage_group_users(config, tables, fields['group_name'], fields['username'])

        # Add the group defaults.
        table = tables['csv2_group_defaults']
        rc, msg = config.db_session_execute(table.insert().values(table_fields(fields, table, columns, 'insert')))
        if rc == 0:
            config.db_close(commit=True)
            return list(request, selector=fields['group_name'], response_code=0, message='group "%s" successfully added.' % (fields['group_name']), active_user=active_user, user_groups=user_groups, attributes=columns)
        else:
            config.db_close()
            return list(request, selector=fields['group_name'], response_code=1, message='%s group defaults add "%s" failed - %s.' % (lno('GV04'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

    ### Bad request.
    else:
        return list(request, response_code=1, message='%s group add, invalid method "%s" specified.' % (lno('GV05'), request.method))

#-------------------------------------------------------------------------------

#@silkp(name='Group Defaults')
def defaults(request):
    """
    Update and list group defaults.
    """

    if not verifyUser(request):
        raise PermissionDenied

    # open the database.
    config.db_open()

    message = None
    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user, user_groups = set_user_groups(config, request)
    if rc == 0:
        if request.method == 'POST':
                # Validate input fields.
                rc, msg, fields, tables, columns = validate_fields(config, request, [GROUP_DEFAULTS_KEYS], ['csv2_group_defaults'], active_user)
                
                if rc == 0 and ('vm_flavor' in fields) and (fields['vm_flavor']):
                    rc, msg = validate_by_filtered_table_entries(config, fields['vm_flavor'], 'vm_flavor', 'cloud_flavors', 'name', [['group_name', fields['group_name']]])
                
                if rc == 0 and ('vm_image' in fields) and (fields['vm_image']):
                    rc, msg = validate_by_filtered_table_entries(config, fields['vm_image'], 'vm_image', 'cloud_images', 'name', [['group_name', fields['group_name']]])
                
                if rc == 0 and ('vm_keyname' in fields) and (fields['vm_keyname']):
                    rc, msg = validate_by_filtered_table_entries(config, fields['vm_keyname'], 'vm_keyname', 'cloud_keypairs', 'name', [['group_name', fields['group_name']]])
                
                if rc == 0 and ('vm_network' in fields) and (fields['vm_network']):
                    rc, msg = validate_by_filtered_table_entries(config, fields['vm_network'], 'vm_network', 'cloud_networks', 'name', [['group_name', fields['group_name']]])
                
                if rc == 0:
                    # Update the group defaults.
                    table = tables['csv2_group_defaults']
                    rc, msg = config.db_session_execute(table.update().where(table.c.group_name==active_user.active_group).values(table_fields(fields, table, columns, 'update')))
                    if rc == 0:
                        config.db_session.commit()
                        #set_defaults_changed(True)
                        message='group defaults "%s" successfully updated.' % (active_user.active_group)
                    else:
                        message='%s group defaults update "%s" failed - %s.' % (lno('GV06'), active_user.active_group, msg)
                else:
                    message='%s group defaults update %s' % (lno('GV07'), msg)
    else:
        message='%s %s' % (lno('GV08'), msg)

    if message and message[:2] == 'GV':
        defaults_list = []
        response_code = 1
    else:
        s = select([csv2_group_defaults]).where(csv2_group_defaults.c.group_name==active_user.active_group)
        defaults_list = qt(config.db_connection.execute(s))
        response_code = 0

    # Retrieve group information.
    if request.META['HTTP_ACCEPT'] == 'application/json':
        image_list = {}
        flavor_list = {}
        metadata_dict = {}
        keyname_list = {}
        network_list = {}
    else:
        # Get all the images in group:
        s = select([cloud_images]).where(cloud_images.c.group_name==active_user.active_group)
        image_list = qt(config.db_connection.execute(s))

        # Get all the flavors in group:
        s = select([cloud_flavors]).where(cloud_flavors.c.group_name==active_user.active_group)
        flavor_list = qt(config.db_connection.execute(s))

        # Get all keynames in group:
        s = select([cloud_keypairs]).where(cloud_keypairs.c.group_name==active_user.active_group)
        keypairs_list = qt(config.db_connection.execute(s))

        # Get all networks in group:
        s = select([cloud_networks]).where(cloud_networks.c.group_name==active_user.active_group)
        network_list = qt(config.db_connection.execute(s))

        # Get the group default metadata list:
        s = select([view_groups_with_metadata_info]).where(csv2_group_defaults.c.group_name==active_user.active_group)
        group_list, metadata_dict = qt(
            config.db_connection.execute(s),
            keys = {
                'primary': [
                    'group_name',
                    ],
                'secondary': [
                    'metadata_name',
                    'metadata_enabled',
                    'metadata_priority',
                    'metadata_mime_type'
                    ]
                },
            prune=['password']    
            )

    config.db_close()

    # Render the page.
    context = {
            'active_user': active_user,
            'active_group': active_user.active_group,
            'user_groups': user_groups,
            'defaults_list': defaults_list,
            'image_list': image_list,
            'flavor_list': flavor_list,
            'metadata_dict': metadata_dict,
            'keypairs_list': keypairs_list,
            'network_list': network_list,
            'response_code': response_code,
            'message': message,
            'enable_glint': config.enable_glint
        }

    return render(request, 'csv2/group_defaults.html', context)



#-------------------------------------------------------------------------------

#@silkp(name='Group Delete')
def delete(request):
    """
    This function should recieve a post request with a payload of group name
    to be deleted.
    """

    if not verifyUser(request):
        raise PermissionDenied

    if not getSuperUserStatus(request):
        raise PermissionDenied

    if request.method == 'POST':
        # open the database.
        config.db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(config, request)
        if rc != 0:
            config.db_close()
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('GV09'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(config, request, [GROUP_DEFAULTS_KEYS, GROUP_KEYS, IGNORE_METADATA_NAME, IGNORE_KEYS], [
                'csv2_groups',
                'csv2_group_metadata',
                'csv2_group_defaults',
                'csv2_group_resources',
                'csv2_group_resource_metadata',
                'csv2_group_metadata_exclusions',
                'csv2_user_groups',
                'csv2_vms',
                'cloud_keypairs',
                'cloud_networks',
                'cloud_limits',
                'cloud_images',
                'cloud_flavors'
            ], active_user)
        if rc != 0:
            config.db_close()
            return list(request, selector='-', response_code=1, message='%s group delete %s' % (lno('GV10'), msg), active_user=active_user, user_groups=user_groups)

        # Delete any group metadata files for the group.
        s = select([view_groups_with_metadata_names]).where((view_groups_with_metadata_names.c.group_name == fields['group_name']))
        group_list = qt(config.db_connection.execute(s))
        for row in group_list:
            if row['group_name'] == fields['group_name'] and row['metadata_names']:
                metadata_names = row['metadata_names'].split(',')
                table = tables['csv2_group_metadata']
                for metadata_name in metadata_names:
                    # Delete the group metadata files.
                    rc, msg = config.db_session_execute(
                        table.delete((table.c.group_name==fields['group_name']) & (table.c.metadata_name==metadata_name))
                        )
                    if rc != 0:
                        config.db_close()
                        return list(request, selector=fields['group_name'], response_code=1, message='%s group metadata file delete "%s::%s" failed - %s.' % (lno('GV11'), fields['group_name'], metadata_name, msg), active_user=active_user, user_groups=user_groups, attributes=columns)

        # Delete the group defaults.
        table = tables['csv2_group_defaults']
        rc, msg = config.db_session_execute(
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            config.db_close()
            return list(request, selector=fields['group_name'], response_code=1, message='%s group defaults delete "%s" failed - %s.' % (lno('GV12'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)


        # Delete the csv2_group_resources.
        table = tables['csv2_group_resources']
        rc, msg = config.db_session_execute(
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            config.db_close()
            return list(request, selector=fields['group_name'], response_code=1, message='%s group resources delete "%s" failed - %s.' % (lno('GV13'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

        # Delete the csv2_group_resource_metadata.
        table = tables['csv2_group_resource_metadata']
        rc, msg = config.db_session_execute(
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            config.db_close()
            return list(request, selector=fields['group_name'], response_code=1, message='%s group resource metadata delete "%s" failed - %s.' % (lno('GV14'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

        # Delete the csv2_group_metadata_exclusions.
        table = tables['csv2_group_metadata_exclusions']
        rc, msg = config.db_session_execute(
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            config.db_close()
            return list(request, selector=fields['group_name'], response_code=1, message='%s delete group metadata exclusions for group "%s" failed - %s.' % (lno('GV14'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

        # Delete the csv2_user_groups.
        table = tables['csv2_user_groups']
        rc, msg = config.db_session_execute(
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            config.db_close()
            return list(request, selector=fields['group_name'], response_code=1, message='%s group users delete "%s" failed - %s.' % (lno('GV15'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

        # Delete the csv2_vms.
        table = tables['csv2_vms']
        rc, msg = config.db_session_execute(
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            config.db_close()
            return list(request, selector=fields['group_name'], response_code=1, message='%s group VMs defaults delete "%s" failed - %s.' % (lno('GV16'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

        # Delete the cloud_keypairs.
        table = tables['cloud_keypairs']
        rc, msg = config.db_session_execute(
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            config.db_close()
            return list(request, selector=fields['group_name'], response_code=1, message='%s group keynames delete "%s" failed - %s.' % (lno('GV17'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

        # Delete the cloud_networks.
        table = tables['cloud_networks']
        rc, msg = config.db_session_execute(
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            config.db_close()
            return list(request, selector=fields['group_name'], response_code=1, message='%s group networks delete "%s" failed - %s.' % (lno('GV17'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

        # Delete the cloud_limits.
        table = tables['cloud_limits']
        rc, msg = config.db_session_execute(
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            config.db_close()
            return list(request, selector=fields['group_name'], response_code=1, message='%s group limits delete "%s" failed - %s.' % (lno('GV18'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

        # Delete the cloud_images.
        table = tables['cloud_images']
        rc, msg = config.db_session_execute(
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            config.db_close()
            return list(request, selector=fields['group_name'], response_code=1, message='%s group images delete "%s" failed - %s.' % (lno('GV19'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

        # Delete the cloud_flavors.
        table = tables['cloud_flavors']
        rc, msg = config.db_session_execute(
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            return list(request, selector=fields['group_name'], response_code=1, message='%s group flavors delete "%s" failed - %s.' % (lno('GV20'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

        # Delete the group.
        table = tables['csv2_groups']
        rc, msg = config.db_session_execute(
            table.delete(table.c.group_name==fields['group_name'])
            )
        if rc == 0:
            config.db_close(commit=True)
            return list(request, selector=fields['group_name'], response_code=0, message='group "%s" successfully deleted.' % (fields['group_name']), active_user=active_user, user_groups=user_groups, attributes=columns)
        else:
            config.db_close()
            return list(request, selector=fields['group_name'], response_code=1, message='%s group delete "%s" failed - %s.' % (lno('GV21'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

    ### Bad request.
    else:
        return list(request, response_code=1, message='%s group delete, invalid method "%s" specified.' % (lno('GV22'), request.method))

#-------------------------------------------------------------------------------

#@silkp(name='Group List')
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

    if not getSuperUserStatus(request):
        raise PermissionDenied

    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    if not active_user:
        rc, msg, active_user, user_groups = set_user_groups(config, request)
        if rc != 0:
            config.db_close()
            return render(request, 'csv2/groups.html', {'response_code': 1, 'message': msg})

    # Validate input fields (should be none).
    if not message:
        rc, msg, fields, tables, columns = validate_fields(config, request, [LIST_KEYS], [], active_user)
        if rc != 0:
            config.db_close()
            return render(request, 'csv2/groups.html', {'response_code': 1, 'message': '%s group list, %s' % (lno('GV23'), msg)})

    # Retrieve group information.
    if request.META['HTTP_ACCEPT'] == 'application/json':
        s = select([view_groups_with_metadata_names]).order_by('group_name')
        group_list = qt(config.db_connection.execute(s))
        metadata_dict = {}
    else:
        s = select([view_groups_with_metadata_info]).order_by('group_name')
        group_list, metadata_dict = qt(
            config.db_connection.execute(s),
            keys = {
                'primary': [
                    'group_name',
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

    # Retrieve user/groups list (dictionary containing list for each user).
    s = select([view_user_groups])
    groups_per_user = qt(
        config.db_connection.execute(s),
            prune=['password']    
            )

    s = select([csv2_group_defaults])
    group_defaults = qt(config.db_connection.execute(s))

    config.db_close()

    # Position the page.
    obj_act_id = request.path.split('/')
    if selector:
        if selector == '-':
            current_group = ''
        else:
            current_group = selector
    elif len(obj_act_id) > 3 and len(obj_act_id[3]) > 0:
        current_group = str(obj_act_id[3])
    else:
        if len(group_list) > 0:
            current_group = str(group_list[0]['group_name'])
        else:
            current_group = ''

    # Render the page.
    context = {
            'active_user': active_user,
            'active_group': active_user.active_group,
            'attributes': attributes,
            'user_groups': user_groups,
            'group_defaults': group_defaults,
            'group_list': group_list,
            'groups_per_user': groups_per_user,
            'metadata_dict': metadata_dict,
            'current_group': current_group,
            'response_code': response_code,
            'message': message,
            'enable_glint': config.enable_glint,
            'is_superuser': getSuperUserStatus(request)
        }

    return render(request, 'csv2/groups.html', context)

#-------------------------------------------------------------------------------

#@silkp(name='Group Metadata Add')
def metadata_add(request):
    """
    This function should recieve a post request with a payload of a metadata file
    to add to a given group.
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
            return render(request, 'csv2/group_defaults.html', {'response_code': 1, 'message': '%s %s' % (lno('GV24'), msg)})

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(config, request, [METADATA_KEYS], ['csv2_group_metadata'], active_user)
        if rc != 0:
            config.db_close()
            return render(request, 'csv2/group_defaults.html', {'response_code': 1, 'message': '%s group metadata-add %s' % (lno('GV25'), msg)})

        # Add the group metadata file.
        table = tables['csv2_group_metadata']
        rc, msg = config.db_session_execute(table.insert().values(table_fields(fields, table, columns, 'insert')))
        if rc == 0:
            config.db_close(commit=True)
            return render(request, 'csv2/group_defaults.html', {'response_code': 0, 'message': 'group metadata file "%s::%s" successfully added.' % (active_user.active_group, fields['metadata_name'])})
        else:
            config.db_close()
            return render(request, 'csv2/group_defaults.html', {'response_code': 1, 'message': '%s group metadata-add "%s::%s" failed - %s.' % (lno('GV26'), active_user.active_group, fields['metadata_name'], msg)})

    ### Bad request.
    else:
        return render(request, 'csv2/group_defaults.html', {'response_code': 1, 'message': '%s group metadata_add, invalid method "%s" specified.' % (lno('GV27'), request.method)})

#-------------------------------------------------------------------------------

#@silkp(name='Group Metadata Delete')
def metadata_delete(request):
    """
    This function should recieve a post request with a payload of a metadata file
    name to be deleted from the given group.
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
            return render(request, 'csv2/group_defaults.html', {'response_code': 1, 'message': '%s %s' % (lno('GV29'), msg)})

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(config, request, [METADATA_KEYS], ['csv2_group_metadata', 'csv2_group_metadata_exclusions,n'], active_user)
        if rc != 0:
            config.db_close()
            return render(request, 'csv2/group_defaults.html', {'response_code': 1, 'message': '%s group metadata-delete %s' % (lno('GV30'), msg)})

        # Delete the csv2_group_metadata_exclusions.
        table = tables['csv2_group_metadata_exclusions']
        rc, msg = config.db_session_execute(
            table.delete((table.c.group_name==fields['group_name']) & (table.c.metadata_name==fields['metadata_name'])),
            allow_no_rows=True
            )
        if rc != 0:
            config.db_close()
            return list(request, selector=fields['group_name'], response_code=1, message='%s delete group metadata exclusion for group=%s, metadata=%s failed - %s.' % (lno('GV14'), fields['group_name'], fields['metadata_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

        # Delete the group metadata file.
        table = tables['csv2_group_metadata']
        rc, msg = config.db_session_execute(
            table.delete( \
                (table.c.group_name==active_user.active_group) & \
                (table.c.metadata_name==fields['metadata_name']) \
                )
            )
        if rc == 0:
            config.db_close(commit=True)
            return render(request, 'csv2/group_defaults.html', {'response_code': 0, 'message': 'group metadata file "%s::%s" successfully deleted.' % (active_user.active_group, fields['metadata_name'])})
        else:
            config.db_close()
            return render(request, 'csv2/group_defaults.html', {'response_code': 1, 'message': '%s group metadata-delete "%s::%s" failed - %s.' % (lno('GV31'), active_user.active_group, fields['metadata_name'], msg)})

    ### Bad request.
    else:
        return render(request, 'csv2/group_defaults.html', {'response_code': 1, 'message': '%s group metadata_delete, invalid method "%s" specified.' % (lno('GV32'), request.method)})

#-------------------------------------------------------------------------------

#@silkp(name='Group Metadata Fetch')
def metadata_fetch(request, selector=None):
    if not verifyUser(request):
        raise PermissionDenied

    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user, user_groups = set_user_groups(config, request)
    if rc != 0:
        config.db_close()
        return render(request, 'csv2/group_defaults.html', {'response_code': 1, 'message': '%s %s' % (lno('GV34'), msg)})

    # Get mime type list:
    s = select([csv2_mime_types])
    mime_types_list = qt(config.db_connection.execute(s))

    # Retrieve metadata file.
    id = request.path.split('/')
    if len(id) > 3:
        METADATA = config.db_map.classes.csv2_group_metadata
        METADATAobj = config.db_session.query(METADATA).filter((METADATA.group_name == active_user.active_group) & (METADATA.metadata_name == id[3]))
        if METADATAobj:
            for row in METADATAobj:
                context = {
                    'group_name': row.group_name,
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
        return render(request, 'csv2/group_defaults.html', {'response_code': 1, 'message': 'group metadata_fetch, file "%s::%s" does not exist.' % (active_user.active_group, id[3])})

    config.db_close()
    return render(request, 'csv2/group_defaults.html', {'response_code': 1, 'message': 'group metadata_fetch, metadata file name omitted.'})

#-------------------------------------------------------------------------------

#@silkp(name='Group Metadata List')
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
        return render(request, 'csv2/clouds.html', {'response_code': 1, 'message': msg})

    # Validate input fields (should be none).
    rc, msg, fields, tables, columns = validate_fields(config, request, [LIST_KEYS], [], active_user)
    if rc != 0:
        config.db_close()
        return render(request, 'csv2/group_defaults.html', {'response_code': 1, 'message': '%s group metadata-list, %s' % (lno('GV35'), msg)})

    # Retrieve cloud/metadata information.
    s = select([csv2_group_metadata]).where(csv2_group_metadata.c.group_name == active_user.active_group)
    group_metadata_list = qt(config.db_connection.execute(s))
    config.db_close()

    # Render the page.
    context = {
            'active_user': active_user,
            'active_group': active_user.active_group,
            'user_groups': user_groups,
            'group_metadata_list': group_metadata_list,
            'response_code': 0,
            'message': None,
            'enable_glint': config.enable_glint
        }

    return render(request, 'csv2/group_metadata_list.html', context)

#-------------------------------------------------------------------------------
#@silkp(name="Group Metadata New")
@requires_csrf_token
def metadata_new(request):
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


    context = {
        'group_name': active_user.active_group,
        'metadata': "",
        'metadata_enabled': 0,
        'metadata_priority': 0,
        'metadata_mime_type': "",
        'metadata_name': "",
        'mime_types_list': mime_types_list,
        'response_code': 0,
        'message': "new-group-metadata",
        'enable_glint': config.enable_glint
        }

    config.db_close()
    return render(request, 'csv2/meta_editor.html', context)


#-------------------------------------------------------------------------------

#@silkp(name='Group Metadata Update')
def metadata_update(request):
    """
    This function should recieve a post request with a payload of a metadata file
    as a replacement for the specified file.
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
            return render(request, 'csv2/group_defaults.html', {'response_code': 1, 'message': '%s %s' % (lno('GV36'), msg)})

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(config, request, [METADATA_KEYS], ['csv2_group_metadata'], active_user)
        if rc != 0:
            config.db_close()
            return render(request, 'csv2/group_defaults.html', {'response_code': 1, 'message': '%s group metadata-update %s' % (lno('GV37'), msg)})

        # Update the group metadata file.
        table = tables['csv2_group_metadata']
        rc, msg = config.db_session_execute(table.update().where( \
            (table.c.group_name==active_user.active_group) & \
            (table.c.metadata_name==fields['metadata_name']) \
            ).values(table_fields(fields, table, columns, 'update')))
        if rc == 0:
            config.db_close(commit=True)
            #return render(request, 'csv2/group_defaults.html', {'response_code': 0, 'message': 'group metadata file "%s::%s" successfully  updated.' % (active_user.active_group, fields['metadata_name'])})
        
            message='group metadata file "%s::%s" successfully  updated.' % (fields['group_name'], fields['metadata_name'])
            context = {
                    'group_name': fields['group_name'],
                    'response_code': 0,
                    'message': message,
                }

            return render(request, 'csv2/meta_editor.html',context)

        else:
            config.db_close()
            return render(request, 'csv2/group_defaults.html', {'response_code': 1, 'message': '%s group metadata-update "%s::%s" failed - %s.' % (lno('GV38'), active_user.active_group, fields['metadata_name'], msg)})

    ### Bad request.
    else:
        return render(request, 'csv2/group_defaults.html', {'response_code': 1, 'message': '%s group metadata_update, invalid method "%s" specified.' % (lno('GV39'), request.method)})

#-------------------------------------------------------------------------------

#@silkp(name='Group Update')
def update(request):
    """
    This function should recieve a post request with a payload of group configuration
    to update a given group.
    """

    if not verifyUser(request):
        raise PermissionDenied

    if not getSuperUserStatus(request):
        raise PermissionDenied

    if request.method == 'POST':
        # open the database.
        config.db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(config, request)
        if rc != 0:
            config.db_close()
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('GV41'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(config, request, [GROUP_KEYS], ['csv2_groups','csv2_user_groups', 'csv2_user,n'], active_user)
        if rc != 0:
            config.db_close()
            return list(request, selector='-', response_code=1, message='%s group update %s' % (lno('GV42'), msg), active_user=active_user, user_groups=user_groups)

        # Validity check the specified users.
        if 'username' in fields:
            rc, msg = manage_user_group_verification(config, tables, fields['username'], None) 
            if rc != 0:
                return list(request, selector=fields['group_name'], response_code=1, message='%s group add, "%s" failed - %s.' % (lno('GV43'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups)

        # Update the group.
        table = tables['csv2_groups']
        group_updates = table_fields(fields, table, columns, 'update')
        if len(group_updates) > 0:
            rc, msg = config.db_session_execute(table.update().where(table.c.group_name==fields['group_name']).values(group_updates), allow_no_rows=False)
            if rc != 0:
                config.db_close()
                return list(request, selector=fields['group_name'], response_code=1, message='%s group update, "%s" failed - %s.' % (lno('GV44'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups)
        else:
            if 'username' not in fields:
                config.db_close()
                return list(request, selector=fields['group_name'], response_code=1, message='%s group update must specify at least one field to update.' % lno('GV45'), active_user=active_user, user_groups=user_groups)


        # Update user groups.
        if request.META['HTTP_ACCEPT'] == 'application/json':
            if 'username' in fields:
                if 'user_option' in fields and fields['user_option'] == 'delete':
                    rc, msg = manage_group_users(config, tables, fields['group_name'], users=fields['username'], option='delete')
                else:
                    rc, msg = manage_group_users(config, tables, fields['group_name'], users=fields['username'], option='add')

        else:
            if 'username' in fields:
                rc, msg = manage_group_users(config, tables, fields['group_name'], fields['username'])
            else:
                rc, msg = manage_group_users(config, tables, fields['group_name'], None)

        if rc == 0:
            config.db_close(commit=True)
            return list(request, selector=fields['group_name'], response_code=0, message='group "%s" successfully updated.' % (fields['group_name']), active_user=active_user, user_groups=user_groups, attributes=columns)
        else:
            config.db_close()
            return list(request, selector=fields['group_name'], response_code=1, message='%s group update "%s" failed - %s.' % (lno('GV46'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

    ### Bad request.
    else:
        return list(request, response_code=1, message='%s group update, invalid method "%s" specified.' % (lno('GV47'), request.method))

