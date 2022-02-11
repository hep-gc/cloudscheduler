from django.conf import settings
config = settings.CSV2_CONFIG

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import requires_csrf_token
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied


from cloudscheduler.lib.view_utils import \
    kill_retire, \
    lno, \
    qt, \
    qt_filter_get, \
    render, \
    set_user_groups, \
    table_fields, \
    get_target_cloud, \
    validate_fields
from collections import defaultdict
import bcrypt
import time

from cloudscheduler.lib.schema import *
from cloudscheduler.lib.log_tools import get_frame_info
from cloudscheduler.lib.signal_functions import event_signal_send
from cloudscheduler.lib.web_profiler import silk_profile as silkp

# lno: VV - error code identifier.
MODID = 'VV'

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
        'vm_hosts':                                                     'lowerdash',
        },
    'array_fields': [
        'vm_hosts',
        ],
    'not_empty': [
        'vm_hosts',
        ],
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

@silkp(name="Foreign List")
@requires_csrf_token
def foreign(request):

    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        return render(request, 'csv2/foreign.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})

    # Validate input fields (should be none).
    rc, msg, fields, tables, columns = validate_fields(config, request, [LIST_KEYS], [], active_user)
    if rc != 0:
        config.db_close()
        return render(request, 'csv2/foreign.html', {'response_code': 1, 'message': '%s vm list, %s' % (lno(MODID), msg)})

    global_view = active_user.kwargs['global_view']

    # Retrieve VM information
    if global_view=='0':
        # show foreign vms for a specific cloud
        where_clause = "group_name='%s'" % active_user.active_group
        rc, msg, foreign_list_raw = config.db_query("view_foreign_flavors", where=where_clause)
        foreign_list = qt(foreign_list_raw, filter=qt_filter_get(['cloud_name'], active_user.kwargs))

    elif global_view=='1':
        # show foreign vms for enabled clouds in all groups
        rc, msg, foreign_list_raw = config.db_query("view_foreign_flavors")
        rc, msg, enabled_cloud_list = config.db_query("view_cloud_status", select=['group_name', 'cloud_name'], where="enabled=1")
        foreign_list = list(filter(lambda x: {'group_name': x.get('group_name'), 'cloud_name': x.get('cloud_name')} in enabled_cloud_list, foreign_list_raw))

    else:
        # show foreign vms for enabled clouds in a specific group
        where_clause = "group_name='%s'" % active_user.active_group
        rc, msg, foreign_list_raw = config.db_query("view_foreign_flavors", where=where_clause)
        where_clause = "group_name='%s' and enabled=1" % active_user.active_group
        rc, msg, enabled_cloud_list = config.db_query("view_cloud_status", select=['cloud_name'], where=where_clause)
        foreign_list = list(filter(lambda x: {'cloud_name': x.get('cloud_name')} in enabled_cloud_list, foreign_list_raw))

    config.db_close()

    # Render the page.
    context = {
            'active_user': active_user.username,
            'active_group': active_user.active_group,
            'user_groups': active_user.user_groups,
            'foreign_list': foreign_list,
            'global_view' : global_view,
            'response_code': 0,
            'message': None,
            'is_superuser': active_user.is_superuser,
            'version': config.get_version()
        }

    return render(request, 'csv2/foreign.html', context)

#-------------------------------------------------------------------------------

@silkp(name="VM List")
@requires_csrf_token
def vm_list(request, args=None, response_code=0, message=None):

    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        return render(request, 'csv2/vms.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})

    # Validate input fields (should be none).
    
    if args==None:
        args=active_user.kwargs
        rc, msg, fields, tables, columns = validate_fields(config, request, [LIST_KEYS], [], active_user)
        if rc != 0:
            config.db_close()
            return render(request, 'csv2/vms.html', {'response_code': 1, 'message': '%s vm list, %s' % (lno(MODID), msg)})

    # Retrieve VM information.
    if active_user.active_group and active_user.active_group == 'ALL':
        rc, msg, vm_list_raw = config.db_query("view_vms")
    else:
        where_clause = "group_name='%s'" % active_user.active_group
        rc, msg, vm_list_raw = config.db_query("view_vms", where=where_clause)
    
    _vm_list = qt(vm_list_raw, filter=qt_filter_get(['cloud_name', 'poller_status', 'hostname'], args, aliases=ALIASES), convert={
        'htcondor_slots_timestamp': 'datetime',
        'htcondor_startd_time': 'datetime',
        'last_updated': 'datetime',
        'retire_time': 'datetime',
        'start_time': 'datetime',
        'status_changed_time': 'datetime',
        'terminate_time': 'datetime'
        })

    show_group = True
    show_cloud = True
    show_poller_status = True
    if active_user.active_group and active_user.active_group == 'ALL':
        show_group = False
    if args and ('cloud_name' not in args or args.get('cloud_name') == ''):
        show_cloud = False
    if args and ('poller_status' not in args or args.get('poller_status') == ''):
        show_poller_status = False


    config.db_close()

    # Render the page.
    context = {
            'active_user': active_user.username,
            'active_group': active_user.active_group,
            'user_groups': active_user.user_groups,
            'form_inputs': {'group': show_group, 'cloud': show_cloud, 'poller_status': show_poller_status},
            'vm_list': _vm_list,
            'response_code': response_code,
            'message': message,
            'is_superuser': active_user.is_superuser,
            'version': config.get_version()
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
    
    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        return render(request, 'csv2/vms.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg), 'active_user': active_user.username, 'active_group': active_user.active_group, 'user_groups': active_user.user_groups})
#       return vm_list(request, selector, response_code=1, message='%s %s' % (lno(MODID), msg), user_groups=user_groups)

    if request.method == 'POST':
        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(config, request, [VM_KEYS, MANDATORY_KEYS], ['csv2_vms,n', 'condor_machines,n'], active_user)
        if rc != 0:
            config.db_close()
            return render(request, 'csv2/vms.html', {'response_code': 1, 'message': '%s vm update %s' % (lno(MODID), msg), 'active_user': active_user.username, 'active_group': active_user.active_group, 'user_groups': active_user.user_groups})
#           return vm_list(request, selector, response_code=1, message='%s vm update %s' % (lno(MODID), msg), user_groups=user_groups)

        if fields['vm_option'] == 'kill':
            table = 'csv2_vms'
            verb = 'killed'
        elif fields['vm_option'] == 'retire':
            table = 'csv2_vms'
            verb = 'retired'
        elif fields['vm_option'] == 'retain':
            if fields['vm_hosts'].isnumeric():
                verb = 'killed or retired'
            else:
                config.db_close()
                return render(request, 'csv2/vms.html', {'response_code': 1, 'message': '%s vm update, the "--vm-hosts" parameter must be numeric when "--vm-option retain" is specified.' % lno(MODID), 'active_user': active_user.username, 'active_group': active_user.active_group, 'user_groups': active_user.user_groups})
#               return vm_list(request, selector, response_code=1, message='%s vm update, the "--vm-hosts" parameter must be numeric when "--vm-option retain" is specified.' % lno(MODID))
        elif fields['vm_option'] == 'manctl':
            table ='csv2_vms'
            verb = 'set to manual control'
        elif fields['vm_option'] == 'sysctl':
            table = 'csv2_vms'
            verb = 'set to system control'
        else:
            config.db_close()
            return render(request, 'csv2/vms.html', {'response_code': 1, 'message': '%s vm update, option "%s" is invalid.' % (lno(MODID), fields['vm_option']), 'active_user': active_user.username, 'active_group': active_user.active_group, 'user_groups': active_user.user_groups})

        
        # Retrieve VM information.
        if isinstance(fields['vm_hosts'], int):
            count = kill_retire(config, active_user.active_group, fields.get('cloud_name', default='-'), fields['vm_option'], fields['vm_hosts'], get_frame_info())
#           count = kill_retire(config, active_user.active_group, fields['cloud_name'], 'control', [50,1000000], get_frame_info())
        else:
            count = 0
            if fields['vm_hosts'] == 'all':
                if active_user.active_group and active_user.active_group == 'ALL':
                    rc, msg, vm_list_raw = config.db_query("view_vms")
                else:
                    where_clause = "group_name='%s'" % active_user.active_group
                    rc, msg, vm_list_raw = config.db_query("view_vms", where=where_clause)
                _vm_list = qt(vm_list_raw, filter=qt_filter_get(['cloud_name', 'poller_status'], fields, aliases=ALIASES))
            else:
                fields['hostname'] = fields['vm_hosts']
                if active_user.active_group and active_user.active_group == 'ALL':
                    rc, msg, vm_list_raw = config.db_query("view_vms")
                else:
                    where_clause = "group_name='%s'" % active_user.active_group
                    rc, msg, vm_list_raw = config.db_query("view_vms", where=where_clause)
                _vm_list = qt(vm_list_raw, filter=qt_filter_get(['cloud_name', 'hostname', 'poller_status'], fields, aliases=ALIASES))

            for vm in _vm_list:
                if fields['vm_option'] == 'kill':
                    vm_dict = {'terminate': 2, 'updater': get_frame_info()}
                    where_clause = "vmid='%s'" % vm['vmid']
                    rc, msg = config.db_update(table, vm_dict, where=where_clause)
                elif fields['vm_option'] == 'retire':
                    vm_dict = {'retire': 1, 'updater': get_frame_info()}
                    where_clause = "vmid='%s'" % vm['vmid']
                    rc, msg = config.db_update(table, vm_dict, where=where_clause)
                elif fields['vm_option'] == 'manctl':
                    vm_dict = {'manual_control': 1}
                    where_clause = "vmid='%s'" % vm['vmid']
                    rc, msg = config.db_update(table, vm_dict, where=where_clause)
                elif fields['vm_option'] == 'sysctl':
                    vm_dict = {'manual_control': 0}
                    where_clause = "vmid='%s'" % vm['vmid']
                    rc, msg = config.db_update(table, vm_dict, where=where_clause)

                if rc == 0:
                    count += 1
                else:
                    config.db_close()
                    return render(request, 'csv2/vms.html', {'response_code': 1, 'message': '%s vm update (%s) failed - %s' % (lno(MODID), fields['vm_option'], msg), 'active_user': active_user.username, 'active_group': active_user.active_group, 'user_groups': active_user.user_groups})
#                   return vm_list(request, selector, response_code=1, message='%s vm update (%s) failed - %s' % (lno(MODID), fields['vm_option'], msg))

        if count > 0:
            cloud_type = None
            if 'cloud_type' in fields:
                cloud_type = fields['cloud_type']
            elif 'cloud_name' in fields:
                rc, msg, target_cloud = get_target_cloud(config, active_user.active_group, fields['cloud_name'])
                if rc == 0:
                    cloud_type = target_cloud['cloud_type']
            if cloud_type == 'amazon':
                event_signal_send(config, "update_csv2_clouds_amazon")
            elif cloud_type == 'openstack':
                event_signal_send(config, "update_csv2_clouds_openstack")
            
            config.db_close(commit=True)
        else:
            config.db_close()

        args = {}
        if 'cloud_name' in fields:
            args['cloud_name'] =  fields['cloud_name']
        if 'poller_status' in fields:
            args['poller_status'] = fields['poller_status']
        args['hostname'] = ''

        return vm_list(request, args, response_code=0, message='vm update, VMs %s: %s.' % (verb, count))

    ### Bad request.
    else:
        config.db_close()
        return render(request, 'csv2/vms.html', {'response_code': 1, 'message': '%s vm update, invalid method "%s" specified.' % (lno(MODID), request.method), 'active_user': active_user.username, 'active_group': active_user.active_group, 'user_groups': active_user.user_groups})
#       return vm_list(request, selector, response_code=1, message='%s vm update, invalid method "%s" specified.' % (lno(MODID), request.method))
