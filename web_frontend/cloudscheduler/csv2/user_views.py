from django.conf import settings
config = settings.CSV2_CONFIG

from django.core.exceptions import PermissionDenied
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

from cloudscheduler.lib.view_utils import \
    lno, \
    manage_user_groups, \
    manage_user_group_verification, \
    qt, \
    render, \
    set_user_groups, \
    table_fields, \
    validate_fields, \
    check_convert_bytestrings
import cloudscheduler.lib.schema as schema_na
from collections import defaultdict
import bcrypt

from cloudscheduler.lib.schema import *
import datetime

from cloudscheduler.lib.web_profiler import silk_profile as silkp

# lno: UV - error code identifier.
MODID = 'UV'

#-------------------------------------------------------------------------------

USER_GROUP_KEYS = {
    # Named argument formats (anything else is a string).
    'format': {
        'username':            'lowerdash',
        'is_superuser':        'dboolean',
        'password':            'password',
        'password1':           'password1',
        'password2':           'password2',

        'csrfmiddlewaretoken': 'ignore',
        'group':               'ignore',
        'group_name':          'ignore',
        'group_option':        ['add', 'delete'],

        'active_group':        'reject',
        'join_date':           'reject',
        },
    'mandatory': [
        'username',
        ],
    'not_empty': [
        'username',
        'group_name',
        ],
    'array_fields': [
        'group_name',
        ],
    }

