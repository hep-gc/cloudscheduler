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
        'vm_hosts':                                                     'lowerdashlist',
        },
    'array_fields': [
        'vm_hosts',
        ],
    'not_empty': [
        'vm_hosts',
        ],
    }

SETTING_KEYS = {
    'auto_active_group': True,
    'format': {
        'service_option':                                               ['show','hide'],
        'csrfmiddlewaretoken':                                          'ignore', 
        'service_alias':                                                'ignore'
        },
    'array_fields': [
        'service_alias',
        ],
    'not_empty': [
        'service_alias',
        ],
}

SETTING_MANDATORY_KEYS = {
    'mandatory': [
        'service_option',
        ]
    }

LIST_KEYS = {
    # Named argument formats (anything else is a string).
    'format': {
        'csrfmiddlewaretoken':                                          'ignore',
        'group':                                                        'ignore',
        'group_name':                                                   'group',
        'job_status':                                                   [0,1,2,4,5]

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

@silkp(name="Settings List")
@requires_csrf_token
def settings_list(request, response_code=0, message=None):
    # open the database.
    config.db_open()

    # Retrieve service information.
    rc, msg, service_list = config.db_query("view_service_status")
    
    config.db_close()
    
    if request.GET.get('msg') == 'success':
        message = 'Update Success'
    elif request.GET.get('msg') == 'error':
        message = 'Update Failed'
        response_code = 1
    
    for service in service_list:
        if service['state'] == 'up':
            service['state'] = 'Active'
        elif service['state'] == 'down':
            service['state'] = 'Not Running'
        else:
            service['state'] = 'ERROR'
    # Render the page.
    context = {
            'service_list': service_list,
            'response_code': response_code,
            'message': message,

        }
    return render(request, 'csv2/service.html', context)

#-------------------------------------------------------------------------------

@silkp(name="Error List")
@requires_csrf_token
def error_list(request, response_code=0, message=None):
    # open the database.
    config.db_open()
    alias = request.GET.get('alias', None) 
    rc, msg, provider_list = config.db_query("csv2_service_providers",select=['provider'],where="alias='%s'" % alias)

    provider = provider_list[0]['provider']

    # Retrieve service information.
    where_clause = "provider='%s' and error_log IS NOT NULL" % provider
    
    rc, msg, error_list = config.db_query("csv2_service_catalog",select=['provider', 'host_id', 'last_error', 'error_message', 'error_log'],where=where_clause)
    rc, msg, service_list = config.db_query("view_service_status", where= "alias='%s'" %alias)
    config.db_close()
    
    error_log= ''
    last_error = None
    
    if error_list:
        error = error_list[0]
        error_log_raw = error.get('error_log', '')
        error_log = error_log_raw.replace('\\n', '<br>').replace('\n', '<br>')
        ts = error.get('last_error')
        if ts:
            try:
                ts = float(ts)
                last_error = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))
            except:
                last_error = ''

    state = ''
    if service_list:
        state = service_list[0]['state']
        if state == 'up':
            state = 'Active'
        elif state == 'down':
            state = 'Not Running'
        else:
            state = 'ERROR'

    # Render the page.
    context = {
            'error_list': error_list,
            'alias': alias,
            'error_log': error_log,
            'state': state,
            'last_error': last_error,
            'response_code': response_code,
            'message': message,
        }
    return render(request, 'csv2/error.html', context)

