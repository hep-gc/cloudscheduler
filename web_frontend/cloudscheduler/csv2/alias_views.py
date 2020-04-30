from django.conf import settings
config = settings.CSV2_CONFIG

from django.core.exceptions import PermissionDenied
from django.contrib.auth import update_session_auth_hash

from cloudscheduler.lib.view_utils import \
    diff_lists, \
    lno, \
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
import datetime

from cloudscheduler.lib.web_profiler import silk_profile as silkp

# lno: AV - error code identifier.
MODID = 'AV'

#-------------------------------------------------------------------------------

CLOUD_ALIAS_KEYS = {
    # Named argument formats (anything else is a string).
    'auto_active_group': True,
    'format': {
        'alias_name':          'lower',
        'cloud_name':          'lower',
        'cloud_option':        ['add', 'delete'],
        'csrfmiddlewaretoken': 'ignore',
        'group':               'ignore',
    },
    'mandatory': [
        'alias_name',
    ],
    'array_fields': [
        'cloud_name',
    ]
}

MANDATORY_CLOUD_NAME = {
    'mandatory': [
        'cloud_name',
    ]
}

ALLOW_EMPTY_CLOUD_NAME = {
    'allow_empty': [
        'cloud_name',
    ]
}

LIST_KEYS = {
    # Named argument formats (anything else is a string).
    'format': {
        'csrfmiddlewaretoken': 'ignore',
        'group':               'ignore',
    }
}

#-------------------------------------------------------------------------------

def manage_cloud_aliases(config, tables, group_name, alias_name, clouds, option=None, new_alias=True):
    """
    Ensure all the specified clouds and only the specified clouds are
    members of the specified cloud alias. The specified cloud alias and clouds
    have all been pre-verified.
    """

    from sqlalchemy.sql import select

    table = tables['csv2_cloud_aliases']

    # if there is only one cloud, make it a list anyway
    if clouds:
        if isinstance(clouds, str):
            cloud_list = clouds.split(',')
        else:
            cloud_list = clouds
    else:
        cloud_list = []

    # Retrieve the list of clouds the cloud alias already has.
    db_clouds = []
    
    s = select([table]).where((table.c.group_name==group_name) & (table.c.alias_name==alias_name))
    alias_list_ = qt(config.db_connection.execute(s))

    for row in alias_list_:
        db_clouds.append(row['cloud_name'])

    if new_alias:
       if len(db_clouds) > 0:
          return 1, 'specified alias already exists.'
    else:
       if len(db_clouds) < 1:
          return 1, 'specified alias does not exist.'

    if not option or option == 'add':
        # Get the list of clouds specified that the alias doesn't already have.
        add_clouds = diff_lists(cloud_list, db_clouds)

        # Add the missing clouds.
        for cloud_name in add_clouds:
            rc, msg = config.db_session_execute(table.insert().values(group_name=group_name, alias_name=alias_name, cloud_name=cloud_name))
            if rc != 0:
                return 1, msg

    if not option:
        # Get the list of clouds that the alias currently has but were not specified.
        remove_clouds = diff_lists(db_clouds, cloud_list)
        
        # Remove the extraneous clouds.
        for cloud_name in remove_clouds:
            rc, msg = config.db_session_execute(table.delete((table.c.group_name==group_name) & (table.c.alias_name==alias_name) & (table.c.cloud_name==cloud_name)))
            if rc != 0:
                return 1, msg

    elif option == 'delete':
        # Get the list of clouds that the cloud alias currently has and were specified.
        remove_clouds = diff_lists(cloud_list, db_clouds, option='and')
        
        # Remove the extraneous clouds.
        for cloud_name in remove_clouds:
            rc, msg = config.db_session_execute(table.delete((table.c.group_name==group_name) & (table.c.alias_name==alias_name) & (table.c.cloud_name==cloud_name)))
            if rc != 0:
                return 1, msg

    return 0, None

#-------------------------------------------------------------------------------

@silkp(name="Alias Add")
def add(request):
    """
    Add a new cloud alias.
    """

    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        return alias_list(request, active_user=active_user, response_code=1, message='%s %s' % (lno(MODID), msg))

    if request.method == 'POST':
        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(config, request, [CLOUD_ALIAS_KEYS, MANDATORY_CLOUD_NAME], ['csv2_cloud_aliases', 'csv2_clouds,n'], active_user)
        if rc != 0:
            config.db_close()
            return alias_list(request, active_user=active_user, response_code=1, message='%s cloud alias add, %s' % (lno(MODID), msg))

        # Verify specified clouds exist.
        if 'cloud_name' in fields and fields['cloud_name']:
            rc, msg = validate_by_filtered_table_entries(config, fields['cloud_name'], 'cloud_name', 'csv2_clouds', 'cloud_name', [['group_name', active_user.active_group]], allow_value_list=True)
            if rc != 0:
                config.db_close()
                return alias_list(request, active_user=active_user, response_code=1, message='%s cloud alias add, "%s" failed - %s.' % (lno(MODID), fields['alias_name'], msg))

        # Add the cloud alias.
        rc, msg = manage_cloud_aliases(config, tables, active_user.active_group, fields['alias_name'], fields['cloud_name'])
        if rc == 0:
            config.db_close(commit=True)
            return alias_list(request, active_user=active_user, response_code=0, message='cloud alias "%s.%s" successfully added.' % (active_user.active_group, fields['alias_name']))
        else:
            config.db_close()
            return alias_list(request, active_user=active_user, response_code=1, message='%s cloud alias add "%s.%s" failed - %s.' % (lno(MODID), active_user.active_group, fields['alias_name'], msg))
                    
    ### Bad request.
    else:
        return alias_list(request, active_user=active_user, response_code=1, message='%s cloud alias add, invalid method "%s" specified.' % (lno(MODID), request.method))

