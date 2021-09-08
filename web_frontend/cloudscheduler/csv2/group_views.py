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

from cloudscheduler.lib.schema import *
import re

from cloudscheduler.lib.web_profiler import silk_profile as silkp

# lno: GV - error code identifier.
MODID= 'GV'

#-------------------------------------------------------------------------------

GROUP_KEYS = {
    'auto_active_group': False,
    # Named argument formats (anything else is a string).
    'format': {
        'group_name':                                 'lowerdash',
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
        'metadata_name':                              'lowerdash',
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
        table = 'csv2_groups'
        rc, msg = config.db_insert(table, table_fields(fields, table, columns, 'insert'))
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

        table = 'csv2_group_metadata'
        meta_dict = {
            "group_name": fields['group_name'],
            "metadata_name": filename, 
            "enabled": 1,
            "priority": 0,
            "metadata": filedata,
            "mime_type": "cloud-config"
        }
        rc, msg = config.db_insert(table, meta_dict)
        if rc != 0:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group add "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))


        # Commit the updates, configure firewall and return.
        config.db_commit()
        configure_fw(config)
        config.db_close()
        return group_list(request, active_user=active_user, response_code=0, message='group "%s" successfully added.' % (fields['group_name']))

    ### Bad request.
    else:
        config.db_close()
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
                table = 'csv2_groups'
                where_clause = "group_name='%s'" % active_user.active_group
                rc, msg = config.db_update(table, table_fields(fields, table, columns, 'update'), where=where_clause)
                if rc == 0:
                    # Commit the updates, configure firewall and return.
                    config.db_commit()
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
    pre_rc = rc
    
    # If User/Groups successfully set, retrieve group information.
    if user_groups_set:
        where_clause = "group_name='%s'" % active_user.active_group
        rc, msg, defaults_list = config.db_query("csv2_groups", where=where_clause)

        # Replace None values with "".
        for defaults in defaults_list:
            for key, value in defaults.items():
                if value == None:
                    defaults_list[0][key]=""

#       # And additional information for the web page.
#       if request.META['HTTP_ACCEPT'] != 'application/json':
        # Get all the images in group:
        rc, msg, image_list = config.db_query("cloud_images", where=where_clause)

        # Get all the flavors in group:
        rc, msg, flavor_list = config.db_query("cloud_flavors", where=where_clause)

        # Get all keynames in group:
        rc, msg, keypairs_list = config.db_query("cloud_keypairs", where=where_clause)

        # Get all networks in group:
        rc, msg, network_list = config.db_query("cloud_networks", where=where_clause)

        # Get all security_groups in group:
        rc, msg, security_groups_list = config.db_query("cloud_security_groups", where=where_clause)

        # Get the group default metadata list:
        rc, msg, _group_list = config.db_query("view_groups_with_metadata_info", where=where_clause)
        _group_list, metadata_dict = qt(
            _group_list,
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
    final_rc = rc if pre_rc == 0 else pre_rc
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
            'response_code': final_rc,
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

        # Delete any group metadata files for the group.
        where_clause = "group_name='%s'" % fields['group_name']
        rc, msg, _group_list = config.db_query("view_groups_with_metadata_names", where=where_clause)
        for row in _group_list:
            if row['group_name'] == fields['group_name'] and row['metadata_names']:
                metadata_names = row['metadata_names'].split(',')
                table = 'csv2_group_metadata'
                for metadata_name in metadata_names:
                    # Delete the group metadata files.
                    where_clause = "group_name='%s' and metadata_name='%s'" % (fields['group_name'], metadata_name)
                    rc, msg = config.db_delete(table, where=where_clause)
                    if rc != 0:
                        config.db_close()
                        return group_list(request, active_user=active_user, response_code=1, message='%s group metadata file delete "%s::%s" failed - %s.' % (lno(MODID), fields['group_name'], metadata_name, msg))

        # Check if group exists
        table = 'csv2_groups'
        where_clause = "group_name='%s'" % fields['group_name']
        rc, msg, found_group_list = config.db_query(table, where=where_clause)
        if not found_group_list or len(found_group_list) == 0:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group resources delete "%s" failed - the request did not match any rows.' % (lno(MODID), fields['group_name'])        )

        # Delete the csv2_clouds.
        table = 'csv2_clouds'
        rc, msg = config.db_delete(table, where=where_clause)
        if rc != 0:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group resources delete "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        # Delete the csv2_cloud_metadata.
        table = 'csv2_cloud_metadata'
        rc, msg = config.db_delete(table, where=where_clause)

        if rc != 0:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group resource metadata delete "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        # Delete the csv2_group_metadata_exclusions.
        table = 'csv2_group_metadata_exclusions'
        rc, msg = config.db_delete(table, where=where_clause)
        if rc != 0:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s delete group metadata exclusions for group "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        # Delete the csv2_user_groups.
        table = 'csv2_user_groups'
        rc, msg = config.db_delete(table, where=where_clause)
        if rc != 0:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group users delete "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))


        # Delete the csv2_cloud_aliases.
        table = 'csv2_cloud_aliases'
        rc, msg = config.db_delete(table, where=where_clause)
        if rc != 0:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group resources delete "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        # Delete the csv2_vms.
        table = 'csv2_vms'
        rc, msg = config.db_delete(table, where=where_clause)
        if rc != 0:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group VMs defaults delete "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        # Delete the cloud_keypairs.
        table = 'cloud_keypairs'
        rc, msg = config.db_delete(table, where=where_clause)
        if rc != 0:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group keynames delete "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        # Delete the cloud_networks.
        table = 'cloud_networks'
        rc, msg = config.db_delete(table, where=where_clause)
        if rc != 0:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group networks delete "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        # Delete the cloud_security_groups.
        table = 'cloud_security_groups'
        rc, msg = config.db_delete(table, where=where_clause)
        if rc != 0:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group  security groups delete "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        # Delete the cloud_limits.
        table = 'cloud_limits'
        rc, msg = config.db_delete(table, where=where_clause)
        if rc != 0:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group limits delete "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        # Delete the cloud_images.
        table = 'cloud_images'
        rc, msg = config.db_delete(table, where=where_clause)
        if rc != 0:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group images delete "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        # Delete the cloud_flavors.
        table = 'cloud_flavors'
        rc, msg = config.db_delete(table, where=where_clause)
        if rc != 0:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group flavors delete "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        # Delete the group.
        table = 'csv2_groups'
        rc, msg = config.db_delete(table, where=where_clause)
        if rc == 0:
            # Commit the deletions, configure firewall and return.
            config.db_commit()
            configure_fw(config)
            config.db_close()
            return group_list(request, active_user=active_user, response_code=0, message='group "%s" successfully deleted.' % (fields['group_name']))
        else:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group delete "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

    ### Bad request.
    else:
      # return group_list(request, active_user=active_user, response_code=1, message='%s group delete request did not contain mandatory parameter "group_name".' % lno(MODID))
        config.db_close()
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
        rc, msg, _group_list = config.db_query("view_groups_with_metadata_names", order_by="group_name")
        metadata_dict = {}
    else:
        rc, msg, _group_list_raw = config.db_query("view_groups_with_metadata_names", order_by="group_name")
        _group_list, metadata_dict = qt(
            _group_list_raw,
            keys = {
                'primary': [
                    'group_name',
                    ],
                'secondary': [
                    'metadata_names',
                    'metadata_enabled',
                    'metadata_priority',
                    'metadata_mime_type',
                    ]
                },
            prune=['password']    
            )

    # Retrieve user/groups list (dictionary containing list for each user).
    rc, msg, groups_per_user_raw = config.db_query("view_user_groups")
    groups_per_user = qt(
        groups_per_user_raw,
            prune=['password']    
            )

    rc, msg, group_defaults = config.db_query("csv2_groups")
    

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
            return metadata_new(request, active_user, response_code=1, message='%s group metadata-add %s' % (lno(MODID), msg))

        # Add the group metadata file.
        table = 'csv2_group_metadata'
        rc, msg = config.db_insert(table, table_fields(fields, table, columns, 'insert'))
        if rc == 0:
            config.db_close(commit=True)
            return render(request, 'csv2/reload_parent.html', {'group_name': fields['group_name'], 'response_code': 0, 'message': 'group metadata file "%s::%s" successfully added.' % (active_user.active_group, fields['metadata_name'])})

        else:
            config.db_close()
            return metadata_new(request, active_user, response_code=1, message='%s group metadata-add "%s::%s" failed - %s.' % (lno(MODID), active_user.active_group, fields['metadata_name'], msg))


    ### Bad request.
    else:
        config.db_close()
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
            metadata_name = request.POST.get("metadata_name")
            if metadata_name:
                return metadata_fetch(request, response_code=1, message='%s group metadata-delete %s' % (lno(MODID), msg), metadata_name=metadata_name)
            return render(request, 'csv2/blank_msg.html', {'response_code': 1, 'message': '%s group metadata-delete %s' % (lno(MODID), msg)})

        # Check if metadata file exists
        table = 'csv2_group_metadata'
        where_clause = "group_name='%s' and metadata_name='%s'" % (active_user.active_group, fields['metadata_name'])
        rc, msg, found_metadata_list = config.db_query(table, where=where_clause)
        if not found_metadata_list or len(found_metadata_list) == 0:
            config.db_close()
            return metadata_fetch(request, response_code=1, message='%s group metadata-delete "%s::%s" failed - the request did not match any rows.' % (lno(MODID), active_user.active_group, fields['metadata_name']), metadata_name=fields['metadata_name'])
        
        # Delete the csv2_group_metadata_exclusions.
        table = 'csv2_group_metadata_exclusions'
        where_clause = "group_name='%s' and metadata_name='%s'" % (fields['group_name'], fields['metadata_name'])
        rc, msg = config.db_delete(table, where=where_clause)
        if rc != 0:
            config.db_close()
            return metadata_fetch(request, response_code=1, message='%s delete group metadata exclusion for group=%s, metadata=%s failed - %s.' % (lno(MODID), fields['group_name'], fields['metadata_name'], msg), metadata_name=fields['metadata_name'])

        # Delete the group metadata file.
        table = 'csv2_group_metadata'
        where_clause = "group_name='%s' and metadata_name='%s'" % (active_user.active_group, fields['metadata_name'])
        rc, msg = config.db_delete(table, where=where_clause)
        if rc == 0:
            config.db_close(commit=True)
            return render(request, 'csv2/reload_parent.html', {'group_name': fields['group_name'], 'response_code': 0, 'message': 'group metadata file "%s::%s" successfully deleted.' % (active_user.active_group, fields['metadata_name'])})

        else:
            config.db_close()
            return metadata_fetch(request, response_code=1, message='%s group metadata-delete "%s::%s" failed - %s.' % (lno(MODID), active_user.active_group, fields['metadata_name'], msg), metadata_name=fields['metadata_name'])


    ### Bad request.
    else:
      # return render(request, 'csv2/blank_msg.html', {'response_code': 1, 'message': '%s group metadata-delete request did not contain mandatory parameter "metadata_name".' % lno(MODID)})
        config.db_close()
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
    rc, msg, mime_types_list = config.db_query("csv2_mime_types")

    # If we are NOT returning from an update, we are fetching from webpage
    if metadata_name == None:
        field_error = validate_url_fields('%s group metadata_fetch' % lno(MODID), request, 'csv2/blank_msg.html', active_user.kwargs, ['metadata_name'])
        if field_error:
            return field_error
        metadata_name = active_user.kwargs['metadata_name']

    # Retrieve metadata file.
    if metadata_name:
        METADATA = "csv2_group_metadata"
        where_clause = "group_name='%s' and metadata_name='%s'" % (active_user.active_group, metadata_name)
        rc, msg, METADATAobj = config.db_query(METADATA, where=where_clause)
        if METADATAobj:
            for row in METADATAobj:
                context = {
                    'group_name': row["group_name"],
                    'metadata': row["metadata"],
                    'metadata_enabled': row["enabled"],
                    'metadata_priority': row["priority"],
                    'metadata_mime_type': row["mime_type"],
                    'metadata_name': row["metadata_name"],
                    'mime_types_list': mime_types_list,
                    'response_code': response_code,
                    'message': message,
                    'is_superuser': active_user.is_superuser,
                    'version': config.get_version()
                    }

                config.db_close()
                return render(request, 'csv2/meta_editor.html', context)
        
        if rc == 0:
            msg = message if message else 'group metadata_fetch, file "%s::%s" does not exist.' % (active_user.active_group, metadata_name)
        else:
            msg = message if message else 'group metadata_fetch, file "%s::%s" does not exist: %s.' % (active_user.active_group, metadata_name, msg)
        config.db_close()
        return render(request, 'csv2/blank_msg.html', {'response_code': 1, 'message': msg})

    msg = message if message else 'group metadata_fetch, metadata file name omitted.'
    config.db_close()
    return render(request, 'csv2/blank_msg.html', {'response_code': 1, 'message': msg})

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
    where_clause = "group_name='%s'" % (active_user.active_group)
    rc, msg, group_metadata_list = config.db_query("csv2_group_metadata", where=where_clause)

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
def metadata_new(request, active_user=None, response_code=0, message='new-group-metadata'):

    context = {}

    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    if not active_user:
        rc, msg, active_user = set_user_groups(config, request, super_user=False)
        if rc != 0:
            config.db_close()
            return render(request, 'csv2/blank_msg.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})

    # Get mime type list:
    rc, msg, mime_types_list = config.db_query("csv2_mime_types")

    context = {
        'group_name': active_user.active_group,
        'metadata': "",
        'metadata_enabled': 0,
        'metadata_priority': 0,
        'metadata_mime_type': "",
        'metadata_name': "",
        'mime_types_list': mime_types_list,
        'response_code': response_code,
        'action_type': "new-group-metadata",
        'message': message,
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
    where_clause = "group_name='%s' and metadata_name='%s'" % (active_user.active_group, fields['metadata_name'])
    rc, msg, group_metadata_list = config.db_query("csv2_group_metadata", where=where_clause)

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
            metadata_name = request.POST.get("metadata_name")
            if metadata_name:
                return metadata_fetch(request, response_code=1, message='%s group metadata-update %s' % (lno(MODID), msg), metadata_name=metadata_name)
            return render(request, 'csv2/blank_msg.html', {'response_code': 1, 'message': '%s group metadata-update %s' % (lno(MODID), msg)})

        # Update the group metadata file.
        table = 'csv2_group_metadata'
        updates = table_fields(fields, table, columns, 'update')
        if len(updates) < 3: #updates always have to have the keys so (name & group) so unless there is 3 fields there is no update to do.
            config.db_close()
            return metadata_fetch(request, response_code=1, message='%s group metadata-update "%s::%s" specified no fields to update and was ignored.' % (lno(MODID), active_user.active_group, fields['metadata_name']), metadata_name=fields['metadata_name'])

        where_clause = 'group_name="%s" and metadata_name="%s"' % (active_user.active_group, fields['metadata_name'])
        
        # Check if metadata file exists
        rc, msg, found_metadata_list = config.db_query(table, where=where_clause)
        if not found_metadata_list or len(found_metadata_list) == 0:
            config.db_close()
            return metadata_fetch(request, response_code=1, message='%s group metadata-update "%s::%s" failed - the request did not match any rows.' % (lno(MODID), active_user.active_group, fields['metadata_name']), metadata_name=fields['metadata_name'])
        
        rc, msg = config.db_update(table, updates, where=where_clause)
        if rc == 0:
            config.db_close(commit=True)
        
            message='group metadata file "%s::%s" successfully  updated.' % (fields['group_name'], fields['metadata_name'])

            return metadata_fetch(request, response_code=0, message=message, metadata_name=fields['metadata_name'])

        else:
            config.db_close()
            return metadata_fetch(request, response_code=1, message='%s group metadata-update "%s::%s" failed - %s.' % (lno(MODID), active_user.active_group, fields['metadata_name'], msg), metadata_name=fields['metadata_name'])

    ### Bad request.
    else:
        config.db_close()
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
                config.db_close()
                return group_list(request, active_user=active_user, response_code=1, message='%s group update, "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

        # Update the group.
        table = 'csv2_groups'
        group_updates = table_fields(fields, table, columns, 'update')

        # group_updates should always have the group name so it should have > 1 updates for there to actually be a change
        if len(group_updates) > 1:
            where_clause = 'group_name="%s"' % fields['group_name']
            
            # Check if group exists
            rc, msg, found_group_list = config.db_query(table, where=where_clause)
            if not found_group_list or len(found_group_list) == 0:
                config.db_close()
                return group_list(request, active_user=active_user, response_code=1, message='%s group update, "%s" failed - the request did not match any rows.' % (lno(MODID), fields['group_name']))
            
            rc, msg = config.db_update(table, group_updates, where=where_clause)
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
            config.db_commit()
            configure_fw(config)
            config.db_close()
            return group_list(request, active_user=active_user, response_code=0, message='group "%s" successfully updated.' % (fields['group_name']))
        else:
            config.db_close()
            return group_list(request, active_user=active_user, response_code=1, message='%s group update "%s" failed - %s.' % (lno(MODID), fields['group_name'], msg))

    ### Bad request.
    else:
        return group_list(request, active_user=active_user, response_code=1, message='%s group update, invalid method "%s" specified.' % (lno(MODID), request.method))

