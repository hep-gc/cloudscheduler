from django.conf import settings
config = settings.CSV2_CONFIG

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import requires_csrf_token
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied


from cloudscheduler.lib.view_utils import \
    lno, \
    qt, \
    render, \
    set_user_groups, \
    table_fields, \
    validate_fields
import bcrypt

from cloudscheduler.lib.schema import *

from cloudscheduler.lib.web_profiler import silk_profile as silkp

# lno: JV - error code identifier.
MODID = 'JV'

#-------------------------------------------------------------------------------

CLOUD_KEYS = {
    'auto_active_group': True,
    # Named argument formats (anything else is a string).
    'format': {
        'cloud_name':          'lower',

        'cores_slider':        'ignore',
        'csrfmiddlewaretoken': 'ignore',
        'group':               'ignore',
        'ram_slider':          'ignore',
        },
    }

YAML_KEYS = {
    'auto_active_group': True,
    # Named argument formats (anything else is a string).
    'format': {
        'cloud_name':          'lower',
        'yaml_name':           'lower',

        'csrfmiddlewaretoken': 'ignore',
        'group':               'ignore',
        },
    }

IGNORE_YAML_NAME = {
    'format': {
        'yaml_name':           'ignore',
        },
    }

LIST_KEYS = {
    # Named argument formats (anything else is a string).
    'format': {
        'csrfmiddlewaretoken':     'ignore',
        'group':                   'ignore',
        },
    }

#-------------------------------------------------------------------------------

@silkp(name="Job List")
@requires_csrf_token
def job_list(request):

    # open the database.
    config.db_open() 

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        config.db_close()
        return render(request, 'csv2/clouds.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})

    # Validate input fields (should be none).
    rc, msg, fields, tables, columns = validate_fields(config, request, [LIST_KEYS], [], active_user)
    if rc != 0:
        config.db_close()
        return render(request, 'csv2/jobs.html', {'response_code': 1, 'message': '%s job list, %s' % (lno(MODID), msg)})

    # Retrieve VM information.
    where_clause = "group_name='%s'" % active_user.active_group
    rc, msg, job_list_raw = config.db_query("view_condor_jobs_group_defaults_applied", where=where_clause)
    _job_list = qt(job_list_raw, convert={'entered_current_status': 'datetime', 'q_date': 'datetime'})

    config.db_close()
    
    # Render the page.
    context = {
            'active_user': active_user.username,
            'active_group': active_user.active_group,
            'user_groups': active_user.user_groups,
            'job_list': _job_list,
            'response_code': 0,
            'message': None,
            'is_superuser': active_user.is_superuser,
            'version': config.get_version()
        }

    return render(request, 'csv2/jobs.html', context)

