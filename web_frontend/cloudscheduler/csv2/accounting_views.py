from django.conf import settings
config = settings.CSV2_CONFIG

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import requires_csrf_token
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied


from cloudscheduler.lib.view_utils_na import \
    lno, \
    qt, \
    qt_filter_get, \
    render, \
    set_user_groups, \
    validate_fields
from collections import defaultdict
import bcrypt
import time

from sqlalchemy import exists
from sqlalchemy.sql import select
from sqlalchemy.sql import and_
from cloudscheduler.lib.schema import *
from cloudscheduler.lib.log_tools import get_frame_info
import sqlalchemy.exc

from cloudscheduler.lib.web_profiler import silk_profile as silkp

# lno: $$ - error code identifier.
MODID = '$$'

#-------------------------------------------------------------------------------

KEYS = {
    # Named argument formats (anything else is a string).
    'format': {
        'last_update':         'integer',
        'csrfmiddlewaretoken': 'ignore',
        'group':               'ignore',
        },
    }

KEYS_SU = {
    # Named argument formats (anything else is a string).
    'format': {
        'all':                 'dboolean',
        'last_update':         'integer',
        'csrfmiddlewaretoken': 'ignore',
        'group':               'ignore',
        },
    }

#-------------------------------------------------------------------------------

@silkp(name="VM List")
@requires_csrf_token
def apel(request, args=None, response_code=0, message=None):

    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        return render(request, 'csv2/vms.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})

    # Validate input fields.
    if args==None:
        args=active_user.kwargs
        if active_user.is_superuser:
            rc, msg, fields, tables, columns = validate_fields(config, request, [KEYS_SU], [], active_user)
        else:
            rc, msg, fields, tables, columns = validate_fields(config, request, [KEYS], [], active_user)
        if rc != 0:
            config.db_close()
            return render(request, 'csv2/vms.html', {'response_code': 1, 'message': '%s vm list, %s' % (lno(MODID), msg)})

    # Retrieve VM information.
    table = view_apel_accounting
    if 'last_update' in fields:
        s = select([table]).where(table.c.last_update>fields['last_update'])
    else:
        s = select([table])

    if 'all' in fields and fields['all'] == True:
        apel_accounting = qt(config.db_connection.execute(s))
    else:
        if active_user.flag_global_status:
            apel_accounting = qt(config.db_connection.execute(s), filter=qt_filter_get(['group_name'], {'group_name': active_user.user_groups}))
        else:
            apel_accounting = qt(config.db_connection.execute(s), filter=qt_filter_get(['group_name'], {'group_name': active_user.active_group}))

    config.db_close()

    # Render the page.
    context = {
            'active_user': active_user.username,
            'active_group': active_user.active_group,
            'user_groups': active_user.user_groups,
            'apel_accounting': apel_accounting,
            'response_code': response_code,
            'message': message,
            'is_superuser': active_user.is_superuser,
            'version': config.get_version()
        }

    return render(request, 'csv2/vms.html', context)