@silkp(name="Job List")
@requires_csrf_token
def jobs(request, args = None, response_code=0, message=None):

    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        return render(request, 'csv2/jobs.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})
    
    request_group = request.GET.get('group_name')
    if request_group:
        active_group = request_group
    else:
        active_group = active_user.active_group

    # Validate input fields (should be none).
    if args == None:
        args = active_user.kwargs
        if request.method == 'GET':
            rc, msg, fields, tables, columns = validate_fields(config, request, [LIST_KEYS], [], active_user)
            if rc != 0:
                config.db_close()
                return render(request, 'csv2/jobs.html', {'response_code': 1, 'message': '%s jobs list, %s' % (lno(MODID), msg)})

  # Retrieve condor jobs information
    if active_user.active_group and active_user.active_group == 'ALL':
        rc, msg, jobs_list_raw = config.db_query("condor_jobs")
    else:
        group = active_user.active_group.lower()
        where_clause = "group_name='%s'" % active_group
        rc, msg, jobs_list_raw = config.db_query("condor_jobs", where=where_clause)
    jobs_list = qt(jobs_list_raw, filter=qt_filter_get(['job_status'], args, aliases=ALIASES))
    show_status = True
    if args and ('job_status' not in args or args.get('job_status') == ''):
        show_status = False

    show_group= True
    if args and ('group_name' not in args or args.get('group_name') == ''):
        show_group = False
   
    try:
        where_clause = "group_name = '%s'" % jobs_list[0]['group_name']
        rc, msg, fqdn_list = config.db_query("csv2_groups", select = ['htcondor_fqdn'], where = where_clause)
        if rc ==0:
            fqdn = fqdn_list[0]['htcondor_fqdn']
    except:
        fqdn = None

    for job in jobs_list:
        if 'job_status' in job and job['job_status']:
            if job['job_status'] == 0:
                job['job_status'] = 'Unexpanded'
            elif job['job_status'] == 1:
                job['job_status'] = 'Idle'
            elif job['job_status'] == 2:
                job['job_status'] = 'Running'
            elif job['job_status'] == 3:
                job['job_status'] = 'Removed'
            elif job['job_status'] == 4:
                job['job_status'] = 'Completed'
            elif job['job_status'] == 5:
                job['job_status'] = 'Held'

        if 'q_date' in job and job['q_date']:
            job['q_date_formatted'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(job['q_date']))
        else:
            job['q_date_formatted'] = ''

        if 'entered_current_status' in job and job['entered_current_status']:
            job['entered_current_status_formatted'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(job['entered_current_status']))
        else:
            job['entered_current_status_formatted'] = ''

    config.db_close()

    # Render the page.
    context = {
            'active_user': active_user.username,
            'active_group': active_user.active_group,
            'user_groups': active_user.user_groups,
            'form_inputs': {'group_name':show_group, 'job_status' :show_status},
            'jobs_list': jobs_list,
            'current_activity_filter': args.get('job_status', ''),
            'response_code': response_code,
            'message': message,
            'is_superuser': active_user.is_superuser,
            'version': config.get_version(),
            'fqdn' : fqdn,
            'group_name' :request_group
        }

    return render(request, 'csv2/jobs.html', context)

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
            if isinstance(fields['vm_hosts'], str) and fields['vm_hosts'].isnumeric():
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

#-------------------------------------------------------------------------------

@silkp(name="Settings Update")
@requires_csrf_token
def settings_update(request):
    """
    Update machines.
    """

    # open the database.
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        return render(request, 'csv2/service.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})

    if request.method == 'POST':
        # Validate input fields.
        rc, msg, fields, tables, columns = validate_fields(
        config, request, [SETTING_KEYS, SETTING_MANDATORY_KEYS], ['csv2_service_providers,n'], active_user)
        if rc != 0:
            config.db_close()
            return settings_list(request, response_code=0, message='%s %s' % (lno(MODID), msg))

        table = 'csv2_service_providers'
        count =0
        if 'service_alias' not in fields or not fields['service_alias']:
            config.db_close()
            return settings_list(request, response_code=1, message='No services selected.')
        
        service_aliases = fields.get('service_alias')
        if isinstance(service_aliases, str):
            service_aliases = [service_aliases]

        if fields['service_option'] == 'show':
            machine_dict = {'visible': 1, 'updater': get_frame_info()}
        elif fields['service_option'] == 'hide':
            machine_dict = {'visible': 0, 'updater': get_frame_info()}
        else:
            return settings_list(request, response_code=1, message='Update Failed') 
       
        for service_alias in service_aliases:     
            where_clause = "alias='%s'" % service_alias
            rc, msg = config.db_update(table, machine_dict, where=where_clause)
        config.db_commit()
        config.db_close()

        return redirect('/vm/settings/?msg=success')
        
    ###Bad request.
    else:
        config.db_close()
        return settings_list(request, response_code=1, message='Invalid Method')
