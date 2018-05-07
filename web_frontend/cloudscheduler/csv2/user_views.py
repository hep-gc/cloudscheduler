#from django.shortcuts import render, get_object_or_404, redirect
from django.shortcuts import render, get_object_or_404, redirect
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
    lno, \
    map_parameter_to_field_values, \
    qt, \
    render, \
    set_user_groups, \
    verifyUser
from collections import defaultdict
import bcrypt

from sqlalchemy import exists
from sqlalchemy.sql import select
from lib.schema import *
import sqlalchemy.exc
import datetime

'''
USER RELATED WEB REQUEST VIEWS
'''

#-------------------------------------------------------------------------------

GROUP_KEYS = {
    # Should the active_group be automatically inserted into the primary keys.
    'auto_active_group': False,
    # The following fields are primary key fields for the table:
    'primary': (
        'group_name',
        ),
    # The following fields maybe in the input form but should be ignored.
    'ignore_bad': (    
        'csrfmiddlewaretoken',
        'username',
        ),
    }

USER_KEYS = {
    # Should the active_group be automatically inserted into the primary keys.
    'auto_active_group': False,
    # The following fields are primary key fields for the table:
    'primary': (
        'username',
        ),
    # The following fields maybe in the input form but should be ignored.
    'ignore_bad': (    
        'csrfmiddlewaretoken',
        'group_name',
        ),
    # Named argument formats (anything else is a string).
    'format': {
        'is_superuser': 'b',
        'password': 'p',
        'password1': 'p1',
        'password2': 'p2',
        },
    }

USER_GROUP_KEYS = {
    # Should the active_group be automatically inserted into the primary keys.
    'auto_active_group': False,
    # The following fields are primary key fields for the table:
    'primary': (
        'username',
        'group_name',
        ),
    # The following fields maybe in the input form but should be ignored.
    'ignore_bad': (    
        'csrfmiddlewaretoken',
        ),
    }

