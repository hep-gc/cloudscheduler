#from django.shortcuts import render, get_object_or_404, redirect
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from django.contrib.auth.models import User #to get auth_user table
from .models import user as csv2_user
from . import config

from .view_utils import \
    db_execute, \
    db_open, \
    getAuthUser, \
    getcsv2User, \
    getSuperUserStatus, \
    lno, \
    manage_user_groups, \
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
import datetime

# lno: UV - error code identifier.

#-------------------------------------------------------------------------------

GROUP_KEYS = {
    # Named argument formats (anything else is a string).
    'format': {
        'group_name':          'lowercase',

        'csrfmiddlewaretoken': 'ignore',
        'username':            'ignore',
        },
    }

USER_KEYS = {
    # Named argument formats (anything else is a string).
    'format': {
        'username':            'lowercase',
        'group_name':          'ignore',
        'is_superuser':        'boolean',
        'password':            'password',
        'password.1':           'password1',
        'password.2':           'password2',

        'csrfmiddlewaretoken': 'ignore',
        'username':            'ignore',
        },
    }

USER_GROUP_KEYS = {
    # Named argument formats (anything else is a string).
    'format': {
        'group_name':          'lowercase',
        'password':            'password',
        'username':            'lowercase',

        'csrfmiddlewaretoken': 'ignore',
        },
    }

UNPRIVILEGED_USER_KEYS = {
    'unnamed_fields_are_bad': True,
    # Named argument formats (anything else is a string).
    'format': {
        'username':            'lowercase',
        'password':            'password',
        'password.1':           'password1',
        'password.2':           'password2',

        'csrfmiddlewaretoken': 'ignore',
        },
    }


#-------------------------------------------------------------------------------


def add(request):
    """
    Add a new user.
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
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('UV00', comment='user_add_set_user_groups_failed'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [USER_GROUP_KEYS], db_engine, ['csv2_user', 'csv2_groups,n', 'csv2_user_groups,n'], active_user)
        if rc != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='%s user add %s' % (lno('UV01', comment='user_add_validate_fields_failed'), msg), active_user=active_user, user_groups=user_groups)

        # Need to perform several checks (Note: password checks are now done in validate_fields).
        s = select([csv2_user])
        csv2_user_list = qt(db_connection.execute(s))

        for registered_user in csv2_user_list:
            # Check #1 Check that the username is valid (ie no username or cert_cn by that name)
            if fields['username'] == registered_user["username"] or fields['username'] == registered_user["cert_cn"]:
                return list(request, selector=fields['username'], response_code=1, message='%s username "%s" unavailable.' % (lno('UV02', comment='username_unavailable'), fields['username']), active_user=active_user, user_groups=user_groups)

            # Check #2 Check that the cert_cn is not equal to any username or other cert_cn
            if fields['cert_cn'] is not None and (fields['cert_cn'] == registered_user["username"] or fields['cert_cn'] == registered_user["cert_cn"]):
                return list(request, selector=fields['username'], response_code=1, message='%s username "%s" conflicts with a registered common name.' % (lno('UV03', comment='username_conflicts_with_common_name'), fields['username']), active_user=active_user, user_groups=user_groups)

        fields['join_date'] = datetime.datetime.today().strftime('%Y-%m-%d')
        
        # Add the user.
        table = tables['csv2_user']
        success, message = db_execute(db_connection, table.insert().values(table_fields(fields, table, columns, 'insert')))
        if not success:
            return list(request, selector=fields['username'], response_code=1, message='%s user add "%s" failed - %s.' % (lno('UV04', comment='user_add_table_insert_failed'), fields['username'], message), active_user=active_user, user_groups=user_groups)

        # Add user_groups.
        if 'group_name' in fields:
            rc, msg = manage_user_groups(db_connection, tables, users=fields['username'], groups=fields['group_name'])
        else:
            rc, msg = manage_user_groups(db_connection, tables, users=fields['username'], groups=[])

        db_connection.close()
        if rc == 0:
            return list(request, selector=fields['username'], response_code=0, message='user "%s" successfully added.' % (fields['username']), active_user=active_user, user_groups=user_groups)
        else:
            return list(request, selector=fields['username'], response_code=1, message='%s user group-add "%s.%s" failed - %s.' % (lno('UV05', comment='user_add_manage_user_group_lists_failed'), fields['username'], group_name, msg), active_user=active_user, user_groups=user_groups)
                    
    ### Bad request.
    else:
        return list(request, response_code=1, message='%s user add, invalid method "%s" specified.' % (lno('UV06', comment='user_add_not_a_POST'), request.method))

#-------------------------------------------------------------------------------

def delete(request):
    """
    Delete a user.
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
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('UV07', comment='user_delete_set_user_groups_failed'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [USER_GROUP_KEYS], db_engine, ['csv2_user', 'csv2_user_groups,n'], active_user)
        if rc != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='%s user delete %s' % (lno('UV08', comment='user_delete_validate_fields_failed'), msg), active_user=active_user, user_groups=user_groups)

        # Delete any user_groups for the user.
        table = tables['csv2_user_groups']
        success, message = db_execute(db_connection, table.delete(table.c.username==fields['username']))
        if not success:
            return list(request, selector=fields['username'], response_code=1, message='%s user group-delete "%s" failed - %s.' % (lno('UV09', comment='user_group_delete_table_delete_failed'), fields['username'], message), active_user=active_user, user_groups=user_groups)

        # Delete the user.
        table = tables['csv2_user']
        success, message = db_execute(db_connection, table.delete(table.c.username==fields['username']))
        db_connection.close()
        if success:
            return list(request, selector=fields['username'], response_code=0, message='user "%s" successfully deleted.' % (fields['username']), active_user=active_user, user_groups=user_groups)
        else:
            return list(request, selector=fields['username'], response_code=1, message='%s user delete "%s" failed - %s.' % (lno('UV10', comment='user_delete_table_delete_failed'), fields['username'], message), active_user=active_user, user_groups=user_groups)

    ### Bad request.
    else:
        return list(request, response_code=1, message='%s user delete, invalid method "%s" specified.' % (lno('UV11', comment='user_delete_not_a_POST'), request.method))

