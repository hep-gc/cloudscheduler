from django.conf import settings
config = settings.CSV2_CONFIG

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import requires_csrf_token
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied


from .view_utils import \
    lno, \
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

# lno: JV - error code identifier.

#-------------------------------------------------------------------------------

CLOUD_KEYS = {
    'auto_active_group': True,
    # Named argument formats (anything else is a string).
    'format': {
        'cloud_name':          'lowerdash',

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
        'cloud_name':          'lowerdash',
        'yaml_name':           'lowercase',

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
def list(
    request,
    selector=None,
    group_name=None,
    response_code=0,
    message=None,
    user_groups=None,
    attributes=None
    ):

    # open the database.
    config.db_open() 

    if response_code != 0:
        config.db_close()
        return render(request, 'csv2/clouds.html', {'response_code': 1, 'message': message})

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user, user_groups = set_user_groups(config, request, False)
    if rc != 0:
        config.db_close()
        return render(request, 'csv2/clouds.html', {'response_code': 1, 'message': msg})

    # Validate input fields (should be none).
    if not message:
        rc, msg, fields, tables, columns = validate_fields(config, request, [LIST_KEYS], [], active_user)
        if rc != 0:
            config.db_close()
            return render(request, 'csv2/jobs.html', {'response_code': 1, 'message': '%s job list, %s' % (lno('JV00'), msg)})

    # Retrieve VM information.
    s = select([view_condor_jobs_group_defaults_applied]).where(view_condor_jobs_group_defaults_applied.c.group_name == active_user.active_group)
    job_list = qt(config.db_connection.execute(s), convert={'entered_current_status': 'datetime', 'q_date': 'datetime'})

    config.db_close()
    
#   # Position the page.
#   obj_act_id = request.path.split('/')
#   if selector:
#       if selector == '-':
#           current_cloud = ''
#       else:
#           current_cloud = selector
#   elif len(obj_act_id) > 3 and len(obj_act_id[3]) > 0:
#       current_cloud = str(obj_act_id[3])
#   else:
#       if len(cloud_list) > 0:
#           current_cloud = str(cloud_list[0]['cloud_name'])
#       else:
#           current_cloud = ''

    # Render the page.
    context = {
            'active_user': active_user.username,
            'active_group': active_user.active_group,
            'attributes': attributes,
            'user_groups': user_groups,
            'job_list': job_list,
            'response_code': response_code,
            'message': message,
            'enable_glint': config.enable_glint,
            'is_superuser': active_user.is_superuser
        }

    return render(request, 'csv2/jobs.html', context)

