from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import requires_csrf_token
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from django.contrib.auth.models import User #to get auth_user table
from .models import user as csv2_user
from . import config

from .view_utils import \
    db_close, \
    db_execute, \
    db_open, \
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
    validate_fields, \
    verifyUser
from collections import defaultdict
import bcrypt

from sqlalchemy import exists
from sqlalchemy.sql import select
from lib.schema import *
import sqlalchemy.exc

# lno: GV - error code identifier.

#-------------------------------------------------------------------------------

GROUP_KEYS = {
    'auto_active_group': False,
    # Named argument formats (anything else is a string).
    'format': {
        'group_name':          'lowerdash',
        'csrfmiddlewaretoken': 'ignore',
        'group':               'ignore',
        'username':            'ignore',
        'user_option':         ['add', 'delete'],
        },
    }

GROUP_DEFAULTS_KEYS = {
    'auto_active_group': True,
    # Named argument formats (anything else is a string).
    'format': {
        'csrfmiddlewaretoken': 'ignore',
        'group':               'ignore',
        'job_cpus':            'integer',
        'job_disk':            'integer',
        'job_ram':             'integer',
        'job_swap':            'integer',
        },
    }

METADATA_KEYS = {
    # Should the active_group be automatically inserted into the primary keys.
    'auto_active_group': True,
    'format': {
        'enabled':             'dboolean',
        'priority':            'integer',
        'metadata':            'metadata',
        'metadata_name':       'lowercase',
        'mime_type':           ('csv2_mime_types', 'mime_type'),

        'csrfmiddlewaretoken': 'ignore',
        'group':               'ignore',
        },
    }

IGNORE_METADATA_NAME = {
    'format': {
        'metadata_name':       'ignore',
        },
    }

IGNORE_KEYS = {
    'format': {
        'cloud_name':           'ignore',
        'username':             'ignore',
        'vmid':                 'ignore',
        'id':                   'ignore',
        },
    }

