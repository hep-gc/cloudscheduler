from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import requires_csrf_token
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from django.contrib.auth.models import User #to get auth_user table
from .models import user as csv2_user

from .view_utils import db_execute, db_open, getAuthUser, getcsv2User, verifyUser, getSuperUserStatus, map_parameter_to_field_values, qt, render, set_user_groups
from collections import defaultdict
import bcrypt

from sqlalchemy import exists
from sqlalchemy.sql import select
from lib.schema import *
import sqlalchemy.exc

#-------------------------------------------------------------------------------

GROUP_KEYS = (
    # The following fields are the key fields for the table:
    (
        'group_name',
        ),
    # The following fields maybe in the input form but should be ignored.
    (    
        'csrfmiddlewaretoken',
        'group',
        ),
    {
        'group_name': 'l',
        },
    )

YAML_KEYS = (
    # The following fields are the key fields for the table:
    (
        'group_name',
        'yaml_name',
        ),
    # The following fields maybe in the input form but should be ignored.
    (    
        'csrfmiddlewaretoken',
        'group',
        ),
    )

#-------------------------------------------------------------------------------

def add(request):
    """
    This function should receive a post request with a payload of group configuration
    to add the specified group.
    """

    if not verifyUser(request):
        raise PermissionDenied

    if request.method == 'POST':
        # open the database.
        db_engine,db_session,db_connection,db_map = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(request, db_session, db_map)
        if rc != 0:
            db_connection.close()
            return list(request, selector='-', response_code=1, message=msg, active_user=active_user, user_groups=user_groups)

        # Map the field list.
        response_code, table, values = map_parameter_to_field_values(request, db_engine, 'csv2_groups', GROUP_KEYS,  active_user)
        if response_code != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='group add %s' % values, active_user=active_user, user_groups=user_groups)

        # Add the group.
        success,message = db_execute(db_connection, table.insert().values({**values[0], **values[1]}))
        db_connection.close()
        if success:
            return list(request, selector=values[0]['group_name'], response_code=0, message='group "%s" successfully added.' % (values[0]['group_name']), active_user=active_user, user_groups=user_groups, attributes=values[2])
        else:
            return list(request, selector=values[0]['group_name'], response_code=1, message='group add "%s" failed - %s.' % (values[0]['group_name'], message), active_user=active_user, user_groups=user_groups, attributes=values[2])

    ### Bad request.
    else:
        return list(request, response_code=1, message='group add, invalid method "%s" specified.' % request.method)

#-------------------------------------------------------------------------------

