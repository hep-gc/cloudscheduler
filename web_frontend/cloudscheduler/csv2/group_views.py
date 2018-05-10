from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import requires_csrf_token
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from django.contrib.auth.models import User #to get auth_user table
from .models import user as csv2_user

from .view_utils import \
    db_execute, \
    db_open, \
    getAuthUser, \
    getcsv2User, \
    getSuperUserStatus, \
    lno,  \
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

#-------------------------------------------------------------------------------

GROUP_KEYS = {
    'auto_active_group': False,
    # Named argument formats (anything else is a string).
    'format': {
        'group_name':          'lowercase',

        'csrfmiddlewaretoken': 'ignore',
        'group':               'ignore',
        },
    }

GROUP_DEFAULTS_KEYS = {
    'auto_active_group': True,
    # Named argument formats (anything else is a string).
    'format': {
        'csrfmiddlewaretoken': 'ignore',
        'group':               'ignore',
        },
    }

YAML_KEYS = {
    # Should the active_group be automatically inserted into the primary keys.
    'auto_active_group': True,
    'format': {
        'yaml_name':           'lowercase',

        'csrfmiddlewaretoken': 'ignore',
        'group':               'ignore',
        },
    }

IGNORE_YAML_NAME = {
    'format': {
        'yaml_name':           'ignore',
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
        db_engine,db_session,db_connection,db_map = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(request, db_session, db_map)
        if rc != 0:
            db_connection.close()
            return list(request, selector='-', response_code=1, message='%s %s' (lno('GV00'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [GROUP_DEFAULTS_KEYS, GROUP_KEYS], db_engine, ['csv2_groups', 'csv2_group_defaults'], active_user)
        if rc != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='%s group add %s' % (lno('CV01'), msg), active_user=active_user, user_groups=user_groups)

        # Add the group.
        table = tables['csv2_groups']
        success,message = db_execute(db_connection, table.insert().values(table_fields(fields, table, columns, 'insert')))
        if not success:
            db_connection.close()
            return list(request, selector=fields['group_name'], response_code=1, message='%s group add "%s" failed - %s.' % (lno('GV02'), fields['group_name'], message), active_user=active_user, user_groups=user_groups, attributes=columns)

        # Add the group defaults.
        table = tables['csv2_group_defaults']
        success,message = db_execute(db_connection, table.insert().values(table_fields(fields, table, columns, 'insert')))
        db_connection.close()
        if success:
            return list(request, selector=fields['group_name'], response_code=0, message='group "%s" successfully added.' % (fields['group_name']), active_user=active_user, user_groups=user_groups, attributes=columns)
        else:
            return list(request, selector=fields['group_name'], response_code=1, message='%s group defaults add "%s" failed - %s.' % (lno('GV03'), fields['group_name'], message), active_user=active_user, user_groups=user_groups, attributes=columns)

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
    db_engine,db_session,db_connection,db_map = db_open()

    message = None
    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user, user_groups = set_user_groups(request, db_session, db_map)
    if rc == 0:
        if request.method == 'POST':
                # Validate input fields.
                rc, msg, fields, tables, columns = validate_fields(request, [GROUP_DEFAULTS_KEYS], db_engine, ['csv2_group_defaults'], active_user)
                if rc == 0:        
                    # Update the group defaults.
                    table = tables['csv2_group_defaults']
                    success, message = db_execute(db_connection, table.update().where(table.c.group_name==active_user.active_group).values(table_fields(fields, table, columns, 'update')))
                    if success:
                        message='group defaults "%s" successfully updated.' % (active_user.active_group)
                    else:
                        message='%s group defaults update "%s" failed - %s.' % (lno('GV05'), active_user.active_group, message)
                else:
                    db_connection.close()
                    message='%s group defaults update %s' % (lno('GV06'), msg)
    else:
        message='%s %s' % (lno('GV07'), msg)

    if message and message[:2] == 'GV':
        response_code = 1
    else:
        response_code = 0

    s = select([csv2_group_defaults]).where(csv2_group_defaults.c.group_name==active_user.active_group)
    defaults_list = qt(db_connection.execute(s))

    db_connection.close()

#   # Position the page.
#   obj_act_id = request.path.split('/')
#   if selector:
#       if selector == '-':
#           current_group = ''
#       else:
#           current_group = selector
#   elif len(obj_act_id) > 3 and len(obj_act_id[3]) > 0:
#       current_group = str(obj_act_id[3])
#   else:
#       if len(group_list) > 0:
#           current_group = str(group_list[0]['group_name'])
#       else:
#           current_group = ''

    # Render the page.
    context = {
            'active_user': active_user,
            'active_group': active_user.active_group,
            'user_groups': user_groups,
            'defaults_list': defaults_list,
#           'current_group': current_group,
            'response_code': response_code,
            'message': message
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
        db_engine,db_session,db_connection,db_map = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(request, db_session, db_map)
        if rc != 0:
            db_connection.close()
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('GV08'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [GROUP_DEFAULTS_KEYS, GROUP_KEYS, IGNORE_YAML_NAME], db_engine, ['csv2_groups', 'csv2_group_defaults', 'csv2_group_yaml'], active_user)
        if rc != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='%s group delete %s' % (lno('CV09'), msg), active_user=active_user, user_groups=user_groups)

        # Delete any group/YAML files for the group.
        s = select([view_groups_with_yaml_names]).where((view_groups_with_yaml_names.c.group_name == fields['group_name']))
        group_list = qt(db_connection.execute(s))
        for row in group_list:
            if row['group_name'] == fields['group_name'] and row['yaml_names']:
                yaml_names = row['yaml_names'].split(',')
                table = tables['csv2_group_yaml']
                for yaml_name in yaml_names:
                    # Delete the groupYAML file.
                    success, message = db_execute(
                        db_connection,
                        table.delete((table.c.group_name==fields['group_name']) & (table.c.yaml_name==yaml_name))
                        )
                    if not success:
                        db_connection.close()
                        return list(request, selector=fields['group_name'], response_code=1, message='%s group YAML file delete "%s.%s" failed - %s.' % (lno('GV10'), fields['group_name'], yaml_name, message), active_user=active_user, user_groups=user_groups, attributes=columns)

        # Delete the group defaults.
        table = tables['csv2_group_defaults']
        success, message = db_execute(
            db_connection,
            table.delete(table.c.group_name==fields['group_name'])
            )
        if not success:
            db_connection.close()
            return list(request, selector=fields['group_name'], response_code=1, message='%s group defaults delete "%s" failed - %s.' % (lno('GV11'), fields['group_name'], message), active_user=active_user, user_groups=user_groups, attributes=columns)

        # Delete the group.
        table = tables['csv2_groups']
        success,message = db_execute(
            db_connection,
            table.delete(table.c.group_name==fields['group_name'])
            )
        db_connection.close()
        if success:
            return list(request, selector=fields['group_name'], response_code=0, message='group "%s" successfully deleted.' % (fields['group_name']), active_user=active_user, user_groups=user_groups, attributes=columns)
        else:
            return list(request, selector=fields['group_name'], response_code=1, message='%s group delete "%s" failed - %s.' % (lno('GV12'), fields['group_name'], message), active_user=active_user, user_groups=user_groups, attributes=columns)

    ### Bad request.
    else:
        return list(request, response_code=1, message='%s group delete, invalid method "%s" specified.' % (lno('GV13'), request.method))

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
    db_engine,db_session,db_connection,db_map = db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    if not active_user:
        rc, msg, active_user, user_groups = set_user_groups(request, db_session, db_map)
        if rc != 0:
            db_connection.close()
            return render(request, 'csv2/groups.html', {'response_code': 1, 'message': msg})

    # Retrieve group information.
    if request.META['HTTP_ACCEPT'] == 'application/json':
        s = select([view_groups_with_yaml_names]).order_by('group_name')
        group_list = qt(db_connection.execute(s))
        yaml_dict = {}
    else:
        s = select([view_groups_with_yaml]).order_by('group_name')
        group_list, yaml_dict = qt(
            db_connection.execute(s),
            keys = {
                'primary': [
                    'group_name',
                    ],
                'secondary': [
                    'yaml_name',
                    'yaml_enabled',
                    'yaml_mime_type',
                    'yaml',
                    ]
                },
            prune=['password']    
            )

    db_connection.close()

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
            'yaml_dict': yaml_dict,
            'current_group': current_group,
            'response_code': response_code,
            'message': message
        }

    return render(request, 'csv2/groups.html', context)

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
        db_engine,db_session,db_connection,db_map = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(request, db_session, db_map)
        if rc != 0:
            db_connection.close()
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('GV14'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [GROUP_KEYS], db_engine, ['csv2_groups'], active_user)
        if rc != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='%s group update %s' % (lno('CV15'), msg), active_user=active_user, user_groups=user_groups)

        # Update the group.
        table = tables['csv2_groups']
        success, message = db_execute(db_connection, table.update().where(table.c.group_name==fields['group_name']).values(table_fields(fields, table, columns, 'update')))
        db_connection.close()
        if success:
            return list(request, selector=fields['group_name'], response_code=0, message='group "%s" successfully updated.' % (fields['group_name']), active_user=active_user, user_groups=user_groups, attributes=columns)
        else:
            return list(request, selector=fields['group_name'], response_code=1, message='%s group update "%s" failed - %s.' % (lno('GV16'), fields['group_name'], message), active_user=active_user, user_groups=user_groups, attributes=columns)

    ### Bad request.
    else:
        return list(request, response_code=1, message='%s group update, invalid method "%s" specified.' % (lno('GV17'), request.method))

#-------------------------------------------------------------------------------

def yaml_add(request):
    """
    This function should recieve a post request with a payload of a YAML file
    to add to a given group.
    """

    if not verifyUser(request):
        raise PermissionDenied

    if request.method == 'POST' and 'yaml_name' in request.POST:
        # open the database.
        db_engine,db_session,db_connection,db_map = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(request, db_session, db_map)
        if rc != 0:
            db_connection.close()
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('GV18'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [YAML_KEYS], db_engine, ['csv2_group_yaml'], active_user)
        if rc != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='%s group yaml-add %s' % (lno('CV19'), msg), active_user=active_user, user_groups=user_groups)

        # Add the group yaml file.
        table = tables['csv2_group_yaml']
        success,message = db_execute(db_connection, table.insert().values(table_fields(fields, table, columns, 'insert')))
        db_connection.close()
        if success:
            return list(request, selector=active_user.active_group, response_code=0, message='group YAML file "%s.%s" successfully added.' % (active_user.active_group, fields['yaml_name']), active_user=active_user, user_groups=user_groups, attributes=columns)
        else:
            return list(request, selector=active_user.active_group, response_code=1, message='%s group yaml-add "%s.%s" failed - %s.' % (lno('GV20'), active_user.active_group, fields['yaml_name'], message), active_user=active_user, user_groups=user_groups, attributes=columns)

    ### Bad request.
    else:
        if request.method != 'POST':
            return list(request, response_code=1, message='%s group yaml_add, invalid method "%s" specified.' % (lno('GV21'), request.method))
        else:
            return list(request, response_code=1, message='%s group yaml_add, no group name specified.' % lno('GV22'))

