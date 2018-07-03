from django.core.exceptions import PermissionDenied
from django.contrib.auth import update_session_auth_hash
from .models import user as csv2_user
from . import config

from .view_utils import \
    db_close, \
    db_execute, \
    db_open, \
    getAuthUser, \
    getcsv2User, \
    getSuperUserStatus, \
    lno, \
    manage_user_groups, \
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
import datetime

# lno: UV - error code identifier.

#-------------------------------------------------------------------------------

USER_GROUP_KEYS = {
    # Named argument formats (anything else is a string).
    'format': {
        'username':            'lowercase',
        'is_superuser':        'dboolean',
        'password':            'password',
        'password1':           'password1',
        'password2':           'password2',

        'csrfmiddlewaretoken': 'ignore',
        'group':               'ignore',
        'group_name':          'ignore',
        'group_option':         ['add', 'delete'],

        'active_group':        'reject',
        'join_date':           'reject',
        },
    }

UNPRIVILEGED_USER_KEYS = {
    'auto_active_user': True,
    'unnamed_fields_are_bad': True,
    # Named argument formats (anything else is a string).
    'format': {
        'password':            'password',
        'password1':           'password1',
        'password2':           'password2',

        'csrfmiddlewaretoken': 'ignore',
        'group':               'ignore',
        },
    }

LIST_KEYS = {
    # Named argument formats (anything else is a string).
    'format': {
        'csrfmiddlewaretoken': 'ignore',
        'group':               'ignore',
        },
    }

#-------------------------------------------------------------------------------