UNPRIVILEGED_USER_KEYS = {
    # Should the active_group be automatically inserted into the primary keys.
    'auto_active_group': False,
    # The following fields are primary key fields for the table:
    'primary': (
        'username',
        ),
    # Only select the following arguments for unprivileged users (others considered bad):
    'secondary_filter': (
        'password',
        'password1',
        'password2',
        ),
    # The following fields maybe in the input form but should be ignored.
    'ignore_bad': (    
        'csrfmiddlewaretoken',
        ),
    # Named argument formats (anything else is a string).
    'format': {
        'password': 'p',
        'password1': 'p1',
        'password2': 'p2',
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
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('UV00'), msg), active_user=active_user, user_groups=user_groups)

        # Map the field list.
        response_code, table, values = map_parameter_to_field_values(request, db_engine, 'csv2_user', USER_KEYS,  active_user)
        if response_code != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='%s user add %s' % (lno('UV01'), values), active_user=active_user, user_groups=user_groups)

        # Need to perform several checks
        # 1. Check that the username is valid (ie no username or cert_cn by that name)
        # 2. Check that the cert_cn is not equal to any username or other cert_cn
        # Note: password checks are now done in map_parameter_to_field_values.

        s = select([csv2_user])
        csv2_user_list = qt(db_connection.execute(s), prune=['password'])

        #csv2_user_list = csv2_user.objects.all()
        for registered_user in csv2_user_list:
            #check #1
            if values[0]['username'] == registered_user["username"] or values[0]['username'] == registered_user["cert_cn"]:
                return list(request, selector=values[0]['username'], response_code=1, message='%s username "%s" unavailable.' % (lno('UV02'), values[0]['username']), active_user=active_user, user_groups=user_groups)

            #check #2
            if values[1]['cert_cn'] is not None and (values[1]['cert_cn'] == registered_user["username"] or values[1]['cert_cn'] == registered_user["cert_cn"]):
                return list(request, selector=values[0]['username'], response_code=1, message='%s username "%s" conflicts with a registered common name.' % (lno('UV03'), values[0]['username']), active_user=active_user, user_groups=user_groups)

        values[1]['join_date'] = datetime.datetime.today().strftime('%Y-%m-%d')
        
        # Add the user.
        success, message = db_execute(db_connection, table.insert().values({**values[0], **values[1]}))
        db_connection.close()

        if success:
            return list(request, selector=values[0]['username'], response_code=0, message='user "%s" successfully added.' % (values[0]['username']), active_user=active_user, user_groups=user_groups)
        else:
            return list(request, selector=values[0]['username'], response_code=1, message='%s user add "%s" failed - %s.' % (lno('UV04'), values[0]['username'], message), active_user=active_user, user_groups=user_groups)

    ### Bad request.
    else:
        return list(request, response_code=1, message='%s user add, invalid method "%s" specified.' % (lno('UV05'), request.method))

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
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('UV06'), msg), active_user=active_user, user_groups=user_groups)

        # Map the field list for user/groups.
        response_code, table, values = map_parameter_to_field_values(request, db_engine, 'csv2_user_groups', USER_GROUP_KEYS,  active_user)
        if response_code != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='%s user delete %s.' % (lno('UV07'), values), active_user=active_user, user_groups=user_groups)

        # Delete any user/group for the user.
        s = select([csv2_user_groups]).where((csv2_user_groups.c.username == values[0]['username']))
        user_group_list = qt(db_connection.execute(s))
        for row in user_group_list:
            if row['username'] == values[0]['username']:
                # Delete the user/group.
                success, message = db_execute(
                    db_connection,
                    table.delete((table.c.username==values[0]['username']) & (table.c.group_name==group_name))
                    )

        # Map the field list for users.
        response_code, table, values = map_parameter_to_field_values(request, db_engine, 'csv2_user', USER_KEYS,  active_user)
        if response_code != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='%s user delete %s' % (lno('UV08'), values), active_user=active_user, user_groups=user_groups)

        # Delete the user.
        success, message = db_execute(
            db_connection,
            table.delete(table.c.username==values[0]['username'])
            )
        db_connection.close()
        if success:
            return list(request, selector=values[0]['username'], response_code=0, message='user "%s" successfully deleted.' % (values[0]['username']), active_user=active_user, user_groups=user_groups)
        else:
            return list(request, selector=values[0]['username'], response_code=1, message='%s user delete "%s" failed - %s.' % (lno('UV09'), values[0]['username'], message), active_user=active_user, user_groups=user_groups)

    ### Bad request.
    else:
        return list(request, response_code=1, message='%s user delete, invalid method "%s" specified.' % (lno('UV10'), request.method))

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
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('UV11'), msg), active_user=active_user, user_groups=user_groups)

        # Make sure the requested user exists.
        response_code, table, values = map_parameter_to_field_values(request, db_engine, 'csv2_user', USER_KEYS,  active_user)
        if response_code != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='%s user group-add %s' % (lno('UV12'), values), active_user=active_user, user_groups=user_groups)

        #temp fix
        save_value_user = values[0]['username']

        table = Table('csv2_user', metadata, autoload=True)
        found = False
        s = select([csv2_user]).where(table.c.username==values[0]['username'])
        csv2_user_list = db_connection.execute(s)
        for registered_user in csv2_user_list:
            if registered_user['username'] == values[0]['username']:
                found = True

        if not found:
            return list(request, selector=values[0]['username'], response_code=1, message='%s user group-add specified an invalid username "%s".' % (lno('UV13'), values[0]['username']), active_user=active_user, user_groups=user_groups)

        # Make sure the requested group exists.
        response_code, table, values = map_parameter_to_field_values(request, db_engine, 'csv2_groups', GROUP_KEYS,  active_user)
        if response_code != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='%s user group-add %s' % (lno('UV14'), values), active_user=active_user, user_groups=user_groups)

        table = Table('csv2_groups', metadata, autoload=True)
        found = False
        s = select([csv2_groups]).where(table.c.group_name==values[0]['group_name'])
        csv2_groups_list = db_connection.execute(s)
        for registered_group in csv2_groups_list:
            if registered_group['group_name'] == values[0]['group_name']:
                found = True

        if not found:
            return list(request, selector=save_value_user, response_code=1, message='%s user group-add specified an invalid group_name "%s".' % (lno('UV15'), values[0]['group_name']), active_user=active_user, user_groups=user_groups)

        # Add the user/group.
        response_code, table, values = map_parameter_to_field_values(request, db_engine, 'csv2_user_groups', USER_GROUP_KEYS,  active_user)
        if response_code != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='%s user group-add %s' % (lno('UV00'), values), active_user=active_user, user_groups=user_groups)

        table = Table('csv2_user_groups', metadata, autoload=True)
        success, message = db_execute(db_connection, table.insert().values({**values[0], **values[1]}))
        db_connection.close()

        if success:
            return list(request, selector=values[0]['username'], response_code=0, message='user/group "%s.%s" successfully added.' % (values[0]['username'], values[0]['group_name']), active_user=active_user, user_groups=user_groups)
        else:
            return list(request, selector=values[0]['username'], response_code=1, message='%s user/group add "%s.%s" failed - %s.' % (lno('UV00'), values[0]['username'], values[0]['group_name'], message), active_user=active_user, user_groups=user_groups)

    ### Bad request.
    else:
        return list(request, response_code=1, message='%s user add, invalid method "%s" specified.' % (lno('UV00'), request.method))

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
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('UV00'), msg), active_user=active_user, user_groups=user_groups)

        # Map the field list for user/groups.
        response_code, table, values = map_parameter_to_field_values(request, db_engine, 'csv2_user_groups', USER_GROUP_KEYS,  active_user)
        if response_code != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='%s user group-delete %s.' % (lno('UV00'), values), active_user=active_user, user_groups=user_groups)

        # Delete the user/group.
        success, message = db_execute(
            db_connection,
            table.delete((table.c.username==values[0]['username']) & (table.c.group_name==values[0]['group_name']))
            )
        db_connection.close()
        if success:
            return list(request, selector=values[0]['username'], response_code=0, message='user/group "%s.%s" successfully deleted.' % (values[0]['username'], values[0]['group_name']), active_user=active_user, user_groups=user_groups)
        else:
            return list(request, selector=values[0]['username'], response_code=1, message='%s user/group delete "%s.%s" failed - %s.' % (lno('UV00'), values[0]['username'], values[0]['group_name'], message), active_user=active_user, user_groups=user_groups)

    ### Bad request.
    else:
        return list(request, response_code=1, message='%s user delete, invalid method "%s" specified.' % (lno('UV00'), request.method))

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
            return render(request, 'csv2/users.html', {'response_code': 1, 'message': message})

    # Retrieve the user list but loose the passwords.
    s = select([view_user_groups_and_available_groups])
    user_list = qt(db_connection.execute(s), prune=['password'])

    # Retrieve user/groups list (dictionary containing list for each user).
    s = select([csv2_user_groups])
    ignore1, ignore2, user_groups = qt(
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
    ignore1, ignore2, available_groups = qt(
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
            'user_groups': user_groups,
            'available_groups': available_groups,
            'current_user': current_user,
            'response_code': response_code,
            'message': message
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
            return list(request, selector='-', response_code=1, message='%s %s' % (lno('UV00'), msg), active_user=active_user, user_groups=user_groups)

        # Map the field list.
        response_code, table, values = map_parameter_to_field_values(request, db_engine, 'csv2_user', USER_KEYS,  active_user)
        if response_code != 0:        
            db_connection.close()
            return list(request, selector='-', response_code=1, message='%s user update %s' % (lno('UV00'), values), active_user=active_user, user_groups=user_groups)

        # Update the user.
        success, message = db_execute(db_connection, table.update().where(table.c.username==values[0]['username']).values(values[1]))
        db_connection.close()

        if success:
            return list(request, selector=values[0]['username'], response_code=0, message='user "%s" successfully updated.' % (values[0]['username']), active_user=active_user, user_groups=user_groups)
        else:
            return list(request, selector=values[0]['username'], response_code=1, message='%s user update "%s" failed - %s.' % (lno('UV00'), values[0]['username'], message), active_user=active_user, user_groups=user_groups)

    ### Bad request.
    else:
        return list(request, response_code=1, message='%s user update, invalid method "%s" specified.' % (lno('UV00'), request.method))

#-------------------------------------------------------------------------------

def settings(request):
    print("+++ settings +++")
    if not verifyUser(request):
        raise PermissionDenied

    if request.method == 'POST':
        # proccess update

        csv2_user_list = csv2_user.objects.all()
        user_to_update = getcsv2User(request)
        new_username = request.POST.get('username')
        cert_cn = request.POST.get('common_name')
        new_pass1 = request.POST.get('password1')
        new_pass2 = request.POST.get('password2')
        
        # Need to perform three checks
        # 1. Check that the new username is valid (ie no username or cert_cn by that name)
        #   if the username hasn't changed we can skip this check since it would have been done on creation.
        # 2. Check that the cert_cn is not equal to any username or other cert_cn
        # 3. If the passwords aren't 0-3 chars and check if they are the same.
        for registered_user in csv2_user_list:
            #check #1
            if not new_username == user_to_update.username:
                if new_username == registered_user.username or new_username == registered_user.cert_cn:
                    context = {
                        'user_obj':user_to_update,
                        'response_code': 1,
                        'message': "Unable to update user: new username unavailable"
                    }
                    return render(request, 'csv2/user_settings.html', context)
            #check #2
            if cert_cn is not None and registered_user.username != user_to_update.username and (cert_cn == registered_user.username or cert_cn == registered_user.cert_cn):
                context = {
                    'user_obj':user_to_update,
                    'response_code': 1,
                    'message': "Unable to update user: Username or DN unavailable or conflicts with a registered Distinguished Name"
                }
                return render(request, 'csv2/user_settings.html', context)

        #check #3 part 1
        if new_pass1 is None or new_pass2 is None:
            context = {
                'user_obj':user_to_update,
                'response_code': 1,
                'message': "Password is empty"
            }
            return render(request, 'csv2/user_settings.html', context)
        #check #3 part 2
        if len(new_pass1)<4:
            context = {
                'user_obj':user_to_update,
                'response_code': 1,
                'message': "Password must be at least 4 characters"
            }
            return render(request, 'csv2/user_settings.html', context)
        #check #3 part 3
        if new_pass1 != new_pass2:
            context = {
                'user_obj':user_to_update,
                'response_code': 1,
                'message': "Passwords do not match"
            }
            return render(request, 'csv2/user_settings.html', context)

        #if we get here all the checks have passed and we can safely update the user data
        user_to_update.username=new_username
        if new_pass1:
            user_to_update.password = bcrypt.hashpw(new_pass1.encode(), bcrypt.gensalt(prefix=b"2a"))
        user_to_update.cert_cn=cert_cn
        user_to_update.save()
        context = {
                'user_obj':user_to_update,
                'response_code': 0,
                'message': "Update Successful"
            }
        return render(request, 'csv2/user_settings.html', context)

    else:
        #render user_settings template
        user_obj=getcsv2User(request)

        context = {
            'user_obj': user_obj,
            'response_code': 0,
            'message': None
        }
        return render(request, 'csv2/user_settings.html', context)

