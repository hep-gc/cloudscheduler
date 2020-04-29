from django.conf import settings
config = settings.CSV2_CONFIG

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import requires_csrf_token
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from cloudscheduler.lib.fw_config import configure_fw 
from cloudscheduler.lib.view_utils import \
    lno,  \
    manage_group_users, \
    manage_user_group_verification, \
    qt, \
    render, \
    set_user_groups, \
    table_fields, \
    validate_by_filtered_table_entries, \
    validate_fields
from collections import defaultdict
import bcrypt

from sqlalchemy import exists
from sqlalchemy.sql import select
from cloudscheduler.lib.schema import *
import sqlalchemy.exc
import re

from cloudscheduler.lib.web_profiler import silk_profile as silkp

# lno: GV - error code identifier.
MODID= 'GV'

#-------------------------------------------------------------------------------

GROUP_KEYS = {
    'auto_active_group': False,
    # Named argument formats (anything else is a string).
    'format': {
        'group_name':                                 'lower',
        'csrfmiddlewaretoken':                        'ignore',
        'group':                                      'ignore',
        'htcondor_fqdn':                              'fqdn,htcondor_host_id',
        'job_cpus':                                   'integer',
        'job_disk':                                   'integer',
        'job_ram':                                    'integer',
        'job_swap':                                   'integer',
        'username':                                   'ignore',
        'user_option':                                ['add', 'delete'],
        'vm_keep_alive':                              'integer',

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
    'array_fields': [
        'username',
        ],
    }

GROUP_ADD_KEYS = {
    'not_empty': [
        'htcondor_fqdn',
        ],
    }

UNPRIVILEGED_GROUP_KEYS = {
    'auto_active_group': True,
    # Named argument formats (anything else is a string).
    'format': {
        'csrfmiddlewaretoken':                        'ignore',
        'group':                                      'ignore',
        'htcondor_fqdn':                              'fqdn,htcondor_host_id',
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
        'metadata_name':                              'lower',
        'mime_type':                                  ('csv2_mime_types', 'mime_type'),

        'csrfmiddlewaretoken':                        'ignore',
        'group':                                      'ignore',
        },
    'mandatory': [
        'metadata_name',
        ],
    'not_empty': [
        'metadata_name',
        ],
    }

METADATA_ADD_KEYS = {
    'mandatory': [
        'metadata',
        ],
    }

IGNORE_METADATA_NAME = {
    'format': {
        'metadata_name':                              'ignore',
        },
    }

IGNORE_KEYS = {
    'format': {
        'alias_name':                                 'ignore',
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

def validate_url_fields(prefix, request, template, actual_fields, expected_fields):
    """Ensure values required in a URL are given, that they are not empty, and that they match the lower format."""
    
    for field in expected_fields:
        if field in actual_fields:
            if actual_fields[field] == '':
                return render(request, template, {'response_code': 1, 'message': '%s, value specified for "%s" must not be the empty string.' % (prefix, field)})
            elif not re.fullmatch('([a-z0-9_.:]-?)*[a-z0-9_.:]', actual_fields[field]):
                return render(request, template, {'response_code': 1, 'message': '%s, value specified for "%s" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.' % (prefix, field)})
        else:
            return render(request, template, {'response_code': 1, 'message': '%s, request did not contain mandatory parameter "%s".' % (prefix, field)})

#-------------------------------------------------------------------------------

@silkp(name='Group Add')
def add(request):
    """
    This function should receive a post request with a payload of group configuration
    to add the specified group.
    """

    # open the database.
    config.db_open()
    config.refresh()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request)
    if rc != 0:
        config.db_close()
        return group_list(request, active_user=active_user, response_code=1, message='%s %s' % (lno(MODID), msg))

    if request.method == 'POST':
        
        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(config, request, [GROUP_KEYS, GROUP_ADD_KEYS], ['csv2_groups', 'csv2_user_groups', 'csv2_user,n', 'csv2_group_metadata,n'], active_user)
        if rc != 0:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group add %s' % (lno(MODID), msg))

        if 'vm_flavor' in fields and fields['vm_flavor']:
            rc, msg = validate_by_filtered_table_entries(config, fields['vm_flavor'], 'vm_flavor', 'cloud_flavors', 'name', [['group_name', fields['group_name']]])
            if rc != 0:
                config.db_close()
                return group_list(request, active_user=active_user, response_code=1, message='%s group add, "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))
        if 'vm_image' in fields and fields['vm_image']:
            rc, msg = validate_by_filtered_table_entries(config, fields['vm_image'], 'vm_image', 'cloud_images', 'name', [['group_name', fields['group_name']]])
            if rc != 0:
                config.db_close()
                return group_list(request, active_user=active_user, response_code=1, message='%s group add, "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        if 'vm_keyname' in fields and fields['vm_keyname']:
            rc, msg = validate_by_filtered_table_entries(config, fields['vm_keyname'], 'vm_keyname', 'cloud_keypairs', 'key_name', [['group_name', fields['group_name']]])
            if rc != 0:
                config.db_close()
                return group_list(request, active_user=active_user, response_code=1, message='%s group add, "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        if 'vm_network' in fields and fields['vm_network']:
            rc, msg = validate_by_filtered_table_entries(config, fields['vm_network'], 'vm_network', 'cloud_networks', 'name', [['group_name', fields['group_name']]])
            if rc != 0:
                config.db_close()
                return group_list(request, active_user=active_user, response_code=1, message='%s group add, "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        if 'vm_security_groups' in fields and fields['vm_security_groups']:
            rc, msg = validate_by_filtered_table_entries(config, fields['vm_security_groups'], 'vm_security_groups', 'cloud_security_groups', 'name', [['group_name', fields['group_name']]], allow_value_list=True)
            if rc != 0:
                config.db_close()
                return group_list(request, active_user=active_user, response_code=1, message='%s group add, "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        # Validity check the specified users.
        if 'username' in fields:
            rc, msg = manage_user_group_verification(config, tables, fields['username'], None) 
            if rc != 0:
                config.db_close()
                return group_list(request, active_user=active_user, response_code=1, message='%s group add, "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        # Add the group.
        table = tables['csv2_groups']
        rc, msg = config.db_session_execute(table.insert().values(table_fields(fields, table, columns, 'insert')))
        if rc != 0:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group add "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        # Add user_groups.
        if 'username' in fields:
            rc, msg = manage_group_users(config, tables, fields['group_name'], fields['username'])
            if rc != 0:
                config.db_close()
                return group_list(request, active_user=active_user, response_code=1, message='%s group add "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))


        # Add the default metadata file.
        filepath = '/opt/cloudscheduler/metadata/'
        filename = 'default.yaml.j2'
        filedata = open(filepath+filename, "r").read()

        table = tables['csv2_group_metadata']
        rc, msg = config.db_session_execute(table.insert().values(group_name=fields['group_name'], metadata_name=filename, enabled=1 ,priority=0, metadata=filedata, mime_type="cloud-config"))
        if rc != 0:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group add "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))


        # Commit the updates, configure firewall and return.
        config.db_session.commit()
        configure_fw(config)
        config.db_close()
        return group_list(request, active_user=active_user, response_code=0, message='group "%s" successfully added.' % (fields['group_name']))

    ### Bad request.
    else:
        return group_list(request, active_user=active_user, response_code=1, message='%s group add, invalid method "%s" specified.' % (lno(MODID), request.method))

#-------------------------------------------------------------------------------

@silkp(name='Group Defaults')
def defaults(request, active_user=None, response_code=0, message=None):
    """
    Update and list group defaults.
    """

    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc == 0:
        user_groups_set = True
        message = None
        if request.method == 'POST':
            # Validate input fields.
            rc, msg, fields, tables, columns = validate_fields(config, request, [UNPRIVILEGED_GROUP_KEYS], ['csv2_groups'], active_user)
            if rc != 0:
                config.db_close()
                return render(request, 'csv2/group_defaults.html', {'response_code': 1, 'message': '%s default update/list %s' % (lno(MODID), msg), 'active_user': active_user.username, 'active_group': active_user.active_group, 'user_groups': active_user.user_groups})

            if rc == 0 and ('vm_flavor' in fields) and (fields['vm_flavor']):
                rc, msg = validate_by_filtered_table_entries(config, fields['vm_flavor'], 'vm_flavor', 'cloud_flavors', 'name', [['group_name', fields['group_name']]])
            
            if rc == 0 and ('vm_image' in fields) and (fields['vm_image']):
                rc, msg = validate_by_filtered_table_entries(config, fields['vm_image'], 'vm_image', 'cloud_images', 'name', [['group_name', fields['group_name']]])
            
            if rc == 0 and ('vm_keyname' in fields) and (fields['vm_keyname']):
                rc, msg = validate_by_filtered_table_entries(config, fields['vm_keyname'], 'vm_keyname', 'cloud_keypairs', 'key_name', [['group_name', fields['group_name']]])
            
            if rc == 0 and ('vm_network' in fields) and (fields['vm_network']):
                rc, msg = validate_by_filtered_table_entries(config, fields['vm_network'], 'vm_network', 'cloud_networks', 'name', [['group_name', fields['group_name']]])
            
            if rc == 0 and ('vm_security_groups' in fields) and (fields['vm_security_groups']):
                rc, msg = validate_by_filtered_table_entries(config, fields['vm_security_groups'], 'vm_security_groups', 'cloud_security_groups', 'name', [['group_name', fields['group_name']]], allow_value_list=True)
            
            if rc == 0:
                # Update the group defaults.
                table = tables['csv2_groups']
                rc, msg = config.db_session_execute(table.update().where(table.c.group_name==active_user.active_group).values(table_fields(fields, table, columns, 'update')))
                if rc == 0:
                    # Commit the updates, configure firewall and return.
                    config.db_session.commit()
                    configure_fw(config)
                    message = 'group defaults "%s" successfully updated.' % (active_user.active_group)
                else:
                    message = '%s group defaults update "%s" failed - %s.' % (lno(MODID), active_user.active_group, msg)
            else:
                message = '%s group defaults update %s.' % (lno(MODID), msg)
    else:
        user_groups_set = False
        message = '%s %s' % (lno(MODID), msg)

    # Prepare default CLI/Error response.
    defaults_list = []
    image_list = []
    flavor_list = []
    metadata_dict = {}
    keypairs_list = []
    network_list = []
    security_groups_list = []

    # If User/Groups successfully set, retrieve group information.
    if user_groups_set:
        s = select([csv2_groups]).where(csv2_groups.c.group_name==active_user.active_group)
        defaults_list = qt(config.db_connection.execute(s))

        # Replace None values with "".
        for defaults in defaults_list:
            for key, value in defaults.items():
                if value == None:
                    defaults_list[0][key]=""

#       # And additional information for the web page.
#       if request.META['HTTP_ACCEPT'] != 'application/json':
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

        # Get all security_groups in group:
        s = select([cloud_security_groups]).where(cloud_security_groups.c.group_name==active_user.active_group)
        security_groups_list = qt(config.db_connection.execute(s))

        # Get the group default metadata list:
        s = select([view_groups_with_metadata_info]).where(csv2_groups.c.group_name==active_user.active_group)
        _group_list, metadata_dict = qt(
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

    # Render the page.
    context = {
            'active_user': active_user.username,
            'active_group': active_user.active_group,
            'user_groups': active_user.user_groups,
            'defaults_list': defaults_list,
            'image_list': image_list,
            'flavor_list': flavor_list,
            'metadata_dict': metadata_dict,
            'keypairs_list': keypairs_list,
            'network_list': network_list,
            'security_groups_list': security_groups_list,
            'response_code': rc,
            'message': message,
            'is_superuser': active_user.is_superuser,
            'version': config.get_version()
        }

    config.db_close()
    return render(request, 'csv2/group_defaults.html', context)



#-------------------------------------------------------------------------------

@silkp(name='Group Delete')
def delete(request):
    """
    This function should recieve a post request with a payload of group name
    to be deleted.
    """

    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request)
    if rc != 0:
        config.db_close()
        return group_list(request, active_user=active_user, response_code=1, message='%s %s' % (lno(MODID), msg))

    if request.method == 'POST':

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(config, request, [GROUP_KEYS, IGNORE_METADATA_NAME, IGNORE_KEYS], [
                'csv2_groups',
                'csv2_group_metadata',
                'csv2_clouds',
                'csv2_cloud_aliases',
                'csv2_cloud_metadata',
                'csv2_group_metadata_exclusions',
                'csv2_user_groups',
                'csv2_vms',
                'cloud_keypairs',
                'cloud_networks',
                'cloud_security_groups',
                'cloud_limits',
                'cloud_images',
                'cloud_flavors'
            ], active_user)
        if rc != 0:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group delete %s' % (lno(MODID), msg))

        # Delete the csv2_cloud_aliases.
        table = tables['csv2_cloud_aliases']
        rc, msg = config.db_session_execute(
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group resources delete "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        # Delete any group metadata files for the group.
        s = select([view_groups_with_metadata_names]).where((view_groups_with_metadata_names.c.group_name == fields['group_name']))
        _group_list = qt(config.db_connection.execute(s))
        for row in _group_list:
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
                        return group_list(request, active_user=active_user, response_code=1, message='%s group metadata file delete "%s::%s" failed - %s.' % (lno(MODID), fields['group_name'], metadata_name, msg))

        # Delete the csv2_clouds.
        table = tables['csv2_clouds']
        rc, msg = config.db_session_execute(
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group resources delete "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        # Delete the csv2_cloud_metadata.
        table = tables['csv2_cloud_metadata']
        rc, msg = config.db_session_execute(
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group resource metadata delete "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        # Delete the csv2_group_metadata_exclusions.
        table = tables['csv2_group_metadata_exclusions']
        rc, msg = config.db_session_execute(
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s delete group metadata exclusions for group "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        # Delete the csv2_user_groups.
        table = tables['csv2_user_groups']
        rc, msg = config.db_session_execute(
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group users delete "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))


        # Delete the csv2 cloud aliases.
        rc = config.db_connection.execute('delete from csv2_cloud_aliases where group_name="%s";' % fields['group_name'])

        # Delete the csv2_vms.
        table = tables['csv2_vms']
        rc, msg = config.db_session_execute(
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group VMs defaults delete "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        # Delete the cloud_keypairs.
        table = tables['cloud_keypairs']
        rc, msg = config.db_session_execute(
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group keynames delete "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        # Delete the cloud_networks.
        table = tables['cloud_networks']
        rc, msg = config.db_session_execute(
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group networks delete "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        # Delete the cloud_security_groups.
        table = tables['cloud_security_groups']
        rc, msg = config.db_session_execute(
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group  security groups delete "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        # Delete the cloud_limits.
        table = tables['cloud_limits']
        rc, msg = config.db_session_execute(
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group limits delete "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        # Delete the cloud_images.
        table = tables['cloud_images']
        rc, msg = config.db_session_execute(
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group images delete "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        # Delete the cloud_flavors.
        table = tables['cloud_flavors']
        rc, msg = config.db_session_execute(
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            return group_list(request, active_user=active_user, response_code=1, message='%s group flavors delete "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        # Delete the group.
        table = tables['csv2_groups']
        rc, msg = config.db_session_execute(
            table.delete(table.c.group_name==fields['group_name'])
            )
        if rc == 0:
            # Commit the deletions, configure firewall and return.
            config.db_session.commit()
            configure_fw(config)
            config.db_close()
            return group_list(request, active_user=active_user, response_code=0, message='group "%s" successfully deleted.' % (fields['group_name']))
        else:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group delete "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

    ### Bad request.
    else:
      # return group_list(request, active_user=active_user, response_code=1, message='%s group delete request did not contain mandatory parameter "group_name".' % lno(MODID))
        return group_list(request, active_user=active_user, response_code=1, message='%s group delete, invalid method "%s" specified.' % (lno(MODID), request.method))

#-------------------------------------------------------------------------------

@silkp(name='Group List')
def group_list(request, active_user=None, response_code=0, message=None):

    group_list_path = '/group/list/'

    if request.path!=group_list_path and request.META['HTTP_ACCEPT'] == 'application/json':
        return render(request, 'csv2/clouds.html', {'response_code': response_code, 'message': message, 'active_user': active_user.username, 'active_group': active_user.active_group, 'user_groups': active_user.user_groups})

    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    if active_user is None:
        rc, msg, active_user = set_user_groups(config, request)
        if rc != 0:
            config.db_close()
            return render(request, 'csv2/groups.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})

    # Validate input fields (should be none).
    rc, msg, fields, tables, columns = validate_fields(config, request, [LIST_KEYS], [], active_user)
    if rc != 0 and request.path==group_list_path:
        config.db_close()
        return render(request, 'csv2/groups.html', {'response_code': 1, 'message': '%s group list, %s' % (lno(MODID), msg)})

    # Retrieve group information.
    if request.META['HTTP_ACCEPT'] == 'application/json':
        s = select([view_groups_with_metadata_names]).order_by('group_name')
        _group_list = qt(config.db_connection.execute(s))
        metadata_dict = {}
    else:
        s = select([view_groups_with_metadata_info]).order_by('group_name')
        _group_list, metadata_dict = qt(
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

    s = select([csv2_groups])
    group_defaults = qt(config.db_connection.execute(s))
    

    # Position the page.
#   obj_act_id = request.path.split('/')
#   if selector:
#       if selector == '-':
#           current_group = ''
#       else:
#           current_group = selector
#   elif len(obj_act_id) > 3 and len(obj_act_id[3]) > 0:
#       current_group = str(obj_act_id[3])
#   else:
    if len(_group_list) > 0:
        current_group = str(_group_list[0]['group_name'])
    else:
        current_group = ''

    # Render the page.
    context = {
            'active_user': active_user.username,
            'active_group': active_user.active_group,
            'user_groups': active_user.user_groups,
            'group_defaults': group_defaults,
            'group_list': _group_list,
            'groups_per_user': groups_per_user,
            'metadata_dict': metadata_dict,
            'current_group': current_group,
            'response_code': response_code,
            'message': message,
            'is_superuser': active_user.is_superuser,
            'version': config.get_version()
        }
    config.db_close()

    return render(request, 'csv2/groups.html', context)

#-------------------------------------------------------------------------------

@silkp(name='Group Metadata Add')
def metadata_add(request):
    """
    This function should recieve a post request with a payload of a metadata file
    to add to a given group.
    """

    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        return render(request, 'csv2/blank_msg.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})

    if request.method == 'POST':
        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(config, request, [METADATA_KEYS, METADATA_ADD_KEYS], ['csv2_group_metadata'], active_user)
        if rc != 0:
            config.db_close()
            return render(request, 'csv2/blank_msg.html', {'response_code': 1, 'message': '%s group metadata-add %s' % (lno(MODID), msg)})


        # Add the group metadata file.
        table = tables['csv2_group_metadata']
        rc, msg = config.db_session_execute(table.insert().values(table_fields(fields, table, columns, 'insert')))
        if rc == 0:
            config.db_close(commit=True)
            return render(request, 'csv2/reload_parent.html', {'group_name': fields['group_name'], 'response_code': 0, 'message': 'group metadata file "%s::%s" successfully added.' % (active_user.active_group, fields['metadata_name'])})

        else:
            config.db_close()
            return render(request, 'csv2/blank_msg.html', {'response_code': 1, 'message': '%s group metadata-add "%s::%s" failed - %s.' % (lno(MODID), active_user.active_group, fields['metadata_name'], msg)})


    ### Bad request.
    else:
        return render(request, 'csv2/blank_msg.html', {'response_code': 1, 'message': '%s group metadata_add, invalid method "%s" specified.' % (lno(MODID), request.method)})


#-------------------------------------------------------------------------------

@silkp(name='Group Metadata Delete')
def metadata_delete(request):
    """
    This function should recieve a post request with a payload of a metadata file
    name to be deleted from the given group.
    """

    context = {}
    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        return render(request, 'csv2/blank_msg.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})

    if request.method == 'POST':
        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(config, request, [METADATA_KEYS], ['csv2_group_metadata', 'csv2_group_metadata_exclusions,n'], active_user)
        if rc != 0:
            config.db_close()
            return render(request, 'csv2/blank_msg.html', {'response_code': 1, 'message': '%s group metadata-delete %s' % (lno(MODID), msg)})

        # Delete the csv2_group_metadata_exclusions.
        table = tables['csv2_group_metadata_exclusions']
        rc, msg = config.db_session_execute(
            table.delete((table.c.group_name==fields['group_name']) & (table.c.metadata_name==fields['metadata_name'])),
            allow_no_rows=True
            )
        if rc != 0:
            config.db_close()
            return render(request, 'csv2/blank_msg.html', {'response_code': 1, 'message': '%s delete group metadata exclusion for group=%s, metadata=%s failed - %s.' % (lno(MODID), fields['group_name'], fields['metadata_name'], msg)})



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
            return render(request, 'csv2/reload_parent.html', {'group_name': fields['group_name'], 'response_code': 0, 'message': 'group metadata file "%s::%s" successfully deleted.' % (active_user.active_group, fields['metadata_name'])})

        else:
            config.db_close()
            return render(request, 'csv2/blank_msg.html', {'response_code': 1, 'message': '%s group metadata-delete "%s::%s" failed - %s.' % (lno(MODID), active_user.active_group, fields['metadata_name'], msg)})


    ### Bad request.
    else:
      # return render(request, 'csv2/blank_msg.html', {'response_code': 1, 'message': '%s group metadata-delete request did not contain mandatory parameter "metadata_name".' % lno(MODID)})
        return render(request, 'csv2/blank_msg.html', {'response_code': 1, 'message': '%s group metadata-delete, invalid method "%s" specified.' % (lno(MODID), request.method)})

#-------------------------------------------------------------------------------

@silkp(name='Group Metadata Fetch')
def metadata_fetch(request, response_code=0, message=None, metadata_name=None):
    
    context = {}

    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        return render(request, 'csv2/blank_msg.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})

    # Get mime type list:
    s = select([csv2_mime_types])
    mime_types_list = qt(config.db_connection.execute(s))

    # If we are NOT returning from an update, we are fetching from webpage
    if metadata_name == None:
        field_error = validate_url_fields('%s group metadata_fetch' % lno(MODID), request, 'csv2/blank_msg.html', active_user.kwargs, ['metadata_name'])
        if field_error:
            return field_error
        metadata_name = active_user.kwargs['metadata_name']

    # Retrieve metadata file.
    if metadata_name:
        METADATA = config.db_map.classes.csv2_group_metadata
        METADATAobj = config.db_session.query(METADATA).filter((METADATA.group_name == active_user.active_group) & (METADATA.metadata_name == metadata_name))
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
                    'response_code': response_code,
                    'message': message,
                    'is_superuser': active_user.is_superuser,
                    'version': config.get_version()
                    }

                config.db_close()
                return render(request, 'csv2/meta_editor.html', context)
        
        config.db_close()
        return render(request, 'csv2/blank_msg.html', {'response_code': 1, 'message': 'group metadata_fetch, file "%s::%s" does not exist.' % (active_user.active_group, active_user.kwargs['metadata_name'])})

    config.db_close()
    return render(request, 'csv2/blank_msg.html', {'response_code': 1, 'message': 'group metadata_fetch, metadata file name omitted.'})

#-------------------------------------------------------------------------------

@silkp(name='Group Metadata List')
@requires_csrf_token
def metadata_list(request):

    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        return defaults(request, active_user=active_user, response_code=1, message='%s %s' % (lno(MODID), msg))

    # Validate input fields (should be none).
    rc, msg, fields, tables, columns = validate_fields(config, request, [LIST_KEYS], [], active_user)
    if rc != 0:
        config.db_close()
        return render(request, 'csv2/blank_msg.html', {'response_code': 1, 'message': '%s group metadata-list, %s' % (lno(MODID), msg)})

    # Retrieve cloud/metadata information.
    s = select([csv2_group_metadata]).where(csv2_group_metadata.c.group_name == active_user.active_group)
    group_metadata_list = qt(config.db_connection.execute(s))

    # Render the page.
    context = {
            'active_user': active_user.username,
            'active_group': active_user.active_group,
            'user_groups': active_user.user_groups,
            'group_metadata_list': group_metadata_list,
            'response_code': 0,
            'message': None,
            'is_superuser': active_user.is_superuser,
            'version': config.get_version()
        }

    config.db_close()
    return render(request, 'csv2/blank_msg.html', context)

#-------------------------------------------------------------------------------
@silkp(name="Group Metadata New")
@requires_csrf_token
def metadata_new(request):

    context = {}

    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        return render(request, 'csv2/blank_msg.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})

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
        'is_superuser': active_user.is_superuser,
        'version': config.get_version()
        }

    config.db_close()
    return render(request, 'csv2/meta_editor.html', context)


#-------------------------------------------------------------------------------

@silkp(name='Group Metadata Query')
@requires_csrf_token
def metadata_query(request):

    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        return defaults(request, active_user=active_user, response_code=1, message='%s group metadata_query %s' % (lno(MODID), msg))

    fields = active_user.kwargs
    field_error = validate_url_fields('%s group metadata_query' % lno(MODID), request, 'csv2/blank_msg.html', fields, ['metadata_name'])
    if field_error:
        return field_error

    # Retrieve cloud/metadata information.
    s = select([csv2_group_metadata]).where((csv2_group_metadata.c.group_name == active_user.active_group) & (csv2_group_metadata.c.metadata_name == fields['metadata_name']))
    group_metadata_list = qt(config.db_connection.execute(s))

    config.db_close()

    metadata_exists = bool(group_metadata_list)

    # Render the page.
    context = {
            'active_user': active_user.username,
            'active_group': active_user.active_group,
            'user_groups': active_user.user_groups,
            'metadata_exists': metadata_exists,
            'response_code': 0,
            'message': None,
            'is_superuser': active_user.is_superuser,
            'version': config.get_version()
        }

    return render(request, 'csv2/blank_msg.html', context)

#-------------------------------------------------------------------------------

@silkp(name='Group Metadata Update')
def metadata_update(request):
    """
    This function should recieve a post request with a payload of a metadata file
    as a replacement for the specified file.
    """
    context = {}

    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        return defaults(request, active_user=active_user, response_code=1, message='%s %s' % (lno(MODID), msg))

    if request.method == 'POST':
        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(config, request, [METADATA_KEYS], ['csv2_group_metadata'], active_user)
        if rc != 0:
            config.db_close()
            return render(request, 'csv2/blank_msg.html', {'response_code': 1, 'message': '%s group metadata-update %s' % (lno(MODID), msg)})

        # Update the group metadata file.
        table = tables['csv2_group_metadata']
        updates = table_fields(fields, table, columns, 'update')
        if len(updates) < 1:
            config.db_close()
            return render(request, 'csv2/blank_msg.html', {'response_code': 1, 'message': '%s group metadata-update "%s::%s" specified no fields to update and was ignored.' % (lno(MODID), active_user.active_group, fields['metadata_name'])})

        rc, msg = config.db_session_execute(table.update().where( \
            (table.c.group_name==active_user.active_group) & \
            (table.c.metadata_name==fields['metadata_name']) \
            ).values(updates))
        if rc == 0:
            config.db_close(commit=True)
        
            message='group metadata file "%s::%s" successfully  updated.' % (fields['group_name'], fields['metadata_name'])

            return metadata_fetch(request, response_code=0, message=message, metadata_name=fields['metadata_name'])

        else:
            config.db_close()
            return render(request, 'csv2/blank_msg.html', {'response_code': 1, 'message': '%s group metadata-update "%s::%s" failed - %s.' % (lno(MODID), active_user.active_group, fields['metadata_name'], msg)})

    ### Bad request.
    else:
        return render(request, 'csv2/blank_msg.html', {'response_code': 1, 'message': '%s group metadata_update, invalid method "%s" specified.' % (lno(MODID), request.method)})

#-------------------------------------------------------------------------------

@silkp(name='Group Update')
def update(request):
    """
    This function should recieve a post request with a payload of group configuration
    to update a given group.
    """

    # open the database.
    config.db_open()
    config.refresh()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request)
    if rc != 0:
        config.db_close()
        return group_list(request, active_user=active_user, response_code=1, message='%s %s' % (lno(MODID), msg))

    if request.method == 'POST':

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(config, request, [GROUP_KEYS], ['csv2_groups','csv2_user_groups', 'csv2_user,n'], active_user)
        if rc != 0:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group update %s' % (lno(MODID), msg))

        if 'vm_flavor' in fields and fields['vm_flavor']:
            rc, msg = validate_by_filtered_table_entries(config, fields['vm_flavor'], 'vm_flavor', 'cloud_flavors', 'name', [['group_name', fields['group_name']]])
            if rc != 0:
                config.db_close()
                return group_list(request, active_user=active_user, response_code=1, message='%s group update, "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        if 'vm_image' in fields and fields['vm_image']:
            rc, msg = validate_by_filtered_table_entries(config, fields['vm_image'], 'vm_image', 'cloud_images', 'name', [['group_name', fields['group_name']]])
            if rc != 0:
                config.db_close()
                return group_list(request, active_user=active_user, response_code=1, message='%s group update, "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        if 'vm_keyname' in fields and fields['vm_keyname']:
            rc, msg = validate_by_filtered_table_entries(config, fields['vm_keyname'], 'vm_keyname', 'cloud_keypairs', 'key_name', [['group_name', fields['group_name']]])
            if rc != 0:
                config.db_close()
                return group_list(request, active_user=active_user, response_code=1, message='%s group update, "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        if 'vm_network' in fields and fields['vm_network']:
            rc, msg = validate_by_filtered_table_entries(config, fields['vm_network'], 'vm_network', 'cloud_networks', 'name', [['group_name', fields['group_name']]])
            if rc != 0:
                config.db_close()
                return group_list(request, active_user=active_user, response_code=1, message='%s group update, "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        if 'vm_security_groups' in fields and fields['vm_security_groups']:
            rc, msg = validate_by_filtered_table_entries(config, fields['vm_security_groups'], 'vm_security_groups', 'cloud_security_groups', 'name', [['group_name', fields['group_name']]], allow_value_list=True)
            if rc != 0:
                config.db_close()
                return group_list(request, active_user=active_user, response_code=1, message='%s group update, "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        # Validity check the specified users.
        if 'username' in fields:
            rc, msg = manage_user_group_verification(config, tables, fields['username'], None) 
            if rc != 0:
                return group_list(request, active_user=active_user, response_code=1, message='%s group update, "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        # Update the group.
        table = tables['csv2_groups']
        group_updates = table_fields(fields, table, columns, 'update')
        print("???????????????????????????????????", group_updates)
        if len(group_updates) > 0:
            rc, msg = config.db_session_execute(table.update().where(table.c.group_name==fields['group_name']).values(group_updates), allow_no_rows=False)
            if rc != 0:
                config.db_close()
                return group_list(request, active_user=active_user, response_code=1, message='%s group update, "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))
        else:
            if 'username' not in fields and request.META['HTTP_ACCEPT'] == 'application/json':
                config.db_close()
                return group_list(request, active_user=active_user, response_code=1, message='%s group update must specify at least one field to update.' % lno(MODID))


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
            # Commit the updates, configure firewall and return.
            config.db_session.commit()
            configure_fw(config)
            config.db_close()
            return group_list(request, active_user=active_user, response_code=0, message='group "%s" successfully updated.' % (fields['group_name']))
        else:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group update "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

    ### Bad request.
    else:
        return group_list(request, active_user=active_user, response_code=1, message='%s group update, invalid method "%s" specified.' % (lno(MODID), request.method))