#-------------------------------------------------------------------------------

def yaml_delete(request):
    """
    This function should recieve a post request with a payload of a YAML file
    name to be deleted from the given group.
    """

    if not verifyUser(request):
        raise PermissionDenied

    if request.method == 'POST' and 'yaml_name' in request.POST:
        # open the database.
        db_engine,db_session,db_connection,db_map = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(request, db_session, db_map)
        if rc != 0:
            db_connection.close()
            return list(request, selector='-', response_code=1, message='%s %s' % (ln('GV18'), msg), active_user=active_user, user_groups=user_groupslno('GV23'), )

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [YAML_KEYS], db_engine, ['csv2_group_yaml'], active_user)
        if rc != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='%s group yaml-add %s' % (lno('CV24'), msg), active_user=active_user, user_groups=user_groups)

        # Delete the group yaml file.
        table = tables['csv2_group_yaml']
        success,message = db_execute(
            db_connection,
            table.delete( \
                (table.c.group_name==active_user.active_group) & \
                (table.c.yaml_name==fields['yaml_name']) \
                )
            )
        db_connection.close()
        if success:
            return list(request, selector=active_user.active_group, response_code=0, message='group YAML file "%s.%s" successfully deleted.' % (active_user.active_group, fields['yaml_name']), active_user=active_user, user_groups=user_groups, attributes=columns)
        else:
            return list(request, selector=active_user.active_group, response_code=1, message='%s group yaml-delete "%s.%s" failed - %s.' % (lno('GV25'), active_user.active_group, fields['yaml_name'], message), active_user=active_user, user_groups=user_groups, attributes=columns)

    ### Bad request.
    else:
        if request.method != 'POST':
            return list(request, response_code=1, message='%s group yaml_delete, invalid method "%s" specified.' % (lno('GV26'), request.method))
        else:
            return list(request, response_code=1, message='%s group yaml_delete, no group name specified.' % lno('GV27'))