#-------------------------------------------------------------------------------

def group_add(request):
    """
    Add a group to a user.
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
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('UV12', comment='user_group_add_set_user_groups_failed'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [USER_GROUP_KEYS], db_engine, ['csv2_user,n', 'csv2_groups,n', 'csv2_user_groups'], active_user)
        if rc != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='%s user group-add %s' % (lno('UV13', comment='user_group_add_validate_fields_failed'), msg), active_user=active_user, user_groups=user_groups)

        # Verify that the user exists.
        table = tables['csv2_user']
        s = select([table]).where(table.c.username==fields['username'])
        csv2_user_list = db_connection.execute(s)
        found = False
        for registered_user in csv2_user_list:
            if registered_user['username'] == fields['username']:
                found = True

        if not found:
            return list(request, selector=fields['username'], response_code=1, message='%s user group-add specified an invalid username "%s".' % (lno('UV14', comment='user_group_add_invalid_username'), fields['username']), active_user=active_user, user_groups=user_groups)

        # Verify that the group exists.
        table = tables['csv2_groups']
        s = select([table]).where(table.c.group_name==fields['group_name'])
        csv2_groups_list = db_connection.execute(s)
        found = False
        for registered_group in csv2_groups_list:
            if registered_group['group_name'] == fields['group_name']:
                found = True

        if not found:
            return list(request, selector=fields['username'], response_code=1, message='%s user group-add specified an invalid group_name "%s".' % (lno('UV15', comment='user_group_add_invalid_group_name'), fields['group_name']), active_user=active_user, user_groups=user_groups)

        # Add the user_group.
        table = tables['csv2_user_groups']
        success, msg = db_execute(db_connection, table.insert().values(table_fields(fields, table, columns, 'insert')))
        db_connection.close()
        if rc == 0:
            return list(request, selector=fields['username'], response_code=0, message='user group "%s.%s" successfully added.' % (fields['username'], fields['group_name']), active_user=active_user, user_groups=user_groups)
        else:
            return list(request, selector=fields['username'], response_code=1, message='%s user group-add "%s.%s" failed - %s.' % (lno('UV16', comment='user_group_add_table_insert_failed'), fields['username'], fields['group_name'], msg), active_user=active_user, user_groups=user_groups)

    ### Bad request.
    else:
        return list(request, response_code=1, message='%s user add, invalid method "%s" specified.' % (lno('UV17', comment='user_group_add_not_a_POST'), request.method))

#-------------------------------------------------------------------------------

def group_delete(request):
    """
    Delete a group from a user.
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
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('UV18', comment='user_group_delete_set_user_groups_failed'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [USER_GROUP_KEYS], db_engine, ['csv2_user_groups'], active_user)
        if rc != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='%s user group-delete %s' % (lno('UV19', comment='user_group_delete_validate_fields_failed'), msg), active_user=active_user, user_groups=user_groups)

        # Delete the user/group.
        table = tables['csv2_user_groups']
        success, message = db_execute(db_connection, table.delete((table.c.username==fields['username']) & (table.c.group_name==fields['group_name'])))
        db_connection.close()
        if success:
            return list(request, selector=fields['username'], response_code=0, message='user/group "%s.%s" successfully deleted.' % (fields['username'], fields['group_name']), active_user=active_user, user_groups=user_groups)
        else:
            return list(request, selector=fields['username'], response_code=1, message='%s user/group delete "%s.%s" failed - %s.' % (lno('UV20', comment='user_group_delete_table_delete_failed'), fields['username'], fields['group_name'], message), active_user=active_user, user_groups=user_groups)

    ### Bad request.
    else:
        return list(request, response_code=1, message='%s user delete, invalid method "%s" specified.' % (lno('UV21', comment='user_group_delete_not_a_POST'), request.method))

