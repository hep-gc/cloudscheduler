from django.conf import settings
config = settings.CSV2_CONFIG

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import requires_csrf_token
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied


from .view_utils import \
    kill_retire, \
    lno, \
    qt, \
    qt_filter_get, \
    render, \
    set_user_groups, \
    table_fields, \
    validate_fields, \
    verifyUser
from collections import defaultdict
import bcrypt
import time

from sqlalchemy import exists
from sqlalchemy.sql import select
from sqlalchemy.sql import and_
from cloudscheduler.lib.schema import *
import sqlalchemy.exc

from cloudscheduler.lib.web_profiler import silk_profile as silkp

# lno: VV - error code identifier.

#-------------------------------------------------------------------------------
ALIASES = {'poller_status': {'native': ['manual', 'error', 'unregistered', 'retiring', 'running', 'other']}}

VM_KEYS = {
    'auto_active_group': True,
    # Named argument formats (anything else is a string).
    'format': {
        'poller_status':                                                ['native', 'idle', 'starting', 'manual', 'error', 'unregistered', 'retiring', 'running', 'other'],
        'vm_option':                                                    ['kill', 'retain', 'retire', 'manctl', 'sysctl'],

        'cloud_name':                                                   'ignore',
        'csrfmiddlewaretoken':                                          'ignore',
        'group':                                                        'ignore',
        'vm_hosts':                                                     'lowercase',
        },
    }

LIST_KEYS = {
    # Named argument formats (anything else is a string).
    'format': {
        'csrfmiddlewaretoken':                                          'ignore',
        'group':                                                        'ignore',
        },
    }

MANDATORY_KEYS = {
    'mandatory': [
        'vm_hosts',
        'vm_option',
        ]
    }

#-------------------------------------------------------------------------------

@silkp(name="VM List")
@requires_csrf_token
def list(
    request,
    selector='::::',
    response_code=0,
    message=None,
    active_user=None,
    user_groups=None,
    ):

    # open the database.
    config.db_open()

    if not verifyUser(request, config):
        raise PermissionDenied

    # Retrieve the active user, associated group list and optionally set the active group.
    if not active_user:
        rc, msg, active_user, user_groups = set_user_groups(config, request)
        if rc != 0:
            config.db_close()
            return render(request, 'csv2/clouds.html', {'response_code': 1, 'message': msg})

    # Validate input fields (should be none).
    if not message:
        rc, msg, fields, tables, columns = validate_fields(config, request, [LIST_KEYS], [], active_user)
        if rc != 0:
            config.db_close()
            return render(request, 'csv2/vms.html', {'response_code': 1, 'message': '%s vm list, %s' % (lno('VV00'), msg)})

    # Retrieve VM information.
    s = select([view_vms]).where(view_vms.c.group_name == active_user.active_group)
    vm_list = qt(config.db_connection.execute(s), filter=qt_filter_get(['cloud_name', 'poller_status', 'hostname'], selector.split('::'), aliases=ALIASES), convert={
        'start_time': 'datetime',
        'status_changed_time': 'datetime',
        'retire_time': 'datetime',
        'terminate_time': 'datetime',
        'last_updated': 'datetime'
        })

    # Retrieve available Clouds.
    s = select([view_cloud_status]).where(view_cloud_status.c.group_name == active_user.active_group)
    cloud_list = qt(config.db_connection.execute(s))

    config.db_close()

    # Render the page.
    context = {
            'active_user': active_user,
            'active_group': active_user.active_group,
            'user_groups': user_groups,
            'cloud_list': cloud_list,
            'vm_list': vm_list,
            'response_code': response_code,
            'message': message,
            'enable_glint': config.enable_glint
        }

    return render(request, 'csv2/vms.html', context)

#-------------------------------------------------------------------------------

@silkp(name="VM Update")
@requires_csrf_token
def update(request):
    """
    Update VMs.
    """

    # open the database.
    config.db_open()

    if not verifyUser(request, config):
        raise PermissionDenied

    if request.method == 'POST':
        

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(config, request)
        if rc != 0:
            config.db_close()
            return list(request, response_code=1, message='%s %s' % (lno('VV01'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(config, request, [VM_KEYS, MANDATORY_KEYS], ['csv2_vms,n', 'condor_machines,n'], active_user)
        if rc != 0:
            config.db_close()
            return list(request, response_code=1, message='%s vm update %s' % (lno('VV02'), msg), active_user=active_user, user_groups=user_groups)

        if fields['vm_option'] == 'kill':
            table = tables['csv2_vms']
            verb = 'killed'
        elif fields['vm_option'] == 'retire':
            table = tables['condor_machines']
            verb = 'retired'
        elif fields['vm_option'] == 'retain':
            if fields['vm_hosts'].isnumeric():
                verb = 'killed or retired'
            else:
                config.db_close()
                return list(request, response_code=1, message='%s vm update, the "--vm-hosts" parameter must be numeric when "--vm-option retain" is specified.' % lno('VV98'))
        elif fields['vm_option'] == 'manctl':
            table = tables['csv2_vms']
            verb = 'set to manual control'
        elif fields['vm_option'] == 'sysctl':
            table = tables['csv2_vms']
            verb = 'set to system control'
        else:
            return list(request, response_code=1, message='%s vm update, option "%s" is invalid.' % (lno('VV03'), fields['vm_option']))

        # Retrieve VM information.
        if fields['vm_hosts'].isnumeric():
            if 'cloud_name' in fields:
                count = kill_retire(config, active_user.active_group, fields['cloud_name'], fields['vm_option'], fields['vm_hosts'])
#               count = kill_retire(config, active_user.active_group, fields['cloud_name'], 'control', [50,1000000])
            else:
                count = kill_retire(config, active_user.active_group, '-', fields['vm_option'], fields['vm_hosts'])
        else:
            count = 0
            if fields['vm_hosts'] != '':
                if fields['vm_hosts'] == 'all':
                    s = select([view_vms]).where(view_vms.c.group_name == active_user.active_group)
                    vm_list = qt(config.db_connection.execute(s), filter=qt_filter_get(['cloud_name', 'poller_status'], fields, aliases=ALIASES))
                else:
                    fields['hostname'] = fields['vm_hosts']
                    s = select([view_vms]).where(view_vms.c.group_name == active_user.active_group)
                    vm_list = qt(config.db_connection.execute(s), filter=qt_filter_get(['cloud_name', 'hostname', 'poller_status'], fields, aliases=ALIASES))

                for vm in vm_list:
                    if fields['vm_option'] == 'kill':
                        update = table.update().where(table.c.vmid == vm['vmid']).values({'terminate': 1})
                    elif fields['vm_option'] == 'retire':
                        update = table.update().where(table.c.vmid == vm['vmid']).values({'retire': 1})
                    elif fields['vm_option'] == 'manctl':
                        update = table.update().where(table.c.vmid == vm['vmid']).values({'manual_control': 1})
                    elif fields['vm_option'] == 'sysctl':
                        update = table.update().where(table.c.vmid == vm['vmid']).values({'manual_control': 0})

                    rc, msg = config.db_session_execute(update, allow_no_rows=True)
                    if rc == 0:
                        count += msg
                    else:
                        config.db_close()
                        return list(request, response_code=1, message='%s vm update (%s) failed - %s' % (lno('VV04'), fields['vm_option'], msg))

        if count > 0:
            config.db_close(commit=True)
        else:
            config.db_close()

        return list(request, response_code=0, message='vm update, VMs %s: %s.' % (verb, count))

    ### Bad request.
    else:
        return list(request, response_code=1, message='%s vm update, invalid method "%s" specified.' % (lno('VV05'), request.method))