UNPRIVILEGED_USER_KEYS = {
    'auto_active_user': True,
    'unnamed_fields_are_bad': True,
    # Named argument formats (anything else is a string).
    'format': {
        'default_group':                'lowerdash',
        'password':                     'password',
        'password1':                    'password1',
        'password2':                    'password2',
        'status_refresh_interval':      'integer',
        'flag_global_status':           'dboolean',
        'flag_jobs_by_target_alias':    'dboolean',
        'flag_show_foreign_global_vms': 'dboolean',
        'flag_show_slot_detail':        'dboolean',
        'flag_show_slot_flavors':       'dboolean',
        'csrfmiddlewaretoken':          'ignore',
        'group':                        'ignore',

        'username':                     'reject',
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

def _verify_username_cert_cn(fields, check_username=False):
    """
    Check username and cert_cn against those already defined; can't allow duplicates.
    """

    config.db_open()

    rc, msg, csv2_user_list = config.db_query("csv2_user")

    for registered_user in csv2_user_list:
        if check_username:
            # Check #1 Check that the username is valid (ie no username or cert_cn by that name)
            if fields['username'] == registered_user["username"] or fields['username'] == registered_user["cert_cn"]:
                return 1, 'username "%s" unavailable.' % fields['username']

        # Check #2 Check that the cert_cn is not equal to any username or other cert_cn
        if ('cert_cn' in fields and fields['cert_cn'] != '') and (fields['username'] != registered_user['username']) and (fields['cert_cn'] == registered_user["username"] or fields['cert_cn'] == registered_user["cert_cn"]):
            return 1, 'common name "%s" conflicts with registered user "%s".' % (fields['cert_cn'], registered_user["username"])

    return 0, None

#-------------------------------------------------------------------------------

@silkp(name="User Add")
def add(request):
    """
    Add a new user.
    """

    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request)
    if rc != 0:
        config.db_close()
        return user_list(request, active_user=active_user, response_code=1, message='%s %s' % (lno(MODID), msg))

    if request.method == 'POST':
        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(config, request, [USER_GROUP_KEYS], ['csv2_user', 'csv2_groups,n', 'csv2_user_groups,n'], active_user)
        if rc != 0:
            config.db_close()
            return user_list(request, active_user=active_user, response_code=1, message='%s user add, %s' % (lno(MODID), msg))

        # Need to perform several checks (Note: password checks are now done in validate_fields).
        rc, msg = _verify_username_cert_cn(fields, check_username=True)
        if rc != 0:
            config.db_close()
            return user_list(request, active_user=active_user, response_code=1, message='%s user add, "%s"' % (lno(MODID), msg))

        # Validity check the specified groups.
        if 'group_name' in fields:
            rc, msg = manage_user_group_verification(config, tables, None, fields['group_name']) 
            if rc != 0:
                config.db_close()
                return user_list(request, active_user=active_user, response_code=1, message='%s user add, "%s" failed - %s.' % (lno(MODID), fields['username'], msg))

        fields['join_date'] = datetime.datetime.today().strftime('%Y-%m-%d')
        
        # Add the user.
        table = 'csv2_user'
        user_updates = table_fields(fields, table, columns, 'insert')
        user_updates = check_convert_bytestrings(user_updates)
        rc, msg = config.db_insert(table, user_updates)
        if rc != 0:
            config.db_close()
            return user_list(request, active_user=active_user, response_code=1, message='%s user add, "%s" failed - %s.' % (lno(MODID), fields['username'], msg))

        # Add user_groups.
        if 'group_name' in fields:
            rc, msg = manage_user_groups(config, tables, fields['username'], fields['group_name'])

        if rc == 0:
            config.db_close(commit=True)
            return user_list(request, active_user=active_user, response_code=0, message='user "%s" successfully added.' % (fields['username']))
        else:
            config.db_close()
            return user_list(request, active_user=active_user, response_code=1, message='%s user group-add "%s.%s" failed - %s.' % (lno(MODID), fields['username'], fields['group_name'], msg))
                    
    ### Bad request.
    else:
        config.db_close()
        return user_list(request, active_user=active_user, response_code=1, message='%s user add, invalid method "%s" specified.' % (lno(MODID), request.method))

#-------------------------------------------------------------------------------

@silkp(name="User Delete")
def delete(request):
    """
    Delete a user.
    """

    # open the database.
    config.db_open()


    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request)
    if rc != 0:
        config.db_close()
        return user_list(request, active_user=active_user, response_code=1, message='%s %s' % (lno(MODID), msg))

    if request.method == 'POST':
        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(config, request, [USER_GROUP_KEYS, {'accept_primary_keys_only': True}], ['csv2_user', 'csv2_user_groups,n'], active_user)
        if rc != 0:
            config.db_close()
            return user_list(request, active_user=active_user, response_code=1, message='%s user delete, %s' % (lno(MODID), msg))

        # Check if user exists
        table = 'csv2_user'
        where_clause = "username='%s'" % fields['username']
        rc, msg, found_user_list = config.db_query(table, where=where_clause)
        if not found_user_list or len(found_user_list) == 0: 
            config.db_close()
            return user_list(request, active_user=active_user, response_code=1, message='%s user group-delete "%s" failed - the request did not match any rows.' % (lno(MODID), fields['username']))

        # Delete any user_groups for the user.
        table = 'csv2_user_groups'
        rc, msg = config.db_delete(table, where=where_clause)
        if rc != 0:
            config.db_close()
            return user_list(request, active_user=active_user, response_code=1, message='%s user group-delete "%s" failed - %s.' % (lno(MODID), fields['username'], msg))

        # Delete the user.
        table = 'csv2_user'
        rc, msg = config.db_delete(table, where=where_clause)
        if rc == 0:
            config.db_close(commit=True)
            return user_list(request, active_user=active_user, response_code=0, message='user "%s" successfully deleted.' % (fields['username']))
        else:
            config.db_close()
            return user_list(request, active_user=active_user, response_code=1, message='%s user delete, "%s" failed - %s.' % (lno(MODID), fields['username'], msg))

    ### Bad request.
    else:
      # return user_list(request, active_user=active_user, response_code=1, message='%s user delete did not contain mandatory parameter "username".' % lno(MODID))
        config.db_close()
        return user_list(request, active_user=active_user, response_code=1, message='%s user delete add, invalid method "%s" specified.' % (lno(MODID), request.method))

#-------------------------------------------------------------------------------