#-------------------------------------------------------------------------------

def list(
    request, 
    selector=None,
    user=None, 
    username=None, 
    response_code=0, 
    message=None, 
    active_user=None, 
    user_groups=None,
    ):
    """
    List users.
    """


    if not verifyUser(request):
        raise PermissionDenied
    if not getSuperUserStatus(request):
        raise PermissionDenied

    # open the database.
    db_engine,db_session,db_connection,db_map = db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    if not active_user:
        response_code, message, active_user, user_groups = set_user_groups(request, db_session, db_map)
        if response_code != 0:
            db_connection.close()
            return render(request, 'csv2/users.html', {'response_code': 1, 'message': '%s %s' % (lno('UV07', comment='user_list_set_user_groups_failed'), message)})

    # Retrieve the user list but loose the passwords.
    s = select([view_user_groups_and_available_groups])
    user_list = qt(db_connection.execute(s), prune=['password'])

    # Retrieve user/groups list (dictionary containing list for each user).
    s = select([csv2_user_groups])
    ignore1, ignore2, groups_per_user = qt(
        db_connection.execute(s),
        keys = {
            'primary': [
                'username',
                ],
            'secondary': [
                'group_name',
                ],
            'match_list': user_list,
            }
        )

    # Retrieve  available groups list (dictionary containing list for each user).
    s = select([view_user_groups_available])
    ignore1, ignore2, available_groups_per_user = qt(
        db_connection.execute(s),
        keys = {
            'primary': [
                'username',
                ],
            'secondary': [
                'group_name',
                'available',
                ],
            'match_list': user_list,
            }
        )

    s = select([csv2_groups])
    group_list = qt(db_connection.execute(s))


    db_connection.close()

    # Position the page.
    obj_act_id = request.path.split('/')
    if user:
        if user == '-':
            current_user = ''
        else:
            current_user = user
    elif len(obj_act_id) > 2 and len(obj_act_id[3]) > 0:
        current_user = str(obj_act_id[3])
    else:
        if len(user_list) > 0:
            current_user = str(user_list[0]['username'])
        else:
            current_user = ''

    # Render the page.
    context = {
            'active_user': active_user,
            'active_group': active_user.active_group,
            'user_groups': user_groups,
            'user_list': user_list,
            'group_list': group_list,
            'groups_per_user': groups_per_user,
            'available_groups_per_user': available_groups_per_user,
            'current_user': current_user,
            'response_code': response_code,
            'message': message,
            'enable_glint': config.enable_glint
        }

    return render(request, 'csv2/users.html', context)

#-------------------------------------------------------------------------------

def update(request):
    """
    Update a user.
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
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('UV22', comment='user_update_set_user_groups_failed'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [USER_KEYS], db_engine, ['csv2_user', 'csv2_groups,n', 'csv2_user_groups'], active_user)
        if rc != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='%s user update %s' % (lno('UV23', comment='user_update_validate_fields_failed'), msg), active_user=active_user, user_groups=user_groups)

        # Update the user.
        table = tables['csv2_user']
        success, message = db_execute(db_connection, table.update().where(table.c.username==fields['username']).values(table_fields(fields, table, columns, 'update')))

        if not success:
            db_connection.close()
            return list(request, selector=fields['username'], response_code=1, message='%s user update "%s" failed - %s.' % (lno('UV24', comment='user_update_table_update_failed'), fields['username'], message), active_user=active_user, user_groups=user_groups)

        # Update user_groups.
        if 'group_name' in fields:
            rc, msg = manage_user_groups(db_connection, tables, users=fields['username'], groups=fields['group_name'])
        else:
            rc, msg = manage_user_groups(db_connection, tables, users=fields['username'], groups=[])

        db_connection.close()
        if rc == 0:
            return list(request, selector=fields['username'], response_code=0, message='user "%s" successfully updated.' % (fields['username']), active_user=active_user, user_groups=user_groups)
        else:
            return list(request, selector=fields['username'], response_code=1, message='%s user group update "%s.%s" failed - %s.' % (lno('UV25', comment='user_update_manage_user_group_lists_failed'), fields['username'], group_name, msg), active_user=active_user, user_groups=user_groups)
                    
    ### Bad request.
    else:
        return list(request, response_code=1, message='%s user update, invalid method "%s" specified.' % (lno('UV26', comment='user_update_not_a_POST'), request.method))



