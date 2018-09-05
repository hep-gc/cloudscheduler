from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import requires_csrf_token
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from django.contrib.auth.models import User #to get auth_user table
from .models import user as csv2_user

from cloudscheduler.lib.csv2_config import Config
web_config = Config('web_frontend')

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
from cloudscheduler.lib.schema import *
import sqlalchemy.exc

# lno: SV - error code identifier.

#-------------------------------------------------------------------------------

CONFIG_KEYS = {
    'auto_active_group': True,
    # Named argument formats (anything else is a string).
    'format': {
        'csrfmiddlewaretoken':  'ignore',
        'group':                'ignore',
        'category':             ('csv2_configuration', 'category'),
        'config_key':           ('csv2_configuration', 'config_key'),
    },
    'mandatory': [
        'value',
    ],
}

#-------------------------------------------------------------------------------

def config(request):
    """
    Update and list server configurations
    """
    
    if not verifyUser(request):
        raise PermissionDenied
    if not getSuperUserStatus(request):
        raise PermissionDenied

    # open the database.
    db_engine, db_session, db_connection, db_map = db_ctl = db_open()

    message = None
    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user, user_groups = set_user_groups(request, db_ctl)
    if rc == 0:
        if (request.method == 'POST') and ((not 'group' in request.POST) or len(request.POST) > 2):
                # Validate input fields.
                rc, msg, fields, tables, columns = validate_fields(request, [CONFIG_KEYS], db_ctl, ['csv2_configuration'], active_user)
                if rc == 0:
                    # Update the server configuration.
                    table = tables['csv2_configuration']
                    rc, msg = db_execute(db_ctl, table.update().where((table.c.category==request.POST['category']) & (table.c.config_key==request.POST['config_key'])).values(table_fields(fields, table, columns, 'update')))
                    if rc == 0:
                        db_session.commit()
                        message = 'server config successfully updated'
                    else:
                        message = '{} server config update failed - {}'.format(lno('SV00'), msg)
                else:
                    message = '{} server config update {}'.format(lno('SV01'), msg)
    else:
        message='{} {}'.format(lno('SV02'), msg)

    if message and message[:2] == 'SV':
        config_list = []
        response_code = 1
    else:
        s = select([csv2_configuration])
        config_list = qt(db_connection.execute(s))
        response_code = 0

    db_close(db_ctl)

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

