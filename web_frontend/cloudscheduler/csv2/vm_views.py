from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import requires_csrf_token
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from django.contrib.auth.models import User #to get auth_user table
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
    qt, \
    qt_filter_get, \
    render, \
    set_user_groups, \
    table_fields, \
    validate_fields, \
    verifyUser
from collections import defaultdict
import bcrypt

from sqlalchemy import exists
from sqlalchemy.sql import select
from sqlalchemy.sql import and_
from lib.schema import *
import sqlalchemy.exc

# lno: VV - error code identifier.

#-------------------------------------------------------------------------------
ALIASES = {'poller_status': {'native': ['manual', 'error', 'unregistered', 'retiring', 'running', 'other']}}

VM_KEYS = {
    'auto_active_group': True,
    # Named argument formats (anything else is a string).
    'format': {
        'poller_status':                                                ['native', 'manual', 'error', 'unregistered', 'retiring', 'running', 'other'],
        'vm_option':                                                    ['kill', 'retire', 'manctl', 'sysctl'],

        'cloud_name':                                                   'ignore',
        'csrfmiddlewaretoken':                                          'ignore',
        'group':                                                        'ignore',
        'hostname':                                                     'ignore',
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
        'vm_option',
        ]
    }

#-------------------------------------------------------------------------------

@requires_csrf_token
def list(
    request,
    selector='::::',
    response_code=0,
    message=None,
    active_user=None,
    user_groups=None,
    ):

    if not verifyUser(request):
        raise PermissionDenied

    # open the database.
    db_engine, db_session, db_connection, db_map = db_ctl = db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    if not active_user:
        rc, msg, active_user, user_groups = set_user_groups(request, db_ctl)
        if rc != 0:
            db_close(db_ctl)
            return render(request, 'csv2/clouds.html', {'response_code': 1, 'message': msg})

    # Validate input fields (should be none).
    if not message:
        rc, msg, fields, tables, columns = validate_fields(request, [LIST_KEYS], db_ctl, [], active_user)
        if rc != 0:
            db_close(db_ctl)
            return render(request, 'csv2/vms.html', {'response_code': 1, 'message': '%s vm list, %s' % (lno('VV00'), msg)})

    # Retrieve VM information.
    s = select([view_vms]).where(view_vms.c.group_name == active_user.active_group)
    vm_list = qt(db_connection.execute(s), filter=qt_filter_get(['cloud_name', 'poller_status', 'hostname'], selector.split('::'), aliases=ALIASES), convert={'status_changed_time': 'datetime', 'last_updated': 'datetime'})

    # Retrieve available Clouds.
    s = select([view_cloud_status]).where(view_cloud_status.c.group_name == active_user.active_group)
    cloud_list = qt(db_connection.execute(s))

    db_close(db_ctl)

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

@requires_csrf_token
def update(request):
    """
    Update VMs.
    """

    if not verifyUser(request):
        raise PermissionDenied

    if request.method == 'POST':
        # open the database.
        db_engine, db_session, db_connection, db_map = db_ctl = db_open()

        # Retrieve the active user, associated group list and optionally set the active group.
        rc, msg, active_user, user_groups = set_user_groups(request, db_ctl)
        if rc != 0:
            db_close(db_ctl)
            return list(request, response_code=1, message='%s %s' % (lno('VV01'), msg), active_user=active_user, user_groups=user_groups)

        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(request, [VM_KEYS, MANDATORY_KEYS], db_ctl, ['csv2_vms,n', 'condor_machines,n'], active_user)
        if rc != 0:
            db_close(db_ctl)
            return list(request, response_code=1, message='%s vm update %s' % (lno('VV02'), msg), active_user=active_user, user_groups=user_groups)

        if fields['vm_option'] == 'kill':
            table = tables['csv2_vms']
            verb = 'killed'
        elif fields['vm_option'] == 'retire':
            table = tables['condor_machines']
            verb = 'retired'
        elif fields['vm_option'] == 'manctl':
            table = tables['csv2_vms']
            verb = 'set to manual control'
        elif fields['vm_option'] == 'sysctl':
            table = tables['csv2_vms']
            verb = 'set to system control'
        else:
            return list(request, response_code=1, message='%s vm update, option "%s" is invalid.' % (lno('VV03'), fields['vm_option']))

        # Retrieve VM information.
        s = select([view_vms]).where((view_vms.c.group_name == active_user.active_group) and (view_vms.c.foreign_vm == 0))
        vm_list = qt(db_connection.execute(s), filter=qt_filter_get(['cloud_name', 'hostname', 'poller_status'], fields, aliases=ALIASES))

        count = 0
        for vm in vm_list:
            if fields['vm_option'] == 'kill':
                update = table.update().where(table.c.vmid == vm['vmid']).values({'terminate': 1})
            elif fields['vm_option'] == 'retire':
                update = table.update().where(table.c.hostname == vm['hostname']).values({'condor_off': 1})
            elif fields['vm_option'] == 'manctl':
                update = table.update().where(table.c.vmid == vm['vmid']).values({'manual_control': 1})
            elif fields['vm_option'] == 'sysctl':
                update = table.update().where(table.c.vmid == vm['vmid']).values({'manual_control': 0})

            # rc, msg = db_execute(db_ctl, table.update().where(table.c.vmid == vm['vmid']).values(control), allow_no_rows=True)
            rc, msg = db_execute(db_ctl, update, allow_no_rows=True)
            if rc == 0:
                count += msg
            else:
                db_close(db_ctl)
                return list(request, response_code=1, message='%s vm update (%s) failed - %s' % (lno('VV04'), fields['vm_option'], msg))

        db_close(db_ctl, commit=True)
        return list(request, response_code=0, message='vm update, VMs %s=%s.' % (verb, count))

    ### Bad request.
    else:
        return list(request, response_code=1, message='%s vm update, invalid method "%s" specified.' % (lno('VV05'), request.method))