def _verify_username_cert_cn(db_ctl, fields, check_username=False):
    """
    Check username and cert_cn against those already defined; can't allow duplicates.
    """

    db_engine, db_session, db_connection, db_map = db_ctl

    s = select([csv2_user])
    csv2_user_list = qt(db_connection.execute(s))

    for registered_user in csv2_user_list:
        if check_username:
            # Check #1 Check that the username is valid (ie no username or cert_cn by that name)
            if fields['username'] == registered_user["username"] or fields['username'] == registered_user["cert_cn"]:
                return 1, 'username "%s" unavailable.' % fields['username']

        # Check #2 Check that the cert_cn is not equal to any username or other cert_cn
        if 'cert_cn' in fields and fields['cert_cn'] != '' and (fields['cert_cn'] == registered_user["username"] or fields['cert_cn'] == registered_user["cert_cn"]):
            return 1, 'common name "%s" conflicts with registered user "%s".' % (fields['cert_cn'], registered_user["username"])

    return 0, None

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
        db_engine, db_session, db_connection, db_map = db_ctl = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(request, db_ctl)
        if rc != 0:
            db_close(db_ctl)
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('UV00'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [USER_GROUP_KEYS], db_ctl, ['csv2_user', 'csv2_groups,n', 'csv2_user_groups,n'], active_user)
        if rc != 0:        
            db_close(db_ctl)
            return list(request, selector='-', response_code=1, message='%s user add, %s' % (lno('UV01'), msg), active_user=active_user, user_groups=user_groups)

        # Need to perform several checks (Note: password checks are now done in validate_fields).
        rc, msg = _verify_username_cert_cn(db_ctl, fields, check_username=True)
        if rc != 0:
            return list(request, selector=fields['username'], response_code=1, message='%s user add, "%s"' % (lno('UV02'), msg), active_user=active_user, user_groups=user_groups)

        # Validity check the specified groups.
        if 'group_name' in fields:
            rc, msg = manage_user_group_verification(db_ctl, tables, None, fields['group_name']) 
            if rc != 0:
                db_close(db_ctl)
                return list(request, selector=fields['username'], response_code=1, message='%s user add, "%s" failed - %s.' % (lno('UV04'), fields['username'], msg), active_user=active_user, user_groups=user_groups)

        fields['join_date'] = datetime.datetime.today().strftime('%Y-%m-%d')
        
        # Add the user.
        table = tables['csv2_user']
        rc, msg = db_execute(db_ctl, table.insert().values(table_fields(fields, table, columns, 'insert')))
        if rc != 0:
            db_close(db_ctl)
            return list(request, selector=fields['username'], response_code=1, message='%s user add, "%s" failed - %s.' % (lno('UV05'), fields['username'], msg), active_user=active_user, user_groups=user_groups)

        # Add user_groups.
        if 'group_name' in fields:
            rc, msg = manage_user_groups(db_ctl, tables, fields['username'], fields['group_name'])

        db_connection.close()
        if rc == 0:
            db_close(db_ctl, commit=True)
            return list(request, selector=fields['username'], response_code=0, message='user "%s" successfully added.' % (fields['username']), active_user=active_user, user_groups=user_groups)
        else:
            db_close(db_ctl)
            return list(request, selector=fields['username'], response_code=1, message='%s user group-add "%s.%s" failed - %s.' % (lno('UV06'), fields['username'], fields['group_name'], msg), active_user=active_user, user_groups=user_groups)
                    
    ### Bad request.
    else:
        return list(request, response_code=1, message='%s user add, invalid method "%s" specified.' % (lno('UV07'), request.method))

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
        db_engine, db_session, db_connection, db_map = db_ctl = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(request, db_ctl)
        if rc != 0:
            db_close(db_ctl)
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('UV08'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [USER_GROUP_KEYS, {'accept_primary_keys_only': True}], db_ctl, ['csv2_user', 'csv2_user_groups,n'], active_user)
        if rc != 0:        
            db_close(db_ctl)
            return list(request, selector='-', response_code=1, message='%s user delete, %s' % (lno('UV09'), msg), active_user=active_user, user_groups=user_groups)

        # Delete any user_groups for the user.
        table = tables['csv2_user_groups']
        rc, msg = db_execute(db_ctl, table.delete(table.c.username==fields['username']), allow_no_rows=True)
        if rc != 0:
            db_close(db_ctl)
            return list(request, selector=fields['username'], response_code=1, message='%s user group-delete "%s" failed - %s.' % (lno('UV10'), fields['username'], msg), active_user=active_user, user_groups=user_groups)

        # Delete the user.
        table = tables['csv2_user']
        rc, msg = db_execute(db_ctl, table.delete(table.c.username==fields['username']))
        if rc == 0:
            db_close(db_ctl, commit=True)
            return list(request, selector=fields['username'], response_code=0, message='user "%s" successfully deleted.' % (fields['username']), active_user=active_user, user_groups=user_groups)
        else:
            db_close(db_ctl)
            return list(request, selector=fields['username'], response_code=1, message='%s user delete, "%s" failed - %s.' % (lno('UV11'), fields['username'], msg), active_user=active_user, user_groups=user_groups)

    ### Bad request.
    else:
        return list(request, response_code=1, message='%s user delete, invalid method "%s" specified.' % (lno('UV12'), request.method))

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
    db_engine, db_session, db_connection, db_map = db_ctl = db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    if not active_user:
        rc, msg, active_user, user_groups = set_user_groups(request, db_ctl)
        if rc != 0:
            db_close(db_ctl)
            return render(request, 'csv2/users.html', {'response_code': 1, 'message': '%s %s' % (lno('UV13'), msg)})

    # Validate input fields (should be none).
    if not message:
        rc, msg, fields, tables, columns = validate_fields(request, [LIST_KEYS], db_ctl, [], active_user)
        if rc != 0:        
            db_close(db_ctl)
            return render(request, 'csv2/users.html', {'response_code': 1, 'message': '%s user list, %s' % (lno('GV06'), msg)})

    # Retrieve the user list but loose the passwords.
    s = select([view_user_groups])
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


    db_close(db_ctl)

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