def delete(request):
    """
    This function should recieve a post request with a payload of group name
    to be deleted.
    """

    if not verifyUser(request):
        raise PermissionDenied

    if request.method == 'POST':
        # open the database.
        db_engine,db_session,db_connection,db_map = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(request, db_session, db_map)
        if rc != 0:
            db_connection.close()
            return list(request, selector='-', response_code=1, message=msg, active_user=active_user, user_groups=user_groups)

        # Map the field list for group/YAML files.
        response_code, table, values = map_parameter_to_field_values(request, db_engine, 'csv2_group_yaml', YAML_KEYS,  active_user)
        if response_code != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='group delete %s.' % values, active_user=active_user, user_groups=user_groups)

        # Delete any group/YAML files for the group.
        s = select([view_groups_with_yaml_names]).where((view_groups_with_yaml_names.c.group_name == values[0]['group_name']))
        group_list = qt(db_connection.execute(s))
        for row in group_list:
            if row['group_name'] == values[0]['group_name'] and row['yaml_names']:
                yaml_names = row['yaml_names'].split(',')
                for yaml_name in yaml_names:
                    # Delete the groupYAML file.
                    success,message = db_execute(
                        db_connection,
                        table.delete((table.c.group_name==values[0]['group_name']) & (table.c.yaml_name==yaml_name))
                        )

        # Map the field list for groups.
        response_code, table, values = map_parameter_to_field_values(request, db_engine, 'csv2_groups', GROUP_KEYS,  active_user)
        if response_code != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='group delete %s' % values, active_user=active_user, user_groups=user_groups)

        # Delete the group.
        success,message = db_execute(
            db_connection,
            table.delete(table.c.group_name==values[0]['group_name'])
            )
        db_connection.close()
        if success:
            return list(request, selector=values[0]['group_name'], response_code=0, message='group "%s" successfully deleted.' % (values[0]['group_name']), active_user=active_user, user_groups=user_groups, attributes=values[2])
        else:
            return list(request, selector=values[0]['group_name'], response_code=1, message='group delete "%s" failed - %s.' % (values[0]['group_name'], message), active_user=active_user, user_groups=user_groups, attributes=values[2])

    ### Bad request.
    else:
        return list(request, response_code=1, message='group delete, invalid method "%s" specified.' % request.method)

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

    if request.method == 'POST':
        # open the database.
        db_engine,db_session,db_connection,db_map = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(request, db_session, db_map)
        if rc != 0:
            db_connection.close()
            return list(request, selector='-', response_code=1, message=msg, active_user=active_user, user_groups=user_groups)

        # Map the field list.
        response_code, table, values = map_parameter_to_field_values(request, db_engine, 'csv2_groups', GROUP_KEYS,  active_user)
        if response_code != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='group update %s' % values, active_user=active_user, user_groups=user_groups)

        # Update the group.
        success, message = db_execute(db_connection, table.update().where(table.c.group_name==values[0]['group_name']).values(values[1]))
        db_connection.close()
        if success:
            return list(request, selector=values[0]['group_name'], response_code=0, message='group "%s" successfully updated.' % (values[0]['group_name']), active_user=active_user, user_groups=user_groups, attributes=values[2])
        else:
            return list(request, selector=values[0]['group_name'], response_code=1, message='group update "%s" failed - %s.' % (values[0]['group_name'], message), active_user=active_user, user_groups=user_groups, attributes=values[2])

    ### Bad request.
    else:
        return list(request, response_code=1, message='group update, invalid method "%s" specified.' % request.method)

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
            return list(request, selector='-', response_code=1, message=msg, active_user=active_user, user_groups=user_groups)

        # Map the field list.
        response_code, table, values = map_parameter_to_field_values(request, db_engine, 'csv2_group_yaml', YAML_KEYS,  active_user)
        if response_code != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='group yaml-add %s' % values, active_user=active_user, user_groups=user_groups)

        # Add the group yaml file.
        success,message = db_execute(db_connection, table.insert().values({**values[0], **values[1]}))
        db_connection.close()
        if success:
            return list(request, selector=active_user.active_group, response_code=0, message='group YAML file "%s.%s" successfully added.' % (active_user.active_group, values[0]['yaml_name']), active_user=active_user, user_groups=user_groups, attributes=values[2])
        else:
            return list(request, selector=active_user.active_group, response_code=1, message='group yaml-add "%s.%s" failed - %s.' % (active_user.active_group, values[0]['yaml_name'], message), active_user=active_user, user_groups=user_groups, attributes=values[2])

    ### Bad request.
    else:
        if request.method != 'POST':
            return list(request, response_code=1, message='group yaml_add, invalid method "%s" specified.' % request.method)
        else:
            return list(request, response_code=1, message='group yaml_add, no group name specified.')

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
            return list(request, selector='-', response_code=1, message=msg, active_user=active_user, user_groups=user_groups)

        # Map the field list.
        response_code, table, values = map_parameter_to_field_values(request, db_engine, 'csv2_group_yaml', YAML_KEYS,  active_user)
        if response_code != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='group yaml-delete %s' % values, active_user=active_user, user_groups=user_groups)

        # Delete the group yaml file.
        success,message = db_execute(
            db_connection,
            table.delete( \
                (table.c.group_name==active_user.active_group) & \
                (table.c.yaml_name==values[0]['yaml_name']) \
                )
            )
        db_connection.close()
        if success:
            return list(request, selector=active_user.active_group, response_code=0, message='group YAML file "%s.%s" successfully deleted.' % (active_user.active_group, values[0]['yaml_name']), active_user=active_user, user_groups=user_groups, attributes=values[2])
        else:
            return list(request, selector=active_user.active_group, response_code=1, message='group yaml-delete "%s.%s" failed - %s.' % (active_user.active_group, values[0]['yaml_name'], message), active_user=active_user, user_groups=user_groups, attributes=values[2])

    ### Bad request.
    else:
        if request.method != 'POST':
            return list(request, response_code=1, message='group yaml_delete, invalid method "%s" specified.' % request.method)
        else:
            return list(request, response_code=1, message='group yaml_delete, no group name specified.')

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
        return list(request, selector='-', response_code=1, message=msg, active_user=active_user, user_groups=user_groups)

    # Retrieve YAML file.
    obj_act_id = request.path.split('/') # /cloud/yaml_fetch/<group>.<yaml>
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
            return list(request, selector='-', response_code=1, message=msg, active_user=active_user, user_groups=user_groups)

        # Map the field list.
        response_code, table, values = map_parameter_to_field_values(request, db_engine, 'csv2_group_yaml', YAML_KEYS,  active_user)
        if response_code != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='group yaml-update %s' % values, active_user=active_user, user_groups=user_groups)

        # Update the group yaml file.
        success,message = db_execute(db_connection, table.update().where( \
            (table.c.group_name==active_user.active_group) & \
            (table.c.yaml_name==values[0]['yaml_name']) \
            ).values(values[1]))
        db_connection.close()
        if success:
            return list(request, selector=active_user.active_group, response_code=0, message='group YAML file "%s.%s" successfully  updated.' % (active_user.active_group, values[0]['yaml_name']), active_user=active_user, user_groups=user_groups, attributes=values[2])
        else:
            return list(request, selector=active_user.active_group, response_code=1, message='group yaml-update "%s.%s" failed - %s.' % (active_user.active_group, values[0]['yaml_name'], message), active_user=active_user, user_groups=user_groups, attributes=values[2])

    ### Bad request.
    else:
        if request.method != 'POST':
            return list(request, response_code=1, message='group yaml_update, invalid method "%s" specified.' % request.method)
        else:
            return list(request, response_code=1, message='group yaml_update, no group name specified.')

