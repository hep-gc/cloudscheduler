from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import requires_csrf_token
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from django.contrib.auth.models import User #to get auth_user table
from .models import user as csv2_user

from cloudscheduler.lib.csv2_config import Config
web_config = Config('web_frontend')

from .view_utils import \
    get_db_connection, \
    get_db_session, \
    db_rollback, \
    db_execute, \
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
from cloudscheduler.lib.schema import *
import sqlalchemy.exc

from silk.profiling.profiler import silk_profile as silkp

# lno: SV - error code identifier.

#-------------------------------------------------------------------------------

CONFIG_KEYS = {
    'auto_active_group': True,
    # Named argument formats (anything else is a string).
    'format': {
        'category':                     ('csv2_configuration', 'category'),
        'delete_cycle_interval':        'integer',
        'enable_glint':                 ['True', 'False'],
        'log_level':                    'integer',
        'no_limit_default':             'integer',
        'sleep_interval_cleanup':       'integer',
        'sleep_interval_command':       'integer',
        'sleep_interval_flavor':        'integer',
        'sleep_interval_image':         'integer',
        'sleep_interval_job':           'integer',
        'sleep_interval_keypair':       'integer',
        'sleep_interval_limit':         'integer',
        'sleep_interval_machine':       'integer',
        'sleep_interval_main_long':     'integer',
        'sleep_interval_main_short':    'integer',
        'sleep_interval_network':       'integer',
        'sleep_interval_vm':            'integer',

        'config_key':                   'reject',
        'type':                         'reject',
        'value':                        'reject',

        'cacerts':                      'ignore',
        'csrfmiddlewaretoken':          'ignore',
        'default_job_group':            'ignore',
        'group':                        'ignore',
        'log_file':                     'ignore',
    },
    'mandatory': [
        'category',
    ],
}

#-------------------------------------------------------------------------------

@silkp(name="Server Config")
def config(request):
    """
    Update and list server configurations
    """
    
    if not verifyUser(request):
        raise PermissionDenied
    if not getSuperUserStatus(request):
        raise PermissionDenied

    # open the database.
    db_session = get_db_session()
    db_connection = get_db_connection()

    message = None
    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user, user_groups = set_user_groups(request)
    if rc == 0:
        if (request.method == 'POST') and ((not 'group' in request.POST) or len(request.POST) > 2):
                # Validate input fields.
                rc, msg, fields, tables, columns = validate_fields(request, [CONFIG_KEYS], ['csv2_configuration,n'], active_user)
                if rc == 0:
                    # Update the server configuration.
                    table = tables['csv2_configuration']
                    category = fields['category']
                    
                    # Remove unwanted fields
                    fields.pop('category')
                    fields.pop('csrfmiddlewaretoken')
                    fields.pop('group_name')

                    if len(fields) == 0:
                        message = '{} server config must specify at least one field to update.'.format(lno('SV00'))
                    else:
                        for field in fields:
                            rc, msg = db_execute(table.update().where((table.c.category==category) & (table.c.config_key==field)).values({table.c.value:fields[field]}))
                            if rc != 0:
                                message = '{} server config update failed - {}'.format(lno('SV01'), msg)
                                break
                        if rc == 0:
                            db_session.commit()
                            message = 'server config successfully updated'
                else:
                    message = '{} server config update {}'.format(lno('SV02'), msg)
    else:
        message='{} {}'.format(lno('SV03'), msg)

    if message and message[:2] == 'SV':
        config_list = []
        response_code = 1
    else:
        db_rollback()
        db_connection = get_db_connection()
        s = select([csv2_configuration])
        config_list = qt(db_connection.execute(s))
        response_code = 0

    db_rollback()

    # Render the page.
    context = {
            'active_user': active_user,
            'active_group': active_user.active_group,
            'user_groups': user_groups,
            'config_list': config_list,
            'response_code': response_code,
            'message': message,
            'enable_glint': web_config.enable_glint
        }

    return render(request, 'csv2/server_config.html', context)