#-------------------------------------------------------------------------------

@silkp(name="Alias List")
def alias_list(request, active_user=None, response_code=0, message=None):
    """
    List cloud aliases.
    """

    alias_list_path = '/alias/list/'

    if request.path!=alias_list_path and request.META['HTTP_ACCEPT'] == 'application/json':
        return render(request, 'csv2/clouds.html', {'response_code': response_code, 'message': message, 'active_user': active_user.username, 'active_group': active_user.active_group, 'user_groups': active_user.user_groups})

    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    if active_user is None:
        rc, msg, active_user = set_user_groups(config, request, super_user=False)
        if rc != 0:
            config.db_close()
            return render(request, 'csv2/cloud_aliases.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})

    # Validate input fields (should be none).
    rc, msg, fields, tables, columns = validate_fields(config, request, [LIST_KEYS], [], active_user)
    if rc != 0 and request.path==alias_list_path:
        config.db_close()
        return render(request, 'csv2/cloud_aliases.html', {'response_code': 1, 'message': '%s cloud alias list, %s' % (lno(MODID), msg)})

    # Retrieve the cloud alias view.
    s = select([view_cloud_aliases]).where(view_cloud_aliases.c.group_name == active_user.active_group)
    alias_list_ = qt(config.db_connection.execute(s))

    # Retrieve the cloud alias table.
    s = select([csv2_cloud_aliases]).where(csv2_cloud_aliases.c.group_name == active_user.active_group)
    cloud_alias_list = qt(config.db_connection.execute(s))

    # Retrieve the cloud table.
    s = select([csv2_clouds]).where(csv2_clouds.c.group_name == active_user.active_group)
    cloud_list = qt(config.db_connection.execute(s))

    # Render the page.
    context = {
            'active_user': active_user.username,
            'active_group': active_user.active_group,
            'user_groups': active_user.user_groups,
            'alias_list': alias_list_,
            'cloud_alias_list': cloud_alias_list,
            'cloud_list': cloud_list,
            'response_code': response_code,
            'message': message,
            'is_superuser': active_user.is_superuser,
            'version': config.get_version()
        }

    config.db_close()
    return render(request, 'csv2/cloud_aliases.html', context)

#-------------------------------------------------------------------------------

@silkp(name="Alias Update")
def update(request):
    """
    Update a cloud alias.
    """

    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        return alias_list(request, active_user=active_user, response_code=1, message='%s %s' % (lno(MODID), msg))

    if request.method == 'POST':
        keys = [CLOUD_ALIAS_KEYS]
        if request.META['HTTP_ACCEPT'] == 'application/json':
            keys.append(MANDATORY_CLOUD_NAME)
        elif not any(parameter.startswith('cloud_name') for parameter in request.POST):
            # Create a copy so that it is mutable.
            request.POST = request.POST.copy()
            request.POST['cloud_name'] = ''
            keys.append(ALLOW_EMPTY_CLOUD_NAME)
        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(config, request, keys, ['csv2_cloud_aliases', 'csv2_clouds,n'], active_user)

        if rc != 0:
            config.db_close()
            return alias_list(request, active_user=active_user, response_code=1, message='%s cloud alias update, %s' % (lno(MODID), msg))

        # Verify specified clouds exist.
        if fields.get('cloud_name'):
            rc, msg = validate_by_filtered_table_entries(config, fields['cloud_name'], 'cloud_name', 'csv2_clouds', 'cloud_name', [['group_name', active_user.active_group]], allow_value_list=True)
            if rc != 0:
                config.db_close()
                return alias_list(request, active_user=active_user, response_code=1, message='%s cloud alias update, "%s" failed - %s.' % (lno(MODID), fields['alias_name'], msg))

        # Update the cloud alias.
        if request.META['HTTP_ACCEPT'] == 'application/json':
            # option defaults to 'add'.
            rc, msg = manage_cloud_aliases(config, tables, active_user.active_group, fields['alias_name'], fields['cloud_name'], option=fields.get('cloud_option', 'add'), new_alias=False)
        else:
            rc, msg = manage_cloud_aliases(config, tables, active_user.active_group, fields['alias_name'], fields['cloud_name'], new_alias=False)

        if rc == 0:
            config.db_close(commit=True)
            return alias_list(request, active_user=active_user, response_code=0, message='cloud alias "%s.%s" successfully updated.' % (active_user.active_group, fields['alias_name']))
        else:
            config.db_close()
            return alias_list(request, active_user=active_user, response_code=1, message='%s cloud alias group update "%s.%s" failed - %s.' % (lno(MODID), fields['group_name'], fields['alias_name'], msg))

    ### Bad request.
    else:
        return alias_list(request, active_user=active_user, response_code=1, message='%s cloud alias update, invalid method "%s" specified.' % (lno(MODID), request.method))