def settings(request):
    """
    Unprivileged update user (password change).
    """

    if not verifyUser(request):
        raise PermissionDenied

    # open the database.
    db_engine, db_session, db_connection, db_map = db_ctl = db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user, user_groups = set_user_groups(request, db_ctl)
    if rc == 0:
        if request.method == 'POST':
            # Validate input fields.
            rc, msg, fields, tables, columns = validate_fields(request, [UNPRIVILEGED_USER_KEYS], db_ctl, ['csv2_user', 'django_session,n'], active_user)
            if rc == 0:        
                # Update the user.
                table = tables['csv2_user']
                rc, msg = db_execute(db_ctl, table.update().where(table.c.username==fields['username']).values(table_fields(fields, table, columns, 'update')))
                if rc == 0:
                    db_session.commit()
                    request.session.delete()
                    update_session_auth_hash(request, getcsv2User(request))
                    message = 'user "%s" successfully updated.' % fields['username']
                else:
                    message = '%s user update, "%s" failed - %s.' % (lno('UV14'), fields['username'], message)

            else:
                message='%s user update, %s' % (lno('UV15'), msg)

        ### Bad request.
        else:
            message = '%s user update, invalid method "%s" specified.' % (lno('UV16'), request.method)

    else:
        message='%s %s' % (lno('UV17'), msg)

    db_close(db_ctl)

    if message[:2] != 'UV':
        response_code = 0
    else:
        response_code = 1

    # Render the page.
    context = {
            'active_user': active_user,
            'active_group': active_user.active_group,
            'user_groups': user_groups,
            'response_code': response_code,
            'message': message,
            'enable_glint': config.enable_glint
        }

    return render(request, 'csv2/user_settings.html', context)

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
        db_engine, db_session, db_connection, db_map = db_ctl = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(request, db_ctl)
        if rc != 0:
            db_close(db_ctl)
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('UV18'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [USER_GROUP_KEYS], db_ctl, ['csv2_user', 'csv2_groups,n', 'csv2_user_groups'], active_user)
        if rc != 0:        
            db_close(db_ctl)
            return list(request, selector='-', response_code=1, message='%s user update, %s' % (lno('UV19'), msg), active_user=active_user, user_groups=user_groups)

        # Need to perform several checks (Note: password checks are now done in validate_fields).
        rc, msg = _verify_username_cert_cn(db_ctl, fields)
        if rc != 0:
            return list(request, selector=fields['username'], response_code=1, message='%s user update, "%s"' % (lno('UV02'), msg), active_user=active_user, user_groups=user_groups)

        # Validity check the specified groups.
        if 'group_name' in fields:
            rc, msg = manage_user_group_verification(db_ctl, tables, None, fields['group_name']) 
            if rc != 0:
                db_close(db_ctl)
                return list(request, selector=fields['username'], response_code=1, message='%s user update, "%s" failed - %s.' % (lno('UV20'), fields['username'], msg), active_user=active_user, user_groups=user_groups)

        # Update the user.
        table = tables['csv2_user']
        user_updates = table_fields(fields, table, columns, 'update')
        if len(user_updates) > 0:
            rc, msg = db_execute(db_ctl, table.update().where(table.c.username==fields['username']).values(user_updates), allow_no_rows=False)
            if rc != 0:
                db_close(db_ctl)
                return list(request, selector=fields['username'], response_code=1, message='%s user update, "%s" failed - %s.' % (lno('UV21'), fields['username'], msg), active_user=active_user, user_groups=user_groups)

        # Update user_groups.
        if request.META['HTTP_ACCEPT'] == 'application/json':
            if 'group_name' in fields:
                if 'group_option' in fields and fields['group_option'] == 'delete':
                    rc, msg = manage_user_groups(db_ctl, tables, fields['username'], groups=fields['group_name'], option='delete')
                else:
                    rc, msg = manage_user_groups(db_ctl, tables, fields['username'], groups=fields['group_name'], option='add')
            else:
                if len(user_updates) < 1:
                    return list(request, selector=fields['username'], response_code=1, message='%s user update must specify at least one field to update.' % lno('UV21'), active_user=active_user, user_groups=user_groups)

        else:
            if 'group_name' in fields:
                rc, msg = manage_user_groups(db_ctl, tables, fields['username'], groups=fields['group_name'])
            else:
                rc, msg = manage_user_groups(db_ctl, tables, fields['username'], None)

        db_connection.close()
        if rc == 0:
            db_close(db_ctl, commit=True)
            return list(request, selector=fields['username'], response_code=0, message='user "%s" successfully updated.' % (fields['username']), active_user=active_user, user_groups=user_groups)
        else:
            db_close(db_ctl)
            return list(request, selector=fields['username'], response_code=1, message='%s user group update "%s.%s" failed - %s.' % (lno('UV22'), fields['username'], fields['group_name'], msg), active_user=active_user, user_groups=user_groups)

    ### Bad request.
    else:
        return list(request, response_code=1, message='%s user update, invalid method "%s" specified.' % (lno('UV23'), request.method))