#-------------------------------------------------------------------------------

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
        db_engine, db_session, db_connection, db_map = db_ctl = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(request, db_ctl)
        if rc != 0:
            db_close(db_ctl)
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('GV00'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [GROUP_KEYS], db_ctl, ['csv2_groups', 'csv2_group_defaults','csv2_user_groups', 'csv2_user,n'], active_user)
        if rc != 0:        
            db_close(db_ctl)
            return list(request, selector='-', response_code=1, message='%s group add %s' % (lno('GV01'), msg), active_user=active_user, user_groups=user_groups)

        # Validity check the specified users.
        if 'username' in fields:
            rc, msg = manage_user_group_verification(db_ctl, tables, fields['username'], None) 
            if rc != 0:
                db_close(db_ctl)
                return list(request, selector=fields['username'], response_code=1, message='%s group add, "%s" failed - %s.' % (lno('GV97'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups)

        # Add the group.
        table = tables['csv2_groups']
        rc, msg = db_execute(db_ctl, table.insert().values(table_fields(fields, table, columns, 'insert')))
        if rc != 0:
            db_close(db_ctl)
            return list(request, selector=fields['group_name'], response_code=1, message='%s group add "%s" failed - %s.' % (lno('GV02'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

        # Add user_groups.
        if 'username' in fields:
            rc, msg = manage_group_users(db_ctl, tables, fields['group_name'], fields['username'])
            if rc != 0:
                db_close(db_ctl)

        # Add the group defaults.
        table = tables['csv2_group_defaults']
        rc, msg = db_execute(db_ctl, table.insert().values(table_fields(fields, table, columns, 'insert')))
        if rc == 0:
            db_close(db_ctl, commit=True)
            return list(request, selector=fields['group_name'], response_code=0, message='group "%s" successfully added.' % (fields['group_name']), active_user=active_user, user_groups=user_groups, attributes=columns)
        else:
            db_close(db_ctl)
            return list(request, selector=fields['group_name'], response_code=1, message='%s group defaults add "%s" failed - %s.' % (lno('GV03'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

    ### Bad request.
    else:
        return list(request, response_code=1, message='%s group add, invalid method "%s" specified.' % (lno('GV04'), request.method))

#-------------------------------------------------------------------------------

def defaults(request):
    """
    Update and list group defaults.
    """

    if not verifyUser(request):
        raise PermissionDenied

    # open the database.
    db_engine, db_session, db_connection, db_map = db_ctl = db_open()

    message = None
    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user, user_groups = set_user_groups(request, db_ctl)
    if rc == 0:
        if request.method == 'POST':
                # Validate input fields.
                rc, msg, fields, tables, columns = validate_fields(request, [GROUP_DEFAULTS_KEYS], db_ctl, ['csv2_group_defaults'], active_user)
                if rc == 0:        
                    # Update the group defaults.
                    table = tables['csv2_group_defaults']
                    rc, msg = db_execute(db_ctl, table.update().where(table.c.group_name==active_user.active_group).values(table_fields(fields, table, columns, 'update')))
                    if rc == 0:
                        db_session.commit()
                        message='group defaults "%s" successfully updated.' % (active_user.active_group)
                    else:
                        message='%s group defaults update "%s" failed - %s.' % (lno('GV05'), active_user.active_group, msg)
                else:
                    message='%s group defaults update %s' % (lno('GV06'), msg)
    else:
        message='%s %s' % (lno('GV07'), msg)

    if message and message[:2] == 'GV':
        defaults_list = []
        response_code = 1
    else:
        s = select([csv2_group_defaults]).where(csv2_group_defaults.c.group_name==active_user.active_group)
        defaults_list = qt(db_connection.execute(s))
        response_code = 0

    db_close(db_ctl)

    # Render the page.
    context = {
            'active_user': active_user,
            'active_group': active_user.active_group,
            'user_groups': user_groups,
            'defaults_list': defaults_list,
            'response_code': response_code,
            'message': message,
            'enable_glint': config.enable_glint
        }

    return render(request, 'csv2/group_defaults.html', context)



#-------------------------------------------------------------------------------

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
        db_engine, db_session, db_connection, db_map = db_ctl = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(request, db_ctl)
        if rc != 0:
            db_close(db_ctl)
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('GV08'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [GROUP_DEFAULTS_KEYS, GROUP_KEYS, IGNORE_METADATA_NAME, IGNORE_KEYS], db_ctl, [
                'csv2_groups',
                'csv2_group_metadata',
                'csv2_group_defaults',
                'csv2_group_resources',
                'csv2_group_resource_metadata',
                'csv2_user_groups',
                'csv2_vms',
                'cloud_networks',
                'cloud_limits',
                'cloud_images',
                'cloud_flavors'
            ], active_user)
        if rc != 0:        
            db_close(db_ctl)
            return list(request, selector='-', response_code=1, message='%s group delete %s' % (lno('CV09'), msg), active_user=active_user, user_groups=user_groups)

        # Delete any group metadata files for the group.
        s = select([view_groups_with_metadata_names]).where((view_groups_with_metadata_names.c.group_name == fields['group_name']))
        group_list = qt(db_connection.execute(s))
        for row in group_list:
            if row['group_name'] == fields['group_name'] and row['metadata_names']:
                metadata_names = row['metadata_names'].split(',')
                table = tables['csv2_group_metadata']
                for metadata_name in metadata_names:
                    # Delete the group metadata files.
                    rc, msg = db_execute(
                        db_ctl,
                        table.delete((table.c.group_name==fields['group_name']) & (table.c.metadata_name==metadata_name))
                        )
                    if rc != 0:
                        db_close(db_ctl)
                        return list(request, selector=fields['group_name'], response_code=1, message='%s group metadata file delete "%s::%s" failed - %s.' % (lno('GV10'), fields['group_name'], metadata_name, msg), active_user=active_user, user_groups=user_groups, attributes=columns)

        # Delete the group defaults.
        table = tables['csv2_group_defaults']
        rc, msg = db_execute(
            db_ctl,
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            db_close(db_ctl)
            return list(request, selector=fields['group_name'], response_code=1, message='%s group defaults delete "%s" failed - %s.' % (lno('GV11'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)


        # Delete the csv2_group_resources.
        table = tables['csv2_group_resources']
        rc, msg = db_execute(
            db_ctl,
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            db_close(db_ctl)
            return list(request, selector=fields['group_name'], response_code=1, message='%s group defaults delete "%s" failed - %s.' % (lno('GV12'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)


        # Delete the csv2_group_resource_metadata.
        table = tables['csv2_group_resource_metadata']
        rc, msg = db_execute(
            db_ctl,
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            db_close(db_ctl)
            return list(request, selector=fields['group_name'], response_code=1, message='%s group defaults delete "%s" failed - %s.' % (lno('GV13'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

        # Delete the csv2_user_groups.
        table = tables['csv2_user_groups']
        rc, msg = db_execute(
            db_ctl,
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            db_close(db_ctl)
            return list(request, selector=fields['group_name'], response_code=1, message='%s group defaults delete "%s" failed - %s.' % (lno('GV14'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

        # Delete the csv2_vms.
        table = tables['csv2_vms']
        rc, msg = db_execute(
            db_ctl,
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            db_close(db_ctl)
            return list(request, selector=fields['group_name'], response_code=1, message='%s group defaults delete "%s" failed - %s.' % (lno('GV15'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

        # Delete the cloud_networks.
        table = tables['cloud_networks']
        rc, msg = db_execute(
            db_ctl,
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            db_close(db_ctl)
            return list(request, selector=fields['group_name'], response_code=1, message='%s group defaults delete "%s" failed - %s.' % (lno('GV16'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

        # Delete the cloud_limits.
        table = tables['cloud_limits']
        rc, msg = db_execute(
            db_ctl,
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            db_close(db_ctl)
            return list(request, selector=fields['group_name'], response_code=1, message='%s group defaults delete "%s" failed - %s.' % (lno('GV17'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

        # Delete the cloud_images.
        table = tables['cloud_images']
        rc, msg = db_execute(
            db_ctl,
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            db_close(db_ctl)
            return list(request, selector=fields['group_name'], response_code=1, message='%s group defaults delete "%s" failed - %s.' % (lno('GV18'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

        # Delete the cloud_flavors.
        table = tables['cloud_flavors']
        rc, msg = db_execute(
            db_ctl,
            table.delete(table.c.group_name==fields['group_name']),
            allow_no_rows=True
            )
        if rc != 0:
            db_close(db_ctl)
            return list(request, selector=fields['group_name'], response_code=1, message='%s group defaults delete "%s" failed - %s.' % (lno('GV19'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

        # Delete the group.
        table = tables['csv2_groups']
        rc, msg = db_execute(
            db_ctl,
            table.delete(table.c.group_name==fields['group_name'])
            )
        if rc == 0:
            db_close(db_ctl, commit=True)
            return list(request, selector=fields['group_name'], response_code=0, message='group "%s" successfully deleted.' % (fields['group_name']), active_user=active_user, user_groups=user_groups, attributes=columns)
        else:
            db_close(db_ctl)
            return list(request, selector=fields['group_name'], response_code=1, message='%s group delete "%s" failed - %s.' % (lno('GV20'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

    ### Bad request.
    else:
        return list(request, response_code=1, message='%s group delete, invalid method "%s" specified.' % (lno('GV21'), request.method))

#-------------------------------------------------------------------------------

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
    db_engine, db_session, db_connection, db_map = db_ctl = db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    if not active_user:
        rc, msg, active_user, user_groups = set_user_groups(request, db_ctl)
        if rc != 0:
            db_close(db_ctl)
            return render(request, 'csv2/groups.html', {'response_code': 1, 'message': msg})

    # Retrieve group information.
    if request.META['HTTP_ACCEPT'] == 'application/json':
        s = select([view_groups_with_metadata_names]).order_by('group_name')
        group_list = qt(db_connection.execute(s))
        metadata_dict = {}
    else:
        s = select([view_groups_with_metadata]).order_by('group_name')
        group_list, metadata_dict = qt(
            db_connection.execute(s),
            keys = {
                'primary': [
                    'group_name',
                    ],
                'secondary': [
                    'metadata_name',
                    'metadata_enabled',
                    'metadata_priority',
                    'metadata_mime_type',
                    'metadata',
                    ]
                },
            prune=['password']    
            )

    # Retrieve user/groups list (dictionary containing list for each user).
    s = select([view_user_groups])
    groups_per_user = qt(
        db_connection.execute(s),
            prune=['password']    
            )

    db_close(db_ctl)

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
            'group_list': group_list,
            'groups_per_user': groups_per_user,
            'metadata_dict': metadata_dict,
            'current_group': current_group,
            'response_code': response_code,
            'message': message,
            'enable_glint': config.enable_glint
        }

    return render(request, 'csv2/groups.html', context)

#-------------------------------------------------------------------------------

def metadata_add(request):
    """
    This function should recieve a post request with a payload of a metadata file
    to add to a given group.
    """

    if not verifyUser(request):
        raise PermissionDenied

    if request.method == 'POST' and 'metadata_name' in request.POST:
        # open the database.
        db_engine, db_session, db_connection, db_map = db_ctl = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(request, db_ctl)
        if rc != 0:
            db_close(db_ctl)
            return render(request, 'csv2/groups.html', {'response_code': 1, 'message': '%s %s' % (lno('GV26'), msg)})

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [METADATA_KEYS], db_ctl, ['csv2_group_metadata'], active_user)
        if rc != 0:        
            db_close(db_ctl)
            return render(request, 'csv2/groups.html', {'response_code': 1, 'message': '%s group metadata-add %s' % (lno('GV27'), msg)})

        # Add the group metadata file.
        table = tables['csv2_group_metadata']
        rc, msg = db_execute(db_ctl, table.insert().values(table_fields(fields, table, columns, 'insert')))
        if rc == 0:
            db_close(db_ctl, commit=True)
            return render(request, 'csv2/groups.html', {'response_code': 0, 'message': 'group metadata file "%s::%s" successfully added.' % (active_user.active_group, fields['metadata_name'])})
        else:
            db_close(db_ctl)
            return render(request, 'csv2/groups.html', {'response_code': 1, 'message': '%s group metadata-add "%s::%s" failed - %s.' % (lno('GV28'), active_user.active_group, fields['metadata_name'], msg)})

    ### Bad request.
    else:
        if request.method != 'POST':
            return render(request, 'csv2/groups.html', {'response_code': 1, 'message': '%s group metadata_add, invalid method "%s" specified.' % (lno('GV29'), request.method)})
        else:
            return render(request, 'csv2/groups.html', {'response_code': 1, 'message': '%s group metadata_add, no group name specified.' % lno('GV30')})

#-------------------------------------------------------------------------------

def metadata_delete(request):
    """
    This function should recieve a post request with a payload of a metadata file
    name to be deleted from the given group.
    """

    if not verifyUser(request):
        raise PermissionDenied

    if request.method == 'POST' and 'metadata_name' in request.POST:
        # open the database.
        db_engine, db_session, db_connection, db_map = db_ctl = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(request, db_ctl)
        if rc != 0:
            db_close(db_ctl)
            return render(request, 'csv2/groups.html', {'response_code': 1, 'message': '%s %s' % (lno('GV18'), msg)})

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [METADATA_KEYS], db_ctl, ['csv2_group_metadata'], active_user)
        if rc != 0:        
            db_close(db_ctl)
            return render(request, 'csv2/groups.html', {'response_code': 1, 'message': '%s group metadata-add %s' % (lno('CV32'), msg)})

        # Delete the group metadata file.
        table = tables['csv2_group_metadata']
        rc, msg = db_execute(
            db_ctl,
            table.delete( \
                (table.c.group_name==active_user.active_group) & \
                (table.c.metadata_name==fields['metadata_name']) \
                )
            )
        if rc == 0:
            db_close(db_ctl, commit=True)
            return render(request, 'csv2/groups.html', {'response_code': 0, 'message': 'group metadata file "%s::%s" successfully deleted.' % (active_user.active_group, fields['metadata_name'])})
        else:
            db_close(db_ctl)
            return render(request, 'csv2/groups.html', {'response_code': 1, 'message': '%s group metadata-delete "%s::%s" failed - %s.' % (lno('GV33'), active_user.active_group, fields['metadata_name'], msg)})

    ### Bad request.
    else:
        if request.method != 'POST':
            return render(request, 'csv2/groups.html', {'response_code': 1, 'message': '%s group metadata_delete, invalid method "%s" specified.' % (lno('GV34'), request.method)})
        else:
            return render(request, 'csv2/groups.html', {'response_code': 1, 'message': '%s group metadata_delete, no group name specified.' % lno('GV35')})

#-------------------------------------------------------------------------------

def metadata_fetch(request, selector=None):
    if not verifyUser(request):
        raise PermissionDenied

    # open the database.
    db_engine, db_session, db_connection, db_map = db_ctl = db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user, user_groups = set_user_groups(request, db_ctl)
    if rc != 0:
        db_close(db_ctl)
        return render(request, 'csv2/groups.html', {'response_code': 1, 'message': '%s %s' % (lno('GV36'), msg)})

    # Retrieve metadata file.
    id = request.path.split('/')
    if len(id) > 3:
        METADATA = db_map.classes.csv2_group_metadata
        METADATAobj = db_session.query(METADATA).filter((METADATA.group_name == active_user.active_group) & (METADATA.metadata_name == id[3]))
        if METADATAobj:
            for row in METADATAobj:
                context = {
                    'group_name': row.group_name,
                    'metadata': row.metadata,
                    'metadata_enabled': row.enabled,
                    'metadata_priority': row.priority,
                    'metadata_mime_type': row.mime_type,
                    'metadata_name': row.metadata_name,
                    'response_code': 0,
                    'message': None,
                    'enable_glint': config.enable_glint
                    }
            
                db_close(db_ctl)
                return render(request, 'csv2/groups.html', context)
         
        db_close(db_ctl)
        return render(request, 'csv2/groups.html', {'response_code': 1, 'message': 'group metadata_fetch, file "%s::%s" does not exist.' % (active_user.active_group, id[3])})

    db_close(db_ctl)
    return render(request, 'csv2/groups.html', {'response_code': 1, 'message': 'group metadata_fetch, metadata file name omitted.'})

#-------------------------------------------------------------------------------

@requires_csrf_token
def metadata_list(request):

    if not verifyUser(request):
        raise PermissionDenied

    # open the database.
    db_engine, db_session, db_connection, db_map = db_ctl = db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user, user_groups = set_user_groups(request, db_ctl)
    if rc != 0:
        db_close(db_ctl)
        return render(request, 'csv2/clouds.html', {'response_code': 1, 'message': msg})

    # Retrieve cloud/metadata information.
    s = select([csv2_group_metadata]).where(csv2_group_metadata.c.group_name == active_user.active_group)
    group_metadata_list = qt(db_connection.execute(s))
    db_close(db_ctl)

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

def metadata_update(request):
    """
    This function should recieve a post request with a payload of a metadata file
    as a replacement for the specified file.
    """

    if not verifyUser(request):
        raise PermissionDenied

    if request.method == 'POST' and 'metadata_name' in request.POST:

        # open the database.
        db_engine, db_session, db_connection, db_map = db_ctl = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(request, db_ctl)
        if rc != 0:
            db_close(db_ctl)
            return render(request, 'csv2/groups.html', {'response_code': 1, 'message': '%s %s' % (lno('GV37'), msg)})

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [METADATA_KEYS], db_ctl, ['csv2_group_metadata'], active_user)
        if rc != 0:        
            db_close(db_ctl)
            return render(request, 'csv2/groups.html', {'response_code': 1, 'message': '%s group metadata-add %s' % (lno('CV38'), msg)})

        # Update the group metadata file.
        table = tables['csv2_group_metadata']
        rc, msg = db_execute(db_ctl, table.update().where( \
            (table.c.group_name==active_user.active_group) & \
            (table.c.metadata_name==fields['metadata_name']) \
            ).values(table_fields(fields, table, columns, 'update')))
        if rc == 0:
            db_close(db_ctl, commit=True)
            return render(request, 'csv2/groups.html', {'response_code': 0, 'message': 'group metadata file "%s::%s" successfully  updated.' % (active_user.active_group, fields['metadata_name'])})
        else:
            db_close(db_ctl)
            return render(request, 'csv2/groups.html', {'response_code': 1, 'message': '%s group metadata-update "%s::%s" failed - %s.' % (lno('GV39'), active_user.active_group, fields['metadata_name'], msg)})

    ### Bad request.
    else:
        if request.method != 'POST':
            return render(request, 'csv2/groups.html', {'response_code': 1, 'message': '%s group metadata_update, invalid method "%s" specified.' % (lno('GV40'), request.method)})
        else:
            return render(request, 'csv2/groups.html', {'response_code': 1, 'message': '%s group metadata_update, no group name specified.' % lno('GV41')})

#-------------------------------------------------------------------------------

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
        db_engine, db_session, db_connection, db_map = db_ctl = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(request, db_ctl)
        if rc != 0:
            db_close(db_ctl)
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('GV22'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [GROUP_KEYS], db_ctl, ['csv2_groups','csv2_user_groups', 'csv2_user,n'], active_user)
        if rc != 0:        
            db_close(db_ctl)
            return list(request, selector='-', response_code=1, message='%s group update %s' % (lno('GV23'), msg), active_user=active_user, user_groups=user_groups)

        # Validity check the specified users.
        if 'username' in fields:
            rc, msg = manage_user_group_verification(db_ctl, tables, fields['username'], None) 
            if rc != 0:
                return list(request, selector=fields['username'], response_code=1, message='%s group add, "%s" failed - %s.' % (lno('GV96'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups)

        # Update the group.
        table = tables['csv2_groups']
        rc, msg = db_execute(db_ctl, table.update().where(table.c.group_name==fields['group_name']).values(table_fields(fields, table, columns, 'update')))

        # Update user groups.
        if request.META['HTTP_ACCEPT'] == 'application/json':
            if 'username' in fields:
                if 'user_option' in fields and fields['user_option'] == 'delete':
                    rc, msg = manage_group_users(db_ctl, tables, fields['group_name'], users=fields['username'], option='delete')
                else:
                    rc, msg = manage_group_users(db_ctl, tables, fields['group_name'], users=fields['username'], option='add')
        else:
            if 'username' in fields:
                rc, msg = manage_group_users(db_ctl, tables, fields['group_name'], fields['username'])
            else:
                rc, msg = manage_group_users(db_ctl, tables, fields['group_name'], None)

        if rc == 0:
            db_close(db_ctl, commit=True)
            return list(request, selector=fields['group_name'], response_code=0, message='group "%s" successfully updated.' % (fields['group_name']), active_user=active_user, user_groups=user_groups, attributes=columns)
        else:
            db_close(db_ctl)
            return list(request, selector=fields['group_name'], response_code=1, message='%s group update "%s" failed - %s.' % (lno('GV24'), fields['group_name'], msg), active_user=active_user, user_groups=user_groups, attributes=columns)

    ### Bad request.
    else:
        return list(request, response_code=1, message='%s group update, invalid method "%s" specified.' % (lno('GV25'), request.method))