#-------------------------------------------------------------------------------

def yaml_fetch(request, selector=None):
    if not verifyUser(request):
        raise PermissionDenied

    # open the database.
    db_engine,db_session,db_connection,db_map = db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user, user_groups = set_user_groups(request, db_session, db_map)
    if rc != 0:
        db_connection.close()
        return list(request, selector='-', response_code=1, message='%s %s' % (lno('GV28'), msg), active_user=active_user, user_groups=user_groups)

    # Retrieve YAML file.
    obj_act_id = request.path.split('/')
    if len(obj_act_id) > 3:
        id = obj_act_id[3]
        ids = id.split('.')
        if len(ids) == 2:
            YAML = db_map.classes.csv2_group_yaml
            YAMLobj = db_session.query(YAML).filter((YAML.group_name==ids[0]) & (YAML.yaml_name==ids[1]))
            if YAMLobj:
                for row in YAMLobj:
                    context = {
                        'group_name': row.group_name,
                        'yaml': row.yaml,
                        'yaml_enabled': row.enabled,
                        'yaml_mime_type': row.mime_type,
                        'yaml_name': row.yaml_name,
                        'response_code': 0,
                        'message': None
                        }
                
                    return render(request, 'csv2/groups.html', context)
             
            return render(request, 'csv2/groups.html', {'response_code': 1, 'message': 'group yaml_fetch, file "%s" does not exist.' % id})

    return render(request, 'csv2/groups.html', {'response_code': 1, 'message': 'group yaml_fetch, received an invalid key "%s".' % id})

