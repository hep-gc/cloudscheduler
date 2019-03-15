from django.conf import settings
config = settings.CSV2_CONFIG

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import requires_csrf_token
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from cloudscheduler.lib.view_utils import \
    lno,  \
    manage_group_users, \
    manage_user_group_verification, \
    qt, \
    render, \
    set_user_groups, \
    table_fields, \
    validate_fields

from collections import defaultdict
import bcrypt

from sqlalchemy import exists
from sqlalchemy.sql import select
from cloudscheduler.lib.schema import *
import sqlalchemy.exc

from cloudscheduler.lib.web_profiler import silk_profile as silkp

# lno: SV - error code identifier.

#-------------------------------------------------------------------------------

CONFIG_KEYS = {
    'auto_active_group': True,
    # Named argument formats (anything else is a string).
    'format': {
        'batch_commit_size':                'integer',
        'category':                         ('csv2_configuration', 'category'),
        'delete_cycle_interval':            'integer',
        'enable_glint':                     ['True', 'False'],
        'enable_profiling':                 ['True', 'False'],
        'log_level':                        'integer',
        'max_start_vm_cloud':               'integer',
        'no_limit_default':                 'integer',
        'orange_threshold':                 'integer',
        'sleep_interval_cleanup':           'integer',
        'sleep_interval_command':           'integer',
        'sleep_interval_flavor':            'integer',
        'sleep_interval_image':             'integer',
        'sleep_interval_job':               'integer',
        'sleep_interval_keypair':           'integer',
        'sleep_interval_limit':             'integer',
        'sleep_interval_machine':           'integer',
        'sleep_interval_main_long':         'integer',
        'sleep_interval_main_short':        'integer',
        'sleep_interval_network':           'integer',
        'sleep_interval_status':            'integer',
        'sleep_interval_vm':                'integer',
        'unregistered_machine_time_limit':  'integer',

        'cache_expire_time':                'integer',
        'celery_backend':                   'string',
        'celery_url':                       'string',
        'cert_auth_bundle_path':            'string',
        'defaults_sleep_interval':          'integer',
        'image_collection_interval':        'integer',
        #'log_file':                         'string',
        'redis_db':                         'integer',
        'redis_host':                       'string',
        'redis_port':                       'integer',
        'sleep_interval_main_long':         'integer',
        'sleep_interval_main_short':        'integer',
        'static_files_root':                'string',
        'csv2_host_id':                     'integer',



        'config_key':                       'reject',
        'type':                             'reject',
        'value':                            'reject',

        'cacerts':                          'ignore',
        'csrfmiddlewaretoken':              'ignore',
        'default_job_group':                'ignore',
        'group':                            'ignore',
        'log_file':                         'ignore',
    },
    'mandatory': [
        'category',
    ],
}

#-------------------------------------------------------------------------------

@silkp(name="Server Config")
def configuration(request):
    """
    Update and list server configurations
    """

    config.db_open()
    message = None

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request)
    if rc == 0:
        if (request.method == 'POST') and ((not 'group' in request.POST) or len(request.POST) > 2):
                # Validate input fields.
                rc, msg, fields, tables, columns = validate_fields(config, request, [CONFIG_KEYS], ['csv2_configuration,n'], active_user)
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
                            rc, msg = config.db_session_execute(table.update().where((table.c.category==category) & (table.c.config_key==field)).values({table.c.config_value:fields[field]}))
                            if rc != 0:
                                config.db_session.rollback()
                                message = '{} server config update failed - {}'.format(lno('SV01'), msg)
                                break
                        if rc == 0:
                            config.db_session.commit()
                            message = 'server config successfully updated'
                else:
                    message = '{} server config update {}'.format(lno('SV02'), msg)
    else:
        message='{} {}'.format(lno('SV03'), msg)

    if message and message[:2] == 'SV':
        config_list = []
        config_categories = []
        response_code = 1
    else:
        s = select([csv2_configuration])
        config_list = qt(config.db_connection.execute(s))
        config_categories = list({v['category']:v for v in config_list})
        response_code = 0


    # Render the page.
    context = {
            'active_user': active_user.username,
            'active_group': active_user.active_group,
            'user_groups': active_user.user_groups,
            'config_list': config_list,
            'config_categories': config_categories,
            'response_code': response_code,
            'message': message,
            'enable_glint': config.enable_glint,
            'is_superuser': active_user.is_superuser,
            'version': config.get_version()
        }

    config.db_close()
    return render(request, 'csv2/server_config.html', context)