@silkp(name="User List")
def user_list(request, active_user=None, response_code=0, message=None):
    """
    List users.
    """

    user_list_path = '/user/list/'

    if request.path!=user_list_path and request.META['HTTP_ACCEPT'] == 'application/json':
        return render(request, 'csv2/users.html', {'response_code': response_code, 'message': message, 'active_user': active_user.username, 'active_group': active_user.active_group, 'user_groups': active_user.user_groups})


    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request)
    if rc != 0:
        config.db_close()
        return render(request, 'csv2/users.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})

    # Validate input fields  when request path is /user/list/.
    rc, msg, fields, tables, columns = validate_fields(config, request, [LIST_KEYS], [], active_user)
    if rc != 0 and request.path==user_list_path:
        config.db_close()
        return render(request, 'csv2/users.html', {'response_code': 1, 'message': '%s user list, %s' % (lno(MODID), msg)})

    # Retrieve the user list but loose the passwords.
    rc, msg, user_list_raw = config.db_query("view_user_groups")
    _user_list = qt(user_list_raw, prune=['password'])

    # Retrieve user/groups list (dictionary containing list for each user).
    rc, msg, groups_per_user_raw = config.db_query("csv2_user_groups")
    ignore1, ignore2, groups_per_user = qt(
        groups_per_user_raw,
        keys = {
            'primary': [
                'username',
                ],
            'secondary': [
                'group_name',
                ],
            'match_list': _user_list,
            }
        )

    # Retrieve  available groups list (dictionary containing list for each user).
    rc, msg, available_groups_per_user_raw = config.db_query("view_user_groups_available")
    ignore1, ignore2, available_groups_per_user = qt(
        available_groups_per_user_raw,
        keys = {
            'primary': [
                'username',
                ],
            'secondary': [
                'group_name',
                'available',
                ],
            'match_list': _user_list,
            }
        )

    rc, msg, group_list = config.db_query("csv2_groups")

    # Position the page.
#   obj_act_id = request.path.split('/')
#   if user:
#       if user == '-':
#           current_user = ''
#       else:
#           current_user = user
#   elif len(obj_act_id) > 2 and len(obj_act_id[3]) > 0:
#       current_user = str(obj_act_id[3])
#   else:
    if len(_user_list) > 0:
        current_user = str(_user_list[0]['username'])
    else:
        current_user = ''

    if message:
        if response_code == 0:
            messages.success(request, message)
        else:
            messages.error(request, message)

    # Render the page.
    context = {
            'active_user': active_user.username,
            'active_group': active_user.active_group,
            'user_groups': active_user.user_groups,
            'user_list': _user_list,
            'group_list': group_list,
            'groups_per_user': groups_per_user,
            'available_groups_per_user': available_groups_per_user,
            'current_user': current_user,
            'response_code': response_code,
            'message': message,
            'is_superuser': active_user.is_superuser,
            'version': config.get_version()
        }

    config.db_close()
    return render(request, 'csv2/users.html', context)

#-------------------------------------------------------------------------------

@silkp(name="User Settings")
def settings(request, active_user=None, response_code=0, message=None):
    """
    Unprivileged update user (password change).
    """

    # open the database.
    config.db_open()
    
    # Retrieve the active user, associated group list and optionally set the active group.
    if active_user is None:
        rc, msg, active_user = set_user_groups(config, request, super_user=False)
        if rc != 0:
            config.db_close()
            return render(request, 'csv2/user_settings.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})

    if rc == 0:
        if request.method == 'POST':
            # Validate input fields.
            rc, msg, fields, tables, columns = validate_fields(config, request, [UNPRIVILEGED_USER_KEYS], ['csv2_user', 'django_session,n'], active_user)
            if rc == 0:        
                # Validity check the specified groups.
                if 'default_group' in fields and fields['default_group'] not in active_user.user_groups:
                    rc = 1; msg = '%s my settings unable to update default - user is not a member of the specified group (%s).' % (lno(MODID), fields['default_group'])

                if rc == 0:
                    # Update the user.
                    table = 'csv2_user'
                    where_clause =  "username='%s'" % active_user.username
                    user_updates = table_fields(fields, table, columns, 'update')
                    user_updates = check_convert_bytestrings(user_updates)
                    rc, qmsg = config.db_update(table, user_updates, where=where_clause)
                    if rc == 0:
                        config.db_commit()
                        request.session.delete()
                        update_session_auth_hash(request, active_user)
                        msg = 'user "%s" successfully updated.' % (fields['username']).username
                    else:
                        msg = '%s user update, "%s" failed - %s.' % (lno(MODID), active_user, message)
            else:
                msg ='%s user update, %s' % (lno(MODID), msg)
    else:
        msg ='%s %s' % (lno(MODID), msg)

    pre_rc = rc
    # Retrieve user settings.
    where_clause =  "username='%s'" % active_user.username
    rc, qmsg, _user_list_raw = config.db_query("csv2_user", where=where_clause)
    _user_list = qt(_user_list_raw, prune='password')

    # Close the database.
    config.db_close()
    final_rc = rc if pre_rc == 0 else pre_rc
    
    if msg:
        if final_rc == 0:
            messages.success(request, msg)
        else:
            messages.error(request, msg)

    # Render the page.
    context = {
            'active_user': active_user.username,
            'active_group': active_user.active_group,
            'user_groups': active_user.user_groups,
            'user_list': _user_list,
            'response_code': final_rc,
            'message': msg,
            'is_superuser': active_user.is_superuser,
            'version': config.get_version()
        }

    return render(request, 'csv2/user_settings.html', context)

#-------------------------------------------------------------------------------

@silkp(name="User Update")
def update(request):
    """
    Update a user.
    """

    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request)
    if rc != 0:
        config.db_close()
        return user_list(request, active_user=active_user, response_code=1, message='%s %s' % (lno(MODID), msg))

    if request.method == 'POST':
        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(config, request, [USER_GROUP_KEYS], ['csv2_user', 'csv2_groups,n', 'csv2_user_groups'], active_user)
        if rc != 0:
            config.db_close()
            return user_list(request, active_user=active_user, response_code=1, message='%s user update, %s' % (lno(MODID), msg))

        # Need to perform several checks (Note: password checks are now done in validate_fields).
        rc, msg = _verify_username_cert_cn(fields)
        if rc != 0:
            return user_list(request, active_user=active_user, response_code=1, message='%s user update, "%s"' % (lno(MODID), msg))

        # Validity check the specified groups.
        if 'group_name' in fields:
            rc, msg = manage_user_group_verification(config, tables, None, fields['group_name']) 
            if rc != 0:
                config.db_close()
                return user_list(request, active_user=active_user, response_code=1, message='%s user update, "%s" failed - %s.' % (lno(MODID), fields['username'], msg))

        # Update the user.
        table = 'csv2_user'
        user_updates = table_fields(fields, table, columns, 'update')
        user_updates = check_convert_bytestrings(user_updates)
        
        # Check if has any property to update other than username
        update_flag = True
        if len(user_updates) == 1:
            key = list(user_updates.keys())[0]
            if key in schema_na.schema[table]['keys']:
                update_flag = False

        if len(user_updates) > 0 and update_flag:
            where_clause = "username='%s'" % fields['username']
            
            # Check if user exists
            rc, msg, found_user_list = config.db_query(table, where=where_clause)
            if not found_user_list or len(found_user_list) == 0: 
                config.db_close()
                return user_list(request, active_user=active_user, response_code=1, message='%s user update failed - the request did not match any rows.' % lno(MODID))
           
            rc, msg = config.db_update(table, user_updates, where=where_clause)
            if rc != 0:
                config.db_close()
                return user_list(request, active_user=active_user, response_code=1, message='%s user update, "%s" failed - %s.' % (lno(MODID), fields['username'], msg))
        else:
            if 'group_name' not in fields and request.META['HTTP_ACCEPT'] == 'application/json':
                config.db_close()
                return user_list(request, active_user=active_user, response_code=1, message='%s user update must specify at least one field to update.' % lno(MODID))
            

        # Update user_groups.
        if request.META['HTTP_ACCEPT'] == 'application/json':
            if 'group_name' in fields:
                if 'group_option' in fields and fields['group_option'] == 'delete':
                    rc, msg = manage_user_groups(config, tables, fields['username'], groups=fields['group_name'], option='delete')
                else:
                    rc, msg = manage_user_groups(config, tables, fields['username'], groups=fields['group_name'], option='add')

        else:
            if 'group_name' in fields:
                rc, msg = manage_user_groups(config, tables, fields['username'], groups=fields['group_name'])
            else:
                rc, msg = manage_user_groups(config, tables, fields['username'], None)

        if rc == 0:
            config.db_close(commit=True)
            return user_list(request, active_user=active_user, response_code=0, message='user "%s" successfully updated.' % (fields['username']))
        else:
            config.db_close()
            return user_list(request, active_user=active_user, response_code=1, message='%s user group update "%s.%s" failed - %s.' % (lno(MODID), fields['username'], fields['group_name'], msg))

    ### Bad request.
    else:
        return user_list(request, active_user=active_user, response_code=1, message='%s user update, invalid method "%s" specified.' % (lno(MODID), request.method))