#-------------------------------------------------------------------------------

def yaml_update(request):
    """
    This function should recieve a post request with a payload of a YAML file
    as a replacement for the specified file.
    """

    if not verifyUser(request):
        raise PermissionDenied

    if request.method == 'POST' and 'yaml_name' in request.POST:

        # open the database.
        db_engine,db_session,db_connection,db_map = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(request, db_session, db_map)
        if rc != 0:
            db_connection.close()
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('GV29'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [YAML_KEYS], db_engine, ['csv2_group_yaml'], active_user)
        if rc != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='%s group yaml-add %s' % (lno('CV30'), msg), active_user=active_user, user_groups=user_groups)

        # Update the group yaml file.
        table = tables['csv2_group_yaml']
        success,message = db_execute(db_connection, table.update().where( \
            (table.c.group_name==active_user.active_group) & \
            (table.c.yaml_name==fields['yaml_name']) \
            ).values(table_fields(fields, table, columns, 'update')))
        db_connection.close()
        if success:
            return list(request, selector=active_user.active_group, response_code=0, message='group YAML file "%s.%s" successfully  updated.' % (active_user.active_group, fields['yaml_name']), active_user=active_user, user_groups=user_groups, attributes=columns)
        else:
            return list(request, selector=active_user.active_group, response_code=1, message='%s group yaml-update "%s.%s" failed - %s.' % (lno('GV31'), active_user.active_group, fields['yaml_name'], message), active_user=active_user, user_groups=user_groups, attributes=columns)

    ### Bad request.
    else:
        if request.method != 'POST':
            return list(request, response_code=1, message='%s group yaml_update, invalid method "%s" specified.' % (lno('GV32'), request.method))
        else:
            return list(request, response_code=1, message='%s group yaml_update, no group name specified.' % lno('GV33'))


